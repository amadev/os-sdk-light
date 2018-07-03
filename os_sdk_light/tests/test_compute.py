import pytest
import uuid
import os_sdk_light as osl
from bravado_core import exception


TEST_FLAVOR = 'test flavor %s' % uuid.uuid4()
compute_client = osl.get_client(
    'devstack', 'compute', osl.schema('compute.yaml'))


def test_list_flavors():
    for flavor in compute_client.flavors.list().response().result['flavors']:
        assert 'id' in flavor
        assert 'name' in flavor


def test_create_flavor():
    pytest.raises(exception.SwaggerMappingError,
                  lambda: compute_client.flavors.create().response().result)
    flavor = compute_client.flavors.create(
        flavor={'flavor': {'name': TEST_FLAVOR,
                           'ram': 16384,
                           'disk': 1,
                           'vcpus': 2}}).response().result['flavor']
    new_flavor = compute_client.flavors.get(
        flavor_id=flavor['id']).response().result['flavor']
    assert flavor['name'] == new_flavor['name']
    compute_client.flavors.delete(flavor_id=flavor['id']).response()
