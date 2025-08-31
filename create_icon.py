#!/usr/bin/env python3
"""
Create custom purple Wireshark W icon for desktop shortcuts
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_wireshark_icon():
    """Create a purple W icon for Wireshark Monitor"""
    
    # Create a 512x512 image with transparent background
    size = 512
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Purple color scheme
    purple_dark = (102, 51, 153)    # Dark purple
    purple_light = (153, 102, 204)  # Light purple
    purple_accent = (204, 153, 255) # Accent purple
    
    # Draw background circle
    margin = 20
    circle_size = size - (margin * 2)
    draw.ellipse([margin, margin, margin + circle_size, margin + circle_size], 
                fill=purple_dark, outline=purple_light, width=8)
    
    # Draw the "W" letter
    font_size = int(size * 0.6)  # 60% of image size
    
    # Try to use a system font, fallback to default
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
    except:
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
    
    # Get text dimensions
    text = "W"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Center the text
    x = (size - text_width) // 2
    y = (size - text_height) // 2 - 20  # Slight upward adjustment
    
    # Draw text with shadow effect
    shadow_offset = 4
    draw.text((x + shadow_offset, y + shadow_offset), text, font=font, fill=(0, 0, 0, 128))
    draw.text((x, y), text, font=font, fill=purple_accent)
    
    # Add small network/monitoring elements around the W
    # Draw small dots representing network nodes
    dot_positions = [
        (100, 100), (400, 100), (100, 400), (400, 400),
        (250, 80), (250, 430), (80, 250), (430, 250)
    ]
    
    for pos in dot_positions:
        draw.ellipse([pos[0]-8, pos[1]-8, pos[0]+8, pos[1]+8], 
                    fill=purple_light, outline=purple_accent, width=2)
    
    # Draw connecting lines (network visualization)
    line_color = (*purple_light, 128)  # Semi-transparent
    draw.line([(100, 100), (250, 80)], fill=line_color, width=3)
    draw.line([(400, 100), (250, 80)], fill=line_color, width=3)
    draw.line([(100, 400), (250, 430)], fill=line_color, width=3)
    draw.line([(400, 400), (250, 430)], fill=line_color, width=3)
    
    return img

def create_icns_file(png_path, icns_path):
    """Convert PNG to ICNS format for macOS"""
    try:
        # Use macOS iconutil to create ICNS
        iconset_path = icns_path.replace('.icns', '.iconset')
        os.makedirs(iconset_path, exist_ok=True)
        
        # Create different sizes for iconset
        sizes = [16, 32, 64, 128, 256, 512, 1024]
        img = Image.open(png_path)
        
        for size in sizes:
            resized = img.resize((size, size), Image.Resampling.LANCZOS)
            resized.save(f"{iconset_path}/icon_{size}x{size}.png")
            
            # Create @2x versions for retina
            if size <= 512:
                resized_2x = img.resize((size*2, size*2), Image.Resampling.LANCZOS)
                resized_2x.save(f"{iconset_path}/icon_{size}x{size}@2x.png")
        
        # Convert iconset to icns
        os.system(f"iconutil -c icns '{iconset_path}' -o '{icns_path}'")
        
        # Clean up iconset directory
        os.system(f"rm -rf '{iconset_path}'")
        
        return True
    except Exception as e:
        print(f"Error creating ICNS: {e}")
        return False

def main():
    print("🎨 Creating custom Wireshark Monitor icon...")
    
    # Create the icon
    icon = create_wireshark_icon()
    
    # Save as PNG
    png_path = "wireshark_monitor_icon.png"
    icon.save(png_path, "PNG")
    print(f"✅ Created PNG icon: {png_path}")
    
    # Create ICNS for macOS app bundle
    icns_path = "wireshark_monitor_icon.icns"
    if create_icns_file(png_path, icns_path):
        print(f"✅ Created ICNS icon: {icns_path}")
    else:
        print("⚠️ Could not create ICNS file")
    
    # Copy to app bundle
    app_bundle = "./Wireshark Monitor.app/Contents/Resources"
    os.makedirs(app_bundle, exist_ok=True)
    
    try:
        os.system(f"cp '{icns_path}' '{app_bundle}/AppIcon.icns'")
        print(f"✅ Copied icon to app bundle")
    except Exception as e:
        print(f"⚠️ Could not copy to app bundle: {e}")
    
    print("🎉 Icon creation completed!")

if __name__ == "__main__":
    main()
