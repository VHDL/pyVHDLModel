from pyTooling.Decorators import export

from pyVHDLModel import ModelEntity, Name, ExpressionUnion


@export
class AssociationItem(ModelEntity):
	_formal: Name
	_actual: ExpressionUnion

	def __init__(self, actual: ExpressionUnion, formal: Name = None):
		super().__init__()

		self._formal = formal
		if formal is not None:
			formal._parent = self

		self._actual = actual
		# actual._parent = self  # FIXME: actual is provided as None

	@property
	def Formal(self) -> Name:  # TODO: can also be a conversion function !!
		return self._formal

	@property
	def Actual(self) -> ExpressionUnion:
		return self._actual

	def __str__(self):
		if self._formal is None:
			return str(self._actual)
		else:
			return "{formal!s} => {actual!s}".format(formal=self._formal, actual=self._actual)


@export
class GenericAssociationItem(AssociationItem):
	pass


@export
class PortAssociationItem(AssociationItem):
	pass


@export
class ParameterAssociationItem(AssociationItem):
	pass