#!/bin/sh

rm -rf test/test_dir_read
python3.9 hsfs_write.py test/test_dir test/test_dir.img  
python3.9 hsfs_read.py test/test_dir_read test/test_dir.img  
diff -r test/test_dir test/test_dir_read


rm -rf hsfs
python3.9 hsfs_read.py hsfs hsfs.img  

