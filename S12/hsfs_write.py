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


# return true if success
def add_entry(directory_block: io.BytesIO, entry: DirEntry) -> bool:
    offset = 0
    while offset < BLOCK_SIZE:
        flags, name_bytes, size, *starting_blocks = struct.unpack_from(
            "B59sI16I", directory_block, offset
        )
        if flags & IS_USED == 0:
            break
        offset += DIR_ENTRY_SIZE
    if offset >= BLOCK_SIZE:
        return False
    write_entry(directory_block, offset, entry)
    return True

def write_entry(directory_block: io.BytesIO, offset: int, entry: DirEntry):
    flags = IS_USED
    if entry.is_dir:
        flags |= IS_DIR
    if entry.is_indirect:
        flags |= IS_INDIRECT
    name_bytes = entry.name.encode("utf-8")
    starting_blocks = entry.entry_blocks
    starting_blocks += [0] * (BLOCKS_IN_DIRECTORY_ENTRY - len(entry.entry_blocks))
    struct.pack_into(
        "B59sI16I",
        directory_block,
        offset,
        flags,
        name_bytes,
        entry.size,
        *starting_blocks
    )

def convert_to_indirect_blocks_if_necessary(entry: DirEntry, target_file: io.FileIO, next_block: int) -> int:
    if len(entry.entry_blocks) > BLOCKS_IN_DIRECTORY_ENTRY:
        all_blocks = entry.entry_blocks
        entry.is_indirect = True
        entry.entry_blocks = []
        offset = 0
        while offset < len(all_blocks):
            entry.entry_blocks.append(next_block)
            blocks_page = all_blocks[offset:offset + BLOCKS_IN_INDIRECT_BLOCK]
            blocks_page += [0] * (BLOCKS_IN_INDIRECT_BLOCK-len(blocks_page))
            target_file.seek(BLOCK_SIZE * next_block)
            target_file.write(struct.pack(INDIRECT_BLOCK_FORMAT, *blocks_page))
            next_block += 1
            offset += BLOCKS_IN_INDIRECT_BLOCK
        return next_block + 1
    return next_block

# returns the next block, size of directory entry in bytes and list of blocks that entry occupies
def convert_directory_to_hsfs_recursively(directory: str, target_file: io.FileIO, next_block: int) -> tuple[int, int, list[int]]:
    target_file.seek(BLOCK_SIZE * next_block)
    entries_per_block = BLOCK_SIZE // DIR_ENTRY_SIZE

    entries = list(os.scandir(directory))

    dir_blocks_count = math.ceil(len(entries) / entries_per_block)
    if next_block == 0 and dir_blocks_count != 1:
        raise Exception("root directory data should occupy exactly one block")

    # first, write dummy blocks
    dir_block_start = next_block
    empty_block = bytearray(BLOCK_SIZE)
    for b_index in range(dir_blocks_count):
        target_file.write(empty_block)

    # then, write subdirectories and files
    next_block += dir_blocks_count
    my_entries = []
    for e in entries:
        if e.is_dir():
            next_block, dir_size, all_blocks = convert_directory_to_hsfs_recursively(e.path, target_file, next_block)
            my_entry = DirEntry(e.name, True, False, dir_size, all_blocks)
            next_block = convert_to_indirect_blocks_if_necessary(my_entry, target_file, next_block)
            my_entries.append(my_entry)
        else:
            file_size = os.path.getsize(e.path)
            file_blocks_count = math.ceil(file_size / BLOCK_SIZE)
            # Reshuffle file blocks. Not necessary and even ill-advised in real filesystem, but
            # I want to make it harder to decode the file, so.
            block_ids = list(range(next_block, next_block+file_blocks_count))
            next_block += file_blocks_count
            random.shuffle(block_ids)
            data = open(e.path, "rb")
            buffer = bytearray(BLOCK_SIZE)
            for i in range(file_blocks_count):
                data.readinto(buffer)
                block_id = block_ids[i]
                target_file.seek(BLOCK_SIZE * block_id)
                target_file.write(buffer)
            my_entry = DirEntry(e.name, False, False, os.path.getsize(e.path), block_ids)
            next_block = convert_to_indirect_blocks_if_necessary(my_entry, target_file, next_block)
            my_entries.append(my_entry)

    # then, actually write directory entries
    dir_blocks = []
    for b_index in range(dir_blocks_count):
        block = bytearray(BLOCK_SIZE)
        entries = my_entries[b_index * entries_per_block:(b_index+1) * entries_per_block]
        for e in entries:
            assert(add_entry(block, e))
        target_file.seek((dir_block_start + b_index) * BLOCK_SIZE)
        target_file.write(block)
        dir_blocks.append(dir_block_start + b_index)
    return (next_block, DIR_ENTRY_SIZE * len(my_entries), dir_blocks)



convert_directory_to_hsfs_recursively(sys.argv[1], open(sys.argv[2], "wb"), 0)
