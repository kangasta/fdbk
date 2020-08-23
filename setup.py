#!/usr/bin/env python3

import re
import setuptools

with open("fdbk/_version.py", "r") as f:
    try:
        version = re.search(
            r"__version__\s*=\s*[\"']([^\"']+)[\"']",f.read()).group(1)
    except:
        raise RuntimeError('Version info not available')

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="fdbk",
    version=version,
    author="Toni Kangas",
    description="Backend and DB wrapper for feedback collection system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kangasta/fdbk",
    packages=setuptools.find_packages(),
    package_data={
        'fdbk': ['schemas/*.json']
    },
    scripts=["bin/fdbk-server"],
    install_requires=[
        "importlib_resources; python_version<'3.7'",
        "jsonschema",
        "flask",
        "python-dateutil",
        "requests"
    ],
    python_requires='>=3.6',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
