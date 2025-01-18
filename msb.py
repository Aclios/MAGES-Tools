from utils import EndianBinaryFileReader, EndianBinaryFileWriter, EndianBinaryStreamWriter, TextStreamReader
import os
import sys
from pathlib import Path
import pandas as pd
from msb_enums import msb_codes, msb_buttons, msb_spec_chars

assert Path('font.txt').exists(), "A font.txt file is required in the active directory"
font = open("font.txt",'r',encoding='utf-8-sig').read().replace('\r','').replace('\n','').replace(' ', '').replace('_', ' ')

class MSB:
    def __init__(self, filepath : str, version : int):
        with EndianBinaryFileReader(filepath) as f:
            self.version = version
            assert version in [1, 2]
            self.filename = Path(filepath).name
            self.magic = f.check_magic(b'MES\x00')
            self.unk = f.read_UInt32()
            self.entry_count = f.read_UInt32()
            self.data_start_offset = f.read_UInt32()
            self.entries = [MSBEntry(f, self.version, self.data_start_offset) for _ in range(self.entry_count)]

    def write_excel(self, out_dir : str):
        out_path = Path(out_dir) / (self.filename + '.xlsx')
        data = [[entry.type, entry.speaker, entry.string, entry.string] for entry in self.entries]
        columns = ["Type", "Speaker", "Original", "Translation"]
        df = pd.DataFrame(data=data, columns=columns)
        df.to_excel(out_path)
                   
    def load_excel(self, excel_file : str):
        df = pd.read_excel(excel_file, index_col = 0, dtype = str, na_filter = False)
        assert len(df["Translation"]) == self.entry_count, f'Number of entries in the Translation column ({len(df["Translation"])}) don\'t match number of entries in the files {self.entry_count}'
        for idx, data in enumerate(df["Translation"]):
            self.entries[idx].string = str(data)

    def save(self, out_filepath):
        with EndianBinaryFileWriter(out_filepath) as f:
            f.write(self.magic)
            f.write_UInt32(self.unk)
            f.write_UInt32(self.entry_count)
            f.write_UInt32(self.data_start_offset)
            f.write(b"\x00" * 8 * self.entry_count)
            for idx, entry in enumerate(self.entries):
                offset = f.tell()
                f.write(entry.to_bytes())
                pos = f.tell()
                f.seek(0x10 + 8 * idx)
                f.write_UInt32(entry.unk)
                if entry.is_invalid:
                    f.write_UInt32(0xFF_FF_FF_FF)
                else:
                    f.write_UInt32(offset - self.data_start_offset)
                f.seek(pos)

    def get_speakers(self):
        speakers = set()
        for entry in self.entries:
            if entry.speaker != '':
                speakers.add(entry.speaker)
        return speakers

    def set_speakers(self, speakers : dict):
        for entry in self.entries:
            if entry.speaker in speakers:
                entry.speaker = speakers[entry.speaker]

