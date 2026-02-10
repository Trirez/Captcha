"""
Text Captcha Generator
Generates distorted text images for captcha verification
with multiple visual styles for enhanced security
"""

import random
import string
import math
import io
import base64
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops


class TextCaptcha:
    def __init__(self, width=280, height=90):
        self.width = width
        self.height = height
        self.characters = string.ascii_uppercase + string.digits
        # Remove confusing characters
        self.characters = self.characters.replace('O', '').replace('0', '').replace('I', '').replace('1', '')
    
    def generate_text(self, length=6):
        """Generate random captcha text"""
        return ''.join(random.choices(self.characters, k=length))
    
    def _get_font(self, size=None):
        """Get a font, falling back to default if arial is unavailable"""
        if size is None:
            size = random.randint(38, 48)
        try:
            return ImageFont.truetype("arial.ttf", size)
        except:
            try:
                return ImageFont.truetype("Arial.ttf", size)
            except:
                return ImageFont.load_default()
    
    # ======== STYLE 1: Classic (original) ========
    
    def _style_classic(self, text):
        """Original style: gradient background, rotated chars, noise lines & dots, blur"""
        image = Image.new('RGB', (self.width, self.height), (255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        # Gradient background
        for y in range(self.height):
            r = int(240 + (15 * y / self.height))
            g = int(240 + (15 * y / self.height))
            b = int(250 - (10 * y / self.height))
            for x in range(self.width):
                draw.point((x, y), fill=(r, g, b))
        
        # Noise lines
        for _ in range(random.randint(4, 8)):
            x1, y1 = random.randint(0, self.width), random.randint(0, self.height)
            x2, y2 = random.randint(0, self.width), random.randint(0, self.height)
            color = (random.randint(100, 180), random.randint(100, 180), random.randint(100, 180))
            draw.line([(x1, y1), (x2, y2)], fill=color, width=1)
        
        # Noise dots
        for _ in range(random.randint(100, 200)):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            color = (random.randint(100, 200), random.randint(100, 200), random.randint(100, 200))
            draw.point((x, y), fill=color)
        
        # Draw rotated characters
        font = self._get_font()
        char_width = self.width // (len(text) + 1)
        
        for i, char in enumerate(text):
            x = char_width * (i + 0.5) + random.randint(-5, 5)
            y = random.randint(10, 30)
            color = (random.randint(0, 80), random.randint(0, 80), random.randint(80, 150))
            
            char_img = Image.new('RGBA', (60, 70), (255, 255, 255, 0))
            char_draw = ImageDraw.Draw(char_img)
            char_draw.text((10, 10), char, font=font, fill=color)
            
            angle = random.randint(-25, 25)
            char_img = char_img.rotate(angle, expand=True, resample=Image.BICUBIC)
            image.paste(char_img, (int(x), int(y)), char_img)
        
        image = image.filter(ImageFilter.GaussianBlur(radius=0.5))
        return image
    
    # ======== STYLE 2: Wave Warp ========
    
    def _style_wave_warp(self, text):
        """Sine-wave warped characters on a pastel background with curved noise"""
        # Pastel background
        base_hue = random.randint(0, 255)
        bg_color = (
            200 + random.randint(0, 40),
            210 + random.randint(0, 40),
            220 + random.randint(0, 35)
        )
        image = Image.new('RGB', (self.width, self.height), bg_color)
        draw = ImageDraw.Draw(image)
        
        # Curved noise lines
        for _ in range(random.randint(3, 6)):
            points = []
            y_start = random.randint(0, self.height)
            amplitude = random.randint(10, 30)
            freq = random.uniform(0.02, 0.06)
            color = (random.randint(140, 200), random.randint(140, 200), random.randint(140, 200))
            for x in range(0, self.width, 2):
                y = y_start + int(amplitude * math.sin(freq * x + random.uniform(0, math.pi)))
                points.append((x, y))
            if len(points) >= 2:
                draw.line(points, fill=color, width=1)
        
        # Dot clusters
        for _ in range(random.randint(5, 12)):
            cx, cy = random.randint(0, self.width), random.randint(0, self.height)
            for _ in range(random.randint(5, 15)):
                dx, dy = random.randint(-8, 8), random.randint(-8, 8)
                color = (random.randint(150, 210), random.randint(150, 210), random.randint(150, 210))
                draw.point((cx + dx, cy + dy), fill=color)
        
        # Draw each character with sine-wave vertical offset
        font = self._get_font(random.randint(36, 46))
        char_width = self.width // (len(text) + 1)
        wave_amp = random.randint(6, 14)
        wave_freq = random.uniform(0.8, 1.5)
        
        for i, char in enumerate(text):
            x = char_width * (i + 0.5) + random.randint(-3, 3)
            y_base = self.height // 2 - 22
            y_offset = int(wave_amp * math.sin(wave_freq * i + random.uniform(0, 1)))
            y = y_base + y_offset
            
            color = (random.randint(10, 90), random.randint(10, 90), random.randint(40, 120))
            
            char_img = Image.new('RGBA', (60, 70), (0, 0, 0, 0))
            char_draw = ImageDraw.Draw(char_img)
            char_draw.text((10, 10), char, font=font, fill=color)
            
            angle = random.randint(-15, 15)
            char_img = char_img.rotate(angle, expand=True, resample=Image.BICUBIC)
            image.paste(char_img, (int(x), int(y)), char_img)
        
        image = image.filter(ImageFilter.GaussianBlur(radius=0.3))
        return image
    
    # ======== STYLE 3: Shadow & Outline ========
    
    def _style_shadow_outline(self, text):
        """Dark gradient background with outlined/shadowed white text and grid noise"""
        image = Image.new('RGB', (self.width, self.height))
        draw = ImageDraw.Draw(image)
        
        # Dark gradient background
        r1, g1, b1 = random.randint(20, 50), random.randint(20, 50), random.randint(40, 80)
        r2, g2, b2 = random.randint(50, 90), random.randint(30, 60), random.randint(60, 110)
        for y in range(self.height):
            t = y / self.height
            r = int(r1 + (r2 - r1) * t)
            g = int(g1 + (g2 - g1) * t)
            b = int(b1 + (b2 - b1) * t)
            draw.line([(0, y), (self.width, y)], fill=(r, g, b))
        
        # Subtle grid lines
        grid_color = (r1 + 25, g1 + 25, b1 + 25)
        for x in range(0, self.width, random.randint(12, 20)):
            draw.line([(x, 0), (x, self.height)], fill=grid_color, width=1)
        for y in range(0, self.height, random.randint(12, 20)):
            draw.line([(0, y), (self.width, y)], fill=grid_color, width=1)
        
        # Spark dots
        for _ in range(random.randint(30, 70)):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            brightness = random.randint(100, 200)
            draw.point((x, y), fill=(brightness, brightness, brightness))
        
        # Draw text with shadow and outline
        font = self._get_font(random.randint(38, 48))
        char_width = self.width // (len(text) + 1)
        
        for i, char in enumerate(text):
            x = char_width * (i + 0.5) + random.randint(-4, 4)
            y = random.randint(12, 28)
            
            char_img = Image.new('RGBA', (70, 80), (0, 0, 0, 0))
            char_draw = ImageDraw.Draw(char_img)
            
            # Shadow (offset dark text)
            shadow_offset = random.randint(2, 4)
            char_draw.text((10 + shadow_offset, 10 + shadow_offset), char, font=font,
                           fill=(0, 0, 0, 160))
            
            # Outline effect: draw text in 4 offset positions
            outline_color = (random.randint(100, 160), random.randint(150, 220), random.randint(200, 255), 255)
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                char_draw.text((10 + dx, 10 + dy), char, font=font, fill=outline_color)
            
            # Main text in bright white
            char_draw.text((10, 10), char, font=font, fill=(255, 255, 255, 245))
            
            angle = random.randint(-20, 20)
            char_img = char_img.rotate(angle, expand=True, resample=Image.BICUBIC)
            image.paste(char_img, (int(x), int(y)), char_img)
        
        image = image.filter(ImageFilter.GaussianBlur(radius=0.4))
        return image
    
    # ======== STYLE 4: Colorful Overlap ========
    
    def _style_colorful_overlap(self, text):
        """White background with bold random-colored characters and cross-hatch / arcs"""
        image = Image.new('RGB', (self.width, self.height), (250, 250, 252))
        draw = ImageDraw.Draw(image)
        
        # Cross-hatch pattern
        hatch_color = (random.randint(210, 235), random.randint(210, 235), random.randint(210, 235))
        spacing = random.randint(8, 14)
        for x in range(-self.height, self.width, spacing):
            draw.line([(x, 0), (x + self.height, self.height)], fill=hatch_color, width=1)
        for x in range(0, self.width + self.height, spacing):
            draw.line([(x, 0), (x - self.height, self.height)], fill=hatch_color, width=1)
        
        # Random arcs
        for _ in range(random.randint(3, 7)):
            x0 = random.randint(-30, self.width)
            y0 = random.randint(-30, self.height)
            x1 = x0 + random.randint(40, 120)
            y1 = y0 + random.randint(40, 80)
            start_angle = random.randint(0, 360)
            end_angle = start_angle + random.randint(60, 180)
            arc_color = (random.randint(160, 220), random.randint(160, 220), random.randint(160, 220))
            draw.arc([(x0, y0), (x1, y1)], start_angle, end_angle, fill=arc_color, width=1)
        
        # Vibrant color palette
        palette = [
            (200, 30, 30), (30, 130, 200), (20, 150, 60),
            (180, 100, 20), (140, 30, 180), (200, 50, 120),
            (30, 160, 160), (160, 140, 0)
        ]
        
        font = self._get_font(random.randint(40, 50))
        char_width = self.width // (len(text) + 1)
        
        for i, char in enumerate(text):
            x = char_width * (i + 0.4) + random.randint(-6, 2)  # slight overlap
            y = random.randint(8, 28)
            color = random.choice(palette)
            
            char_img = Image.new('RGBA', (65, 75), (0, 0, 0, 0))
            char_draw = ImageDraw.Draw(char_img)
            char_draw.text((10, 10), char, font=font, fill=color + (random.randint(200, 255),))
            
            angle = random.randint(-22, 22)
            char_img = char_img.rotate(angle, expand=True, resample=Image.BICUBIC)
            image.paste(char_img, (int(x), int(y)), char_img)
        
        image = image.filter(ImageFilter.GaussianBlur(radius=0.3))
        return image
    
    # ======== STYLE 5: Pixelated Blocks ========
    
    def _style_pixelated_blocks(self, text):
        """Tiled colored blocks background with pixelated text and random rectangles"""
        image = Image.new('RGB', (self.width, self.height), (240, 240, 240))
        draw = ImageDraw.Draw(image)
        
        # Tiled block background
        block_size = random.randint(10, 18)
        for bx in range(0, self.width, block_size):
            for by in range(0, self.height, block_size):
                shade = random.randint(215, 250)
                tint = random.choice([(shade, shade - 5, shade - 10),
                                       (shade - 10, shade, shade - 5),
                                       (shade - 5, shade - 10, shade)])
                draw.rectangle([(bx, by), (bx + block_size, by + block_size)], fill=tint)
        
        # Random colored rectangles as noise
        for _ in range(random.randint(6, 14)):
            rx = random.randint(0, self.width)
            ry = random.randint(0, self.height)
            rw = random.randint(8, 30)
            rh = random.randint(8, 25)
            rect_color = (random.randint(170, 220), random.randint(170, 220), random.randint(170, 220))
            draw.rectangle([(rx, ry), (rx + rw, ry + rh)], fill=rect_color, outline=rect_color)
        
        # Render text at full size first
        font = self._get_font(random.randint(38, 46))
        
        # Create text layer
        text_layer = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        text_draw = ImageDraw.Draw(text_layer)
        
        char_width = self.width // (len(text) + 1)
        for i, char in enumerate(text):
            x = char_width * (i + 0.5) + random.randint(-4, 4)
            y = random.randint(14, 30)
            color = (random.randint(0, 60), random.randint(0, 60), random.randint(0, 60), 240)
            
            char_img = Image.new('RGBA', (60, 70), (0, 0, 0, 0))
            char_draw = ImageDraw.Draw(char_img)
            char_draw.text((10, 10), char, font=font, fill=color)
            angle = random.randint(-18, 18)
            char_img = char_img.rotate(angle, expand=True, resample=Image.BICUBIC)
            text_layer.paste(char_img, (int(x), int(y)), char_img)
        
        # Pixelate the text layer: downscale then upscale
        pixel_factor = random.choice([3, 4])
        small = text_layer.resize(
            (self.width // pixel_factor, self.height // pixel_factor),
            Image.NEAREST
        )
        text_layer = small.resize((self.width, self.height), Image.NEAREST)
        
        image.paste(text_layer, (0, 0), text_layer)
        return image
    
    # ======== STYLE 6: Striped Interference ========
    
    def _style_striped(self, text):
        """Horizontal color stripes background with vertical interference bars"""
        image = Image.new('RGB', (self.width, self.height))
        draw = ImageDraw.Draw(image)
        
        # Horizontal stripe background
        stripe_height = random.randint(3, 6)
        color_a = (random.randint(220, 245), random.randint(220, 245), random.randint(230, 255))
        color_b = (color_a[0] - random.randint(10, 25),
                   color_a[1] - random.randint(10, 25),
                   color_a[2] - random.randint(10, 25))
        for y in range(0, self.height, stripe_height):
            color = color_a if (y // stripe_height) % 2 == 0 else color_b
            draw.rectangle([(0, y), (self.width, y + stripe_height)], fill=color)
        
        # Draw characters with alternating bold/thin appearance
        font_large = self._get_font(random.randint(42, 50))
        font_small = self._get_font(random.randint(34, 40))
        char_width = self.width // (len(text) + 1)
        
        for i, char in enumerate(text):
            x = char_width * (i + 0.5) + random.randint(-4, 4)
            font = font_large if i % 2 == 0 else font_small
            y = random.randint(10, 28) if i % 2 == 0 else random.randint(18, 34)
            
            color = (random.randint(0, 70), random.randint(0, 70), random.randint(50, 130))
            
            char_img = Image.new('RGBA', (65, 75), (0, 0, 0, 0))
            char_draw = ImageDraw.Draw(char_img)
            char_draw.text((10, 10), char, font=font, fill=color)
            
            angle = random.randint(-20, 20)
            char_img = char_img.rotate(angle, expand=True, resample=Image.BICUBIC)
            image.paste(char_img, (int(x), int(y)), char_img)
        
        # Vertical interference bars (semi-transparent overlay)
        overlay = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        
        bar_width = random.randint(2, 4)
        bar_spacing = random.randint(8, 16)
        for x in range(0, self.width, bar_spacing):
            alpha = random.randint(30, 70)
            bar_color = (random.randint(80, 180), random.randint(80, 180), random.randint(80, 180), alpha)
            overlay_draw.rectangle([(x, 0), (x + bar_width, self.height)], fill=bar_color)
        
        image = image.convert('RGBA')
        image = Image.alpha_composite(image, overlay)
        image = image.convert('RGB')
        
        image = image.filter(ImageFilter.GaussianBlur(radius=0.4))
        return image
    
    # ======== Main generation methods ========
    
    def generate_image(self, text):
        """Generate captcha image — randomly picks one of the visual styles"""
        styles = [
            self._style_classic,
            self._style_wave_warp,
            self._style_shadow_outline,
            self._style_colorful_overlap,
            self._style_pixelated_blocks,
            self._style_striped,
        ]
        style_fn = random.choice(styles)
        return style_fn(text)
    
    def generate(self, length=6):
        """Generate captcha text and image, return base64 encoded image and text"""
        text = self.generate_text(length)
        image = self.generate_image(text)
        
        # Convert to base64
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return {
            'text': text,
            'image': f'data:image/png;base64,{image_base64}'
        }
