# MAGES-Tools

Collection of tools to modify some file formats from MAGES (ex 5pb.) engine.

## MPK files

Mpk is the main archive format.

Batch export files from mpk archives:

```
py mpk.py -e <mpk_dir_path> <output_dir_path>
```

Batch import files to mpk archives:

```
py mpk.py -i <mpk_dir_path> <output_dir_path>
```

Only the files that you modified need to be in the output directory, you can delete files you don't need to modify to speed up the process.

## MSB files

Msb files contain the text of the game.

Batch export msb files to xlsx:

```
py msb.py -e <game code> <msb_dir_path> <xlsx_dir_path>
```

Since op codes, characters, buttons are mapped differently depending on the game, only supported games can have their text exported and reimported. Here are the supported games so far (the font mapping may be off sometimes):

| Game   | Code |
|---      |---    |
|Famicom Detective Club: The Missing Heir|FDC1
|Famicom Detective Club: The Girl Who Stands Behind|FDC2
|Famicom Detective Club: Emio - The Smiling Man|FDC3
|Never 7: The End of Infinity|Never7
|Ever 17: The Out of Infinity|Ever17

The font.txt file in profiles/game_code is used to convert characters to the custom encoding used by MAGES. If you added new characters to the font by replacing another character, you need to modify the font.txt accordingly (for example, if you replaced the A by a œ in the font image, you need to replace the A of the font.txt file by a œ).

Batch import text to msb files:

```
py msb.py -i <game code> <msb_dir_path> <xlsx_dir_path>
```

During export, the nametags will also be written in a speakers.xlsx file. By translating it you will be able to batch translate the nametags in all the Excel files.

Batch translate the nametags in all Excel files, using the speakers.xlsx file:

```
py msb.py -s <xlsx_dir_path> <speakers_file_path>
```

## SCX files

Instead of using msb files, some games store the text directly in script files (.scx).

Importing and exporting is virtually the same as msb files, so everything that's in the previous section also applies here.

Batch export scx files to xlsx:

```
py scx.py -e <game code> <scx_dir_path> <xlsx_dir_path>
```
Supported games:

| Game   | Code |
|---      |---    |
|CHAOS;CHILD|CHAOS
|STEIN;GATE|GATE
|STEIN;GATE 0|GATE0

Batch import text to scx files:

```
py scx.py -i <game code> <scx_dir_path> <xlsx_dir_path>
```

Batch translate the nametags in all Excel files, using the speakers.xlsx file:

```
py scx.py -s <xlsx_dir_path> <speakers_file_path>
```

## SFP files

Sfp files are another type of archive, found in FDC3, and containing the data for backgrounds and characters.

Batch export files from sfp archives:

```
py sfp.py -e <sfp_dir_path> <output_dir_path>
```

Batch import files to sfp archives:

```
py sfp.py -i <sfp_dir_path> <output_dir_path>
```

Only the files that you modified need to be in the output directory, you can delete files you don't need to modify to speed up the process.

## MFT files

Mft files contain a font. They are also found in FDC3.

Export the glyphs from a mft file:

```
py mft.py -e <mft_file_path> <glyphs_png_path>
```

## Infinity games font

Export/import glyphs mapping using a json file, and update the font.txt file accordingly, for the Infinity games (Ever17 and Never7)

Export glyphs mapping to json (see above for game codes):

```
py infinityFont.py -e <game code> <font.bin_file_path> <json_path>
```

Import glyphs mapping to a new font.bin file and update font.txt:

```
py infinityFont.py -i <game code> <json_path> <new_font.bin_file_path>
```

## Famicom Detective 1 & 2 Font

Export/import glyphs mapping using a json file, and update the font.txt file accordingly, for Famicom Detective 1 & 2 (english versions)

Since it's bundled in the 'main' compiled (and compressed) code, you need to uncompress and convert it to a .elf file, using nx2elf, and then compress it back, using elf2nso.

Export glyphs mapping to json:

```
py FDCFont.py -e <FDC1|FDC2> <main_elf_file_path> <json_path>
```

Import glyphs mapping to the main.elf file and update font.txt:

```
py FDCFont.py -i <FDC1|FDC2> <json_path> <main_elf_file_path>
```