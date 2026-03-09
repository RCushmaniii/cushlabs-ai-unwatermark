"""CLI entry point for unwatermark."""

from pathlib import Path

import click


@click.command()
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.option("-o", "--output", type=click.Path(path_type=Path), default=None, help="Output path.")
@click.option(
    "--position",
    type=click.Choice(
        ["bottom-right", "bottom-left", "bottom-center", "top-right", "top-left", "top-center"]
    ),
    default="bottom-right",
    help="Watermark position hint.",
)
@click.option("--width-ratio", type=float, default=0.25, help="Watermark width as fraction of image.")
@click.option("--height-ratio", type=float, default=0.06, help="Watermark height as fraction of image.")
def main(
    input_file: Path,
    output: Path | None,
    position: str,
    width_ratio: float,
    height_ratio: float,
) -> None:
    """Remove watermarks from images, PDFs, and PPTX files.

    Drop a file in, get a clean version out.
    """
    suffix = input_file.suffix.lower()

    if output is None:
        output = input_file.with_stem(input_file.stem + "_clean")

    handler = _get_handler(suffix)
    if handler is None:
        raise click.ClickException(
            f"Unsupported file type: {suffix}. Supported: .png, .jpg, .jpeg, .bmp, .tiff, .pdf, .pptx"
        )

    click.echo(f"Processing {input_file.name}...")
    result = handler(input_file, output, position, width_ratio, height_ratio)
    click.echo(f"Done! Saved to {result}")


def _get_handler(suffix: str):
    """Return the appropriate handler function for a file extension."""
    if suffix in (".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"):
        from unwatermark.handlers.image import process_image
        return process_image
    elif suffix == ".pdf":
        from unwatermark.handlers.pdf import process_pdf
        return process_pdf
    elif suffix == ".pptx":
        from unwatermark.handlers.pptx import process_pptx
        return process_pptx
    return None


if __name__ == "__main__":
    main()
