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
# Copyright 2026-2026 Patrick Lehmann - Bötzingen, Germany                                                             #
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
Tests for analyzing a design again (:meth:`~pyVHDLModel.Design.Analyze`, :meth:`~pyVHDLModel.Design.ResetAnalysis`).

A design analyzed again, e.g. after it was changed, has the state of a fresh design of the same content analyzed once.
The state is compared by names, so designs built from different objects can be compared.
"""
from pathlib                   import Path
from typing                    import Any

from pyTooling.Graph           import Graph
from pyTooling.Testing         import Testcase

from pyVHDLModel               import Design, Document
from pyVHDLModel.Base          import Mode
from pyVHDLModel.Concurrent    import EntityInstantiation, ComponentInstantiation, ProcessStatement
from pyVHDLModel.DesignUnit    import Architecture, Component, Context, Entity, Package, PackageBody
from pyVHDLModel.DesignUnit    import ContextReference, LibraryClause, UseClause
from pyVHDLModel.Instantiation import PackageInstantiation
from pyVHDLModel.Interface     import GenericConstantInterfaceItem
from pyVHDLModel.Name          import AllName, SelectedName, SimpleName
from pyVHDLModel.Symbol        import AllPackageMembersReferenceSymbol, ComponentInstantiationSymbol
from pyVHDLModel.Symbol        import ContextReferenceSymbol, EntityInstantiationSymbol, LibraryReferenceSymbol
from pyVHDLModel.Symbol        import PackageReferenceSymbol, PackageSymbol

from tests.unit                import _entitySymbol, _subtypeSymbol
from tests.unit.Mutation       import _port


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


def _packages() -> Document:
	"""A document with a package and its body, a generic package and its instantiation, and a context."""
	genericPackage = Package(
		"gpkg",
		genericItems=[GenericConstantInterfaceItem(["W"], Mode.Default, _subtypeSymbol("natural"))],
		declaredItems=[Component("leaf")]
	)
	document = Document(Path("a.vhdl"))
	document.AddDesignUnit(Package("pkg", declaredItems=[Component("leaf")]))
	document.AddDesignUnit(PackageBody(PackageSymbol(SimpleName("pkg"))))
	document.AddDesignUnit(genericPackage)
	document.AddDesignUnit(PackageInstantiation("ipkg", PackageReferenceSymbol(SelectedName("gpkg", SimpleName("work")))))
	document.AddDesignUnit(Context("ctx", [LibraryClause([LibraryReferenceSymbol(SimpleName("ieee"))])]))

	return document


def _leaf() -> Document:
	"""A document with an entity and its architecture."""
	document = Document(Path("b.vhdl"))
	document.AddDesignUnit(Entity("leaf", portItems=[_port("clk")]))
	document.AddDesignUnit(Architecture("rtl", _entitySymbol("leaf")))

	return document


def _topArchitecture() -> Architecture:
	"""An architecture instantiating the leaf entity directly and as a component, with an unlabeled process."""
	return Architecture("rtl", _entitySymbol("top"), statements=[
		EntityInstantiation("inst1", EntityInstantiationSymbol(SelectedName("leaf", SimpleName("work")))),
		ComponentInstantiation("inst2", ComponentInstantiationSymbol(SimpleName("leaf"))),
		ProcessStatement()
	])


def _top(withArchitecture: bool = True) -> Document:
	"""A document with an entity using the packages and the context, and optionally its architecture."""
	contextItems = [
		ContextReference([ContextReferenceSymbol(SelectedName("ctx", SimpleName("work")))]),
		UseClause([AllPackageMembersReferenceSymbol(AllName(SelectedName("pkg", SimpleName("work"))))]),
		UseClause([PackageReferenceSymbol(SelectedName("ipkg", SimpleName("work")))])
	]
	document = Document(Path("c.vhdl"))
	document.AddDesignUnit(Entity("top", contextItems))
	if withArchitecture:
		document.AddDesignUnit(_topArchitecture())

	return document


def _design(*documents: Document) -> Design:
	"""A design with the libraries ``std`` and ``ieee``, and library ``lib`` holding the documents."""
	design = Design("design")
	design.LoadStdLibrary()
	design.LoadIEEELibrary()
	library = design.GetLibrary("lib")
	for document in documents:
		design.AddDocument(document, library)

	return design


def _name(element: Any) -> Any:
	"""The name of a model entity referenced by the state."""
	if element is None:
		return None
	elif isinstance(element, Architecture):
		entityName = element._entity._name._normalizedIdentifier
		return f"Architecture {element._parent._normalizedIdentifier}.{entityName}({element._normalizedIdentifier})"
	elif isinstance(element, (Entity, Package, PackageBody, Context)):
		return f"{element.__class__.__name__} {element._parent._normalizedIdentifier}.{element._normalizedIdentifier}"

	return f"{element.__class__.__name__} {element._normalizedIdentifier}"


def _graph(graph: Graph) -> dict[str, Any]:
	"""The vertices, edges and links of a graph."""
	return {
		"vertices": sorted((str(v.ID), str(v.get("kind")), v.get("predefined")) for v in graph.IterateVertices()),
		"edges":    sorted((str(e.Source.ID), str(e.Destination.ID), str(e.get("kind"))) for e in graph.IterateEdges()),
		"links":    sorted((str(link.Source.ID), str(link.Destination.ID)) for link in graph.IterateLinks())
	}


def _vertex(vertex: Any, graph: Graph) -> Any:
	"""The ID of a vertex, and whether the vertex is a vertex of the design's graph."""
	return None if vertex is None else (str(vertex.ID), vertex.Graph is graph)


