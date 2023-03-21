Password: pwAW96B6

1. Determine file type with `file`

```console
$ file password.elf                                                                                                                     
password.elf: ELF 64-bit LSB shared object, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=0cbaf08a25175401e6e7a026bc75f32a3fc5e6cd, for GNU/Linux 3.2.0, not stripped
```

2. Run gdb

```console
$ gdb password.elf                                                                                                                     
```

3. Run exe and stop it to debug

```console
(gdb) r
Starting program: /home/batrr/study/M8/S06/password.elf 
^C
Program received signal SIGINT, Interrupt.
```

4. Check memory mapping

```console
(gdb) info proc mappings
process 167525
Mapped address spaces:

          Start Addr           End Addr       Size     Offset objfile
      0x555555554000     0x555555555000     0x1000        0x0 /home/batrr/study/M8/S06/password.elf
      0x555555555000     0x555555556000     0x1000     0x1000 /home/batrr/study/M8/S06/password.elf
      0x555555556000     0x555555557000     0x1000     0x2000 /home/batrr/study/M8/S06/password.elf
      0x555555557000     0x555555558000     0x1000     0x2000 /home/batrr/study/M8/S06/password.elf
      0x555555558000     0x555555559000     0x1000     0x3000 /home/batrr/study/M8/S06/password.elf
      0x555555559000     0x55555557a000    0x21000        0x0 [heap]
      0x7ffff7db9000     0x7ffff7ddb000    0x22000        0x0 /usr/lib/x86_64-linux-gnu/libc-2.31.so
      0x7ffff7ddb000     0x7ffff7f53000   0x178000    0x22000 /usr/lib/x86_64-linux-gnu/libc-2.31.so
      0x7ffff7f53000     0x7ffff7fa1000    0x4e000   0x19a000 /usr/lib/x86_64-linux-gnu/libc-2.31.so
      0x7ffff7fa1000     0x7ffff7fa5000     0x4000   0x1e7000 /usr/lib/x86_64-linux-gnu/libc-2.31.so
      0x7ffff7fa5000     0x7ffff7fa7000     0x2000   0x1eb000 /usr/lib/x86_64-linux-gnu/libc-2.31.so
      0x7ffff7fa7000     0x7ffff7fad000     0x6000        0x0 
      0x7ffff7fcb000     0x7ffff7fce000     0x3000        0x0 [vvar]
      0x7ffff7fce000     0x7ffff7fcf000     0x1000        0x0 [vdso]
      0x7ffff7fcf000     0x7ffff7fd0000     0x1000        0x0 /usr/lib/x86_64-linux-gnu/ld-2.31.so
      0x7ffff7fd0000     0x7ffff7ff3000    0x23000     0x1000 /usr/lib/x86_64-linux-gnu/ld-2.31.so
      0x7ffff7ff3000     0x7ffff7ffb000     0x8000    0x24000 /usr/lib/x86_64-linux-gnu/ld-2.31.so
      0x7ffff7ffc000     0x7ffff7ffd000     0x1000    0x2c000 /usr/lib/x86_64-linux-gnu/ld-2.31.so
      0x7ffff7ffd000     0x7ffff7ffe000     0x1000    0x2d000 /usr/lib/x86_64-linux-gnu/ld-2.31.so
      0x7ffff7ffe000     0x7ffff7fff000     0x1000        0x0 
      0x7ffffffde000     0x7ffffffff000    0x21000        0x0 [stack]
  0xffffffffff600000 0xffffffffff601000     0x1000        0x0 [vsyscall]
```

4. Dump memory

```console
(gdb) dump memory stack 0x7ffffffde000     0x7ffffffff000
(gdb) dump memory heap  0x555555559000     0x55555557a000
```

5. Display printable strings in stack and heap

```console
$ strings stack heap
DUUUU
Y=Nb
....
pwAW96B6
```


