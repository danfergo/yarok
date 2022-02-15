from setuptools import setup, find_packages


# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='yarok',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    version='0.0.1',
    description='YAROK - Yet another robot framework',
    author='danfergo',
    entry_points={
        'console_scripts': [
            'yarok = yarok.__main__:main'
        ],
    },
    # scripts=['bin/lidaco'],
    author_email='danfergo@gmail.com',
    url='https://github.com/danfergo/yarok',  # use the URL to the github repo
    # download_url='https://github.com/e-WindLidar/Lidaco/archive/v0.0.1.tar.gz',
    keywords=['yarok', 'robot', 'framework', 'mujoco'],  # arbitrary keywords
    classifiers=[],
    install_requires=[
        # 'pyyaml',
    ]
)