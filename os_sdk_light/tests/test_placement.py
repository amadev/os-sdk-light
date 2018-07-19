import pytest
import uuid
import os_sdk_light as osl
from bravado_core import exception


TEST_RP = 'test resource provider %s' % uuid.uuid4()
CLOUD = 'devstack'
placement_client = osl.get_client(
    CLOUD, 'placement', osl.schema('placement.yaml'))


def test_rps():
    orig_rp = {'name': TEST_RP}
    placement_client.resource_providers.create_resource_provider(
        body=orig_rp
    )
    rp = placement_client.resource_providers.list_resource_providers(
        name=orig_rp['name']
    )['resource_providers'][0]
    rp1 = placement_client.resource_providers.get_resource_provider(
        resource_provider_id=rp['uuid'])
    assert rp['name'] == rp1['name']
    placement_client.resource_providers.delete_resource_provider(
        resource_provider_id=rp['uuid'])
