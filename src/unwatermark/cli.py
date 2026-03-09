"""CLI entry point for unwatermark."""

from __future__ import annotations

from pathlib import Path

import click

from unwatermark.config import load_config


@click.command()
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.option("-o", "--output", type=click.Path(path_type=Path), default=None, help="Output path.")
@click.option(
    "--annotate",
    type=str,
    default=None,
    help="Text description of the watermark to help AI detection.",
)
@click.option(
    "--strategy",
    type=click.Choice(["solid_fill", "gradient_fill", "clone_stamp", "inpaint"]),
    default=None,
    help="Force a specific removal strategy (skip AI recommendation).",
)
@click.option("--no-ai", is_flag=True, help="Disable AI analysis, use position-based heuristic.")
@click.option(
    "--model",
    type=click.Choice(["claude", "openai"]),
    default=None,
    help="Which vision model to use for analysis.",
)
def main(
    input_file: Path,
    output: Path | None,
    annotate: str | None,
    strategy: str | None,
    no_ai: bool,
    model: str | None,
) -> None:
    """Remove watermarks from images, PDFs, and PPTX files.

    Drop a file in, get a clean version out. Uses AI vision to detect
    watermarks and choose the best removal technique automatically.
    """
    overrides = {}
    if no_ai:
        overrides["use_ai"] = False
    if model:
        from unwatermark.config import AnalysisProvider
        overrides["analysis_provider"] = AnalysisProvider(model)

    config = load_config(**overrides)

    suffix = input_file.suffix.lower()
    if output is None:
        output = input_file.with_stem(input_file.stem + "_clean")

    handler = _get_handler(suffix)
    if handler is None:
        raise click.ClickException(
            f"Unsupported file type: {suffix}. Supported: .png, .jpg, .jpeg, .bmp, .tiff, .pdf, .pptx"
        )

    annotation = None
    if annotate:
        from unwatermark.models.annotation import UserAnnotation
        annotation = UserAnnotation(description=annotate)

    if config.can_use_ai:
        click.echo(f"Analyzing {input_file.name} with {config.analysis_provider.value}...")
    else:
        click.echo(f"Processing {input_file.name} (heuristic mode)...")

    result = handler(input_file, output, config, annotation, strategy)
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
