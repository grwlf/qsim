from typing import List, Union, Optional, Dict, Any, TypeVar, Iterable, Tuple

from qsim.core import (QGraph, SimState, QId, QInput, QVecOp, QBitOp, QVec,
                       evaluate, addinput, addop, schedule, nqbits, nqbitsG,
                       nqbitsOp, opI, opH, opX, opY, opZ, opR, opCNOT,
                       mkvec, braket, opmatrix, tprod)

from numpy import array, kron

from itertools import chain, combinations

InputId = Union[int,tuple]

class OpHandle:

  def __init__(self, c:'Circuit', op:QVecOp):
    self.circuit:'Circuit' = c
    self.op = op

  def on(self, input_ids:Union[InputId,List[InputId]])->None:
    input_id_l:List[InputId] = [input_ids] if not isinstance(input_ids,list) else input_ids
    input_id_2 = tuple(input_id_l) if len(input_id_l)>1 else input_id_l[0]
    qid, self.circuit.graph = \
      addop(self.circuit.graph, self.op,
            [self.circuit.tails[x] for x in input_id_l])
    self.circuit.tails[input_id_2] = qid # type:ignore

class Circuit:

  def __init__(self, qbit_count:int):
    self.graph = QGraph({})
    self.state0:Dict[QId,QVec] = {}
    self.state:Optional[Dict[QId,QVec]] = None
    self.mstate:Optional[Dict[QId,QVec]] = None
    self.tails:Dict[InputId,QId] = {}
    self.heads:Dict[int,QId]={}
    for nbit in range(qbit_count):
      qid,self.graph = addinput(self.graph, 1)
      self.heads[nbit] = qid
      self.tails[nbit] = qid


  def initialize(self, state:Union[List[int],List[List[complex]]])->None:
    if isinstance(state,list) and all([isinstance(x,complex) for x in state]):
      assert len(state) == len(self.heads.keys())
      for (n,qid),value in zip(self.heads.items(),state):
        self.state0[qid] = mkvec(value) # type:ignore
    elif isinstance(state,list) and all([isinstance(x,int) for x in state]):
      assert len(state) == len(self.heads.keys())
      for (n,qid),value in zip(self.heads.items(),state):
        self.state0[qid] = braket([value]) # type:ignore
    else:
      assert False, "Invalid initial state representation"

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

  def execute(self)->Dict[Union[int,tuple],QVec]:
    assert self.state0 is not None, "Circuit is not initialized"
    self.state = evaluate(self.state0, self.graph,
                          sched=schedule(self.graph))
    self.mstate = opmatrix(self.graph, sched=schedule(self.graph))
    return {code:self.state[self.tails[code]] for code in self.tails.keys()}

  def opmatrix(self, *args)->QVec:
    assert self.mstate is not None
    return tprod([self.mstate[self.tails[a]] for a in args])


def circuit(*args, **kwargs)->Circuit:
  return Circuit(*args, **kwargs)

