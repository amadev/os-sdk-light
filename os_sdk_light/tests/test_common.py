import os
import pytest
import os_sdk_light as osl
import tempfile
import yaml


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
    f = tempfile.NamedTemporaryFile()
    data = yaml.load(open('clouds.yaml'))
    data['clouds']['devstack']['auth']['password'] = 'fake'
    yaml.dump(data, f)
    with pytest.raises(
            osl.exceptions.CannotConnectToCloud,
            match='Authentication failed'):
        osl.get_client('devstack', 0, 0, config={'config_files': [f.name]})


def test_incorrect_auth_schema():
    f = tempfile.NamedTemporaryFile()
    data = yaml.load(open('clouds.yaml'))
    del data['clouds']['devstack']['auth']['password']
    yaml.dump(data, f)
    with pytest.raises(
            osl.exceptions.CannotConnectToCloud,
            match='Authentication failed'):
        osl.get_client('devstack', 0, 0, config={'config_files': [f.name]})


def test_empty_auth_schema():
    f = tempfile.NamedTemporaryFile()
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
