# Find most similar image

[![Codacy Badge](https://app.codacy.com/project/badge/Grade/55d712073a944bacb55944f83739a493)](https://www.codacy.com/gh/kolayne/find_most_similar_image/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=kolayne/find_most_similar_image&amp;utm_campaign=Badge_Grade)

Sorts an array of images by color similarity to a given image.

Imagine you are given a directory with a HUGE amount of images inside and something like a screenshot of one of them.

This script allows you to find an image (in fact images) visually nearest to a given (target) image. It prints a table with absolute paths to original images sorted by similarity so that last entry is the most similar to the target

It also allows to quickly search for images, similar to different targets, if you are searching in the same set of images.
## Basic usage
```
$ ./find_most_similar_image.py -h
usage: find_most_similar_image.py [--help]
                                  [--mode {precalculate,search,onflight}]
                                  [--storage STORAGE] [--dir DIR]
                                  [--target TARGET] [--suppress-extras]

PLASE, NOTE, by default only REQUIRED arguments are displayed in the help message. Use -h/--help argument TWICE to also see OPTIONAL arguments

Sorts an array of images by color similarity to a given image.
Imagine you are given a directory with a HUGE amount of images inside and something like a screenshot of one of them.
This script allows you to find an image (in fact images) visually nearest to a given (target) image. It prints a table with absolute paths to original images sorted by similarity so that last entry is the most similar to the target
It also allows to quickly search for images, similar to different targets, if you are searching in the same set of images.

Abstract usage:
    1. Precalculate data for an images set (multiprocessing is out of the box, see --fork at detailed help)
    2. Search for images an similar to the target
This two steps can be combined into one with the ONFLIGHT mode (default)

optional arguments:
  --help, -h            Show help message and exit. Use it once (-h) to only see most needed arguments, twice (-hh) for detailed help with all arguments described

GLOBAL args:
  --mode {precalculate,search,onflight}, -m {precalculate,search,onflight}
                        The mode in which you want to run ("precalculate" to create storage, "search" to search for images using storage, "onflight" (DEFAULT) is precalculate+search)
  --storage STORAGE, -p STORAGE
                        Path to a data storage (to be created or read)

PRECALCULATION (or ONFLIGHT) mode arguments:
  --dir DIR, -d DIR     Path to the directory with images to precalculate data for

SEARCH (or ONFLIGHT) mode arguments:
  --target TARGET, -t TARGET
                        Path to the target image to search similar to (note that split depth is detected automatically from the storage)
  --suppress-extras, -x
                        Just print absolute path to the most similar image, suppress any other output. Equivalent to "--best-only --no-notes --table-fmt plane --no-headers --no-index --no-error-rate"

Examples:
    With two separate commands:
        ./find_most_similar_image.py --mode precalculate --storage ./storage.json --dir ./source_dir
        ./find_most_similar_image.py --mode search --storage ./storage.json --target ./image.png
    Or with one command:
        ./find_most_similar_image.py --dir ./source_dir --target ./image.png
    Also possible (to save storage):
        ./find_most_similar_image.py --dir ./source_dir --target ./image.png --storage ./storage.json
    When you want to omit all extra messages and, for example, use the output as an argument to another command:
        ./find_most_similar_image.py --dir ./source_dir --target ./image.png --best-only --table-fmt=plain --no-headers --no-notes \
            --no-index --no-error-rate
```
## Advanced usage
```
$ ./find_most_similar_image.py -hh
usage: find_most_similar_image.py [--help]
                                  [--mode {precalculate,search,onflight}]
                                  [--storage STORAGE] [--fork FORK]
                                  [--dir DIR] [--split-depth SPLIT_DEPTH]
                                  [--target TARGET] [--suppress-extras]
                                  [--best-only] [--no-notes]
                                  [--table-fmt TABLE_FMT] [--no-headers]
                                  [--no-index] [--no-error-rate]

PLASE, NOTE, by default only REQUIRED arguments are displayed in the help message. Use -h/--help argument TWICE to also see OPTIONAL arguments

Sorts an array of images by color similarity to a given image.
Imagine you are given a directory with a HUGE amount of images inside and something like a screenshot of one of them.
This script allows you to find an image (in fact images) visually nearest to a given (target) image. It prints a table with absolute paths to original images sorted by similarity so that last entry is the most similar to the target
It also allows to quickly search for images, similar to different targets, if you are searching in the same set of images.

Abstract usage:
    1. Precalculate data for an images set (multiprocessing is out of the box, see --fork at detailed help)
    2. Search for images an similar to the target
This two steps can be combined into one with the ONFLIGHT mode (default)

optional arguments:
  --help, -h            Show help message and exit. Use it once (-h) to only see most needed arguments, twice (-hh) for detailed help with all arguments described

GLOBAL args:
  --mode {precalculate,search,onflight}, -m {precalculate,search,onflight}
                        The mode in which you want to run ("precalculate" to create storage, "search" to search for images using storage, "onflight" (DEFAULT) is precalculate+search)
  --storage STORAGE, -p STORAGE
                        Path to a data storage (to be created or read)

PRECALCULATION (or ONFLIGHT) mode arguments:
  --fork FORK, -f FORK  Number of parallel processes for precalculation (DEFAULT 1)
  --dir DIR, -d DIR     Path to the directory with images to precalculate data for
  --split-depth SPLIT_DEPTH, -s SPLIT_DEPTH
                        When calculating average colors, all images are split into SPLIT_DEPTH^2 rectangles, average color is calculated for each of them. (DEFAULT 4)

SEARCH (or ONFLIGHT) mode arguments:
  --target TARGET, -t TARGET
                        Path to the target image to search similar to (note that split depth is detected automatically from the storage)
  --suppress-extras, -x
                        Just print absolute path to the most similar image, suppress any other output. Equivalent to "--best-only --no-notes --table-fmt plane --no-headers --no-index --no-error-rate"

OUTPUT STYLE of search (or onflight) mode:
  --best-only, -b       Only print one image filename which is the best match
  --no-notes            Don't show constant notes for user, only print the final table
  --table-fmt TABLE_FMT
                        Table format (explained in detail in the `tabulate` library's docs). Use "plain" to not use any pseudo-graphics (DEFAULT "github")
  --no-headers          Don't show headers of the final table being printed
  --no-index            Don't show first column with indexes in the final table being printed
  --no-error-rate       Don't show last column with error rate in the final table being printed

Examples:
    With two separate commands:
        ./find_most_similar_image.py --mode precalculate --storage ./storage.json --dir ./source_dir
        ./find_most_similar_image.py --mode search --storage ./storage.json --target ./image.png
    Or with one command:
        ./find_most_similar_image.py --dir ./source_dir --target ./image.png
    Also possible (to save storage):
        ./find_most_similar_image.py --dir ./source_dir --target ./image.png --storage ./storage.json
    When you want to omit all extra messages and, for example, use the output as an argument to another command:
        ./find_most_similar_image.py --dir ./source_dir --target ./image.png --best-only --table-fmt=plain --no-headers --no-notes \
            --no-index --no-error-rate
```
## Algorithm overview
The algorithm of looking for similar images is pretty simple.

Firstly (in `precalculate` mode), the app creates a storage with cached data of images inside `--dir` and it's subdirectories. Each of these images is split into `--split-depth` * `--split-depth` (approximately) equal rectangles, and an average color value is calculated for each of the rectangles. These average colors (and some meta data) are stored in the `--storage` file.

After that (in `search` mode), the `--storage` file is read, the `--target` image is split into the same number of rectangles the candidates were split into, the average colors for the last rectangles are calculated. A distance between two images now is the sum of distances between corresponding average colors. All the images are sorted by a value called `Error rate` which is the distance between an image and the target image.
## Known issues
* Tqdm bars may behave strange (for example, create empty lines or fake bars) when forking is used
