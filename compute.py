import os
import logging

import os_client_config
from bravado.client import SwaggerClient
from bravado.requests_client import RequestsClient
from six.moves.urllib import parse as urlparse


log = logging.getLogger(__name__)


def get_http_client(cloud_name, service_name):
    config = os_client_config.OpenStackConfig()
    cloud = config.get_one_cloud(cloud_name)
    adapter = cloud.get_session_client(service_name)
    access_info = adapter.session.auth.get_access(adapter.session)
    endpoints = access_info.service_catalog.get_endpoints()
    http_client = RequestsClient()
    host = urlparse.urlsplit(endpoints[service_name][0]['url']).hostname
    http_client.set_api_key(
        host, access_info.auth_token,
        param_name='x-auth-token', param_in='header'
    )
    return http_client


compute_http_client = get_http_client('devstack', 'compute')
dir_path = os.path.dirname(os.path.realpath(__file__))
config = {
    'also_return_response': True
}
compute_client = SwaggerClient.from_url(
    'file://%s/compute.yaml' % dir_path ,
    http_client=compute_http_client,
    config=config
)

for f in compute_client.flavors.list().response().result['flavors']:
    print f['id'], f['name']
