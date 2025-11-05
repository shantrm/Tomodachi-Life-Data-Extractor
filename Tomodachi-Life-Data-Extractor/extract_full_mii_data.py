#!/usr/bin/env python3
"""
Tomodachi Life Save Editor - Complete Mii Data Extractor
Extracts ALL possible information about a single Mii from save files
"""

import json
import struct
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

# Relationship type mappings
RELATIONSHIP_TYPES = {
    0: "Unknown",
    1: "Friend",
    2: "Lover",
    3: "Ex",
    4: "Spouse",
    5: "Spouse (1)",
    6: "Ex-spouse",
    7: "Parent/Child",
    8: "Sibling",
    9: "Friend (in conflict)",
    10: "Lover (in conflict)",
    11: "Spouse (in conflict)",
    12: "Best friend"
}

class CompleteMiiExtractor:
    def __init__(self, file_path: str, region: Optional[str] = None):
        self.file_path = Path(file_path)
        self.region = region or "EU"  # Default to EU/US/KR
        self.data = None
        
    def read_file(self):
        """Read the save file into memory"""
        with open(self.file_path, 'rb') as f:
            self.data = f.read()
        print(f"Read {len(self.data)} bytes from {self.file_path}")
        return len(self.data)
    
    def _read_byte(self, offset: int) -> int:
        """Read a single byte"""
        if offset >= len(self.data):
            return 0
        return struct.unpack('<B', self.data[offset:offset+1])[0]
    
    def _read_uint16(self, offset: int) -> int:
        """Read a 16-bit unsigned integer (little-endian)"""
        if offset + 2 > len(self.data):
            return 0
        return struct.unpack('<H', self.data[offset:offset+2])[0]
    
    def _read_uint32(self, offset: int) -> int:
        """Read a 32-bit unsigned integer (little-endian)"""
        if offset + 4 > len(self.data):
            return 0
        return struct.unpack('<I', self.data[offset:offset+4])[0]
    
    def _read_unicode_string(self, offset: int, max_length: int) -> str:
        """Read a Unicode string (little-endian UTF-16)"""
        try:
            chars = []
            for i in range(max_length):
                pos = offset + (i * 2)
                if pos + 2 > len(self.data):
                    break
                char_code = struct.unpack('<H', self.data[pos:pos+2])[0]
                if char_code == 0:
                    break
                try:
                    # Handle valid Unicode characters, skip surrogates
                    if 0xD800 <= char_code <= 0xDFFF:
                        continue  # Skip surrogate pairs
                    char = chr(char_code)
                    # Only add printable characters
                    if char.isprintable() or char == ' ':
                        chars.append(char)
                    else:
                        break
                except (ValueError, OverflowError):
                    break
            result = ''.join(chars).strip('\0')
            # Clean up any remaining invalid characters
            return result.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')
        except:
            return ""
    
    def _read_hex_string(self, offset: int, length: int) -> str:
        """Read a hex string"""
        if offset + length > len(self.data):
            return ""
        return ''.join(f'{b:02X}' for b in self.data[offset:offset+length])
    
    def get_base_offset(self, mii_index: int) -> int:
        """Get base offset for a mii (EU/US/KR uses 0x660 increment)"""
        # Mii 0 starts at 0x1C8A (for names), personality at 0x1D80
        # Each mii block is 0x660 bytes
        return 0x1C8A + (mii_index * 0x660)
    
    def calculate_personality_type(self, traits: Dict[str, int]) -> str:
        """
        Calculate personality type from trait values using the official Tomodachi Life grid chart.
        
        Based on the chart:
        - Movement = Energy (0-8, where 0=Slow, 8=Quick)
        - Speech = Speech (0-8, but skips 4: 0,1,2,3,5,6,7,8)
        - Expressiveness = Facialexpressions (0-8, where 0=Flat, 8=Varied)
        - Attitude = Mood (0-8, but skips 4: 0,1,2,3,5,6,7,8)
        - Overall = NOT used for personality determination
        
        The personality is determined by:
        - Horizontal axis = Movement + Speech (0-15)
        - Vertical axis = Expressiveness + Attitude (0-15)
        
        Grid ranges:
        Row 1 (Expressiveness + Attitude > 11):
          - Movement + Speech < 4: Easygoing Softie
          - Movement + Speech (3-7): Easygoing Optimist
          - Movement + Speech (7-11): Outgoing Trendsetter
          - Movement + Speech > 11: Outgoing Entertainer
        
        Row 2 (Expressiveness + Attitude 7-11):
          - Movement + Speech < 4: Easygoing Buddy
          - Movement + Speech (3-7): Easygoing Dreamer
          - Movement + Speech (7-11): Outgoing Charmer
          - Movement + Speech > 11: Outgoing Leader
        
        Row 3 (Expressiveness + Attitude 3-7):
          - Movement + Speech < 4: Independent Free Spirit
          - Movement + Speech (3-7): Independent Artist
          - Movement + Speech (7-11): Confident Designer
          - Movement + Speech > 11: Confident Adventurer
        
        Row 4 (Expressiveness + Attitude < 4):
          - Movement + Speech < 4: Independent Lone Wolf
          - Movement + Speech (3-7): Independent Thinker
          - Movement + Speech (7-11): Confident Brainiac
          - Movement + Speech > 11: Confident Go-getter
        """
        # Map traits to chart values
        # Values are already in correct ranges:
        # Energy: 0-7 (Movement)
        # Speech: 0-3, 5-8 (skips 4)
        # Facialexpressions: 0-7 (Expressiveness)
        # Mood: 0-3, 5-8 (skips 4) (Attitude)
        
        movement = traits.get('Energy', 0)  # Already 0-7
        speech = traits.get('Speech', 0)    # Already 0-3, 5-8 (no 4)
        expressiveness = traits.get('Facialexpressions', 0)  # Already 0-7
        attitude = traits.get('Mood', 0)    # Already 0-3, 5-8 (no 4)
        
        # Values are already validated in extract_single_mii, but ensure they're in range
        movement = max(0, min(7, movement))
        expressiveness = max(0, min(7, expressiveness))
        
        # Speech and Mood should already be valid (0-3, 5-8), but ensure
        if speech == 4:
            speech = 5
        speech = max(0, min(8, speech))
        if speech > 3 and speech < 5:
            speech = 5
        
        if attitude == 4:
            attitude = 5
        attitude = max(0, min(8, attitude))
        if attitude > 3 and attitude < 5:
            attitude = 5
        
        # Calculate axes
        horizontal = movement + speech  # Movement + Speech (0-16, but chart shows 0-15)
        vertical = expressiveness + attitude  # Expressiveness + Attitude (0-16, but chart shows 0-15)
        
        # Clamp to chart range (0-15)
        horizontal = min(15, horizontal)
        vertical = min(15, vertical)
        
        # Determine personality type based on grid
        # Row 1: Expressiveness + Attitude (Vertical > 11)
        if vertical > 11:
            if horizontal < 4:
                return "Easygoing Softie"
            elif 3 < horizontal < 8:
                return "Easygoing Optimist"
            elif 7 < horizontal < 12:
                return "Outgoing Trendsetter"
            else:  # horizontal >= 12
                return "Outgoing Entertainer"
        
        # Row 2: Expressiveness + Attitude (7 < Vertical < 12)
        elif 7 < vertical < 12:
            if horizontal < 4:
                return "Easygoing Buddy"
            elif 3 < horizontal < 8:
                return "Easygoing Dreamer"
            elif 7 < horizontal < 12:
                return "Outgoing Charmer"
            else:  # horizontal >= 12
                return "Outgoing Leader"
        
        # Row 3: Expressiveness + Attitude (3 < Vertical < 8)
        elif 3 < vertical < 8:
            if horizontal < 4:
                return "Independent Free Spirit"
            elif 3 < horizontal < 8:
                return "Independent Artist"
            elif 7 < horizontal < 12:
                return "Confident Designer"
            else:  # horizontal >= 12
                return "Confident Adventurer"
        
        # Row 4: Expressiveness + Attitude (Vertical < 4)
        else:  # vertical <= 3
            if horizontal < 4:
                return "Independent Lone Wolf"
            elif 3 < horizontal < 8:
                return "Independent Thinker"
            elif 7 < horizontal < 12:
                return "Confident Brainiac"
            else:  # horizontal >= 12
                return "Confident Go-getter"
    
    def extract_single_mii(self, mii_index: int) -> Dict:
        """Extract ALL data for a single Mii"""
        if not self.data:
            self.read_file()
        
        base = self.get_base_offset(mii_index)
        
        result = {
            'mii_index': mii_index,
            'profile': {},
            'personality': {},
            'relationships': {},
            'personality_type': None,
            'total_size': 0  # Will be calculated after extraction
        }
        
        # ===== PROFILE DATA =====
        # Offsets from TLSE_miiprofile.vb (EU/US/KR)
        profile_base = base  # 0x1C8A for mii 0
        result['profile'] = {
            'nickname': self._read_unicode_string(profile_base, 10),
            'firstname': self._read_unicode_string(profile_base + 0x46, 15),  # 0x1CD0 - 0x1C8A = 0x46
            'lastname': self._read_unicode_string(profile_base + 0x66, 15),    # 0x1CF0 - 0x1C8A = 0x66
            'creator': self._read_unicode_string(profile_base + 0x2E, 10),   # 0x1CB8 - 0x1C8A
            'favorite_color': self._read_byte(profile_base - 0x1),            # 0x1C89 - 0x1C8A
            'relation_to_you': self._read_byte(profile_base + 0x2A3),         # 0x1F2D - 0x1C8A
            'grow_kid': self._read_byte(profile_base + 0x624)               # 0x22AE - 0x1C8A
        }
        
        # ===== PERSONALITY DATA =====
        # Base offset for personality: 0x1D80 for mii 0
        personality_base = 0x1D80 + (mii_index * 0x660)
        
        # Read raw byte values
        energy_raw = self._read_byte(personality_base + 0x0)
        speech_raw = self._read_byte(personality_base + 0x1)
        facial_raw = self._read_byte(personality_base + 0x2)
        mood_raw = self._read_byte(personality_base + 0x3)
        overall_raw = self._read_byte(personality_base + 0x4)
        
        # Use raw byte values directly
        energy = energy_raw - 1
        facialexpressions = facial_raw - 1
        
        # Speech and Mood (Attitude): if raw value < 5, subtract 1; otherwise leave as-is
        speech = speech_raw - 1 if speech_raw < 5 else speech_raw
        mood = mood_raw - 1 if mood_raw < 5 else mood_raw
        
        personality_traits = {
            'Energy': energy,
            'Speech': speech,
            'Facialexpressions': facialexpressions,
            'Mood': mood,
            'Overall': overall_raw,  # Overall not used in personality calculation but kept for reference
            'Pitch': self._read_byte(personality_base - 0x6),
            'Speed': self._read_byte(personality_base - 0x5),
            'Quality': self._read_byte(personality_base - 0x4),
            'Tone': self._read_byte(personality_base - 0x3),
            'Accent': self._read_byte(personality_base - 0x2),
            'Intonation': self._read_byte(personality_base - 0x1)
        }
        
        result['personality'] = {
            'traits': personality_traits,
            'type': self.calculate_personality_type(personality_traits)
        }
        result['personality_type'] = result['personality']['type']
        
        # ===== RELATIONSHIPS =====
        # Extract relationships with all other miis
        relationships = {}
        rel_base = 0x299F0 + (mii_index * 0x100)
        
        # First, get all mii names for relationship display
        mii_names = {}
        for i in range(100):
            try:
                name_offset = 0x1C8A + (i * 0x660)
                name = self._read_unicode_string(name_offset, 10)
                if name and name.strip():
                    mii_names[i] = name
            except:
                pass
        
        # Extract relationships
        for target_mii in range(100):
            try:
                valrela_offset = rel_base + target_mii
                rela_offset = rel_base + 0x64 + target_mii
                
                rel_value = self._read_byte(valrela_offset)
                rel_type = self._read_byte(rela_offset)
                
                if rel_value > 0 or rel_type > 0:
                    target_name = mii_names.get(target_mii, f"Mii {target_mii}")
                    relationships[target_mii] = {
                        'value': rel_value,
                        'type': rel_type,
                        'type_name': RELATIONSHIP_TYPES.get(rel_type, f"Unknown ({rel_type})"),
                        'target_name': target_name
                    }
            except:
                continue
        
        result['relationships'] = relationships
        result['relationship_count'] = len(relationships)
        
        # Calculate total size (approximate JSON size)
        json_str = json.dumps(result, ensure_ascii=False)
        result['total_size'] = len(json_str.encode('utf-8'))
        
        return result
    
    def extract_all_miis(self, max_miis: int = 100) -> Dict:
        """Extract data for all Miis"""
        if not self.data:
            self.read_file()
        
        print(f"Extracting data for up to {max_miis} Miis...\n")
        
        all_data = {
            'region': self.region,
            'file_path': str(self.file_path),
            'file_size': len(self.data),
            'total_miis': 0,
            'miis': {}
        }
        
        # First, collect all Mii names for relationship lookups
        mii_names = {}
        for i in range(max_miis):
            try:
                name_offset = 0x1C8A + (i * 0x660)
                name = self._read_unicode_string(name_offset, 10)
                if name and name.strip():
                    mii_names[i] = name
            except:
                pass
        
        # Extract data for each Mii
        extracted_count = 0
        for mii_index in range(max_miis):
            try:
                # Check if Mii exists by checking if name exists or personality data exists
                name = mii_names.get(mii_index)
                if not name:
                    # Check personality data to see if Mii exists
                    personality_base = 0x1D80 + (mii_index * 0x660)
                    energy = self._read_byte(personality_base)
                    if energy == 0:
                        continue  # Skip empty Mii slots
                    name = f"Mii {mii_index}"
                
                print(f"Extracting Mii {mii_index}: {name}")
                mii_data = self.extract_single_mii(mii_index)
                all_data['miis'][str(mii_index)] = mii_data
                extracted_count += 1
                
            except Exception as e:
                print(f"Error extracting mii {mii_index}: {e}")
                continue
        
        all_data['total_miis'] = extracted_count
        return all_data


