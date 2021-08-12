# =============================================================================
#            __     ___   _ ____  _     __  __           _      _
#  _ __  _   \ \   / / | | |  _ \| |   |  \/  | ___   __| | ___| |
# | '_ \| | | \ \ / /| |_| | | | | |   | |\/| |/ _ \ / _` |/ _ \ |
# | |_) | |_| |\ V / |  _  | |_| | |___| |  | | (_) | (_| |  __/ |
# | .__/ \__, | \_/  |_| |_|____/|_____|_|  |_|\___/ \__,_|\___|_|
# |_|    |___/
# =============================================================================
# Authors:            Patrick Lehmann
#
# Package installer:  An abstract VHDL language model.
#
# License:
# ============================================================================
# Copyright 2017-2021 Patrick Lehmann - Boetzingen, Germany
# Copyright 2016-2017 Patrick Lehmann - Dresden, Germany
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#		http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0
# ============================================================================
#
from pathlib    import Path
from setuptools import setup as setuptools_setup, find_packages as setuptools_find_packages

gitHubNamespace = "vhdl"
projectName =     "pyVHDLModel"

# Read README for upload to PyPI
readmeFile = Path("README.md")
with readmeFile.open("r") as file:
	long_description = file.read()

# Read requirements file and add them to package dependency list
requirementsFile = Path("requirements.txt")
with requirementsFile.open("r") as file:
	requirements = [line for line in file.readlines()]

# Derive URLs
sourceCodeURL =     "https://github.com/{namespace}/{projectName}".format(namespace=gitHubNamespace, projectName=projectName)
documentationURL =  "https://{namespace}.github.io/{projectName}".format(namespace=gitHubNamespace, projectName=projectName)

# Assemble all package information
setuptools_setup(
	name=projectName,
	version="0.11.4",

	author="Patrick Lehmann",
	author_email="Paebbels@gmail.com",
	# maintainer="Patrick Lehmann",
	# maintainer_email="Paebbels@gmail.com",
  license='Apache 2.0',

	description="An abstract VHDL language model.",
	long_description=long_description,
	long_description_content_type="text/markdown",

	url=sourceCodeURL,
	project_urls={
		'Documentation': documentationURL,
		'Source Code':   sourceCodeURL,
		'Issue Tracker': sourceCodeURL + "/issues"
	},
	# download_url="https://github.com/vhdl/pyVHDLModel/tarball/0.1.0",

	packages=setuptools_find_packages(exclude=["tests", "tests.*",]),
	classifiers=[
		"License :: OSI Approved :: Apache Software License",
		"Operating System :: OS Independent",
		"Programming Language :: Python :: 3 :: Only",
		"Programming Language :: Python :: 3.6",
		"Programming Language :: Python :: 3.7",
		"Programming Language :: Python :: 3.8",
		"Programming Language :: Python :: 3.9",
   "Development Status :: 4 - Beta",
#		"Development Status :: 5 - Production/Stable",
		"Intended Audience :: Developers",
		"Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)",
		"Topic :: Software Development :: Code Generators",
		"Topic :: Software Development :: Compilers",
		"Topic :: Utilities"
	],
	keywords="Python3 VHDL Language Model Abstract",

	python_requires='>=3.6',
	install_requires=requirements,
)
