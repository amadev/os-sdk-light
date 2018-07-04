import os
import logging
import yaml

import os_client_config
from bravado.client import SwaggerClient, CallableOperation, ResourceDecorator
from bravado.requests_client import RequestsClient
from swagger_spec_validator.common import SwaggerValidationError
from six.moves.urllib import parse as urlparse
import keystoneauth1.exceptions as ka_excs
from os_sdk_light import exceptions


LOG = logging.getLogger(__name__)
SCHEMAS = os.path.dirname(os.path.realpath(__file__)) + '/schemas/'


class OSLCallableOperation(CallableOperation):
    def __call__(self, **op_kwargs):
        return super(OSLCallableOperation, self).__call__(
            **op_kwargs).response().result


class OSLResourceDecorator(ResourceDecorator):
    def __getattr__(self, name):
        """
        :rtype: :class:`CallableOperation`
        """
        return OSLCallableOperation(getattr(self.resource, name), False)


class OSLSwaggerClient(SwaggerClient):
    def _get_resource(self, item):
        """
        :param item: name of the resource to return
        :return: :class:`Resource`
        """
        resource = self.swagger_spec.resources.get(item)
        if not resource:
            raise AttributeError(
                'Resource {0} not found. Available resources: {1}'
                .format(item, ', '.join(dir(self))))

        # Wrap bravado-core's Resource and Operation objects in order to
        # execute a service call via the http_client.
        return OSLResourceDecorator(resource, False)


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
            'Failed to find service endpoint')
    try:
        with open(schema) as f:
            spec = yaml.safe_load(f)
            SwaggerClient.from_spec(spec)
    except (IOError, ValueError, SwaggerValidationError):
        LOG.exception(
            'Schema file %s cannot be read or incorrect. '
            'Please check file exists, accessible '
            'and satisfies swagger 2.0 specification.')
        raise exceptions.SchemaError('Schema file cannot be read or invalid')
    url = urlparse.urlsplit(endpoint['url'])
    spec['host'] = url.netloc
    path = url.path[:-1] if url.path.endswith('/') else url.path
    spec['basePath'] = path + spec['basePath']
    spec['schemes'] = [url.scheme]
    LOG.debug('Got swagger server configuration for service %s: %s%s',
              service, spec['host'], spec['basePath'])

    http_client = RequestsClient()
    http_client.set_api_key(
        url.hostname, access_info.auth_token,
        param_name='x-auth-token', param_in='header'
    )
    client = OSLSwaggerClient.from_spec(
        spec,
        http_client=http_client,
        config=config)
    return client
