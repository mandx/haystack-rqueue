from django.conf import settings
from django.db.models import signals, get_model

from haystack import indexes
from haystack.utils import get_identifier
from haystack.constants import DEFAULT_ALIAS
from haystack import connections
from haystack.exceptions import NotHandled

from django_rq import get_queue

from haystack_rqueue.conf import QUEUE_NAME


def get_index(model_class):
    """Fetch the model's registered ``SearchIndex`` in a standarized way."""
    try:
        return connections['default'].get_unified_index().get_index(model_class)
    except NotHandled:
        return None


def get_model_class(object_path):
    """Fetch the model's class in a standarized way."""
    bits = object_path.split('.')
    app_name = '.'.join(bits[:-1])
    classname = bits[-1]
    return get_model(app_name, classname)


def split_obj_identifier(obj_identifier):
    """
    Break down the identifier representing the instance.

    Converts 'notes.note.23' into ('notes.note', 23).
    """
    bits = obj_identifier.split('.')

    if len(bits) < 2:
        return (None, None)

    pk = bits[-1]
    # In case Django ever handles full paths...
    object_path = '.'.join(bits[:-1])
    return (object_path, pk)


def index_update_obj(object_id):
    object_path, pk = split_obj_identifier(object_id)
    if not (object_path or pk):
        return

    model_class = get_model_class(object_path)
    if not model_class:
        return

    index = get_index(model_class)
    if not index:
        return

    try:
        obj = model_class._default_manager.get(pk=pk)
        index._get_backend(DEFAULT_ALIAS).update(index, [obj])
    except model_class.DoesNotExist:
        pass


def index_delete_obj(object_id):
    object_path, pk = split_obj_identifier(object_id)
    if not (object_path or pk):
        return

    model_class = get_model_class(object_path)
    if not model_class:
        return

    index = get_index(model_class)
    if not index:
        return

    index.remove_object(object_id, using=DEFAULT_ALIAS)


class RQueueSearchIndex(indexes.SearchIndex):
    """
    A ``SearchIndex`` subclass that handles updates/deletes in the background using RQ.
    """

    # We override the built-in _setup_* methods to connect the enqueuing operation.
    def _setup_save(self):
        signals.post_save.connect(self.enqueue_save, sender=self.get_model())

    def _setup_delete(self):
        signals.post_delete.connect(self.enqueue_delete, sender=self.get_model())

    def _teardown_save(self):
        signals.post_save.disconnect(self.enqueue_save, sender=self.get_model())

    def _teardown_delete(self):
        signals.post_delete.disconnect(self.enqueue_delete, sender=self.get_model())

    def enqueue_save(self, instance, **kwargs):
        get_queue(QUEUE_NAME).enqueue(index_update_obj, get_identifier(instance))

    def enqueue_delete(self, instance, **kwargs):
        get_queue(QUEUE_NAME).enqueue(index_delete_obj, get_identifier(instance))
