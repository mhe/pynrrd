from typing import Any, Dict, Literal

NRRDFieldType = Literal['int', 'double', 'string', 'int list', 'double list', 'string list', 'quoted string list',
                        'int vector', 'double vector', 'int matrix', 'double matrix']

IndexOrder = Literal['F', 'C']

NRRDFieldMap = Dict[str, NRRDFieldType]
NRRDHeader = Dict[str, Any]
