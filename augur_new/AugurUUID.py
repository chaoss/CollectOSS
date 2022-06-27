from __future__ import annotations
import uuid, typing

class AugurUUID:
    def __init__(self, platform: int=0, owner: int=0, repo: int=0):
        self.bytes = list(int(0).to_bytes(16, "big"))
        if platform != 0:
            self.set_platform_id(platform)
        if owner != 0:
            self.set_owner_id(owner)
        if repo != 0:
            self.set_repo_id(repo)

    def is_valid_index(self, index: int)-> bool:
        return index >= 0 and index < len(self.bytes)

    def set_bytes(self, byte_array: typing.Union[list, bytes], start_byte: int):
        if not self.is_valid_index(start_byte):
            raise ValueError(f"Start byte must be witin range(0, 16), value: {start_byte}")
        if (len(self.bytes) - len(byte_array) - start_byte) < 0:
            raise ValueError(f"Too many bytes for start index, available: {len(self.bytes) - start_byte}, required: {len(byte_array)}")

        for i in range(start_byte, start_byte + len(byte_array)):
            self.bytes[i] = byte_array[i - start_byte]

    def set_platform_id(self, platform_id: int):
        try:
            platform_id = int(platform_id)
            platform_bytes = platform_id.to_bytes(1, "big")
        except ValueError as e:
            raise ValueError("The platform_id must be an integer") from None
        except OverflowError as e:
            raise ValueError(f"The platform_id must be one byte in size: {platform_id} is too big") from None

        self.set_bytes(platform_bytes, 0)

    def set_owner_id(self, owner_id: int):
        try:
            owner_id = int(owner_id)
            owner_bytes = owner_id.to_bytes(4, "big")
        except ValueError as e:
            raise ValueError("The owner_id must be an integer") from None
        except OverflowError as e:
            raise ValueError(f"The owner_id must be at most 4 bytes in size: {owner_id} is too big") from None

        self.set_bytes(owner_bytes, 1)

    def set_repo_id(self, repo_id: int):
        try:
            repo_id = int(repo_id)
            repo_bytes = repo_id.to_bytes(4, "big")
        except ValueError as e:
            raise ValueError("The repo_id must be an integer") from None
        except OverflowError as e:
            raise ValueError(f"The repo_id must be at most 4 bytes in size: {repo_id} is too big") from None

        self.set_bytes(repo_bytes, 5)

    def to_UUID(self)-> uuid.UUID:
        return uuid.UUID(bytes=bytes(self.bytes))

    def __int__(self)-> int:
        return int.from_bytes(self.bytes, "big")

    def __getitem__(self, index: int)-> int:
        return self.bytes[index]

    def __setitem__(self, index: int, value: int):
        try:
            value = int(value)
            value_byte = value.to_bytes(1, "big")
        except ValueError as e:
            raise ValueError("The value must be an integer") from None
        except OverflowError as e:
            raise ValueError(f"The value must be one byte: {value} is too big") from None
        if not self.is_valid_index(index):
            raise IndexError(f"Index {index} out of bounds")

        self.bytes[index] = value_byte[0]

    # Referencing a class type within itself like this requies the annotations import from above
    def __eq__(self, other: AugurUUID)-> bool:
        return self.bytes == other.bytes

    def __lt__(self, other: AugurUUID)-> bool:
        return int(self) < int(other)

    def __gt__(self, other: AugurUUID)-> bool:
        return int(self) > int(other)

    def __len__(self)-> int:
        return len(self.bytes)

    def __str__(self)-> str:
        return str(self.to_UUID())

    def __iter__(self):
        return (byte for byte in self.bytes)

# Some examples of using this class:
id = AugurUUID()

print(id)

id[0] = 17

id.set_owner_id(1)

print(int(id))

# for byte in id:
#     print(byte)

print(id[0])

print(AugurUUID(17, 1, 1).bytes)
