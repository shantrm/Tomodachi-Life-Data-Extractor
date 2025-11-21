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

# Favorite color mappings (from save editor code)
FAVORITE_COLORS = {
    0: "Red",
    1: "Orange",
    2: "Yellow",
    3: "Light Green",
    4: "Green",
    5: "Blue",
    6: "Light Blue",
    7: "Pink",
    8: "Purple",
    9: "Brown",
    10: "White",
    11: "Black"
}

# Gesture/Emotion mappings (from save editor designer code)
GESTURE_EMOTIONS = {
    0: "Normal",
    1: "Happy",
    2: "Angry",
    3: "Sad",
    4: "In love"
}

# Food ID to name mappings (from save editor designer and SelectedIndexChanged handlers)
# Food names list and ID mappings extracted from TLSE_miifoods.Designer.vb and TLSE_miifoods.vb
FOOD_NAMES = [
    "Ice cream cone", "Apple pie", "Strawberry", "Prawn pilaf", "Green tea", "Omelette", "Orange juice", "Castella cake",
    "Chocolate gateau", "Mouldy bread", "Fried chicken", "Spaghetti carbonara", "Quiche", "Mushroom", "Caviar", "Milk",
    "Spoilt milk", "Gummy candy", "Gratin", "Creamy stew", "Crepe", "Grapefruit", "Croissant", "Tea", "Coffee", "Rice",
    "Croquettes", "Cherries", "Salad", "Sandwich", "Grilled marckerel", "Baked potato", "Strawberry shortcake", "White bread",
    "Watermelon", "Tap water", "Steak", "Sausage", "Soft serve ice cream", "Tacos", "Chocolate", "Chocolate sundae",
    "Red chilli pepper", "Tofu", "Corn on the cob", "Doughnut", "Banana", "Banana skin", "Spring rolls", "Cheeseburger",
    "Rissole", "Pizza", "Cracker", "Grapes", "French fries", "Creme caramel", "Blue cheese", "French toast", "Lollipop",
    "Crisps", "Drumstick", "Macadamia nuts", "Spaghetti bolognese", "Orange", "Fried egg", "Peach", "Cooked aubergine",
    "Hard-boiled egg", "Apple", "Meat and patato stew", "Tomato juice", "Avocado", "Bacon", "Broccoli", "Squid rings",
    "Roast chestnuts", "Candyfloss", "Cappuccino", "Coconut", "Corn flakes", "Birthday cake", "Cheesecake", "Kiwi",
    "Lasagne", "Macaron", "Meatballs", "Melon", "Custard slice", "Muffin", "Raw oyster", "Paella", "Space food",
    "Peanuts", "Pear", "Pretzel", "Risotto", "Roast beef", "Salami", "Escargot", "Spaghetti peperoncino",
    "Squid-ink spaghetti", "Tiramisu", "Toffee apple", "Truffle", "Roast turkey", "Waffle", "Yogurt", "Jelly", "Cola",
    "Pancakes", "Instant noodles", "Popcorn", "Garlic", "Stuffed cabbage roll", "Protein shake", "Tomato", "Apple juice",
    "Mango", "Hot dog", "Cheese", "Parma ham", "Pineapple", "Salmon meuniere", "Chilli prawns", "Peking duck", "Octopus",
    "Green pepper", "Stewed beef", "Handmade chocolate", "Pot-au-feu", "Ruined meal", "Barbecued meat", "Yakitori",
    "Onion gratin soup", "Celery", "Box of chocolates", "Smoothie", "Expresso", "Honey", "Doner kebab", "Lemonade",
    "Olives", "Polenta", "Ravioli", "Schnitzel", "Roast chicken", "Tortilla", "Scone", "Smoked salmon", "Sunflower seeds",
    "Chamomile tea", "Hot chocolate", "Black Forest gateau", "Prawn salad", "Pork cutlet", "Herring", "Liquorice",
    "Mashed potato", "Pasta pesto", "Danish pastry", "Porridge", "Brussels sprouts", "Clotted cream", "Gingerbread cake",
    "Panini", "Fudge", "Fishcakes", "Fried seafood", "Olivier salad", "Pain au chocolat", "Yule log", "Roast lamb",
    "English breakfast", "Marron", "Pandoro", "Panettone", "Beans on toast", "Cherimoya", "Bacalao", "Cornish pasty",
    "Turron", "Fried sardines", "Bundt cake", "Roast duck", "Hake fillet", "Natillas", "Custard pastry", "Rollmop herrings",
    "Ham and asparagus", "Baguette", "Borscht", "Cannoli", "Chilli con carne", "Chicken tikka masala", "Couscous",
    "Creme brulee", "Fish and chips", "Gazpacho", "Mozzarella salad", "Mussels", "Minestrone", "Panna cotta",
    "Beef bourguignon", "Marzipan fruit", "Gnocchi", "Greek salad", "Hummus", "Melanzane parmigiana", "Mince pie",
    "Rice pudding", "Sauerkraut", "Christmas pudding", "Souffle", "Churros", "Iberian ham", "Dates", "Mozzarella",
    "Pistachios", "Pork pie", "Walnuts", "Grated carrot", "Ratatouille", "Sparkling water", "Spinach", "Tapas",
    "Bread with chocolate spread", "Courgette", "Gherkins", "Saltimbocca", "Profiteroles", "Mint sweet", "Nothing", "-Wrong ID-"
]

