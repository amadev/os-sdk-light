import pytest
import uuid
import os_sdk_light as osl
from bravado_core import exception


TEST_FLAVOR = 'test flavor %s' % uuid.uuid4()
TEST_SERVER = 'test server %s' % uuid.uuid4()
CLOUD = 'devstack'
compute_client = osl.get_client(
    CLOUD, 'compute', osl.schema('compute.yaml'))
image_client = osl.get_client(
    CLOUD, 'image', osl.schema('image.yaml'))
network_client = osl.get_client(
    CLOUD, 'network', osl.schema('network.yaml'))


def test_list_flavors():
    for flavor in compute_client.flavors.list_flavors().response().result[
            'flavors']:
        assert 'id' in flavor
        assert 'name' in flavor


def test_create_flavor():
    pytest.raises(exception.SwaggerMappingError,
                  lambda: compute_client.flavors.
                  create_flavor().response().result)
    flavor = compute_client.flavors.create_flavor(
        flavor={'flavor': {'name': TEST_FLAVOR,
                           'ram': 16384,
                           'disk': 1,
                           'vcpus': 2}}).response().result['flavor']
    new_flavor = compute_client.flavors.get_flavor(
        flavor_id=flavor['id']).response().result['flavor']
    assert flavor['name'] == new_flavor['name']
    compute_client.flavors.delete_flavor(flavor_id=flavor['id']).response()


def test_server():
    flavors = compute_client.flavors.list_flavors().response().result[
        'flavors']
    flavors.sort(key=lambda x: x['ram'])
    flavor = flavors[0]
    images = image_client.images.list().response().result['images']
    image = [i for i in images if 'cirros' in i['name']][0]
    networks = network_client.networks.list().response().result['networks']
    network = [i for i in networks if 'private' in i['name']][0]
    server = compute_client.servers.create_server(
        server={'server': {'name': TEST_SERVER,
                           'imageRef': image['id'],
                           'flavorRef': flavor['id'],
                           'networks': [{'uuid': network['id']}]}}
    ).response().result['server']
    compute_client.servers.delete_server(server_id=server['id']).response()