def _state(design: Design) -> dict[str, Any]:
	"""The state of a design an analysis derives, by names."""
	state: dict[str, Any] = {
		"graphs": {
			"dependency":   _graph(design.DependencyGraph),
			"compileOrder": _graph(design.CompileOrderGraph),
			"hierarchy":    _graph(design.HierarchyGraph),
			"object":       _graph(design.ObjectGraph)
		},
		"toplevel":  _name(design._toplevel),
		"libraries": {
			name: _vertex(library._dependencyVertex, design.DependencyGraph) for name, library in design.Libraries.items()
		},
		"documents": {
			str(document.Path): (
				_vertex(document._dependencyVertex, design.DependencyGraph),
				_vertex(document._compileOrderVertex, design.CompileOrderGraph)
			) for document in design.Documents
		}
	}

	designUnits: dict[str, Any] = {}
	for designUnit in design.IterateDesignUnits():
		references = (*designUnit._libraryReferences, *designUnit._packageReferences, *designUnit._contextReferences)
		designUnitState: dict[str, Any] = {
			"dependencyVertex":    _vertex(designUnit._dependencyVertex, design.DependencyGraph),
			"hierarchyVertex":     _vertex(designUnit._hierarchyVertex, design.HierarchyGraph),
			"referencedLibraries": sorted(designUnit._referencedLibraries),
			"referencedPackages":  {lib: sorted(packages) for lib, packages in designUnit._referencedPackages.items()},
			"referencedContexts":  {lib: sorted(contexts) for lib, contexts in designUnit._referencedContexts.items()},
			"contextSymbols":      [_name(symbol._reference) for reference in references for symbol in reference.Symbols]
		}
		if (namespace := getattr(designUnit, "_namespace", None)) is not None:
			designUnitState["namespace"] = {
				"elements":      sorted(namespace.Elements()),
				"imports":       {key: _name(element) for key, element in namespace.Imports().items()},
				"parent":        None if namespace.ParentNamespace is None else namespace.ParentNamespace.Name,
				"subNamespaces": sorted(str(subNamespace.Name) for subNamespace in namespace.SubNamespaces)
			}

		if isinstance(designUnit, Entity):
			designUnitState["architectures"] = sorted(designUnit.Architectures)
		elif isinstance(designUnit, Architecture):
			designUnitState["entity"] = _name(designUnit._entity._reference)
			instantiations = []
			for instance in designUnit.IterateInstantiations():
				symbol = instance._entity if isinstance(instance, EntityInstantiation) else instance._component
				instantiations.append((instance.Label, _name(symbol._reference)))

			designUnitState["instantiations"] = sorted(instantiations)
		elif isinstance(designUnit, PackageBody):
			designUnitState["package"] = _name(designUnit._package._reference)

		if isinstance(designUnit, Package):
			designUnitState["packageBody"] = _name(designUnit._packageBody)
			designUnitState["components"] = {
				key: (_name(component._entity), component._isBlackbox) for key, component in designUnit._components.items()
			}

		if isinstance(designUnit, PackageInstantiation):
			designUnitState["genericPackage"] = _name(designUnit._packageReference._reference)

		designUnits[_name(designUnit)] = designUnitState

	state["designUnits"] = designUnits
	return state


class Reanalysis(Testcase):
	"""A design analyzed again has the state of a fresh design of the same content analyzed once."""

	def test_Analyze(self) -> None:
		design = _design(_packages(), _leaf(), _top())
		design.Analyze()
		state = _state(design)

		design.Analyze()

		self.assertDictEqual(state, _state(design))

	def test_Analyze_Fresh(self) -> None:
		"""A design analyzed twice has the state of a fresh design analyzed once."""
		design = _design(_packages(), _leaf(), _top())
		design.Analyze()
		design.Analyze()

		expected = _design(_packages(), _leaf(), _top())
		expected.Analyze()

		state = _state(design)
		self.assertDictEqual(_state(expected), state)
		self.assertListEqual(
			[("inst1", "Entity lib.leaf"), ("inst2", "Component leaf")],
			state["designUnits"]["Architecture lib.top(rtl)"]["instantiations"]
		)

	def test_Analyze_AddDocument(self) -> None:
		design = _design(_packages(), _leaf())
		design.Analyze()

		design.AddDocument(_top(), design.GetLibrary("lib"))
		design.Analyze()

		expected = _design(_packages(), _leaf(), _top())
		expected.Analyze()
		self.assertDictEqual(_state(expected), _state(design))

	def test_Analyze_AddDesignUnit(self) -> None:
		top = _top(withArchitecture=False)
		design = _design(_packages(), _leaf(), top)
		design.Analyze()

		top.AddDesignUnit(_topArchitecture())
		design.Analyze()

		expected = _design(_packages(), _leaf(), _top())
		expected.Analyze()
		self.assertDictEqual(_state(expected), _state(design))

	def test_Analyze_RemoveDesignUnit(self) -> None:
		top = _top()
		design = _design(_packages(), _leaf(), top)
		design.Analyze()

		top.RemoveDesignUnit(top.DesignUnits[1])
		design.Analyze()

		expected = _design(_packages(), _leaf(), _top(withArchitecture=False))
		expected.Analyze()
		self.assertDictEqual(_state(expected), _state(design))

	def test_Analyze_RemoveDocument(self) -> None:
		top = _top()
		design = _design(_packages(), _leaf(), top)
		design.Analyze()

		design.RemoveDocument(top)
		design.Analyze()

		expected = _design(_packages(), _leaf())
		expected.Analyze()
		self.assertDictEqual(_state(expected), _state(design))


