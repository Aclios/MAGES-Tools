from utils import EndianBinaryFileReader, EndianBinaryFileWriter
import os
from pathlib import Path
import zlib
import sys

class MPK:
    def __init__(self, filepath : str):
        with EndianBinaryFileReader(filepath) as f:
            self.filepath = filepath
            self.magic = f.check_magic(b'MPK\x00')
            self.unk1 = f.read_UInt16()
            self.unk2 = f.read_UInt16()
            self.entry_count = f.read_UInt64()
            self.padding = f.read(0x30)
            self.entries = [MPKEntry(f) for _ in range(self.entry_count)]

    def unpack(self, extract_dir : str):
        os.makedirs(extract_dir, exist_ok = True)
        for entry in self.entries:
            if entry.filepath != '':
                print(f"Extracting {entry.filepath} from {self.filepath}...")
                extract_path = Path(extract_dir) / entry.filepath
                os.makedirs(extract_path.parent, exist_ok=True)
                entry.write_file(extract_path)

    def import_files(self, dir : str):
        for entry in self.entries:
            lookup_path = Path(dir) / entry.filepath
            if lookup_path.exists():
                print(f"Importing {lookup_path} to {self.filepath}...")
                newdata = open(lookup_path, 'rb').read()
                entry.import_data(newdata)

    def save(self, filepath : str):
        with EndianBinaryFileWriter(filepath) as f:
            f.write(self.magic)
            f.write_UInt16(self.unk1)
            f.write_UInt16(self.unk2)
            f.write_UInt64(self.entry_count)
            f.write(self.padding)
            for entry in self.entries:
                entry.write_info(f)
            for idx, entry in enumerate(self.entries):
                f.pad(0x800)
                offset = f.tell()
                f.write(entry.data)
                f.seek(0x48 + 0x100 * idx)
                f.write_UInt64(offset)
                f.seek(0, 2)

class MPKEntry:
    def __init__(self, f : EndianBinaryFileReader):
        self.compress_flag = f.read_UInt32()
        self.idx = f.read_UInt32()
        self.data_offset = f.read_UInt64()
        self.compressed_data_size = f.read_UInt64()
        self.uncompressed_data_size = f.read_UInt64()
        self.filepath = f.read(0xE0).decode().strip('\x00')
        self.read_data(f)

    def read_data(self, f : EndianBinaryFileReader):
        pos = f.tell()
        f.seek(self.data_offset)
        self.data = f.read(self.compressed_data_size)
        f.seek(pos)

    def import_data(self, newdata : bytes):
        self.uncompressed_data_size = len(newdata)
        match self.compress_flag:
            case 0:
                self.data = newdata
            case 1:
                self.data = zlib.compress(newdata)
            case _:
                raise Exception(f"Unsupported compression with id {self.compress_flag}") 
        self.compressed_data_size = len(self.data)

    def write_file(self, extract_path : str):
        match self.compress_flag:
            case 0:
                out_data = self.data
            case 1:
                out_data = zlib.decompress(self.data)
            case _:
                raise Exception(f"Unsupported compression with id {self.compress_flag}")         
        assert len(out_data) == self.uncompressed_data_size, "Error: the actual length of the data don't match the expected size"
        open(extract_path, 'wb').write(out_data)

    def write_info(self, f : EndianBinaryFileWriter):
        f.write_UInt32(self.compress_flag)
        f.write_UInt32(self.idx)
        f.write_UInt64(0)
        f.write_UInt64(self.compressed_data_size)
        f.write_UInt64(self.uncompressed_data_size)
        f.write(self.filepath.encode('utf-8'))
        f.write((0xE0 - len(self.filepath)) * b"\x00")

def batch_export_mpk(input_dir : str, extracted_dir : str):
    for file in os.listdir(input_dir):
        if file.lower().endswith(".mpk"):
            abs_path = Path(input_dir) / file
            mpk = MPK(abs_path)
            mpk.unpack(Path(extracted_dir) / file)

def batch_import_mpk(input_dir : str, extracted_dir : str):
    for file in os.listdir(input_dir):
        if file.lower().endswith(".mpk"):
            abs_path = Path(input_dir) / file
            mpk = MPK(abs_path)
            mpk.import_files(Path(extracted_dir) / file)
            mpk.save(abs_path)

def main():
    args = sys.argv
    if args[1] == "-e":
        batch_export_mpk(args[2], args[3])
    elif args[1] == "-i":
        batch_import_mpk(args[2], args[3])

if __name__ == '__main__':
    main()