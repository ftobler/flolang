from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='flolang',
    version='0.1.0',
    description='programming language project',
    long_description=readme,
    author='Florin Tobler',
    author_email='florin.tobler@hotmail.com',
    url='https://github.com/ftobler/flolang',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=[
        "colorama>=0.4.6"
        # Add your dependencies here.
        # example:
        # 'numpy>=1.21.0,<2.0.0',
    ],
    entry_points={
        'console_scripts': [
            'flolang=flolang.main:main_func',
            # a^      b^     c^   d^
            # a => the command line argument
            # b => the package name
            # c => the file name in the package (same as imports)
            # d => the function to call
        ],
    },
)