# Food ID mappings: Item index -> Food ID (from Select_fav_1_SelectedIndexChanged for EU)
FOOD_ID_MAPPING = {
    0: 0, 1: 2, 2: 5, 3: 10, 4: 16, 5: 20, 6: 23, 7: 26, 8: 27, 9: 29, 10: 31, 11: 32, 12: 34, 13: 36, 14: 38, 15: 40,
    16: 42, 17: 44, 18: 45, 19: 46, 20: 47, 21: 48, 22: 49, 23: 50, 24: 51, 25: 53, 26: 54, 27: 56, 28: 58, 29: 61,
    30: 62, 31: 63, 32: 66, 33: 67, 34: 69, 35: 70, 36: 73, 37: 76, 38: 77, 39: 80, 40: 86, 41: 87, 42: 89, 43: 90,
    44: 91, 45: 92, 46: 96, 47: 97, 48: 98, 49: 99, 50: 100, 51: 101, 52: 102, 53: 103, 54: 104, 55: 105, 56: 106,
    57: 107, 58: 108, 59: 109, 60: 110, 61: 112, 62: 114, 63: 115, 64: 117, 65: 119, 66: 122, 67: 123, 68: 126,
    69: 132, 70: 135, 71: 136, 72: 137, 73: 138, 74: 139, 75: 140, 76: 141, 77: 142, 78: 143, 79: 144, 80: 146,
    81: 147, 82: 148, 83: 149, 84: 150, 85: 151, 86: 152, 87: 153, 88: 154, 89: 155, 90: 156, 91: 157, 92: 158,
    93: 159, 94: 160, 95: 161, 96: 162, 97: 163, 98: 164, 99: 165, 100: 166, 101: 167, 102: 168, 103: 169, 104: 170,
    105: 171, 106: 172, 107: 173, 108: 174, 109: 175, 110: 178, 111: 180, 112: 182, 113: 183, 114: 185, 115: 186,
    116: 187, 117: 188, 118: 189, 119: 190, 120: 191, 121: 192, 122: 193, 123: 194, 124: 195, 125: 197, 126: 198,
    127: 199, 128: 200, 129: 201, 130: 202, 131: 205, 132: 210, 133: 216, 134: 218, 135: 222, 136: 229, 137: 230,
    138: 231, 139: 232, 140: 233, 141: 234, 142: 235, 143: 236, 144: 237, 145: 238, 146: 239, 147: 240, 148: 241,
    149: 242, 150: 243, 151: 244, 152: 245, 153: 246, 154: 247, 155: 248, 156: 249, 157: 250, 158: 251, 159: 252,
    160: 253, 161: 297, 162: 298, 163: 299, 164: 300, 165: 301, 166: 302, 167: 303, 168: 304, 169: 305, 170: 306,
    171: 307, 172: 308, 173: 309, 174: 310, 175: 311, 176: 312, 177: 314, 178: 315, 179: 316, 180: 317, 181: 318,
    182: 319, 183: 320, 184: 321, 185: 322, 186: 323, 187: 324, 188: 325, 189: 326, 190: 327, 191: 328, 192: 329,
    193: 330, 194: 331, 195: 332, 196: 333, 197: 334, 198: 335, 199: 336, 200: 337, 201: 338, 202: 340, 203: 342,
    204: 343, 205: 344, 206: 345, 207: 346, 208: 347, 209: 348, 210: 349, 211: 350, 212: 354, 213: 355, 214: 356,
    215: 357, 216: 358, 217: 359, 218: 360, 219: 361, 220: 362, 221: 363, 222: 364, 223: 365, 224: 366, 225: 367,
    226: 368, 227: 369, 228: 370, 229: 371, 230: 381, 231: 65535
}

