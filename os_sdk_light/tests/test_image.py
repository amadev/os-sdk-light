import pytest
import uuid
import os_sdk_light as osl
from bravado_core import exception

CLOUD = "devstack"
c = osl.get_client(cloud=CLOUD, service="image", schema=osl.schema("image.yaml"))


def test_image():
    image = c.images.create_image(image={'name': 'myubuntu'})
    image = c.images.get_image(image_id=image['id'])
    # update = [{"op": "replace", "path": "/name", "value": image["id"]}]
    # image = c.images.update_image(image_id=image['id'], image=update)
    c.images.delete_image(image_id=image['id'])
