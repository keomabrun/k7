import os
from setuptools import setup

HERE = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the README file
with open(os.path.join(HERE, 'README.md'), 'r') as f:
    long_description = f.read()

setup(
    name='k7',
    version='0.0.5',
    description='Manipulate k7 files with one hand',
    long_description=long_description,
    url='http://github.com/keomabrun/k7',
    author='Keoma Brun-Laguna',
    author_email='contact@kbl.netlib.re',
    classifiers=[
        'Programming Language :: Python :: 2.7',
    ],
    license='GPL',
    packages=['k7'],
    install_requires=['pandas'],
    package_data={
        'samples': ['sample.k7', 'sample.k7.gz'],
        },
    )
