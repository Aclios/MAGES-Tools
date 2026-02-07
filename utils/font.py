from pathlib import Path


def load_font_txt(game_code: str):
    return (
        open(Path("profiles", game_code, "font.txt"), mode="r", encoding="utf-8-sig")
        .read()
        .replace("\n", "")
        .replace("\r", "")
    )


def write_font_txt(game_code: str, chars: str):
    with open(
        Path("profiles", game_code, "font.txt"), mode="w", encoding="utf-8-sig"
    ) as f:
        for i in range(len(chars) // 64):
            f.write(chars[i * 64 : (i + 1) * 64] + "\n")
        if len(chars) % 64 != 0:
            f.write(chars[(i + 1) * 64 :])
