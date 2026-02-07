from utils import EndianBinaryFileUpdater, EndianBinaryFileReader, load_font_txt, write_font_txt
import json
import sys

FONT_DATA_OFFSET = 0x1B0E8D
GLYPH_COUNT = 0x400

def export_font_metrics(game_code : str, main_path : str, json_path : str):
    font = load_font_txt(game_code)

    with EndianBinaryFileReader(main_path) as f:
        f.seek(FONT_DATA_OFFSET)
        width = [f.read_Int8() for _ in range(GLYPH_COUNT)]
        height = [f.read_Int8() for _ in range(GLYPH_COUNT)]
        unk2 = [f.read_Int8() for _ in range(GLYPH_COUNT)]
        x_off = [f.read_Int8() for _ in range(GLYPH_COUNT)]
        y_off = [f.read_Int8() for _ in range(GLYPH_COUNT)]

    chars = [font[i] for i in range(GLYPH_COUNT)]

    json_data = [
            {
            "char" : chars[i],
            "width" : width[i],
            "height" : height[i],
            "unk2" : unk2[i],
            "x_off" : x_off[i],
            "y_off" : y_off[i]
            } for i in range(GLYPH_COUNT)]

    json.dump(json_data, open(json_path, mode='x', encoding='utf-8'), ensure_ascii=False, indent=5)

def import_font_metrics(game_code : str, json_path : str, main_path : str):
    json_data = json.load(open(json_path, mode='r', encoding='utf-8'))
    with EndianBinaryFileUpdater(main_path) as f:
        f.seek(FONT_DATA_OFFSET)
        for glyph in json_data: f.write_Int8(glyph['width'])
        for glyph in json_data: f.write_Int8(glyph['height'])
        for glyph in json_data: f.write_Int8(glyph['unk2'])
        for glyph in json_data: f.write_Int8(glyph['x_off'])
        for glyph in json_data: f.write_Int8(glyph['y_off'])
    chars = ''
    for glyph in json_data: chars += glyph['char']
    write_font_txt(game_code, chars)

def main():
    args = sys.argv
    if args[1] == '-e':
        export_font_metrics(args[2], args[3], args[4])
        print(f'Successfully exported font to {args[4]}!')

    elif args[1] == '-i':
        import_font_metrics(args[2], args[3], args[4])
        print(f'Successfully imported new font to {args[4]} and imported new characters to font.txt!')
    else:
        print('Error: expected either -e or -i argument')

if __name__ == '__main__':
    main()