import struct
from io import BytesIO, StringIO

class EndianBinaryReader:
    def __init__(self, filepath : str, endianness : str = 'little'): #overwritten
        self.set_endianness(endianness)
        self.filepath = filepath
        self.file = open(self.filepath,mode='rb')
        self.read = self.file.read
        self.tell = self.file.tell
        self.seek = self.file.seek

    def set_endianness(self, endianness : str):
        if endianness == 'little':
            self.endian_flag = '<'
        elif endianness == 'big':
            self.endian_flag = '>'
        else:
            raise Exception(r"Unknown endianness : should be 'little' or 'big'")
        
    def read_Int8(self) -> int:
        return struct.unpack(f'{self.endian_flag}b',self.read(1))[0]

    def read_UInt8(self) -> int:
        return struct.unpack(f'{self.endian_flag}B',self.read(1))[0]

    def read_Int16(self) -> int:
        return struct.unpack(f'{self.endian_flag}h',self.read(2))[0]
    
    def read_UInt16(self) -> int:
        return struct.unpack(f'{self.endian_flag}H',self.read(2))[0]

    def read_Int32(self) -> int:
        return struct.unpack(f'{self.endian_flag}i',self.read(4))[0]
    
    def read_UInt32(self) -> int:
        return struct.unpack(f'{self.endian_flag}I',self.read(4))[0]

    def read_Int64(self) -> int:
        return struct.unpack(f'{self.endian_flag}q',self.read(8))[0]
    
    def read_UInt64(self) -> int:
        return struct.unpack(f'{self.endian_flag}Q',self.read(8))[0]
    
    def read_float32(self) -> float:
        struct.unpack(f'{self.endian_flag}f',self.read(4))[0]
    
    def read_bool(self):
        return self.read_UInt8() == 1
    
    def check_magic(self, magic):
        check = self.read(4)
        if check != magic:
            raise Exception(f"Error: Invalid magic. Expected {str(magic)}, read {str(check)}")
        return check
    
    def read_string_until_null(self) -> bytes:
        data = b""
        byte = self.read(1)
        while byte not in [b'\x00', b'']:
            data += byte
            byte = self.read(1)
        if byte == b'':
            raise EOFError()
        return data
    
    def get_filesize(self) -> int:
        pos = self.tell()
        self.seek(0, 2)
        filesize = self.tell()
        self.seek(pos)
        return filesize

class EndianBinaryFileReader(EndianBinaryReader):
    def __init__(self, filepath : str, endianness : str = 'little'):
        self.set_endianness(endianness)
        self.filepath = filepath
        self.file = open(self.filepath,mode='rb')
        self.read = self.file.read
        self.tell = self.file.tell
        self.seek = self.file.seek

    def __enter__(self):
        return self

    def __exit__(self,exc_type, exc_val, exc_tb):
        self.file.close()

class EndianBinaryStreamReader(EndianBinaryReader):
    def __init__(self,stream : bytes, endianness : str = 'little'):
        self.set_endianness(endianness)
        self.stream = BytesIO(stream)
        self.read = self.stream.read
        self.tell = self.stream.tell
        self.seek = self.stream.seek
        self.getvalue = self.stream.getvalue