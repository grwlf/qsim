import numpy as np

from math import log2
from os.path import join
from typing import (NewType, List, Union, Dict, Tuple, Iterable, Any, Callable,
                    Optional, Set)
from collections import defaultdict
from queue import PriorityQueue
from dataclasses import dataclass
from copy import copy

@dataclass(frozen=True, eq=True)
class QVec:
  basis:List[np.complex]

@dataclass(frozen=True, eq=True)
class QVecM:
  mat:np.array

def nqbits(v:QVec)->int:
  n=log2(len(v.basis))
  assert float(int(n))==n, \
    f"QVec should contain 2^N elements, not {len(v.basis)}"
  return int(n)

def nqbitsM(v:QVecM)->int:
  n=v.mat.shape[0]
  assert float(int(n))==n, \
    f"QVecM should contain (2^N)^2 elements, not ({v.mat.shape[0]}^2)"
  return int(n)

def vec2mat(v:QVec)->QVecM:
  return QVecM(np.array(v.basis, dtype=np.complex)*
               np.eye(int(2**nqbits(v)), dtype=np.complex))

def mat2vec(v:QVecM)->QVec:
  return np.matmul(np.ones([1,int(2**nqbitsM(v))],dtype=np.complex), v.mat)

def mkstate(bas:List[np.complex])->QVec:
  nqbits=len(bas)
  assert float(int(nqbits))==nqbits, \
    f"State basis should contain 2^N elements, not {len(bas)}"
  return QVec(bas)

QVecOp=Union['QBitOp','QTProd']

@dataclass(frozen=True, eq=True)
class QBitOp:
  mat:np.array

@dataclass(frozen=True, eq=True)
class QTProd:
  a:QVecOp
  b:QVecOp

def tprod(a:QVecOp,b:QVecOp)->QVecOp:
  return QTProd(a,b)

def qbitop(mat:np.array)->QVecOp:
  return QBitOp(mat)

def nqbitsOp(op:QVecOp)->int:
  if isinstance(op, QBitOp):
    return nqbitsM(QVecM(op.mat))
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

QId=NewType('QId',int)

@dataclass(frozen=True, eq=True)
class QInput:
  n:int

@dataclass(frozen=True, eq=True)
class QGraph:
  graph:Dict[QId, Tuple[Union[QVecOp,QInput], List[QId]]]

def nqbitsG(g:QGraph, qid:QId)->int:
  node:Union[QVecOp,QInput]=g.graph[qid][0]
  if isinstance(node,QBitOp) or isinstance(node,QTProd):
    return nqbitsOp(node)
  elif isinstance(node, QInput):
    return 1
  else:
    assert False, f"Invalid node {qid}: {node}"

def addinput(g:QGraph)->Tuple[QId,QGraph]:
  g2=copy(g.graph)
  i=QId(len(g2.keys()))
  n=len([i[0] for i in g2.values() if isinstance(i[0],QInput)])
  g2.update({i:(QInput(n),[])})
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
  """ Kahn's algorithm for topological sorting.
  Take iterable `nodes` and pure-function `inbounds`. Output list of nodes in
  topological order, or None if graph has a cycle.

  One modification is that we use PriorityQueue insted of plain list to put
  take name-order into account.
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

@dataclass(frozen=True, eq=True)
class SimState:
  vecop_cache:Dict[str,np.array]

def getop(ss:SimState, op:QVecOp)->np.array:
  sop=str(op)
  if sop in ss.vecop_cache:
    return ss.vecop_cache[sop]
  mat=qvecop2mat(op)
  ss.vecop_cache[sop]=mat
  return mat

def apply_opM(ss:SimState, op:QVecOp, vec:QVecM)->QVecM:
  return QVecM(np.matmul(getop(ss,op),vec.mat))

def evaluate(ss:SimState,
             g:QGraph,
             s:List[QId],
             state:Dict[QId,QVecM])->Dict[QId,QVecM]:
  for qid in s:
    op,inputs=g.graph[qid]
    for iid in inputs:
      assert iid in state.keys(), "Input {iid} is not yet evaluated (impossible!)"
  # TODO




# def eval_chainM(ss:SimState, chain:QChain, vec:QVecM)->QVecM:
#   acc=vec
#   for vo in chain.chain:
#     acc=apply_opM(ss, vo, acc)
#   return acc

# def eval_chain(ss:SimState, chain:QChain, vec:QVec)->QVec:
#   return mat2vec(eval_chainM(ss, chain, vec2mat(vec)))

