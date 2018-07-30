#!/usr/bin/env python
from __future__ import print_function
import sys
import yaml

import os_sdk_light as osl


placement_client = osl.get_client(
    'devstack', 'placement', osl.schema('placement.yaml'))


def main(limit):
    output = {}
    rps = placement_client.resource_providers.list_resource_providers()[
        'resource_providers']
    for rp in rps[0:limit]:
        output[rp['uuid']] = {}
        usages = placement_client.resource_providers.get_usages(
            uuid=rp['uuid'])['usages']
        traits = placement_client.resource_providers.get_rp_traits(
            uuid=rp['uuid'])['traits']
        aggregates = placement_client.resource_providers.get_aggregates(
            uuid=rp['uuid'])['aggregates']
        for name, props in placement_client.resource_providers.get_inventories(
                uuid=rp['uuid'])['inventories'].items():
            output[rp['uuid']][name] = {'total': props['total'],
                                        'used': usages.get(name, 0)}
        output[rp['uuid']]['traits'] = traits
        output[rp['uuid']]['aggregates'] = aggregates

    print(yaml.safe_dump(output))


if __name__ == '__main__':
    try:
        limit = sys.argv[1]
    except IndexError:
        limit = 1
    main(1)
