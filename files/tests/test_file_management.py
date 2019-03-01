from io import StringIO
import pytest
from moto import mock_s3
import boto3
from django.contrib.auth.models import User
from django.conf import settings
from core.models import Locality
from files.models import File


@pytest.fixture
def user():
    return User.objects.create(username="testuser")


@pytest.fixture
def s3():
    with mock_s3():
        s3 = boto3.resource('s3', region_name='us-east-1')
        s3.create_bucket(Bucket=settings.RAW_FILE_S3_BUCKET)
        # yield to keep context manager active
        yield s3


@pytest.mark.django_db
def test_upload_files(client, user, s3):
    locality = Locality.objects.get(name='Wake County', state_id='NC')
    user.groups.create(name="NC write")
    client.force_login(user)
    faux_file = StringIO("file contents")
    faux_file.name = "fake.txt"
    resp = client.post("/files/upload/",
                       {"locality": locality.id,
                        "files": [faux_file],
                        })

    # ensure redirect to state page
    assert resp.status_code == 302
    assert resp.url == f"/locality/{locality.id}/"

    # ensure the file was created
    f = File.objects.all().get()
    assert f.stage == "S"
    assert f.size == 13
    assert f.locality == locality
    assert f.source_filename == "fake.txt"
    assert f.created_by == user

    # check s3 for the file
    body = s3.Object(settings.RAW_FILE_S3_BUCKET, f.s3_path).get()['Body'].read().decode("utf-8")
    assert body == "file contents"


@pytest.mark.django_db
def test_upload_files_unauthorized(client, user, s3):
    client.force_login(user)
    faux_file = StringIO("file contents")
    faux_file.name = "fake.txt"
    resp = client.post("/files/upload/",
                       {"locality": 1,
                        "files": [faux_file],
                        })
    # user isn't in NC write group
    assert resp.status_code == 403


@pytest.mark.django_db
def test_download(client, user, s3):
    locality = Locality.objects.get(name='Wake County', state_id='NC')
    user.groups.create(name="NC write")
    client.force_login(user)
    faux_file = StringIO("file contents")
    faux_file.name = "fake.txt"
    resp = client.post("/files/upload/",
                       {"locality": locality.id,
                        "files": [faux_file],
                        })

    assert resp.status_code == 302
    f = File.objects.all().get()
    resp = client.get(f"/files/download/{f.id}/")
    assert resp.status_code == 200
    assert resp.get('Content-Disposition') == 'attachment; filename="fake.txt"'
