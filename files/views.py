from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST, require_GET
from django.contrib import messages
from core.models import Locality
from core.permissions import ensure_permission, Permissions
from .models import File
from .utils import upload_django_file, get_from_s3
from .transformations.base import validate_files_for_transformation
from .transformations.basic import ZipFiles
from . import tasks


@require_POST
def upload_files(request):
    locality = Locality.objects.get(pk=request.POST["locality"])

    ensure_permission(request.user, locality.state, "write")

    source_url = request.POST.get("source_url", "")
    stage = request.POST.get("stage", "S")
    cycle = request.POST.get("cycle", None)
    for file in request.FILES.getlist("files"):
        upload_django_file(
            file,
            stage=stage,
            cycle=cycle,
            locality=locality,
            created_by=request.user,
            source_url=source_url,
        )
    return redirect("locality_overview", locality.id)


@require_GET
def download_file(request, uuid):
    df = get_object_or_404(File.active_files, pk=uuid)
    fileobj = get_from_s3(df)
    return FileResponse(fileobj, as_attachment=True, filename=df.filename)


@require_POST
def download_zip(request):
    id_list = request.POST.getlist("id")
    buffer, _ = ZipFiles(id_list).do_transform()
    return FileResponse(buffer, as_attachment=True, filename="download.zip")


@require_POST
def alter_files(request):
    transformation = request.POST.get("transformation")
    alter_files = request.POST.get("alter_files")

    file_ids = request.POST.getlist("files")
    files = File.active_files.filter(pk__in=file_ids)
    assert len(file_ids) == len(files)

    # ensure permission for state
    state = files[0].cycle.state

    if transformation and alter_files:
        messages.error(request, "Cannot set transformation and file alteration.")
    elif not transformation and not alter_files:
        messages.error(request, "Must set transformation or file alteration.")
    elif transformation:
        # verify that all files have the same locality and cycle
        validate_files_for_transformation(files)
        ensure_permission(request.user, state, Permissions.ADMIN)
        transformation_func = getattr(tasks, transformation)
        transformation_func.delay(request.user.id, file_ids)
    elif alter_files:
        for f in files:
            ensure_permission(request.user, f.cycle.state, Permissions.ADMIN)
            if alter_files == "make_final":
                # can only move from intermediate to final
                if f.stage == "I":
                    f.stage = "F"
            elif alter_files == "deactivate":
                f.active = False
            f.save()

    return redirect("state_admin", state.abbreviation.lower())
