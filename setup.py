# EMACS settings: -*-  tab-width: 2; indent-tabs-mode: t -*-
# vim: tabstop=2:shiftwidth=2:noexpandtab
# kate: tab-width 2; replace-tabs off; indent-width 2;
# =============================================================================
#             __     ___   _ ____  _     __  __           _      _
#   _ __  _   \ \   / / | | |  _ \| |   |  \/  | ___   __| | ___| |
#  | '_ \| | | \ \ / /| |_| | | | | |   | |\/| |/ _ \ / _` |/ _ \ |
#  | |_) | |_| |\ V / |  _  | |_| | |___| |  | | (_) | (_| |  __/ |
#  | .__/ \__, | \_/  |_| |_|____/|_____|_|  |_|\___/ \__,_|\___|_|
#  |_|    |___/
# =============================================================================
# Authors:            Patrick Lehmann
#
# Package installer:  An abstract VHDL language model.
#
# License:
# ============================================================================
# Copyright 2017-2020 Patrick Lehmann - Boetzingen, Germany
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
import setuptools

with open("README.md", "r") as file:
	long_description = file.read()

requirements = []
with open("requirements.txt") as file:
	for line in file.readlines():
		requirements.append(line)

projectName = "pyVHDLModel"

github_url =  "https://github.com/vhdl/" + projectName
rtd_url =     "https://" + projectName + ".readthedocs.io/en/latest/"

setuptools.setup(
	name=projectName,
	version="0.7.1",

	author="Patrick Lehmann",
	author_email="Paebbels@gmail.com",
	# maintainer="Patrick Lehmann",
	# maintainer_email="Paebbels@gmail.com",

	description="An abstract VHDL language model.",
	long_description=long_description,
	long_description_content_type="text/markdown",

	url=github_url,
	project_urls={
		'Documentation': rtd_url,
		'Source Code':   github_url,
		'Issue Tracker': github_url + "/issues"
	},
	# download_url="https://github.com/vhdl/pyVHDLModel/tarball/0.1.0",

	packages=setuptools.find_packages(),
	# entry_points={
	# 	'console_scripts': [
	# 		"VHDLParser = pyVHDLParser.CLI.VHDLParser:main"
	# 	]
	# },
	classifiers=[
		"License :: OSI Approved :: Apache Software License",
		"Operating System :: OS Independent",
		"Programming Language :: Python :: 3 :: Only",
		"Programming Language :: Python :: 3.8",
   "Development Status :: 3 - Alpha",
#		"Development Status :: 5 - Production/Stable",
		"Intended Audience :: Developers",
		"Topic :: Utilities"
	],
	keywords="Python3 VHDL Language Model Abstract",

	python_requires='>=3.8',
	install_requires=requirements,
	# provides=
	# obsoletes=
)
