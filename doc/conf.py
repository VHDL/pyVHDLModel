# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
from importlib.util import find_spec
from sys import path as sys_path
from os.path import abspath
from pathlib import Path
from json import loads

from pyTooling.Packaging import extractVersionInformation

ROOT = Path(__file__).resolve().parent

sys_path.insert(0, abspath("."))
sys_path.insert(0, abspath(".."))
sys_path.insert(0, abspath("../pyVHDLModel"))
# sys_path.insert(0, abspath("_extensions"))


# ==============================================================================
# Project information and versioning
# ==============================================================================
# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
project = "pyVHDLModel"

packageInformationFile = Path(f"../{project.replace('.', '/')}/__init__.py")
versionInformation = extractVersionInformation(packageInformationFile)

author =    versionInformation.Author
copyright = versionInformation.Copyright
version =   ".".join(versionInformation.Version.split(".")[:2])  # e.g. 2.3    The short X.Y version.
release =   versionInformation.Version


# ==============================================================================
# Miscellaneous settings
# ==============================================================================
# The master toctree document.
master_doc = "index"

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = [
	"_build",
	"_theme",
	"Thumbs.db",
	".DS_Store"
]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "manni"


# ==============================================================================
# Restructured Text settings
# ==============================================================================
prologPath = Path("prolog.inc")
try:
	with prologPath.open("r", encoding="utf-8") as fileHandle:
		rst_prolog = fileHandle.read()
except Exception as ex:
	print(f"[ERROR:] While reading '{prologPath}'.")
	print(ex)
	rst_prolog = ""


# ==============================================================================
# Options for HTML output
# ==============================================================================
html_context = {}
ctx = ROOT / "context.json"
if ctx.is_file():
	html_context.update(loads(ctx.open('r').read()))

# ==============================================================================
# Options for HTML output
# ==============================================================================
html_theme = "sphinx_rtd_theme"
html_theme_options = {
	"logo_only": True,
	"vcs_pageview_mode": 'blob',
	"navigation_depth": 5,
}
html_css_files = [
	'css/override.css',
]

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

html_logo = str(Path(html_static_path[0]) / "logo.svg")
html_favicon = str(Path(html_static_path[0]) / "favicon.svg")

# Output file base name for HTML help builder.
htmlhelp_basename = "pyVHDLModelDoc"

# If not None, a 'Last updated on:' timestamp is inserted at every page
# bottom, using the given strftime format.
# The empty string is equivalent to '%b %d, %Y'.
html_last_updated_fmt = "%d.%m.%Y"

# ==============================================================================
# Python settings
# ==============================================================================
modindex_common_prefix = [
	f"{project}."
]

# ==============================================================================
# Options for LaTeX / PDF output
# ==============================================================================
from textwrap import dedent

latex_elements = {
	# The paper size ('letterpaper' or 'a4paper').
	"papersize": "a4paper",

	# The font size ('10pt', '11pt' or '12pt').
	#'pointsize': '10pt',

	# Additional stuff for the LaTeX preamble.
	"preamble": dedent(r"""
		% ================================================================================
		% User defined additional preamble code
		% ================================================================================
		% Add more Unicode characters for pdfLaTeX.
		% - Alternatively, compile with XeLaTeX or LuaLaTeX.
		% - https://GitHub.com/sphinx-doc/sphinx/issues/3511
		%
		\ifdefined\DeclareUnicodeCharacter
			\DeclareUnicodeCharacter{2265}{$\geq$}
			\DeclareUnicodeCharacter{21D2}{$\Rightarrow$}
		\fi


		% ================================================================================
		"""),

	# Latex figure (float) alignment
	#'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
	( master_doc,
		"pyVHDLModel.tex",
		"The pyVHDLModel Documentation",
		"Patrick Lehmann",
		"manual"
	),
]


# ==============================================================================
# Extensions
# ==============================================================================
extensions = [
# Standard Sphinx extensions
	"sphinx.ext.autodoc",
	"sphinx.ext.extlinks",
	"sphinx.ext.intersphinx",
	"sphinx.ext.inheritance_diagram",
	"sphinx.ext.todo",
	"sphinx.ext.graphviz",
	"sphinx.ext.mathjax",
	"sphinx.ext.ifconfig",
	"sphinx.ext.viewcode",
# SphinxContrib extensions
	"sphinxcontrib.mermaid",
# Other extensions
	"sphinx_design",
	"sphinx_copybutton",
	"sphinx_autodoc_typehints",
	"autoapi.sphinx",
	"sphinx_reports",
# User defined extensions
]


