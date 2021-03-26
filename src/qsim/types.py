from typing import (NewType, List, Union, Dict, Tuple, Iterable, Any, Callable,
                    Optional, Set)
from dataclasses import dataclass
from numpy import array, complex as np_complex


# README:S1BEGIN
@dataclass(frozen=True, eq=True)
class QVec:
  mat:array

QVecOp=Union['QBitOp','QTProd']

@dataclass(frozen=True, eq=True)
class QBitOp:
  mat:array

@dataclass(frozen=True, eq=True)
class QTProd:
  a:QVecOp
  b:QVecOp
# README:S1END

# README:S2BEGIN
QId=NewType('QId',int)

@dataclass(frozen=True, eq=True)
class QInput:
  nqbits:int

@dataclass(frozen=True, eq=True)
class QGraph:
  graph:Dict[QId, Tuple[Union[QVecOp,QInput], List[QId]]]
# README:S2END

