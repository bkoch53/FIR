from django.contrib.contenttypes.models import ContentType

from fir_notifications.registry import registry
from fir_notifications.tasks import handle_notification

from findings.models import BusinessLine


def notification_observation(observation, signal, model, verbose_name=None, section=None):
    """
    Decorates a Django signal handler to create a notification observation
    Args:
        observation: observation name
        signal: Django signal to listen to
        model: Django model sending the signal (and observation)
        verbose_name: verbose name of the notification observation
        section: section in the user preference panel (default model application name)

    The signal handler function must return a tuple (model instance, business lines list concerned by the observation)

    """
    def decorator_func(func):
        def wrapper_func(*args, **kwargs):
            instance, business_lines = func(*args, **kwargs)
            if instance is None:
                return instance, business_lines
            if isinstance(business_lines, BusinessLine):
                business_lines = [business_lines.path,]
            else:
                business_lines = list(business_lines.distinct().values_list('path', flat=True))
            handle_notification.delay(ContentType.objects.get_for_model(instance).pk,
                                      instance.pk,
                                       business_lines,
                                      observation)
            return instance, business_lines

        registry.register_observation(observation, signal, model, wrapper_func, verbose_name, section)
        return wrapper_func
    return decorator_func