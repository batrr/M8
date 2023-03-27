Bad allocator finds first a free block of memory that is large enough and splits it if necessary.
```python
{'total_free_ram': 65533, 'max_free_block': 65533, 'overhead': 2}
{'total_free_ram': 41739, 'max_free_block': 9413, 'overhead': 384}
```
The allocator usually split free memory blocks.
When we are free memory, we end up with two smaller free blocks.
With repeated allocations and releases, we get many small free blocks which are unlikely to be used again.

* Wasted memory. Even if a large contiguous free memory block is available, the allocator does not use it because memory splitted into small blocks.
* Slow. The allocator have to search many small free blocks before finding large enough block.



Best fit allocator finds the smallest a free block of memory that is large enough and splits it if necessary.
```python
{'total_free_ram': 65533, 'max_free_block': 65533, 'overhead': 2}
{'total_free_ram': 40785, 'max_free_block': 28895, 'overhead': 298}
```
A bit better because the allocator is more likely to find blocks with the requested size and doesn't split them.


I think the best way to make this allocator better is by merging small blocks. When we free memory, we can check adjacent blocks and join them together or periodically go through the entire list and merge free memory blocks.



