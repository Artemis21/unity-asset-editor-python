"""Reader/writers for various pieces of metadata."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .primitives import Boolean, SInt16, SInt32, SInt64, String
from ..streams import Reader, Writer


@dataclass
class ExternalMeta:
    """Metadata describing an asset in another file."""

    unknown_value: bytes
    path_name: String

    @classmethod
    def read(cls, reader: Reader) -> ExternalMeta:
        """Read external file metadata from a stream."""
        # 21 bytes, most of which null, 9th of which sometimes not.
        # More investigation needed.
        unknown_value = reader.read_bytes(21)
        path_name = reader.read(String)
        return cls(unknown_value, path_name)

    def __len__(self) -> int:
        """Get the number of bytes the object takes up."""
        return sum(map(len, (self.unknown_value, self.path_name)))

    def write(self, writer: Writer):
        """Write the external file metadata to a stream."""
        writer.write_bytes(self.unknown_value)
        writer.write(self.path_name)


@dataclass
class ScriptMeta:
    """Metadata describing the location of a script in a file."""

    file_index: SInt32
    id_in_file: SInt64

    @classmethod
    def read(cls, reader: Reader) -> ScriptMeta:
        """Read script metadata from a stream."""
        file_index = reader.read(SInt32)
        reader.align()
        id_in_file = reader.read(SInt64)
        return cls(file_index, id_in_file)

    def __len__(self) -> int:
        """Get the number of bytes the metadata takes up."""
        # +4 is to account for alignment.
        return sum(map(len, (self.file_index, self.id_in_file)))

    def write(self, writer: Writer):
        """Write the script metadata to a stream."""
        writer.write(self.file_index)
        writer.align()
        writer.write(self.id_in_file)


@dataclass
class AssetType:
    """A Unity asset type."""

    class_id: SInt32
    is_stripped: Boolean
    script_type_index: SInt16
    script_id: Optional[bytes]
    old_type_hash: bytes

    @classmethod
    def read(cls, reader: Reader) -> AssetType:
        """Read an asset type from a stream."""
        class_id = reader.read(SInt32)
        is_stripped = reader.read(Boolean)
        script_type_index = reader.read(SInt16)
        if class_id.value == 114:
            script_id = reader.read_bytes(16)
        else:
            script_id = None
        old_type_hash = reader.read_bytes(16)
        return cls(
            class_id, is_stripped, script_type_index, script_id,
            old_type_hash
        )

    def __len__(self) -> int:
        """Get the number of bytes the type definition takes up."""
        length = sum(map(len, (
            self.class_id, self.is_stripped, self.script_type_index,
            self.old_type_hash
        )))
        if self.script_id:
            length += len(self.script_id)
        return length

    def write(self, writer: Writer):
        """Write the asset type to a stream."""
        writer.write(self.class_id)
        writer.write(self.is_stripped)
        writer.write(self.script_type_index)
        if self.class_id.value == 114:
            writer.write_bytes(self.script_id)
        writer.write_bytes(self.old_type_hash)
