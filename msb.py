from utils import EndianBinaryFileReader, EndianBinaryFileWriter, EndianBinaryStreamWriter, TextStreamReader
import os
import sys
import json
from pathlib import Path
import pandas as pd

class MSB:
    def __init__(self, filepath : str, game_code : str):
        self.load_profile(game_code)
        with EndianBinaryFileReader(filepath) as f:
            self.filename = Path(filepath).name
            self.magic = f.check_magic(b'MES\x00')
            self.unk = f.read_UInt32()
            self.entry_count = f.read_UInt32()
            self.data_start_offset = f.read_UInt32()
            self.entries = [MSBEntry(f, self.data_start_offset, self.settings, self.font, self.op_codes, self.buttons) for _ in range(self.entry_count)]

    def write_excel(self, out_dir : str):
        out_path = Path(out_dir) / (self.filename + '.xlsx')
        data = [[entry.type, entry.speaker, entry.speaker, entry.string, entry.string, entry.static_code] for entry in self.entries]
        columns = ["Type", "Speaker Original", "Speaker Translation", "Original", "Translation", "Static code"]
        df = pd.DataFrame(data=data, columns=columns)
        df.to_excel(out_path)
                   
    def load_excel(self, excel_file : str):
        df = pd.read_excel(excel_file, index_col = 0, dtype = str, na_filter = False)
        for idx, data in enumerate(df["Translation"]):
            self.entries[idx].string = str(data)
        for idx, speaker in enumerate(df["Speaker Translation"]):
            self.entries[idx].speaker = str(speaker)
        for idx, data in enumerate(df["Static code"]):
            self.entries[idx].static_code = str(data)

    def load_profile(self, game_code : str):
        profile_path = Path('profiles') / game_code
        assert profile_path.exists() , f"Error: No profile found for this game code: {game_code}"
        self.font = open(profile_path / 'font.txt', mode = 'r', encoding = 'utf-8-sig').read().replace('\n','').replace('\r','')
        buttons = json.load(open(profile_path / 'buttons.json', mode = 'r', encoding = 'utf-8'))
        self.buttons = {int(k) : v for k, v in buttons.items()}
        op_codes = json.load(open(profile_path / 'op_codes.json', mode = 'r', encoding = 'utf-8'))
        self.op_codes = {int(k) : v for k, v in op_codes.items()}
        self.settings = json.load(open(profile_path / 'settings.json', mode = 'r', encoding = 'utf-8'))

    def save(self, out_filepath : str):
        with EndianBinaryFileWriter(out_filepath) as f:
            f.write(self.magic)
            f.write_UInt32(self.unk)
            f.write_UInt32(self.entry_count)
            f.write_UInt32(self.data_start_offset)
            entries_data = bytearray()
            for entry in self.entries:
                entry_offset = len(entries_data)
                f.write_UInt32(entry.unk)
                if entry.is_invalid:
                    f.write_UInt32(0xFF_FF_FF_FF)
                else:
                    f.write_UInt32(entry_offset)
                entries_data += entry.to_bytes()
            f.write(entries_data)

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
    is_invalid : bool = False

    def __init__(self, f : EndianBinaryFileReader, data_start_offset : int, settings : dict, font : str, op_codes : dict, buttons : dict):
        self.settings, self.font, self.op_codes, self.buttons = settings, font, op_codes, buttons
        self.data_start_offset = data_start_offset
        self.unk = f.read_UInt32() # ?
        self.data_offset = f.read_UInt32()
        self.string = ""
        self.speaker = ""
        self.static_code = ""

        if self.data_offset != 0xFF_FF_FF_FF:
            f.set_endianness('big')
            pos = f.tell()
            f.seek(self.data_start_offset + self.data_offset)
            self.read_data(f)
            f.seek(pos)
            f.set_endianness('little')

        else:
            self.is_invalid = True
    
    def read_data(self, f : EndianBinaryFileReader):
        val = f.read_UInt8()
        while True:
            match val:
                case 0x01: #speaker name if it's a dialogue entry
                    self.type = "dialogue"
                    self.speaker, val = self.decode_string(f)

                case 0x02: #text if it's a dialogue entry
                    if self.string != "": #very rarely, there is a code before the speaker
                        self.static_code = self.string
                    self.string, val = self.decode_string(f)

                case 0xff: #end of section
                    break

                case _: #entry with text only (UI text)
                    f.seek(-1, 1)
                    self.string, val = self.decode_string(f)

    def decode_string(self, f : EndianBinaryFileReader) -> str:
        color_flag = False
        out_string = ""
        val = f.read_UInt8()
        while True:

            if val in [1, 2, 0xff]:
                break

            elif val >= 0x80:
                f.seek(-1, 1)
                if self.settings["bytes_per_char"] == 2:
                    idx = f.read_UInt16() - 0x8000 #16 bits per char
                elif self.settings["bytes_per_char"] == 4:
                    idx = f.read_UInt32() - 0x80_00_00_00 #32 bits per chat

                if self.font[idx] == chr(0x3000) and idx in self.buttons:
                    out_string += f"<{self.buttons[idx]}>"
                else:
                    assert idx < len(self.font), f"Char number {idx} is beyond font table length"
                    out_string += self.font[idx]

            elif val == 0:
                out_string += '\n'

            elif val in self.op_codes:
                name, arg_count = self.op_codes[val]

                if val == 4 and self.settings["asymetrical_color_code"]: #in Famicom Detective Club, text color op codes have 4 arguments then 3 (annoying)
                    if color_flag:
                        color_flag = False
                    else:
                        arg_count = 4
                        color_flag = True

                if arg_count == 0:
                    out_string += f"<{name}>"
                else:
                    args = [str(f.read_UInt8()) for _ in range(arg_count)]
                    out_string += f"<{name}:{','.join(args)}>"

            else:
                raise Exception(f"Unknown code value {val} at offset {hex(f.tell() - 1)}")
            
            val = f.read_UInt8()
        return out_string, val
    
    def encode_string(self, string : str) -> bytes:
        reverse_op_codes = {v[0] : k for k, v in self.op_codes.items()}
        reverse_buttons = {v : k for k, v in self.buttons.items()}
        out_stream = EndianBinaryStreamWriter(endianness = 'big')
        stream = TextStreamReader(string)
        char = stream.read(1)

        while char != "":
            if char == "<":
                code = stream.readUntilOccurrence('>')
                name = code.split(':')[0]

                if name in reverse_op_codes:
                    out_stream.write_UInt8(reverse_op_codes[name])
                elif name in reverse_buttons:
                    if self.settings["bytes_per_char"] == 2:
                        out_stream.write_UInt16(0x8000 + reverse_buttons[name])
                    elif self.settings["bytes_per_char"] == 4:
                        out_stream.write_UInt32(0x80_00_00_00 + reverse_buttons[name])
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
                elif char not in self.font:
                    print(f"WARNING: The character {char} isn't in the font.txt file, it must be added. It has been ignored.")
                else:
                    val = self.font.index(char)
                    if self.settings["bytes_per_char"] == 2:
                        out_stream.write_UInt16(0x8000 + val)
                    elif self.settings["bytes_per_char"] == 4:
                        out_stream.write_UInt32(0x80_00_00_00 + val)

            char = stream.read(1)
        return out_stream.getvalue()

    def to_bytes(self) -> bytes:

        if self.is_invalid:
            return bytes()
        
        stream = EndianBinaryStreamWriter()
        stream.write(self.encode_string(self.static_code))

        if self.type == "dialogue":
            stream.write_UInt8(1)
            stream.write(self.encode_string(self.speaker))
            stream.write_UInt8(2)
            stream.write(self.encode_string(self.string))
        
        else:
            stream.write(self.encode_string(self.string))

        stream.write_UInt8(0xff)

        return stream.getvalue()

