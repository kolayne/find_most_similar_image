# find_nearest_image
Sorts an array of images by color similarity to a given image.

Imagine you are given a directory with a HUGE amount of images inside and something like a screenshot of one of them.

This script allows you to find an image (in fact images) visually nearest to a given (target) image.

It also allows to quickly search for images, similar to different targets, if you are searching in the same folder
## Usage
```
usage: find_nearest_image.py [-h] {precalculate,search} --storage STORAGE [--fork FORK] [--dir DIR] [--split-depth SPLIT_DEPTH] [--target TARGET]

Sorts an array of images by color similarity to a given image.

Imagine you are given a directory with a HUGE amount of images inside and something like a screenshot of one of them.

This script allows you to find an image (in fact images) visually nearest to a given (target) image.

It also allows to quickly search for images, similar to different targets.

Abstract usage:
    1. Precalculate data for an images set (multiprocessing is out of the box)
    2. Search for images similar to target

positional arguments:
  {precalculate,search}
                        The mode in which you want to run

optional arguments:
  -h, --help            show this help message and exit
  --storage STORAGE, -p STORAGE
                        Path to the precalculated data storage

Precalculation mode:
  --fork FORK, -f FORK  Number of parallel processes for precalculation (default 1)
  --dir DIR, -d DIR     Path to the direcotory with images to precalculate data for
  --split-depth SPLIT_DEPTH, -s SPLIT_DEPTH
                        When calculating average colors, all images are split into SPLIT_DEPTH**2 rectangles, average color is calculated for each of them. (default 4)

Search mode:
  --target TARGET, -t TARGET
                        Path to the target image to search similar to (note that split depth is detected automatically from the storage)

Examples:
    ./find_nearest_image.py precalculate --storage dir1_storage.json --dir ./dir1
    ./find_nearest_image.py search --storage dir1_storage.json --target img1.png
```
