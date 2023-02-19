import io
import json
import zipfile
from typing import IO
from os import PathLike


class FlipperFile:
    def __init__(self, file: str | PathLike[str] | IO[bytes]):
        self._zip_file = zipfile.ZipFile(file)
        self._icon_svg = None
        self._manifest = None
        self._scratch_file = None
        self._project = None

    def _read(self, name: str) -> bytes:
        return self._zip_file.read(name)

    @property
    def type(self):
        return self.manifest['type']

    @property
    def icon_svg(self):
        if self._icon_svg is None:
            self._icon_svg = self._read('icon.svg')
        return self._icon_svg

    @property
    def manifest(self):
        if self._manifest is None:
            json_bytes = self._read('manifest.json')
            self._manifest = json.loads(json_bytes)
        return self._manifest

    @property
    def scratch_file(self):
        if self.type != 'python' and self._scratch_file is None:
            file_bytes = self._read('scratch.sb3')
            scratch_io = io.BytesIO(file_bytes)
            self._scratch_file = zipfile.ZipFile(scratch_io, 'r')
        return self._scratch_file

    @property
    def project(self):
        if self._project is None:
            if self.type == 'python':
                json_bytes = self._read('projectbody.json')
            else:
                json_bytes = self.scratch_file.read('project.json')
            self._project = json.loads(json_bytes)
        return self._project
