from typing import List, Union, Optional, Dict, Any, TypeVar, Iterable, Tuple

from qsim.core import (QGraph, SimState, QId, QInput, QVecOp, QBitOp, QVec,
                       evaluate, addinput, addop, schedule, nqbits, nqbitsG,
                       nqbitsOp, tprod, opI, opH, opX, opY, opZ, opR, opCNOT,
                       constvec, mkvec, mkvecI)

from numpy import array

from itertools import chain

_A=TypeVar('_A')
def concat(l:List[Tuple[_A,...]])->Tuple[_A,...]:
  return tuple(chain.from_iterable(l))

class OpHandle:

  def __init__(self, c:'Circuit', op:QVecOp):
    self.circuit:'Circuit' = c
    self.op = op

  def on(self, input_id:Union[int,List[int]])->None:
    if isinstance(input_id, int):
      input_id = [input_id]
    if isinstance(input_id,list):
      if any([n in concat(list(self.circuit.pending.keys())) for n in input_id]):
        self.circuit.apply()
      self.circuit.pending[tuple(input_id)] = self.op
    else:
      assert False, f"Expected input of type List[int] or int, not {input_id}"

class Circuit:

  def __init__(self, qbit_count:int):
    self.graph = QGraph({})
    self.headid, self.graph = addinput(self.graph, qbit_count)
    self.tailid = self.headid
    self.state0:Optional[QVec] = None
    self.pending:Dict[tuple,QVecOp] = {}

  def initialize(self, state:Union[List[int],List[complex]])->None:
    if all([isinstance(x,complex) for x in state]):
      state_ = mkvec(state)
    elif all([isinstance(x,int) for x in state]):
      state_ = mkvecI(state) # type:ignore
    else:
      assert False, "Invalid initial state representation"
    assert nqbitsG(self.graph, self.headid) == nqbits(state_), (
      f"Initial state encodes {nqbits(state_)} qbits, expected "
      f"{nqbitsG(self.graph, self.headid)} qbits")
    self.state0 = state_


  def apply(self):
    n = nqbitsG(self.graph, self.headid) - 1
    op:Optional[QVecOp] = None
    while n>=0:
      if n in concat(self.pending.keys()):
        ns = [k for k in self.pending.keys() if n in k]
        assert len(ns)==1, f"More than one op change qbit {n}: {ns}"
        op2 = self.pending[tuple(ns[0])]
        n -= nqbitsOp(op2)
      else:
        op2 = opI()
        n -= 1
      op = tprod(op, op2) if op is not None else op2
    assert op is not None
    self.tailid, self.graph = addop(self.graph, op, [self.tailid])
    self.pending = {}

  @property
  def x(self)->OpHandle:
    return OpHandle(self, opX())
  @property
  def y(self)->OpHandle:
    return OpHandle(self, opY())
  @property
  def z(self)->OpHandle:
    return OpHandle(self, opZ())
  @property
  def h(self)->OpHandle:
    return OpHandle(self, opH())
  @property
  def i(self)->OpHandle:
    return OpHandle(self, opI())
  def r(self, phi:float)->OpHandle:
    return OpHandle(self, opR(phi))
  @property
  def cnot(self)->OpHandle:
    return OpHandle(self, opCNOT())

  def execute(self)->array:
    assert self.state0 is not None, "Circuit is not Initialized"
    ss = SimState({})
    if self.pending:
      self.apply()
    state=evaluate(ss, self.graph,
                   sched=schedule(self.graph),
                   state={self.headid:self.state0})
    return state[self.tailid]


def circuit(*args, **kwargs)->Circuit:
  return Circuit(*args, **kwargs)

