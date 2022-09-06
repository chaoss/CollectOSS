from __future__ import annotations

import uuid
import typing

class AugurUUID:
    struct = {
        "platform": {"start": 0, "size": 1}
    }
    def __init__(self, platform: int=0):
        self.bytes = list(int(0).to_bytes(16, "big"))

        if platform != 0:
            self.set_platform_id(platform)

    def is_valid_index(self, index: int)-> bool:
        return index >= 0 and index < len(self.bytes)

    def set_bytes(self, byte_array: typing.Union[list, bytes], start_byte: int):
        if not self.is_valid_index(start_byte):
            raise ValueError(f"Start byte must be witin range(0, 16), value: {start_byte}")
        if (len(self.bytes) - len(byte_array) - start_byte) < 0:
            raise ValueError(f"Too many bytes for start index, available: {len(self.bytes) - start_byte}, required: {len(byte_array)}")

        for i in range(start_byte, start_byte + len(byte_array)):
            self.set_byte(i, byte_array[i - start_byte])

    def write_int(self, source: int, start_byte: int, num_bytes: int):
        try:
            source = int(source)
            source_bytes = source.to_bytes(num_bytes, "big")
        except ValueError:
            raise ValueError("The source must be an integer") from None
        except OverflowError:
            raise ValueError(f"The source must be at most {num_bytes} bytes in size: {source} is too big") from None

        self.set_bytes(source_bytes, start_byte)

    def get_int(self, start_byte: int, num_bytes: int):
        source_bytes = []

        for i in range(start_byte, start_byte + num_bytes):
            source_bytes.append(self.get_byte(i))

        return int.from_bytes(source_bytes, "big")

    def set_platform_id(self, platform_id: int):
        try:
            platform_id = int(platform_id)
            platform_bytes = platform_id.to_bytes(1, "big")
        except ValueError:
            raise ValueError("The platform_id must be an integer") from None
        except OverflowError:
            raise ValueError(f"The platform_id must be one byte in size: {platform_id} is too big") from None

        self.set_bytes(platform_bytes, 0)

    def to_UUID(self)-> uuid.UUID:
        return uuid.UUID(bytes=bytes(self.bytes))

    def __int__(self)-> int:
        return int.from_bytes(self.bytes, "big")

    def get_byte(self, index: int)-> int:
        try:
            return self.bytes[index]
        except:
            raise IndexError("UUID index out of range") from None

    def set_byte(self, index: int, value: int):
        try:
            value = int(value)
            value_byte = value.to_bytes(1, "big")
        except ValueError:
            raise ValueError("The value must be an integer") from None
        except OverflowError:
            raise ValueError(f"The value must be one byte: {value} is too big") from None
        if not self.is_valid_index(index):
            raise IndexError(f"Index {index} out of bounds")

        self.bytes[index] = value_byte[0]

    def __getitem__(self, key: str)-> int:
        structure = self.struct[key]
        return self.get_int(structure["start"], structure["size"])

    def __setitem__(self, key: str, value: int):
        structure = self.struct[key]
        self.write_int(value, structure["start"], structure["size"])

    # Referencing a class type within itself like this requies the annotations import from above
    def __eq__(self, other: AugurUUID)-> bool:
        return self.bytes == other.bytes

    def __lt__(self, other: AugurUUID)-> bool:
        return int(self) < int(other)

    def __gt__(self, other: AugurUUID)-> bool:
        return int(self) > int(other)

    def __len__(self)-> int:
        return len(self.bytes)

    def __dict__(self)-> dict:
        result = {}

        for key in self.struct.keys():
            structure = self.struct[key]
            result[key] = self.get_int(structure["start"], structure["size"])

        return result

    def __str__(self)-> str:
        return str(self.__dict__())

    def __iter__(self):
        return (byte for byte in self.bytes)

class GithubUUID(AugurUUID):
    struct = {
        "platform": {"start": 0, "size": 1},
        "user": {"start": 1, "size": 4},
        "repo": {"start": 5, "size": 3},
        "issue": {"start": 8, "size": 4},
        "event": {"start": 12, "size": 4},
        "metadata": {"start": 12, "size": 4}
    }

    def __init__(self):
        super().__init__(platform = 1)

class UnresolvableUUID(GithubUUID):
    def __init__(self):
        super(GithubUUID, self).__init__(platform = 0)

if __name__ == "__main__":
    pass
    # Some examples of using this class:
    # id = GithubUUID()

    # id["user"] = 15
    # id["repo"] = 65535
    # id["issue"] = 297

    # print(id)

    # uid = UnresolvableUUID()

    # print(uid)

    # id = AugurUUID()
    #
    # print(id)
    #
    # id[0] = 17
    #
    # id.set_owner_id(1)
    #
    # print(int(id))
    #
    # # for byte in id:
    # #     print(byte)
    #
    # print(id[0])
    #
    # print(AugurUUID(17, 1, 1).bytes)
