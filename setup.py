#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import codecs
from setuptools import setup


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding="utf-8").read()


setup(
    name="pytest-it",
    version="0.1",
    description="Display pytest test reports as a plaintext spec, inspired by RSpec",
    long_description=read("README.md"),
    author="Matt Duck",
    author_email="matt@mattduck.com",
    maintainer="Matt Duck",
    maintainer_email="matt@mattduck.com",
    url="https://github.com/Ometria/pytest-it",
    keywords="pytest pytest-it test bdd rspec org-mode",
    license="MIT",
    python_requires=">=2.7",
    install_requires=["pytest>=3.6.0"],
    packages=["pytest_it"],
    entry_points={"pytest11": ["it = pytest_it.plugin"]},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Pytest",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
    ],
)
