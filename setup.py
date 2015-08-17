from distutils.core import setup
setup(name='pynrrd',
      version='0.1',
      description='Pure python module for reading nrrd files.',
      author='Maarten Everts',
      author_email='maarten@bitpuzzle.com',
      url='http://github.com/mhe/pynrrd',
      py_modules=['nrrd'],
      install_requires=['numpy'],
      )
