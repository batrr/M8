from typing import Generator
from dataclasses import dataclass
import struct, io, os, math, sys, random

# flags
IS_USED = 1
IS_DIR = 2
IS_INDIRECT = 4

BLOCK_SIZE = 4096
BLOCKS_IN_DIRECTORY_ENTRY = 16
BLOCKS_IN_INDIRECT_BLOCK = BLOCK_SIZE // 4
INDIRECT_BLOCK_FORMAT = "<1024I"

@dataclass
class DirEntry:
    name: str
    is_dir: bool
    # If entry is "direct" it means that file/directory data has no more than 16 blocks.
    # In this case the 16 references to blocks in dir entry are referencing the data blocks.

    # If entry is "indirect" it means that file/directory data has more than 16 blocks.
    # In this case the 16 references to blocks in dir entry are referencing the blocks that contain
    # references to actual data blocks.
    is_indirect: bool
    size: int
    entry_blocks: list[int] # up to 16


DIR_ENTRY_SIZE = 128
DIR_ENTRY_FORMAT = "<B59sI16I"
# each dir entry is 128 bytes:
# 1 byte flags
# 59 bytes file name
# 4 bytes total size of file or directory data
# 64 = 4 * 16 bytes ids of starting blocks


# TODO use block entry size and not fetch zeros
def filter_blocks(blocks: list[int]) -> list[int]:
    return list(filter(lambda x : x != 0, blocks))

def check_flag(flags: int, flag: int) -> bool:
    return (flags & flag) != 0

def get_entries(directory_block: io.BytesIO) -> Generator[DirEntry, None, None]: 
    offset = 0
    while offset < BLOCK_SIZE:
        flags, name_bytes, size, *starting_blocks = struct.unpack_from(
            DIR_ENTRY_FORMAT, directory_block, offset
        )
        if flags & IS_USED == 0:
            print(offset, BLOCK_SIZE)
            break
        
        entry = DirEntry(
            name_bytes.decode("utf-8").rstrip("\x00"), 
            check_flag(flags, IS_DIR),
            check_flag(flags, IS_INDIRECT),
            size,
            filter_blocks(starting_blocks),
            )
        yield entry
        
        offset += DIR_ENTRY_SIZE

def get_blocks(entry: DirEntry, source_file: io.FileIO) -> list[int]:
    next_blocks = []
    if entry.is_indirect:
        for indirect_block_id in entry.entry_blocks:
            if indirect_block_id == 0:
                continue
            source_file.seek(BLOCK_SIZE * indirect_block_id)
            indirect_block = source_file.read(BLOCK_SIZE)
            block_page = struct.unpack(INDIRECT_BLOCK_FORMAT, indirect_block)
            next_blocks += filter_blocks(block_page)
    else:
        next_blocks += entry.entry_blocks

    return next_blocks

def convert_hsfs_to_directory_recursively(target_directory: str, source_file: io.FileIO, blocks: list[int]) -> tuple[int, int, list[int]]:
    os.mkdir(target_directory)
    for block_id in blocks:
        source_file.seek(BLOCK_SIZE * block_id)
        block = source_file.read(BLOCK_SIZE)
        for entry in get_entries(block):
            path = os.path.join(target_directory, entry.name)
            next_blocks = get_blocks(entry, source_file)
            if entry.is_dir:
                convert_hsfs_to_directory_recursively(path, source_file, next_blocks)
            else:
                size = entry.size
                with open(path, "wb") as file:
                    for block_id in next_blocks:
                        source_file.seek(BLOCK_SIZE * block_id)
                        block = source_file.read(BLOCK_SIZE)
                        
                        current_size = min(size, BLOCK_SIZE)             
                        data = block[:current_size]
                        size -= current_size
                        
                        file.write(data)


convert_hsfs_to_directory_recursively(sys.argv[1], open(sys.argv[2], "rb"), [0])
