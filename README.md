# Find most similar image
Sorts an array of images by color similarity to a given image.

Imagine you are given a directory with a HUGE amount of images inside and something like a screenshot of one of them.

This script allows you to find an image (in fact images) visually nearest to a given (target) image.

It also allows to quickly search for images, similar to different targets, if you are searching in the same folder
## Usage
```
usage: find_nearest_image.py [-h] [--mode {precalculate,search,onflight}] [--storage STORAGE] [--fork FORK] [--dir DIR] [--split-depth SPLIT_DEPTH] [--target TARGET]

Sorts an array of images by color similarity to a given image.

Imagine you are given a directory with a HUGE amount of images inside and something like a screenshot of one of them.

This script allows you to find an image (in fact images) visually nearest to a given (target) image.

It also allows to quickly search for images, similar to different targets, if you are searching inside the same folder.

Abstract usage:
    1. Precalculate data for an images set (multiprocessing is out of the box, see --fork)
    2. Search for images similar to target

optional arguments:
  -h, --help            show this help message and exit

Global args:
  --mode {precalculate,search,onflight}, -m {precalculate,search,onflight}
                        The mode in which you want to run (`precalculate` to create storage, `search` to search for images using storage, `onflight` (DEFAULT) is precalculate+search)
  --storage STORAGE, -p STORAGE
                        Path to a data storage (to be created or read)

Precalculation (or onflight) mode:
  --fork FORK, -f FORK  Number of parallel processes for precalculation (DEFAULT 1)
  --dir DIR, -d DIR     Path to the direcotory with images to precalculate data for
  --split-depth SPLIT_DEPTH, -s SPLIT_DEPTH
                        When calculating average colors, all images are split into SPLIT_DEPTH**2 rectangles, average color is calculated for each of them. (DEFAULT 4)

Search (or onflight) mode:
  --target TARGET, -t TARGET
                        Path to the target image to search similar to (note that split depth is detected automatically from the storage)

Examples:
    With two commands:
        ./find_nearest_image.py --mode precalculate --storage storage.json --dir ./some_dir
        ./find_nearest_image.py --mode search --storage storage.json --target some_img.png
    Or with one command:
        ./find_nearest_image.py --dir some_dir --target some_img.png
    Also possible (to save storage):
        ./find_nearest_image.py --dir some_dir --target some_img.png --storage storage.json
```
## Algorithm overview
The algorithm of looking for similar images is pretty simple.

Firstly (in `precalculate` mode), the app creates a storage with cached data of images inside `--dir` and it's subdirectories. Each of these images is split into `--split-depth` * `--split-depth` (approximately) equal rectangles, and an average color value is calculated for each of the rectangles. These average colors (and some meta data) are stored in the `--storage` file.

After that (in `search` mode), the `--storage` file is read, the `--target` image is split into the same number of rectangles the candidates were split into, the average colors for the last rectangles are calculated. A distance between two images now is the sum of distances between corresponding average colors. All the images are sorted by a value called `Error rate` which is the distance between an image and the target image.
## Known issues
* Tqdm bars may behave strange (for example, create empty lines or fake bars) with forking
