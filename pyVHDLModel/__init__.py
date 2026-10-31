# ==================================================================================================================== #
#             __     ___   _ ____  _     __  __           _      _                                                     #
#   _ __  _   \ \   / / | | |  _ \| |   |  \/  | ___   __| | ___| |                                                    #
#  | '_ \| | | \ \ / /| |_| | | | | |   | |\/| |/ _ \ / _` |/ _ \ |                                                    #
#  | |_) | |_| |\ V / |  _  | |_| | |___| |  | | (_) | (_| |  __/ |                                                    #
#  | .__/ \__, | \_/  |_| |_|____/|_____|_|  |_|\___/ \__,_|\___|_|                                                    #
#  |_|    |___/                                                                                                        #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2017-2026 Patrick Lehmann - Boetzingen, Germany                                                            #
# Copyright 2016-2017 Patrick Lehmann - Dresden, Germany                                                               #
#                                                                                                                      #
# Licensed under the Apache License, Version 2.0 (the "License");                                                      #
# you may not use this file except in compliance with the License.                                                     #
# You may obtain a copy of the License at                                                                              #
#                                                                                                                      #
#   http://www.apache.org/licenses/LICENSE-2.0                                                                         #
#                                                                                                                      #
# Unless required by applicable law or agreed to in writing, software                                                  #
# distributed under the License is distributed on an "AS IS" BASIS,                                                    #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.                                             #
# See the License for the specific language governing permissions and                                                  #
# limitations under the License.                                                                                       #
#                                                                                                                      #
# SPDX-License-Identifier: Apache-2.0                                                                                  #
# ==================================================================================================================== #
#
"""
**An abstract VHDL language model.**

This package provides a unified abstract language model for VHDL. Projects reading from source files can derive own
classes and implement additional logic to create a concrete language model for their tools.

Projects consuming pre-processed VHDL data (parsed, analyzed or elaborated) can build higher level features and services
on such a model, while supporting multiple frontends.

.. admonition:: Copyright Information

   :copyright: Copyright 2017-2026 Patrick Lehmann - Bötzingen, Germany
   :copyright: Copyright 2016-2017 Patrick Lehmann - Dresden, Germany
   :license: Apache License, Version 2.0
"""
from __future__ import annotations

__author__ =            "Patrick Lehmann"
__email__ =             "Paebbels@gmail.com"
__copyright__ =         "2016-2026, Patrick Lehmann"
__license__ =           "Apache License, Version 2.0"
__version__ =           "0.42.0"
# __keywords__ =          []
__project_url__ =       "https://github.com/VHDL/pyVHDLModel"
__documentation_url__ = "https://vhdl.github.io/pyVHDLModel"
__issue_tracker_url__ = "https://GitHub.com/VHDL/pyVHDLModel/issues"


from enum                      import unique, Enum, Flag, auto
from pathlib                   import Path

from typing                    import TYPE_CHECKING, Union, cast, Generator, Optional as Nullable

from pyTooling.Common          import getFullyQualifiedName, getTypeName
from pyTooling.Decorators      import export, readonly
from pyTooling.Graph           import Graph, Vertex, Edge
from pyTooling.Warning         import WarningCollector

from pyVHDLModel.Exception     import VHDLModelException, NotImplementedWarning, BlackboxWarning, \
                                      LibraryExistsInDesignError, LibraryRegisteredToForeignDesignError, \
                                      LibraryNotRegisteredError, EntityExistsInLibraryError, \
                                      ArchitectureExistsInLibraryError, PackageExistsInLibraryError, \
                                      PackageBodyExistsError, ConfigurationExistsInLibraryError, \
                                      ContextExistsInLibraryError, ReferencedLibraryNotExistingError, \
                                      LibraryNotFoundError, EntityNotFoundError, PackageNotFoundError, \
                                      ConfigurationNotFoundError, ContextNotFoundError, AlreadyInDesignError, \
                                      NotAChildError, DuplicateDocumentError, DuplicateDesignUnitError, \
                                      LibraryInUseError
from pyVHDLModel.Base          import ModelEntity, NamedEntityMixin, MultipleNamedEntityMixin, DocumentedEntityMixin
from pyVHDLModel.Expression    import UnaryExpression, BinaryExpression, TernaryExpression
from pyVHDLModel.Namespace     import Namespace
from pyVHDLModel.Object        import Obj, Signal, Constant, DeferredConstant, SharedVariable, Variable, File
from pyVHDLModel.Symbol        import PackageReferenceSymbol, AllPackageMembersReferenceSymbol, \
                                      PackageMemberReferenceSymbol, SimpleObjectOrFunctionCallSymbol
from pyVHDLModel.Common        import AllowBlackboxMixin
from pyVHDLModel.Regions       import ConcurrentDeclarationRegionMixin, SequentialDeclarationRegionMixin, \
                                      ProtectedTypeDeclarationRegionMixin
from pyVHDLModel.Concurrent    import EntityInstantiation, ComponentInstantiation, ConfigurationInstantiation, \
                                      GenerateStatement, IfGenerateStatement, ForGenerateStatement, \
                                      CaseGenerateStatement, GenerateBranch, ConcurrentStatementsMixin, \
                                      ConcurrentBlockStatement
from pyVHDLModel.DesignUnit    import DesignUnit, PrimaryUnit, Architecture, PackageBody, Context, Entity, \
                                      Configuration, Package, Component, UseClause
from pyVHDLModel.PSLModel      import VerificationUnit, VerificationProperty, VerificationMode, PSLEntity
from pyVHDLModel.Instantiation import PackageInstantiation
from pyVHDLModel.Type          import IntegerType, PhysicalType, ArrayType, RecordType, BaseType
from pyVHDLModel.Configuration import ComponentConfiguration
from pyVHDLModel.Declaration   import Alias, Attribute, AttributeSpecification
from pyVHDLModel.Interface     import ModeViewDeclaration
from pyVHDLModel.Subprogram    import Subprogram

if TYPE_CHECKING:
	from pyVHDLModel.Visitor     import Visitor


# Classes of declared items each declarative region accepts (ClassVar _DECLARED_ITEM_TYPES).
ConcurrentDeclarationRegionMixin._DECLARED_ITEM_TYPES = (
	BaseType, Subprogram, Package, PackageBody, Constant, Signal, SharedVariable, File, Alias, Component, Attribute,
	AttributeSpecification, ComponentConfiguration, ModeViewDeclaration, UseClause, PSLEntity
)
Package._DECLARED_ITEM_TYPES = (*ConcurrentDeclarationRegionMixin._DECLARED_ITEM_TYPES, DeferredConstant)
SequentialDeclarationRegionMixin._DECLARED_ITEM_TYPES = (
	BaseType, Subprogram, Package, PackageBody, Constant, Variable, File, Alias, Attribute, AttributeSpecification,
	UseClause
)
ProtectedTypeDeclarationRegionMixin._DECLARED_ITEM_TYPES = (Subprogram, )


