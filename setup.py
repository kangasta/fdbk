#!/usr/bin/env python3

import setuptools

with open("README.md", "r") as f:
	long_description = f.read()

setuptools.setup(
	name="fdbk",
	version="1.0.5",
	author="Toni Kangas",
	description="Backend and DB wrapper for feedback collection system",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/kangasta/fdbk",
	packages=setuptools.find_packages(),
	scripts=["bin/fdbk-server"],
	install_requires=[
		"flask",
		"requests"
	],
	classifiers=(
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	)
)
