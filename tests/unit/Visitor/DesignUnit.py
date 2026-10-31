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
"""Tests for the walk of context items, design units, configurations and documents (:mod:`pyVHDLModel.Visitor`)."""
from pathlib                   import Path

from pyTooling.Testing         import Testcase

from pyVHDLModel               import Document
from pyVHDLModel.Association   import PortAssociationItem
from pyVHDLModel.Configuration import EntityAspectEntity, BindingIndication, AllInstantiationList, \
                                      ComponentConfiguration, BlockConfiguration
from pyVHDLModel.DesignUnit    import LibraryClause, Entity, Architecture, Configuration, Context
from pyVHDLModel.Name          import SimpleName
from pyVHDLModel.Symbol        import LibraryReferenceSymbol, EntitySymbol, ArchitectureSymbol, \
                                      ComponentInstantiationSymbol

from tests.unit.Visitor        import FullRecorder


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class DesignUnits(Testcase):
	def test_Entity(self) -> None:
		"""The context clause precedes the design unit; the walk passes ``begin`` before the statements."""
		ieee =     LibraryReferenceSymbol(SimpleName("ieee"))
		std =      LibraryReferenceSymbol(SimpleName("std"))
		clause =   LibraryClause([ieee, std])
		entity =   Entity("e", [clause])
		recorder = FullRecorder()

		entity.Visit(recorder)

		self.assertEqual([
			("VisitContextClause",     entity),
			("VisitLibraryClause",     clause),
			("VisitSymbol",            ieee),
			("VisitSimpleName",        ieee.Name),
			("DepartSimpleName",       ieee.Name),
			("DepartSymbol",           ieee),
			("VisitNameListSeparator", clause),
			("VisitSymbol",            std),
			("VisitSimpleName",        std.Name),
			("DepartSimpleName",       std.Name),
			("DepartSymbol",           std),
			("VisitTerminator",        clause),
			("DepartLibraryClause",    clause),
			("DepartContextClause",    entity),
			("VisitEntity",            entity),
			("VisitBegin",             entity),
			("VisitEnd",               entity),
			("VisitTerminator",        entity),
			("DepartEntity",           entity),
		], recorder.Events)

	def test_Architecture(self) -> None:
		entity =       EntitySymbol(SimpleName("e"))
		architecture = Architecture("rtl", entity)
		recorder =     FullRecorder()

		architecture.Visit(recorder)

		self.assertEqual([
			("VisitContextClause",  architecture),
			("DepartContextClause", architecture),
			("VisitArchitecture",   architecture),
			("VisitSymbol",         entity),
			("VisitSimpleName",     entity.Name),
			("DepartSimpleName",    entity.Name),
			("DepartSymbol",        entity),
			("VisitIs",             architecture),
			("VisitBegin",          architecture),
			("VisitEnd",            architecture),
			("VisitTerminator",     architecture),
			("DepartArchitecture",  architecture),
		], recorder.Events)

	def test_Context(self) -> None:
		"""A context declaration has no context clause: its context items are walked inside the declaration."""
		ieee =     LibraryReferenceSymbol(SimpleName("ieee"))
		clause =   LibraryClause([ieee])
		context =  Context("project", [clause])
		recorder = FullRecorder()

		context.Visit(recorder)

		self.assertEqual([
			("VisitContext",        context),
			("VisitLibraryClause",  clause),
			("VisitSymbol",         ieee),
			("VisitSimpleName",     ieee.Name),
			("DepartSimpleName",    ieee.Name),
			("DepartSymbol",        ieee),
			("VisitTerminator",     clause),
			("DepartLibraryClause", clause),
			("VisitEnd",            context),
			("VisitTerminator",     context),
			("DepartContext",       context),
		], recorder.Events)

	def test_Document(self) -> None:
		entity =       Entity("e")
		architecture = Architecture("rtl", EntitySymbol(SimpleName("e")))
		document =     Document(Path("e.vhdl"))
		document._AddDesignUnit(entity)
		document._AddDesignUnit(architecture)
		recorder = FullRecorder()

		document.Visit(recorder)

		events = recorder.Events
		self.assertEqual(("VisitDocument", document), events[0])
		self.assertEqual(("DepartDocument", document), events[-1])
		self.assertEqual(
			[("VisitEntity", entity), ("VisitArchitecture", architecture)],
			[event for event in events if event[0] in ("VisitEntity", "VisitArchitecture")]
		)


