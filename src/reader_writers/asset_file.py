"""Reader/writers for the entire asset file, and it's header."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .asset_object import AssetObject
from .metadata import AssetType, ExternalMeta, ScriptMeta
from .primitives import Boolean, SInt32, String, UInt32
from ..streams import Reader, Writer


@dataclass
class Header:
    """An asset file header."""

    metadata_size: UInt32
    file_size: UInt32
    format_version: UInt32
    data_offset: UInt32
    big_endian: Boolean
    unity_version: String
    target_platform_id: SInt32
    enable_type_tree: Boolean

    @classmethod
    def read(cls, reader: Reader) -> Header:
        """Read an asset file header from a stream."""
        reader.endian = 'big'
        metadata_size = reader.read(UInt32)
        file_size = reader.read(UInt32)
        format_version = reader.read(UInt32)
        if format_version.value != 21:
            print(
                f'Warning: unsupported version (got {format_version}, '
                'expected 21)'
            )
        data_offset = reader.read(UInt32)
        reader.data_offset = data_offset.value
        big_endian = reader.read(Boolean)
        reader.read_bytes(3)
        reader.endian = 'big' if big_endian.value else 'little'
        unity_version = reader.read(String)
        target_platform_id = reader.read(SInt32)
        enable_type_tree = reader.read(Boolean)
        if enable_type_tree.value:
            print('Warning: type trees used but unsuported.')
        return cls(
            metadata_size, file_size, format_version, data_offset, big_endian,
            unity_version, target_platform_id, enable_type_tree
        )

    def __len__(self) -> int:
        """Get the number of bytes this header will take up."""
        return sum(map(len, (
            self.metadata_size, self.file_size, self.format_version,
            self.data_offset, self.big_endian, self.unity_version,
            self.target_platform_id, self.enable_type_tree
        ))) + 3

    def write(self, writer: Writer):
        """Write the header to a stream."""
        writer.endian = 'big'
        for val in (
                self.metadata_size, self.file_size, self.format_version,
                self.data_offset, self.big_endian):
            writer.write(val)
        writer.write_bytes(b'\x00' * 3)
        writer.endian = 'big' if self.big_endian.value else 'little'
        writer.write(self.unity_version)
        writer.write(self.target_platform_id)
        writer.write(self.enable_type_tree)


@dataclass
class AssetFile:
    """Reader/writer for an entire Unity asset file."""

    header: Header
    types: list[AssetType]
    objects: list[AssetObject]
    scripts: list[ScriptMeta]
    externals: list[ExternalMeta]
    ref_types: list[AssetType]
    user_information: String

    @classmethod
    def read(cls, reader: Reader) -> AssetFile:
        """Read file metadata from a stream."""
        header = reader.read(Header)
        types = reader.read_array(AssetType)
        objects = reader.read_array(AssetObject)
        scripts = reader.read_array(ScriptMeta)
        externals = reader.read_array(ExternalMeta)
        ref_types = reader.read_array(AssetType)
        user_information = reader.read(String)
        return cls(
            header, types, objects, scripts, externals, ref_types,
            user_information
        )

    def array_length(self, array: list[Any]) -> int:
        """Calculate the number of bytes an array will take up."""
        # For some reason, it only works if we don't include the
        # number indicating the length of the array.
        return sum(map(len, array))

    def __len__(self) -> int:
        """Calculate the number of bytes the metadata will take up."""
        return (
            len(self.header)
            + self.array_length(self.types)
            + self.array_length(self.objects)
            + self.array_length(self.scripts)
            + self.array_length(self.externals)
            + self.array_length(self.ref_types)
            + len(self.user_information)
        )

    def write(self, writer: Writer):
        """Write the asset file to a stream."""
        metadata_size = len(self)
        data_offset = metadata_size + 32 - (metadata_size % 32)
        body_size = self.allocate_object_offsets()
        self.header.file_size = UInt32(data_offset + body_size - 4)
        self.header.metadata_size = UInt32(metadata_size)
        self.header.data_offset = UInt32(data_offset)
        writer.write(self.header)
        for array in (
                self.types, self.objects, self.scripts, self.externals):
            writer.write_array(array)
        writer.write_bytes(b'\x00' * 4)    # We need to do this, why?
        writer.write_array(self.ref_types)
        writer.write(self.user_information)
        for asset_obj in self.objects:
            asset_obj.write_asset(writer)

    def allocate_object_offsets(self) -> int:
        """Allocate starting bytes to each object.

        Returns the total length of all objects.
        """
        offset = 0
        for asset_obj in self.objects:
            asset_obj.start_byte = UInt32(offset)
            offset += asset_obj.asset_length
            alignment = (8 - (offset % 8)) % 8
            asset_obj.alignment = alignment
            offset += alignment
        return offset
