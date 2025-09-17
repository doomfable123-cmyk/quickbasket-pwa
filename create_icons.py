#!/usr/bin/env python3
"""
Simple icon generator for QuickBasket PWA
Creates basic PNG icons from text
"""

import os

try:
    from PIL import Image, ImageDraw, ImageFont
    
    def create_icon(size, filename):
        """Create a simple icon with QB text"""
        # Create image with green background
        img = Image.new('RGB', (size, size), color='#2c5530')
        draw = ImageDraw.Draw(img)
        
        # Try to use a system font, fallback to default
        try:
            font = ImageFont.truetype("arial.ttf", size//4)
        except:
            font = ImageFont.load_default()
        
        # Draw white circle background
        margin = size // 8
        circle_bbox = [margin, margin, size-margin, size-margin]
        draw.ellipse(circle_bbox, fill='white', outline='#2c5530', width=3)
        
        # Draw QB text
        text = "QB"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (size - text_width) // 2
        y = (size - text_height) // 2 - size//16  # Slight offset up
        
        draw.text((x, y), text, fill='#2c5530', font=font)
        
        # Add small grocery basket emoji effect (simplified)
        basket_y = y + text_height + size//20
        draw.rectangle([x, basket_y, x + text_width, basket_y + 3], fill='#2c5530')
        
        # Save the image
        img.save(f'static/{filename}')
        print(f"Created {filename} ({size}x{size})")
    
    # Create required icon sizes
    icon_sizes = [
        (192, 'icon-192.png'),
        (512, 'icon-512.png'),
        (192, 'icon-maskable-192.png'),
        (512, 'icon-maskable-512.png')
    ]
    
    # Ensure static directory exists
    os.makedirs('static', exist_ok=True)
    
    for size, filename in icon_sizes:
        create_icon(size, filename)
    
    print("All PWA icons created successfully!")
    
except ImportError:
    print("PIL (Pillow) not available - creating simple SVG placeholders instead")
    
    # Create simple HTML placeholders that show as icons
    html_icon = '''<svg width="{size}" height="{size}" xmlns="http://www.w3.org/2000/svg">
    <rect width="{size}" height="{size}" fill="#2c5530"/>
    <circle cx="{center}" cy="{center}" r="{radius}" fill="white" stroke="#2c5530" stroke-width="4"/>
    <text x="{center}" y="{text_y}" text-anchor="middle" font-family="Arial" font-size="{font_size}" font-weight="bold" fill="#2c5530">QB</text>
</svg>'''
    
    os.makedirs('static', exist_ok=True)
    
    sizes = [192, 512]
    for size in sizes:
        svg_content = html_icon.format(
            size=size,
            center=size//2,
            radius=size//3,
            text_y=size//2 + size//12,
            font_size=size//6
        )
        
        # Save as SVG (browsers can use SVG as icons)
        with open(f'static/icon-{size}.png.svg', 'w') as f:
            f.write(svg_content)
        
        # Also save maskable versions
        with open(f'static/icon-maskable-{size}.png.svg', 'w') as f:
            f.write(svg_content)
    
    print("Created SVG icon placeholders (browsers will display them as icons)")
    
except Exception as e:
    print(f"Error creating icons: {e}")
    
    # Create minimal text files as last resort
    os.makedirs('static', exist_ok=True)
    for size in [192, 512]:
        with open(f'static/icon-{size}.png', 'w') as f:
            f.write(f"QuickBasket Icon {size}x{size}")
        with open(f'static/icon-maskable-{size}.png', 'w') as f:
            f.write(f"QuickBasket Maskable Icon {size}x{size}")
    
    print("Created text placeholders for icons")