class ResetAnalysis(Testcase):
	"""Resetting an analysis keeps what the user built."""

	def test_ResetAnalysis(self) -> None:
		design = _design(_packages(), _leaf(), _top())
		dependencyGraph = design.DependencyGraph
		design.Analyze()

		design.ResetAnalysis()

		self.assertIsNot(dependencyGraph, design.DependencyGraph)
		self.assertEqual(0, design.DependencyGraph.VertexCount)
		self.assertEqual(0, design.CompileOrderGraph.VertexCount)
		self.assertEqual(0, design.HierarchyGraph.VertexCount)
		self.assertIsNone(design._toplevel)
		for designUnit in design.IterateDesignUnits():
			self.assertIsNone(designUnit.DependencyVertex)
			self.assertIsNone(designUnit.HierarchyVertex)
			self.assertDictEqual({}, designUnit.ReferencedLibraries)
			self.assertDictEqual({}, designUnit.ReferencedPackages)
			self.assertDictEqual({}, designUnit.ReferencedContexts)

	def test_ResetAnalysis_Links(self) -> None:
		design = _design(_packages(), _leaf(), _top())
		design.Analyze()
		entity = design.GetEntity("lib", "top")
		architecture = entity.Architectures["rtl"]
		package = design.GetPackage("lib", "pkg")
		packageBody = package.PackageBody
		packageInstance = design.GetPackage("lib", "ipkg")

		design.ResetAnalysis()

		self.assertDictEqual({}, entity.Architectures)
		self.assertIsNone(architecture.Entity.Reference)
		self.assertIsNone(architecture._namespace.ParentNamespace)
		self.assertListEqual([], entity._namespace.SubNamespaces)
		self.assertIsNone(package.PackageBody)
		self.assertIsNone(packageBody.Package.Reference)
		self.assertIsNone(packageBody._namespace.ParentNamespace)
		self.assertIsNone(packageInstance.PackageReference.Reference)
		self.assertDictEqual({}, packageInstance.Components)

	def test_ResetAnalysis_Symbols(self) -> None:
		design = _design(_packages(), _leaf(), _top())
		design.Analyze()
		entity = design.GetEntity("lib", "top")
		architecture = entity.Architectures["rtl"]

		design.ResetAnalysis()

		for reference in entity.ContextItems:
			for symbol in reference.Symbols:
				self.assertIsNone(symbol.Reference)

		instantiations = list(architecture.IterateInstantiations())
		self.assertEqual(2, len(instantiations))
		self.assertIsNone(instantiations[0].Entity.Reference)
		self.assertIsNone(instantiations[1].Component.Reference)

	def test_ResetAnalysis_Components(self) -> None:
		design = _design(_packages(), _leaf(), _top())
		design.Analyze()
		component = design.GetPackage("lib", "pkg").Components["leaf"]

		design.ResetAnalysis()

		self.assertIsNone(component.Entity)
		self.assertIsNone(component.IsBlackbox)

	def test_ResetAnalysis_Namespaces(self) -> None:
		"""Imports are removed, declarations are kept."""
		design = _design(_packages(), _leaf(), _top())
		design.Analyze()
		entity = design.GetEntity("lib", "leaf")
		top = design.GetEntity("lib", "top")

		design.ResetAnalysis()

		self.assertDictEqual({"clk": entity.PortItems[0]}, entity._namespace.Elements())
		self.assertDictEqual({}, top._namespace.Imports())

	def test_ResetAnalysis_NotAnalyzed(self) -> None:
		design = _design(_packages(), _leaf(), _top())
		state = _state(design)

		design.ResetAnalysis()

		self.assertDictEqual(state, _state(design))


class EntityNamespace(Testcase):
	def test_Analyze_IndexEntities(self) -> None:
		"""Analyzing a design indexes the entities: an entity's ports are declared in its namespace."""
		design = _design(_leaf())

		design.Analyze()

		entity = design.GetEntity("lib", "leaf")
		self.assertDictEqual({"clk": entity.PortItems[0]}, entity._namespace.Elements())
