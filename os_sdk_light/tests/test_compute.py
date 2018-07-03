import os_sdk_light as osl


compute_client = osl.get_client(
    'devstack', 'compute', osl.schema('compute.yaml'))


def test_list_flavors():
    for flavor in compute_client.flavors.list().response().result['flavors']:
        assert 'id' in flavor
        assert 'name' in flavor
