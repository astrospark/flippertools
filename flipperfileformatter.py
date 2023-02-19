import hexdump
import io
import json
import os
import zipfile


from flipperfile import FlipperFile


class FlipperFileFormatter:
    @staticmethod
    def format(flipper_file: FlipperFile):
        flipper_file._zip_file.filename = os.path.basename(flipper_file._zip_file.filename)
        FlipperFileFormatter.print_zip_file(flipper_file._zip_file)

    @staticmethod
    def print_binary_file(file_bytes: bytes):
        hexdump.hexdump(file_bytes)
        print()

    @staticmethod
    def print_json_file(file_bytes: bytes):
        json_object = json.loads(file_bytes)
        print(json.dumps(json_object, indent=2))
        print()

    @staticmethod
    def print_xml_file(file_bytes: bytes):
        print(file_bytes.decode('utf8', 'strict'))
        print()

    @staticmethod
    def print_zip_file(zip_file: zipfile):
        namelist = zip_file.namelist()
        namelist.sort()
        for filename in namelist:
            FlipperFileFormatter.print_file(zip_file, filename)

    @staticmethod
    def print_file(zip_file: zipfile, filename: str):
        file_info = zip_file.getinfo(filename)
        full_path = f'{zip_file.filename}/{filename}'
        timestamp = '{0}-{1}-{2} {3}:{4:02}:{5:02}'.format(*file_info.date_time)
        print(f'{full_path}\t{timestamp}\t({file_info.file_size} bytes)')
        FlipperFileFormatter.print_rule()

        file_bytes = zip_file.read(filename)
        extension = os.path.splitext(filename)[1]
        match extension:
            case '.json':
                FlipperFileFormatter.print_json_file(file_bytes)

            case '.sb3':
                scratch_io = io.BytesIO(file_bytes)
                scratch_file = zipfile.ZipFile(scratch_io, 'r')
                scratch_file.filename = full_path
                FlipperFileFormatter.print_zip_file(scratch_file)

            case '.svg':
                FlipperFileFormatter.print_xml_file(file_bytes)

            case _:
                FlipperFileFormatter.print_binary_file(file_bytes)

    @staticmethod
    def print_rule(length=79):
        print('-' * length)
