from typing import List, Iterable

from pyTooling.Decorators import export

from pyVHDLModel import Name, ExpressionUnion


@export
class SimpleName(Name):
	def __str__(self):
		return self._identifier


@export
class ParenthesisName(Name):
	_associations: List

	def __init__(self, prefix: Name, associations: Iterable):
		super().__init__("", prefix)

		self._associations = []
		for association in associations:
			self._associations.append(association)
			association._parent = self

	@property
	def Associations(self) -> List:
		return self._associations

	def __str__(self):
		return str(self._prefix) + "(" + ", ".join([str(a) for a in self._associations]) + ")"


@export
class IndexedName(Name):
	_indices: List[ExpressionUnion]

	def __init__(self, prefix: Name, indices: Iterable[ExpressionUnion]):
		super().__init__("", prefix)

		self._indices = []
		for index in indices:
			self._indices.append(index)
			index._parent = self

	@property
	def Indices(self) -> List[ExpressionUnion]:
		return self._indices


@export
class SlicedName(Name):
	pass


@export
class SelectedName(Name):
	def __init__(self, identifier: str, prefix: Name):
		super().__init__(identifier, prefix)

	def __str__(self):
		return str(self._prefix) + "." + self._identifier


@export
class AttributeName(Name):
	def __init__(self, identifier: str, prefix: Name):
		super().__init__(identifier, prefix)

	def __str__(self):
		return str(self._prefix) + "'" + self._identifier


@export
class AllName(Name):
	def __init__(self, prefix: Name):
		super().__init__("all", prefix)

	def __str__(self):
		return str(self._prefix) + "." + "all"


@export
class OpenName(Name):
	def __init__(self):
		super().__init__("open")

	def __str__(self):
		return "open"
