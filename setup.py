# -*- coding: utf-8 -*-

from setuptools import setup


def install_data_files_hack():
    # This is a clever hack to circumvent distutil's data_files
    # policy "install once, find never". Definitely a TODO!
    # -- https://groups.google.com/group/comp.lang.python/msg/2105ee4d9e8042cb
    from distutils.command.install import INSTALL_SCHEMES
    for scheme in INSTALL_SCHEMES.values():
        scheme['data'] = scheme['purelib']


install_data_files_hack()

requires = ['pygments', 'dulwich>=0.8.6', 'Django>=1.4']

try:
    import argparse  # not available for Python 2.6
except ImportError:
    requires.append('argparse')


setup(
    name='django-klaus',
    version='0.1.1',
    author='Marcin Biernat, Jonas Haag',
    author_email='mb@marcinbiernat.pl, jonas@lophus.org',
    packages=['klaus'],
    include_package_data=True,
    zip_safe=False,
    url='https://github.com/biern/django-klaus',
    description='Git web viewer app for django.',
    long_description=__doc__,
    classifiers=[
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "Topic :: Software Development :: Version Control",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: ISC License (ISCL)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
    ],
    install_requires=requires,
)