class MSBEntry:
    type : str = "static"
    speaker : str = ""
    def __init__(self, f : EndianBinaryFileReader, version : int, data_start_offset : int):
        self.version = version
        self.data_start_offset = data_start_offset
        self.unk = f.read_UInt32() # ?
        self.data_offset = f.read_UInt32()
        if self.data_offset == 0xFF_FF_FF_FF:
            self.is_invalid = True
            self.string = ""
            self.has_three = False
        else:
            self.is_invalid = False
            f.set_endianness('big')
            self.read_data(f)
            f.set_endianness('little')
    
    def read_data(self, f : EndianBinaryFileReader):
        self.string = ""
        self.speaker = ""
        self.has_three = False
        pos = f.tell()
        f.seek(self.data_start_offset + self.data_offset)
        val = f.read_UInt8()
        while True:
            match val:
                case 0x01: #speaker name (in Japanese) if it's a dialogue entry
                    self.type = "dialogue"
                    self.speaker, val = self.decode_string(f)
                case 0x02: #text
                    self.string, val = self.decode_string(f)
                case 0x03:  #it's a flag
                    self.has_three = True
                    break
                case 0xff: #end of section
                    break
                case _: #entry with text only (UI text)
                    f.seek(-1, 1)
                    self.string, val = self.decode_string(f)
        f.seek(pos)

    def decode_string(self, f : EndianBinaryFileReader) -> str:
        color_flag = False
        out_string = ""
        val = f.read_UInt8()
        while True:

            if val in [1, 2, 3, 0xff]:
                break

            elif val >= 0x80:
                f.seek(-1, 1)
                if self.version == 1:
                    idx = f.read_UInt16() - 0x8000 #16 bits per char
                elif self.version == 2:
                    idx = f.read_UInt32() - 0x80_00_00_00 #32 bits per chat

                if idx in msb_buttons:
                    out_string += f"<{msb_buttons[idx]}>"
                elif idx in msb_spec_chars:
                    out_string += msb_spec_chars[idx]
                else:
                    assert idx < len(font), f"Char number {idx} is beyond font table length"
                    out_string += font[idx]

            elif val == 0:
                out_string += '\n'

            elif val in msb_codes:
                name, arg_count = msb_codes[val]

                if val == 4 and not color_flag:
                    arg_count = 4
                    color_flag = True
                elif val == 4 and color_flag:
                    arg_count = 3  
                    color_flag = False

                if arg_count == 0:
                    out_string += f"<{name}>"
                else:
                    args = [str(f.read_UInt8()) for _ in range(arg_count)]
                    out_string += f"<{name}:{','.join(args)}>"

            else:
                raise Exception(f"Unknown code value {hex(val)} at offset {hex(f.tell())}")
            
            val = f.read_UInt8()
        return out_string, val
    
    def encode_string(self, string : str) -> bytes:
        reverse_msb_codes = {v[0] : k for k, v in msb_codes.items()}
        reverse_msb_buttons = {v : k for k, v in msb_buttons.items()}
        reverse_msb_spec_chars = {v : k for k, v in msb_spec_chars.items()}
        out_stream = EndianBinaryStreamWriter(endianness = 'big')
        stream = TextStreamReader(string)
        char = stream.read(1)

        while char != "":
            if char == "<":
                code = stream.readUntilOccurrence('>')
                name = code.split(':')[0]

                if name in reverse_msb_codes:
                    out_stream.write_UInt8(reverse_msb_codes[name])
                elif name in reverse_msb_buttons:
                    if self.version == 1:
                        out_stream.write_UInt16(0x8000 + reverse_msb_buttons[name])
                    elif self.version == 2:
                        out_stream.write_UInt32(0x80_00_00_00 + reverse_msb_buttons[name])
                else:
                    raise Exception(f"Unknown tag {code}")
                
                if ':' in code:
                    args = code.split(':')[1].split(',')
                    for arg in args:
                        out_stream.write_UInt8(int(arg))
            else:
                if char == '\n':
                    out_stream.write_UInt8(0)
                elif char == '\r':
                    pass
                elif char not in font and char not in reverse_msb_spec_chars:
                    print(f"WARNING: The character {char} isn't in the font.txt file, you need to add it at the right place. It has been skipped.")
                else:
                    if char in reverse_msb_spec_chars:
                        val = reverse_msb_spec_chars[char]
                    else:
                        val = font.index(char)
                    if self.version == 1:
                        out_stream.write_UInt16(0x8000 + val)
                    elif self.version == 2:
                        out_stream.write_UInt32(0x80_00_00_00 + val)

            char = stream.read(1)
        return out_stream.getvalue()

    def to_bytes(self) -> bytes:
        stream = EndianBinaryStreamWriter()
        if self.type == "dialogue":
            stream.write_UInt8(1)
            stream.write(self.encode_string(self.speaker))
            stream.write_UInt8(2)
        stream.write(self.encode_string(self.string))
        if self.has_three:
            stream.write_UInt8(3)
        if not self.is_invalid:
            stream.write_UInt8(0xff)
        return stream.getvalue()

def write_speakers(filepath : str, speakers : set):
    with open(filepath, mode='w', encoding='utf-8') as f:
        for speaker in speakers:
            f.write(f"{speaker}={speaker}\n")

def load_speakers(filepath : str):
    speakers = {}
    with open(filepath, mode = 'r', encoding = 'utf-8') as f:
        lines = f.readlines()
        for line in lines:
            try:
                data = line.replace('\n', '').replace('\r', '')
                speak_jp, speak_trad = data.split('=')
                speakers[speak_jp] = speak_trad
            except:
                pass
    return speakers

def convert_speakers(xlsx_dir : str, speakers_path : str):
    print("Converting speakers...")
    speakers = load_speakers(speakers_path)
    for file in os.listdir(xlsx_dir):
        if file.endswith('.xlsx'):
            df = pd.read_excel(Path(xlsx_dir) / file, index_col = 0, dtype = str, na_filter = False)
            for idx, speaker in enumerate(df["Speaker"]):
                if speaker in speakers:
                    df["Speaker"][idx] = speakers[speaker]
            df.to_excel(Path(xlsx_dir) / file)
    print("Done!")

def batch_export(version : int, input_dir : str, extraction_dir : str):
    speakers = set()
    os.makedirs(extraction_dir, exist_ok=True)

    for file in os.listdir(input_dir):
        if file.lower().endswith('.msb'):
            print(f"Exporting {Path(input_dir) / file}...")
            msb = MSB(Path(input_dir) / file, version)
            speakers |= msb.get_speakers()           
            msb.write_excel(extraction_dir)

    print("Writing speakers file...")
    write_speakers(Path(extraction_dir) / "speakers.txt", speakers)
    print("Done!")

def batch_import(version : int, input_dir : str, extraction_dir : str):
    for file in os.listdir(input_dir):
        if file.lower().endswith('.msb'):
            msb = MSB(Path(input_dir) / file, version)
            print(f"Importing text to {Path(input_dir) / file}...")
            msb.load_excel(Path(extraction_dir) / (file + '.xlsx'))
            msb.save(Path(input_dir) / file)
    print("Done!")

def main():
    args = sys.argv
    if args[1] == '-e':
        batch_export(int(args[2]), args[3], args[4])
    elif args[1] == '-i':
        batch_import(int(args[2]), args[3], args[4])
    elif args[1] == '-speakers':
        convert_speakers(args[2], args[3])
    else:
        return
    
if __name__ == '__main__':
    main()