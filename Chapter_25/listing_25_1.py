'''Read a MySQL 8 file-per-table tablespace file and generate an
SVG formatted map of the LSN age of each page.

Invoke with the --help argument to see a list of arguments and
Usage instructions.'''

import sys
import argparse
import math
from struct import unpack

# Some constants from InnoDB
FIL_PAGE_OFFSET = 4          # Offset for the page number
FIL_PAGE_LSN = 16            # Offset for the LSN
FIL_PAGE_TYPE = 24           # Offset for the page type
FIL_PAGE_TYPE_ALLOCATED = 0  # Freshly allocated page


def mach_read_from_2(page, offset):
    '''Read 2 bytes in big endian. Based on the function of the same
    name in the InnoDB source code.'''
    return unpack('>H', page[offset:offset + 2])[0]


def mach_read_from_4(page, offset):
    '''Read 4 bytes in big endian. Based on the function of the same
    name in the InnoDB source code.'''
    return unpack('>L', page[offset:offset + 4])[0]


def mach_read_from_8(page, offset):
    '''Read 8 bytes in big endian. Based on the function of the same
    name in the InnoDB source code.'''
    return unpack('>Q', page[offset:offset + 8])[0]


def get_color(lsn, delta_lsn, greyscale):
    '''Get the RGB color of a relative lsn.'''
    color_fmt = '#{0:02x}{1:02x}{2:02x}'

    if greyscale:
        value = int(255 * lsn / delta_lsn)
        color = color_fmt.format(value, value, value)
    else:
        # 0000FF -> 00FF00 -> FF0000 -> FFFF00
        # 256 + 256 + 256 values
        value = int((3 * 256 - 1) * lsn / delta_lsn)
        if value < 256:
            color = color_fmt.format(0, value, 255 - value)
        elif value < 512:
            value = value % 256
            color = color_fmt.format(value, 255 - value, 0)
        else:
            value = value % 256
            color = color_fmt.format(255, value, 0)

    return color


def gen_svg(min_lsn, max_lsn, lsn_age, args):
    '''Generate an SVG output and print to stdout.'''
    pages_per_row = args.width
    page_width = args.size
    num_pages = len(lsn_age)
    num_rows = int(math.ceil(1.0 * num_pages / pages_per_row))
    x1_label = 5 * page_width + 1
    x2_label = (pages_per_row + 7) * page_width
    delta_lsn = max_lsn - min_lsn

    print('<?xml version="1.0"?>')
    print('<svg xmlns="http://www.w3.org/2000/svg" version="1.1">')
    print('<text x="{0}" y="{1}" font-family="monospace" font-size="{2}" '
          .format(x1_label, int(1.5 * page_width) + 1, page_width) +
          'font-weight="bold" text-anchor="end">Page</text>')

    page_number = 0
    page_fmt = '  <rect x="{0}" y="{1}" width="{2}" height="{2}" fill="{3}" />'
    label_fmt = '  <text x="{0}" y="{1}" font-family="monospace" '
    label_fmt += 'font-size="{2}" text-anchor="{3}">{4}</text>'
    for i in range(num_rows):
        y = (i + 2) * page_width
        for j in range(pages_per_row):
            x = 6 * page_width + j * page_width
            if page_number >= len(lsn_age) or lsn_age[page_number] is None:
                color = 'black'
            else:
                relative_lsn = lsn_age[page_number] - min_lsn
                color = get_color(relative_lsn, delta_lsn, args.greyscale)

            print(page_fmt.format(x, y, page_width, color))
            page_number += 1

        y_label = y + page_width
        label1 = i * pages_per_row
        label2 = (i + 1) * pages_per_row
        print(label_fmt.format(x1_label, y_label, page_width, 'end', label1))
        print(label_fmt.format(x2_label, y_label, page_width, 'start', label2))

    # Create a frame around the pages
    frame_fmt = '  <path stroke="black" stroke-width="1" fill="none" d="'
    frame_fmt += 'M{0},{1} L{2},{1} S{3},{1} {3},{4} L{3},{5} S{3},{6} {2},{6}'
    frame_fmt += ' L{0},{6} S{7},{6} {7},{5} L{7},{4} S{7},{1} {0},{1} Z" />'
    x1 = int(page_width * 6.5)
    y1 = int(page_width * 1.5)
    x2 = int(page_width * 5.5) + page_width * pages_per_row
    x2b = x2 + page_width
    y1b = y1 + page_width
    y2 = int(page_width * (1.5 + num_rows))
    y2b = y2 + page_width
    x1c = x1 - page_width
    print(frame_fmt.format(x1, y1, x2, x2b, y1b, y2, y2b, x1c))

    # Create legend
    x_left = 6 * page_width
    x_right = x_left + pages_per_row * page_width
    x_mid = x_left + int((x_right - x_left) * 0.5)
    y = y2b + 2 * page_width
    print('<text x="{0}" y="{1}" font-family="monospace" '.format(x_left, y) +
          'font-size="{0}" text-anchor="start">{1}</text>'.format(page_width,
                                                                  min_lsn))
    print('<text x="{0}" y="{1}" font-family="monospace" '.format(x_right, y) +
          'font-size="{0}" text-anchor="end">{1}</text>'.format(page_width,
                                                                max_lsn))
    print('<text x="{0}" y="{1}" font-family="monospace" '.format(x_mid, y) +
          'font-size="{0}" font-weight="bold" text-anchor="middle">{1}</text>'
          .format(page_width, 'LSN Age'))

    color_width = 1
    color_steps = page_width * pages_per_row
    y = y + int(page_width * 0.5)
    for i in range(color_steps):
        x = 6 * page_width + i * color_width
        color = get_color(i, color_steps, args.greyscale)
        print('<rect x="{0}" y="{1}" width="{2}" height="{3}" fill="{4}" />'
              .format(x, y, color_width, page_width, color))

    print('</svg>')


