import os
import tempfile
import mock
import pytest
import yaml
import os_sdk_light as osl


@pytest.fixture
def change_dir():
    dir = os.getcwd()
    os.chdir(os.path.dirname(__file__))
    yield
    os.chdir(dir)


def test_no_cloud_config(change_dir):
    with pytest.raises(
            osl.exceptions.CannotConnectToCloud, match='Not enough params'):
        osl.get_client(0, 0, 0)


def test_invalid_auth_params():
    f = tempfile.NamedTemporaryFile(mode='w')
    data = yaml.load(open('clouds.yaml'))
    data['clouds']['devstack']['auth']['password'] = 'fake'
    yaml.dump(data, f)
    with pytest.raises(
            osl.exceptions.CannotConnectToCloud,
            match='Authentication failed'):
        osl.get_client('devstack', 0, 0, config={'config_files': [f.name]})


def test_incorrect_auth_schema():
    f = tempfile.NamedTemporaryFile(mode='w')
    data = yaml.load(open('clouds.yaml'))
    del data['clouds']['devstack']['auth']['password']
    yaml.dump(data, f)
    with pytest.raises(
            osl.exceptions.CannotConnectToCloud,
            match='Authentication failed'):
        osl.get_client('devstack', 0, 0, config={'config_files': [f.name]})


def test_empty_auth_schema():
    f = tempfile.NamedTemporaryFile(mode='w')
    data = yaml.load(open('clouds.yaml'))
    del data['clouds']['devstack']['auth']['password']
    del data['clouds']['devstack']['auth']['username']
    yaml.dump(data, f)
    with pytest.raises(
            osl.exceptions.CannotConnectToCloud,
            match='Authentication failed'):
        osl.get_client('devstack', 0, 0, config={'config_files': [f.name]})


def test_get_endpoint_failed():
    with pytest.raises(
            osl.exceptions.CannotConnectToCloud,
            match='Failed to find service endpoint'):
        osl.get_client('devstack', 0, 0)


def test_incorrect_schema():
    f = tempfile.NamedTemporaryFile()
    with pytest.raises(
            osl.exceptions.SchemaError,
            match='cannot be read or invalid'):
        osl.get_client('devstack', 'compute', f.name)


def test_request_not_match_schema():
    compute = osl.get_client('devstack', 'compute', osl.schema('compute.yaml'))
    with pytest.raises(
            osl.exceptions.ValidationError,
            match='required parameter'):
        compute.flavors.create_flavor()
    with pytest.raises(
            osl.exceptions.ValidationError,
            match='required property'):
        compute.flavors.create_flavor(flavor={'flavor': {'name': 'test'}})


def test_response_not_match_schema():
    compute = osl.get_client('devstack', 'compute', osl.schema('compute.yaml'))
    with mock.patch(
            'bravado.requests_client.RequestsResponseAdapter') as resp_class:
        resp = mock.MagicMock()
        resp.status_code = 200
        resp.json.return_value = {}
        resp_class.return_value = resp
        with pytest.raises(
                osl.exceptions.ValidationError,
                match='required property'):
            compute.flavors.get_flavor(flavor_id='fake')


def test_not_defined_response():
    compute = osl.get_client('devstack', 'compute', osl.schema('compute.yaml'))
    with mock.patch(
            'bravado.requests_client.RequestsResponseAdapter') as resp_class:
        resp = mock.MagicMock()
        resp.status_code = 404
        resp.json.return_value = {}
        resp_class.return_value = resp
        try:
            compute.flavors.get_flavor(flavor_id='fake')
            pytest.fail('Exception must be thrown')
        except osl.exceptions.UnexpectedResponse as e:
            assert resp.status_code == e.status_code


def test_microversion_in_header():
    p = osl.get_client('devstack', 'placement', osl.schema('placement.yaml'))
    p.traits.get_traits()