def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_full_mii_data.py <save_file> [mii_index|all] [region] [max_miis]")
        print("  save_file: Path to the save file")
        print("  mii_index: Index of the Mii to extract (0-based) OR 'all' to extract all Miis")
        print("  region: Optional - EU, US, JP, or KR (default: EU)")
        print("  max_miis: Optional - Maximum number of Miis to extract when using 'all' (default: 100)")
        sys.exit(1)
    
    save_file = sys.argv[1]
    mii_arg = sys.argv[2] if len(sys.argv) > 2 else "all"
    region = sys.argv[3] if len(sys.argv) > 3 else "EU"
    max_miis = int(sys.argv[4]) if len(sys.argv) > 4 else 100
    
    extractor = CompleteMiiExtractor(save_file, region)
    
    print("=" * 60)
    print("Tomodachi Life - Complete Mii Data Extractor")
    print("=" * 60)
    print(f"Save file: {save_file}")
    print(f"Region: {region}\n")
    
    try:
        if mii_arg.lower() == "all":
            # Extract all Miis
            print("Extracting ALL Miis...\n")
            all_data = extractor.extract_all_miis(max_miis)
            
            # Create output folder for individual Mii files
            output_dir = Path(__file__).parent
            miis_folder = output_dir / "extracted_miis"
            miis_folder.mkdir(exist_ok=True)
            
            # Save each Mii to its own JSON file (inside a per-Mii subfolder)
            print(f"\nSaving individual Mii files to: {miis_folder} (one subfolder per Mii)\n")
            total_size = 0
            for mii_id, mii_data in all_data['miis'].items():
                # Create a safe filename from the Mii's nickname
                nickname = mii_data.get('profile', {}).get('nickname', f'Mii_{mii_id}')
                # Sanitize filename (remove invalid characters)
                safe_nickname = "".join(c for c in nickname if c.isalnum() or c in (' ', '-', '_')).strip()
                if not safe_nickname:
                    safe_nickname = f"Mii_{mii_id}"
                # Create subfolder per Mii (folder uses display name, file uses lowercase name.json)
                mii_subfolder = miis_folder / safe_nickname
                mii_subfolder.mkdir(exist_ok=True)
                json_filename = f"{safe_nickname.lower()}.json"
                json_file = mii_subfolder / json_filename
                
                # Add metadata to each Mii's data
                mii_output = {
                    'region': all_data['region'],
                    'save_file_path': all_data['file_path'],
                    'save_file_size': all_data['file_size'],
                    **mii_data  # Include all the Mii data
                }
                
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(mii_output, f, indent=2, ensure_ascii=False)
                
                file_size = json_file.stat().st_size
                total_size += file_size
                print(f"  ✓ Saved Mii {mii_id} ({nickname}): {safe_nickname}/{json_filename} ({file_size:,} bytes)")
            
            # Also create a summary file with overview
            summary_file = miis_folder / "_summary.json"
            summary_data = {
                'region': all_data['region'],
                'save_file_path': all_data['file_path'],
                'save_file_size': all_data['file_size'],
                'total_miis': all_data['total_miis'],
                'total_json_size': total_size,
                'extraction_date': datetime.now().isoformat(),
                'miis': {}
            }
            
            # Add summary info for each Mii (referencing subfolder path)
            for mii_id, mii_data in all_data['miis'].items():
                nickname = mii_data.get('profile', {}).get('nickname', f'Mii_{mii_id}')
                safe_nickname = "".join(c for c in nickname if c.isalnum() or c in (' ', '-', '_')).strip()
                if not safe_nickname:
                    safe_nickname = f"Mii_{mii_id}"
                json_filename = f"{safe_nickname}/{safe_nickname.lower()}.json"
                summary_data['miis'][mii_id] = {
                    'index': int(mii_id),
                    'nickname': nickname,
                    'filename': json_filename,
                    'personality_type': mii_data.get('personality_type', 'Unknown'),
                    'relationship_count': mii_data.get('relationship_count', 0),
                    'total_size': mii_data.get('total_size', 0)
                }
            
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary_data, f, indent=2, ensure_ascii=False)
            
            print(f"\n{'=' * 60}")
            print("Extraction Complete!")
            print(f"{'=' * 60}")
            print(f"Total Miis extracted: {all_data['total_miis']}")
            print(f"Output folder: {miis_folder}")
            print(f"Total size of all JSON files: {total_size:,} bytes ({total_size / 1024:.2f} KB)")
            print(f"Summary file: {summary_file}")
            
            # Show personality type summary
            personality_types = {}
            for mii_id, mii_data in all_data['miis'].items():
                pt = mii_data.get('personality_type', 'Unknown')
                personality_types[pt] = personality_types.get(pt, 0) + 1
            
            print(f"\nPersonality Type Distribution:")
            for pt, count in sorted(personality_types.items()):
                print(f"  {pt}: {count}")
            
            # Check for requested personality types
            found_types = []
            for mii_id, mii_data in all_data['miis'].items():
                pt = mii_data.get('personality_type', '')
                if "Easygoing Softie" in pt or "Independent Free Spirit" in pt:
                    found_types.append((mii_id, mii_data['profile']['nickname'], pt))
            
            if found_types:
                print(f"\n✓ Found {len(found_types)} Mii(s) with requested personality types:")
                for mii_id, name, pt in found_types:
                    print(f"  Mii {mii_id} ({name}): {pt}")
            else:
                print(f"\n(Requested types: 'Easygoing Softie', 'Independent Free Spirit')")
        
        else:
            # Extract single Mii
            mii_index = int(mii_arg)
            print(f"Extracting Mii {mii_index}...\n")
            
            result = extractor.extract_single_mii(mii_index)
            
            # Save to JSON
            output_dir = Path(__file__).parent
            output_file = output_dir / f"mii_{mii_index}_complete_data.json"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"\nSaved complete data to: {output_file}")
            print("\n" + "=" * 60)
            print("Extraction Summary")
            print("=" * 60)
            print(f"Mii Name: {result['profile']['nickname']} ({result['profile']['firstname']} {result['profile']['lastname']})")
            print(f"Personality Type: {result['personality_type']}")
            print(f"Relationships: {result['relationship_count']}")
            print(f"\nPersonality Traits:")
            for trait, value in result['personality']['traits'].items():
                print(f"  {trait}: {value}")
            
            # Check if personality type matches requested types
            personality_type = result['personality_type']
            if "Easygoing Softie" in personality_type or "Independent Free Spirit" in personality_type:
                print(f"\n✓ FOUND REQUESTED PERSONALITY TYPE: {personality_type}")
            else:
                print(f"\nPersonality type detected: {personality_type}")
                print("(Requested types: 'Easygoing Softie', 'Independent Free Spirit')")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

