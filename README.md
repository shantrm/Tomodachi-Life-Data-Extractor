# Tomodachi Life Data Extractor

Extract and convert all Miis from Tomodachi Life save files to Mii Studio format.

Place your save file in the `SaveFile` folder, then run:

```bash
python extract_and_convert_all.py [region] [max_miis]
```

Example:
```bash
python extract_and_convert_all.py EU
```

Each Mii gets its own folder in `extracted_miis/` with:
- [name].json - Complete Mii data
- [name].mnms - Mii Studio format file
- face.png - Face render image
- body.png - Body render image

Requirements: Python 3.6+, requests, kaitaistruct, pycryptodome

MASSIVE THANKS to BrionJV HEYimHeroic!! :)

Check out their projects, which I used, here:

https://github.com/Brionjv/Tomodachi-Life-Save-Editor#

https://github.com/HEYimHeroic/mii2studio#