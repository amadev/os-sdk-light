#!/usr/bin/env python

from setuptools import setup, find_packages
setup(
    name="os-sdk-light",
    version="0.1.0",
    packages=find_packages(),
    # metadata for upload to PyPI
    author="Andrey Volkov",
    author_email="amadev@mail.ru",
    description="Simple library for analytics",
    license="MIT",
    keywords="openstack client swagger openapi",
    url="https://github.com/amadev/os-sdk-light",
    install_requires=[
        'os-client-config',
        'bravado',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities',
        'Topic :: Scientific/Engineering :: Information Analysis',
    ],
    include_package_data=True,
)
