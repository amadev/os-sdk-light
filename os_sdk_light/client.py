import os
import logging
import yaml

import os_client_config
from bravado.client import SwaggerClient
from bravado.requests_client import RequestsClient
from six.moves.urllib import parse as urlparse
import keystoneauth1.exceptions as ka_excs
from os_sdk_light import exceptions


LOG = logging.getLogger(__name__)
SCHEMAS = os.path.dirname(os.path.realpath(__file__)) + '/schemas/'


def schema(name):
    return SCHEMAS + name


def get_client(cloud, service, schema, config={}):
    try:
        cloud = os_client_config.OpenStackConfig(**config).get_one(cloud)
    except ka_excs.MissingRequiredOptions:
        LOG.exception(
            'Not enough params to build a cloud connection. '
            'Please provide config file or environment variables, '
            'See https://docs.openstack.org/'
            'os-client-config/latest/user/configuration.html')
        raise exceptions.CannotConnectToCloud(
            'Not enough params to build a cloud connection')

    adapter = cloud.get_session_client(service)
    try:
        access_info = adapter.session.auth.get_access(adapter.session)
    except (ka_excs.Unauthorized, ka_excs.BadRequest):
        LOG.exception(
            'Cloud authentication failed. '
            'Please check credintial and auth_url')
        raise exceptions.CannotConnectToCloud('Authentication failed')
    endpoints = access_info.service_catalog.get_endpoints()
    try:
        interface = cloud.config.get('interface', 'public')
        endpoint = [e for e in endpoints[service]
                    if e['interface'] == interface][0]
    except (KeyError, IndexError, TypeError):
        LOG.exception(
            'Endpoint for service %s with interface %s is not found. '
            'Try to check service exists in service catalog.'
            % (service, interface))
        raise exceptions.CannotConnectToCloud(
            'Failed failed to find service endpoint')

    http_client = RequestsClient()
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
