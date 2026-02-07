from utils import (
    EndianBinaryFileUpdater,
    EndianBinaryFileReader,
    load_font_txt,
    write_font_txt,
)
import json
import sys


def get_preset(game_code: str) -> tuple[int, int]:
    if game_code == "FDC3":
        raise Exception("FDC3 isn't supported.")
    if game_code not in ["FDC1", "FDC2"]:
        raise Exception("This game code doesn't belong to a Famicom Detective game.")
    if game_code == "FDC1":
        return 0x1B0E8D, 0x400
    if game_code == "FDC2":
        return 0x1AD53D, 0x400


def export_font_metrics(game_code: str, main_path: str, json_path: str):
    font = load_font_txt(game_code)
    fontDataOffset, glyphCount = get_preset(game_code)

    with EndianBinaryFileReader(main_path) as f:
        f.seek(fontDataOffset)
        width = [f.read_Int8() for _ in range(glyphCount)]
        height = [f.read_Int8() for _ in range(glyphCount)]
        unk2 = [f.read_Int8() for _ in range(glyphCount)]
        x_off = [f.read_Int8() for _ in range(glyphCount)]
        y_off = [f.read_Int8() for _ in range(glyphCount)]

    chars = [font[i] for i in range(glyphCount)]

    json_data = [
        {
            "char": chars[i],
            "width": width[i],
            "height": height[i],
            "unk2": unk2[i],
            "x_off": x_off[i],
            "y_off": y_off[i],
        }
        for i in range(glyphCount)
    ]

    json.dump(
        json_data,
        open(json_path, mode="x", encoding="utf-8"),
        ensure_ascii=False,
        indent=5,
    )


def import_font_metrics(game_code: str, json_path: str, main_path: str):
    json_data = json.load(open(json_path, mode="r", encoding="utf-8"))
    fontDataOffset, glyphCount = get_preset(game_code)
    if len(json_data) != glyphCount:
        raise Exception("Adding/removing glyphs isn't supported.")
    with EndianBinaryFileUpdater(main_path) as f:
        f.seek(fontDataOffset)
        for glyph in json_data:
            f.write_Int8(glyph["width"])
        for glyph in json_data:
            f.write_Int8(glyph["height"])
        for glyph in json_data:
            f.write_Int8(glyph["unk2"])
        for glyph in json_data:
            f.write_Int8(glyph["x_off"])
        for glyph in json_data:
            f.write_Int8(glyph["y_off"])
    chars = ""
    for glyph in json_data:
        chars += glyph["char"]
    write_font_txt(game_code, chars)


def main():
    args = sys.argv
    if args[1] == "-e":
        export_font_metrics(args[2], args[3], args[4])
        print(f"Successfully exported font to {args[4]}!")

    elif args[1] == "-i":
        import_font_metrics(args[2], args[3], args[4])
        print(
            f"Successfully imported new font to {args[4]} and imported new characters to font.txt!"
        )
    else:
        print("Error: expected either -e or -i argument")


if __name__ == "__main__":
    main()
