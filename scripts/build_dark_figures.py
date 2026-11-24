"""Build dark SVG displays from the exact raster figures embedded in the report.

The SVG filter changes colors only. It does not redraw scientific content.
Run from the repository root with: python3 scripts/build_dark_figures.py
"""

from base64 import b64encode
from pathlib import Path
from struct import unpack


ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = ROOT / "figures" / "original"
DARK = ROOT / "figures" / "dark"


def png_size(data: bytes) -> tuple[int, int]:
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("Expected a PNG file")
    return unpack(">II", data[16:24])


def main() -> None:
    DARK.mkdir(parents=True, exist_ok=True)
    for source in sorted(ORIGINAL.glob("*.png")):
        data = source.read_bytes()
        width, height = png_size(data)
        encoded = b64encode(data).decode("ascii")
        # This maps white paper to navy and black ink to off-white. Intermediate
        # RGB values remain distinct, so plotted lines and heatmap marks survive.
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Dark rendering of {source.stem}">
  <defs>
    <filter id="dark" color-interpolation-filters="sRGB">
      <feComponentTransfer>
        <feFuncR type="table" tableValues="0.906 0.043"/>
        <feFuncG type="table" tableValues="0.925 0.063"/>
        <feFuncB type="table" tableValues="0.961 0.125"/>
      </feComponentTransfer>
    </filter>
  </defs>
  <rect width="100%" height="100%" fill="#0B1020"/>
  <image width="{width}" height="{height}" xlink:href="data:image/png;base64,{encoded}" filter="url(#dark)"/>
</svg>
'''
        (DARK / f"{source.stem}.svg").write_text(svg)
        print(f"{source.name} -> {source.stem}.svg ({width}x{height})")


if __name__ == "__main__":
    main()
