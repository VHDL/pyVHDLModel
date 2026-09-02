# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
from sys      import path as sys_path
from os.path  import abspath
from pathlib  import Path
from json     import loads
from textwrap import dedent

from pyTooling.Packaging import extractVersionInformation

# ==============================================================================
# Project configuration
# ==============================================================================
githubNamespace = "VHDL"
githubProject = pythonProject = "pyVHDLModel"
directoryName = pythonProject.replace('.', '/')


# ==============================================================================
# Project paths
# ==============================================================================
ROOT = Path(__file__).resolve().parent

sys_path.insert(0, abspath("."))
sys_path.insert(0, abspath(".."))
sys_path.insert(0, abspath(f"../{directoryName}"))


# ==============================================================================
# Project information and versioning
# ==============================================================================
# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
packageInformationFile = Path(f"../{directoryName}/__init__.py")
versionInformation = extractVersionInformation(packageInformationFile)

project =   pythonProject
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
htmlhelp_basename = f"{project}Doc"

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
latex_engine = "lualatex"
latex_use_xindy = False
latex_elements = {
	"papersize":   "a4paper",      # The paper size ('letterpaper' or 'a4paper').
	"pointsize":   "10pt",         # The font size ('10pt', '11pt' or '12pt').
	"inputenc":    "",             # Let LuaLaTeX handle input encoding
	"utf8extra":   "",
	"polyglossia": "",
	"babel":      r"\usepackage[english]{babel}",
	"fontenc":    r"\usepackage{fontspec}",  # Disable the default T1 font encoding (Essential for LuaLaTeX)
	"fontpkg":    dedent("""\
		\\usepackage[fontfamily=libertinus]{pytooling}
	"""),
	"passoptionstopackages": dedent("""\
		\\PassOptionsToPackage{verbatimvisiblespace=\\ }{sphinx}
	"""),
# "sphinxsetup": "verbatimvisiblespace=\\textvisiblespace"
# "figure_align": "htbp",     # Latex figure (float) alignment
	"makeindex":  r"\usepackage[columns=1]{idxlayout}\makeindex",
	"printindex": r"\def\twocolumn[#1]{#1}\printindex",
}

# WORKAROUND: Python <3.12
#   Reusing the f-string's own quote character inside its expression - and a backslash in it - both need PEP 701.
#   The escaped project name is built first, so this file still parses on Python 3.11.
#   Replace by inlining it again:
#     f"The {pythonProject.replace("_", r"\_")} Documentation",
latexProject = pythonProject.replace("_", r"\_")

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
	( master_doc,
		f"{pythonProject}.tex",
		f"The {latexProject} Documentation",
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
	"pyTool": ("https://pyTooling.github.io/pyTooling/", None),
	"vasg":   ("https://IEEE-P1076.gitlab.io/", None),
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
	"gh":          (f"https://GitHub.com/%s", "%s"),
	"ghissue":     (f"https://GitHub.com/{githubNamespace}/{project}/issues/%s", "issue #%s"),
	"ghpull":      (f"https://GitHub.com/{githubNamespace}/{project}/pull/%s", "pull request #%s"),
	"ghsrc":       (f"https://GitHub.com/{githubNamespace}/{project}/blob/main/%s", None),
	"pypi":        ("https://PyPI.org/project/%s", "%s"),
	"wiki":        (f"https://en.wikipedia.org/wiki/%s", None),
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

report_unittest_testsuites = {
	"src": {
		"name":        f"{project}",
		"xml_report":  "../report/unit/unittest.xml",
	}
}
report_codecov_packages = {
	"src": {
		"name":        f"{project}",
		"json_report": "../report/coverage/coverage.json",
		"fail_below":  80,
		"levels":      "default"
	}
}
report_doccov_packages = {
	"src": {
		"name":       f"{project}",
		"directory":  f"../{directoryName}",
		"fail_below": 80,
		"levels":     "default"
	}
}


# ==============================================================================
# Sphinx_Design
# ==============================================================================
# sd_fontawesome_latex = True


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
