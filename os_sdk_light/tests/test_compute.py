from os_sdk_light import get_client


compute_client = get_client('devstack', 'compute', 'compute.yaml')


def test_list_flavors():
    for flavor in compute_client.flavors.list().response().result['flavors']:
        assert 'id' in flavor
        assert 'name' in flavor
