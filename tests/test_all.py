from numpy import allclose
from numpy.testing import assert_allclose
from math import sqrt, pi
from qsim import *

def test_core_X():
  g=QGraph({})
  i1,g=addinput(g,1)
  i2,g=addinput(g,1)
  o1,g=addop(g,tprod(opX(),opX()),[i1,i2])
  ss=SimState({})
  s=evaluate(ss,g,schedule(g),{i1:braket([1]),
                               i2:braket([0])})
  assert_allclose(s[o1].mat,braket([0,1]).mat)

def test_core_18():
  g=QGraph({})
  i1,g=addinput(g,1)
  o1,g=addop(g,opX(),[i1])
  ss=SimState({})
  s=evaluate(ss,g,schedule(g),{i1:QVec([1.,0.])})
  assert_allclose(s[o1].mat,[0.,1.])

def test_core_111():
  g=QGraph({})
  i1,g=addinput(g,2)
  o1,g=addop(g,tprod(opX(),opI()),[i1])
  ss=SimState({})
  s=evaluate(ss,g,schedule(g),{i1:mkvec([1.,0.,0.,0.])})
  assert_allclose(s[o1].mat,[0.,0.,1.,0,])

def test_core_112():
  g=QGraph({})
  i1,g=addinput(g,2)
  o1,g=addop(g,tprod(opX(),opH()),[i1])
  ss=SimState({})
  s=evaluate(ss,g,schedule(g),{i1:mkvec([1.,0.,0.,0.])})
  assert_allclose(s[o1].mat,[0.,0.,1./sqrt(2),1./sqrt(2)])

def test_core_112_2():
  g=QGraph({})
  i1,g=addinput(g,2)
  o1,g=addop(g,tprod(opX(),opH()),[i1])
  ss=SimState({})
  s=evaluate(ss,g,schedule(g),{i1:braket([0,1])})
  print(s[o1].mat)
  assert_allclose(s[o1].mat,[0,0,1./sqrt(2),-1./sqrt(2)])

def test_api1_221():
  c = circuit(qbit_count=2)
  c.initialize([0,1])
  c.h.on(0)
  c.x.on(1)
  state = c.execute()
  print(state.mat)
  assert_allclose(state.mat,[0,0,1./sqrt(2),-1./sqrt(2)])

def test_api1_222():
  c = circuit(qbit_count=1)
  c.initialize([1])
  c.r(pi/2).on(0)
  state = c.execute()
  print(state.mat)

def test_api1_223():
  c = circuit(qbit_count=2)
  c.initialize([1,0])
  c.cnot.on([0,1])
  state = c.execute()
  print(state.mat)

def test_api1_3():
  c = circuit(qbit_count=1)
  c.initialize([0])
  c.x.on(0)
  c.h.on(0)
  state = c.execute()
  print(state.mat)
  assert_allclose(state.mat,[1./sqrt(2),-1./sqrt(2)])

