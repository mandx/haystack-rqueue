# haystack-rqueue

Allows you to leverage the update/delete operations of your
[Haystack](http://haystacksearch.org/) search index to backgrounds tasks
using [RQ](http://python-rq.org), a lightweight [Redis](http://redis.io) background queue.

For use with [Haystack](http://haystacksearch.org) version 2.0+.

## Requirements

* Django 1.3+
* [Haystack 2.0.X](http://github.com/toastdriven/django-haystack)
* [RQ](http://python-rq.org)
* [django-rq](http://github.com/ui/django-rq)

You also need to install your choice of one of the supported search engines for
Haystack and have properly configured Redis and `django-rq`.

## Setup

1. Just make shure the `haystack_rqueue` directory is available in your `PYTHON_PATH`. The prefered way is to run `pip install http://github.com/mandx/haystack-rqueue/tarball/master`
1. Include this line in your settings module `HAYSTACK_SIGNAL_PROCESSOR = 'haystack_rqueue.signals.RQueueSignalProcessor'`).
1. If you are running Django 1.8+, add `'haystack_rqueue'` to your `INSTALLED_APPS` setting.
1. Configure `django-rq` (see the README) and ensure your Redis instance is running and it's accessible.
1. Start the RQ workers (via `$ ./manage.py rqworker`).
1. Profit!
