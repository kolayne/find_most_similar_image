#!/usr/bin/python3
from sys import argv
from os import walk, path
import json
import argparse
from multiprocessing import Pool
import warnings
from operator import itemgetter
from io import StringIO

import numpy as np
from PIL import Image, UnidentifiedImageError

try:
    from tqdm import tqdm
except ImportError:
    print("`tqdm` library not found. This is not an issue, but I would recommend to install it")
    def tqdm(x, *a, **k): return x
try:
    from termcolor import colored
except ImportError:
    print("`termcolor` library not found. This is not an issue, but I would recommend to install it")
    def colored(x, *a, **k): return x
try:
    from tabulate import tabulate
except ImportError:
    print("`tabulate` library not found. This is not an issue, but I would recommend to install it")
    def tabulate(x, *a, **k): return '\n'.join('\t'.join(map(str, i)) for i in x)


def does_raise(func, args=None, kwargs=None, expected=None, *, reraise_other=True):
    if args is None:
        args = ()
    if kwargs is None:
        kwargs = {}
    if expected is None:
        expected = Exception

    try:
        func(*args, **kwargs)
        return False
    except expected:
        return True
    except:
        if reraise_other:
            raise
        else:
            return False


def chunkify(iterable, chunks_count):
    iterable = list(iterable)
    for i in range(chunks_count):
        yield iterable[i::chunks_count]


def avg(pixels):
    return np.sum(pixels, axis=0) // pixels.size


# `split_depth` is a square rot of count of rectangles an image will be split to
def get_avg_pixels(img, split_depth=2):
    ans = np.zeros((split_depth, split_depth, 3))

    img = np.asarray(img)
    x_size, y_size, _ = img.shape

    for x_multiplier in range(split_depth):
        x_range_from = int(x_size / split_depth * x_multiplier)
        x_range_to = int(x_size / split_depth * (x_multiplier + 1))

        for y_multiplier in range(split_depth):
            y_range_from = int(y_size / split_depth * y_multiplier)
            y_range_to = int(y_size / split_depth * (y_multiplier + 1))

            ans[x_multiplier, y_multiplier] = avg(img[x_range_from:x_range_to, y_range_from:y_range_to].ravel())
    return ans


def get_avged_images_dist(a, b):
    return np.sum(abs(a - b)).item()


def precalculate_part(args):
    candidate_paths = args[0]
    split_depth = args[1]
    tqdm_position = args[2]

    return {candidate_path: get_avg_pixels(Image.open(candidate_path).convert("RGB"), split_depth).tolist()
            for candidate_path in tqdm(candidate_paths, position=tqdm_position)}

def precalculate(candidate_paths, output_file, /, split_depth=2, process_count=1):
    data = {}

    idxes_and_chunks = enumerate(chunkify(candidate_paths, process_count))
    args = map(lambda x: (x[1], split_depth, x[0]), idxes_and_chunks)

    with Pool(process_count) as pool:
        for data_part in pool.imap_unordered(precalculate_part, args):
            data = {**data, **data_part}

    json.dump({'split_depth': split_depth, 'data': data}, output_file)


def get_sorted(target_path, storage_file, reverse=False):
    precalculated = json.load(storage_file)
    split_depth = precalculated['split_depth']
    precalculated_avgs = {k: np.asarray(v) for k, v in precalculated['data'].items()}

    target = Image.open(target_path)
    target_avg = get_avg_pixels(target, split_depth)

    rated_images = [(k, get_avged_images_dist(target_avg, precalculated_avgs[k])) for k in precalculated_avgs.keys()]
    return sorted(rated_images, key=itemgetter(1), reverse=reverse)


description = '''PLASE, NOTE, by default only REQUIRED arguments are displayed in the help message. Use -h/--help \
argument TWICE to also see OPTIONAL arguments

Sorts an array of images by color similarity to a given image.
Imagine you are given a directory with a HUGE amount of images inside and something like a screenshot of one of them.
This script allows you to find an image (in fact images) visually nearest to a given (target) image. It prints a table \
with absolute paths to original images sorted by similarity so that last entry is the most similar to the target
It also allows to quickly search for images, similar to different targets, if you are searching in the same set of \
images.

Abstract usage:
    1. Precalculate data for an images set (multiprocessing is out of the box, see --fork at detailed help)
    2. Search for images an similar to the target
This two steps can be combined into one with the ONFLIGHT mode (default)
'''

examples = f'''Examples:
    With two separate commands:
        {argv[0]} --mode precalculate --storage ./storage.json --dir ./source_dir
        {argv[0]} --mode search --storage ./storage.json --target ./image.png
    Or with one command:
        {argv[0]} --dir ./source_dir --target ./image.png
    Also possible (to save storage):
        {argv[0]} --dir ./source_dir --target ./image.png --storage ./storage.json
    When you want to omit all extra messages and, for example, use the output as an argument to another command:
        {argv[0]} --dir ./source_dir --target ./image.png --best-only --table-fmt=plain --no-headers --no-notes \\
            --no-index --no-error-rate
'''


