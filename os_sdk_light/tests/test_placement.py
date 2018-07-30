import pytest
import uuid
import os_sdk_light as osl
from bravado_core import exception


TEST_RP = 'test resource provider %s' % uuid.uuid4()
CLOUD = 'devstack'
placement_client = osl.get_client(
    CLOUD, 'placement', osl.schema('placement.yaml'))


@pytest.fixture
def rp():
    orig_rp = {'name': TEST_RP}
    placement_client.resource_providers.create_resource_provider(
        body=orig_rp
    )
    rp = placement_client.resource_providers.list_resource_providers(
        name=orig_rp['name']
    )['resource_providers'][0]
    yield rp
    placement_client.resource_providers.delete_resource_provider(
        uuid=rp['uuid'])


def test_rps(rp):
    rp1 = placement_client.resource_providers.get_resource_provider(
        uuid=rp['uuid'])
    assert rp['name'] == rp1['name']


def test_inventories(rp):
    placement_client.resource_providers.put_inventories(
        uuid=rp['uuid'],
        body={
            'resource_provider_generation': rp['generation'],
            'inventories': {'MEMORY_MB': {'total': 512}}}
    )
    invs = placement_client.resource_providers.get_inventories(
        uuid=rp['uuid']
    )
    placement_client.resource_providers.put_inventories(
        uuid=rp['uuid'],
        body={
            'resource_provider_generation': invs[
                'resource_provider_generation'],
            'inventories': {}}
    )
