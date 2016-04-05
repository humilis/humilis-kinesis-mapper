# -*- coding: utf-8 -*-
from __future__ import print_function

import logging
import json

import lambdautils.utils as utils

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class KinesisError(Exception):
    pass


class FirehoseError(Exception):
    pass


def _default_mapper(ev, state_args):
    return ev


def process_event(
        kinesis_event, context, environment, layer, stage, input, output):
    """Forwards events to a Kinesis stream (for further processing) and
    to a Kinesis Firehose delivery stream (for persistence in S3 and/or
    Redshift)"""

    events, shard_id = utils.unpack_kinesis_event(
        kinesis_event, deserializer=json.loads)

    input_delivery_stream = input.get("firehose_delivery_stream")
    if input_delivery_stream:
        send_to_delivery_stream(events, input_delivery_stream)

    # Arguments passed to user callables that are needed to set/get processor
    # state.
    sargs = dict(environment=environment, layer=layer, stage=stage,
                 shard_id=shard_id)

    logger.info("Going to process {} events".format(len(events)))
    logger.info("First event: {}".format(pretty(events[0])))

    if input.get("filter"):
        logger.info("Filtering input events")
        events = [ev for ev in events if input["filter"](ev, sargs)]
        if not events:
            logger.info("All input events were filtered out: nothing to do")
            return
        else:
            logger.info("Selected {} input events".format(len(events)))
    else:
        logger.info("No input filter: using all input events")

    if input.get("mapper"):
        logger.info("Mapping input evets")
        for ev in events:
            input["mapper"](ev, sargs)
        logger.info("First mapped input events: {}".format(pretty(events[0])))
    else:
        logger.info("No input mapping: processing raw input events")

    oevents = []
    _all = lambda ev, sargs: True
    for i, o in enumerate(output):
        logger.info("Producing output #{}".format(i))
        ofilter = o.get("filter", _all)
        if not ofilter:
            ofilter = _all
        oevents.append([dict(ev) for ev in events if ofilter(ev, sargs)])
        logger.info("Selected {} events".format(len(oevents[i])))

        if not oevents[i]:
            continue

        omapper = o.get("mapper", _default_mapper)
        for ev in oevents[i]:
            omapper(ev, state_args=sargs)

        logger.info("Successfully mapped {} events".format(len(oevents[i])))
        logger.info("First mapped event: {}".format(pretty(oevents[0])))

        # To make the processing task as atomic as possible, do no send any
        # event to the output streams before making sure that no filter nor
        # mapper raises an exception.

    for i, o in enumerate(output):
        logger.info("Forwarding output #{}".format(i))
        stream = o.get("kinesis_stream")
        if stream:
            send_to_kinesis_stream(oevents[i], stream, o.get("partition_key"))
        else:
            logger.info("No output Kinesis stream: not forwarding to Kinesis")

        delivery_stream = o.get("firehose_delivery_stream")
        if delivery_stream:
            send_to_delivery_stream(oevents[i], delivery_stream)
        else:
            logger.info("No FH delivery stream: not forwarding to FH")


def send_to_delivery_stream(events, delivery_stream):
    if events:
        logger.info("Sending events to delivery stream '{}' ...".format(
            len(events), delivery_stream))
        resp = utils.send_to_delivery_stream(events, delivery_stream)
        if resp['ResponseMetadata']['HTTPStatusCode'] != 200:
            raise FirehoseError(json.dumps(resp))
        logger.info(resp)


def send_to_kinesis_stream(events, stream, partition_key):
    if events:
        logger.info("Sending {} events to stream '{}' ...".format(
            len(events), stream))

        logger.info("Using partition key: {}".format(partition_key))
        resp = utils.send_to_kinesis_stream(events, stream,
                                            partition_key=partition_key)
        if resp['ResponseMetadata']['HTTPStatusCode'] != 200:
            raise KinesisError(json.dumps(resp))
        logger.info(resp)


def pretty(event):
    return json.dumps(event, indent=4)