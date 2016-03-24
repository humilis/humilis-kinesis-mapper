"""Lambda function entry point."""
from .processor.main import process_event
import lambdautils.utils as utils
from werzeug.utils import import_string

# preprocessor:jinja2
callables = [
    {% for name in callables %}
        import_string("{{name}}"),
    {% endfor %}
]


@utils.sentry_monitor(
    environment="{{_env.name}}",
    stage="{{_env.stage}}",
    layer="{{_layer.name}}",
    error_delivery_stream="{{error_delivery_stream and error_delivery_stream.name}}",
    error_stream="{{error_stream and error_stream.name}}")
def lambda_handler(event, context):
    """Lambda function."""
    return process_event(
        event, context,
        "{{output_stream and output_stream.name}}",
        "{{input_delivery_stream and input_delivery_stream.name}}",
        "{{output_delivery_stream and output_delivery_stream.name}}",
        callables,
    )
