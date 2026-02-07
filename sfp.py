from utils import EndianBinaryFileReader, EndianBinaryFileWriter, has_correct_suffix
from pathlib import Path
import sys

extensions = {
    "info": ".inf",
    "skeleton": ".skel",
    "atlas": ".atlas",
    "image": ".png",
    "audio": ".opus",
}

MAGIC = b"MGBDSPFT"


class SFP:
    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        self.filename = self.filepath.name
        with EndianBinaryFileReader(filepath) as f:
            f.check_magic(MAGIC)
            self.unk = f.read_UInt32()
            self.entry_count = f.read_UInt32()
            self.entries = [SFPEntry(f) for _ in range(self.entry_count)]

    def unpack(
        self, out_dir: str
    ):  # it doesn't extract the "real" filenames, but I am not really sure how that whole thing work rn
        print(f"Extracting files from {self.filepath}...")
        Path(out_dir).mkdir(parents=True, exist_ok=True)
        types = {}
        for entry in self.entries:
            if entry.file_type not in types:
                Path(out_dir, self.filename + extensions[entry.file_type]).write_bytes(
                    entry.data
                )
                types[entry.file_type] = 1
            else:
                Path(
                    out_dir,
                    self.filename
                    + f"{types[entry.file_type]}"
                    + extensions[entry.file_type],
                ).write_bytes(entry.data)
                types[entry.file_type] += 1

    def import_files(self, in_dir: str):
        types = {}
        for entry in self.entries:
            if entry.file_type not in types:
                lookup_path = Path(in_dir) / (
                    self.filename + extensions[entry.file_type]
                )
                types[entry.file_type] = 1
            else:
                lookup_path = Path(in_dir) / (
                    self.filename
                    + f"{types[entry.file_type]}"
                    + extensions[entry.file_type]
                )
                types[entry.file_type] += 1

            if lookup_path.exists():
                print(f"Importing {lookup_path} to {self.filepath}...")
                newdata = open(lookup_path, "rb").read()
                entry.import_data(newdata)

    def save(self, filepath: str):
        with EndianBinaryFileWriter(filepath) as f:
            f.write(MAGIC)
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
    def __init__(self, f: EndianBinaryFileReader):
        self.data_offset = f.read_UInt32()
        self.data_size = f.read_UInt32()
        self.file_type = f.read(8).decode().strip("\x00")
        pos = f.tell()
        f.seek(self.data_offset)
        self.data = f.read(self.data_size)
        f.seek(pos)

    def import_data(self, newdata: bytes):
        self.data = newdata
        self.data_size = len(self.data)

    def write_info(self, f: EndianBinaryFileWriter):
        f.write_UInt32(0)
        f.write_UInt32(self.data_size)
        f.write(self.file_type.encode())
        f.pad(8)


def batch_export_sfp(input_dir: str, extracted_dir: str):
    for path in Path(input_dir).rglob("*"):
        if has_correct_suffix(path, ".sfp"):
            sfp = SFP(path)
            out_dir = Path(extracted_dir, path.relative_to(input_dir))
            sfp.unpack(out_dir)


def batch_import_sfp(input_dir: str, extracted_dir: str):
    for path in Path(input_dir).iterdir():
        if has_correct_suffix(path, ".sfp"):
            sfp = SFP(path)
            sfp.import_files(Path(extracted_dir, path.name))
            sfp.save(path)


def main():
    args = sys.argv
    if args[1] == "-e":
        batch_export_sfp(args[2], args[3])
    elif args[1] == "-i":
        batch_import_sfp(args[2], args[3])


if __name__ == "__main__":
    main()