def write_speakers(filepath : str, speakers : list):
    data = [[speakers[idx], speakers[idx]] for idx in range(len(speakers))]
    df = pd.DataFrame(data = data, columns = ["Original", "Translation"])
    df.to_excel(filepath)

def load_speakers(filepath : str):
    speakers = {}
    df = pd.read_excel(filepath)
    for idx in range(len(df["Original"])):
        speakers[df["Original"][idx]] = df["Translation"][idx]
    return speakers

def convert_speakers(xlsx_dir : str, speakers_path : str):
    print("Converting speakers...")
    speaker_trad_map = load_speakers(speakers_path)
    for file in os.listdir(xlsx_dir):
        if file.endswith('.xlsx'):
            df = pd.read_excel(Path(xlsx_dir) / file, index_col = 0, dtype = str, na_filter = False)
            if "Speaker Original" in df.columns:
                for idx, speaker in enumerate(df["Speaker Original"]):
                    if speaker in speaker_trad_map:
                        df["Speaker Translation"][idx] = speaker_trad_map[speaker]
                df.to_excel(Path(xlsx_dir) / file)
    print("Done!")

def batch_export(game_code : str, input_dir : str, extraction_dir : str):
    speakers = set()
    os.makedirs(extraction_dir, exist_ok=True)

    for file in os.listdir(input_dir):
        if file.lower().endswith('.msb'):
            print(f"Exporting {Path(input_dir) / file}...")
            msb = MSB(Path(input_dir) / file, game_code)
            speakers |= msb.get_speakers()           
            msb.write_excel(extraction_dir)

    print("Writing speakers file...")
    write_speakers(Path(extraction_dir) / "speakers.xlsx", list(speakers))
    print("Done!")

def batch_import(game_code : str, input_dir : str, extraction_dir : str):
    for file in os.listdir(input_dir):
        if file.lower().endswith('.msb'):
            msb = MSB(Path(input_dir) / file, game_code)
            print(f"Importing text to {Path(input_dir) / file}...")
            msb.load_excel(Path(extraction_dir) / (file + '.xlsx'))
            msb.save(Path(input_dir) / file)
    print("Done!")

def main():
    args = sys.argv
    if args[1] == '-e':
        batch_export(args[2], args[3], args[4])
    elif args[1] == '-i':
        batch_import(args[2], args[3], args[4])
    elif args[1] == '-s':
        convert_speakers(args[2], args[3])
    else:
        return
    
if __name__ == '__main__':
    main()