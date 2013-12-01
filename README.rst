django-klaus - port of klaus Git web viewer to django
=====================================================

`Klaus <http://github.com/jonashaag/klaus>`_ is a simple Git web viewer that Just Works™ originally created by Jonas Haag, written in Flask.

If you need just to host a standalone Git web viewer, then check out the `original <http://github.com/jonashaag/klaus>`_ which makes it easier. On the other hand, if you need to integrate a Git viewer with a django application, then this is a way to go!


Dependencies
------------

 - ``dulwich`` is used to handle git repositories along with ``pygments`` to highlight the results.

 - ``ReST`` and ``Markdown`` rendering is supported if ``docutils`` / ``markdown`` is available


Installation
------------

::

    pip install django-klaus


in settings.py:
::

    INSTALLED_APPS = (
        (...),
        'klaus'
    )

in urls.py:
::

    url(r'^klaus/', include('klaus.urls', namespace='klaus'))


Configuration
-------------

In ``settings.py`` set ``KLAUS_REPO_PATHS`` to list of paths to repositories you would like to list.

::

    KLAUS_REPO_PATHS = ['/path/to/git/repo/']


Repositories can be also managed dynamically using ``klaus.repo.RepoManager`` class.


For extra information reference the `original <http://github.com/jonashaag/klaus>`_
