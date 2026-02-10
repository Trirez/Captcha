"""
Audio Captcha Generator
Generates spoken-word audio captcha using text-to-speech (pyttsx3).
Speaks digits as words ("one", "two", "three") with background noise distortion.
"""

import random
import string
import struct
import wave
import io
import math
import base64
import tempfile
import os
import threading

import pyttsx3


class AudioCaptcha:
    """Generates spoken-word audio captcha using system TTS."""

    # Map characters to spoken words
    CHAR_TO_WORD = {
        '0': 'zero', '1': 'one', '2': 'two', '3': 'three', '4': 'four',
        '5': 'five', '6': 'six', '7': 'seven', '8': 'eight', '9': 'nine',
        'A': 'ay', 'B': 'bee', 'C': 'see', 'D': 'dee', 'E': 'ee',
        'F': 'eff', 'G': 'jee', 'H': 'aitch', 'J': 'jay', 'K': 'kay',
        'L': 'ell', 'M': 'em', 'N': 'en', 'P': 'pee', 'Q': 'queue',
        'R': 'are', 'S': 'ess', 'T': 'tee', 'U': 'you', 'V': 'vee',
        'W': 'double you', 'X': 'ex', 'Y': 'why', 'Z': 'zed',
    }

    def __init__(self):
        self.characters = string.digits
        self._lock = threading.Lock()

    def generate_text(self, length=5):
        """Generate random captcha text (digits for clear audio recognition)."""
        return ''.join(random.choices(self.characters, k=length))

    def _generate_speech_wav(self, spoken_text):
        """Use pyttsx3 to generate WAV speech and return raw WAV bytes."""
        temp_path = tempfile.mktemp(suffix='.wav')

        try:
            with self._lock:
                engine = pyttsx3.init()

                # Randomize speech rate for variation (normal ~150-200)
                rate = random.randint(120, 160)
                engine.setProperty('rate', rate)
                engine.setProperty('volume', 0.9)

                # Try to pick a voice (prefer female for clarity variation)
                voices = engine.getProperty('voices')
                if voices and len(voices) > 1:
                    engine.setProperty('voice', random.choice(voices).id)

                engine.save_to_file(spoken_text, temp_path)
                engine.runAndWait()
                engine.stop()

            # Read the WAV file
            with open(temp_path, 'rb') as f:
                wav_bytes = f.read()

            return wav_bytes
        finally:
            if os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except OSError:
                    pass

    def _wav_to_samples(self, wav_bytes):
        """Convert WAV bytes to float samples and return (samples, sample_rate)."""
        buffer = io.BytesIO(wav_bytes)
        with wave.open(buffer, 'rb') as wf:
            n_channels = wf.getnchannels()
            sampwidth = wf.getsampwidth()
            framerate = wf.getframerate()
            n_frames = wf.getnframes()
            raw_data = wf.readframes(n_frames)

        # Convert to 16-bit mono samples
        if sampwidth == 2:
            samples = struct.unpack(f'<{len(raw_data) // 2}h', raw_data)
        elif sampwidth == 1:
            samples = [((b - 128) * 256) for b in raw_data]
        else:
            # 24-bit or other — downsample to 16-bit
            samples = []
            for i in range(0, len(raw_data), sampwidth):
                val = int.from_bytes(raw_data[i:i + sampwidth], 'little', signed=True)
                samples.append(val >> (8 * (sampwidth - 2)))

        # If stereo, convert to mono by averaging channels
        if n_channels == 2:
            mono = []
            for i in range(0, len(samples), 2):
                if i + 1 < len(samples):
                    mono.append((samples[i] + samples[i + 1]) // 2)
                else:
                    mono.append(samples[i])
            samples = mono

        # Normalize to float [-1.0, 1.0]
        float_samples = [s / 32768.0 for s in samples]
        return float_samples, framerate

    def _resample(self, samples, from_rate, to_rate):
        """Simple linear interpolation resampling."""
        if from_rate == to_rate:
            return samples

        ratio = from_rate / to_rate
        new_length = int(len(samples) / ratio)
        resampled = []
        for i in range(new_length):
            src_idx = i * ratio
            idx = int(src_idx)
            frac = src_idx - idx
            if idx + 1 < len(samples):
                val = samples[idx] * (1 - frac) + samples[idx + 1] * frac
            else:
                val = samples[idx] if idx < len(samples) else 0.0
            resampled.append(val)
        return resampled

    def _add_noise(self, samples, sample_rate):
        """Add background noise and distortion to make it harder for bots."""
        n = len(samples)

        # 1. White noise
        noise_vol = random.uniform(0.02, 0.06)
        for i in range(n):
            samples[i] += random.uniform(-noise_vol, noise_vol)

        # 2. Low-frequency hum
        hum_freq = random.uniform(45, 65)
        hum_vol = random.uniform(0.02, 0.05)
        for i in range(n):
            t = i / sample_rate
            samples[i] += hum_vol * math.sin(2 * math.pi * hum_freq * t)

        # 3. Random crackle bursts
        for _ in range(random.randint(3, 8)):
            start = random.randint(0, max(0, n - 500))
            length = random.randint(80, 300)
            crackle_vol = random.uniform(0.03, 0.08)
            for i in range(start, min(start + length, n)):
                samples[i] += random.uniform(-crackle_vol, crackle_vol)

        # 4. Slight pitch warble
        warble_freq = random.uniform(2, 4)
        warble_depth = random.uniform(0.003, 0.008)
        for i in range(n):
            t = i / sample_rate
            samples[i] *= (1.0 + warble_depth * math.sin(2 * math.pi * warble_freq * t))

        return samples

    def _samples_to_wav(self, samples, sample_rate=22050):
        """Convert float samples to WAV bytes."""
        buffer = io.BytesIO()
        with wave.open(buffer, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)

            packed = b''
            for s in samples:
                clamped = max(-1.0, min(1.0, s))
                packed += struct.pack('<h', int(clamped * 32767))
            wf.writeframes(packed)

        buffer.seek(0)
        return buffer.getvalue()

    def generate_audio(self, text):
        """Generate spoken audio for the captcha text with noise."""
        # Build the spoken phrase: "one ... three ... seven ..."
        words = []
        for char in text:
            word = self.CHAR_TO_WORD.get(char, char)
            words.append(word)

        # Join with pauses (commas create natural pauses in TTS)
        spoken_text = ' .... '.join(words)

        # Generate TTS WAV
        wav_bytes = self._generate_speech_wav(spoken_text)

        # Convert to float samples
        float_samples, original_rate = self._wav_to_samples(wav_bytes)

        # Resample to standard rate if needed
        target_rate = 22050
        if original_rate != target_rate:
            float_samples = self._resample(float_samples, original_rate, target_rate)

        # Add noise distortion
        float_samples = self._add_noise(float_samples, target_rate)

        # Convert back to WAV
        return self._samples_to_wav(float_samples, target_rate)

    def generate(self, length=5):
        """Generate captcha text and spoken audio, return base64 encoded audio and text."""
        text = self.generate_text(length)
        wav_bytes = self.generate_audio(text)

        audio_base64 = base64.b64encode(wav_bytes).decode('utf-8')

        return {
            'text': text,
            'audio': f'data:audio/wav;base64,{audio_base64}'
        }
