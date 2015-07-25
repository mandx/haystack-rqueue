# -*- coding: utf-8 -*-


from django.utils.translation import ugettext_lazy as _

__author__ = u'Armando Pérez'


try:
    from django.apps import AppConfig
except ImportError:
    class AppConfig(object):
        pass

class HaystackRqueueAppConfig(AppConfig):
    name = 'haystack_rqueue'
    verbose_name = _('Haystack RQ Signal Processor')

    def ready(self):
        try:
            self.init()
        except (AttributeError, TypeError):
            pass


default_app_config = 'haystack_rqueue.HaystackRqueueAppConfig'
