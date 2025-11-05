# mii2studio

mii2studio is a command-line tool written in Python that can take any Mii from a Wii, 3DS, Wii U, Miitomo, or Switch and output it into a file that [Mii Studio](https://my.nintendo.com/mii) can load. Mii Studio is Nintendo's official online Mii editor.

Furthermore, the tool also outputs a link to the Mii rendered in PNG form, thanks to an API endpoint that Nintendo made. The Miis are encoded and additional parameters for the API can be played with [here](https://pf2m.com/tools/mii/) (facial expressions, showing a full body, renders of multiple 360° angles of a Mii's body, etc).

Also, the tool can print out some useful information about a Mii, like its birthday, height, build, Mii name, gender, favorite color, and more.

Example of a rendered Mii:

![Matt](https://studio.mii.nintendo.com/miis/image.png?data=000f145b5f5e646e49546169687477858e878a87878e969d9c9fa6b3b9c0e5acafb6bbb6bcb6b9b8bebfc3cfd1d9da&type=face&width=512&instanceCount=1)

## How to Use

Command Syntax: `mii2studio <input mii file / qr code / cmoc entry number> <output studio mii file> <input type (wii/3ds/wiiu/miitomo/switchdb/switch/studio)>`

The script can also be ran without parameters, in which it will allow you to input them with text.

## Examples

* Using a Mii binary file from a Wii: `python mii2studio.py /path/to/MichaelTutori.rcd /path/to/MichaelTutori.mnms wii`
* Using a 3DS QR Code: `python mii2studio.py "https://cdn.discordapp.com/attachments/687051755174887425/729799032561729597/sensei01_Michael_Tutori.JPG" /path/to/MichaelTutori.mnms 3ds`
* Using a Check Mii Out Channel entry number: `python mii2studio.py 4661-9722-1903 /path/to/MichaelTutori.mnms wii`

The script will output a .mnms file, along with image URLs of the Mii's face and body rendered as PNGs, and some useful information about the Mii. It will also print the Mii Studio code, ready to be copy/pasted into the site using my [Mii Studio Mii Loader](https://github.com/HEYimHeroic/MiiStudioMiiLoader).

## Input Types

You can use almost every Mii format with this script:

* Mii binary files from many platforms
    * Wii
    * DS
    * Wii U/3DS (after countless revisions from myself...)
    * SwitchDB
        * Mii format used in the Mii DB on the Switch NAND
    * Switch
        * Mii format used in save files in Switch games
    * Mii Studio
        * Currently broken for some reason.
* Mii QR Codes from many platforms
    * 3DS
    * Wii U
    * Miitomo
    * Tomodachi Life
    * Miitopia

For a complete list on the differences of all Mii data file format types, see [here](https://github.com/HEYimHeroic/MiiDataFiles#types).

## Kaitai

[Kaitai](https://kaitai.io/) is an incredibly useful tool that can document file structures and read them. We use them to document the Mii file structures,. The .ksy file is in the Kaitai language, and the .py is used at runtime for Python scripts (and can be compiled with [Kaitai's IDE](https://ide.kaitai.io/)).

## Credits

* [bendevnull](https://github.com/bendevnull) for his support.
* [HEYimHeroic](https://github.com/HEYimHeroic) for writing the Kaitais for Switch, SwitchDB, and Mii Studio (and fixing larsen's terrible Wii U/3DS Kaitai).
* [jaames](https://github.com/jaames) for the [Mii QR decrypting script](https://gist.github.com/jaames/96ce8daa11b61b758b6b0227b55f9f78).
* Larsenv for writing this script. (Some of it, anyways... his code has broken so much, it'd be untrue to say he was the only one.)
* Matthe815 for figuring out the obfuscation used for the Mii Studio renderer.
