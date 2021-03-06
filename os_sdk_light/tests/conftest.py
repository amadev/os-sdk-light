import time
import pytest
import uuid
import os_sdk_light as osl
from bravado_core import exception

TEST_FLAVOR = "test flavor %s" % uuid.uuid4()
TEST_SERVER = "test server %s" % uuid.uuid4()
CLOUD = "devstack"
compute_client = osl.get_client(CLOUD, "compute", osl.schema("compute.yaml"))
image_client = osl.get_client(CLOUD, "image", osl.schema("image.yaml"))
network_client = osl.get_client(CLOUD, "network", osl.schema("network.yaml"))


@pytest.fixture
def server():
    flavors = compute_client.flavors.list_flavors()["flavors"]
    flavors.sort(key=lambda x: x["ram"])
    flavor = flavors[0]
    images = image_client.images.list()["images"]
    image = [i for i in images if "cirros" in i["name"]][0]
    networks = network_client.networks.list()["networks"]
    network = [i for i in networks if "private" in i["name"]][0]
    server = compute_client.servers.create_server(
        server={
            "server": {
                "name": TEST_SERVER,
                "imageRef": image["id"],
                "flavorRef": flavor["id"],
                "networks": [{"uuid": network["id"]}],
            }
        }
    )["server"]
    for i in range(20):
        server = compute_client.servers.get_server(server_id=server['id'])['server']
        if server['status'] == 'ACTIVE':
            break
        time.sleep(1)
    else:
        raise ValueError('Timeout waiting server active')
    yield server
    compute_client.servers.delete_server(server_id=server["id"])
