from numpy import allclose
from math import sqrt, pi

from qsim import *

def test_core1():
  g=QGraph({})
  i1,g=addinput(g,1)
  o1,g=addop(g,opI(),[i1])
  ss=SimState({})
  s=evaluate(ss,g,schedule(g),{i1:vec2mat(QVec([1.0,0.0]))})
  assert(allclose(s[o1].mat,s[i1].mat))


def test_api1_221():
  c = circuit(qbit_count=2)
  # c.initialize([(1/sqrt(2)), 0.0, 0.0, (1/sqrt(2))])
  c.initialize([1.0, 1.0, 1.0, 1.0]) # State vector is not normalized
  c.h.on(0)
  c.x.on(1)
  state = c.execute()
  print(state.mat)


def test_api1_222():
  c = circuit(qbit_count=1)
  c.initialize([1.0, 1.0]) # State vector is not normalized
  c.r(pi/2).on(0)
  state = c.execute()
  print(state.mat)


def test_api1_223():
  c = circuit(qbit_count=2)
  c.initialize([1.0, 1.0, 1.0, 1.0]) # State vector is not normalized
  c.cnot.on([0,1])
  state = c.execute()
  print(state.mat)

