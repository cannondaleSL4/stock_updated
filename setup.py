from setuptools import setup

setup(name='application',
      version='0.1.0',
      packages=['application'],
      entry_points={
          'console_scripts': [
              'application = application.__main__:main'
          ]
      },
)