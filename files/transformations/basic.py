import io
import os
import shutil
import zipfile
import tempfile
import subprocess
from ..utils import get_from_s3
from .exceptions import CommandError


class TransformationCommand:
    def __init__(self, *files):
        self.files = files
        self.tmpdir = None
        self.input_filenames = []

    def reconstitute_files(self):
        """
        populate self.tmpdir with all the files that were sent to the transformation
        also populates input_filenames with fully-resolved versions of these filenames
        """
        self.tmpdir = tempfile.mkdtemp()
        for file in self.files:
            fn = os.path.join(self.tmpdir, file.source_filename)
            with open(fn, "wb") as f:
                f.write(get_from_s3(file).read())
            self.input_filenames.append(fn)

    def file_path(self, path):
        """
        resolve a file path within the working directory
        """
        return os.path.join(self.tmpdir, path)

    def cleanup(self):
        """
        remove everything in the working directory, called at the very end of run
        """
        if self.tmpdir:
            shutil.rmtree(self.tmpdir)

    def run(self):
        """
        fully-functional run method that works as long as get_command returns a command
        that generates output and saves it at output_filename
        """
        self.reconstitute_files()

        cp = subprocess.run(self.get_command(), capture_output=True, text=True)
        if cp.returncode != 0:
            command = " ".join(cp.args)
            raise CommandError(f"'{command}' returned {cp.returncode}: {cp.stderr}")

        data = self.get_result_data()

        self.cleanup()
        return data, self.mime_type

    def get_result_data(self):
        """ pull data from output_filename """
        with open(self.file_path(self.output_filename)) as f:
            return f.read()

    def get_command(self):
        """ should return a command to run in list format """
        raise NotImplementedError


class ZipFiles(TransformationCommand):
    def run(self):
        buffer = io.BytesIO()
        zf = zipfile.ZipFile(buffer, "w")
        for file in self.files:
            fileobj = get_from_s3(file)
            zf.writestr(str(file.id) + file.source_filename, fileobj.read())
        zf.close()
        buffer.seek(0)
        return buffer, "application/zip"


class ToGeoJSON(TransformationCommand):
    mime_type = "application/vnd.geo+json"
    output_filename = "output.json"

    def get_command(self):
        return [
            "ogr2ogr",
            "-f",
            "GeoJSON",
            self.file_path(self.output_filename),
            self.file_path(self.input_filenames[0]),
        ]


class GeojsonToMbtile(TransformationCommand):
    mime_type = "application/vnd.mapbox-vector-tile"
    output_filename = "output.mbtiles"

    # TODO: add validation of inputs

    def get_command(self):
        return [
            "tippecanoe",
            "-o",
            self.file_path(self.output_filename),
            "-z14",
            "--drop-densest-as-needed",
            "--generate-ids",
            self.input_filenames[0],
        ]
