try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
import os
import re

currentPath = os.path.abspath(os.path.dirname(__file__))


def findVersion(*filePaths):
    with open(os.path.join(currentPath, *filePaths), 'r') as f:
        versionFile = f.read()
        versionMatch = re.search(r'^__version__ = [\'"]([^\'"]*)[\'"]', versionFile, re.M)

        if versionMatch:
            return versionMatch.group(1)

        raise RuntimeError('Unable to find version string.')


# Get the long description from the README file
with open(os.path.join(currentPath, 'README.md'), 'r') as f:
    longDescription = f.read()

longDescription = '\n' + longDescription

setup(name='pynrrd',
      version=findVersion('nrrd.py'),
      description='Pure python module for reading and writing NRRD files.',
      long_description=longDescription,
      long_description_content_type='text/markdown',
      author='Maarten Everts',
      author_email='me@nn8.nl',
      url='https://github.com/mhe/pynrrd',
      py_modules=['nrrd'],
      license='MIT License',
      install_requires=['numpy>=1.11.1'],
      keywords='nrrd teem image processing file format',
      classifiers=[
          'License :: OSI Approved :: MIT License',
          'Topic :: Scientific/Engineering',
          'Programming Language :: Python',
          "Programming Language :: Python :: 2.7",
          'Programming Language :: Python :: 3',
          "Programming Language :: Python :: 3.4",
          "Programming Language :: Python :: 3.5",
          "Programming Language :: Python :: 3.6"
      ],
      project_urls={
          'Tracker': 'https://github.com/mhe/pynrrd/issues',
      }
      )
