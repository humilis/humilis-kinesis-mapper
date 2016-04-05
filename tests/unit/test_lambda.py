"""Test the logic of the Lambda function."""
from mock import Mock

from humilis_kinesis_mapper.lambda_function.handler.processor.main import process_event  # noqa


def test_process_event(kinesis_event, event, context, boto3_client,
                       monkeypatch):
    """Process events."""
    cal = Mock()
    partition_key = lambda ev: ev.get("client_id", "")
    process_event(kinesis_event, context,
                  "output_stream", "input_delivery", "output_delivery",
                  "environment",
                  "layer",
                  "stage",
                  [cal],
                  partition_key)
    # The processor should have inserted the records in the output stream
    assert boto3_client("kinesis").put_records.call_count == 1
    state_args = dict(
        environment="environment",
        layer="layer", stage="stage",
        shard_id="shardId-000000000000")
    cal.assert_called_once_with(event, state_args=state_args)
