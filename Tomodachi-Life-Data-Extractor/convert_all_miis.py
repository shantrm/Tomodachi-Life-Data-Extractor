#!/usr/bin/env python3
"""
Convert all Tomodachi Life Miis to Mii Studio format and download render images
"""

import sys
import json
import subprocess
import re
import requests
from pathlib import Path
from typing import Optional, Tuple

# Add parent directory to path to import mii2studio modules
sys.path.insert(0, str(Path(__file__).parent.parent / "mii2studio"))

def get_mii_offset(mii_index: int, region: str = "EU") -> int:
    """Get the offset for a Mii in the save file"""
    if region == "JP":
        return 0x1C40 + (mii_index * 0x590)
    else:
        return 0x1C70 + (mii_index * 0x660)

def extract_mii_raw(save_file: str, mii_index: int, region: str = "EU") -> bytes:
    """Extract the raw 96-byte (0x60) Mii block from save file"""
    with open(save_file, 'rb') as f:
        data = f.read()
    
    offset = get_mii_offset(mii_index, region)
    
    if offset + 0x60 > len(data):
        raise ValueError(f"Mii {mii_index} offset {hex(offset)} + 0x60 exceeds file size {len(data)}")
    
    mii_data = data[offset:offset + 0x60]
    return mii_data

def convert_mii_to_studio(mii_data: bytes, output_file: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Convert Mii data to Mii Studio format and return Face and Body URLs
    Returns: (face_url, body_url)
    """
    # Save temporary Mii file
    temp_mii_file = Path(output_file).parent / "temp_mii.cfsd"
    with open(temp_mii_file, 'wb') as f:
        f.write(mii_data)
    
    try:
        # Run mii2studio conversion
        mii2studio_path = Path(__file__).parent.parent / "mii2studio" / "mii2studio.py"
        
        result = subprocess.run(
            [sys.executable, str(mii2studio_path), str(temp_mii_file), output_file, "3ds"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            print(f"  ✗ Conversion failed: {result.stderr}")
            return None, None
        
        # Parse output to extract URLs
        output = result.stdout
        face_url = None
        body_url = None
        
        # Look for "Face: " and "Body: " lines
        for line in output.split('\n'):
            if line.startswith('Face: '):
                face_url = line.replace('Face: ', '').strip()
            elif line.startswith('Body: '):
                body_url = line.replace('Body: ', '').strip()
        
        return face_url, body_url
    
    finally:
        # Clean up temporary file
        if temp_mii_file.exists():
            temp_mii_file.unlink()

def download_image(url: str, output_path: Path) -> bool:
    """Download an image from URL and save to file"""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        return True
    except Exception as e:
        print(f"    ✗ Failed to download {output_path.name}: {e}")
        return False

def main():
    if len(sys.argv) < 3:
        print("Usage: python convert_all_miis.py <save_file> <extracted_miis_folder> [region]")
        print("  save_file: Path to Tomodachi Life save file")
        print("  extracted_miis_folder: Path to extracted_miis folder")
        print("  region: Optional - EU, US, JP, or KR (default: EU)")
        sys.exit(1)
    
    save_file = sys.argv[1]
    extracted_miis_folder = Path(sys.argv[2])
    region = sys.argv[3] if len(sys.argv) > 3 else "EU"
    
    if not Path(save_file).exists():
        print(f"Error: Save file not found: {save_file}")
        sys.exit(1)
    
    if not extracted_miis_folder.exists():
        print(f"Error: Extracted Miis folder not found: {extracted_miis_folder}")
        sys.exit(1)
    
    # Read summary file
    summary_file = extracted_miis_folder / "_summary.json"
    if not summary_file.exists():
        print(f"Error: Summary file not found: {summary_file}")
        sys.exit(1)
    
    with open(summary_file, 'r', encoding='utf-8') as f:
        summary = json.load(f)
    
    print("=" * 60)
    print("Tomodachi Life to Mii Studio - Batch Converter")
    print("=" * 60)
    print(f"Save file: {save_file}")
    print(f"Region: {region}")
    print(f"Total Miis: {summary['total_miis']}\n")
    
    # Process each Mii
    success_count = 0
    fail_count = 0
    
    for mii_id, mii_info in summary['miis'].items():
        mii_index = mii_info['index']
        nickname = mii_info['nickname']
        
        print(f"Processing Mii {mii_index} ({nickname})...")
        
        # Get Mii's folder
        safe_nickname = "".join(c for c in nickname if c.isalnum() or c in (' ', '-', '_')).strip()
        if not safe_nickname:
            safe_nickname = f"Mii_{mii_index}"
        
        mii_folder = extracted_miis_folder / safe_nickname
        if not mii_folder.exists():
            print(f"  ⚠ Mii folder not found: {mii_folder}")
            fail_count += 1
            continue
        
        # Extract Mii data from save file
        try:
            mii_data = extract_mii_raw(save_file, mii_index, region)
        except Exception as e:
            print(f"  ✗ Failed to extract Mii data: {e}")
            fail_count += 1
            continue
        
        # Convert to Mii Studio format
        output_file = mii_folder / f"{safe_nickname.lower()}.mnms"
        face_url, body_url = convert_mii_to_studio(mii_data, str(output_file))
        
        if face_url is None or body_url is None:
            print(f"  ✗ Conversion failed")
            fail_count += 1
            continue
        
        print(f"  ✓ Converted to: {output_file.name}")
        
        # Download images
        face_file = mii_folder / "face.png"
        body_file = mii_folder / "body.png"
        
        print(f"  Downloading images...")
        face_success = download_image(face_url, face_file)
        body_success = download_image(body_url, body_file)
        
        if face_success and body_success:
            print(f"  ✓ Downloaded face.png and body.png")
            success_count += 1
        else:
            print(f"  ⚠ Some images failed to download")
            if face_success or body_success:
                success_count += 1  # Partial success
            else:
                fail_count += 1
    
    print("\n" + "=" * 60)
    print("Conversion Complete!")
    print("=" * 60)
    print(f"Successfully converted: {success_count}")
    print(f"Failed: {fail_count}")
    print(f"Total: {summary['total_miis']}")

if __name__ == "__main__":
    main()

