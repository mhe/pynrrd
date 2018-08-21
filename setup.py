import os

from setuptools import setup, find_packages

from nrrd._version import __version__

currentPath = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the README file
with open(os.path.join(currentPath, 'README.rst'), 'r') as f:
    longDescription = f.read()

longDescription = '\n' + longDescription

setup(name='pynrrd',
      version=__version__,
      description='Pure python module for reading and writing NRRD files.',
      long_description=longDescription,
      long_description_content_type='text/x-rst',
      author='Maarten Everts',
      author_email='me@nn8.nl',
      url='https://github.com/mhe/pynrrd',
      license='MIT License',
      install_requires=['numpy>=1.11.1'],
      packages=find_packages(),
      package_data={
          'nrrd': ['tests/*']
      },
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
