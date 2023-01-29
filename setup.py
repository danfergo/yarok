from setuptools import setup, find_packages

# read the contents of your README file
from os import path
from yarok import __VERSION__

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='yarok',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(
        # exclude=["yarok/comm", "yarok/comm.*"]
    ),
    include_package_data=True,
    version=__VERSION__,
    description='YAROK - Yet another robot framework',
    author='danfergo',
    entry_points={
        'console_scripts': [
            'yarok = yarok.__main__:main'
        ],
    },
    author_email='danfergo@gmail.com',
    url='https://github.com/danfergo/yarok',
    keywords=['yarok', 'robot', 'framework', 'mujoco'],
    classifiers=[],
    install_requires=[
        'mujoco',
        'mujoco-python-viewer'
    ]
)
