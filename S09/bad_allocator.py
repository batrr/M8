import array, random

mem_size = 64 * 1024

MAGIC_ALLOCATED_BLOCK = 12345
MAGIC_NO_NEXT_FREE_BLOCK = 99999999

# Our memory is 64K unsigned 32-bit integers (so, 256 kB)
memory = array.array("L", [0] * mem_size)

# memory cell 0 will be always pointing to the first free block
FREE_LIST_INITIAL_ADDRESS = 0

# free block layout:
# memory[start-2] = size
# memory[start-1] = address_of_the_next_block

# allocated block layout:
# memory[start-2] = size
# memory[start-1] = MAGIC_ALLOCATED_BLOCK
# the user data can be written from the "start"


def init_free_block(location, size, next_free_block):
    memory[location - 2] = size
    memory[location - 1] = next_free_block  # next block


def allocate(requested_size):
    # we walk the free list, checking every free block (starting at free_block_ptr);
    # we also need to keep track of where in the memory free_block_ptr was stored - because we might
    # need to change free_block_ptr when we are splitting blocks

    # we need a pointer to pointer - because we might need to overwrite the pointer value
    # initially we set this to 0, that means that memory[0] holds the address of the first free block
    free_block_ptr_ptr = FREE_LIST_INITIAL_ADDRESS
    free_block_ptr = memory[free_block_ptr_ptr]

    while free_block_ptr != MAGIC_NO_NEXT_FREE_BLOCK:
        block_size = memory[free_block_ptr - 2]
        if block_size >= requested_size:
            if block_size >= requested_size + 3:
                # turn the remainder of the free block into a smaller free block
                allocated_block_size_with_headers = 2 + requested_size
                new_free_block_offset = (
                    free_block_ptr + allocated_block_size_with_headers
                )
                new_free_block_size = block_size - allocated_block_size_with_headers
                next_free_block_ptr = memory[free_block_ptr - 1]
                init_free_block(
                    new_free_block_offset, new_free_block_size, next_free_block_ptr
                )
                memory[free_block_ptr_ptr] = new_free_block_offset
                # trim the size of the first part of the block
                memory[free_block_ptr - 2] = requested_size
            else:
                # just turn the whole of the free block to the allocated block
                memory[free_block_ptr_ptr] = memory[free_block_ptr - 1]
            memory[free_block_ptr - 1] = MAGIC_ALLOCATED_BLOCK
            assert memory[free_block_ptr - 2] >= requested_size
            return free_block_ptr
        free_block_ptr_ptr = free_block_ptr - 1
        free_block_ptr = memory[free_block_ptr_ptr]
    raise Exception(
        f"could not allocate requested {requested_size} elements of memory space"
    )


def free(allocated_block_ptr):
    assert memory[allocated_block_ptr - 1] == MAGIC_ALLOCATED_BLOCK
    init_free_block(allocated_block_ptr, memory[allocated_block_ptr - 2], memory[0])
    memory[0] = allocated_block_ptr


def max_object_can_allocate():
    free_block_ptr = memory[0]
    m = 0
    while pointer != MAGIC_NO_NEXT_FREE_BLOCK:
        block_size = memory[free_block_ptr - 2]
        if block_size > m:
            m = block_size
        pointer = memory[free_block_ptr - 1]
    return m


def total_free_ram():
    free_block_ptr = memory[0]
    s = 0
    while pointer != MAGIC_NO_NEXT_FREE_BLOCK:
        block_size = memory[free_block_ptr - 2]
        s += block_size
        free_block_ptr = memory[free_block_ptr - 1]
    return s


def stats():
    free_block_ptr = memory[0]
    m = 0
    count = 0
    total = 0
    while free_block_ptr != MAGIC_NO_NEXT_FREE_BLOCK:
        block_size = memory[free_block_ptr - 2]
        if block_size > m:
            m = block_size
        total += block_size
        count += 1
        free_block_ptr = memory[free_block_ptr - 1]
    # overhead is the space wasted for the headers of free blocks
    # we don't count the overhead for the headers of the allocated blocks, it's considered to
    # be inevitable
    return dict(total_free_ram=total, max_free_block=m, overhead=count * 2)


def ensure_no_overlaps(block_pointers):
    # inefficient but simple check
    all_used_cells = set()
    for p in block_pointers:
        assert memory[p - 1] == MAGIC_ALLOCATED_BLOCK
        size = memory[p - 2]
        used_cells = set(range(p, p + size))
        assert len(all_used_cells & used_cells) == 0
        all_used_cells.update(used_cells)


# initially, turn all the memory into one big free block
first_free_block_start = (
    3
)  # first cell is free list start, 2 more reserved for free block header
init_free_block(
    first_free_block_start, mem_size - first_free_block_start, MAGIC_NO_NEXT_FREE_BLOCK
)
memory[0] = first_free_block_start

print(stats())

all_allocated_blocks = []


for i in range(50):
    a = allocate(random.randint(10, 50) * 16)
    b = allocate(random.randint(10, 50) * 16)
    c = allocate(random.randint(10, 50) * 16)
    d = allocate(random.randint(10, 50) * 16)
    e = allocate(random.randint(10, 50) * 16)
    ensure_no_overlaps(all_allocated_blocks + [a, b, c, d, e])
    free(a)
    free(b)
    free(c)
    free(d)
    all_allocated_blocks.append(e)

print(stats())
