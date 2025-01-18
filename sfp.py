from utils import EndianBinaryFileReader, EndianBinaryFileWriter
import os
from pathlib import Path
import sys

extensions = {
    "info" : ".inf",
    "skeleton" : ".skel",
    "atlas" : ".atlas",
    "image" : ".png",
    "audio" : ".opus"
}

class SFP:
    def __init__(self, filepath : str):
        self.filename = os.path.basename(filepath).split('.')[0]
        self.filepath = filepath
        with EndianBinaryFileReader(filepath) as f:
            self.magic1 = f.check_magic(b'MGBD')
            self.magic2 = f.check_magic(b'SPFT')
            self.unk = f.read_UInt32()
            self.entry_count = f.read_UInt32()
            self.entries = [SFPEntry(f) for _ in range(self.entry_count)]

    def unpack(self, out_dir : str): #it doesn't extract the "real" filenames, but I am not really sure how that whole thing work rn
        print(f"Extracting files from {self.filepath}...")
        os.makedirs(out_dir, exist_ok=True)
        types = {}
        for entry in self.entries:
            if entry.file_type not in types:
                entry.write_file(Path(out_dir) / (self.filename + extensions[entry.file_type]))
                types[entry.file_type] = 1
            else:
                entry.write_file(Path(out_dir) / (self.filename + f"{types[entry.file_type]}" + extensions[entry.file_type]))
                types[entry.file_type] += 1

    def import_files(self, in_dir : str):
        types = {}
        for entry in self.entries:
            if entry.file_type not in types:
                lookup_path = Path(in_dir) / (self.filename + extensions[entry.file_type])
                types[entry.file_type] = 1
            else:
                lookup_path = Path(in_dir) / (self.filename + f"{types[entry.file_type]}" + extensions[entry.file_type])
                types[entry.file_type] += 1

            if lookup_path.exists():
                print(f"Importing {lookup_path} to {self.filepath}...")
                newdata = open(lookup_path, 'rb').read()
                entry.import_data(newdata)

    def save(self, filepath : str):
        with EndianBinaryFileWriter(filepath) as f:
            f.write(self.magic1)
            f.write(self.magic2)
            f.write_UInt32(self.unk)
            f.write_UInt32(self.entry_count)
            for entry in self.entries:
                entry.write_info(f)
            for idx, entry in enumerate(self.entries):
                offset = f.tell()
                f.write(entry.data)
                f.pad(0x10)
                f.seek(0x10 + 0x10 * idx)
                f.write_UInt32(offset)
                f.seek(0, 2)

class SFPEntry:
    def __init__(self, f : EndianBinaryFileReader):
        self.data_offset = f.read_UInt32()
        self.data_size = f.read_UInt32()
        self.file_type = f.read(8).decode().strip('\x00')
        pos = f.tell()
        f.seek(self.data_offset)
        self.data = f.read(self.data_size)
        f.seek(pos)

    def import_data(self, newdata : bytes):
        self.data = newdata
        self.data_size = len(self.data)

    def write_file(self, out_filepath : str):
        open(out_filepath, 'wb').write(self.data)

    def write_info(self, f : EndianBinaryFileWriter):
        f.write_UInt32(0)
        f.write_UInt32(self.data_size)
        f.write(self.file_type.encode())
        f.pad(8)

def batch_export_sfp(input_dir : str, extracted_dir : str):
    for path, _, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith(".sfp"):
                abs_path = Path(path) / file
                sfp = SFP(abs_path)
                out_dir = Path(extracted_dir) / abs_path.relative_to(input_dir)
                sfp.unpack(out_dir)

def batch_import_sfp(input_dir : str, extracted_dir : str):
    for file in os.listdir(input_dir):
        if file.lower().endswith(".sfp"):
            abs_path = Path(input_dir) / file
            sfp = SFP(abs_path)
            sfp.import_files(Path(extracted_dir) / file)
            sfp.save(abs_path)

def main():
    args = sys.argv
    if args[1] == '-e':
        batch_export_sfp(args[2], args[3])
    elif args[1] == '-i':
        batch_import_sfp(args[2], args[3])

if __name__ == '__main__':
    main()