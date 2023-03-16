# S03

Check zig: https://ziglang.org/

To compile code install zig and run `zig build`.

To execute `./zig-out/bin/S03`

Source code at `src/main.zig`:

```
const std = @import("std");

pub fn main() !void {
    
    const stdout_file = std.io.getStdOut().writer();
    var bw = std.io.bufferedWriter(stdout_file);
    const stdout = bw.writer();

    const a: f32 = 1.3;
    const b: f32 = 2.6;
    const c: f32 = 3.14;
    
    var x: f32 = 0;
    while (x <= 5) : (x += 1) 
        try stdout.print("{d:.6}\n", .{a * x * x + b * x + c});
    
    try bw.flush();
}
```

Size of binary file 994304 bytes.
```
 stat zig-out/bin/S03                                                                                                                                                                             
 
  File: zig-out/bin/S03
  Size: 994304    	Blocks: 1944       IO Block: 4096   regular file
Device: 10305h/66309d	Inode: 8662741     Links: 1
Access: (0775/-rwxrwxr-x)  Uid: ( 1000/   batrr)   Gid: ( 1000/   batrr)
Access: 2023-03-16 16:57:57.125664672 +0100
Modify: 2023-03-16 16:57:52.433532072 +0100
Change: 2023-03-16 16:57:52.437532185 +0100
 Birth: -

``` 