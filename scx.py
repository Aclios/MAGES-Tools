from utils import EndianBinaryFileReader, EndianBinaryFileWriter, has_correct_suffix
import sys
from pathlib import Path
from msb import MSB, MSBEntry, write_speakers, convert_speakers

MAGIC = b"SC3\x00"


class SCX(MSB):  # inherit MSB methods
    def __init__(self, filepath: str, game_code: str):
        self.load_profile(game_code)
        with EndianBinaryFileReader(filepath) as f:
            self.filename = Path(filepath).name
            f.check_magic(MAGIC)
            self.text_table_offset = f.read_UInt32()
            self.unk_table_offset = f.read_UInt32()
            self.text_entry_count = (
                self.unk_table_offset - self.text_table_offset
            ) // 4
            self.script_data = f.read(self.text_table_offset - 12)
            self.entries = [
                SCXTextEntry(f, self.settings, self.font, self.op_codes, self.buttons)
                for _ in range(self.text_entry_count)
            ]
            f.seek(self.unk_table_offset)
            if len(self.entries) > 0:
                self.unk_table_data = f.read(
                    self.entries[0].data_offset - self.unk_table_offset
                )
            else:
                f.seek(self.unk_table_offset)
                self.unk_table_data = f.read()

    def save(self, out_filepath: str):
        with EndianBinaryFileWriter(out_filepath) as f:
            f.write(MAGIC)
            f.write_UInt32(self.text_table_offset)
            f.write_UInt32(self.unk_table_offset)
            f.write(self.script_data)
            entries_data = bytearray()
            for entry in self.entries:
                entry_offset = (
                    self.text_table_offset
                    + 4 * self.text_entry_count
                    + len(self.unk_table_data)
                    + len(entries_data)
                )
                if entry.is_invalid:
                    f.write_UInt32(0xFF_FF_FF_FF)
                else:
                    f.write_UInt32(entry_offset)
                entries_data += entry.to_bytes()
            f.write(self.unk_table_data)
            f.write(entries_data)


class SCXTextEntry(MSBEntry):  # inherit MSB methods related to data encoding
    type: str = "static"

    def __init__(
        self,
        f: EndianBinaryFileReader,
        settings: dict,
        font: str,
        op_codes: dict,
        buttons: dict,
    ):
        self.settings, self.font, self.op_codes, self.buttons = (
            settings,
            font,
            op_codes,
            buttons,
        )
        self.data_offset = f.read_UInt32()
        self.is_invalid = False
        self.string = ""
        self.speaker = ""
        self.static_code = ""

        if self.data_offset == 0xFF_FF_FF_FF:
            self.is_invalid = True

        else:
            f.set_endianness("big")
            pos = f.tell()
            f.seek(self.data_offset)
            self.read_data(f)
            f.seek(pos)
            f.set_endianness("little")


def batch_export(game_code: str, input_dir: str, extraction_dir: str):
    speakers = set()
    Path(extraction_dir).mkdir(exist_ok=True, parents=True)
    for path in Path(input_dir).iterdir():
        if has_correct_suffix(path, ".scx"):
            print(f"Exporting {path}...")
            scx = SCX(path, game_code)
            speakers |= scx.get_speakers()
            scx.write_excel(extraction_dir)

    print("Writing speakers file...")
    write_speakers(Path(extraction_dir) / "speakers.xlsx", list(speakers))
    print("Done!")


def batch_import(game_code: str, input_dir: str, extraction_dir: str):
    for path in Path(input_dir).iterdir():
        if has_correct_suffix(path, ".scx"):
            scx = SCX(path, game_code)
            print(f"Importing text to {path}...")
            scx.load_excel(Path(extraction_dir, path.name + ".xlsx"))
            scx.save(path)
    print("Done!")


def main():
    args = sys.argv
    if args[1] == "-e":
        batch_export(args[2], args[3], args[4])
    elif args[1] == "-i":
        batch_import(args[2], args[3], args[4])
    elif args[1] == "-s":
        convert_speakers(args[2], args[3])
    else:
        return


if __name__ == "__main__":
    main()
