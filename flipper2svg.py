#!/usr/local/bin/python3
import argparse
import os

from flipperfile import FlipperFile

_VERSION = '1.0'


def main():
    parser = argparse.ArgumentParser(
        description='Converts LEGO MINDSTORMS EV3 Classroom and SPIKE project files to SVG.',
        epilog='LEGO, MINDSTORMS, and SPIKE are trademarks of the LEGO Group. This software is not authorized or '
               'endorsed by the LEGO Group.',
        add_help=False,
    )

    options_group = parser.add_argument_group('options')
    options_group.add_argument('--help', action='help', help='show this help message and exit')
    options_group.add_argument('--version', action='version', version=f'%(prog)s {_VERSION}')

    options_group.add_argument('-f', '--force', action='store_true', help='overwrite existing file')

    options_group.add_argument('infile', type=argparse.FileType('rb'), help='the name of the project file')
    options_group.add_argument('outfile', nargs='?', help='the name of the SVG file to output')

    args = parser.parse_args()

    if args.force:
        write_mode = 'wb'
    else:
        write_mode = 'xb'

    if args.outfile is None:
        args.outfile = os.path.splitext(args.infile.name)[0] + '.svg'

    with open(args.outfile, write_mode) as outfile:
        flipper_file = FlipperFile(args.infile)
        outfile.write(flipper_file.icon_svg)


if __name__ == '__main__':
    main()