if __name__ == "__main__":
    warnings.filterwarnings("ignore", category=UserWarning)

    hidden_arg_help_message = argparse.SUPPRESS

    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter,
                                     epilog=examples, add_help=False)
    parser.add_argument('--help', '-h', action='count', default=0, help='Show help message and exit. Use it once (-h) '
                                                                        'to only see most needed arguments, twice '
                                                                        '(-hh) for detailed help with all arguments '
                                                                        'described')

    is_long_help_request = parser.parse_known_args()[0].help >= 2

    common_group = parser.add_argument_group('GLOBAL args')
    common_group.add_argument('--mode', '-m', choices=['precalculate', 'search', 'onflight'],
                              help='The mode in which you want to run ("precalculate" to create storage, "search" to '
                                   'search for images using storage, "onflight" (DEFAULT) is precalculate+search)',
                              default='onflight')
    common_group.add_argument('--storage', '-p', help='Path to a data storage (to be created or read)')

    precalculation_group = parser.add_argument_group('PRECALCULATION (or ONFLIGHT) mode arguments')
    if is_long_help_request:
        hidden_arg_help_message = 'Number of parallel processes for precalculation (DEFAULT 1)'
    precalculation_group.add_argument('--fork', '-f', help=hidden_arg_help_message, type=int, default=1)
    precalculation_group.add_argument('--dir', '-d', help='Path to the directory with images to precalculate data for')
    if is_long_help_request:
        hidden_arg_help_message = 'When calculating average colors, all images are split into SPLIT_DEPTH^2 ' \
                                  'rectangles, average color is calculated for each of them. (DEFAULT 4)'
    precalculation_group.add_argument('--split-depth', '-s', help=hidden_arg_help_message, type=int, default=4)

    search_group = parser.add_argument_group('SEARCH (or ONFLIGHT) mode arguments')
    search_group.add_argument('--target', '-t', help='Path to the target image to search similar to (note that split '
                                                     'depth is detected automatically from the storage)')
    search_group.add_argument('--suppress-extras', '-x', help='Just print absolute path to the most similar image, '
                                                              'suppress any other output. Equivalent to "--best-only '
                                                              '--no-notes --table-fmt plane --no-headers --no-index '
                                                              '--no-error-rate"',
                              default=False, action='store_true')

    ui_group = parser.add_argument_group('OUTPUT STYLE of search (or onflight) mode')
    if is_long_help_request:
        hidden_arg_help_message = 'Only print one image filename which is the best match'
    ui_group.add_argument('--best-only', '-b', help=hidden_arg_help_message, default=False, action='store_true')
    if is_long_help_request:
        hidden_arg_help_message = 'Don\'t show constant notes for user, only print the final table'
    ui_group.add_argument('--no-notes', help=hidden_arg_help_message, default=False, action='store_true')
    if is_long_help_request:
        hidden_arg_help_message = 'Table format (explained in detail in the `tabulate` library\'s docs). Use ' \
                                  '"plain" to not use any pseudo-graphics (DEFAULT "github")'
    ui_group.add_argument('--table-fmt', help=hidden_arg_help_message, type=str, default="github")
    if is_long_help_request:
        hidden_arg_help_message = 'Don\'t show headers of the final table being printed'
    ui_group.add_argument('--no-headers', help=hidden_arg_help_message, default=False, action='store_true')
    if is_long_help_request:
        hidden_arg_help_message = 'Don\'t show first column with indexes in the final table being printed'
    ui_group.add_argument('--no-index', help=hidden_arg_help_message, default=False, action='store_true')
    if is_long_help_request:
        hidden_arg_help_message = 'Don\'t show last column with error rate in the final table being printed'
    ui_group.add_argument('--no-error-rate', help=hidden_arg_help_message, default=False, action='store_true')

    args = parser.parse_args()
    if args.help:
        parser.print_help()
        exit(0)
    if args.suppress_extras:
        args.best_only = True
        args.no_notes = True
        args.table_fmt = "plain"
        args.no_headers = True
        args.no_index = True
        args.no_error_rate = True

    virtual_file = StringIO()

    # Required args checks
    if args.storage is None and args.mode != 'onflight':
        parser.error("--storage argument can only be omitted in the `onflight` mode")
    if args.mode in ('precalculate', 'onflight'):
        if args.dir is None:
            parser.error("--dir argument is required in the current mode")
    if args.mode in ('search', 'onflight'):
        if args.target is None:
            parser.error("--target argument is required in the current mode")

    # Precalculating
    if args.mode in ('precalculate', 'onflight'):
        candidates = (path.join(i[0], j) for i in walk(args.dir) for j in i[2])
        candidates = filter(lambda x: not does_raise(Image.open, (x,), expected=UnidentifiedImageError), candidates)
        precalculate(candidates, virtual_file, args.split_depth, process_count=args.fork)
        virtual_file.seek(0)

        print(colored("Precalculation's finished!", attrs=['bold', 'blink']))

    # Synchronizing files
    if args.mode in ('precalculate', 'onflight'):
        if args.storage is not None:
            with open(args.storage, "w") as f:
                f.write(virtual_file.read())
            virtual_file.seek(0)
    elif args.mode == 'search':
        with open(args.storage, "r") as f:
            virtual_file.write(f.read())
        virtual_file.seek(0)

    # Searching
    if args.mode in ('search', 'onflight'):
        if not args.no_notes:
            print("I will reprint all the images files. The lower they are in the list, the more they look like a "
                  "target\n")

        rated_images = get_sorted(args.target, virtual_file, reverse=True)
        if args.no_error_rate:
            rated_images = [(i[0],) for i in rated_images]
        if args.best_only:
            rated_images = [rated_images[-1]]

        headers = ("Path to image", "Error rate")
        if args.no_headers:
            headers = ()
        show_index = not args.no_index
        if args.no_index:
            show_index = None
        print(tabulate(rated_images, headers=headers, tablefmt=args.table_fmt, showindex=show_index))
        if not args.no_notes:
            print("\nRemember that the printed list is reversed: the lower items are, the more they look like a target")
            print("Please, also, note, that \"Error rate\" (last column) can differ a lot for different split depths. "
                  "Don't compare error rates from runs with different split depths")
