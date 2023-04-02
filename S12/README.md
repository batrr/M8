
# Harbour Space Filesystem

Harbour Space Filesystem - simple and efficient way of storing data.



Block - 4KB data block
- Directory block store directory entries up to 32
- Data block store file data
- Indirect block store addresses of direct/data blocks up to 1024

Directory entry - main structure of the filesystem. Represent file or directory. Store basic information such as name, flags and entry blocks. 
- For files, entry blocks is a list of data blocks where the file data is stored.
- For directory, entry blocks is a list of directory blocks where the nested directory entries are stored.

If the number of entry blocks is less or equal to 16, blocks list is stored directly in the directory entry otherwise indirect blocks with actual blocks list are used.


Issues:
- We can store only files of size
    (entry blocks) * (indirect block capacity) * (data block size) =
    16 * 1024 * 4096 = 2 ^ 26 B = 64 MB :(
- To navigate in a directory we should iterate over all directory entries
- Fragmentation - inefficient use of space from the way we allocate blocks
- Security - no permissions, encryption

Future improvements:
- To make indirect block store indirect blocks allowing to store infinite big files
- To use caching and more advanced data structure for data entries with a big number of entry blocks
- To use better allocator(that we need anyway to make filesystem updatable)
- To add more flags for security?

To decode the filesystem use `python hsfs_read.py hsfs hsfs.img`. Filesystem will be decoded in hsfs folder.

![](winlin.png)


Ideas on updating file:
- Find directory entry of the file or create a new one
- Adjust the size of the directory entry (create or delete blocks). We will need some allocator for that
- write new data in blocks
- Update direct/indirect type  
- TODO: make it persistence