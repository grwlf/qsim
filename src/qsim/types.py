from typing import (NewType, List, Union, Dict, Tuple, Iterable, Any, Callable,
                    Optional, Set)
from dataclasses import dataclass
from numpy import array, complex as np_complex


@dataclass(frozen=True, eq=True)
class QVec:
  basis:List[np_complex]

@dataclass(frozen=True, eq=True)
class QVecM:
  mat:array

QVecOp=Union['QBitOp','QTProd']

@dataclass(frozen=True, eq=True)
class QBitOp:
  mat:array

@dataclass(frozen=True, eq=True)
class QTProd:
  a:QVecOp
  b:QVecOp

QId=NewType('QId',int)

@dataclass(frozen=True, eq=True)
class QInput:
  nqbits:int

@dataclass(frozen=True, eq=True)
class QGraph:
  graph:Dict[QId, Tuple[Union[QVecOp,QInput], List[QId]]]

@dataclass(frozen=True, eq=True)
class SimState:
  vecop_cache:Dict[str,array]