@export
@unique
class VHDLVersion(Enum):
	"""
	An enumeration for all possible version numbers for VHDL and VHDL-AMS.

	A version can be given as integer or string and is represented as a unified
	enumeration value.

	This enumeration supports compare operators.
	"""

	Any =                -1  #: Any
	VHDL87 =             87  #: VHDL-1987
	VHDL93 =             93  #: VHDL-1993
	AMS93 =            1993  #: VHDL-AMS-1993
	AMS99 =            1999  #: VHDL-AMS-1999
	VHDL2000 =         2000  #: VHDL-2000
	VHDL2002 =         2002  #: VHDL-2002
	VHDL2008 =         2008  #: VHDL-2008
	AMS2017 =          2017  #: VHDL-AMS-2017
	VHDL2019 =         2019  #: VHDL-2019
	Latest =          10000  #: Latest VHDL (2019)

	__VERSION_MAPPINGS__: dict[Union[int, str], Enum] = {
		-1:       Any,
		87:       VHDL87,
		93:       VHDL93,
		# 93:       AMS93,
		99:       AMS99,
		0:        VHDL2000,
		2:        VHDL2002,
		8:        VHDL2008,
		17:       AMS2017,
		19:       VHDL2019,
		1987:     VHDL87,
		# 1993:     VHDL93,
		1993:     AMS93,
		1999:     AMS99,
		2000:     VHDL2000,
		2002:     VHDL2002,
		2008:     VHDL2008,
		2017:     AMS2017,
		2019:     VHDL2019,
		10000:    Latest,
		"Any":    Any,
		"87":     VHDL87,
		"93":     VHDL93,
		# "93":     AMS93,
		"99":     AMS99,
		"00":     VHDL2000,
		"02":     VHDL2002,
		"08":     VHDL2008,
		"17":     AMS2017,
		"19":     VHDL2019,
		"1987":   VHDL87,
		# "1993":   VHDL93,
		"1993":   AMS93,
		"1999":   AMS99,
		"2000":   VHDL2000,
		"2002":   VHDL2002,
		"2008":   VHDL2008,
		"2017":   AMS2017,
		"2019":   VHDL2019,
		"Latest": Latest,
	}  #: Dictionary of VHDL and VHDL-AMS year codes variants as integer and strings for mapping to unique enum values.

	def __init__(self, *_) -> None:
		"""Patch the embedded MAP dictionary"""
		for k, v in self.__class__.__VERSION_MAPPINGS__.items():
			if (not isinstance(v, self.__class__)) and (v == self.value):
				self.__class__.__VERSION_MAPPINGS__[k] = self

	@classmethod
	def Parse(cls, value: Union[int, str]) -> VHDLVersion:
		"""
		Parses a VHDL or VHDL-AMS year code as integer or string to an enum value.

		:param value:       VHDL/VHDL-AMS year code.
		:returns:           Enumeration value.
		:raises ValueError: If the year code is not recognized.
		"""
		try:
			return cls.__VERSION_MAPPINGS__[value]
		except KeyError:
			raise ValueError(f"Value '{value!s}' cannot be parsed to member of {cls.__name__}.")

	def __lt__(self, other: Any) -> bool:
		"""
		Compare two VHDL/VHDL-AMS versions if the version is less than the second operand.

		:param other:      Parameter to compare against.
		:returns:          True if version is less than the second operand.
		:raises TypeError: If parameter ``other`` is not of type :class:`VHDLVersion`.
		"""
		if isinstance(other, VHDLVersion):
			return self.value < other.value
		else:
			ex = TypeError("Second operand is not of type 'VHDLVersion'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

	def __le__(self, other: Any) -> bool:
		"""
		Compare two VHDL/VHDL-AMS versions if the version is less or equal than the second operand.

		:param other:      Parameter to compare against.
		:returns:          True if version is less or equal than the second operand.
		:raises TypeError: If parameter ``other`` is not of type :class:`VHDLVersion`.
		"""
		if isinstance(other, VHDLVersion):
			return self.value <= other.value
		else:
			ex = TypeError("Second operand is not of type 'VHDLVersion'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

	def __gt__(self, other: Any) -> bool:
		"""
		Compare two VHDL/VHDL-AMS versions if the version is greater than the second operand.

		:param other:      Parameter to compare against.
		:returns:          True if version is greater than the second operand.
		:raises TypeError: If parameter ``other`` is not of type :class:`VHDLVersion`.
		"""
		if isinstance(other, VHDLVersion):
			return self.value > other.value
		else:
			ex = TypeError("Second operand is not of type 'VHDLVersion'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

	def __ge__(self, other: Any) -> bool:
		"""
		Compare two VHDL/VHDL-AMS versions if the version is greater or equal than the second operand.

		:param other:      Parameter to compare against.
		:returns:          True if version is greater or equal than the second operand.
		:raises TypeError: If parameter ``other`` is not of type :class:`VHDLVersion`.
		"""
		if isinstance(other, VHDLVersion):
			return self.value >= other.value
		else:
			ex = TypeError("Second operand is not of type 'VHDLVersion'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

	def __ne__(self, other: Any) -> bool:
		"""
		Compare two VHDL/VHDL-AMS versions if the version is unequal to the second operand.

		:param other:      Parameter to compare against.
		:returns:          True if version is unequal to the second operand.
		:raises TypeError: If parameter ``other`` is not of type :class:`VHDLVersion`.
		"""
		if isinstance(other, VHDLVersion):
			return self.value != other.value
		else:
			ex = TypeError("Second operand is not of type 'VHDLVersion'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

	def __eq__(self, other: Any) -> bool:
		"""
		Compare two VHDL/VHDL-AMS versions if the version is equal to the second operand.

		:param other:      Parameter to compare against.
		:returns:          True if version is equal to the second operand.
		:raises TypeError: If parameter ``other`` is not of type :class:`VHDLVersion`.
		"""
		if isinstance(other, VHDLVersion):
			if (self is self.__class__.Any) or (other is self.__class__.Any):
				return True
			else:
				return self.value == other.value
		else:
			ex = TypeError("Second operand is not of type 'VHDLVersion'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

	def __hash__(self) -> int:
		"""
		Return the hash of the VHDL version using the underlying version number.

		.. note::

		   ``Any`` compares equal to every other member (see :meth:`__eq__`), which no hash value can satisfy
		   simultaneously for all members without collapsing every member to the same hash. This implementation
		   hashes by ``self.value``, which is internally consistent for all comparisons *except* those
		   involving ``Any`` - avoid using ``Any`` as a dict key or set member.

		:returns: Hash value of the underlying VHDL version number.
		"""
		return hash(self.value)

	@readonly
	def IsVHDL(self) -> bool:
		"""
		Check if the version is a VHDL (not VHDL-AMS) version.

		:returns: ``True``, if the version is a VHDL version.
		"""
		return self in (self.VHDL87, self.VHDL93, self.VHDL2002, self.VHDL2008, self.VHDL2019)

	@readonly
	def IsAMS(self) -> bool:
		"""
		Check if the version is a VHDL-AMS (not VHDL) version.

		:returns: ``True``, if the version is a VHDL-AMS version.
		"""
		return self in (self.AMS93, self.AMS99, self.AMS2017)

	def __str__(self) -> str:
		"""
		Formats the VHDL version to pattern ``VHDL'xx`` or in case of VHDL-AMS to ``VHDL-AMS'xx``.

		:returns: Formatted VHDL/VHDL-AMS version.
		"""
		if self.value == self.Any.value:
			return "VHDL'Any"
		elif self.value == self.Latest.value:
			return "VHDL'Latest"

		year = str(self.value)[-2:]
		if self.IsVHDL:
			return f"VHDL'{year}"
		else:
			return f"VHDL-AMS'{year}"

	def __repr__(self) -> str:
		"""
		Formats the VHDL/VHDL-AMS version to pattern ``xxxx``.

		:returns: Formatted VHDL/VHDL-AMS version.
		"""
		if self.value == self.Any.value:
			return "Any"
		elif self.value == self.Latest.value:
			return "Latest"
		else:
			return str(self.value)


@export
class IEEEFlavor(Flag):
	"""
	The ``IEEE`` VHDL library as a fixed set of predefined VHDL packages according to IEEE Std. 1076.

	Nonetheless, some vendors decided to sneak in additional packages into the ``IEEE`` namespace. |br|
	Supported flavors are:

	* ``Synopsys``
	* ``MentorGraphics``

	In addition, IEEE Std. 1076.X extensions can be loaded. |br|
	Supported extensions are:

	* ``WithVITAL`` - IEEE Std. 1076.4

	"""
	Unknown = 0         #: Unknown IEEE flavor
	IEEE = 1            #: IEEE Std. 1076 compliant list of IEEE packages.
	Synopsys = 2        #: Additional packages created by Synopsys are visible within the IEEE library.
	MentorGraphics = 4  #: Additional packages created by Mentor Graphics are visible within the IEEE library.
	WithVITAL = 32      #: Additionally load IEEE Std 1076.4 VITAL packages. (VITAL = VHDL Initiative Towards ASIC Libraries)


@export
@unique
class ObjectClass(Enum):
	"""
	An ``ObjectClass`` is an enumeration and represents an object's class (``constant``, ``signal``, ...).

	In case no *object class* is defined, ``Default`` is used, so the *object class* is inferred from context.
	"""

	Default =    0  #: Object class not defined, thus it's context dependent.
	Constant =   1  #: Constant
	Variable =   2  #: Variable
	Signal =     3  #: Signal
	File =       4  #: File
	Type =       5  #: Type
	# FIXME: Package?
	Procedure =  6  #: Procedure
	Function =   7  #: Function

	def __str__(self) -> str:
		"""
		Formats the object class.

		:returns: Formatted object class.
		"""
		return ("", "constant", "variable", "signal", "file", "type", "procedure", "function")[cast(int, self.value)]       # TODO: check performance


@export
@unique
class DesignUnitKind(Flag):
	"""
	A ``DesignUnitKind`` is an enumeration and represents the kind of design unit (``Entity``, ``Architecture``, ...).

	"""
	Context = auto()                                                             #: Context
	Package = auto()                                                             #: Package
	PackageBody = auto()                                                         #: Package Body
	Entity = auto()                                                              #: Entity
	Architecture = auto()                                                        #: Architecture
	Configuration = auto()                                                       #: Configuration

	Primary = Context | Configuration | Entity | Package                         #: List of primary design units.
	Secondary = PackageBody | Architecture                                       #: List of secondary design units.
	WithContext = Configuration | Package | Entity | PackageBody | Architecture  #: List of design units with a context.
	WithDeclaredItems = Package | Entity | PackageBody | Architecture            #: List of design units having a declaration region.

	All = Primary | Secondary                                                    #: List of all design units.


@export
@unique
class DependencyGraphVertexKind(Flag):
	"""
	A ``DependencyGraphVertexKind`` is an enumeration and represents the kind of vertex in the dependency graph.
	"""
	Document = auto()       #: A document (VHDL source file).
	Library = auto()        #: A VHDL library.

	Context = auto()        #: A context design unit.
	Package = auto()        #: A package design unit.
	PackageBody = auto()    #: A package body design unit.
	Entity = auto()         #: A entity design unit.
	Architecture = auto()   #: A architecture design unit.
	Component = auto()      #: A VHDL component.
	Configuration = auto()  #: A configuration design unit.


@export
@unique
class DependencyGraphEdgeKind(Flag):
	"""
	A ``DependencyGraphEdgeKind`` is an enumeration and represents the kind of edge in the dependency graph.
	"""
	Document =       auto()
	Library =        auto()
	Context =        auto()
	Package =        auto()
	Entity =         auto()
	# Architecture = auto()
	Configuration =  auto()
	Component =      auto()

	DeclaredIn =     auto()
	Order =          auto()
	Reference =      auto()
	Implementation = auto()
	Instantiation =  auto()

	SourceFile =                 Document | DeclaredIn
	CompileOrder =               Document | Order

	LibraryClause =              Library | Reference
	UseClause =                  Package | Reference
	ContextReference =           Context | Reference

	EntityImplementation =       Entity | Implementation
	PackageImplementation =      Package | Implementation

	EntityInstantiation =        Entity | Instantiation
	ComponentInstantiation =     Component | Instantiation
	ConfigurationInstantiation = Configuration | Instantiation

	PackageInstantiation =       Package | Instantiation


@export
@unique
class ObjectGraphVertexKind(Flag):
	"""
	A ``ObjectGraphVertexKind`` is an enumeration and represents the kind of vertex in the object graph.
	"""
	Type =             auto()
	Subtype =          auto()

	Constant =         auto()
	DeferredConstant = auto()
	Variable =         auto()
	Signal =           auto()
	File =             auto()

	Alias =            auto()


@export
@unique
class ObjectGraphEdgeKind(Flag):
	"""
	A ``ObjectGraphEdgeKind`` is an enumeration and represents the kind of edge in the object graph.
	"""
	BaseType = auto()
	Subtype =  auto()

	ReferenceInExpression = auto()


@export
class Design(ModelEntity, AllowBlackboxMixin):
	"""
	A ``Design`` represents set of VHDL libraries as well as all loaded and analysed source files (see :class:`~pyVHDLModel.Document`).

	It's the root of this code document-object-model (CodeDOM). It contains at least one VHDL library (see :class:`~pyVHDLModel.Library`). When the design is
	analysed (see :meth:`Analyze`), multiple graph data structures will be created and populated with vertices and edges. As a first result, the design's compile
	order and hierarchy can be iterated. As a second result, the design's *top-level* is identified and referenced from the design (see :attr:`TopLevel`).

	The *design* contains references to the following graphs:

	* :attr:`DependencyGraph`
	* :attr:`CompileOrderGraph`
	* :attr:`HierarchyGraph`
	* :attr:`ObjectGraph`
	"""
	_name:              Nullable[str]         #: Name of the design.
	_libraries:         dict[str, Library]    #: List of all libraries defined for a design.
	_documents:         list[Document]        #: List of all documents loaded for a design.
	_documentsByPath:   dict[Path, Document]  #: The documents loaded for a design, indexed by path.
	_dependencyGraph:   Graph                 #: The graph of all dependencies in the designs.
	_compileOrderGraph: Graph                 #: A graph derived from dependency graph containing the order of documents for compilation.
	_hierarchyGraph:    Graph                 #: A graph derived from dependency graph containing the design hierarchy.
	_objectGraph:       Graph                 #: The graph of all types and objects in the design.
	_toplevel:          Union[Entity, Configuration]  #: When computed, the toplevel design unit is cached in this field.

	def __init__(
		self,
		name:          Nullable[str] = None,
		allowBlackbox: bool = False
	) -> None:
		"""
		Initialize a VHDL design.

		:param name:          Name of the design.
		:param allowBlackbox: Specify if blackboxes are allowed in this design.
		"""
		super().__init__()
		AllowBlackboxMixin.__init__(self, allowBlackbox)

		self._name = name

		self._libraries =       {}
		self._documents =       []
		self._documentsByPath = {}

		self._compileOrderGraph = Graph()
		self._dependencyGraph = Graph()
		self._hierarchyGraph = Graph()
		self._objectGraph = Graph()
		self._toplevel = None

	@readonly
	def Name(self) -> Nullable[str]:
		"""
		Read-only property to access the design's name (:attr:`_name`).

		:returns: The name of the design.
		"""
		return self._name

	@readonly
	def Libraries(self) -> dict[str, Library]:
		"""
		Read-only property to access the dictionary of library names and VHDL libraries (:attr:`_libraries`).

		:returns: A dictionary of library names and VHDL libraries.
		"""
		return self._libraries

	@readonly
	def Documents(self) -> list[Document]:
		"""
		Read-only property to access the list of all documents (VHDL source files) loaded for this design (:attr:`_documents`).

		:returns: A list of all documents.
		"""
		return self._documents

	@readonly
	def CompileOrderGraph(self) -> Graph:
		"""
		Read-only property to access the compile-order graph (:attr:`_compileOrderGraph`).

		:returns: Reference to the compile-order graph.
		"""
		return self._compileOrderGraph

	@readonly
	def DependencyGraph(self) -> Graph:
		"""
		Read-only property to access the dependency graph (:attr:`_dependencyGraph`).

		:returns: Reference to the dependency graph.
		"""
		return self._dependencyGraph

	@readonly
	def HierarchyGraph(self) -> Graph:
		"""
		Read-only property to access the hierarchy graph (:attr:`_hierarchyGraph`).

		:returns: Reference to the hierarchy graph.
		"""
		return self._hierarchyGraph

	@readonly
	def ObjectGraph(self) -> Graph:
		"""
		Read-only property to access the object graph (:attr:`_objectGraph`).

		:returns: Reference to the object graph.
		"""
		return self._objectGraph

	@readonly
	def TopLevel(self) -> Union[Entity, Configuration]:
		"""
		Read-only property to access the design's *top-level* (:attr:`_toplevel`).

		When called the first time, the hierarchy graph is checked for its root elements. When there is only one root element in the graph, a new field ``toplevel``
		is added to :attr:`_hierarchyGraph` referencing that single element. In addition, the result is cached in :attr:`_toplevel`.

		:returns:                   Reference to the design's *top-level*.
		:raises VHDLModelException: If the hierarchy graph is not yet computed from dependency graph.
		:raises VHDLModelException: If there is more than one *top-level*.
		"""
		# Check for cached result
		if self._toplevel is not None:
			return self._toplevel

		if self._hierarchyGraph.VertexCount == 0:
			raise VHDLModelException("Hierarchy is not yet computed from dependency graph.")

		roots = tuple(self._hierarchyGraph.IterateRoots())
		if len(roots) == 1:
			toplevel = roots[0]
			self._hierarchyGraph["toplevel"] = toplevel
			self._toplevel = toplevel.Value

			return toplevel.Value
		else:
			raise VHDLModelException(f"Found more than one toplevel: {', '.join(str(r) for r in roots)}")

	def LoadStdLibrary(self) -> Library:
		"""
		Load the predefined VHDL library ``std`` into the design.

		This will create a virtual source code file ``std.vhdl`` and register VHDL design units of library ``std`` to that file.

		:returns: The library object of library ``std``.
		"""
		from pyVHDLModel.STD import Std

		doc = Document(Path("std.vhdl"), parent=self)

		library = Std()
		for designUnit in library.IterateDesignUnits():
			doc._AddDesignUnit(designUnit)

		self.AddLibrary(library)

		return library

	def LoadIEEELibrary(self, flavor: Nullable[IEEEFlavor] = None) -> Library:
		"""
		Load the predefined VHDL library ``ieee`` into the design.

		This will create a virtual source code file ``ieee.vhdl`` and register VHDL design units of library ``ieee`` to that file.

		:param flavor: Select the IEEE library flavor: IEEE, Synopsys, MentorGraphics.
		:returns:      The library object of library ``ieee``.
		"""
		from pyVHDLModel.IEEE import Ieee

		doc = Document(Path("ieee.vhdl"), parent=self)

		library = Ieee(flavor)
		for designUnit in library.IterateDesignUnits():
			doc._AddDesignUnit(designUnit)

		self.AddLibrary(library)

		return library

	def AddLibrary(self, library: Library) -> None:
		"""
		Add a VHDL library to the design.

		Ensure the libraries name doesn't collide with existing libraries in the design. |br|
		If ok, set the libraries parent reference to the design.

		:param library:                                Library object to loaded.
		:raises LibraryExistsInDesignError:            If the library already exists in the design.
		:raises LibraryRegisteredToForeignDesignError: If library is already used by a different design.
		"""
		libraryIdentifier = library.NormalizedIdentifier
		if libraryIdentifier in self._libraries:
			raise LibraryExistsInDesignError(library)

		if library._parent is not None:
			raise LibraryRegisteredToForeignDesignError(library)

		self._libraries[libraryIdentifier] = library
		library.Parent = self

	def RemoveLibrary(self, library: Library) -> None:
		"""
		Remove a VHDL library from the design.

		The library is detached: its parent is cleared. Its design units stay design units of the library, so the library
		can be added to a design again (:meth:`AddLibrary`).

		:param library:            The VHDL library to remove.
		:raises ValueError:        If parameter 'library' is ``None``.
		:raises TypeError:         If parameter 'library' is not of type :class:`Library`.
		:raises NotAChildError:    If parameter 'library' is not a library of this design.
		:raises LibraryInUseError: If documents of this design still use the library.

		.. seealso::

		   :meth:`AddLibrary`
		      |rarr| Add a VHDL library to the design.
		   :meth:`RemoveDocument`
		      |rarr| Remove a document from the design.
		"""
		if library is None:
			raise ValueError("Parameter 'library' is None.")
		elif not isinstance(library, Library):
			ex = TypeError("Parameter 'library' is not of type 'Library'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(library)}'.")
			raise ex
		elif self._libraries.get(library._normalizedIdentifier) is not library:
			raise NotAChildError(
				f"Library '{library._identifier}' is not a library of this design.",
				element=library,
				parent=self
			)

		users = tuple(document for document in self._documents if document._library is library)
		if len(users) > 0:
			paths = "', '".join(str(document._path) for document in users)
			ex = LibraryInUseError(
				f"Library '{library._identifier}' is used by {len(users)} document(s).",
				element=library,
				users=users
			)
			ex.add_note(f"Used by: '{paths}'.")
			ex.add_note("Remove the documents from the design first.")
			raise ex

		del self._libraries[library._normalizedIdentifier]
		library._parent = None

	def GetLibrary(self, libraryName: str) -> Library:
		"""
		Return an (existing) VHDL library object of name ``libraryName``.

		If the requested VHDL library doesn't exist, a new VHDL library with that name will be created.

		:param libraryName: Name of the requested VHDL library.
		:returns:           The VHDL library object.
		"""
		libraryIdentifier = libraryName.lower()
		try:
			return self._libraries[libraryIdentifier]
		except KeyError:
			lib = Library(libraryName, parent=self)
			self._libraries[libraryIdentifier] = lib
			lib.Parent = self
			return lib

	def GetEntity(self, libraryName: str, entityName: str) -> Entity:
		"""
		Return the entity named ``entityName`` from the library named ``libraryName``.

		The lookup is case-insensitive. Nothing is created, if the library or entity doesn't exist.

		:param libraryName:           Name of the library containing the entity.
		:param entityName:            Name of the requested entity.
		:returns:                     The entity.
		:raises ValueError:           If parameter 'libraryName' is None or empty.
		:raises TypeError:            If parameter 'libraryName' is not of type :class:`str`.
		:raises ValueError:           If parameter 'entityName' is None or empty.
		:raises TypeError:            If parameter 'entityName' is not of type :class:`str`.
		:raises LibraryNotFoundError: If the library doesn't exist in the design.
		:raises EntityNotFoundError:  If the entity doesn't exist in the library.
		"""
		if libraryName is None:
			raise ValueError("Parameter 'libraryName' is None.")
		elif not isinstance(libraryName, str):
			ex = TypeError("Parameter 'libraryName' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(libraryName)}'.")
			raise ex
		elif libraryName == "":
			raise ValueError("Parameter 'libraryName' is empty.")

		if entityName is None:
			raise ValueError("Parameter 'entityName' is None.")
		elif not isinstance(entityName, str):
			ex = TypeError("Parameter 'entityName' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(entityName)}'.")
			raise ex
		elif entityName == "":
			raise ValueError("Parameter 'entityName' is empty.")

		libraryIdentifier = libraryName.lower()
		if libraryIdentifier not in self._libraries:
			raise LibraryNotFoundError(libraryName)

		library =          self._libraries[libraryIdentifier]
		entityIdentifier = entityName.lower()
		if entityIdentifier not in library._entities:
			raise EntityNotFoundError(entityName, libraryName)

		return library._entities[entityIdentifier]

	def SearchEntity(self, entityName: str) -> tuple[Entity, ...]:
		"""
		Return all entities named ``entityName`` from the libraries of the design.

		The search is case-insensitive. Each entity references its library by
		:attr:`~pyVHDLModel.DesignUnit.DesignUnit.Library`.

		:param entityName:  Name of the searched entity.
		:returns:           Tuple of entities in the order of the design's libraries, empty if no library contains one.
		:raises ValueError: If parameter 'entityName' is None or empty.
		:raises TypeError:  If parameter 'entityName' is not of type :class:`str`.
		"""
		if entityName is None:
			raise ValueError("Parameter 'entityName' is None.")
		elif not isinstance(entityName, str):
			ex = TypeError("Parameter 'entityName' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(entityName)}'.")
			raise ex
		elif entityName == "":
			raise ValueError("Parameter 'entityName' is empty.")

		entityIdentifier = entityName.lower()
		return tuple(
			library._entities[entityIdentifier]
			for library in self._libraries.values()
			if entityIdentifier in library._entities
		)

	def GetPackage(self, libraryName: str, packageName: str) -> Package:
		"""
		Return the package named ``packageName`` from the library named ``libraryName``.

		The lookup is case-insensitive. Nothing is created, if the library or package doesn't exist.

		:param libraryName:           Name of the library containing the package.
		:param packageName:           Name of the requested package.
		:returns:                     The package.
		:raises ValueError:           If parameter 'libraryName' is None or empty.
		:raises TypeError:            If parameter 'libraryName' is not of type :class:`str`.
		:raises ValueError:           If parameter 'packageName' is None or empty.
		:raises TypeError:            If parameter 'packageName' is not of type :class:`str`.
		:raises LibraryNotFoundError: If the library doesn't exist in the design.
		:raises PackageNotFoundError: If the package doesn't exist in the library.
		"""
		if libraryName is None:
			raise ValueError("Parameter 'libraryName' is None.")
		elif not isinstance(libraryName, str):
			ex = TypeError("Parameter 'libraryName' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(libraryName)}'.")
			raise ex
		elif libraryName == "":
			raise ValueError("Parameter 'libraryName' is empty.")

		if packageName is None:
			raise ValueError("Parameter 'packageName' is None.")
		elif not isinstance(packageName, str):
			ex = TypeError("Parameter 'packageName' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(packageName)}'.")
			raise ex
		elif packageName == "":
			raise ValueError("Parameter 'packageName' is empty.")

		libraryIdentifier = libraryName.lower()
		if libraryIdentifier not in self._libraries:
			raise LibraryNotFoundError(libraryName)

		library =           self._libraries[libraryIdentifier]
		packageIdentifier = packageName.lower()
		if packageIdentifier not in library._packages:
			raise PackageNotFoundError(packageName, libraryName)

		return library._packages[packageIdentifier]

	def SearchPackage(self, packageName: str) -> tuple[Package, ...]:
		"""
		Return all packages named ``packageName`` from the libraries of the design.

		The search is case-insensitive. Each package references its library by
		:attr:`~pyVHDLModel.DesignUnit.DesignUnit.Library`.

		:param packageName: Name of the searched package.
		:returns:           Tuple of packages in the order of the design's libraries, empty if no library contains one.
		:raises ValueError: If parameter 'packageName' is None or empty.
		:raises TypeError:  If parameter 'packageName' is not of type :class:`str`.
		"""
		if packageName is None:
			raise ValueError("Parameter 'packageName' is None.")
		elif not isinstance(packageName, str):
			ex = TypeError("Parameter 'packageName' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(packageName)}'.")
			raise ex
		elif packageName == "":
			raise ValueError("Parameter 'packageName' is empty.")

		packageIdentifier = packageName.lower()
		return tuple(
			library._packages[packageIdentifier]
			for library in self._libraries.values()
			if packageIdentifier in library._packages
		)

	def GetConfiguration(self, libraryName: str, configurationName: str) -> Configuration:
		"""
		Return the configuration named ``configurationName`` from the library named ``libraryName``.

		The lookup is case-insensitive. Nothing is created, if the library or configuration doesn't exist.

		:param libraryName:                 Name of the library containing the configuration.
		:param configurationName:           Name of the requested configuration.
		:returns:                           The configuration.
		:raises ValueError:                 If parameter 'libraryName' is None or empty.
		:raises TypeError:                  If parameter 'libraryName' is not of type :class:`str`.
		:raises ValueError:                 If parameter 'configurationName' is None or empty.
		:raises TypeError:                  If parameter 'configurationName' is not of type :class:`str`.
		:raises LibraryNotFoundError:       If the library doesn't exist in the design.
		:raises ConfigurationNotFoundError: If the configuration doesn't exist in the library.
		"""
		if libraryName is None:
			raise ValueError("Parameter 'libraryName' is None.")
		elif not isinstance(libraryName, str):
			ex = TypeError("Parameter 'libraryName' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(libraryName)}'.")
			raise ex
		elif libraryName == "":
			raise ValueError("Parameter 'libraryName' is empty.")

		if configurationName is None:
			raise ValueError("Parameter 'configurationName' is None.")
		elif not isinstance(configurationName, str):
			ex = TypeError("Parameter 'configurationName' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(configurationName)}'.")
			raise ex
		elif configurationName == "":
			raise ValueError("Parameter 'configurationName' is empty.")

		libraryIdentifier = libraryName.lower()
		if libraryIdentifier not in self._libraries:
			raise LibraryNotFoundError(libraryName)

		library =                 self._libraries[libraryIdentifier]
		configurationIdentifier = configurationName.lower()
		if configurationIdentifier not in library._configurations:
			raise ConfigurationNotFoundError(configurationName, libraryName)

		return library._configurations[configurationIdentifier]

	def SearchConfiguration(self, configurationName: str) -> tuple[Configuration, ...]:
		"""
		Return all configurations named ``configurationName`` from the libraries of the design.

		The search is case-insensitive. Each configuration references its library by
		:attr:`~pyVHDLModel.DesignUnit.DesignUnit.Library`.

		:param configurationName: Name of the searched configuration.
		:returns:                 Tuple of configurations in the order of the design's libraries, empty if no library
		                          contains one.
		:raises ValueError:       If parameter 'configurationName' is None or empty.
		:raises TypeError:        If parameter 'configurationName' is not of type :class:`str`.
		"""
		if configurationName is None:
			raise ValueError("Parameter 'configurationName' is None.")
		elif not isinstance(configurationName, str):
			ex = TypeError("Parameter 'configurationName' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(configurationName)}'.")
			raise ex
		elif configurationName == "":
			raise ValueError("Parameter 'configurationName' is empty.")

		configurationIdentifier = configurationName.lower()
		return tuple(
			library._configurations[configurationIdentifier]
			for library in self._libraries.values()
			if configurationIdentifier in library._configurations
		)

	def GetContext(self, libraryName: str, contextName: str) -> Context:
		"""
		Return the context named ``contextName`` from the library named ``libraryName``.

		The lookup is case-insensitive. Nothing is created, if the library or context doesn't exist.

		:param libraryName:           Name of the library containing the context.
		:param contextName:           Name of the requested context.
		:returns:                     The context.
		:raises ValueError:           If parameter 'libraryName' is None or empty.
		:raises TypeError:            If parameter 'libraryName' is not of type :class:`str`.
		:raises ValueError:           If parameter 'contextName' is None or empty.
		:raises TypeError:            If parameter 'contextName' is not of type :class:`str`.
		:raises LibraryNotFoundError: If the library doesn't exist in the design.
		:raises ContextNotFoundError: If the context doesn't exist in the library.
		"""
		if libraryName is None:
			raise ValueError("Parameter 'libraryName' is None.")
		elif not isinstance(libraryName, str):
			ex = TypeError("Parameter 'libraryName' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(libraryName)}'.")
			raise ex
		elif libraryName == "":
			raise ValueError("Parameter 'libraryName' is empty.")

		if contextName is None:
			raise ValueError("Parameter 'contextName' is None.")
		elif not isinstance(contextName, str):
			ex = TypeError("Parameter 'contextName' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(contextName)}'.")
			raise ex
		elif contextName == "":
			raise ValueError("Parameter 'contextName' is empty.")

		libraryIdentifier = libraryName.lower()
		if libraryIdentifier not in self._libraries:
			raise LibraryNotFoundError(libraryName)

		library =           self._libraries[libraryIdentifier]
		contextIdentifier = contextName.lower()
		if contextIdentifier not in library._contexts:
			raise ContextNotFoundError(contextName, libraryName)

		return library._contexts[contextIdentifier]

	def SearchContext(self, contextName: str) -> tuple[Context, ...]:
		"""
		Return all contexts named ``contextName`` from the libraries of the design.

		The search is case-insensitive. Each context references its library by
		:attr:`~pyVHDLModel.DesignUnit.DesignUnit.Library`.

		:param contextName: Name of the searched context.
		:returns:           Tuple of contexts in the order of the design's libraries, empty if no library contains one.
		:raises ValueError: If parameter 'contextName' is None or empty.
		:raises TypeError:  If parameter 'contextName' is not of type :class:`str`.
		"""
		if contextName is None:
			raise ValueError("Parameter 'contextName' is None.")
		elif not isinstance(contextName, str):
			ex = TypeError("Parameter 'contextName' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(contextName)}'.")
			raise ex
		elif contextName == "":
			raise ValueError("Parameter 'contextName' is empty.")

		contextIdentifier = contextName.lower()
		return tuple(
			library._contexts[contextIdentifier]
			for library in self._libraries.values()
			if contextIdentifier in library._contexts
		)

	# TODO: allow overloaded parameter library to be str?
	def AddDocument(self, document: Document, library: Library) -> None:
		"""
		Add a document (VHDL source file) to the design and register all embedded design units to the given VHDL library.

		All checks are done, before the design, the document or the library is changed.

		.. rubric:: Algorithm

		1. Check the document isn't a document of a design, and the design contains no document of the same path.
		2. Check none of the document's entities, architectures, packages, package bodies, configurations and contexts
		   exists in the library.
		3. Add the document to the design and set the document's library.
		4. Add the document's entities, architectures, packages, package bodies, configurations and contexts to the
		   library and update their library membership.

		:param document:                           The VHDL source code file.
		:param library:                            The VHDL library used to register the embedded design units to.
		:raises ValueError:                        If parameter 'document' is ``None``.
		:raises TypeError:                         If parameter 'document' is not of type :class:`Document`.
		:raises AlreadyInDesignError:              If parameter 'document' is already a document of a design.
		:raises DuplicateDocumentError:            If the design already contains a document of the same path.
		:raises ValueError:                        If parameter 'library' is ``None``.
		:raises TypeError:                         If parameter 'library' is not of type :class:`Library`.
		:raises LibraryNotRegisteredError:         If the given VHDL library is not a library in the design.
		:raises EntityExistsInLibraryError:        If the processed entity's name is already existing in the VHDL library.
		:raises ArchitectureExistsInLibraryError:  If the processed architecture's name is already existing in the VHDL library.
		:raises PackageExistsInLibraryError:       If the processed package's name is already existing in the VHDL library.
		:raises PackageBodyExistsError:            If the processed package body's name is already existing in the VHDL library.
		:raises ConfigurationExistsInLibraryError: If the processed configuration's name is already existing in the VHDL library.
		:raises ContextExistsInLibraryError:       If the processed context's name is already existing in the VHDL library.

		.. seealso::

		   :meth:`RemoveDocument`
		      |rarr| Remove a document from the design.
		"""
		if document is None:
			raise ValueError("Parameter 'document' is None.")
		elif not isinstance(document, Document):
			ex = TypeError("Parameter 'document' is not of type 'Document'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(document)}'.")
			raise ex
		elif isinstance(document._parent, Design) and document._parent._documentsByPath.get(document._path) is document:
			ex = AlreadyInDesignError(
				f"Document '{document._path}' is already a document of a design.",
				element=document,
				parent=document._parent
			)
			ex.add_note("Remove it from its design first.")
			raise ex

		if (existing := self._documentsByPath.get(document._path)) is not None:
			raise DuplicateDocumentError(
				f"Design already contains a document of path '{document._path}'.",
				path=document._path,
				parent=self,
				element=document,
				existing=existing
			)

		if library is None:
			raise ValueError("Parameter 'library' is None.")
		elif not isinstance(library, Library):
			ex = TypeError("Parameter 'library' is not of type 'Library'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(library)}'.")
			raise ex
		elif self._libraries.get(library._normalizedIdentifier) is not library:
			raise LibraryNotRegisteredError(library)

		for entityIdentifier, entity in document._entities.items():
			if entityIdentifier in library._entities:
				raise EntityExistsInLibraryError(entity, library)

		for entityIdentifier, architectures in document._architectures.items():
			architecturesPerEntity = library._architectures.get(entityIdentifier, {})
			for architectureIdentifier, architecture in architectures.items():
				if architectureIdentifier in architecturesPerEntity:
					raise ArchitectureExistsInLibraryError(architecture, library._entities[entityIdentifier], library)

		for packageIdentifier, package in document._packages.items():
			if packageIdentifier in library._packages:
				raise PackageExistsInLibraryError(package, library)

		for packageBodyIdentifier, packageBody in document._packageBodies.items():
			if packageBodyIdentifier in library._packageBodies:
				raise PackageBodyExistsError(packageBody, library)

		for configurationIdentifier, configuration in document._configurations.items():
			if configurationIdentifier in library._configurations:
				raise ConfigurationExistsInLibraryError(configuration, library)

		for contextIdentifier, context in document._contexts.items():
			if contextIdentifier in library._contexts:
				raise ContextExistsInLibraryError(context, library)

		self._documents.append(document)
		self._documentsByPath[document._path] = document
		document.Parent = self
		document._library = library

		for entityIdentifier, entity in document._entities.items():
			library._entities[entityIdentifier] = entity
			entity.Library = library

		for entityIdentifier, architectures in document._architectures.items():
			architecturesPerEntity = library._architectures.setdefault(entityIdentifier, {})
			for architectureIdentifier, architecture in architectures.items():
				architecturesPerEntity[architectureIdentifier] = architecture
				architecture.Library = library

		for packageIdentifier, package in document._packages.items():
			library._packages[packageIdentifier] = package
			package.Library = library

		for packageBodyIdentifier, packageBody in document._packageBodies.items():
			library._packageBodies[packageBodyIdentifier] = packageBody
			packageBody.Library = library

		for configurationIdentifier, configuration in document._configurations.items():
			library._configurations[configurationIdentifier] = configuration
			configuration.Library = library

		for contextIdentifier, context in document._contexts.items():
			library._contexts[contextIdentifier] = context
			context.Library = library

	def RemoveDocument(self, document: Document) -> None:
		"""
		Remove a document (VHDL source file) from the design.

		The document is detached: its parent and library are cleared. Its entities, architectures, packages, package bodies,
		configurations and contexts leave the library, and their parent is cleared. The design units stay design units of
		the document, so the document can be added to a design again.

		:param document:        The VHDL source code file.
		:raises ValueError:     If parameter 'document' is ``None``.
		:raises TypeError:      If parameter 'document' is not of type :class:`Document`.
		:raises NotAChildError: If parameter 'document' is not a document of this design.

		.. seealso::

		   :meth:`AddDocument`
		      |rarr| Add a document to the design.
		"""
		if document is None:
			raise ValueError("Parameter 'document' is None.")
		elif not isinstance(document, Document):
			ex = TypeError("Parameter 'document' is not of type 'Document'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(document)}'.")
			raise ex

		if self._documentsByPath.get(document._path) is not document:
			raise NotAChildError(
				f"Document '{document._path}' is not a document of this design.",
				element=document,
				parent=self
			)

		library = document._library
		for entityIdentifier, entity in document._entities.items():
			del library._entities[entityIdentifier]
			entity._parent = None

		for entityIdentifier, architectures in document._architectures.items():
			architecturesPerEntity = library._architectures[entityIdentifier]
			for architectureIdentifier, architecture in architectures.items():
				del architecturesPerEntity[architectureIdentifier]
				architecture._parent = None

			if len(architecturesPerEntity) == 0:
				del library._architectures[entityIdentifier]

		for packageIdentifier, package in document._packages.items():
			del library._packages[packageIdentifier]
			package._parent = None

		for packageBodyIdentifier, packageBody in document._packageBodies.items():
			del library._packageBodies[packageBodyIdentifier]
			packageBody._parent = None

		for configurationIdentifier, configuration in document._configurations.items():
			del library._configurations[configurationIdentifier]
			configuration._parent = None

		for contextIdentifier, context in document._contexts.items():
			del library._contexts[contextIdentifier]
			context._parent = None

		for index, item in enumerate(self._documents):
			if item is document:
				del self._documents[index]
				break
		del self._documentsByPath[document._path]
		document._parent = None
		document._library = None

	def IterateDesignUnits(self, filter: DesignUnitKind = DesignUnitKind.All) -> Generator[DesignUnit, None, None]:
		"""
		Iterate all design units in the design.

		A union of :class:`DesignUnitKind` values can be given to filter the returned result for suitable design units.

		.. rubric:: Algorithm

		1. Iterate all VHDL libraries.

		   1. Iterate all contexts in that library.
		   2. Iterate all packages in that library.
		   3. Iterate all package bodies in that library.
		   4. Iterate all entites in that library.
		   5. Iterate all architectures in that library.
		   6. Iterate all configurations in that library.

		:param filter: An enumeration with possibly multiple flags to filter the returned design units.
		:returns:      A generator to iterate all matched design units in the design.

		.. seealso::

		   :meth:`pyVHDLModel.Library.IterateDesignUnits`
		     Iterate all design units in the library.
		   :meth:`pyVHDLModel.Document.IterateDesignUnits`
		     Iterate all design units in the document.
		"""
		for library in self._libraries.values():
			yield from library.IterateDesignUnits(filter)

	def Analyze(self) -> None:
		"""
		Analyze the whole design.

		The analysis can be repeated, e.g. after the design was changed: the previous analysis is reset first.

		.. rubric:: Algorithm

		1. Reset a previous analysis. |br|
		   |rarr| :meth:`ResetAnalysis`
		2. Analyze dependencies of design units. |br|
		   This will also yield the design hierarchy and the compiler order.
		3. Analyze dependencies of types and objects.

		.. seealso::

		   :meth:`ResetAnalysis`
		     Reset everything an analysis derived.

		   :meth:`AnalyzeDependencies`
		     Analyze the dependencies of design units.

		   :meth:`AnalyzeObjects`
		     Analyze the dependencies of types and objects.

		:raises UnhandledCriticalWarningError: If an identifier is declared twice in a declarative region and no
		                                       :class:`~pyTooling.Warning.WarningCollector` collects the
		                                       :exc:`~pyVHDLModel.Exception.DuplicateDeclarationWarning`.
		"""
		self.ResetAnalysis()
		self.AnalyzeDependencies()
		# self.AnalyzeObjects()

	def ResetAnalysis(self) -> None:
		"""
		Reset everything an analysis (:meth:`Analyze`) derived, so the design can be analyzed again.

		Everything built by the user is kept: libraries, documents, design units, declarations and the declarations in
		namespaces. Lookup tables built by indexing (e.g. :meth:`IndexPackages`) are kept too, as indexing again yields
		the same lookup tables. Resetting a design, which wasn't analyzed, changes nothing.

		.. rubric:: Algorithm

		1. Delete the dependency, compile-order, hierarchy and object graph (:meth:`~pyTooling.Graph.Graph.Delete`), so
		   their vertices and edges are freed at once, replace them by empty graphs, and forget the top-level.
		2. Clear the references to vertices of all libraries, documents and design units.
		3. Clear the references of all design units: referenced libraries, packages and contexts, the symbols of library
		   clauses, use clauses and context references, and the items imported into namespaces.
		4. Unlink architectures from entities and package bodies from packages: an entity's architectures, a package's
		   body, the symbols referencing the entity or package, and the link to the parent namespace.
		5. Unlink package instantiations from their generic package: the symbol and the components copied from it.
		6. Unbind all components: their entity and blackbox state.
		7. Clear the symbols of entity and component instantiations.
		"""
		self._dependencyGraph.Delete()
		self._compileOrderGraph.Delete()
		self._hierarchyGraph.Delete()
		self._objectGraph.Delete()

		self._dependencyGraph =   Graph()
		self._compileOrderGraph = Graph()
		self._hierarchyGraph =    Graph()
		self._objectGraph =       Graph()
		self._toplevel =          None

		for library in self._libraries.values():
			library._dependencyVertex = None

		for document in self._documents:
			document._dependencyVertex =   None
			document._compileOrderVertex = None

		for designUnit in self.IterateDesignUnits():
			designUnit._dependencyVertex = None
			designUnit._hierarchyVertex =  None
			designUnit._referencedLibraries.clear()
			designUnit._referencedPackages.clear()
			designUnit._referencedContexts.clear()
			references = (*designUnit._libraryReferences, *designUnit._packageReferences, *designUnit._contextReferences)
			for reference in references:
				for symbol in reference._symbols:
					symbol._reference = None

		for designUnit in self.IterateDesignUnits(DesignUnitKind.WithContext):
			designUnit._namespace.ClearImports()

		for entity in self.IterateDesignUnits(DesignUnitKind.Entity):  # type: Entity
			for architecture in entity._architectures.values():
				architecture._namespace.ParentNamespace = None

			entity._architectures.clear()

		for architecture in self.IterateDesignUnits(DesignUnitKind.Architecture):  # type: Architecture
			architecture._entity._reference = None
			architecture._namespace.ParentNamespace = None
			for instance in architecture.IterateInstantiations():
				if isinstance(instance, EntityInstantiation):
					instance._entity._reference = None
				elif isinstance(instance, ComponentInstantiation):
					instance._component._reference = None

		for package in self.IterateDesignUnits(DesignUnitKind.Package):  # type: Package
			if package._packageBody is not None:
				package._packageBody._namespace.ParentNamespace = None
				package._packageBody = None

			if isinstance(package, PackageInstantiation):
				package._packageReference._reference = None
				package._components.clear()

		for packageBody in self.IterateDesignUnits(DesignUnitKind.PackageBody):  # type: PackageBody
			packageBody._package._reference = None
			packageBody._namespace.ParentNamespace = None

		for _, component in self._IterateComponents():
			component._entity =     None
			component._isBlackbox = None

	def AnalyzeDependencies(self) -> None:
		"""
		Analyze the dependencies of design units.

		.. rubric:: Algorithm

		1. Create all vertices of the dependency graph by iterating all design units in all libraries. |br|
		   |rarr| :meth:`CreateDependencyGraph`
		2. Create the compile order graph. |br|
		   |rarr| :meth:`CreateCompileOrderGraph`
		3. Index all packages. |br|
		   |rarr| :meth:`IndexPackages`
		4. Index all entities. |br|
		   |rarr| :meth:`IndexEntities`
		5. Index all architectures. |br|
		   |rarr| :meth:`IndexArchitectures`
		6. Link all contexts |br|
		   |rarr| :meth:`LinkContexts`
		7. Link all architectures. |br|
		   |rarr| :meth:`LinkArchitectures`
		8. Link all package bodies. |br|
		   |rarr| :meth:`LinkPackageBodies`
		9. Link all package instances. |br|
		   |rarr| :meth:`LinkPackageInstances`
		10. Link all library references. |br|
		    |rarr| :meth:`LinkLibraryReferences`
		11. Link all package references. |br|
		    |rarr| :meth:`LinkPackageReferences`
		12. Link all context references. |br|
		    |rarr| :meth:`LinkContextReferences`
		13. Link all components. |br|
		    |rarr| :meth:`LinkComponents`
		14. Link all instantiations. |br|
		    |rarr| :meth:`LinkInstantiations`
		15. Create the hierarchy graph. |br|
		    |rarr| :meth:`CreateHierarchyGraph`
		16. Compute the compile order. |br|
		    |rarr| :meth:`ComputeCompileOrder`

		:raises UnhandledCriticalWarningError: If an identifier is declared twice in a declarative region and no
		                                       :class:`~pyTooling.Warning.WarningCollector` collects the
		                                       :exc:`~pyVHDLModel.Exception.DuplicateDeclarationWarning`.
		"""
		self.CreateDependencyGraph()
		self.CreateCompileOrderGraph()

		self.IndexPackages()
		self.IndexEntities()
		self.IndexArchitectures()

		self.LinkContexts()
		self.LinkArchitectures()
		self.LinkPackageBodies()
		self.LinkPackageInstances()
		self.LinkLibraryReferences()
		self.LinkPackageReferences()
		self.LinkContextReferences()

		self.LinkComponents()
		self.LinkInstantiations()
		self.CreateHierarchyGraph()
		self.ComputeCompileOrder()

	def AnalyzeObjects(self) -> None:
		"""
		Analyze the dependencies of types and objects.

		.. rubric:: Algorithm

		1. Index all entities. |br|
		   |rarr| :meth:`IndexEntities`
		2. Index all package bodies. |br|
		   |rarr| :meth:`IndexPackageBodies`
		3. Import objects. |br|
		   |rarr| :meth:`ImportObjects`
		4. Create the type and object graph. |br|
		   |rarr| :meth:`CreateTypeAndObjectGraph`

		:raises UnhandledCriticalWarningError: If an identifier is declared twice in a declarative region and no
		                                       :class:`~pyTooling.Warning.WarningCollector` collects the
		                                       :exc:`~pyVHDLModel.Exception.DuplicateDeclarationWarning`.
		"""
		self.IndexEntities()
		self.IndexPackageBodies()

		self.ImportObjects()
		self.CreateTypeAndObjectGraph()

	def CreateDependencyGraph(self) -> None:
		"""
		Create all vertices of the dependency graph by iterating all design units in all libraries.

		This method will purely create a sea of vertices without any linking between vertices. The edges will be created later by other methods. |br|
		See :meth:`AnalyzeDependencies` for these methods and their algorithmic order.

		Each vertex has the following properties:

		* The vertex' ID is the design unit's identifier.
		* The vertex' value references the design unit.
		* A key-value-pair called ``kind`` denotes the vertex's kind as an enumeration value of type :class:`DependencyGraphVertexKind`.
		* A key-value-pair called ``predefined`` denotes if the referenced design unit is a predefined language entity.

		.. rubric:: Algorithm

		1. Iterate all libraries in the design.

		   * Create a vertex for that library and reference the library by the vertex' value field. |br|
		     In return, set the library's :attr:`~pyVHDLModel.Library._dependencyVertex` field to reference the created vertex.

		   1. Iterate all contexts in that library.

		      * Create a vertex for that context and reference the context by the vertex' value field. |br|
		        In return, set the context's :attr:`~pyVHDLModel.DesignUnit.Context._dependencyVertex` field to reference the created vertex.

		   2. Iterate all packages in that library.

		      * Create a vertex for that package and reference the package by the vertex' value field. |br|
		        In return, set the package's :attr:`~pyVHDLModel.DesignUnit.Package._dependencyVertex` field to reference the created vertex.

		   3. Iterate all package bodies in that library.

		      * Create a vertex for that package body and reference the package body by the vertex' value field. |br|
		        In return, set the package body's :attr:`~pyVHDLModel.DesignUnit.PackageBody._dependencyVertex` field to reference the created vertex.

		   4. Iterate all entities in that library.

		      * Create a vertex for that entity and reference the entity by the vertex' value field. |br|
		        In return, set the entity's :attr:`~pyVHDLModel.DesignUnit.Entity._dependencyVertex` field to reference the created vertex.

		   5. Iterate all architectures in that library.

		      * Create a vertex for that architecture and reference the architecture by the vertex' value field. |br|
		        In return, set the architecture's :attr:`~pyVHDLModel.DesignUnit.Architecture._dependencyVertex` field to reference the created vertex.

		   6. Iterate all configurations in that library.

		      * Create a vertex for that configuration and reference the configuration by the vertex' value field. |br|
		        In return, set the configuration's :attr:`~pyVHDLModel.DesignUnit.Configuration._dependencyVertex` field to reference the created vertex.
		"""
		predefinedLibraries = ("std", "ieee")

		for libraryIdentifier, library in self._libraries.items():
			dependencyVertex = Vertex(vertexID=f"{libraryIdentifier}", value=library, graph=self._dependencyGraph)
			dependencyVertex["kind"] = DependencyGraphVertexKind.Library
			dependencyVertex["predefined"] = libraryIdentifier in predefinedLibraries
			library._dependencyVertex = dependencyVertex

			for contextIdentifier, context in library._contexts.items():
				dependencyVertex = Vertex(vertexID=f"{libraryIdentifier}.{contextIdentifier}", value=context, graph=self._dependencyGraph)
				dependencyVertex["kind"] = DependencyGraphVertexKind.Context
				dependencyVertex["predefined"] = context._parent._normalizedIdentifier in predefinedLibraries
				context._dependencyVertex = dependencyVertex

			for packageIdentifier, package in library._packages.items():
				dependencyVertex = Vertex(vertexID=f"{libraryIdentifier}.{packageIdentifier}", value=package, graph=self._dependencyGraph)
				dependencyVertex["kind"] = DependencyGraphVertexKind.Package
				dependencyVertex["predefined"] = package._parent._normalizedIdentifier in predefinedLibraries
				package._dependencyVertex = dependencyVertex

			for packageBodyIdentifier, packageBody in library._packageBodies.items():
				dependencyVertex = Vertex(vertexID=f"{libraryIdentifier}.{packageBodyIdentifier}(body)", value=packageBody, graph=self._dependencyGraph)
				dependencyVertex["kind"] = DependencyGraphVertexKind.PackageBody
				dependencyVertex["predefined"] = packageBody._parent._normalizedIdentifier in predefinedLibraries
				packageBody._dependencyVertex = dependencyVertex

			for entityIdentifier, entity in library._entities.items():
				dependencyVertex = Vertex(vertexID=f"{libraryIdentifier}.{entityIdentifier}", value=entity, graph=self._dependencyGraph)
				dependencyVertex["kind"] = DependencyGraphVertexKind.Entity
				dependencyVertex["predefined"] = entity._parent._normalizedIdentifier in predefinedLibraries
				entity._dependencyVertex = dependencyVertex

			for entityIdentifier, architectures in library._architectures.items():
				for architectureIdentifier, architecture in architectures.items():
					dependencyVertex = Vertex(vertexID=f"{libraryIdentifier}.{entityIdentifier}({architectureIdentifier})", value=architecture, graph=self._dependencyGraph)
					dependencyVertex["kind"] = DependencyGraphVertexKind.Architecture
					dependencyVertex["predefined"] = architecture._parent._normalizedIdentifier in predefinedLibraries
					architecture._dependencyVertex = dependencyVertex

			for configurationIdentifier, configuration in library._configurations.items():
				dependencyVertex = Vertex(vertexID=f"{libraryIdentifier}.{configurationIdentifier}", value=configuration, graph=self._dependencyGraph)
				dependencyVertex["kind"] = DependencyGraphVertexKind.Configuration
				dependencyVertex["predefined"] = configuration._parent._normalizedIdentifier in predefinedLibraries
				configuration._dependencyVertex = dependencyVertex

	def CreateCompileOrderGraph(self) -> None:
		"""
		Create a compile-order graph with bidirectional references to the dependency graph.

		Add vertices representing a document (VHDL source file) to the dependency graph. Each "document" vertex in dependency graph is copied into the compile-order
		graph and bidirectionally referenced.

		In addition, each vertex of a corresponding design unit in a document is linked to the vertex representing that document to express the design unit in
		document relationship.

		Each added vertex has the following properties:

		* The vertex' ID is the document's filename.
		* The vertex' value references the document.
		* A key-value-pair called ``kind`` denotes the vertex's kind as an enumeration value of type :class:`DependencyGraphVertexKind`.
		* A key-value-pair called ``predefined`` does not exist.

		.. rubric:: Algorithm

		1. Iterate all documents in the design.

		   * Create a vertex for that document with the document's path as vertex ID and reference the document by the
		     vertex' value field. |br|
		     In return, set the documents's :attr:`~pyVHDLModel.Document._dependencyVertex` field to reference the created vertex.
		   * Copy the vertex from dependency graph to compile-order graph and link both vertices bidirectionally. |br|
		     In addition, set the documents's :attr:`~pyVHDLModel.Document._dependencyVertex` field to reference the copied vertex.

		     * Add a key-value-pair called ``compileOrderVertex`` to the dependency graph's vertex.
		     * Add a key-value-pair called ``dependencyVertex`` to the compiler-order graph's vertex.

		   1. Iterate the documents design units and create an edge from the design unit's corresponding dependency vertex to the documents corresponding
		      dependency vertex. This expresses a "design unit is located in document" relation.

		      * Add a key-value-pair called `kind`` denoting the edge's kind as an enumeration value of type :class:`DependencyGraphEdgeKind`.
		"""
		for document in self._documents:
			dependencyVertex = Vertex(vertexID=str(document._path), value=document, graph=self._dependencyGraph)
			dependencyVertex["kind"] = DependencyGraphVertexKind.Document
			document._dependencyVertex = dependencyVertex

			compilerOrderVertex = dependencyVertex.Copy(
				self._compileOrderGraph,
				copyDict=True,
				linkingKeyToOriginalVertex="dependencyVertex",
				linkingKeyFromOriginalVertex="compileOrderVertex"
			)
			document._compileOrderVertex = compilerOrderVertex

			for designUnit in document._designUnits:
				edge = dependencyVertex.EdgeFromVertex(designUnit._dependencyVertex)
				edge["kind"] = DependencyGraphEdgeKind.SourceFile

	def ImportObjects(self) -> None:
		def _ImportObjects(package: Package) -> None:
			from pyVHDLModel.Declaration import AttributeSpecification

			for referencedLibrary in package._referencedPackages.values():
				for referencedPackage in referencedLibrary.values():
					for declaredItem in referencedPackage._declaredItems:
						if isinstance(declaredItem, MultipleNamedEntityMixin):
							for normalizedIdentifier in declaredItem._normalizedIdentifiers:
								package._namespace.AddImport(normalizedIdentifier, declaredItem)
						elif isinstance(declaredItem, NamedEntityMixin):
							package._namespace.AddImport(declaredItem._normalizedIdentifier, declaredItem)
						elif isinstance(declaredItem, AttributeSpecification):
							# FIXME: actually, this is not a declared item, but a application of an attribute to named entities
							WarningCollector.Raise(NotImplementedWarning("Attribute specification.", item=declaredItem))

						else:
							raise VHDLModelException("Unexpected declared item.")

		for libraryName in ("std", "ieee"):
			for package in self.GetLibrary(libraryName).IterateDesignUnits(filter=DesignUnitKind.Package):  # type: Package
				_ImportObjects(package)

		for document in self.IterateDocumentsInCompileOrder():
			for package in document.IterateDesignUnits(filter=DesignUnitKind.Package):  # type: Package
				_ImportObjects(package)

	def CreateTypeAndObjectGraph(self) -> None:
		def _HandlePackage(package) -> None:
			packagePrefix = f"{package.Library.NormalizedIdentifier}.{package.NormalizedIdentifier}"

			for deferredConstant in package._deferredConstants.values():
				print(f"Deferred Constant: {deferredConstant}")
				deferredConstantVertex = Vertex(
					vertexID=f"{packagePrefix}.{deferredConstant.NormalizedIdentifiers[0]}",
					value=deferredConstant,
					graph=self._objectGraph
				)
				deferredConstantVertex["kind"] = ObjectGraphVertexKind.DeferredConstant
				deferredConstant._objectVertex = deferredConstantVertex

			for constant in package._constants.values():
				print(f"Constant: {constant}")
				constantVertex = Vertex(
					vertexID=f"{packagePrefix}.{constant.NormalizedIdentifiers[0]}",
					value=constant,
					graph=self._objectGraph
				)
				constantVertex["kind"] = ObjectGraphVertexKind.Constant
				constant._objectVertex = constantVertex

			for type in package._types.values():
				print(f"Type: {type}")
				typeVertex = Vertex(
					vertexID=f"{packagePrefix}.{type.NormalizedIdentifier}",
					value=type,
					graph=self._objectGraph
				)
				typeVertex["kind"] = ObjectGraphVertexKind.Type
				type._objectVertex = typeVertex

			for subtype in package._subtypes.values():
				print(f"Subtype: {subtype}")
				subtypeVertex = Vertex(
					vertexID=f"{packagePrefix}.{subtype.NormalizedIdentifier}",
					value=subtype,
					graph=self._objectGraph
				)
				subtypeVertex["kind"] = ObjectGraphVertexKind.Subtype
				subtype._objectVertex = subtypeVertex

			for function in package._functions.values():
				print(f"Function: {function}")
				functionVertex = Vertex(
					vertexID=f"{packagePrefix}.{function.NormalizedIdentifier}",
					value=function,
					graph=self._objectGraph
				)
				functionVertex["kind"] = ObjectGraphVertexKind.Function
				function._objectVertex = functionVertex

			for procedure in package._procedures.values():
				print(f"Procedure: {procedure}")
				procedureVertex = Vertex(
					vertexID=f"{packagePrefix}.{procedure.NormalizedIdentifier}",
					value=procedure,
					graph=self._objectGraph
				)
				procedureVertex["kind"] = ObjectGraphVertexKind.Function
				procedure._objectVertex = procedureVertex

			for signal in package._signals.values():
				print(f"Signal: {signal}")
				signalVertex = Vertex(
					vertexID=f"{packagePrefix}.{signal.NormalizedIdentifiers[0]}",
					value=signal,
					graph=self._objectGraph
				)
				signalVertex["kind"] = ObjectGraphVertexKind.Signal
				signal._objectVertex = signalVertex

		def _LinkSymbolsInExpression(expression, namespace: Namespace, typeVertex: Vertex) -> None:
			if isinstance(expression, UnaryExpression):
				_LinkSymbolsInExpression(expression.Operand, namespace, typeVertex)
			elif isinstance(expression, BinaryExpression):
				_LinkSymbolsInExpression(expression.LeftOperand, namespace, typeVertex)
				_LinkSymbolsInExpression(expression.RightOperand, namespace, typeVertex)
			elif isinstance(expression, TernaryExpression):
				WarningCollector.Raise(NotImplementedWarning("Handling of ternary expression.", item=expression))
			elif isinstance(expression, SimpleObjectOrFunctionCallSymbol):
				obj = namespace.FindObject(expression)
				expression._reference = obj

				edge = obj._objectVertex.EdgeToVertex(typeVertex)
				edge["kind"] = ObjectGraphEdgeKind.ReferenceInExpression
			else:
				WarningCollector.Raise(NotImplementedWarning("Unhandled else-branch", item=expression))

		def _LinkItems(package: Package) -> None:
			for item in package._declaredItems:
				if isinstance(item, Constant):
					print(f"constant: {item}")
				elif isinstance(item, DeferredConstant):
					print(f"deferred constant: {item}")
				elif isinstance(item, Signal):
					print(f"signal: {item}")
				elif isinstance(item, IntegerType):
					typeNode = item._objectVertex

					_LinkSymbolsInExpression(item.Range.LeftBound, package._namespace, typeNode)
					_LinkSymbolsInExpression(item.Range.RightBound, package._namespace, typeNode)
				# elif isinstance(item, FloatingType):
				# 	print(f"signal: {item}")
				elif isinstance(item, PhysicalType):
					typeNode = item._objectVertex

					_LinkSymbolsInExpression(item.Range.LeftBound, package._namespace, typeNode)
					_LinkSymbolsInExpression(item.Range.RightBound, package._namespace, typeNode)
				elif isinstance(item, ArrayType):
					# Resolve dimensions
					for dimension in item._dimensions:
						subtype = package._namespace.FindSubtype(dimension)
						dimension._reference = subtype

						edge = item._objectVertex.EdgeToVertex(subtype._objectVertex)
						edge["kind"] = ObjectGraphEdgeKind.Subtype

					# Resolve element subtype
					subtype = package._namespace.FindSubtype(item._elementType)
					item._elementType._reference = subtype

					edge = item._objectVertex.EdgeToVertex(subtype._objectVertex)
					edge["kind"] = ObjectGraphEdgeKind.Subtype
				elif isinstance(item, RecordType):
					# Resolve each elements subtype
					for element in item._elements:
						subtype = package._namespace.FindSubtype(element._subtype)
						element._subtype._reference = subtype

						edge = item._objectVertex.EdgeToVertex(subtype._objectVertex)
						edge["kind"] = ObjectGraphEdgeKind.Subtype
				else:
					print(f"not handled: {item}")

		for libraryName in ("std", "ieee"):
			for package in self.GetLibrary(libraryName).IterateDesignUnits(filter=DesignUnitKind.Package):  # type: Package
				_HandlePackage(package)
				_LinkItems(package)

		for document in self.IterateDocumentsInCompileOrder():
			for package in document.IterateDesignUnits(filter=DesignUnitKind.Package):  # type: Package
				_HandlePackage(package)
				_LinkItems(package)

	def LinkContexts(self) -> None:
		"""
		Resolves and links all items (library clauses, use clauses and nested context references) in contexts.

		It iterates all contexts in the design. Therefore, the library of the context is used as the working library. By
		default, the working library is implicitly referenced in :data:`_referencedLibraries`. In addition, a new empty
		dictionary is created in :data:`_referencedPackages` and :data:`_referencedContexts` for that working library.

		At first, all library clauses are resolved (a library clause my have multiple library reference symbols). For each
		referenced library an entry in :data:`_referencedLibraries` is generated and new empty dictionaries in
		:data:`_referencedPackages` and :data:`_referencedContexts` for that working library. In addition, a vertex in the
		dependency graph is added for that relationship.

		At second, all use clauses are resolved (a use clause my have multiple package member reference symbols). For each
		referenced package,
		"""
		for context in self.IterateDesignUnits(DesignUnitKind.Context):  # type: Context
			# Create entries in _referenced*** for the current working library under its real name.
			workingLibrary: Library = context.Library
			libraryNormalizedIdentifier = workingLibrary._normalizedIdentifier

			context._referencedLibraries[libraryNormalizedIdentifier] = self._libraries[libraryNormalizedIdentifier]
			context._referencedPackages[libraryNormalizedIdentifier] = {}
			context._referencedContexts[libraryNormalizedIdentifier] = {}

			# Process all library clauses
			for libraryReference in context._libraryReferences:
				# A library clause can have multiple comma-separated references
				for libraryName in libraryReference.Symbols:
					libraryNormalizedIdentifier = libraryName.Name._normalizedIdentifier
					try:
						library = self._libraries[libraryNormalizedIdentifier]
					except KeyError:
						raise ReferencedLibraryNotExistingError(context, libraryName)
						# TODO: add position to these messages

					libraryName.Library = library

					context._referencedLibraries[libraryNormalizedIdentifier] = library
					context._referencedPackages[libraryNormalizedIdentifier] = {}
					context._referencedContexts[libraryNormalizedIdentifier] = {}
					# TODO: warn duplicate library reference

					dependency = context._dependencyVertex.EdgeToVertex(library._dependencyVertex, edgeValue=libraryReference)
					dependency["kind"] = DependencyGraphEdgeKind.LibraryClause

			# Process all use clauses
			for packageReference in context.PackageReferences:
				# A use clause can have multiple comma-separated references
				for symbol in packageReference.Symbols:  # type: PackageReferenceSymbol
					packageName = symbol.Name.Prefix
					libraryName = packageName.Prefix

					libraryNormalizedIdentifier = libraryName._normalizedIdentifier
					packageNormalizedIdentifier = packageName._normalizedIdentifier

					# In case work is used, resolve to the real library name.
					if libraryNormalizedIdentifier == "work":
						library: Library = context._parent
						libraryNormalizedIdentifier = library._normalizedIdentifier
					elif libraryNormalizedIdentifier not in context._referencedLibraries:
						# TODO: This check doesn't trigger if it's the working library.
						raise VHDLModelException(f"Use clause references library '{libraryName._identifier}', which was not referenced by a library clause.")
					else:
						library = self._libraries[libraryNormalizedIdentifier]

					try:
						package = library._packages[packageNormalizedIdentifier]
					except KeyError:
						raise VHDLModelException(f"Package '{packageName._identifier}' not found in {'working ' if libraryName._normalizedIdentifier == 'work' else ''}library '{library._identifier}'.")

					# FIXME: check if package isn't a generic package
					symbol.Package = package

					# TODO: warn duplicate package reference
					context._referencedPackages[libraryNormalizedIdentifier][packageNormalizedIdentifier] = package

					dependency = context._dependencyVertex.EdgeToVertex(package._dependencyVertex, edgeValue=packageReference)
					dependency["kind"] = DependencyGraphEdgeKind.UseClause

					# TODO: update the namespace with visible members
					if isinstance(symbol, AllPackageMembersReferenceSymbol):
						WarningCollector.Raise(NotImplementedWarning("Handling of 'myLib.myPackage.all'.", item=symbol))

					elif isinstance(symbol, PackageMemberReferenceSymbol):
						WarningCollector.Raise(NotImplementedWarning("Handling of 'myLib.myPackage.mySymbol'.", item=symbol))

					else:
						raise VHDLModelException()

	def LinkArchitectures(self) -> None:
		"""
		Link all architectures to corresponding entities in all libraries.

		.. rubric:: Algorithm

		1. Iterate all libraries:

		   1. Iterate all architecture groups (grouped per entity symbol's name).
		      |rarr| :meth:`pyVHDLModel.Library.LinkArchitectures`

		      * Check if entity symbol's name exists as an entity in this library.

		      1. For each architecture in the same architecture group:

		         * Add architecture to entities architecture dictionary :attr:`pyVHDLModel.DesignUnit.Entity._architectures`.
		         * Assign found entity to architecture's entity symbol :attr:`pyVHDLModel.DesignUnit.Architecture._entity`
		         * Set parent namespace of architecture's namespace to the entitie's namespace.
		         * Add an edge in the dependency graph from the architecture's corresponding dependency vertex to the entity's corresponding dependency vertex.

		.. seealso::

		   :meth:`LinkPackageBodies`
		     Link all package bodies to corresponding packages in all libraries.
		   :meth:`LinkPackageInstances`
		     Link all package instances to corresponding generic packages in all libraries.
		"""
		for library in self._libraries.values():
			library.LinkArchitectures()

	def LinkPackageBodies(self) -> None:
		"""
		Link all package bodies to corresponding packages in all libraries.

		.. rubric:: Algorithm

		1. Iterate all libraries:

		   1. Iterate all package bodies.
		      |rarr| :meth:`pyVHDLModel.Library.LinkPackageBodies`

		      * Check if package body symbol's name exists as a package in this library.
		      * Add package body to package :attr:`pyVHDLModel.DesignUnit.Package._packageBody`.
		      * Assign found package to package body's package symbol :attr:`pyVHDLModel.DesignUnit.PackageBody._package`
		      * Set parent namespace of package body's namespace to the package's namespace.
		      * Add an edge in the dependency graph from the package body's corresponding dependency vertex to the package's corresponding dependency vertex.

		.. seealso::

		   :meth:`LinkArchitectures`
		     Link all architectures to corresponding entities in all libraries.
		   :meth:`LinkPackageInstances`
		     Link all package instances to corresponding generic packages in all libraries.
		"""
		for library in self._libraries.values():
			library.LinkPackageBodies()

	def LinkPackageInstances(self) -> None:
		"""
		Link all package instances to corresponding generic packages in all libraries.

		.. rubric:: Algorithm

		1. Iterate all libraries:

		   1. Iterate all package instances.
		      |rarr| :meth:`pyVHDLModel.Library.LinkPackageInstances`

          .. todo::

		         * Check if package instance's symbol's name exists as a generic package in this library.
		         * Add generic package to package instance :attr:`pyVHDLModel.DesignUnit.Package._packageBody`.
		         * Assign found package to package body's package symbol :attr:`pyVHDLModel.DesignUnit.PackageBody._package`
		         * Set parent namespace of package body's namespace to the package's namespace.
		         * Add an edge in the dependency graph from the package body's corresponding dependency vertex to the package's corresponding dependency vertex.

		.. seealso::

		   :meth:`LinkArchitectures`
		     Link all architectures to corresponding entities in all libraries.
		   :meth:`LinkPackageBodies`
		     Link all package bodies to corresponding packages in all libraries.
		"""
		for library in self._libraries.values():
			library.LinkPackageInstances()

	def LinkLibraryReferences(self) -> None:
		"""
		Link all library references (library clause) to the matching VHDL library.

		.. rubric:: Algorithm

		1. Iterate all design units with contexts:

		   * If the design unit is a primary unit:

		     1. Iterate all library identifiers in ``DEFAULT_LIBRARIES`` (``std``):

		        * Get the referenced library by name from the design.
		        * Add an entry in the design unit's ``_referencedLibraries`` dictionary referencing the referenced library.
		        * Add an empty dictionary in the design unit's ``_referencedPackages`` dictionary.
		        * Add an empty dictionary in the design unit's ``_referencedContexts`` dictionary.
		        * Add an edge in the dependency graph from design unit to the referenced library.

		     2. Get the design unit's library:

		        * Add an entry in the design unit's ``_referencedLibraries`` dictionary referencing the referenced library.
		        * Add an empty dictionary in the design unit's ``_referencedPackages`` dictionary.
		        * Add an empty dictionary in the design unit's ``_referencedContexts`` dictionary.
		        * Add an edge in the dependency graph from design unit to the referenced library.

		   * If the design unit is a secondary unit:

		     * If design unit is an architecture, get the corresponding entity's referenced libraries.
		     * If design unit is a package body, get the corresponding package's referenced libraries.
		     * Otherwise, raise an exception

		     For every referenced library create new dictionary entries in the design unit's ``_referencedLibraries``.

		2. Iterate every library reference (library clause) in the design unit:

		   * Iterate every library symbol within the library reference:

		     * Get the library identifier from the symbol.
		     * Continue the inner loop, if identifier is ``work``.
		     * Get the referenced library from the design or raise an exception.
		     * Update the library symbol's target with the referenced library.
		     * Add an entry in the design unit's ``_referencedLibraries`` dictionary referencing the referenced library.
		     * Add an empty dictionary in the design unit's ``_referencedPackages`` dictionary.
		     * Add an empty dictionary in the design unit's ``_referencedContexts`` dictionary.
		     * Add an edge in the dependency graph from design unit to the referenced library.

		.. seealso::

		   :meth:`LinkPackageReferences`
		     Link *use clause*.
		   :meth:`LinkContextReferences`
		     Link *context clause*.
		   :meth:`AnalyzeDependencies`
		     Analyze dependencies and link relations.
		"""
		DEFAULT_LIBRARIES = ("std",)

		for designUnit in self.IterateDesignUnits(DesignUnitKind.WithContext):
			# All primary units supporting a context, have at least one library implicitly referenced
			if isinstance(designUnit, PrimaryUnit):
				for libraryIdentifier in DEFAULT_LIBRARIES:
					referencedLibrary = self._libraries[libraryIdentifier]
					designUnit._referencedLibraries[libraryIdentifier] = referencedLibrary
					designUnit._referencedPackages[libraryIdentifier] = {}
					designUnit._referencedContexts[libraryIdentifier] = {}
					# TODO: catch KeyError on self._libraries[libName]
					# TODO: warn duplicate library reference

					dependency = designUnit._dependencyVertex.EdgeToVertex(referencedLibrary._dependencyVertex)
					dependency["kind"] = DependencyGraphEdgeKind.LibraryClause

				# TODO: this could create a duplicate linking, if primary unit is put into library 'std'
				workingLibrary: Library = designUnit.Library
				libraryIdentifier = workingLibrary.NormalizedIdentifier
				referencedLibrary = self._libraries[libraryIdentifier]   # TODO: isn't this the same as the workingLibrary from 2 lines before?

				designUnit._referencedLibraries[libraryIdentifier] = referencedLibrary
				designUnit._referencedPackages[libraryIdentifier] = {}
				designUnit._referencedContexts[libraryIdentifier] = {}

				dependency = designUnit._dependencyVertex.EdgeToVertex(referencedLibrary._dependencyVertex)
				dependency["kind"] = DependencyGraphEdgeKind.LibraryClause

			# All secondary units inherit referenced libraries from their primary units.
			else:
				if isinstance(designUnit, Architecture):
					referencedLibraries = designUnit.Entity.Entity._referencedLibraries
				elif isinstance(designUnit, PackageBody):
					referencedLibraries = designUnit.Package.Package._referencedLibraries
				else:
					raise VHDLModelException()  # FIXME: exception message

				for libraryIdentifier, library in referencedLibraries.items():
					designUnit._referencedLibraries[libraryIdentifier] = library   # TODO: Could we use the .update() method

			for libraryReference in designUnit._libraryReferences:
				# A library clause can have multiple comma-separated references
				for librarySymbol in libraryReference.Symbols:
					libraryIdentifier = librarySymbol.Name.NormalizedIdentifier
					if libraryIdentifier == "work":
						continue

					try:
						library = self._libraries[libraryIdentifier]
					except KeyError:
						ex = VHDLModelException(f"Library '{librarySymbol.Name.Identifier}' referenced by library clause of design unit '{designUnit.Identifier}' doesn't exist in design.")
						ex.add_note(f"""Known libraries: '{"', '".join(library for library in self._libraries)}'""")
						raise ex

					librarySymbol.Library = library
					designUnit._referencedLibraries[libraryIdentifier] = library
					designUnit._referencedPackages[libraryIdentifier] = {}
					designUnit._referencedContexts[libraryIdentifier] = {}
					# TODO: warn duplicate library reference

					dependency = designUnit._dependencyVertex.EdgeToVertex(library._dependencyVertex, edgeValue=libraryReference)
					dependency["kind"] = DependencyGraphEdgeKind.LibraryClause

	def LinkPackageReferences(self) -> None:
		"""
		Link all package references (use clause) to the matching packages.

		.. rubric:: Algorithm

		1. Iterate all design units with contexts:

		   * If the design unit is a primary unit:

		     * If primary unit isn't package ``std.standard``:

		       1. Iterate all library, packages tuples in ``DEFAULT_PACKAGES`` (``std``: [``standard``]):

		          * Raise an exception, if library isn't listed in design unit's ``_referencedLibraries``.
		          * For every package in packages:

		            * Get the referenced package by library name and package name from the design.
		            * Add an entry in the design unit's ``_referencedPackages`` dictionary referencing the referenced package.
		            * Add an edge in the dependency graph from design unit to the referenced package.

		   * If the design unit is a secondary unit:

		     * If design unit is an architecture, get the corresponding entity's referenced packages.
		     * If design unit is a package body, get the corresponding package's referenced packages.
		     * Otherwise, raise an exception

		     For every referenced package create new dictionary entries in the design unit's ``_referencedPackages``.

		2. Iterate every package reference (use clause) in the design unit:

		   * Iterate every package symbol within the package reference:

		     1. Get the library identifier from the symbol.
		     2. Get the package identifier from the symbol.
		     3. Resolve library:

		        * If library name is ``work``, get library from design unit.
		        * If library name is not in design unit's ``_referencedLibraries``, raise an exception.
		        * Otherwise, lookup library by name in design.

		     4. Resolve package:

		        * Lookup package by name in library.

		     5. Update design unit:

		        * Update the package symbol's target with the referenced package.
		        * Add an entry in the design unit's ``_referencedPackages`` dictionary referencing the referenced package.
		        * Add an edge in the dependency graph from design unit to the referenced package.

		     6. Import public package members.

		        * If package symbol is a ``AllPackageMembersReferenceSymbol``:

		          * Iterate all components within the referenced package and import each component into the design unit's
		            namespace.

		          .. todo:: Other elements are not implemented.

		        * If package symbol is a ``PackageMemberReferenceSymbol``

		          .. todo:: Not implemented.

		        * Otherwise, raise an exception.

		.. seealso::

		   :meth:`LinkLibraryReferences`
		     Link *library clause*.
		   :meth:`LinkContextReferences`
		     Link *context clause*.
		   :meth:`AnalyzeDependencies`
		     Analyze dependencies and link relations.
		"""
		DEFAULT_PACKAGES = (
			("std", ("standard",)),
		)

		for designUnit in self.IterateDesignUnits(DesignUnitKind.WithContext):
			# All primary units supporting a context, have at least one package implicitly referenced
			if isinstance(designUnit, PrimaryUnit):
				if not (designUnit.Library.NormalizedIdentifier == "std" and designUnit.NormalizedIdentifier == "standard"):
					for lib, packages in DEFAULT_PACKAGES:
						if lib not in designUnit._referencedLibraries:
							raise VHDLModelException()  # TODO: missing exception message
						for package in packages:
							referencedPackage = self._libraries[lib]._packages[package]
							designUnit._referencedPackages[lib][package] = referencedPackage
							# TODO: catch KeyError on self._libraries[lib[0]]._packages[package]
							# TODO: warn duplicate package reference

							dependency = designUnit._dependencyVertex.EdgeToVertex(referencedPackage._dependencyVertex)
							dependency["kind"] = DependencyGraphEdgeKind.UseClause

			# All secondary units inherit referenced packages from their primary units.
			else:
				if isinstance(designUnit, Architecture):
					referencedPackages = designUnit.Entity.Entity._referencedPackages
				elif isinstance(designUnit, PackageBody):
					referencedPackages = designUnit.Package.Package._referencedPackages
				else:
					raise VHDLModelException()  # FIXME: exception message

				for packageIdentifier, package in referencedPackages.items():
					designUnit._referencedPackages[packageIdentifier] = package

			for packageReference in designUnit.PackageReferences:
				# A use clause can have multiple comma-separated references
				for packageMemberSymbol in packageReference.Symbols:
					if isinstance(packageMemberSymbol, PackageReferenceSymbol):
						packageName = packageMemberSymbol.Name
					elif isinstance(packageMemberSymbol, (AllPackageMembersReferenceSymbol, PackageMemberReferenceSymbol)):
						packageName = packageMemberSymbol.Name.Prefix

					libraryName = packageName.Prefix

					libraryIdentifier = libraryName.NormalizedIdentifier
					packageIdentifier = packageName.NormalizedIdentifier

					# In case work is used, resolve to the real library name.
					if libraryIdentifier == "work":
						library: Library = designUnit.Library
						libraryIdentifier = library.NormalizedIdentifier
					elif libraryIdentifier not in designUnit._referencedLibraries:
						# TODO: This check doesn't trigger if it's the working library.
						raise VHDLModelException(f"Use clause references library '{libraryName.Identifier}', which was not referenced by a library clause.")
					else:
						library = self._libraries[libraryIdentifier]

					try:
						package = library._packages[packageIdentifier]
					except KeyError:
						ex = VHDLModelException(f"Package '{packageName.Identifier}' not found in {'working ' if libraryName.NormalizedIdentifier == 'work' else ''}library '{library.Identifier}'.")
						ex.add_note(f"Caused in design unit '{designUnit}' in file '{designUnit.Document}'.")
						raise ex

					# FIXME: check if package isn't a generic package
					packageMemberSymbol.Package = package

					# TODO: warn duplicate package reference
					designUnit._referencedPackages[libraryIdentifier][packageIdentifier] = package

					dependency = designUnit._dependencyVertex.EdgeToVertex(package._dependencyVertex, edgeValue=packageReference)
					dependency["kind"] = DependencyGraphEdgeKind.UseClause

					# TODO: update the namespace with visible members
					if isinstance(packageMemberSymbol, PackageReferenceSymbol):
						designUnit._namespace.AddImport(packageIdentifier, package)

					elif isinstance(packageMemberSymbol, AllPackageMembersReferenceSymbol):
						WarningCollector.Raise(NotImplementedWarning(
							"Handling of 'myLib.myPackage.all'. Exception: components are handled.",
							item=packageMemberSymbol
						))

						for componentIdentifier, component in package._components.items():
							designUnit._namespace.AddImport(componentIdentifier, component)

					elif isinstance(packageMemberSymbol, PackageMemberReferenceSymbol):
						WarningCollector.Raise(NotImplementedWarning(
							"Handling of 'myLib.myPackage.mySymbol'.",
							item=packageMemberSymbol
						))

					else:
						ex = VHDLModelException("Unknown package reference symbol type.")
						ex.add_note(f"Got type '{getFullyQualifiedName(packageMemberSymbol)}'.")
						raise ex

	def LinkContextReferences(self) -> None:
		"""
		Link all context references (context clause) to the matching context.

		.. rubric:: Algorithm

		1. Iterate all design units:

		   * Iterate all context references in the design unit:

		     * Iterate each context symbol within the context reference.

		       1. Get the library identifier from the symbol.
		       2. Get the context identifier from the symbol.
		       3. Resolve library:

		          * If library name is ``work``, get library from design unit.
		          * If library name is not in design unit's ``_referencedLibraries``, raise an exception.
		          * Otherwise, lookup library by name in design.

		       4. Resolve context:

		          * Lookup context by name in library.

		       5. Update design unit:

		          * Update the context symbol's target with the referenced context.
		          * Add an entry in the design unit's ``_referencedContexts`` dictionary referencing the referenced context.
		          * Add an edge in the dependency graph from design unit to the referenced context.

		2. Iterate all context vertices in the dependency graph (``_dependencyGraph``) in topological order:

		   * Get the context from the context vertex.
		   * Iterate all predecessor vertices (design unit vertices) of the context vertex:

		     1. Get the design unit from design unit vertex.
		     2. Iterate referenced libraries of the context:

		        * Add an entry in the design unit's ``_referencedLibraries`` dictionary referencing the referenced library.
		        * Add an empty dictionary in the design unit's ``_referencedPackages`` dictionary.

		     3. Iterate referenced packages of the context:

		        * Raise an exception if package name is already listed in ``_referencedPackages``.
		        * Add an entry in the design unit's ``_referencedPackages`` dictionary referencing the referenced package.

		.. seealso::

		   :meth:`LinkLibraryReferences`
		     Link *library clause*.
		   :meth:`LinkPackageReferences`
		     Link *use clause*.
		   :meth:`AnalyzeDependencies`
		     Analyze dependencies and link relations.
		"""
		for designUnit in self.IterateDesignUnits():
			for contextReference in designUnit._contextReferences:
				# A context reference can have multiple comma-separated references
				for contextSymbol in contextReference.Symbols:
					libraryName = contextSymbol.Name.Prefix

					libraryIdentifier = libraryName.NormalizedIdentifier
					contextIdentifier = contextSymbol.Name.NormalizedIdentifier

					# In case work is used, resolve to the real library name.
					if libraryIdentifier == "work":
						referencedLibrary = designUnit.Library
						libraryIdentifier = referencedLibrary.NormalizedIdentifier
					elif libraryIdentifier not in designUnit._referencedLibraries:
						# TODO: This check doesn't trigger if it's the working library.
						raise VHDLModelException(f"Context reference references library '{libraryName.Identifier}', which was not referenced by a library clause.")
					else:
						referencedLibrary = self._libraries[libraryIdentifier]

					try:
						referencedContext = referencedLibrary._contexts[contextIdentifier]
					except KeyError:
						raise VHDLModelException(f"Context '{contextSymbol.Name.Identifier}' not found in {'working ' if libraryName.NormalizedIdentifier == 'work' else ''}library '{referencedLibrary.Identifier}'.")

					contextSymbol.Package = referencedContext

					# TODO: warn duplicate referencedContext reference
					designUnit._referencedContexts[libraryIdentifier][contextIdentifier] = referencedContext

					dependency = designUnit._dependencyVertex.EdgeToVertex(referencedContext._dependencyVertex, edgeValue=contextReference)
					dependency["kind"] = DependencyGraphEdgeKind.ContextReference

		for vertex in self._dependencyGraph.IterateTopologically(predicate=lambda v: v["kind"] is DependencyGraphVertexKind.Context):
			context: Context = vertex.Value
			for designUnitVertex in vertex.IteratePredecessorVertices():  # TODO: should this be filtered to exclude non-contexts?
				designUnit: DesignUnit = designUnitVertex.Value
				for libraryIdentifier, library in context._referencedLibraries.items():
					# if libraryIdentifier in designUnit._referencedLibraries:
					# 	raise VHDLModelException(f"Referenced library '{library.Identifier}' already exists in references for design unit '{designUnit.Identifier}'.")

					designUnit._referencedLibraries[libraryIdentifier] = library
					designUnit._referencedPackages[libraryIdentifier] = {}

				for libraryIdentifier, packages in context._referencedPackages.items():
					for packageIdentifier, package in packages.items():
						if packageIdentifier in designUnit._referencedPackages:
							raise VHDLModelException(f"Referenced package '{package.Identifier}' already exists in references for design unit '{designUnit.Identifier}'.")

						designUnit._referencedPackages[libraryIdentifier][packageIdentifier] = package

	def LinkComponents(self) -> None:
		"""
		Link components to matching entities found in same VHDL library.

		.. rubric:: Algorithm

		1. Iterate all design units with component declarations (packages and architectures):

		   1. Iterate all component declarations in a package or architecture:

		      * Check if an entity with matching name can be found in the VHDL library the package is declared within. If
		        found, set the component's entity reference to that entity, otherwise check if blackboxes are allowed for
		        that component. If so, mark the component as a blackbox, otherwise, raise an exception.

		   2. Iterate concurrent statements with declaration regions (block statements, generate statements) if the design
		      unit is an architecture:

		      * If the statement is an :class:`IfGenerateStatement`:

		        1. Iterate declared components in the :class:`IfGenerateBranch`.
		        2. Iterate declared components in each :class:`ElIfGenerateBranch`.
		        3. Iterate declared components in the :class:`ElseGenerateBranch` if it exists.

		      * If the statement is an :class:`ForGenerateStatement`:

		        1. Iterate declared components.

		      * If the statement is an :class:`CaseGenerateStatement`:

		        1. Iterate declared components.
		        2. Iterate

		:raises VHDLModelException: If no entity is found for a component, which doesn't allow blackboxes.

		.. seealso::

		   :meth:`LinkInstantiations`
		     Link instantiations to components and entities.
		   :meth:`AnalyzeDependencies`
		     Analyze dependencies in a design (calls this method).
		"""
		for library, component in self._IterateComponents():
			# QUESTION: Add link in dependency graph as dashed line from component to entity?
			#           Currently, component has no _dependencyVertex field
			try:
				entity = library._entities[component.NormalizedIdentifier]
			except KeyError:
				if component.AllowBlackbox:
					component._isBlackbox = True
					continue
				else:
					raise VHDLModelException(
						f"Entity '{component.Identifier}' not found for component '{component.Identifier}' in library '{library.Identifier}'.")

			component.Entity = entity

	def _IterateComponents(self) -> Generator[tuple[Library, Component], None, None]:
		"""
		Iterate all components of packages and architectures, including the components declared in blocks and generate
		statements nested in architectures.

		:returns: A generator to iterate tuples of the library of the design unit and a component.
		"""
		def iterateStatements(concurrent: ConcurrentStatementsMixin) -> Generator[Component, None, None]:
			"""
			Nested function for recursion.

			:param concurrent: The language construct containing concurrent statements.
			:returns:          A generator to iterate the components declared in the nested statements.
			"""
			for statement in concurrent._statements:
				if isinstance(statement, IfGenerateStatement):
					yield from iterateDeclaredItems(statement._ifBranch)
					yield from iterateStatements(statement._ifBranch)
					for branch in statement._elsifBranches:
						yield from iterateDeclaredItems(branch)
						yield from iterateStatements(branch)

					if (branch := statement._elseBranch) is not None:
						yield from iterateDeclaredItems(branch)
						yield from iterateStatements(branch)
				elif isinstance(statement, ForGenerateStatement):
					yield from iterateDeclaredItems(statement)
					yield from iterateStatements(statement)
				elif isinstance(statement, CaseGenerateStatement):
					for case in statement._cases:
						yield from iterateDeclaredItems(case)
						yield from iterateStatements(case)
				elif isinstance(statement, ConcurrentBlockStatement):
					yield from iterateDeclaredItems(statement)
					yield from iterateStatements(statement)

		def iterateDeclaredItems(declarationRegion: ConcurrentDeclarationRegionMixin) -> Generator[Component, None, None]:
			"""
			Nested function iterating the components declared in a declaration region.

			:param declarationRegion: The declaration region.
			:returns:                 A generator to iterate the declared components.
			"""
			for item in declarationRegion._declaredItems:
				if isinstance(item, Component):
					yield item

		for designUnit in self.IterateDesignUnits(DesignUnitKind.Package | DesignUnitKind.Architecture):  # type: Union[Package, Architecture]
			library = designUnit._parent
			for component in designUnit._components.values():
				yield library, component

			if isinstance(designUnit, Architecture):
				for component in iterateStatements(designUnit):
					yield library, component

	def LinkInstantiations(self) -> None:
		for architecture in self.IterateDesignUnits(DesignUnitKind.Architecture):  # type: Architecture
			for instance in architecture.IterateInstantiations():
				if isinstance(instance, EntityInstantiation):
					entityName =  instance.Entity.Name
					libraryName = entityName.Prefix
					if libraryName is None:
						ex = VHDLModelException(f"Direct entity instantiation '{instance.Label}' has no library prefix.")
						ex.add_note(f"Use a selected name like 'work.{entityName.Identifier}'.")
						ex.add_note("Entities made visible by a use clause aren't supported.")
						raise ex

					libraryIdentifier = libraryName.Identifier
					normalizedLibraryIdentifier = libraryName.NormalizedIdentifier
					if normalizedLibraryIdentifier == "work":
						libraryIdentifier = architecture.Library.Identifier
						normalizedLibraryIdentifier = architecture.Library.NormalizedIdentifier
					elif normalizedLibraryIdentifier not in architecture._referencedLibraries:
						ex = VHDLModelException(
							f"Referenced library '{libraryIdentifier}' in direct entity instantiation '{instance.Label}: "
							f"entity {libraryName.Identifier}.{entityName.Identifier}' not found in architecture '{architecture!r}'."
						)
						ex.add_note(f"Add a library reference to the architecture or entity using a library clause like: 'library {libraryIdentifier};'.")
						raise ex

					try:
						library = self._libraries[normalizedLibraryIdentifier]
					except KeyError:
						ex = VHDLModelException(
							f"Referenced library '{libraryIdentifier}' in direct entity instantiation '{instance.Label}: "
							f"entity {libraryName.Identifier}.{entityName.Identifier}' not found in design."
						)
						ex.add_note(f"No design units were parsed into library '{libraryIdentifier}'. Thus it doesn't exist in design.")
						raise ex

					try:
						entity = library._entities[instance.Entity.Name.NormalizedIdentifier]
					except KeyError:
						ex = VHDLModelException(f"Referenced entity '{instance.Entity.Name.Identifier}' in direct entity instantiation '{instance.Label}: entity {instance.Entity.Name.Prefix.Identifier}.{instance.Entity.Name.Identifier}' not found in {'working ' if instance.Entity.Name.Prefix.NormalizedIdentifier == 'work' else ''}library '{libraryIdentifier}'.")
						libs = [library.Identifier for library in self._libraries.values() for entityIdentifier in library._entities.keys() if entityIdentifier == instance.Entity.Name.NormalizedIdentifier]
						if libs:
							ex.add_note(f"Found entity '{instance.Entity!s}' in other libraries: {', '.join(libs)}")
						raise ex

					instance.Entity.Entity = entity

					dependency = architecture._dependencyVertex.EdgeToVertex(entity._dependencyVertex, edgeValue=instance)
					dependency["kind"] = DependencyGraphEdgeKind.EntityInstantiation

				elif isinstance(instance, ComponentInstantiation):
					component = instance._parent._namespace.FindComponent(instance.Component)

					instance.Component.Component = component

					if not component.IsBlackbox:
						dependency = architecture._dependencyVertex.EdgeToVertex(component.Entity._dependencyVertex, edgeValue=instance)
						dependency["kind"] = DependencyGraphEdgeKind.ComponentInstantiation
					else:
						WarningCollector.Raise(BlackboxWarning(
							f"Blackbox caused by '{instance.Label}: {instance.Component.Name}'.",
							instance=instance,
							component=component
						))

				elif isinstance(instance, ConfigurationInstantiation):
					WarningCollector.Raise(NotImplementedWarning(
						f"Configuration instantiation of '{instance.Label}: {instance.Configuration}'.",
						item=instance
					))

	def IndexPackages(self) -> None:
		"""
		Index all declared items in all packages in all libraries.

		.. rubric:: Algorithm

		1. Iterate all libraries:

		   1. Iterate all packages |br|
		      |rarr| :meth:`pyVHDLModel.Library.IndexPackages`

		      * Index all declared items in that package. |br|
		        |rarr| :meth:`pyVHDLModel.DesignUnit.Package.IndexDeclaredItems`

		.. seealso::

		   :meth:`IndexPackageBodies`
		     Index all declared items in all package bodies in all libraries.
		   :meth:`IndexEntities`
		     Index all declared items in all entities in all libraries.
		   :meth:`IndexArchitectures`
		     Index all declared items in all architectures in all libraries.

		:raises UnhandledCriticalWarningError: If an identifier is declared twice in a declarative region and no
		                                       :class:`~pyTooling.Warning.WarningCollector` collects the
		                                       :exc:`~pyVHDLModel.Exception.DuplicateDeclarationWarning`.
		"""
		for library in self._libraries.values():
			library.IndexPackages()

	def IndexPackageBodies(self) -> None:
		"""
		Index all declared items in all packages in all libraries.

		.. rubric:: Algorithm

		1. Iterate all libraries:

		   1. Iterate all packages |br|
		      |rarr| :meth:`pyVHDLModel.Library.IndexPackageBodies`

		      * Index all declared items in that package body. |br|
		        |rarr| :meth:`pyVHDLModel.DesignUnit.PackageBody.IndexDeclaredItems`

		.. seealso::

		   :meth:`IndexPackages`
		     Index all declared items in all packages in all libraries.
		   :meth:`IndexEntities`
		     Index all declared items in all entities in all libraries.
		   :meth:`IndexArchitectures`
		     Index all declared items in all architectures in all libraries.

		:raises UnhandledCriticalWarningError: If an identifier is declared twice in a declarative region and no
		                                       :class:`~pyTooling.Warning.WarningCollector` collects the
		                                       :exc:`~pyVHDLModel.Exception.DuplicateDeclarationWarning`.
		"""
		for library in self._libraries.values():
			library.IndexPackageBodies()

	def IndexEntities(self) -> None:
		"""
		Index all declared items in all packages in all libraries.

		.. rubric:: Algorithm

		1. Iterate all libraries:

		   1. Iterate all packages |br|
		      |rarr| :meth:`pyVHDLModel.Library.IndexEntities`

		      * Index all declared items in that entity. |br|
		        |rarr| :meth:`pyVHDLModel.DesignUnit.Entity.IndexDeclaredItems`

		.. seealso::

		   :meth:`IndexPackages`
		     Index all declared items in all packages in all libraries.
		   :meth:`IndexPackageBodies`
		     Index all declared items in all package bodies in all libraries.
		   :meth:`IndexArchitectures`
		     Index all declared items in all architectures in all libraries.

		:raises UnhandledCriticalWarningError: If an identifier is declared twice in a declarative region and no
		                                       :class:`~pyTooling.Warning.WarningCollector` collects the
		                                       :exc:`~pyVHDLModel.Exception.DuplicateDeclarationWarning`.
		"""
		for library in self._libraries.values():
			library.IndexEntities()

	def IndexArchitectures(self) -> None:
		"""
		Index all declared items in all packages in all libraries.

		.. rubric:: Algorithm

		1. Iterate all libraries:

		   1. Iterate all packages |br|
		      |rarr| :meth:`pyVHDLModel.Library.IndexArchitectures`

		      * Index all declared items in that architecture. |br|
		        |rarr| :meth:`pyVHDLModel.DesignUnit.Architecture.IndexDeclaredItems`

		.. seealso::

		   :meth:`IndexPackages`
		     Index all declared items in all packages in all libraries.
		   :meth:`IndexPackageBodies`
		     Index all declared items in all package bodies in all libraries.
		   :meth:`IndexEntities`
		     Index all declared items in all entities in all libraries.

		:raises UnhandledCriticalWarningError: If an identifier is declared twice in a declarative region and no
		                                       :class:`~pyTooling.Warning.WarningCollector` collects the
		                                       :exc:`~pyVHDLModel.Exception.DuplicateDeclarationWarning`.
		"""
		for library in self._libraries.values():
			library.IndexArchitectures()

	def CreateHierarchyGraph(self) -> None:
		"""
		Create the hierarchy graph from dependency graph.

		.. rubric:: Algorithm

		1. Iterate all vertices corresponding to entities and architectures in the dependency graph:

		   * Copy these vertices to the hierarchy graph and create a bidirectional linking. |br|
		     In addition, set the referenced design unit's :attr:`~pyVHDLModel.Document._hierarchyVertex` field to reference the copied vertex.

		     * Add a key-value-pair called ``hierarchyVertex`` to the dependency graph's vertex.
		     * Add a key-value-pair called ``dependencyVertex`` to the hierarchy graph's vertex.

		2. Iterate all architectures ...

		   .. todo:: Design::CreateHierarchyGraph describe algorithm

		   1. Iterate all outbound edges

		      .. todo:: Design::CreateHierarchyGraph describe algorithm
		"""
		# Copy all entity and architecture vertices from dependency graph to hierarchy graph and double-link them
		entityArchitectureFilter = lambda v: v["kind"] in DependencyGraphVertexKind.Entity | DependencyGraphVertexKind.Architecture
		for vertex in self._dependencyGraph.IterateVertices(predicate=entityArchitectureFilter):
			hierarchyVertex = vertex.Copy(self._hierarchyGraph, copyDict=True, linkingKeyToOriginalVertex="dependencyVertex", linkingKeyFromOriginalVertex="hierarchyVertex")
			vertex.Value._hierarchyVertex = hierarchyVertex

		# Copy implementation edges from
		for hierarchyArchitectureVertex in self._hierarchyGraph.IterateVertices(predicate=lambda v: v["kind"] is DependencyGraphVertexKind.Architecture):
			for dependencyEdge in hierarchyArchitectureVertex["dependencyVertex"].IterateOutboundEdges():
				kind: DependencyGraphEdgeKind = dependencyEdge["kind"]
				if DependencyGraphEdgeKind.Implementation in kind:
					hierarchyDestinationVertex = dependencyEdge.Destination["hierarchyVertex"]
					newEdge = hierarchyArchitectureVertex.EdgeFromVertex(hierarchyDestinationVertex)
				elif DependencyGraphEdgeKind.Instantiation in kind:
					hierarchyDestinationVertex = dependencyEdge.Destination["hierarchyVertex"]

					# FIXME: avoid parallel edges, to graph can be converted to a tree until "real" hierarchy is computed (unrole generics and blocks)
					if hierarchyArchitectureVertex.HasEdgeToDestination(hierarchyDestinationVertex):
						continue

					newEdge = hierarchyArchitectureVertex.EdgeToVertex(hierarchyDestinationVertex)
				else:
					continue

				newEdge["kind"] = kind

	def ComputeCompileOrder(self) -> None:
		def predicate(edge: Edge) -> bool:
			return (
				DependencyGraphEdgeKind.Implementation in edge["kind"] or
				DependencyGraphEdgeKind.Instantiation in edge["kind"] or
				DependencyGraphEdgeKind.UseClause in edge["kind"] or
				DependencyGraphEdgeKind.ContextReference in edge["kind"]
			) and edge.Destination["predefined"] is False

		for edge in self._dependencyGraph.IterateEdges(predicate=predicate):
			sourceDocument:      Document = edge.Source.Value.Document
			destinationDocument: Document = edge.Destination.Value.Document

			sourceVertex =      sourceDocument._compileOrderVertex
			destinationVertex = destinationDocument._compileOrderVertex

			# Don't add self-edges
			if sourceVertex is destinationVertex:
				continue
			# Don't add parallel edges
			elif sourceVertex.HasEdgeToDestination(destinationVertex):
				continue

			e = sourceVertex.EdgeToVertex(destinationVertex)
			e["kind"] = DependencyGraphEdgeKind.CompileOrder

			e = sourceVertex["dependencyVertex"].EdgeToVertex(destinationVertex["dependencyVertex"])
			e["kind"] = DependencyGraphEdgeKind.CompileOrder

	def IterateDocumentsInCompileOrder(self) -> Generator[Document, None, None]:
		"""
		Iterate all document in compile-order.

		.. rubric:: Algorithm

		* Check if compile-order graph was populated with vertices and its vertices are linked by edges.

		1. Iterate compile-order graph in topological order. |br|
		   :meth:`pyTooling.Graph.Graph.IterateTopologically`

		   * yield the compiler-order vertex' referenced document.

		:returns:                   A generator to iterate all documents in compile-order in the design.
		:raises VHDLModelException: If compile-order was not computed.

		.. seealso::

		   .. todo:: missing text

		      :meth:`pyVHDLModel.Design.ComputeCompileOrder`

		"""
		if self._compileOrderGraph.EdgeCount < self._compileOrderGraph.VertexCount - 1:
			raise VHDLModelException("Compile order is not yet computed from dependency graph.")

		for compileOrderNode in self._compileOrderGraph.IterateTopologically():
			yield compileOrderNode.Value

	def GetUnusedDesignUnits(self) -> list[DesignUnit]:
		WarningCollector.Raise(NotImplementedWarning("Compute unused design units."))

	def __repr__(self) -> str:
		"""
		Formats a representation of the design.

		**Format:** ``Document: 'my_design'``

		:returns: String representation of the design.
		"""
		return f"Design: {self._name}"

	__str__ = __repr__


@export
class Library(ModelEntity, NamedEntityMixin, DocumentedEntityMixin, AllowBlackboxMixin):
	"""
	A ``Library`` represents a VHDL library. It contains all *primary* and *secondary* design units.

	.. seealso::

	   * :class:`Predefined library <pyVHDLModel.Predefined.PredefinedLibrary>`
	"""

	_contexts:       dict[str, Context]                  #: Dictionary of all contexts defined in a library.
	_configurations: dict[str, Configuration]            #: Dictionary of all configurations defined in a library.
	_entities:       dict[str, Entity]                   #: Dictionary of all entities defined in a library.
	_architectures:  dict[str, dict[str, Architecture]]  #: Dictionary of all architectures defined in a library.
	_packages:       dict[str, Package]                  #: Dictionary of all packages defined in a library.
	_packageBodies:  dict[str, PackageBody]              #: Dictionary of all package bodies defined in a library.

	_dependencyVertex: Vertex  #: Reference to the vertex in the dependency graph representing the library. |br| This reference is set by :meth:`~pyVHDLModel.Design.CreateDependencyGraph`.

	def __init__(
		self,
		identifier:    str,
		documentation: Nullable[str] = None,
		allowBlackbox: Nullable[bool] = None,
		parent:        Nullable[ModelEntity] = None
	) -> None:
		"""
		Initialize a VHDL library.

		:param identifier:    Name of the VHDL library.
		:param documentation: Documentation of this VHDL library, if the caller has one to supply.
		:param allowBlackbox: Specify if blackboxes are allowed in this design.
		:param parent:        The parent model entity (design) of this VHDL library.
		"""
		super().__init__(parent)
		NamedEntityMixin.__init__(self, identifier)
		DocumentedEntityMixin.__init__(self, documentation)
		AllowBlackboxMixin.__init__(self, allowBlackbox)

		self._contexts =        {}
		self._configurations =  {}
		self._entities =        {}
		self._architectures =   {}
		self._packages =        {}
		self._packageBodies =   {}

		self._dependencyVertex = None

	@property
	def Documentation(self) -> Nullable[str]:
		"""
		Property to access the library's documentation (:attr:`_documentation`).

		.. hint::

		   Unlike every other documented entity, a library's documentation cannot come from VHDL source:
		   the language has no library declaration to attach a comment to. It is therefore settable, so a
		   caller can supply one from elsewhere - a compile-order file, a project description, ...

		:returns: Associated documentation of this VHDL library.
		"""
		return self._documentation

	@Documentation.setter
	def Documentation(self, documentation: Nullable[str]) -> None:
		self._documentation = documentation

	@readonly
	def Contexts(self) -> dict[str, Context]:
		"""
		Read-only property to access the dictionary of all context declarations in this library (:attr:`_contexts`).

		:returns: Dictionary of all contexts, indexed by normalized identifier.
		"""
		return self._contexts

	@readonly
	def Configurations(self) -> dict[str, Configuration]:
		"""
		Read-only property to access the dictionary of all configuration declarations in this library (:attr:`_configurations`).

		:returns: Dictionary of all configurations, indexed by normalized identifier.
		"""
		return self._configurations

	@readonly
	def Entities(self) -> dict[str, Entity]:
		"""
		Read-only property to access the dictionary of all entity declarations in this library (:attr:`_entities`).

		:returns: Dictionary of all entities, indexed by normalized identifier.
		"""
		return self._entities

	@readonly
	def Architectures(self) -> dict[str, dict[str, Architecture]]:
		"""
		Read-only property to access the dictionary of all architecture declarations in this library (:attr:`_architectures`).

		:returns: Dictionary of all architectures, indexed by normalized entity identifier, then by normalized
		          architecture identifier.
		"""
		return self._architectures

	@readonly
	def Packages(self) -> dict[str, Package]:
		"""
		Read-only property to access the dictionary of all package declarations in this library (:attr:`_packages`).

		:returns: Dictionary of all packages, indexed by normalized identifier.
		"""
		return self._packages

	@readonly
	def PackageBodies(self) -> dict[str, PackageBody]:
		"""
		Read-only property to access the dictionary of all package body declarations in this library (:attr:`_packageBodies`).

		:returns: Dictionary of all package bodies, indexed by normalized identifier.
		"""
		return self._packageBodies

	@readonly
	def DependencyVertex(self) -> Vertex:
		"""
		Read-only property to access the corresponding dependency vertex (:attr:`_dependencyVertex`).

		The dependency vertex references this library by its value field.

		:returns: The corresponding dependency vertex.
		"""
		return self._dependencyVertex

	def IterateDesignUnits(self, filter: DesignUnitKind = DesignUnitKind.All) -> Generator[DesignUnit, None, None]:
		"""
		Iterate all design units in the library.

		A union of :class:`DesignUnitKind` values can be given to filter the returned result for suitable design units.

		.. rubric:: Algorithm

		1. Iterate all contexts in that library.
		2. Iterate all packages in that library.
		3. Iterate all package bodies in that library.
		4. Iterate all entities in that library.
		5. Iterate all architectures in that library.
		6. Iterate all configurations in that library.

		:param filter: An enumeration with possibly multiple flags to filter the returned design units.
		:returns:      A generator to iterate all matched design units in the library.

		.. seealso::

		   :meth:`pyVHDLModel.Design.IterateDesignUnits`
		     Iterate all design units in the design.
		   :meth:`pyVHDLModel.Document.IterateDesignUnits`
		     Iterate all design units in the document.
		"""
		if DesignUnitKind.Context in filter:
			for context in self._contexts.values():
				yield context

		if DesignUnitKind.Package in filter:
			for package in self._packages.values():
				yield package

		if DesignUnitKind.PackageBody in filter:
			for packageBody in self._packageBodies.values():
				yield packageBody

		if DesignUnitKind.Entity in filter:
			for entity in self._entities.values():
				yield entity

		if DesignUnitKind.Architecture in filter:
			for architectures in self._architectures.values():
				for architecture in architectures.values():
					yield architecture

		if DesignUnitKind.Configuration in filter:
			for configuration in self._configurations.values():
				yield configuration

		# for verificationProperty in self._verificationUnits.values():
		# 	yield verificationProperty
		# for verificationUnit in self._verificationProperties.values():
		# 	yield entity
		# for verificationMode in self._verificationModes.values():
		# 	yield verificationMode

	def LinkArchitectures(self) -> None:
		"""
		Link all architectures to corresponding entities.

		.. rubric:: Algorithm

		1. Iterate all architecture groups (grouped per entity symbol's name).

		   * Check if entity symbol's name exists as an entity in this library.

		   1. For each architecture in the same architecture group:

		      * Add architecture to entities architecture dictionary :attr:`pyVHDLModel.DesignUnit.Entity._architectures`.
		      * Assign found entity to architecture's entity symbol :attr:`pyVHDLModel.DesignUnit.Architecture._entity`
		      * Set parent namespace of architecture's namespace to the entitie's namespace.
		      * Add an edge in the dependency graph from the architecture's corresponding dependency vertex to the entity's corresponding dependency vertex.

		:raises VHDLModelException: If entity name doesn't exist.
		:raises VHDLModelException: If architecture name already exists for entity.

		.. seealso::

		   :meth:`LinkPackageBodies`
		     Link all package bodies to corresponding packages.
		   :meth:`LinkPackageInstances`
		     Link all package instances to corresponding generic packages.
		"""
		for entityName, architecturesPerEntity in self._architectures.items():
			if entityName not in self._entities:
				architectureNames = "', '".join(architecturesPerEntity.keys())
				raise VHDLModelException(f"Entity '{entityName}' referenced by architecture(s) '{architectureNames}' doesn't exist in library '{self._identifier}'.")
			# TODO: search in other libraries to find that entity.
			# TODO: add code position

			entity = self._entities[entityName]
			for architecture in architecturesPerEntity.values():
				if architecture._normalizedIdentifier in entity._architectures:
					raise VHDLModelException(f"Architecture '{architecture._identifier}' already exists for entity '{entity._identifier}'.")
				# TODO: add code position of existing and current

				entity._architectures[architecture._normalizedIdentifier] = architecture
				architecture._entity.Entity = entity
				architecture._namespace.ParentNamespace = entity._namespace

				# add "architecture -> entity" relation in dependency graph
				dependency = architecture._dependencyVertex.EdgeToVertex(entity._dependencyVertex)
				dependency["kind"] = DependencyGraphEdgeKind.EntityImplementation

	def LinkPackageBodies(self) -> None:
		"""
		Link all package bodies to corresponding packages.

		.. rubric:: Algorithm

		1. Iterate all package bodies.

		   * Check if package body symbol's name exists as a package in this library.
		   * Add package body to package :attr:`pyVHDLModel.DesignUnit.Package._packageBody`.
		   * Assign found package to package body's package symbol :attr:`pyVHDLModel.DesignUnit.PackageBody._package`
		   * Set parent namespace of package body's namespace to the package's namespace.
		   * Add an edge in the dependency graph from the package body's corresponding dependency vertex to the package's corresponding dependency vertex.

		:raises VHDLModelException: If package name doesn't exist.

		.. seealso::

		   :meth:`LinkArchitectures`
		     Link all architectures to corresponding entities.
		   :meth:`LinkPackageInstances`
		     Link all package instances to corresponding generic packages.
		"""
		for packageBodyName, packageBody in self._packageBodies.items():
			if packageBodyName not in self._packages:
				raise VHDLModelException(f"Package '{packageBodyName}' referenced by package body '{packageBodyName}' doesn't exist in library '{self._identifier}'.")

			package = self._packages[packageBodyName]
			package._packageBody = packageBody    # TODO: add warning if package had already a body, which is now replaced
			packageBody._package.Package = package
			packageBody._namespace.ParentNamespace = package._namespace

			# add "package body -> package" relation in dependency graph
			dependency = packageBody._dependencyVertex.EdgeToVertex(package._dependencyVertex)
			dependency["kind"] = DependencyGraphEdgeKind.PackageImplementation

	def LinkPackageInstances(self) -> None:
		"""
		Link all package instances to corresponding generic packages.

		.. rubric:: Algorithm

		1. Iterate all package instances.

		   .. todo::

		      * Check if package body symbol's name exists as a package in this library.
		      * Add package body to package :attr:`pyVHDLModel.DesignUnit.Package._packageBody`.
		      * Assign found package to package body's package symbol :attr:`pyVHDLModel.DesignUnit.PackageBody._package`
		      * Set parent namespace of package body's namespace to the package's namespace.
		      * Add an edge in the dependency graph from the package body's corresponding dependency vertex to the package's corresponding dependency vertex.

		:raises VHDLModelException: If generic package name doesn't exist.

		.. seealso::

		   :meth:`LinkArchitectures`
		     Link all architectures to corresponding entities.
		   :meth:`LinkPackageBodies`
		     Link all package bodies to corresponding packages.
		"""
		for packageInstanceName, packageInstance in self._packages.items():
			if isinstance(packageInstance, PackageInstantiation):
				packageSymbol = packageInstance._packageReference
				packageName = packageSymbol.Name
				libraryName = packageName.Prefix

				libraryIdentifier = libraryName.NormalizedIdentifier
				packageIdentifier = packageName.NormalizedIdentifier

				# In case work is used, resolve to the real library name.
				if libraryIdentifier == "work":
					library: Library = self
					libraryIdentifier = library.NormalizedIdentifier
				elif libraryIdentifier not in self._parent._libraries:
					# TODO: This check doesn't trigger if it's the working library.
					raise VHDLModelException(f"Package instantiation of '{packageInstanceName}' references library '{libraryName.Identifier}', which cannot be found in design.")
				else:
					library = self._parent._libraries[libraryIdentifier]

				try:
					package = library._packages[packageIdentifier]
				except KeyError:
					ex = VHDLModelException(
						f"Package '{packageName.Identifier}' not found in {'working ' if libraryName.NormalizedIdentifier == 'work' else ''}library '{library.Identifier}'.")
					ex.add_note(f"Caused in library '{self}' in file '{packageInstance.Document}'.")
					raise ex

				# FIXME: check if package is a generic package
				if package.GenericCount == 0:
					raise VHDLModelException(f"Package '{libraryName.Identifier}.{packageName.Identifier}' referenced by '{self._identifier}.{packageInstanceName}' is not a generic package.")

				packageSymbol.Package = package

				dependency = packageInstance._dependencyVertex.EdgeToVertex(package._dependencyVertex)  # , edgeValue=packageReference)
				dependency["kind"] = DependencyGraphEdgeKind.PackageInstantiation

				packageInstance.Instantiate()

	def IndexPackages(self) -> None:
		"""
		Index declared items in all packages.

		.. rubric:: Algorithm

		1. Iterate all packages:

		   * Index all declared items. |br|
		     |rarr| :meth:`pyVHDLModel.DesignUnit.Package.IndexDeclaredItems`

		.. seealso::

		   :meth:`IndexPackageBodies`
		     Index all declared items in a package body.
		   :meth:`IndexEntities`
		     Index all declared items in an entity.
		   :meth:`IndexArchitectures`
		     Index all declared items in an architecture.

		:raises UnhandledCriticalWarningError: If an identifier is declared twice in a declarative region and no
		                                       :class:`~pyTooling.Warning.WarningCollector` collects the
		                                       :exc:`~pyVHDLModel.Exception.DuplicateDeclarationWarning`.
		"""
		for package in self._packages.values():
			if isinstance(package, Package):
				package.IndexDeclaredItems()

	def IndexPackageBodies(self) -> None:
		"""
		Index declared items in all package bodies.

		.. rubric:: Algorithm

		1. Iterate all package bodies:

		   * Index all declared items. |br|
		     |rarr| :meth:`pyVHDLModel.DesignUnit.PackageBody.IndexDeclaredItems`

		.. seealso::

		   :meth:`IndexPackages`
		     Index all declared items in a package.
		   :meth:`IndexEntities`
		     Index all declared items in an entity.
		   :meth:`IndexArchitectures`
		     Index all declared items in an architecture.

		:raises UnhandledCriticalWarningError: If an identifier is declared twice in a declarative region and no
		                                       :class:`~pyTooling.Warning.WarningCollector` collects the
		                                       :exc:`~pyVHDLModel.Exception.DuplicateDeclarationWarning`.
		"""
		for packageBody in self._packageBodies.values():
			packageBody.IndexDeclaredItems()

	def IndexEntities(self) -> None:
		"""
		Index declared items in all entities.

		.. rubric:: Algorithm

		1. Iterate all entities:

		   * Index all declared items. |br|
		     |rarr| :meth:`pyVHDLModel.DesignUnit.Entity.IndexDeclaredItems`

		.. seealso::

		   :meth:`IndexPackages`
		     Index all declared items in a package.
		   :meth:`IndexPackageBodies`
		     Index all declared items in a package body.
		   :meth:`IndexArchitectures`
		     Index all declared items in an architecture.

		:raises UnhandledCriticalWarningError: If an identifier is declared twice in a declarative region and no
		                                       :class:`~pyTooling.Warning.WarningCollector` collects the
		                                       :exc:`~pyVHDLModel.Exception.DuplicateDeclarationWarning`.
		"""
		for entity in self._entities.values():
			entity.IndexDeclaredItems()

	def IndexArchitectures(self) -> None:
		"""
		Index declared items in all architectures.

		.. rubric:: Algorithm

		1. Iterate all architectures:

		   * Index all declared items. |br|
		     |rarr| :meth:`pyVHDLModel.DesignUnit.Architecture.IndexDeclaredItems`

		.. seealso::

		   :meth:`IndexPackages`
		     Index all declared items in a package.
		   :meth:`IndexPackageBodies`
		     Index all declared items in a package body.
		   :meth:`IndexEntities`
		     Index all declared items in an entity.

		:raises UnhandledCriticalWarningError: If an identifier is declared twice in a declarative region and no
		                                       :class:`~pyTooling.Warning.WarningCollector` collects the
		                                       :exc:`~pyVHDLModel.Exception.DuplicateDeclarationWarning`.
		"""
		for architectures in self._architectures.values():
			for architecture in architectures.values():
				architecture.IndexDeclaredItems()
				architecture.IndexStatements()

	def __repr__(self) -> str:
		"""
		Formats a representation of the library.

		**Format:** ``Library: 'my_library'``

		:returns: String representation of the library.
		"""
		return f"Library: '{self._identifier}'"

	__str__ = __repr__


@export
class Document(ModelEntity, DocumentedEntityMixin):
	"""A ``Document`` represents a sourcefile. It contains *primary* and *secondary* design units."""

	_path:                   Path                                #: Path to the document.
	_vhdlVersion:            VHDLVersion                         #: VHDL version used for analyzing this source file.
	_library:                Library                             #: VHDL library used for analyzing the source file's content into.
	_designUnits:            list[DesignUnit]                    #: List of all design units defined in a document.
	_contexts:               dict[str, Context]                  #: Dictionary of all contexts defined in a document.
	_configurations:         dict[str, Configuration]            #: Dictionary of all configurations defined in a document.
	_entities:               dict[str, Entity]                   #: Dictionary of all entities defined in a document.
	_architectures:          dict[str, dict[str, Architecture]]  #: Dictionary of all architectures defined in a document.
	_packages:               dict[str, Package]                  #: Dictionary of all packages defined in a document.
	_packageBodies:          dict[str, PackageBody]              #: Dictionary of all package bodies defined in a document.
	_verificationUnits:      dict[str, VerificationUnit]         #: Dictionary of all PSL verification units defined in a document.
	_verificationProperties: dict[str, VerificationProperty]     #: Dictionary of all PSL verification properties defined in a document.
	_verificationModes:      dict[str, VerificationMode]         #: Dictionary of all PSL verification modes defined in a document.

	_dependencyVertex:       Vertex  #: Reference to the vertex in the dependency graph representing the document. |br| This reference is set by :meth:`~pyVHDLModel.Design.CreateCompileOrderGraph`.
	_compileOrderVertex:     Vertex  #: Reference to the vertex in the compile-order graph representing the document. |br| This reference is set by :meth:`~pyVHDLModel.Design.CreateCompileOrderGraph`.

	def __init__(
		self,
		path:          Path,
		documentation: Nullable[str] = None,
		vhdlVersion:   VHDLVersion = VHDLVersion.VHDL2008,
		library:       Nullable[Library] = None,
		parent:        Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes a VHDL document.

		:param path:          Path to the document.
		:param documentation: The documentation comment associated with this declaration.
		:param vhdlVersion:   VHDL version used for analyzing this source file.
		:param library:       VHDL library used for analyzing the source file's content into.
		:param parent:        The parent model entity of this entity.
		:raises ValueError:   If parameter 'path' is None.
		:raises TypeError:    If parameter 'path' is not of type :class:`~pathlib.Path`.
		"""
		super().__init__(parent)
		DocumentedEntityMixin.__init__(self, documentation)

		if path is None:
			raise ValueError("Parameter 'path' is None.")
		elif not isinstance(path, Path):
			ex = TypeError("Parameter 'path' is not of type 'Path'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(path)}'.")
			raise ex

		self._path =                   path
		self._vhdlVersion =            vhdlVersion
		self._library =                library
		self._designUnits =            []
		self._contexts =               {}
		self._configurations =         {}
		self._entities =               {}
		self._architectures =          {}
		self._packages =               {}
		self._packageBodies =          {}
		self._verificationUnits =      {}
		self._verificationProperties = {}
		self._verificationModes =      {}

		self._dependencyVertex =   None
		self._compileOrderVertex = None

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this document and its design units with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitDocument(self)
		for designUnit in self._designUnits:
			designUnit.Visit(visitor)

		visitor.DepartDocument(self)

	def _AddEntity(self, item: Entity) -> None:
		"""
		Add an entity to the document's lists of design units.

		:param item:                Entity object to be added to the document.
		:raises TypeError:          If parameter 'item' is not of type :class:`~pyVHDLModel.DesignUnit.Entity`.
		:raises VHDLModelException: If entity name already exists in document.
		"""
		if not isinstance(item, Entity):
			ex = TypeError("Parameter 'item' is not of type 'Entity'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(item)}'.")
			raise ex

		identifier = item._normalizedIdentifier
		if identifier in self._entities:
			# TODO: use a more specific exception
			raise VHDLModelException(f"An entity '{item._identifier}' already exists in this document.")

		self._entities[identifier] = item
		self._designUnits.append(item)
		item._document = self

		# TODO: add entity to _library and vice versa

	def _AddArchitecture(self, item: Architecture) -> None:
		"""
		Add an architecture to the document's lists of design units.

		:param item:                Architecture object to be added to the document.
		:raises TypeError:          If parameter 'item' is not of type :class:`~pyVHDLModel.DesignUnit.Architecture`.
		:raises VHDLModelException: If architecture name already exists for the referenced entity name in document.
		"""
		if not isinstance(item, Architecture):
			ex = TypeError("Parameter 'item' is not of type 'Architecture'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(item)}'.")
			raise ex

		entity =           item._entity.Name
		entityIdentifier = entity._normalizedIdentifier
		identifier =       item._normalizedIdentifier
		try:
			architectures = self._architectures[entityIdentifier]
			if identifier in architectures:
				# TODO: use a more specific exception
				# FIXME: this is allowed and should be a warning or a strict mode.
				raise VHDLModelException(f"An architecture '{item._identifier}' for entity '{entity._identifier}' already exists in this document.")

			architectures[identifier] = item
		except KeyError:
			self._architectures[entityIdentifier] = {identifier: item}

		self._designUnits.append(item)
		item._document = self

		# TODO: add architecture to _library and vice versa

	def _AddPackage(self, item: Package) -> None:
		"""
		Add a package to the document's lists of design units.

		:param item:                Package object to be added to the document.
		:raises TypeError:          If parameter 'item' is not of type :class:`~pyVHDLModel.DesignUnit.Package`.
		:raises VHDLModelException: If package name already exists in document.
		"""
		if not isinstance(item, (Package, PackageInstantiation)):
			ex = TypeError("Parameter 'item' is not of type 'Package' or 'PackageInstantiation'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(item)}'.")
			raise ex

		identifier = item._normalizedIdentifier
		if identifier in self._packages:
			# TODO: use a more specific exception
			raise VHDLModelException(f"A package '{item._identifier}' already exists in this document.")

		self._packages[identifier] = item
		self._designUnits.append(item)
		item._document = self

		# TODO: add package to _library and vice versa

	def _AddPackageBody(self, item: PackageBody) -> None:
		"""
		Add a package body to the document's lists of design units.

		:param item:                Package body object to be added to the document.
		:raises TypeError:          If parameter 'item' is not of type :class:`~pyVHDLModel.DesignUnit.PackageBody`.
		:raises VHDLModelException: If package body name already exists in document.
		"""
		if not isinstance(item, PackageBody):
			ex = TypeError("Parameter 'item' is not of type 'PackageBody'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(item)}'.")
			raise ex

		identifier = item._normalizedIdentifier
		if identifier in self._packageBodies:
			# TODO: use a more specific exception
			raise VHDLModelException(f"A package body '{item._identifier}' already exists in this document.")

		self._packageBodies[identifier] = item
		self._designUnits.append(item)
		item._document = self

		# TODO: add packagebody to _library and vice versa

	def _AddContext(self, item: Context) -> None:
		"""
		Add a context to the document's lists of design units.

		:param item:                Context object to be added to the document.
		:raises TypeError:          If parameter 'item' is not of type :class:`~pyVHDLModel.DesignUnit.Context`.
		:raises VHDLModelException: If context name already exists in document.
		"""
		if not isinstance(item, Context):
			ex = TypeError("Parameter 'item' is not of type 'Context'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(item)}'.")
			raise ex

		identifier = item._normalizedIdentifier
		if identifier in self._contexts:
			# TODO: use a more specific exception
			raise VHDLModelException(f"A context '{item._identifier}' already exists in this document.")

		self._contexts[identifier] = item
		self._designUnits.append(item)
		item._document = self

		# TODO: add context to _library and vice versa

	def _AddConfiguration(self, item: Configuration) -> None:
		"""
		Add a configuration to the document's lists of design units.

		:param item:                Configuration object to be added to the document.
		:raises TypeError:          If parameter 'item' is not of type :class:`~pyVHDLModel.DesignUnit.Configuration`.
		:raises VHDLModelException: If configuration name already exists in document.
		"""
		if not isinstance(item, Configuration):
			ex = TypeError("Parameter 'item' is not of type 'Configuration'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(item)}'.")
			raise ex

		identifier = item._normalizedIdentifier
		if identifier in self._configurations:
			# TODO: use a more specific exception
			raise VHDLModelException(f"A configuration '{item._identifier}' already exists in this document.")

		self._configurations[identifier] = item
		self._designUnits.append(item)
		item._document = self

		# TODO: add configuration to _library and vice versa

	def _AddVerificationUnit(self, item: VerificationUnit) -> None:
		if not isinstance(item, VerificationUnit):
			ex = TypeError("Parameter 'item' is not of type 'VerificationUnit'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(item)}'.")
			raise ex

		identifier = item._normalizedIdentifier
		if identifier in self._verificationUnits:
			raise ValueError(f"A verification unit '{item._identifier}' already exists in this document.")

		self._verificationUnits[identifier] = item
		self._designUnits.append(item)
		item._document = self

		# TODO: add vunit to _library and vice versa

	def _AddVerificationProperty(self, item: VerificationProperty) -> None:
		if not isinstance(item, VerificationProperty):
			ex = TypeError("Parameter 'item' is not of type 'VerificationProperty'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(item)}'.")
			raise ex

		identifier = item.NormalizedIdentifier
		if identifier in self._verificationProperties:
			raise ValueError(f"A verification property '{item.Identifier}' already exists in this document.")

		self._verificationProperties[identifier] = item
		self._designUnits.append(item)
		item._document = self

		# TODO: add vprop to _library and vice versa

	def _AddVerificationMode(self, item: VerificationMode) -> None:
		if not isinstance(item, VerificationMode):
			ex = TypeError("Parameter 'item' is not of type 'VerificationMode'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(item)}'.")
			raise ex

		identifier = item.NormalizedIdentifier
		if identifier in self._verificationModes:
			raise ValueError(f"A verification mode '{item.Identifier}' already exists in this document.")

		self._verificationModes[identifier] = item
		self._designUnits.append(item)
		item._document = self

		# TODO: add vmode to _library and vice versa

	def _AddDesignUnit(self, item: DesignUnit) -> None:
		"""
		Add a design unit to the document's lists of design units.

		:param item:                Configuration object to be added to the document.
		:raises TypeError:          If parameter 'item' is not of type :class:`~pyVHDLModel.DesignUnit.DesignUnit`.
		:raises ValueError:         If parameter 'item' is an unknown :class:`~pyVHDLModel.DesignUnit.DesignUnit`.
		:raises VHDLModelException: If configuration name already exists in document.
		"""
		if not isinstance(item, DesignUnit):
			ex = TypeError("Parameter 'item' is not of type 'DesignUnit'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(item)}'.")
			raise ex

		if isinstance(item, Entity):
			self._AddEntity(item)
		elif isinstance(item, Architecture):
			self._AddArchitecture(item)
		elif isinstance(item, Package):
			self._AddPackage(item)
		elif isinstance(item, PackageBody):
			self._AddPackageBody(item)
		elif isinstance(item, Context):
			self._AddContext(item)
		elif isinstance(item, Configuration):
			self._AddConfiguration(item)
		elif isinstance(item, VerificationUnit):
			self._AddVerificationUnit(item)
		elif isinstance(item, VerificationProperty):
			self._AddVerificationProperty(item)
		elif isinstance(item, VerificationMode):
			self._AddVerificationMode(item)
		else:
			ex = ValueError("Parameter 'item' is an unknown 'DesignUnit'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(item)}'.")
			raise ex

	def AddDesignUnit(self, designUnit: DesignUnit) -> None:
		"""
		Add a design unit at the end of the document.

		The design unit's document is set to this document. If the document is registered in a design
		(:meth:`Design.AddDocument`), the design unit enters the document's library too.

		:param designUnit:                         The design unit to add.
		:raises ValueError:                        If parameter 'designUnit' is ``None``.
		:raises TypeError:                         If parameter 'designUnit' is not of type
		                                           :class:`~pyVHDLModel.DesignUnit.DesignUnit`.
		:raises AlreadyInDesignError:              If parameter 'designUnit' is already a design unit of a document.
		:raises DuplicateDesignUnitError:          If the document contains a design unit of the same kind and identifier.
		:raises EntityExistsInLibraryError:        If the library already contains an entity of the same identifier.
		:raises ArchitectureExistsInLibraryError:  If the library already contains an architecture of the same identifier
		                                           for the same entity.
		:raises PackageExistsInLibraryError:       If the library already contains a package of the same identifier.
		:raises PackageBodyExistsError:            If the library already contains a package body of the same identifier.
		:raises ConfigurationExistsInLibraryError: If the library already contains a configuration of the same identifier.
		:raises ContextExistsInLibraryError:       If the library already contains a context of the same identifier.

		.. seealso::

		   :meth:`InsertDesignUnit`
		      |rarr| Insert a design unit at a position of the document.
		   :meth:`RemoveDesignUnit`
		      |rarr| Remove a design unit from the document.
		"""
		self.InsertDesignUnit(len(self._designUnits), designUnit)

	def InsertDesignUnit(self, index: int, designUnit: DesignUnit) -> None:
		"""
		Insert a design unit at a position of the document.

		The design units of a document are in source order. The design unit's document is set to this document. If the
		document is registered in a design (:meth:`Design.AddDocument`), the design unit enters the document's library too:
		the library becomes its parent. PSL verification units, properties and modes enter no library.

		:param index:                              Position, from ``0`` (first) to the number of design units (append).
		                                           A negative index counts from the end, as for :meth:`list.insert`.
		:param designUnit:                         The design unit to insert.
		:raises ValueError:                        If parameter 'index' is ``None``.
		:raises TypeError:                         If parameter 'index' is not of type :class:`int`.
		:raises ValueError:                        If parameter 'index' is out of range.
		:raises ValueError:                        If parameter 'designUnit' is ``None``.
		:raises TypeError:                         If parameter 'designUnit' is not of type
		                                           :class:`~pyVHDLModel.DesignUnit.DesignUnit`.
		:raises AlreadyInDesignError:              If parameter 'designUnit' is already a design unit of a document.
		:raises DuplicateDesignUnitError:          If the document contains a design unit of the same kind and identifier.
		:raises EntityExistsInLibraryError:        If the library already contains an entity of the same identifier.
		:raises ArchitectureExistsInLibraryError:  If the library already contains an architecture of the same identifier
		                                           for the same entity.
		:raises PackageExistsInLibraryError:       If the library already contains a package of the same identifier.
		:raises PackageBodyExistsError:            If the library already contains a package body of the same identifier.
		:raises ConfigurationExistsInLibraryError: If the library already contains a configuration of the same identifier.
		:raises ContextExistsInLibraryError:       If the library already contains a context of the same identifier.

		.. seealso::

		   :meth:`AddDesignUnit`
		      |rarr| Add a design unit at the end of the document.
		   :meth:`RemoveDesignUnit`
		      |rarr| Remove a design unit from the document.
		"""
		if index is None:
			raise ValueError("Parameter 'index' is None.")
		elif not isinstance(index, int):
			ex = TypeError("Parameter 'index' is not of type 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(index)}'.")
			raise ex
		elif not (-len(self._designUnits) <= index <= len(self._designUnits)):
			ex = ValueError(f"Parameter 'index' is out of range {-len(self._designUnits)}..{len(self._designUnits)}.")
			ex.add_note(f"Got value '{index}'.")
			raise ex

		if designUnit is None:
			raise ValueError("Parameter 'designUnit' is None.")
		elif not isinstance(designUnit, DesignUnit):
			ex = TypeError("Parameter 'designUnit' is not of type 'DesignUnit'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(designUnit)}'.")
			raise ex
		elif designUnit._document is not None:
			ex = AlreadyInDesignError(
				f"{getTypeName(designUnit)} '{designUnit._identifier}' is already a design unit of a document.",
				element=designUnit,
				parent=designUnit._document
			)
			ex.add_note(f"Remove it from document '{designUnit._document._path}' first.")
			raise ex

		inDesign =   isinstance(self._parent, Design) and self._parent._documentsByPath.get(self._path) is self
		library =    self._library if inDesign else None
		identifier = designUnit._normalizedIdentifier
		libraryUnits: Nullable[dict[str, DesignUnit]] = None
		if isinstance(designUnit, Entity):
			documentUnits = self._entities
			if library is not None:
				libraryUnits = library._entities
		elif isinstance(designUnit, Architecture):
			entityIdentifier = designUnit._entity.Name._normalizedIdentifier
			documentUnits = self._architectures.get(entityIdentifier, {})
			if library is not None:
				libraryUnits = library._architectures.get(entityIdentifier, {})
		elif isinstance(designUnit, Package):
			documentUnits = self._packages
			if library is not None:
				libraryUnits = library._packages
		elif isinstance(designUnit, PackageBody):
			documentUnits = self._packageBodies
			if library is not None:
				libraryUnits = library._packageBodies
		elif isinstance(designUnit, Context):
			documentUnits = self._contexts
			if library is not None:
				libraryUnits = library._contexts
		elif isinstance(designUnit, Configuration):
			documentUnits = self._configurations
			if library is not None:
				libraryUnits = library._configurations
		elif isinstance(designUnit, VerificationUnit):
			documentUnits = self._verificationUnits
		elif isinstance(designUnit, VerificationProperty):
			documentUnits = self._verificationProperties
		elif isinstance(designUnit, VerificationMode):
			documentUnits = self._verificationModes
		else:
			ex = TypeError("Parameter 'designUnit' is not of a known type of design unit.")
			ex.add_note(f"Got type '{getFullyQualifiedName(designUnit)}'.")
			raise ex

		if (existing := documentUnits.get(identifier)) is not None:
			ex = DuplicateDesignUnitError(
				f"Document '{self._path}' already contains {getTypeName(existing)} '{existing._identifier}'.",
				identifier=designUnit._identifier,
				parent=self,
				element=designUnit,
				existing=existing
			)
			ex.add_note(f"Existing design unit is of type '{getFullyQualifiedName(existing)}'.")
			raise ex

		if libraryUnits is not None and identifier in libraryUnits:
			if isinstance(designUnit, Entity):
				raise EntityExistsInLibraryError(designUnit, library)
			elif isinstance(designUnit, Architecture):
				raise ArchitectureExistsInLibraryError(designUnit, library._entities[entityIdentifier], library)
			elif isinstance(designUnit, Package):
				raise PackageExistsInLibraryError(designUnit, library)
			elif isinstance(designUnit, PackageBody):
				raise PackageBodyExistsError(designUnit, library)
			elif isinstance(designUnit, Context):
				raise ContextExistsInLibraryError(designUnit, library)
			else:
				raise ConfigurationExistsInLibraryError(designUnit, library)

		self._designUnits.insert(index, designUnit)
		designUnit._document = self
		if isinstance(designUnit, Architecture):
			self._architectures.setdefault(entityIdentifier, {})[identifier] = designUnit
			if library is not None:
				library._architectures.setdefault(entityIdentifier, {})[identifier] = designUnit
		else:
			documentUnits[identifier] = designUnit
			if libraryUnits is not None:
				libraryUnits[identifier] = designUnit

		if libraryUnits is not None:
			designUnit._parent = library

	def RemoveDesignUnit(self, designUnit: DesignUnit) -> None:
		"""
		Remove a design unit from the document.

		The design unit is detached: its document is cleared. If the document is registered in a design
		(:meth:`Design.AddDocument`), the design unit leaves the document's library too, and its parent is cleared. The
		design unit itself is unchanged and can be added to another document, or inserted at another position.

		:param designUnit:      The design unit to remove.
		:raises ValueError:     If parameter 'designUnit' is ``None``.
		:raises TypeError:      If parameter 'designUnit' is not of type :class:`~pyVHDLModel.DesignUnit.DesignUnit`.
		:raises NotAChildError: If parameter 'designUnit' is not a design unit of this document.

		.. seealso::

		   :meth:`AddDesignUnit`
		      |rarr| Add a design unit at the end of the document.
		   :meth:`InsertDesignUnit`
		      |rarr| Insert a design unit at a position of the document.
		"""
		if designUnit is None:
			raise ValueError("Parameter 'designUnit' is None.")
		elif not isinstance(designUnit, DesignUnit):
			ex = TypeError("Parameter 'designUnit' is not of type 'DesignUnit'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(designUnit)}'.")
			raise ex

		for index, item in enumerate(self._designUnits):
			if item is designUnit:
				break
		else:
			raise NotAChildError(
				f"{getTypeName(designUnit)} '{designUnit._identifier}' is not a design unit of document '{self._path}'.",
				element=designUnit,
				parent=self
			)

		inDesign =   isinstance(self._parent, Design) and self._parent._documentsByPath.get(self._path) is self
		library =    self._library if inDesign else None
		identifier = designUnit._normalizedIdentifier
		libraryUnits: Nullable[dict[str, DesignUnit]] = None
		if isinstance(designUnit, Entity):
			documentUnits = self._entities
			if library is not None:
				libraryUnits = library._entities
		elif isinstance(designUnit, Architecture):
			entityIdentifier = designUnit._entity.Name._normalizedIdentifier
			documentUnits = self._architectures[entityIdentifier]
			if library is not None:
				libraryUnits = library._architectures[entityIdentifier]
		elif isinstance(designUnit, Package):
			documentUnits = self._packages
			if library is not None:
				libraryUnits = library._packages
		elif isinstance(designUnit, PackageBody):
			documentUnits = self._packageBodies
			if library is not None:
				libraryUnits = library._packageBodies
		elif isinstance(designUnit, Context):
			documentUnits = self._contexts
			if library is not None:
				libraryUnits = library._contexts
		elif isinstance(designUnit, Configuration):
			documentUnits = self._configurations
			if library is not None:
				libraryUnits = library._configurations
		elif isinstance(designUnit, VerificationUnit):
			documentUnits = self._verificationUnits
		elif isinstance(designUnit, VerificationProperty):
			documentUnits = self._verificationProperties
		else:
			documentUnits = self._verificationModes

		del self._designUnits[index]
		del documentUnits[identifier]
		designUnit._document = None
		if libraryUnits is not None:
			del libraryUnits[identifier]
			designUnit._parent = None

		if isinstance(designUnit, Architecture):
			if len(documentUnits) == 0:
				del self._architectures[entityIdentifier]

			if libraryUnits is not None and len(libraryUnits) == 0:
				del library._architectures[entityIdentifier]

	@readonly
	def Path(self) -> Path:
		"""
		Read-only property to access the document's path (:attr:`_path`).

		:returns: The path of this document.
		"""
		return self._path

	@readonly
	def VHDLVersion(self) -> VHDLVersion:
		"""
		Read-only property to access the document's VHDL version (:attr:`_vhdlVersion`).

		:returns: VHDL version used to analyze this VHDL file.
		"""
		return self._vhdlVersion

	# @property
	@readonly
	def Library(self) -> Library:
		"""
		Read-only property to access the document's VHDL library (:attr:`_library`).

		:returns: VHDL library used to analyze the VHDL file's design units into.
		"""
		return self._library

	# @Library.setter
	# def Library(self, library: Library) -> None:
	# 	self._library = library
	#
	# 	# TODO: check and set library to design unit?

	@readonly
	def DesignUnits(self) -> list[DesignUnit]:
		"""
		Read-only property to access a list of all design units declarations found in this document (:attr:`_designUnits`).

		:returns: List of all design units.
		"""
		return self._designUnits

	@readonly
	def Contexts(self) -> dict[str, Context]:
		"""
		Read-only property to access the dictionary of all context declarations in this document (:attr:`_contexts`).

		:returns: Dictionary of all contexts, indexed by normalized identifier.
		"""
		return self._contexts

	@readonly
	def Configurations(self) -> dict[str, Configuration]:
		"""
		Read-only property to access the dictionary of all configuration declarations in this document (:attr:`_configurations`).

		:returns: Dictionary of all configurations, indexed by normalized identifier.
		"""
		return self._configurations

	@readonly
	def Entities(self) -> dict[str, Entity]:
		"""
		Read-only property to access the dictionary of all entity declarations in this document (:attr:`_entities`).

		:returns: Dictionary of all entities, indexed by normalized identifier.
		"""
		return self._entities

	@readonly
	def Architectures(self) -> dict[str, dict[str, Architecture]]:
		"""
		Read-only property to access the dictionary of all architecture declarations in this document (:attr:`_architectures`).

		:returns: Dictionary of all architectures, indexed by normalized entity identifier, then by normalized
		          architecture identifier.
		"""
		return self._architectures

	@readonly
	def Packages(self) -> dict[str, Package]:
		"""
		Read-only property to access the dictionary of all package declarations in this document (:attr:`_packages`).

		:returns: Dictionary of all packages, indexed by normalized identifier.
		"""
		return self._packages

	@readonly
	def PackageBodies(self) -> dict[str, PackageBody]:
		"""
		Read-only property to access the dictionary of all package body declarations in this document (:attr:`_packageBodies`).

		:returns: Dictionary of all package bodies, indexed by normalized identifier.
		"""
		return self._packageBodies

	@readonly
	def VerificationUnits(self) -> dict[str, VerificationUnit]:
		"""
		Read-only property to access the dictionary of all verification unit declarations in this document (:attr:`_verificationUnits`).

		:returns: Dictionary of all verification units, indexed by normalized identifier.
		"""
		return self._verificationUnits

	@readonly
	def VerificationProperties(self) -> dict[str, VerificationProperty]:
		"""
		Read-only property to access the dictionary of all verification property declarations in this document (:attr:`_verificationProperties`).

		:returns: Dictionary of all verification properties, indexed by normalized identifier.
		"""
		return self._verificationProperties

	@readonly
	def VerificationModes(self) -> dict[str, VerificationMode]:
		"""
		Read-only property to access the dictionary of all verification mode declarations in this document (:attr:`_verificationModes`).

		:returns: Dictionary of all verification mode declarations, indexed by normalized identifier.
		"""
		return self._verificationModes

	@readonly
	def CompileOrderVertex(self) -> Vertex:
		"""
		Read-only property to access the corresponding compile-order vertex (:attr:`_compileOrderVertex`).

		The compile-order vertex references this document by its value field.

		:returns: The corresponding compile-order vertex.
		"""
		return self._compileOrderVertex

	def IterateDesignUnits(self, filter: DesignUnitKind = DesignUnitKind.All) -> Generator[DesignUnit, None, None]:
		"""
		Iterate all design units in the document.

		A union of :class:`DesignUnitKind` values can be given to filter the returned result for suitable design units.

		.. rubric:: Algorithm

		* If contexts are selected in the filter:

		  1. Iterate all contexts in that library.

		* If packages are selected in the filter:

		  1. Iterate all packages in that library.

		* If package bodies are selected in the filter:

		  1. Iterate all package bodies in that library.

		* If entites are selected in the filter:

		  1. Iterate all entites in that library.

		* If architectures are selected in the filter:

		  1. Iterate all architectures in that library.

		* If configurations are selected in the filter:

		  1. Iterate all configurations in that library.

		:param filter: An enumeration with possibly multiple flags to filter the returned design units.
		:returns:      A generator to iterate all matched design units in the document.

		.. seealso::

		   :meth:`pyVHDLModel.Design.IterateDesignUnits`
		     Iterate all design units in the design.
		   :meth:`pyVHDLModel.Library.IterateDesignUnits`
		     Iterate all design units in the library.
		"""
		if DesignUnitKind.Context in filter:
			for context in self._contexts.values():
				yield context

		if DesignUnitKind.Package in filter:
			for package in self._packages.values():
				yield package

		if DesignUnitKind.PackageBody in filter:
			for packageBody in self._packageBodies.values():
				yield packageBody

		if DesignUnitKind.Entity in filter:
			for entity in self._entities.values():
				yield entity

		if DesignUnitKind.Architecture in filter:
			for architectures in self._architectures.values():
				for architecture in architectures.values():
					yield architecture

		if DesignUnitKind.Configuration in filter:
			for configuration in self._configurations.values():
				yield configuration

		# for verificationProperty in self._verificationUnits.values():
		# 	yield verificationProperty
		# for verificationUnit in self._verificationProperties.values():
		# 	yield entity
		# for verificationMode in self._verificationModes.values():
		# 	yield verificationMode

	def __repr__(self) -> str:
		"""
		Formats a representation of the document.

		**Format:** ``Document: 'path/to/file.vhdl'``

		:returns: String representation of the document.
		"""
		return f"Document: '{self._path}'"

	__str__ = __repr__
