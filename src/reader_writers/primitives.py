"""Reader/writers for primitive types."""
from __future__ import annotations

from .. import streams


class Integer:
    """Generic class for reading/writing integers to/from a stream."""

    length = NotImplemented
    signed = NotImplemented

    @classmethod
    def read(cls, reader: streams.Reader) -> Integer:
        """Read an integer from a stream."""
        return cls(int.from_bytes(
            reader.read_bytes(cls.length),
            reader.endian,
            signed=cls.signed
        ))

    def __init__(self, value: int):
        """Store the int's value."""
        self.value = value

    def __len__(self) -> int:
        """Get the length of the int."""
        return type(self).length

    def write(self, writer: streams.Writer):
        """Write the int to a stream."""
        writer.write_bytes(self.value.to_bytes(
            type(self).length,
            writer.endian,
            signed=type(self).signed
        ))

    def __str__(self) -> str:
        """Display the int as a string."""
        return str(self.value)

    def __repr__(self) -> str:
        """Display the Integer reader/writer representation."""
        return f'{type(self).__name__}({self.value})'


class Boolean(Integer):
    """Reader/writer for booleans."""

    length = 1
    signed = False

    def __init__(self, value: int):
        """Store the bool's value."""
        if value not in (0, 1):
            print('Warning: Boolean not 0 or 1.')
        self.value = value

    def __str__(self) -> str:
        """Display the bool as a string."""
        return str(bool(self.value))

    def __repr__(self) -> str:
        """Display the Boolean reader/writer representation."""
        return f'Boolean({bool(self.value)})'


class SInt16(Integer):
    """Reader/writer for signed 2 byte integers."""

    length = 2
    signed = True


class UInt32(Integer):
    """Reader/writer for unsigned 4 byte integers."""

    length = 4
    signed = False


class SInt32(Integer):
    """Reader/writer for signed 4 byte integers."""

    length = 4
    signed = True


class SInt64(Integer):
    """Reader/writer for signed 8 byte integers."""

    length = 8
    signed = True


class StringBase:
    """Base class for readers/writers of string types."""

    def __init__(self, value: str):
        """Store the string's value."""
        self.value = value

    def __str__(self) -> str:
        """Display the string."""
        return self.value

    def __repr__(self) -> str:
        """Display the String reader/writer representation."""
        return f'{type(self).__name__}({repr(self.value)})'


class String(StringBase):
    """Reader/writer for a null-terminated string."""

    max_length = 2 ** 15 - 1

    @classmethod
    def read(cls, reader: streams.Reader) -> String:
        """Read a null-terminated string from a stream."""
        value = []
        while ((len(value) < cls.max_length)
                and (byte_list := reader.read_bytes(1))
                and (byte := byte_list[0])):
            value.append(byte)
        return cls(bytes(value).decode('utf8'))

    def __len__(self) -> int:
        """Get the number of bytes the string takes up."""
        return 1 + len(self.value)

    def write(self, writer: streams.Writer):
        """Write a null-terminated string."""
        writer.write_bytes(self.value.encode('utf-8') + b'\x00')


class CharArray(StringBase):
    """Reader/writer for a string prefixed with it's length."""

    @classmethod
    def read(cls, reader: streams.Reader) -> CharArray:
        """Read a character array from a stream."""
        length = reader.read(UInt32)
        raw = reader.read_bytes(length.value)
        try:
            value = raw.decode('utf-8')
        except UnicodeDecodeError:
            print('Warning: Bad chararray (invalid unicode).')
            value = ''
        return cls(value)

    def __len__(self) -> int:
        """Get the number of bytes the string takes up."""
        return 4 + len(self.value)

    def write(self, writer: streams.Writer):
        """Write a character array to a stream."""
        writer.align(16)
        writer.write(UInt32(len(self.value)))
        writer.write_bytes(self.value.encode('utf-8'))
