# -*- coding: utf-8 -*-
from setuptools import setup
try:  # Pour pip >= 10
    from pip._internal.req import parse_requirements
except ImportError:  # For pip <= 9
    from pip.req import parse_requirements

# Based on http://peterdowns.com/posts/first-time-with-pypi.html

__version__ = '0.0.7'  # Should match with __init.py__
_NAME = 'revolut'
_PACKAGE_LIST = ['revolut', 'revolut_bot']
_URL_GITHUB = 'https://github.com/tducret/revolut-python'
_DESCRIPTION = 'Package to get account balances and do operations on Revolut'
_MOTS_CLES = ['api', 'revolut', 'bank', 'parsing', 'cli',
              'python-wrapper', 'scraping', 'scraper', 'parser']
_SCRIPTS = ['revolut_cli.py', 'revolutbot.py']
# To delete here + 'scripts' dans setup()
# if no command is used in the package

install_reqs = parse_requirements('requirements.txt', session='hack')
requirements = [str(ir.req) for ir in install_reqs]

setup(
    name=_NAME,
    packages=_PACKAGE_LIST,
    package_data={},
    scripts=_SCRIPTS,
    version=__version__,
    license='MIT',
    platforms='Posix; MacOS X',
    description=_DESCRIPTION,
    long_description=_DESCRIPTION,
    author='Thibault Ducret',
    author_email='thibault.ducret@gmail.com',
    url=_URL_GITHUB,
    download_url='%s/tarball/%s' % (_URL_GITHUB, __version__),
    keywords=_MOTS_CLES,
    setup_requires=requirements,
    install_requires=requirements,
    classifiers=['Programming Language :: Python :: 3'],
    python_requires='>=3',
    tests_require=['pytest'],
)

# ------------------------------------------
# To upload a new version on pypi
# ------------------------------------------
# Make sure everything was pushed (with a git status)
# (or git commit --am "Comment" and git push)
# export VERSION=0.0.7; git tag $VERSION -m "Code quality improvements (thanks @haakonvt)"; git push --tags

# If you need to delete a tag
# git push --delete origin $VERSION; git tag -d $VERSION
