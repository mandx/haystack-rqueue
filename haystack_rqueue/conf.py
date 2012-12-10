from django.conf import settings

QUEUE_NAME = getattr(settings, 'HAYSTACK_RQUEUE_QUEUE_NAME', 'default')
