from fastapi.testclient import TestClient
from app import app


client = TestClient(app)


def test_get_image():
    response = client.get('/frames/?request_code=1')
    assert response.status_code == 200


def test_get_non_existent_image():
    response = client.get('/frames/?request_code=500')
    assert response.status_code == 404


def test_save_image():
    response = client.post('/frames/', files={"file": ("filename", open('test_files/test_img.jpg', "rb"), "image/jpeg")})
    response.status_code == 201


def test_save_image_wrong_format():
    response = client.post('/frames/', files={"file": ("filename", open('test_files/Test_Python.docx', "rb"), "image/jpeg")})
    response.status_code == 422


def test_delete_image():
    response = client.delete('/frames/?request_code=2')
    response.status_code == 200


def test_delete_non_existent_image():
    response = client.delete('/frames/?request_code=1000')
    response.status_code == 422