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
py msb.py -e <game code> <"msb_dir_path"> <"xlsx_dir_path">
```
Since op codes, characters, buttons are mapped differently depending on the game, only supported games can have their text exported and reimported. Here are the supported games so far (the font mapping may be off sometimes):

| Game   | Code |
|---      |---    |
|Famicom Detective Club: The Missing Heir|FDC1
|Famicom Detective Club: The Girl Who Stands Behind|FDC2
|Famicom Detective Club: Emio - The Smiling Man|FDC3
|Never 7: The End of Infinity|Never7
|Ever 17: The Out of Infinity|Ever17

The nametags will also be exported in a speakers.xlsx file. By translating it you will be able to batch translate the nametags in all the Excel files.

Batch import text to msb files:

```
py msb.py -i <game code> <"msb_dir_path"> <"xlsx_dir_path">
```
The font.txt file in profiles/game_code is used to convert characters to the custom encoding used by MAGES. If you added new characters to the font by replacing another character, you need to modify the font.txt accordingly (for example, if you replaced the A by a œ in the font image, you need to replace the A of the font.txt file by a œ).

Batch translate the nametags in all Excel files, using the speakers.xlsx file:

```
py msb.py -s <"xlsx_dir_path"> <"speakers_file_path">
```

## SCX files

Instead of using msb files, so games store the text directly in script files (.scx)

Batch export scx files to xlsx:

```
py scx.py -e <game code> <"scx_dir_path"> <"xlsx_dir_path">
```
Since op codes, characters, buttons are mapped differently depending on the game, only supported games can have their text exported and reimported. Here are the supported games so far (the font mapping may be off sometimes):

| Game   | Code |
|---      |---    |
|CHAOS;CHILD|CHAOS

The nametags will also be exported in a speakers.xlsx file. By translating it you will be able to batch translate the nametags in all the Excel files.

Batch import text to scx files:

```
py scx.py -i <game code> <"scx_dir_path"> <"xlsx_dir_path">
```

Batch translate the nametags in all Excel files, using the speakers.xlsx file:

```
py scx.py -s <"xlsx_dir_path"> <"speakers_file_path">
```

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