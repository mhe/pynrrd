# TODO Finish this
from typing import Literal, TypedDict

# NRRDField = Literal[]
NRRDFieldType = Literal['int', 'double', 'string', 'int list', 'double list', 'string list', 'quoted string list',
                        'int vector', 'double vector', 'int matrix', 'double matrix']

IndexOrder = Literal['F', 'C']

FieldMap = Dict[str, NRRDFieldType]


# TODO Will this fail pre-3.8?
class NRRDHeader(TypedDict):
    # TODO
    pass
