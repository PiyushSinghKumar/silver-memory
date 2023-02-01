from setuptools import find_namespace_packages, setup

setup(
    name='module_dataalliance',
    version='0.1',
    description='Library with functions for the dataalliance project',
    author='Gonçalo Coutinho',
    author_email='11016322@stud.hochschule-heidelberg.de',
    packages=find_namespace_packages(include=['module_dataalliance*']),
    python_requires=">=3.7, <3.11",
    install_requires=[],
)