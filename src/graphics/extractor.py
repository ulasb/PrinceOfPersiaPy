"""
Graphics Extractor for Prince of Persia (Apple II)

Extracts sprite data from IMG.CHTAB files.
"""

import os
import struct
from PIL import Image
import numpy as np

# All CHTAB files appear to be compiled with a base address of $6000,
# regardless of where they are loaded in memory.
# The game likely relocates them or bank-switches them.
# For extraction, we assume base $6000 to resolve pointers correctly.
BASE_ADDRESS = 0x6000

FILES_TO_EXTRACT = [
    "IMG.CHTAB1",
    "IMG.CHTAB2",
    "IMG.CHTAB3",
    "IMG.CHTAB4.GD",
    "IMG.CHTAB4.SKEL",
    "IMG.CHTAB4.SHAD",
    "IMG.CHTAB4.VIZ",
    "IMG.CHTAB4.FAT",
    "IMG.CHTAB5",
    "IMG.CHTAB6.A",
    "IMG.CHTAB6.B",
    "IMG.CHTAB7",
]

def extract_chtab(filepath, output_dir):
    """
    Extract images from a CHTAB file.
    
    Format:
    - File is a collection of images referenced by a pointer table.
    - Pointer table is implicit? No, likely at start of file or implicitly indexed.
    - Based on analysis: Pointers seem to be at offsets 1, 3, 5... (Image 1, 2, 3...)
    - Pointers are absolute memory addresses (based on LOAD_OFFSET).
    - Image format: [Width: 1 byte] [Height: 1 byte] [Data: W*H bytes]
    """
    filename = os.path.basename(filepath)
    if filename not in FILES_TO_EXTRACT:
        print(f"Skipping {filename}")
        return

    load_offset = BASE_ADDRESS
    
    with open(filepath, 'rb') as f:
        data = f.read()
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Extracting {filename} (Base Address: ${load_offset:04x})...")
    
    # Iterate through potential images
    # We iterate index 1..127 (max likely)
    for index in range(1, 128):
        ptr_offset = (index * 2) - 1
        
        if ptr_offset + 1 >= len(data):
            break
            
        # Read pointer (Little Endian)
        ptr_low = data[ptr_offset]
        ptr_high = data[ptr_offset + 1]
        ptr_addr = (ptr_high << 8) | ptr_low
        
        # Calculate file offset
        img_offset = ptr_addr - load_offset
        
        # Validations
        if img_offset < 0 or img_offset >= len(data):
            # Invalid pointer, might be end of table or unused entry
            # In POP, tables might be sparse or end early. 
            # If we hit an invalid pointer, check if it's 00 00 or garbage.
            continue
            
        # Check if we've seen this offset before (avoid infinite loops/duplicates)
        # (Optional optimization)
        
        # Read Header
        if img_offset + 2 > len(data):
            break
            
        width = data[img_offset]
        height = data[img_offset + 1]
        
        # Heuristic check: Width and Height should be reasonable
        if width == 0 or width > 40 or height == 0 or height > 192:
            # Likely garbage or not an image
            continue
            
        # Read Data
        data_size = width * height
        if img_offset + 2 + data_size > len(data):
            print(f"  Img {index}: Data truncated")
            continue
            
        img_data = data[img_offset + 2 : img_offset + 2 + data_size]
        
        # Create PNG
        # Apple II standard: 7 pixels per byte. Bit 7 is palette control (ignore for shape).
        # We process 7 pixels per byte.
        
        pixel_width = width * 7
        pixel_height = height
        
        # Create a simple bitmap (monochrome)
        img = Image.new('1', (pixel_width, pixel_height), 0)
        pixels = img.load()
        
        for y in range(height):
            for x_byte in range(width):
                byte = img_data[y * width + x_byte]
                # Draw 7 bits (0-6)
                for b in range(7):
                    bit = (byte >> b) & 1
                    # x coordinate: x_byte * 7 + b
                    pixels[x_byte * 7 + b, y] = bit
        
        # Save
        out_name = f"{filename}_img_{index:03d}_{width}x{height}.png"
        img.save(os.path.join(output_dir, out_name))
        
    print(f"  Extracted images to {output_dir}")

if __name__ == "__main__":
    import argparse
    
    # Default paths
    base_src_dir = "source_reference/01 POP Source/Images"
    base_out_dir = "assets/graphics/dump"
    
    files = [
        "IMG.CHTAB1", 
        "IMG.CHTAB2", 
        "IMG.CHTAB3", 
        "IMG.CHTAB4.GD",
        "IMG.CHTAB4.SKEL",
        "IMG.CHTAB4.SHAD",
        "IMG.CHTAB4.VIZ",
        "IMG.CHTAB4.FAT",
        "IMG.CHTAB7"
    ]
    
    for f in FILES_TO_EXTRACT:
        src = os.path.join(base_src_dir, f)
        if os.path.exists(src):
            extract_chtab(src, base_out_dir)
        else:
            print(f"File not found: {src}")
