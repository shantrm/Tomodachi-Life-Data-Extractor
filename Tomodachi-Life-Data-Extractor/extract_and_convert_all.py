#!/usr/bin/env python3
"""
Tomodachi Life Data Extractor - Master Script
Extracts all Mii data and converts to Mii Studio format in one go
"""

import sys
import subprocess
from pathlib import Path

def main():
    # Get script directory and SaveFile folder
    script_dir = Path(__file__).parent
    save_file_dir = script_dir.parent / "SaveFile"
    
    # Look for save file in SaveFile folder
    save_files = list(save_file_dir.glob("*.txt")) + list(save_file_dir.glob("*.sav"))
    
    if not save_files:
        print("=" * 70)
        print("ERROR: No save file found!")
        print("=" * 70)
        print(f"\nPlease place your Tomodachi Life save file in:")
        print(f"  {save_file_dir}")
        print("\nThe script will automatically detect and use it.")
        sys.exit(1)
    
    if len(save_files) > 1:
        print("=" * 70)
        print("Multiple save files found. Using the first one:")
        print("=" * 70)
        for sf in save_files:
            print(f"  - {sf.name}")
        print()
    
    save_file = save_files[0]
    region = sys.argv[1] if len(sys.argv) > 1 else "EU"
    max_miis = sys.argv[2] if len(sys.argv) > 2 else "100"
    
    extract_script = script_dir / "extract_full_mii_data.py"
    convert_script = script_dir / "convert_all_miis.py"
    
    # Determine output folder (extracted_miis will be created in script_dir)
    output_folder = script_dir / "extracted_miis"
    
    print("=" * 70)
    print("Tomodachi Life Data Extractor - Complete Pipeline")
    print("=" * 70)
    print(f"Save file: {save_file.name} (from SaveFile folder)")
    print(f"Region: {region}")
    print(f"Output folder: {output_folder}\n")
    
    # Step 1: Extract all Mii data
    print("=" * 70)
    print("STEP 1: Extracting Mii Data")
    print("=" * 70)
    print()
    
    extract_cmd = [
        sys.executable,
        str(extract_script),
        str(save_file),
        "all",
        region,
        max_miis
    ]
    
    extract_result = subprocess.run(extract_cmd, cwd=str(script_dir))
    
    if extract_result.returncode != 0:
        print("\n✗ Extraction failed!")
        sys.exit(1)
    
    print("\n✓ Extraction complete!\n")
    
    # Step 2: Convert all Miis to Mii Studio format
    print("=" * 70)
    print("STEP 2: Converting to Mii Studio Format")
    print("=" * 70)
    print()
    
    convert_cmd = [
        sys.executable,
        str(convert_script),
        str(save_file),
        str(output_folder),
        region
    ]
    
    convert_result = subprocess.run(convert_cmd, cwd=str(script_dir))
    
    if convert_result.returncode != 0:
        print("\n✗ Conversion failed!")
        sys.exit(1)
    
    print("\n" + "=" * 70)
    print("✓ COMPLETE! All Miis extracted and converted!")
    print("=" * 70)
    print(f"\nOutput folder: {output_folder}")
    print("\nEach Mii folder contains:")
    print("  - [name].json - Complete Mii data")
    print("  - [name].mnms - Mii Studio format file")
    print("  - face.png - Face render image")
    print("  - body.png - Body render image")
    print("  - _summary.json - Overview of all Miis")

if __name__ == "__main__":
    main()

