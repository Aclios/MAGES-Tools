from utils import EndianBinaryFileReader
from PIL import Image
import zlib
import sys

MAGIC = b'MFNT'

class MFT:
    def __init__(self, filepath : str):
        with EndianBinaryFileReader(filepath) as f:
            f.check_magic(MAGIC)
            self.unk1 = f.read_UInt16()
            self.unk2 = f.read_UInt16()
            self.glyph_width = f.read_UInt16()
            self.glyph_height = f.read_UInt16()
            self.glyph_datasize = self.glyph_width * self.glyph_height
            self.compressed_datasize = f.read_UInt32()

            self.offset1 = f.read_UInt32()
            self.count1 = f.read_UInt32() #?

            self.offset2 = f.read_UInt32()
            self.count2 = f.read_UInt32() #glyph count

            self.offset3 = f.read_UInt32()
            self.count3 = f.read_UInt32()
            assert self.count3 == 0

            self.offset4 = f.read_UInt32()
            self.count4 = f.read_UInt32() #glyph count

            self.offset5 = f.read_UInt32()
            self.count5 = f.read_UInt32()
            assert self.count5 == 0

            self.offset6 = f.read_UInt32()
            self.count6 = f.read_UInt32()
            assert self.count6 == 0

            f.seek(self.offset1)
            self.entries1 = [f.read_UInt16 for _ in range(self.count1)]

            f.seek(self.offset2)
            self.entries2 = [f.read_UInt16 for _ in range(self.count2)]

            f.seek(self.offset4)
            self.glyph_data = zlib.decompress(f.read(self.compressed_datasize))

    def export_glyphs(self, out_path : str):
        width = 64 * self.glyph_width
        height = (self.count2 // 64) * self.glyph_height
        if self.count2 % 64 != 0:
            height += self.glyph_height
        im = Image.new(mode = 'L', size = (width, height))
        for idx in range(self.count4):
            glyph_data = self.glyph_data[self.glyph_datasize * idx : self.glyph_datasize * (idx + 1)]
            glyph = Image.frombytes(mode = 'L', size = (self.glyph_width, self.glyph_height), data = glyph_data)
            im.paste(glyph, box = ((idx % 64) * self.glyph_width, (idx // 64) * self.glyph_height))
        im.save(out_path)

def export_mft(filepath : str, png_filepath : str):
    mft = MFT(filepath)
    mft.export_glyphs(png_filepath)
    print(f"Exported glyphs to {filepath}.")

def main():
    args = sys.argv
    if args[1] == '-e':
        export_mft(args[2], args[3])

if __name__ == '__main__':
    main()