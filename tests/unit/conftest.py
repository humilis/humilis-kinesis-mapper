# -*- coding: utf-8 -*-
"""Fixtures."""
from __future__ import unicode_literals
import codecs

import json
from unittest.mock import Mock
import uuid

import pytest


@pytest.fixture(scope="session")
def event(request):
    """An event that will be inserted in a Kinesis stream."""
    return {
        "id": str(uuid.uuid4()),
        "user_agent": "BlackBerry9700/5.0.0.862 Profile/MIDP-2.1 Configuration/CLDC-1.1 "
                      "VendorID/331 UNTRUSTED/1.0 3gpp-gba",
    }


@pytest.fixture
def kinesis_event_template():
    """A sample Kinesis event."""
    return {
        "Records": [
            {
                "eventID": "shardId-000000000000:44200961",
                "eventVersion": "1.0",
                "kinesis": {
                    "partitionKey": "partitionKey-3",
                    "data": "",
                    "kinesisSchemaVersion": "1.0",
                    "sequenceNumber": "4954511524144582180062593244200961"
                },
                "invokeIdentityArn": "arn:aws:iam::EXAMPLE",
                "eventName": "aws:kinesis:record",
                "eventSourceARN": "arn:aws:kinesis:EXAMPLE",
                "eventSource": "aws:kinesis",
                "awsRegion": "us-east-1"
            }
        ]
    }


@pytest.fixture
def kinesis_event(kinesis_event_template, event):
    """A sample Kinesis event."""
    encoded_event = codecs.encode(json.dumps(event).encode("utf-8"), "base64")
    kinesis_event_template["Records"][0]["kinesis"]["data"] = encoded_event
    return kinesis_event_template


@pytest.fixture
def event_bad():
    """A bad event that should trigger and exception."""
    return "This is a bad event!"


@pytest.fixture
def kinesis_event_bad(kinesis_event, event_bad):
    """A sample Kinesis event."""
    encoded_event = codecs.encode(event_bad.encode("utf-8"), "base64")
    kinesis_event["Records"][0]["kinesis"]["data"] = encoded_event
    return kinesis_event


@pytest.fixture(scope="session")
def context():
    """A dummy CF context object."""
    class DummyContext:

        def __init__(self):
            self.function_name = "dummy_name"
            self.function_version = 1
            self.invoked_function_arn = "arn"
            self.memory_limit_in_mb = 128
            self.aws_request_id = str(uuid.uuid4())
            self.log_group_name = "dummy_group"
            self.log_stream_name = "dummy_stream"
            self.identity = Mock(return_value=None)
            self.client_context = Mock(return_value=None)

        def get_remaining_Time_in_millis():
            return 100

    return DummyContext()


@pytest.fixture
def kms_client():
    """A mocked version of boto3 DynamoDB client."""
    mocked = Mock()
    mocked.decrypt = Mock(return_value={"Plaintext": b"dummy"})
    return mocked


@pytest.fixture
def kinesis_client():
    """A mocked version of boto3 Kinesis client."""
    mocked = Mock()
    ok_resp = {"ResponseMetadata": {"HTTPStatusCode": 200}}
    mocked.put_records = Mock(return_value=ok_resp)
    mocked.put_record_batch = Mock(return_value=ok_resp)
    return mocked


@pytest.fixture
def dynamodb_resource():
    """A mocked version of boto3 DynamoDB resource."""
    mock_item = Mock()
    mock_item.value = "encrypted"
    mock_item.get = Mock(return_value=None)
    rv = {"Item": mock_item}
    mocked_table = Mock()
    mocked_table.get_item = Mock(return_value=rv)
    mocked = Mock()
    mocked.Table = Mock(return_value=mocked_table)
    return mocked


@pytest.fixture
def dynamodb_client():
    """DynamoDB client."""
    mocked = Mock()
    rv = {"Item": {"value": {"B": "encrypted"}}}
    mocked.get_item = Mock(return_value=rv)
    mocked.decrypt = Mock(return_value={"Plaintext": b"dummy"})
    return mocked


@pytest.fixture
def boto3_client(kinesis_client, kms_client, dynamodb_client):
    """A mock for boto3.client."""
    def produce_client(name):
        return {"kinesis": kinesis_client, "kms": kms_client,
                "firehose": kinesis_client,
                "dynamodb": dynamodb_client}[name]

    mocked = Mock(side_effect=produce_client)
    return mocked


@pytest.fixture
def boto3_resource(dynamodb_resource):
    """A mock for boto3.resource."""
    def produce_resource(name):
        return {"dynamodb": dynamodb_resource}[name]

    mocked = Mock(side_effect=produce_resource)
    return mocked


@pytest.fixture(autouse=True)
def global_patch(boto3_client, boto3_resource, monkeypatch):
    """Patch boto3."""
    monkeypatch.setattr("boto3.client", boto3_client)
    monkeypatch.setattr("boto3.resource", boto3_resource)
