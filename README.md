# MAGES-Tools

Collection of tools to modify some file formats from MAGES (ex 5pb.) engine.

## MPK files

Mpk is the main archive format.

Batch export files from mpk archives:

```
py mpk.py -e <"mpk_dir_path"> <"output_dir_path">
```

Batch import files to mpk archives:

```
py mpk.py -i <"mpk_dir_path"> <"output_dir_path">
```

Only the files that you modified need to be in the output directory, you can delete files you don't need to modify to speed up the process.

## MSB files

Msb files contain the text of the game.

Batch export msb files to xlsx:

```
py msb.py -e <version> <"msb_dir_path"> <"xlsx_dir_path">
```

Batch import text to msb files:

```
py msb.py -e <version> <"msb_dir_path"> <"xlsx_dir_path">
```

Version is either 1 or 2:

- 1 means the characters are encoded in 2 bytes. Presumably, it's used for games that don't have all three of Japanese, Chinese and Korean languages.

- 2 means the characters are encoded in 4 bytes. Presumably, it's used for games that have at least Japanese, Korean, Chinese languages.

The font.txt file is used to convert characters to the custom encoding used by MAGES. If you added new characters to the font by replacing another character, you need to modify the font.txt accordingly (for example, if you replaced the A by a œ in the font image, you need to replace the A of the font.txt file by a œ).

Even if the file contains another language, in msb files the name of the person talking is always in Japanese. While exporting msb files, a speakers.txt file will be created. If you want to translate easily the name of the speakers in your xlsx file, modify this speaker file by replacing the names at the right of the "=" characters by your translation, and run:

```
py msb.py -speakers <"xlsx_dir_path"> <"speakers.txt_file_path">
```

Note that the only thing imported to the msb files will be the text in the Translation column, the rest is only here for context.

## SFP files

Sfp files are another type of archive, containing the data for backgrounds and characters.

Batch export files from sfp archives:

```
py sfp.py -e <"sfp_dir_path"> <"output_dir_path">
```

Batch import files to sfp archives:

```
py sfp.py -i <"sfp_dir_path"> <"output_dir_path">
```

Only the files that you modified need to be in the output directory, you can delete files you don't need to modify to speed up the process.

## MFT files

Mft files contain a font.

Export the glyphs from a mft file:

```
py mft.py -e <"mft_file_path"> <"glyphs_png_path">
```