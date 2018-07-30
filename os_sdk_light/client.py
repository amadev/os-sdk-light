import sys
import six
import os
import logging
import yaml
import keystoneauth1.exceptions as ka_excs
import jsonschema.exceptions
import os_client_config

from six.moves.urllib import parse as urlparse
from bravado.client import SwaggerClient, CallableOperation, ResourceDecorator
from bravado.requests_client import RequestsClient
from swagger_spec_validator.common import SwaggerValidationError
from bravado_core.exception import SwaggerMappingError
from os_sdk_light import exceptions


LOG = logging.getLogger(__name__)
SCHEMAS = os.path.dirname(os.path.realpath(__file__)) + '/schemas/'


class OSLCallableOperation(CallableOperation):
    def __call__(self, **op_kwargs):
        try:
            return super(OSLCallableOperation, self).__call__(
                **op_kwargs).response().result
        except (SwaggerMappingError,
                jsonschema.exceptions.ValidationError) as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            LOG.exception(
                'Exception happens during request or response parsing. '
                'Please check schema is valid and server version corresponds '
                'to the declared')
            raise six.reraise(
                exceptions.ValidationError,
                exceptions.ValidationError(e),
                exc_traceback)
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            LOG.exception(
                'Exception happens while getting response from server. '
                'This could be part of the normal flow '
                'like 404 for non existing objects')
            new_exception = exceptions.UnexpectedResponse(e, e)
            raise six.reraise(
                exceptions.UnexpectedResponse,
                new_exception,
                exc_traceback)


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


class OSLRequestsClient(RequestsClient):
    def request(self, *args, **kwargs):
        http_future = super(OSLRequestsClient, self).request(*args, **kwargs)
        if hasattr(self, 'custom_headers'):
            for header, value in self.custom_headers:
                http_future.future.request.headers.setdefault(header, value)
        return http_future


def schema(name):
    return SCHEMAS + name


def get_client(cloud, service, schema, config={}):
    try:
        cloud = os_client_config.OpenStackConfig(**config).get_one(cloud)
    except ka_excs.MissingRequiredOptions as e:
        LOG.exception(
            'Not enough params to build a cloud connection. '
            'Please provide config file or environment variables, '
            'See https://docs.openstack.org/'
            'os-client-config/latest/user/configuration.html')
        raise exceptions.CannotConnectToCloud(
            'Not enough params to build a cloud connection: %s' % e)

    adapter = cloud.get_session_client(service)
    try:
        access_info = adapter.session.auth.get_access(adapter.session)
    except (ka_excs.Unauthorized, ka_excs.BadRequest) as e:
        LOG.exception(
            'Cloud authentication failed. '
            'Please check credintial and auth_url')
        raise exceptions.CannotConnectToCloud('Authentication failed: %s' % e)
    endpoints = access_info.service_catalog.get_endpoints()
    try:
        interface = cloud.config.get('interface', 'public')
        endpoint = [e for e in endpoints[service]
                    if e['interface'] == interface][0]
    except (KeyError, IndexError, TypeError) as e:
        LOG.exception(
            'Endpoint for service %s with interface %s is not found. '
            'Try to check service exists in service catalog.'
            % (service, interface))
        raise exceptions.CannotConnectToCloud(
            'Failed to find service endpoint: %s' % e)
    try:
        with open(schema) as f:
            spec = yaml.safe_load(f)
            SwaggerClient.from_spec(spec)
    except (IOError, ValueError, SwaggerValidationError) as e:
        LOG.exception(
            'Schema file %s cannot be read or incorrect. '
            'Please check file exists, accessible '
            'and satisfies swagger 2.0 specification.' % schema)
        raise exceptions.SchemaError(
            'Schema file cannot be read or invalid: %s' % e)

    url = urlparse.urlsplit(endpoint['url'])
    spec['host'] = url.netloc
    path = url.path[:-1] if url.path.endswith('/') else url.path
    spec['basePath'] = path + spec['basePath']
    spec['schemes'] = [url.scheme]
    LOG.debug('Got swagger server configuration for service %s: %s%s',
              service, spec['host'], spec['basePath'])

    http_client = OSLRequestsClient()
    http_client.set_api_key(
        url.hostname, access_info.auth_token,
        param_name='x-auth-token', param_in='header'
    )
    version_header = spec['info'].get('x-version-header')
    if version_header:
        template = spec['info'].get('x-version-header-value-template', '%s')
        http_client.custom_headers = [
            (version_header, template % spec['info']['version'])]

    client = OSLSwaggerClient.from_spec(
        spec,
        http_client=http_client,
        config=config)
    return client
