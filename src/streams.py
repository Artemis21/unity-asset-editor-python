"""Tools for interacting with binary IO streams."""
from __future__ import annotations

import io
from typing import Any

from . import reader_writers


class Reader:
    """Tool for reading basic types from a byte stream."""

    def __init__(self, stream: io.BufferedIOBase):
        """Store the stream for reading."""
        self.read_bytes = stream.read
        self.seek = stream.seek
        self.tell = stream.tell
        self.endian = 'big'

    def read(self, reader: Any) -> Any:
        """Read a value of the specified type."""
        return reader.read(self)

    def read_array(self, reader: Any) -> list[Any]:
        """Read an array of a specified type."""
        length = self.read(reader_writers.UInt32).value
        return [reader.read(self) for _ in range(length)]

    def align(self, to: int = 4):
        """Move the pointer to the next multiple of `to`."""
        position = self.tell()
        offset = position % to
        if offset != 0:
            self.seek(position + offset)

    def slice(self, start: int, length: int) -> Reader:
        """Return a reader containing a slice of the data from this reader."""
        old_position = self.tell()
        self.seek(start)
        reader = Reader(io.BytesIO(self.read_bytes(length)))
        reader.endian = self.endian
        self.seek(old_position)
        return reader


class Writer:
    """Tool for writing basic types to a byte stream."""

    def __init__(self, stream: io.BufferedIOBase):
        """Store the stream for writing."""
        self.write_bytes = stream.write
        self.seek = stream.seek
        self.tell = stream.tell
        self.endian = 'big'

    def write(self, value: Any):
        """Write a value that supports the write method."""
        value.write(self)

    def write_array(self, values: list[Any]):
        """Write an array, and it's length."""
        self.write(reader_writers.UInt32(len(values)))
        for value in values:
            value.write(self)

    def align(self, to: int = 4, fill: bytes = b'\x00'):
        """Move the pointer to the next multiple of `to`."""
        position = self.tell()
        offset = position % to
        if offset != 0:
            self.write_bytes(fill * offset)