# ==============================================================================
# Sphinx.Ext.InterSphinx
# ==============================================================================
intersphinx_mapping = {
	"python": ("https://docs.python.org/3", None),
	"vasg":   ("https://IEEE-P1076.gitlab.io/", None),
	"pyTool": ("https://pyTooling.github.io/pyTooling/", None),
	"ghdl":   ("https://GHDL.github.io/ghdl/", None),
}


# ==============================================================================
# Sphinx.Ext.AutoDoc
# ==============================================================================
# see: https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#configuration
#autodoc_default_options = {
#	"private-members": True,
#	"special-members": True,
#	"inherited-members": True,
#	"exclude-members": "__weakref__"
#}
#autodoc_class_signature = "separated"
autodoc_member_order = "bysource"       # alphabetical, groupwise, bysource
autodoc_typehints = "both"
#autoclass_content = "both"


# ==============================================================================
# Sphinx.Ext.ExtLinks
# ==============================================================================
extlinks = {
	"gh":      ("https://GitHub.com/%s", "gh:%s"),
	"ghissue": ("https://GitHub.com/VHDL/pyVHDLModel/issues/%s", "issue #%s"),
	"ghpull":  ("https://GitHub.com/VHDL/pyVHDLModel/pull/%s", "pull request #%s"),
	"ghsrc":   ("https://GitHub.com/VHDL/pyVHDLModel/blob/main/%s", None),
	"wiki":    ("https://en.wikipedia.org/wiki/%s", None),
}


# ==============================================================================
# Sphinx.Ext.Graphviz
# ==============================================================================
graphviz_output_format = "svg"


# ==============================================================================
# SphinxContrib.Mermaid
# ==============================================================================
mermaid_params = [
	'--backgroundColor', 'transparent',
]
mermaid_verbose = True


# ==============================================================================
# Sphinx.Ext.Inheritance_Diagram
# ==============================================================================
inheritance_node_attrs = {
#	"shape": "ellipse",
#	"fontsize": 14,
#	"height": 0.75,
	"color": "dodgerblue1",
	"style": "filled"
}


# ==============================================================================
# Sphinx.Ext.ToDo
# ==============================================================================
# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True
todo_link_only = True


# ==============================================================================
# Sphinx-reports
# ==============================================================================
report_dep_dependencies = {
	"src":     ["../requirements.txt"],
	"doc":     ["requirements.txt"],
	"unit":    ["../tests/unit/requirements.txt"],
	"build":   ["../build/requirements.txt"],
	"publish": ["../dist/requirements.txt"],
}

_coverageLevels = {
	30:      {"class": "report-cov-below30",  "desc": "almost undocumented"},
	50:      {"class": "report-cov-below50",  "desc": "poorly documented"},
	80:      {"class": "report-cov-below80",  "desc": "roughly documented"},
	90:      {"class": "report-cov-below90",  "desc": "well documented"},
	100:     {"class": "report-cov-below100", "desc": "excellent documented"},
	"error": {"class": "report-cov-error",    "desc": "internal error"},
}

report_unittest_testsuites = {
	"src":   {"xml_report": "../report/unit/TestReportSummary.xml"},
}
report_codecov_packages = {
	"src": {
		"name":        "pyVHDLModel",
		"json_report": "../report/coverage/coverage.json",
		"fail_below":  80,
		"levels":      _coverageLevels
	}
}
report_doccov_packages = {
	"src": {
		"name":       "pyVHDLModel",
		"directory":  "../pyVHDLModel",
		"fail_below": 80,
		"levels":     _coverageLevels
	}
}


# ==============================================================================
# Sphinx_Design
# ==============================================================================
sd_fontawesome_latex = True


# ==============================================================================
# AutoAPI.Sphinx
# ==============================================================================
autoapi_modules = {
	project: {
		"template": "module",
		"output":   project,
		"override": True
	}
}

# for directory in [mod for mod in Path(f"../{project}").iterdir() if mod.is_dir() and mod.name != "__pycache__"]:
# 	print(f"Adding module rule for '{project}.{directory.name}'")
# 	autoapi_modules[f"{project}.{directory.name}"] = {
# 		"template": "module",
# 		"output":   project,
# 		"override": True
# 	}
