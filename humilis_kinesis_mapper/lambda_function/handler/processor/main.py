# -*- coding: utf-8 -*-
from __future__ import print_function

import logging
import json


from . import core
import lambdautils.utils as utils
from .exceptions import KinesisError, FirehoseError

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def process_event(
        kinesis_event, context, output_stream_name, input_delivery_stream_name,
        output_delivery_stream_name, environment, layer, stage, callables,
        partition_key):
    """Forwards events to a Kinesis stream (for further processing) and
    to a Kinesis Firehose delivery stream (for persistence in S3 and/or
    Redshift)"""
    events, shard_id = utils.unpack_kinesis_event(
        kinesis_event, deserializer=json.loads)

    if input_delivery_stream_name:
        logger.info("Sending {} events to delivery stream '{}' ...".format(
            len(events), input_delivery_stream_name))
        resp = utils.send_to_delivery_stream(events,
                                             input_delivery_stream_name)
        if resp['ResponseMetadata']['HTTPStatusCode'] != 200:
            raise FirehoseError(json.dumps(resp))
        logger.info(resp)

    logger.info("Going to transform {} events from shard '{}'".format(
        len(events), shard_id))

    logger.info("First input event: {}".format(
        json.dumps(events[0], indent=4)))

    logger.info("Applying {} callables: {}".format(len(callables), callables))

    core.transform_events(events, callables, environment, layer, stage,
                          shard_id)

    logger.info("First transformed event: {}".format(
        json.dumps(events[0], indent=4)))

    if output_stream_name:
        logger.info("Sending {} events to output stream '{}' ...".format(
            len(events), output_stream_name))

        logger.info("Using partition key: {}".format(partition_key))
        resp = utils.send_to_kinesis_stream(events, output_stream_name,
                                            partition_key=partition_key)
        if resp['ResponseMetadata']['HTTPStatusCode'] != 200:
            raise KinesisError(json.dumps(resp))
        logger.info(resp)
    else:
        logger.info("No output stream: will not deliver transformed events")

    if output_delivery_stream_name:
        logger.info("Sending {} events to delivery stream '{}' ...".format(
            len(events), input_delivery_stream_name))
        resp = utils.send_to_delivery_stream(events,
                                             output_delivery_stream_name)
        if resp['ResponseMetadata']['HTTPStatusCode'] != 200:
            raise FirehoseError(json.dumps(resp))
        logger.info(resp)

    logger.info("Successfully processed {} Kinesis records:".format(
        len(events)))
