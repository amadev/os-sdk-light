import os
import logging
import yaml

import os_client_config
from bravado.client import SwaggerClient
from bravado.requests_client import RequestsClient
from six.moves.urllib import parse as urlparse


log = logging.getLogger(__name__)
SCHEMAS = os.path.dirname(
    os.path.dirname(os.path.realpath(__file__))) + '/schemas/'


def schema(name):
    return SCHEMAS + name


def get_client(cloud, service, schema):
    config = os_client_config.OpenStackConfig()
    cloud = config.get_one_cloud(cloud)
    adapter = cloud.get_session_client(service)
    access_info = adapter.session.auth.get_access(adapter.session)
    endpoints = access_info.service_catalog.get_endpoints()
    http_client = RequestsClient()
    endpoint = [e for e in endpoints[service] if e['interface'] == 'public'][0]
    url = urlparse.urlsplit(endpoint['url'])
    http_client.set_api_key(
        url.hostname, access_info.auth_token,
        param_name='x-auth-token', param_in='header'
    )
    spec = yaml.safe_load(open(schema))
    spec['host'] = url.hostname if not url.port else '%s:%s' % (
        url.hostname, url.port)
    path = url.path[:-1] if url.path[-1] == '/' else url.path
    spec['basePath'] = path + spec['basePath']
    spec['schemes'] = [url.scheme]
    config = {
        'also_return_response': True
    }
    client = SwaggerClient.from_spec(
        spec,
        http_client=http_client,
        config=config)
    return client
