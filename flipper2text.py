#!/usr/bin/env python
import argparse
import contextlib
import sys
from os import PathLike
from typing import IO

from flipperfile import FlipperFile
from flipperfileformatter import FlipperFileFormatter
from pythoncodeformatter import PythonCodeFormatter
from scratchcodeformatter import ScratchCodeFormatter

_VERSION = '1.0'


def open_file_or_stdout(file: str | bytes | PathLike[str] | PathLike[bytes] | int,
                        mode: str = 'w',
                        encoding: str | None = None) -> IO:
    @contextlib.contextmanager
    def stdout_manager():
        yield sys.stdout

    if not file or file == '-':
        return stdout_manager()
    else:
        return open(file, mode, encoding=encoding)


def main():
    parser = argparse.ArgumentParser(
        description='Converts LEGO MINDSTORMS EV3 Classroom and SPIKE project files to text.',
        epilog='LEGO, MINDSTORMS, and SPIKE are trademarks of the LEGO Group. This software is not authorized or '
               'endorsed by the LEGO Group.',
        add_help=False,
    )

    options_group = parser.add_argument_group('options')
    options_group.add_argument('--help', action='help', help='show this help message and exit')
    options_group.add_argument('--version', action='version', version=f'%(prog)s {_VERSION}')

    options_group.add_argument('-d', '--dump', action='store_true', help='dump everything in the project file')
    options_group.add_argument('-f', '--force', action='store_true', help='overwrite existing file')

    options_group.add_argument('infile', type=argparse.FileType('rb'), help='the name of the project file')
    options_group.add_argument('outfile', nargs='?', default=None, help='the name of the text file to output')

    args = parser.parse_args()

    if args.force:
        write_mode = 'wt'
    else:
        write_mode = 'xt'

    with open_file_or_stdout(args.outfile, write_mode, encoding='utf-8') as outfile:
        flipper_file = FlipperFile(args.infile)

        if args.dump:
            outfile.write(FlipperFileFormatter.format(flipper_file))
        else:
            if flipper_file.type == 'python':
                outfile.write(PythonCodeFormatter.format(flipper_file.project))
            else:
                outfile.write(ScratchCodeFormatter.format(flipper_file.project))


if __name__ == '__main__':
    main()