def analyze_lsn_age(args):
    '''Read the tablespace file and find the LSN for each page.'''
    page_size_bytes = int(args.page_size[0:-1]) * 1024
    min_lsn = None
    max_lsn = None
    lsn_age = []
    with open(args.tablespace, 'rb') as fs:
        # Read at most 1000 pages at a time to avoid storing too much
        # in memory at a time.
        chunk = fs.read(1000 * page_size_bytes)
        while len(chunk) > 0:
            num_pages = int(math.floor(len(chunk) / page_size_bytes))
            for i in range(num_pages):
                # offset is the start of the page inside the
                # chunk of data
                offset = i * page_size_bytes
                # The page number, lsn for the page, and page
                # type can be found at the FIL_PAGE_OFFSET,
                # FIL_PAGE_LSN, and FIL_PAGE_TYPE offsets
                # relative to the start of the page.
                page_number = mach_read_from_4(chunk, offset + FIL_PAGE_OFFSET)
                page_lsn = mach_read_from_8(chunk, offset + FIL_PAGE_LSN)
                page_type = mach_read_from_2(chunk, offset + FIL_PAGE_TYPE)

                if page_type == FIL_PAGE_TYPE_ALLOCATED:
                    # The page has not been used yet
                    continue

                if min_lsn is None:
                    min_lsn = page_lsn
                    max_lsn = page_lsn
                else:
                    min_lsn = min(min_lsn, page_lsn)
                    max_lsn = max(max_lsn, page_lsn)

                if page_number == len(lsn_age):
                    lsn_age.append(page_lsn)
                elif page_number > len(lsn_age):
                    # The page number is out of order - expand the list first
                    lsn_age += [None] * (page_number - len(lsn_age))
                    lsn_age.append(page_lsn)
                else:
                    lsn_age[page_number] = page_lsn

            chunk = fs.read(1000 * page_size_bytes)

    sys.stderr.write("Total # Pages ...: {0}\n".format(len(lsn_age)))
    gen_svg(min_lsn, max_lsn, lsn_age, args)


def main():
    '''Parse the arguments and call the analyze_lsn_age()
    function to perform the analysis.'''
    parser = argparse.ArgumentParser(
        prog='listing_25_1.py',
        description='Generate an SVG map with the LSN age for each page in an' +
        ' InnoDB tablespace file. The SVG is printed to stdout.')

    parser.add_argument(
        '-g', '--grey', '--greyscale', default=False,
        dest='greyscale', action='store_true',
        help='Print the LSN age map in greyscale.')

    parser.add_argument(
        '-p', '--page_size', '--page-size', default='16k',
        dest='page_size',
        choices=['4k', '8k', '16k', '32k', '64k'],
        help='The InnoDB page size. Defaults to 16k.')

    parser.add_argument(
        '-s', '--size', default=16, dest='size',
        choices=[4, 8, 12, 16, 20, 24], type=int,
        help='The size of the square representing a page in the output. ' +
        'Defaults to 16.')

    parser.add_argument(
        '-w', '--width', default=64, dest='width',
        type=int,
        help='The number of pages to include per row in the output. ' +
        'The default is 64.')

    parser.add_argument(
        dest='tablespace',
        help='The tablespace file to analyze.')

    args = parser.parse_args()
    analyze_lsn_age(args)


if __name__ == '__main__':
    main()
