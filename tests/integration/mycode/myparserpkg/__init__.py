"""A sample Python package to test the layer."""

import uuid

import lambdautils.utils as utils
from user_agents import parse


def partition_key(event, **kwargs):
    """Produces the partition key for an event."""
    return event.get("client_id", str(uuid.uuid4()))


def parse_ua(event, state_args=None):
    parsed = parse(event["user_agent"])
    event["device_family"] = parsed.device.family or ""
    event["device_brand"] = parsed.device.brand or ""

    utils.set_state("my_state_key", "my_state_value", namespace="my_namespace",
                    **state_args)
    assert utils.get_state("my_state_key", namespace="my_namespace",
                           **state_args) == "my_state_value"
