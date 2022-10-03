import os

from setuptools import find_packages, setup

from nrrd._version import __version__

currentPath = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the README file
with open(os.path.join(currentPath, 'README.rst')) as fh:
    longDescription = fh.read()

longDescription = '\n' + longDescription

setup(name='pynrrd',
      python_requires='>=3.7',
      version=__version__,
      description='Pure python module for reading and writing NRRD files.',
      long_description=longDescription,
      long_description_content_type='text/x-rst',
      author='Maarten Everts',
      author_email='me@nn8.nl',
      url='https://github.com/mhe/pynrrd',
      license='MIT License',
      install_requires=['numpy>=1.11.1', 'nptyping', 'typing_extensions'],
      packages=find_packages(exclude=['*.tests', '*.tests.*', 'tests.*', 'tests']),
      keywords='nrrd teem image processing file format',
      classifiers=[
          'License :: OSI Approved :: MIT License',
          'Topic :: Scientific/Engineering',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
          'Programming Language :: Python :: 3.10',
          'Programming Language :: Python :: 3.11',
      ],
      project_urls={
          'Tracker': 'https://github.com/mhe/pynrrd/issues',
      }
      )
