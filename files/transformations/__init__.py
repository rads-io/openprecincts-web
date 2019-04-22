import pytz
import datetime
from django.db import transaction
from . import basic
from ..models import Transformations
from ..utils import upload_file


TRANSFORMATION_CLASSES = {
    Transformations.ZIP: basic.ZipFiles,
    Transformations.TO_GEOJSON: basic.ToGeoJSON,
}


def validate_files_for_transformation(files):
    localities = set()
    cycles = set()
    for f in files:
        localities.add(f.locality_id)
        cycles.add(f.cycle_id)
    if len(localities) != 1:
        raise ValueError("files must all be from the same locality")
    if len(cycles) != 1:
        raise ValueError("files must all be from the same cycle")


def run_transformation(transformation):
    TClass = TRANSFORMATION_CLASSES[transformation.transformation]
    files = list(transformation.input_files.all())

    # ensure locality & cycle are the same
    try:
        validate_files_for_transformation(files)
    except ValueError as e:
        transformation.error = str(e)

    if not transformation.error:
        try:
            output_bytes, mime_type = TClass(*files).run()
        except Exception as e:
            transformation.error = str(e)

    with transaction.atomic():
        transformation.finished_at = pytz.utc.localize(datetime.datetime.utcnow())
        transformation.save()

        if transformation.error:
            return None

        return upload_file(
            stage="I",
            locality=files[0].locality,
            mime_type=mime_type,
            size=len(output_bytes.getvalue()),
            created_by=transformation.created_by,
            cycle=files[0].cycle,
            file_obj=output_bytes,
            from_transformation=transformation,
        )