try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='pynrrd',
      version='0.2.0',
      description='Pure python module for reading and writing nrrd files.',
      long_description='Pure python module for reading and writing nrrd files. See the github page for more information.',
      author='Maarten Everts',
      author_email='me@nn8.nl',
      url='http://github.com/mhe/pynrrd',
      py_modules=['nrrd'],
      license="MIT License",
      install_requires=['numpy'],
      keywords = ["nrrd"],
      classifiers = [
          "License :: OSI Approved :: MIT License",
          "Topic :: Scientific/Engineering",
          "Programming Language :: Python",
          "Programming Language :: Python :: 3"
      ]
      )
