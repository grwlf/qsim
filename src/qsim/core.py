import numpy as np

from numpy import array
from math import log2
from os.path import join
from typing import (NewType, List, Union, Dict, Tuple, Iterable, Any, Callable,
                    Optional, Set)
from collections import defaultdict
from queue import PriorityQueue
from copy import copy, deepcopy

from qsim.types import (QVec, QVecOp, QBitOp, QTProd, QId, QInput,
                        QGraph, SimState)


def constvec(val:complex, nqbits:int=1)->QVec:
  return QVec([val]*(2**nqbits))

def nqbits(v:QVec)->int:
  n=log2(v.mat.shape[0])
  assert float(int(n))==n, \
    f"QVec should contain (2^N)^2 elements, not ({v.mat.shape[0]}^2)"
  return int(n)

def mkvec(v:Union[List[complex],array])->QVec:
  return QVec(array(v))

def braket(v:List[int])->QVec:
  z=np.zeros([2**len(v)])
  z[int(''.join(map(str,v)),base=2)]=1
  return QVec(z)

def mkstate(bas:List[np.complex])->QVec:
  nqbits=len(bas)
  assert float(int(nqbits))==nqbits, \
    f"State basis should contain 2^N elements, not {len(bas)}"
  return QVec(bas)

def tprod(a:QVecOp,b:QVecOp)->QVecOp:
  return QTProd(a,b)

def qbitop(mat:np.array)->QVecOp:
  return QBitOp(mat)

def nqbitsOp(op:QVecOp)->int:
  if isinstance(op, QBitOp):
    return nqbits(QVec(op.mat))
  elif isinstance(op, QTProd):
    return nqbitsOp(op.a)+nqbitsOp(op.b)
  else:
    assert False, f"Invalid QVecOp: {op}"

def qvecop2mat(op:QVecOp)->np.array:
  if isinstance(op, QBitOp):
    return op.mat
  elif isinstance(op, QTProd):
    return np.kron(qvecop2mat(op.a),qvecop2mat(op.b))
  else:
    assert False, f"Invalid QVecOp: {op}"


def opX()->QBitOp:
  return QBitOp(np.array([[0.0,1.0],[1.0,0.0]]))
def opY()->QBitOp:
  return QBitOp(np.array([[0.0,-1.0j],[1.0j,0.0]]))
def opZ()->QBitOp:
  return QBitOp(np.array([[1.0,0.0],[0.0,-1.0]]))
def opH()->QBitOp:
  return QBitOp((1/np.sqrt(2))*np.array([[1.0,1.0],[1.0,-1.0]]))
def opI()->QBitOp:
  return QBitOp(np.array([[1.0,0.0],[0.0,1.0]]))
def opR(phi:float)->QBitOp:
  return QBitOp(np.array([[1.0,0.0],[0.0,np.exp(1.0j*phi)]]))
def opCNOT()->QVecOp:
  return QBitOp(np.array([[1.0,0.0,0.0,0.0],
                          [0.0,1.0,0.0,0.0],
                          [0.0,0.0,0.0,1.0],
                          [0.0,0.0,1.0,0.0]]))

def nqbitsG(g:QGraph, qid:QId)->int:
  node:Union[QVecOp,QInput]=g.graph[qid][0]
  if isinstance(node,QBitOp) or isinstance(node,QTProd):
    return nqbitsOp(node)
  elif isinstance(node, QInput):
    return node.nqbits
  else:
    assert False, f"Invalid node {qid}: {node}"

def addinput(g:QGraph, nqbits:int)->Tuple[QId,QGraph]:
  g2=copy(g.graph)
  i=QId(len(g2.keys()))
  g2.update({i:(QInput(nqbits),[])})
  return i,QGraph(g2)

def addop(g:QGraph, op:QVecOp, inp:List[QId])->Tuple[QId,QGraph]:
  n=sum([nqbitsG(g,qid) for qid in inp])
  assert n==nqbitsOp(op), (
    f"The number of input QBits ({n}) doesn't match the "
    f"number of QBits of the operation ({nqbitsOp(op)})")
  g2=copy(g.graph)
  i=QId(len(g2.keys()))
  g2.update({i:(op,inp)})
  return i,QGraph(g2)


def kahntsort(nodes:Iterable[Any],
              inbounds:Callable[[Any],Set[Any]])->Optional[List[Any]]:
  """ Kahn's algorithm for Graph topological sorting.
  Take iterable `nodes` and pure-function `inbounds`. Output list of nodes in
  topological order or `None` if graph has a cycle.
  """
  indeg:dict={}
  outbounds:dict=defaultdict(set)
  q:PriorityQueue=PriorityQueue()
  sz:int=0
  for n in nodes:
    ns=inbounds(n)
    outbounds[n]|=set()
    indeg[n]=0
    for inn in ns:
      outbounds[inn].add(n)
      indeg[n]+=1
    if indeg[n]==0:
      q.put(n)
    sz+=1
  acc=[]
  cnt=0
  while not q.empty():
    n=q.get()
    acc.append(n)
    for on in outbounds[n]:
      indeg[on]-=1
      if indeg[on]==0:
        q.put(on)
    cnt+=1
  return None if cnt>sz else acc

def schedule(g:QGraph)->List[QId]:
  s=kahntsort(g.graph.keys(), lambda k:set(g.graph[k][1]))
  assert s is not None, "QGraph has a cycle!"
  return s

def getop(ss:SimState, op:QVecOp)->np.array:
  sop=str(op)
  if sop in ss.vecop_cache:
    return ss.vecop_cache[sop]
  mat=qvecop2mat(op)
  ss.vecop_cache[sop]=mat
  return mat

def apply_opM(ss:SimState, op:QVecOp, vec:QVec)->QVec:
  return QVec(np.matmul(getop(ss,op),vec.mat))

def evaluate(ss:SimState,
             g:QGraph,
             sched:List[QId],
             state:Dict[QId,QVec])->Dict[QId,QVec]:
  state2=deepcopy(state)
  for qid in sched:
    op,inputs=g.graph[qid]
    if isinstance(op,QInput):
      assert qid in state, (
        f"State doesn't contain the value for input node {qid}.")
    elif isinstance(op,QBitOp) or isinstance(op,QTProd):
      acc:Optional[QVec]=None
      for i in inputs:
        assert i in state2, f"State doesn't contain the value of node {i}."
        acc=QVec(np.kron(acc.mat,state2[i].mat)) if acc is not None else state2[i]
      assert acc is not None, f"Operation {str(op)} seems to have no inputs"
      state2[qid]=apply_opM(ss,op,acc)
  return state2

