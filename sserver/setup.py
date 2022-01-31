from setuptools import find_packages, setup

long_description = ''
with open('README.md', 'r') as readme:
    long_description = readme.read()

setup(
    name='SServer',
    version='1.0',
    description='Python Simple Server',
    long_description=long_description,
    author='Aaron Boult',
    author_email='sserver@aaronboult.com',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: GNU GPLv3',
        'Operating System :: Linux :: Ubuntu',
    ]
)