# Build reverse mapping: Food ID -> Food Name
FOOD_IDS = {}
for item_index, food_id in FOOD_ID_MAPPING.items():
    if item_index < len(FOOD_NAMES):
        FOOD_IDS[food_id] = FOOD_NAMES[item_index]

# Add fallback: if ID is not in mapping, try using it as direct array index
# Some food IDs in save files are stored as direct indices into FOOD_NAMES
for food_id in range(len(FOOD_NAMES)):
    if food_id not in FOOD_IDS:
        FOOD_IDS[food_id] = FOOD_NAMES[food_id]

# Add special cases
FOOD_IDS[0] = "Nothing"
FOOD_IDS[65535] = "Nothing"

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
            'status': {},
            'personality': {},
            'relationships': {},
            'personality_type': None,
            'total_size': 0  # Will be calculated after extraction
        }
        
        # ===== PROFILE DATA =====
        # Offsets from TLSE_miiprofile.vb (EU/US/KR)
        # Base: 0x1C8A for mii 0, each mii is 0x660 bytes apart
        profile_base = base  # 0x1C8A for mii 0
        
        # Calculate relative offsets from profile_base (0x1C8A for mii 0)
        result['profile'] = {
            'nickname': self._read_unicode_string(profile_base, 10),
            'firstname': self._read_unicode_string(profile_base + 0x46, 15),  # 0x1CD0 - 0x1C8A = 0x46
            'lastname': self._read_unicode_string(profile_base + 0x66, 15),    # 0x1CF0 - 0x1C8A = 0x66
            'pronunciation_nickname': self._read_unicode_string(profile_base + 0x1C6, 20),  # 0x1E50 - 0x1C8A = 0x1C6 (20 chars)
            'pronunciation_firstname': self._read_unicode_string(profile_base + 0x208, 30),  # 0x1E92 - 0x1C8A = 0x208 (30 chars)
            'pronunciation_lastname': self._read_unicode_string(profile_base + 0x24A, 30),  # 0x1ED4 - 0x1C8A = 0x24A (30 chars)
            'creator': self._read_unicode_string(profile_base + 0x2E, 10),   # 0x1CB8 - 0x1C8A = 0x2E
            # Gender: byte at 0x1C88, only last bit (bit 0) is used (0=male, 1=female)
            # Bits 1-7 are reserved/unknown
            'gender': self._read_byte(profile_base - 0x2) & 0x01,  # 0x1C88 - 0x1C8A = -0x2, extract bit 0
            # Favorite color: byte at 0x1C89, bits 2-5 contain the color value (0-11)
            # Bits 0-1 and 6-7 are reserved/unknown
            'favorite_color': (fav_color_val := (self._read_byte(profile_base - 0x1) >> 2) & 0x0F),  # 0x1C89 - 0x1C8A = -0x1, extract bits 2-5
            'favorite_color_name': FAVORITE_COLORS.get(fav_color_val, f"Unknown ({fav_color_val})"),  # Color name from mapping
            'sharing': self._read_byte(profile_base + 0x16),          # 0x1CA0 - 0x1C8A = 0x16
            'copying': self._read_byte(profile_base - 0x19),          # 0x1C71 - 0x1C8A = -0x19
            'relation_to_you': self._read_byte(profile_base + 0x2A3),         # 0x1F2D - 0x1C8A = 0x2A3
            'grow_kid': self._read_byte(profile_base + 0x624),               # 0x22AE - 0x1C8A = 0x624
            'mii_sysid': self._read_hex_string(profile_base - 0x16, 4),       # 0x1C74 - 0x1C8A = -0x16, 4 bytes (8 hex chars)
            'tomodachi_life_mii_sysid': self._read_hex_string(profile_base + 0xDE, 4),  # 0x1D68 - 0x1C8A = 0xDE, 4 bytes (8 hex chars)
            'origin_island': self._read_byte(profile_base + 0xCE),            # 0x1D58 - 0x1C8A = 0xCE
            'actual_island': self._read_byte(profile_base + 0xBE)             # 0x1D48 - 0x1C8A = 0xBE
        }
        
        # ===== STATUS DATA =====
        # Offsets from TLSE_miistatus.vb (EU/US/KR), Else clause starting at line 2919
        # Base: 0x1C8A for mii 0, each mii is 0x660 bytes apart
        # Calculate relative offsets from profile_base (0x1C8A for mii 0)
        # Catchphrase order: 1=Regular, 2=Happy, 3=Sad, 4=Mad/Angry, 5=Worried
        result['status'] = {
            'level': self._read_byte(profile_base + 0x99),           # 0x1F23 - 0x1C8A = 0x99
            'experience': self._read_byte(profile_base + 0x98),      # 0x1F22 - 0x1C8A = 0x98
            'hair_color': self._read_byte(profile_base + 0x89),      # 0x1D13 - 0x1C8A = 0x89
            'pampered_ranking': self._read_uint32(profile_base + 0x9A),  # 0x1F24 - 0x1C8A = 0x9A (UInt32)
            'splurge_ranking': self._read_uint32(profile_base + 0x626),  # 0x22B0 - 0x1C8A = 0x626 (UInt32)
            'catchphrases': {
                'catchphrase': self._read_unicode_string(profile_base + 0x96, 16),   # 0x1D20 - 0x1C8A = 0x96 (Regular catchphrase)
                'happy_phrase': self._read_unicode_string(profile_base + 0x13A, 16),  # 0x1DC4 - 0x1C8A = 0x13A (Happy phrase)
                'sad_phrase': self._read_unicode_string(profile_base + 0x15C, 16),  # 0x1DE6 - 0x1C8A = 0x15C (Sad phrase)
                'mad_phrase': self._read_unicode_string(profile_base + 0x17E, 16),  # 0x1E08 - 0x1C8A = 0x17E (Mad/Angry phrase)
                'worried_phrase': self._read_unicode_string(profile_base + 0x1A0, 16)   # 0x1E2A - 0x1C8A = 0x1A0 (Worried phrase)
            },
            'gestures': {
                'gesture_1': self._read_byte(profile_base + 0x8C),   # 0x1F16 - 0x1C8A = 0x8C
                'gesture_2': self._read_byte(profile_base + 0x8D),   # 0x1F17 - 0x1C8A = 0x8D
                'gesture_3': self._read_byte(profile_base + 0x8E),   # 0x1F18 - 0x1C8A = 0x8E
                'gesture_4': self._read_byte(profile_base + 0x8F),   # 0x1F19 - 0x1C8A = 0x8F
                'gesture_5': self._read_byte(profile_base + 0x90)    # 0x1F1A - 0x1C8A = 0x90
            }
        }
        
        # ===== FOOD PREFERENCES =====
        # Estimated EU offsets based on relative position from profile base
        # JP: Profile base=0x1C5A, Food base=0x2198, relative=0x53E
        # EU: Profile base=0x1C8A, Estimated food base=0x1C8A+0x53E=0x21C8
        # EU uses 0x660 spacing between miis (vs JP's 0x590)
        # Note: These are ESTIMATED offsets - not explicitly documented in save editor
        def get_food_name(food_id: int) -> str:
            """Get food name from ID"""
            if food_id == 0:
                return "Nothing"
            if food_id == 65535:
                return "Nothing"
            return FOOD_IDS.get(food_id, f"Unknown ({food_id})")
        
        if self.region in ['EU', 'US', 'KR']:
            # Estimated EU/US/KR offsets - found through pattern matching
            # Food data appears to be at profile_base + 0x5D0 for Mii 0
            # EU uses 0x660 spacing between miis
            food_base_eu = profile_base + 0x5D0 + (mii_index * 0x660)
            
            # Read food IDs (all UInt16) - same relative pattern as JP
            allfav_1_id = self._read_uint16(food_base_eu + 0x0)  # Base
            worst_2_id = self._read_uint16(food_base_eu + 0x2)   # +0x2
            allfav_2_id = self._read_uint16(food_base_eu + 0x4)  # +0x4
            worst_1_id = self._read_uint16(food_base_eu + 0x6)   # +0x6
            fav_1_id = self._read_uint16(food_base_eu + 0x8)     # +0x8
            fav_2_id = self._read_uint16(food_base_eu + 0xA)     # +0xA
            fav_3_id = self._read_uint16(food_base_eu + 0xC)     # +0xC
            
            # Read checktummy and fullness (bytes) - estimated relative offsets
            # Need to find these - trying relative to food base
            checktummy = self._read_byte(food_base_eu - 0x26)    # Estimated
            fullness = self._read_byte(food_base_eu - 0x5)       # Estimated
        else:
            # JP offsets (documented)
            food_base_jp = 0x2198 + (mii_index * 0x590)  # JP uses 0x590 spacing
            
            allfav_1_id = self._read_uint16(food_base_jp + 0x0)
            worst_2_id = self._read_uint16(food_base_jp + 0x2)
            allfav_2_id = self._read_uint16(food_base_jp + 0x4)
            worst_1_id = self._read_uint16(food_base_jp + 0x6)
            fav_1_id = self._read_uint16(food_base_jp + 0x8)
            fav_2_id = self._read_uint16(food_base_jp + 0xA)
            fav_3_id = self._read_uint16(food_base_jp + 0xC)
            checktummy = self._read_byte(food_base_jp - 0x26)
            fullness = self._read_byte(food_base_jp - 0x5)
        
        result['food_preferences'] = {
            'all_time_favorites': {
                'favorite_1': {
                    'id': allfav_1_id,
                    'name': get_food_name(allfav_1_id)
                },
                'favorite_2': {
                    'id': allfav_2_id,
                    'name': get_food_name(allfav_2_id)
                }
            },
            'current_favorites': {
                'favorite_1': {
                    'id': fav_1_id,
                    'name': get_food_name(fav_1_id)
                },
                'favorite_2': {
                    'id': fav_2_id,
                    'name': get_food_name(fav_2_id)
                },
                'favorite_3': {
                    'id': fav_3_id,
                    'name': get_food_name(fav_3_id)
                }
            },
            'worst_foods': {
                'worst_1': {
                    'id': worst_1_id,
                    'name': get_food_name(worst_1_id)
                },
                'worst_2': {
                    'id': worst_2_id,
                    'name': get_food_name(worst_2_id)
                }
            },
            'checktummy': checktummy,
            'fullness': fullness
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

