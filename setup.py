"""Packaging settings."""


from codecs import open
from os.path import abspath, dirname, join
from subprocess import call

from setuptools import Command, find_packages, setup

from autoversion import __version__


this_dir = abspath(dirname(__file__))
with open(join(this_dir, 'README.md'), encoding='utf-8') as file:
    try:
        import pypandoc
        long_description = pypandoc.convert_text(file.read(), 'rst', format='md')
    except (IOError, ImportError):
        long_description = ''

class RunTests(Command):
    """Run all tests."""
    description = 'run tests'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        errno = call(['py.test', '--cov=autoversion', '--cov-report=term-missing'])
        raise SystemExit(errno)

setup(
    name = 'autoversion',
    version = __version__,
    description = 'A Python tool for semantic versioning and changelog generation based on source control conventional commits.',
    long_description = long_description,
    url = 'https://github.com/peetonn/autoversion',
    author = 'Peter Gusev',
    author_email = 'peter@gusev.io',
    license = 'UNLICENSED',
    classifiers = [
        'Intended Audience :: Developers',
        'Topic :: Utilities',
        'License :: Public Domain',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    keywords = 'semver conventional-commits changelog',
    packages = find_packages(exclude=['docs', 'tests*']),
    install_requires = ['docopt', 'semver', 'mistletoe'],
    extras_require = {
       'test': ['coverage', 'pytest', 'pytest-cov'],
    },
    entry_points = {
        'console_scripts': [
            'autoversion=autoversion.cli:main',
        ],
    },
    cmdclass = {'test': RunTests},
)
