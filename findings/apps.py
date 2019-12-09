from django.apps import AppConfig


class FindingsConfig(AppConfig):
    name = 'findings'

    def ready(self):
        from fir_plugins.links import registry
        from django.conf import settings
        registry.register_reverse_link(settings.EVENT_ID_PREFIX + "(\d+)", 'findings:details',
                                       model='findings.Finding', reverse=settings.EVENT_ID_PREFIX + "{}")
