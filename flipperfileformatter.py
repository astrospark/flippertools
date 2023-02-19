import hexdump
import io
import json
import os
import zipfile


from flipperfile import FlipperFile


class FlipperFileFormatter:
    @staticmethod
    def format(flipper_file: FlipperFile):
        with io.StringIO() as output:
            flipper_file._zip_file.filename = os.path.basename(flipper_file._zip_file.filename)
            FlipperFileFormatter._format_zip_file(flipper_file._zip_file, output)
            return output.getvalue()

    @staticmethod
    def _format_binary_file(file_bytes: bytes, output):
        output.write(hexdump.hexdump(file_bytes, result='return'))
        output.write('\n\n')

    @staticmethod
    def _format_json_file(file_bytes: bytes, output):
        json_object = json.loads(file_bytes)
        output.write(json.dumps(json_object, indent=2))
        output.write('\n\n')

    @staticmethod
    def _format_xml_file(file_bytes: bytes, output):
        output.write(file_bytes.decode('utf8', 'strict'))
        output.write('\n\n')

    @staticmethod
    def _format_zip_file(zip_file: zipfile, output):
        namelist = zip_file.namelist()
        namelist.sort()
        for filename in namelist:
            FlipperFileFormatter._format_file(zip_file, filename, output)

    @staticmethod
    def _format_file(zip_file: zipfile, filename: str, output):
        file_info = zip_file.getinfo(filename)
        full_path = f'{zip_file.filename}/{filename}'
        timestamp = '{0}-{1}-{2} {3}:{4:02}:{5:02}'.format(*file_info.date_time)
        output.write(f'{full_path}\t{timestamp}\t({file_info.file_size} bytes)\n')
        FlipperFileFormatter._write_rule(output)

        file_bytes = zip_file.read(filename)
        extension = os.path.splitext(filename)[1]
        match extension:
            case '.json':
                FlipperFileFormatter._format_json_file(file_bytes, output)

            case '.sb3':
                scratch_io = io.BytesIO(file_bytes)
                scratch_file = zipfile.ZipFile(scratch_io, 'r')
                scratch_file.filename = full_path
                FlipperFileFormatter._format_zip_file(scratch_file, output)

            case '.svg':
                FlipperFileFormatter._format_xml_file(file_bytes, output)

            case _:
                FlipperFileFormatter._format_binary_file(file_bytes, output)

    @staticmethod
    def _write_rule(output, length=79):
        output.write('-' * length)
        output.write('\n')
