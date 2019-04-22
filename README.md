This project is comprised of the following scripts
- lang_cinesite_pyqt_test.py
- lang_cinesite_imgseq_test.py

## lang_cinesite_pyqt_test
PyQt GUI to render a sphere (using Arnold) with the option to change the colour. The Arnold log is spied to populate a text field.

### Usage

This script was meant to be run in the 'main scope'. 

Uses/requires the following:
- [Python 3.7 (64-bit)](https://www.python.org/ftp/python/3.7.3/python-3.7.3-amd64.exe)
- [PyQt5](https://pypi.org/project/PyQt5/)
- [Arnold SDK](https://www.arnoldrenderer.com/dynamic_resources/product_downloads/2764/files/Arnold-5.3.0.2-windows.zip)

Also requires modules provided in this repo:
- ainodes.py


### Other notes

The script will create a log file and the rendered image in the same location as the script.

## lang_cinesite_imgseq_test

Function which finds animated sequences in a given directory and prints their frame ranges in the following format:

> `name: 1001-2000` (if there are no gaps)
> 
> `name: 1001, 1003-1500, 1600-2000` (if there are gaps)

The format for an animated sequence is `name.####.ext`

> e.g. `/job/.../my_render_v001.1001.jpg`

This function follows these basic steps:

1. Get the file list and sort
2. Iterate through the files and generate a dict of lists (`imgseq`). The keys of of the dict are the sequence names; the value is a list of low-high list-pairs. It can be described like this:

```py
	# imgseq = {
	# 	'render_v001': [
	# 		[low_frame_int, high_frame_int]
	# 	]
	# }
```
Each time a frame skips more than 1 frame from the previous recorded frame, a new 'list-pair' is created and appended.

3. Iterate through `imgseq` converting existing low-frame/high-frame values as formatted zfill'd ranges or single frames format into a list.

4. Iterate through zfilled list and print into format.

### Usage

Input a valid directory into the function `print_frame_ranges()`.

