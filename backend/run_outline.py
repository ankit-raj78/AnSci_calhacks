#!/usr/bin/env python3
"""
Script to run the outline generation from the ansci package
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ansci.outline import generate_outline

if __name__ == "__main__":
    # Import the test data from outline.py
    from ansci.outline import pdf_url, pdf_data, history
    
    print("Generating outline...")
    result = generate_outline(history)
    
    if result:
        print("Outline generated successfully:")
        print(f"Title: {result.title}")
        print(f"Number of blocks: {len(result.blocks)}")
        for i, block in enumerate(result.blocks):
            print(f"Block {i+1}: {block.content[:100]}...")
    else:
        print("Failed to generate outline") 