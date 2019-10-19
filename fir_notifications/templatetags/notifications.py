from django import template

from fir_notifications.registry import registry

register = template.Library()


@register.inclusion_tag('fir_notifications/actions.html')
def notification_actions():
    actions = {}
    for method_name, method_object in registry.methods.items():
        if len(method_object.options):
            actions[method_name] = method_object.verbose_name
    return {'actions': actions}


@register.inclusion_tag('fir_notifications/actions_form.html', takes_context=True)
def notification_forms(context):
    actions = {}
    for method_name, method_object in registry.methods.items():
        if len(method_object.options):
            actions[method_name] = method_object.form(user=context['user'])
    return {'actions': actions}


@register.filter
def display_method(arg):
    method = registry.methods.get(arg, None)
    if method is None:
        return 'Unknown'
    return method.verbose_name


@register.filter
def display_observation(arg):
    observation = registry.observations.get(arg, None)
    if observation is None:
        return 'Unknown'
    return observation.verbose_name


@register.filter
def display_observation_section(arg):
    observation = registry.observations.get(arg, None)
    if observation is None:
        return 'Unknown'
    return observation.section
