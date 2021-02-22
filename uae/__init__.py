"""Tool for editing Unity assets."""
import io

from .reader_writers import AssetFile
from .streams import Reader, Writer


def load(file: io.BufferedIOBase) -> AssetFile:
    """Load a file for editing."""
    reader = Reader(file)
    return reader.read(AssetFile)


def dump(assets: AssetFile, file: io.BufferedIOBase):
    """Save an edited file."""
    writer = Writer(file)
    writer.write(assets)
