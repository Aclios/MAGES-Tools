from utils import EndianBinaryFileReader, EndianBinaryFileWriter
from PIL import Image
from pathlib import Path
import json
import sys

class InfinityFont:
    def __init__(self, filepath : str, game_code : str):
        self.game_code = game_code
        self.font = open(Path('profiles', game_code, 'font.txt'), mode = 'r', encoding = 'utf-8-sig').read().replace('\n','').replace('\r','')
        if str(filepath).endswith('.json'):
            self.import_json(filepath)
        else:
            with EndianBinaryFileReader(filepath) as f:
                self.entry_count = f.get_filesize() // 16
                self.glyphs = [FontGlyph(f, char = self.font[i], i = i) for i in range(self.entry_count)]


    def reorganize_font(self, out_path : str, font_sheet_filepath : str):
        with Image.open(font_sheet_filepath) as font_sheet:
            max_height = int(max(self.glyphs, key = lambda e: e.height).height * 1.5)
            max_width = int(max(self.glyphs, key = lambda e: e.width).width * 1.5)

            im = Image.new(mode='RGB', size = [64 * max_width, max_height * (self.entry_count // 64) + 1])

            for idx, glyph in enumerate(self.glyphs):
                im.paste(glyph.get_glyph_im(font_sheet), (max_width * (idx % 64), max_height * (idx // 64)))

            im.save(out_path)

    def export_json(self, out_path : str):
        data = {'chars' : [glyph.to_dict() for glyph in self.glyphs]}
        with open(out_path, mode='w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=0)

    def import_json(self, json_path : str):
        with open(json_path, mode='r', encoding='utf-8') as f:
            data = json.load(f)
            self.glyphs = [FontGlyph(glyph_data) for glyph_data in data["chars"]]

    def export_font_txt(self):
        chars = ''
        for glyph in self.glyphs : chars += glyph.char
        with open(Path('profiles', self.game_code, 'font.txt'), mode = 'w', encoding = 'utf-8-sig') as f:
            for i in range(len(chars) // 64):
                f.write(chars[i * 64 : (i + 1) * 64] + '\n')
            if len(chars) % 64 != 0:
                f.write(chars[(i + 1) * 64:])

    def write(self, out_path : str):
        with EndianBinaryFileWriter(out_path) as f:
            for glyph in self.glyphs:
                glyph.write_to(f)

class FontGlyph:
    def __init__(self, f : EndianBinaryFileReader | dict, char : str = '', i : int = 0):
        if isinstance(f, EndianBinaryFileReader):
            self.char = char
            self.idx = i
            self.x_offset = f.read_Int16()
            self.y_offset = f.read_Int16()
            self.x_pos = f.read_Int16()
            self.y_pos = f.read_Int16()
            self.width = f.read_Int16()
            self.height = f.read_Int16()
            self.display_width = f.read_Int16()
            self.display_height = f.read_Int16()

        elif isinstance(f, dict):
            self.from_dict(f)

    def get_glyph_im(self, font_sheet : Image.Image):
        return font_sheet.crop((self.x_pos, self.y_pos, self.x_pos + self.width, self.y_pos + self.height))
    
    def to_dict(self):
        return {
            'idx' : self.idx,
            'char' : self.char,
            'x_offset' : self.x_offset,
            'y_offset' : self.y_offset,
            'x_pos' : self.x_pos,
            'y_pos' : self.y_pos,
            'width' : self.width,
            'height' : self.height,
            'display_width' : self.display_width,
            'display_height' : self.display_height
        }
    
    def from_dict(self, inp : dict):
        self.char = inp['char']
        assert len(self.char) == 1, 'Only one char per glyph!'
        self.idx = inp['idx']
        self.x_offset = inp['x_offset']
        self.y_offset = inp['y_offset']
        self.x_pos = inp['x_pos']
        self.y_pos = inp['y_pos']
        self.width = inp['width']
        self.height = inp['height']
        self.display_width = inp['display_width']
        self.display_height = inp['display_height']

    def write_to(self, f : EndianBinaryFileWriter):
        f.write_Int16(self.x_offset)
        f.write_Int16(self.y_offset)
        f.write_Int16(self.x_pos)
        f.write_Int16(self.y_pos)
        f.write_Int16(self.width)
        f.write_Int16(self.height)
        f.write_Int16(self.display_width)
        f.write_Int16(self.display_height)

def main():
    args = sys.argv
    if args[1] == '-e':
        font = InfinityFont(args[3], args[2])
        font.export_json(args[4])
        print(f'Successfully exported font to {args[4]}!')
    elif args[1] == '-i':
        font = InfinityFont(args[3], args[2])
        font.write(args[4])
        font.export_font_txt()
        print(f'Successfully wrote new font to {args[4]} and imported new characters to font.txt!')
    else:
        print('Error: expected either -e or -i argument')

if __name__ == '__main__':
    main()