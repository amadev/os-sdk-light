import pytest
import uuid
import os_sdk_light as osl
from bravado_core import exception


TEST_RP = "test resource provider %s" % uuid.uuid4()
CLOUD = "devstack"
c = osl.get_client(CLOUD, "placement", osl.schema("placement.yaml"))


@pytest.fixture
def rp():
    orig_rp = {"name": TEST_RP}
    c.resource_providers.create_resource_provider(body=orig_rp)
    rp = c.resource_providers.list_resource_providers(
        name=orig_rp["name"]
    )["resource_providers"][0]
    yield rp
    c.resource_providers.delete_resource_provider(uuid=rp["uuid"])


def test_rps(rp):
    rp1 = c.resource_providers.get_resource_provider(uuid=rp["uuid"])
    assert rp["name"] == rp1["name"]


def test_inventories(rp):
    c.resource_providers.put_inventories(
        uuid=rp["uuid"],
        body={
            "resource_provider_generation": rp["generation"],
            "inventories": {"MEMORY_MB": {"total": 512}},
        },
    )
    invs = c.resource_providers.get_inventories(uuid=rp["uuid"])
    c.resource_providers.put_inventories(
        uuid=rp["uuid"],
        body={
            "resource_provider_generation": invs["resource_provider_generation"],
            "inventories": {},
        },
    )


def test_aggregates(rp):
    u1 = "%s" % uuid.uuid4()
    u2 = "%s" % uuid.uuid4()
    c.resource_providers.put_aggregates(uuid=rp["uuid"], body=[u1, u2])
    aggs = c.resource_providers.get_aggregates(uuid=rp["uuid"])[
        "aggregates"
    ]
    assert set([u1, u2]) == set(aggs)
    c.resource_providers.put_aggregates(uuid=rp["uuid"], body=[])


def test_traits():
    name = f'custom-trait-{uuid.uuid4()}'.replace('-', '_').upper()
    c.traits.set_trait(name=name)
    c.traits.get_trait(name=name)
    c.traits.delete_trait(name=name)
