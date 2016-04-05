# -*- coding: utf-8 -*-

# preprocessor:jinja2


def transform_events(events, callables, environment, layer, stage, shard_id):
    """Transforms events with the given callables."""

    state_args = dict(environment=environment, layer=layer, stage=stage,
                      shard_id=shard_id)
    for event in events:
        for cal in callables:
            cal(event, state_args=state_args)

    return events
