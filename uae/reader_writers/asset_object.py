"""Reader/writer for a Unity asset object."""
from __future__ import annotations

from dataclasses import dataclass

from .primitives import CharArray, SInt32, SInt64, UInt32
from ..streams import Reader, Writer


@dataclass
class AssetObject:
    """An asset in the file."""

    path_id: SInt64
    raw_file_data: Reader
    start_byte: UInt32
    _unmodified_length: UInt32
    _file_name: CharArray
    _file_content: bytes
    alignment: int
    _file_modified: bool
    type_id: SInt64

    @classmethod
    def read(cls, reader: Reader) -> AssetObject:
        """Read object metadata from a stream."""
        reader.align()
        path_id = reader.read(SInt64)
        start_byte = reader.read(UInt32)
        byte_length = reader.read(UInt32)
        raw_file_data = reader.slice((
            reader.data_offset + start_byte.value
        ), byte_length.value)
        file_name = raw_file_data.read(CharArray)
        raw_file_data.read(UInt32)    # File length, not needed.
        file_content = raw_file_data.read_bytes().rstrip(b'\x00')
        file_modified = False
        type_id = reader.read(SInt32)
        return cls(
            path_id, raw_file_data, start_byte, byte_length, file_name,
            file_content, 0, file_modified, type_id
        )

    def __len__(self) -> int:
        """Get the number of bytes the object takes up."""
        return sum(map(len, (
            self.path_id, self.start_byte, self._unmodified_length,
            self.type_id
        )))

    @property
    def file_name(self) -> CharArray:
        """Get the file name."""
        return self._file_name

    @file_name.setter
    def file_name(self, new: CharArray):
        """Change the file name."""
        self._file_modified = True
        self._file_name = new

    @property
    def file_content(self) -> bytes:
        """Get the file content."""
        return self._file_content

    @file_content.setter
    def file_content(self, new: bytes):
        """Change the file content."""
        self._file_modified = True
        self._file_content = new

    @property
    def asset_length(self) -> int:
        """Get the length of the raw file data."""
        if self._file_modified:
            char_array_size = 4 + len(self._file_name.value)
            return len(self._file_content) + char_array_size
        return self._unmodified_length.value

    def write(self, writer: Writer):
        """Write the object metadata to a stream."""
        writer.align()
        for val in (
                self.path_id, self.start_byte, UInt32(self.asset_length),
                self.type_id):
            writer.write(val)

    def write_asset(self, writer: Writer):
        """Write the object itself to a stream."""
        if self.alignment:
            writer.write_bytes(b'\x00' * self.alignment)
        if self._file_modified:
            writer.write(self._file_name)
            writer.write(UInt32(len(self._file_content)))
            writer.write_bytes(self._file_content)
        else:
            self.raw_file_data.seek(0)
            writer.write_bytes(self.raw_file_data.read_bytes())
