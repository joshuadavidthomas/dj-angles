import logging

from django.apps import apps

from dj_angles.templatetags.call import CallNode, do_call

logger = logging.getLogger(__name__)

"""
Global storage of all available models.
"""
models = None


class ModelNode(CallNode):
    def render(self, context):
        global models  # noqa: PLW0603

        if models is None:
            models = {}
            for app_config in apps.get_app_configs():
                for model in app_config.get_models():
                    # TODO: What if model names overlap?
                    models[model.__name__] = model

        context["__dj_angles_models"] = models

        return super().render(context)


def do_model(parser, token) -> ModelNode:  # noqa: ARG001
    call_node = do_call(parser, token)

    # Models are stored in a special part of the context so it doesn't conflict with other data
    # so add this fake object name because we will use it in the render method
    call_node.parsed_function.object_tokens.insert(0, "__dj_angles_models")

    return ModelNode(call_node.parsed_function, call_node.context_variable_name)
