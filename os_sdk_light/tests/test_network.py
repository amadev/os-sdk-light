import pytest
import uuid
import os_sdk_light as osl
from bravado_core import exception

CLOUD = "devstack"
c = osl.get_client(cloud=CLOUD, service="network", schema=osl.schema("network.yaml"))


def test_port():
    networks = c.networks.list()["networks"]
    network = [i for i in networks if "private" in i["name"]][0]
    port_id = str(uuid.uuid4())
    port = c.ports.create_port(port={"port": {"network_id": network["id"]}})["port"]
    port = c.ports.get_port(port_id=port["id"])["port"]
    c.ports.list_ports(id=port["id"])
    port = c.ports.update_port(port_id=port["id"], port={"port": {"name": port_id}})[
        "port"
    ]
    c.ports.delete_port(port_id=port["id"])


def test_floatingip(server):
    networks = c.networks.list()["networks"]
    network = [i for i in networks if "public" in i["name"]][0]
    port = c.ports.list_ports(device_id=server["id"])['ports'][0]
    floatingip_id = str(uuid.uuid4())
    floatingip = c.floatingips.create_floatingip(
        floatingip={
            "floatingip": {"floating_network_id": network["id"], "port_id": port['id']}
        }
    )["floatingip"]
    floatingip = c.floatingips.get_floatingip(floatingip_id=floatingip["id"])[
        "floatingip"
    ]
    c.floatingips.list_floatingips(id=floatingip["id"])
    floatingip = c.floatingips.update_floatingip(
        floatingip_id=floatingip["id"],
        floatingip={"floatingip": {"description": floatingip_id}},
    )["floatingip"]
    c.floatingips.delete_floatingip(floatingip_id=floatingip["id"])
