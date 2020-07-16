#!/usr/bin/python3
from sys import argv, stderr
from os import listdir, path
import json
import argparse
from multiprocessing import Pool
import warnings

import numpy as np
from PIL import Image
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


def get_avged_imgs_dist(a, b):
    return np.sum(abs(a - b))


def precalculate_part(args):
    candidate_paths = args[0]
    split_depth = args[1]
    tqdm_position = args[2]

    return {candidate_path: get_avg_pixels(Image.open(candidate_path).convert("RGB"), split_depth).tolist()
            for candidate_path in tqdm(candidate_paths, position=tqdm_position)}

def precalculate(candidate_paths, output_path, /, split_depth=2, process_count=1):
    data = {}

    idxs_and_chunks = enumerate(chunkify(candidate_paths, process_count))
    args = map(lambda x: (x[1], split_depth, x[0]), idxs_and_chunks)

    with Pool(process_count) as pool:
        for data_part in pool.imap_unordered(precalculate_part, args):
            data = {**data, **data_part}

    with open(output_path, "w") as f:
        json.dump({'split_depth': split_depth, 'data': data}, f)


def get_sorted(target_path, storage_path, reverse=False):
    with open(storage_path, "r") as f:
        precalculated = json.load(f)

    split_depth = precalculated['split_depth']
    precalculated_avgs = {k: np.asarray(v) for k, v in precalculated['data'].items()}
    
    target = Image.open(target_path)
    target_avg = get_avg_pixels(target, split_depth)

    return sorted(list(precalculated_avgs.keys()),
            key=lambda k: get_avged_imgs_dist(target_avg, precalculated_avgs[k]), reverse=reverse)


description = '''Sorts an array of images by color similarity to a given image.\n\n
Imagine you are given a directory with a HUGE amount of images inside and something like a screenshot of one of them.\n
This script allows you to find an image (in fact images) visually nearest to a given (target) image.\n
It also allows to quickly search for images, similar to different targets, if you are searching in the same folder.\n\n
Abstract usage:
    1. Precalculate data for an images set (multiprocessing is out of the box)
    2. Search for images similar to target
'''

examples = f'''Examples:
    {argv[0]} precalculate --storage dir1_storage.json --dir ./dir1
    {argv[0]} search --storage dir1_storage.json --target img1.png
'''


if __name__ == "__main__":
    # The following class is from https://stackoverflow.com/a/26986546/11248508
    class ArgparseFormatter(argparse.RawTextHelpFormatter):
        # use defined argument order to display usage
        def _format_usage(self, usage, actions, groups, prefix):
            if prefix is None:
                prefix = 'usage: '

            # if usage is specified, use that
            if usage is not None:
                usage = usage % dict(prog=self._prog)

            # if no optionals or positionals are available, usage is just prog
            elif not actions:
                usage = '%(prog)s' % dict(prog=self._prog)
            elif usage is None:
                prog = '%(prog)s' % dict(prog=self._prog)
                # build full usage string
                action_usage = self._format_actions_usage(actions, groups) # NEW
                usage = ' '.join([s for s in [prog, action_usage] if s])
                # omit the long line wrapping code
            # prefix with 'usage:'
            return '%s%s\n\n' % (prefix, usage)


    warnings.filterwarnings("ignore", category=UserWarning)


    parser = argparse.ArgumentParser(description=description, formatter_class=ArgparseFormatter, epilog=examples)
    parser.add_argument('mode', choices=['precalculate', 'search'], help='The mode in which you want to run')

    parser.add_argument('--storage', '-p', help='Path to the precalculated data storage', required=True)

    precalculation_group = parser.add_argument_group('Precalculation mode')
    precalculation_group.add_argument('--fork', '-f', help='Number of parallel processes for precalculation '
        '(default 1)', type=int, default=1)
    precalculation_group.add_argument('--dir', '-d', help='Path to the direcotory with images to precalculate data for')
    precalculation_group.add_argument('--split-depth', '-s', help='When calculating average colors, all images '
        'are split into SPLIT_DEPTH**2 rectangles, average color is calculated for each of them. (default 4)', type=int,
        default=4)

    search_group = parser.add_argument_group('Search mode')
    search_group.add_argument('--target', '-t', help='Path to the target image to search similar to (note that split '
            'depth is detected automatically from the storage)')

    args = parser.parse_args()
    if args.mode == 'precalculate':
        if args.dir is None:
            parser.error("--dir argument is required in precalculation mode")

        precalculate((path.join(args.dir, i) for i in listdir(args.dir)), args.storage, args.split_depth,
                process_count=args.fork)

        print(colored('Done!', attrs=['bold', 'blink']))
    elif args.mode == 'search':
        if args.target is None:
            parser.error("--target argument is required in search mode")
        print("I will reprint all the imags files. The lower they are in the list, the more they look like a target\n")
        print('\n'.join(get_sorted(args.target, args.storage, reverse=True)))
        print("\nRemember that the printed list is reversed: the lower items are, the more they look like a target")
