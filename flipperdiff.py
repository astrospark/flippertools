#!/usr/local/bin/python3
import argparse
import difflib
from datetime import datetime
from os import path
from sys import stdout
from tzlocal import get_localzone

from flipperfile import FlipperFile
from flipperfileformatter import FlipperFileFormatter
from pythoncodeformatter import PythonCodeFormatter
from scratchcodeformatter import ScratchCodeFormatter

_VERSION = '1.0'


def main():
    parser = argparse.ArgumentParser(
        description='Shows the differences between two LEGO MINDSTORMS EV3 Classroom or SPIKE project files.',
        epilog='LEGO, MINDSTORMS, and SPIKE are trademarks of the LEGO Group. This software is not authorized or '
               'endorsed by the LEGO Group.',
        add_help=False,
    )

    options_group = parser.add_argument_group('options')
    options_group.add_argument('--help', action='help', help='show this help message and exit')
    options_group.add_argument('--version', action='version', version=f'%(prog)s {_VERSION}')

    options_group.add_argument('-d', '--dump', action='store_true', help='compare everything in the project files')

    options_group.add_argument('file1', type=argparse.FileType('rb'), help='the name of the first file to compare')
    options_group.add_argument('file2', type=argparse.FileType('rb'), help='the name of the second file to compare')

    args = parser.parse_args()
    files = [args.file1, args.file2]
    local_timezone = get_localzone()

    flipper_files = []
    file_mtimes = []
    file_contents = []
    for file in files:
        flipper_file = FlipperFile(file)
        flipper_files.append(flipper_file)
        file_mtimes.append(datetime.fromtimestamp(path.getmtime(file.name), local_timezone).isoformat())

        if args.dump:
            file_string = FlipperFileFormatter.format(flipper_file)
        else:
            if flipper_file.type == 'python':
                file_string = PythonCodeFormatter.format(flipper_file.project)
            else:
                file_string = ScratchCodeFormatter.format(flipper_file.project)
        file_contents.append(file_string.splitlines(True))

    stdout.writelines(difflib.unified_diff(*file_contents,
                                           fromfile=files[0].name, fromfiledate=file_mtimes[0],
                                           tofile=files[1].name, tofiledate=file_mtimes[1]))


if __name__ == '__main__':
    main()
