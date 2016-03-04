from django.db.models import signals
from django.db import connection

try:
    from django.apps import apps
    get_model = apps.get_model
except ImportError:
    from django.db.models import get_model

from haystack.signals import BaseSignalProcessor


# from haystack import indexes
from haystack.utils import get_identifier
from haystack.constants import DEFAULT_ALIAS
from haystack import connections
from haystack.exceptions import NotHandled

from django_rq import get_queue

from haystack_rqueue.conf import QUEUE_NAME


def split_obj_identifier(obj_identifier):
    """
    Break down the identifier representing the instance.

    Converts 'notes.note.23' into ('notes.note', 23).
    """
    bits = obj_identifier.split('.')

    if len(bits) < 2:
        return (None, None)

    pk = '.'.join(bits[2:])
    # In case Django ever handles full paths...
    object_path = '.'.join(bits[0:2])
    return (object_path, pk)


def get_model_class(object_path):
    """Fetch the model's class in a standarized way."""
    bits = object_path.split('.')
    app_name = '.'.join(bits[:-1])
    classname = bits[-1]
    return get_model(app_name, classname)


def get_index_for_model(model_class, connection=DEFAULT_ALIAS):
    """Fetch the model's registered ``SearchIndex`` in a standarized way."""
    try:
        return connections[connection].get_unified_index().get_index(model_class)
    except NotHandled:
        return None


def index_update_obj(object_id):
    connection.close()

    object_path, pk = split_obj_identifier(object_id)
    if not (object_path or pk):
        return

    model_class = get_model_class(object_path)
    if not model_class:
        return

    index = get_index_for_model(model_class)
    if not index:
        return

    try:
        obj = model_class._default_manager.get(pk=pk)
        index._get_backend(DEFAULT_ALIAS).update(index, [obj])
    except model_class.DoesNotExist:
        pass


def index_delete_obj(object_id):
    connection.close()

    object_path, pk = split_obj_identifier(object_id)
    if not (object_path or pk):
        return

    model_class = get_model_class(object_path)
    if not model_class:
        return

    index = get_index_for_model(model_class)
    if not index:
        return

    index.remove_object(object_id, using=DEFAULT_ALIAS)


class RQueueSignalProcessor(BaseSignalProcessor):
    """
    A ``BaseSignalProcessor`` subclass that handles updates/deletes in the background using RQ.
    """

    def _get_dispatch_uid(self, model_class):
        return '{processor_class}@{processor_instance}-{model_class}'.format(
            processor_class=self.__class__.__name__,
            processor_instance=id(self),
            model_class=model_class.__name__,
        )

    def connect_signals(self):
        for using in self.connections.connections_info.keys():
            for model_class in self.connections[using].get_unified_index().get_indexed_models():
                signals.post_save.connect(
                    self.enqueue_save,
                    sender=model_class,
                    dispatch_uid=self._get_dispatch_uid(model_class) + '-save'
                )

                signals.post_delete.connect(
                    self.enqueue_delete, sender=model_class,
                    dispatch_uid=self._get_dispatch_uid(model_class) + '-delete')

    def setup(self):
        try:
            from django.apps import apps
            models_ready = apps.models_ready
        except ImportError:
            models_ready = True

        if models_ready:
            self.connect_signals()
        else:
            from haystack_rqueue import HaystackRqueueAppConfig
            HaystackRqueueAppConfig.init = self.connect_signals

    def teardown(self):
        signals.post_save.disconnect(self.enqueue_save)
        signals.post_delete.disconnect(self.enqueue_delete)

    def enqueue_save(self, instance, **kwargs):
        get_queue(QUEUE_NAME).enqueue(index_update_obj, get_identifier(instance))

    def enqueue_delete(self, instance, **kwargs):
        get_queue(QUEUE_NAME).enqueue(index_delete_obj, get_identifier(instance))