class Configurations(Testcase):
	def test_Configuration(self) -> None:
		entity =                 EntitySymbol(SimpleName("top"))
		block =                  ArchitectureSymbol(SimpleName("rtl"))
		instances =              AllInstantiationList()
		component =              ComponentInstantiationSymbol(SimpleName("sub"))
		aspectEntity =           EntitySymbol(SimpleName("sub"))
		architecture =           ArchitectureSymbol(SimpleName("rtl"))
		aspect =                 EntityAspectEntity(aspectEntity, architecture)
		formal =                 SimpleName("a")
		actual =                 SimpleName("b")
		association =            PortAssociationItem(formal, actual)
		indication =             BindingIndication(aspect, portAssociationItems=[association])
		componentConfiguration = ComponentConfiguration(instances, component, indication)
		blockConfiguration =     BlockConfiguration(block, [componentConfiguration])
		configuration =          Configuration("cfg", entity, blockConfiguration)
		recorder =               FullRecorder()

		configuration.Visit(recorder)

		self.assertEqual([
			("VisitContextClause",           configuration),
			("DepartContextClause",          configuration),
			("VisitConfiguration",           configuration),
			("VisitSymbol",                  entity),
			("VisitSimpleName",              entity.Name),
			("DepartSimpleName",             entity.Name),
			("DepartSymbol",                 entity),
			("VisitIs",                      configuration),
			("VisitBlockConfiguration",      blockConfiguration),
			("VisitBlockSpecification",      blockConfiguration),
			("VisitSymbol",                  block),
			("VisitSimpleName",              block.Name),
			("DepartSimpleName",             block.Name),
			("DepartSymbol",                 block),
			("DepartBlockSpecification",     blockConfiguration),
			("VisitComponentConfiguration",  componentConfiguration),
			("VisitInstantiationList",       componentConfiguration),
			("VisitAllInstantiationList",    instances),
			("DepartAllInstantiationList",   instances),
			("DepartInstantiationList",      componentConfiguration),
			("VisitSymbol",                  component),
			("VisitSimpleName",              component.Name),
			("DepartSimpleName",             component.Name),
			("DepartSymbol",                 component),
			("VisitBindingIndication",       indication),
			("VisitEntityAspectEntity",      aspect),
			("VisitSymbol",                  aspectEntity),
			("VisitSimpleName",              aspectEntity.Name),
			("DepartSimpleName",             aspectEntity.Name),
			("DepartSymbol",                 aspectEntity),
			("VisitLeftParenthesis",         aspect),
			("VisitSymbol",                  architecture),
			("VisitSimpleName",              architecture.Name),
			("DepartSimpleName",             architecture.Name),
			("DepartSymbol",                 architecture),
			("VisitRightParenthesis",        aspect),
			("DepartEntityAspectEntity",     aspect),
			("VisitPortMapAspect",           indication),
			("VisitAssociationItem",         association),
			("VisitSimpleName",              formal),
			("DepartSimpleName",             formal),
			("VisitArrow",                   association),
			("VisitSimpleName",              actual),
			("DepartSimpleName",             actual),
			("DepartAssociationItem",        association),
			("DepartPortMapAspect",          indication),
			("DepartBindingIndication",      indication),
			("VisitEnd",                     componentConfiguration),
			("VisitTerminator",              componentConfiguration),
			("DepartComponentConfiguration", componentConfiguration),
			("VisitEnd",                     blockConfiguration),
			("VisitTerminator",              blockConfiguration),
			("DepartBlockConfiguration",     blockConfiguration),
			("VisitEnd",                     configuration),
			("VisitTerminator",              configuration),
			("DepartConfiguration",          configuration),
		], recorder.Events)

	def test_InstantiationList(self) -> None:
		"""The labels of an instantiation list are separated by commas."""
		first =         SimpleName("u1")
		second =        SimpleName("u2")
		configuration = ComponentConfiguration([first, second], ComponentInstantiationSymbol(SimpleName("sub")))
		recorder =      FullRecorder()

		configuration.Visit(recorder)

		self.assertEqual([
			("VisitComponentConfiguration", configuration),
			("VisitInstantiationList",      configuration),
			("VisitSimpleName",             first),
			("DepartSimpleName",            first),
			("VisitNameListSeparator",      configuration),
			("VisitSimpleName",             second),
			("DepartSimpleName",            second),
			("DepartInstantiationList",     configuration),
		], recorder.Events[:8])
