from typing import Iterable, Optional as Nullable

from pyTooling.Decorators import export

from pyVHDLModel import ModelEntity, MultipleNamedEntityMixin, DocumentedEntityMixin, SubtypeOrSymbol, ExpressionUnion


@export
class Obj(ModelEntity, MultipleNamedEntityMixin, DocumentedEntityMixin):
	_subtype: SubtypeOrSymbol

	def __init__(self, identifiers: Iterable[str], subtype: SubtypeOrSymbol, documentation: str = None):
		super().__init__()
		MultipleNamedEntityMixin.__init__(self, identifiers)
		DocumentedEntityMixin.__init__(self, documentation)

		self._subtype = subtype
		subtype._parent = self

	@property
	def Subtype(self) -> SubtypeOrSymbol:
		return self._subtype


@export
class BaseConstant(Obj):
	pass


@export
class WithDefaultExpressionMixin:
	"""A ``WithDefaultExpression`` is a mixin class for all objects declarations accepting default expressions."""

	_defaultExpression: Nullable[ExpressionUnion]

	def __init__(self, defaultExpression: ExpressionUnion = None):
		self._defaultExpression = defaultExpression
		if defaultExpression is not None:
			defaultExpression._parent = self

	@property
	def DefaultExpression(self) -> Nullable[ExpressionUnion]:
		return self._defaultExpression


@export
class Constant(BaseConstant, WithDefaultExpressionMixin):
	def __init__(self, identifiers: Iterable[str], subtype: SubtypeOrSymbol, defaultExpression: ExpressionUnion = None, documentation: str = None):
		super().__init__(identifiers, subtype, documentation)
		WithDefaultExpressionMixin.__init__(self, defaultExpression)


@export
class DeferredConstant(BaseConstant):
	_constantReference: Constant

	def __init__(self, identifiers: Iterable[str], subtype: SubtypeOrSymbol, documentation: str = None):
		super().__init__(identifiers, subtype, documentation)

	@property
	def ConstantReference(self) -> Constant:
		return self._constantReference


@export
class Variable(Obj, WithDefaultExpressionMixin):
	def __init__(self, identifiers: Iterable[str], subtype: SubtypeOrSymbol, defaultExpression: ExpressionUnion = None, documentation: str = None):
		super().__init__(identifiers, subtype, documentation)
		WithDefaultExpressionMixin.__init__(self, defaultExpression)


@export
class SharedVariable(Obj):
	pass


@export
class Signal(Obj, WithDefaultExpressionMixin):
	def __init__(self, identifiers: Iterable[str], subtype: SubtypeOrSymbol, defaultExpression: ExpressionUnion = None, documentation: str = None):
		super().__init__(identifiers, subtype, documentation)
		WithDefaultExpressionMixin.__init__(self, defaultExpression)


@export
class File(Obj):
	pass
