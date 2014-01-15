#!/usr/bin/python3
import os
from setuptools import setup
from setuptools import find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='stanza',
      packages=find_packages(),
      version='0.1',
      description='A lyric viewer and media player controller',
      author='Harvey Hunt',
      url='https://github.com/HarveyHunt/stanza',
      author_email='harveyhuntnexus@gmail.com',
      license="GPLv3",
      keywords="python urwid music player lyrics metadata cmus mpd customisation",
      install_requires=[],
      long_description=read('README.md'),
      entry_points={'console_scripts': ['stanza=stanza.main:main']})
