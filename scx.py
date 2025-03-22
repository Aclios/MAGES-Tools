from utils import EndianBinaryFileReader, EndianBinaryFileWriter
import os
import sys
from pathlib import Path
from msb import MSB, MSBEntry, write_speakers, convert_speakers, load_speakers

class SCX(MSB): #inherit MSB methods
    def __init__(self, filepath : str, game_code : str):
        self.load_profile(game_code)
        with EndianBinaryFileReader(filepath) as f:
            self.filename = Path(filepath).name
            self.magic = f.check_magic(b'SC3\x00')
            self.text_table_offset = f.read_UInt32()
            self.unk_table_offset = f.read_UInt32()
            self.text_entry_count = (self.unk_table_offset - self.text_table_offset) // 4
            self.script_data = f.read(self.text_table_offset - 12)
            self.entries = [SCXTextEntry(f, self.settings, self.font, self.op_codes, self.buttons) for _ in range(self.text_entry_count)]
            f.seek(self.unk_table_offset)
            if len(self.entries) > 0:
                self.unk_table_data = f.read(self.entries[0].data_offset - self.unk_table_offset)
            else:
                f.seek(self.unk_table_offset)
                self.unk_table_data = f.read()

    def save(self, out_filepath : str):
        with EndianBinaryFileWriter(out_filepath) as f:
            f.write(self.magic)
            f.write_UInt32(self.text_table_offset)
            f.write_UInt32(self.unk_table_offset)
            f.write(self.script_data)
            entries_data = bytearray()
            for entry in self.entries:
                entry_offset = self.text_table_offset + 4 * self.text_entry_count + len(self.unk_table_data) + len(entries_data)
                if entry.is_invalid:
                    f.write_UInt32(0xFF_FF_FF_FF)
                else:
                    f.write_UInt32(entry_offset)
                entries_data += entry.to_bytes()
            f.write(self.unk_table_data)
            f.write(entries_data)

class SCXTextEntry(MSBEntry): #inherit MSB methods related to data encoding
    type : str = "static"

    def __init__(self, f : EndianBinaryFileReader, settings : dict, font : str, op_codes : dict, buttons : dict):
        self.settings, self.font, self.op_codes, self.buttons = settings, font, op_codes, buttons
        self.data_offset = f.read_UInt32()
        self.is_invalid = False
        self.string = ""
        self.speaker = ""
        self.static_code = ""

        if self.data_offset == 0xFF_FF_FF_FF:
            self.is_invalid = True

        else:
            f.set_endianness('big')
            pos = f.tell()
            f.seek(self.data_offset)
            self.read_data(f)
            f.seek(pos)
            f.set_endianness('little')

def batch_export(game_code : str, input_dir : str, extraction_dir : str):
    speakers = set()
    os.makedirs(extraction_dir, exist_ok=True)

    for file in os.listdir(input_dir):
        if file.lower().endswith('.scx'):
            print(f"Exporting {Path(input_dir) / file}...")
            scx = SCX(Path(input_dir) / file, game_code)
            speakers |= scx.get_speakers()           
            scx.write_excel(extraction_dir)

    print("Writing speakers file...")
    write_speakers(Path(extraction_dir) / "speakers.xlsx", list(speakers))
    print("Done!")

def batch_import(game_code : str, input_dir : str, extraction_dir : str):
    for file in os.listdir(input_dir):
        if file.lower().endswith('.scx'):
            scx = SCX(Path(input_dir) / file, game_code)
            print(f"Importing text to {Path(input_dir) / file}...")
            scx.load_excel(Path(extraction_dir) / (file + '.xlsx'))
            scx.save(Path(input_dir) / file)
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