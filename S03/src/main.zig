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
