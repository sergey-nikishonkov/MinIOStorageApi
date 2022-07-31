"""
This module provides tools for working with MinIo
"""
import base64
import json
from datetime import date
from urllib3.exceptions import MaxRetryError
from minio import Minio
from fastapi import UploadFile
from fastapi.exceptions import HTTPException
from sql_app.models import Image

_client = Minio(
    "localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False,
)


def uploader(files: list[UploadFile]) -> bool:
    """
    Automatically create bucket with current date in minio and put given images
    """

    today = date.today().strftime('%Y%m%d')

    try:
        if not _client.bucket_exists(today):
            _client.make_bucket(today)

        for file in files:
            _client.put_object(
                bucket_name=today,
                object_name=file.filename,
                data=file.file,
                length=-1,
                part_size=10 * 1024 * 1024,
                content_type='image/jpeg',
            )

    except MaxRetryError as max_retry:
        raise HTTPException(503, detail='MinIO unavailable') from max_retry
    return True


def getter(files: list[Image]) -> json:

    """Serialize image file to json format"""

    data = []
    for file in files:
        bucket = file.date_register.date().strftime('%Y%m%d')
        try:
            response = _client.get_object(bucket, file.title)
        except MaxRetryError as max_retry:
            raise HTTPException(503, detail='MinIO unavailable') from max_retry

        try:
            title = file.title
            date_register = file.date_register.isoformat()
            data.append({'title': title, 'date': date_register, 'file': response.data})
        finally:
            response.close()
            response.release_conn()
    return json.dumps(data)


def deleter(files: list[Image]) -> bool:
    """Delete given files """
    try:
        for file in files:
            bucket = file.date_register.date().strftime('%Y%m%d')
            _client.remove_object(bucket, file.title)
    except MaxRetryError as max_retry:
        raise HTTPException(503, detail='MinIO unavailable') from max_retry
    return True
