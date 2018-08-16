try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
import os

currentPath = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the README file
with open(os.path.join(currentPath, 'README.md'), 'r') as f:
    long_description = f.read()

long_description = '\n' + long_description

setup(name='pynrrd',
      version='0.2.4',
      description='Pure python module for reading and writing NRRD files.',
      long_description=long_description,
      author='Maarten Everts',
      author_email='me@nn8.nl',
      url='https://github.com/mhe/pynrrd',
      py_modules=['nrrd'],
      license='MIT License',
      install_requires=['numpy'],
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
          'Source': 'https://github.com/mhe/pynrrd',
          'Tracker': 'https://github.com/mhe/pynrrd/issues',
      }
      )
