from numpy import allclose
from numpy.testing import assert_allclose
from math import sqrt, pi
from qsim import (QVec, circuit,addinput, addop, tprod, opX, opI, opH, opCNOT,
                  evaluate, mkvec, QGraph, braket, schedule, opmatrix)


def test_core_multyinput():
  g=QGraph({})
  i1,g=addinput(g,1)
  i2,g=addinput(g,1)
  o1,g=addop(g,tprod(opX(),opX()),[i1,i2])
  s=evaluate({i1:braket([1]),i2:braket([0])},g,schedule(g))
  assert_allclose(s[o1].mat,braket([0,1]).mat)

def test_core_18():
  g=QGraph({})
  i1,g=addinput(g,1)
  o1,g=addop(g,opX(),[i1])
  s=evaluate({i1:QVec([1.,0.])},g,schedule(g))
  assert_allclose(s[o1].mat,[0.,1.])

def test_core_111_opmatrix():
  g=QGraph({})
  i1,g=addinput(g,2)
  o1,g=addop(g,tprod(opI(),opX()),[i1])
  s=opmatrix(g,schedule(g))
  print(s[o1].mat)
  assert_allclose(s[o1].mat,[[0.,1.,0.,0.],
                             [1.,0.,0.,0.],
                             [0.,0.,0.,1.],
                             [0.,0.,1.,0.]])

def test_core_111_opmatrix_i2():
  g=QGraph({})
  i1,g=addinput(g,1)
  o1,g=addop(g,opI(),[i1])
  i2,g=addinput(g,1)
  o2,g=addop(g,opX(),[i2])
  o3,g=addop(g,tprod(opI(),opI()),[o1,o2])
  s=opmatrix(g,schedule(g))
  print(s[o3].mat)
  assert_allclose(s[o3].mat,[[0.,1.,0.,0.],
                             [1.,0.,0.,0.],
                             [0.,0.,0.,1.],
                             [0.,0.,1.,0.]])

def test_core_111():
  g=QGraph({})
  i1,g=addinput(g,2)
  o1,g=addop(g,tprod(opI(),opX()),[i1])
  s=evaluate({i1:braket([0,0])},g,schedule(g))
  print(s[o1].mat)
  assert_allclose(s[o1].mat,[0.,1.,0.,0,])
  assert_allclose(s[o1].mat,braket([0,1]).mat)

def test_core_111_i2():
  g=QGraph({})
  i1,g=addinput(g,1)
  o1,g=addop(g,opI(),[i1])
  i2,g=addinput(g,1)
  o2,g=addop(g,opX(),[i2])
  o3,g=addop(g,tprod(opI(),opI()),[o1,o2])
  s=evaluate({i1:braket([0]),i2:braket([0])},g,schedule(g))
  assert_allclose(s[o3].mat,[0.,1.,0.,0,])
  assert_allclose(s[o3].mat,braket([0,1]).mat)

def test_core_112_opmatrix():
  g=QGraph({})
  i1,g=addinput(g,2)
  o1,g=addop(g,tprod(opH(),opX()),[i1])
  s=opmatrix(g,schedule(g))
  print(s[o1].mat)
  assert_allclose(s[o1].mat,
                  [[ 0.      ,  1./sqrt(2),  0.      ,  1./sqrt(2)],
                   [ 1./sqrt(2),  0.      ,  1./sqrt(2),  0.      ],
                   [ 0.      ,  1./sqrt(2),  0.      , -1./sqrt(2)],
                   [ 1./sqrt(2),  0.      , -1./sqrt(2),  0.      ]])

def test_core_112_opmatrix_i2():
  g=QGraph({})
  i1,g=addinput(g,1)
  o1,g=addop(g,opH(),[i1])
  i2,g=addinput(g,1)
  o2,g=addop(g,opX(),[i2])
  o3,g=addop(g,tprod(opI(),opI()),[o1,o2])
  s=opmatrix(g,schedule(g))
  print(s[o3].mat)
  assert_allclose(s[o3].mat,
                  [[ 0.      ,  1./sqrt(2),  0.      ,  1./sqrt(2)],
                   [ 1./sqrt(2),  0.      ,  1./sqrt(2),  0.      ],
                   [ 0.      ,  1./sqrt(2),  0.      , -1./sqrt(2)],
                   [ 1./sqrt(2),  0.      , -1./sqrt(2),  0.      ]])

def test_core_112():
  g=QGraph({})
  i1,g=addinput(g,2)
  o1,g=addop(g,tprod(opH(),opX()),[i1])
  s=evaluate({i1:braket([0,0])},g,schedule(g))
  print(s[o1].mat)
  assert_allclose(s[o1].mat,[0.,1./sqrt(2),0.,1./sqrt(2)])

def test_core_112_i2():
  g=QGraph({})
  i1,g=addinput(g,1)
  o1,g=addop(g,opH(),[i1])
  i2,g=addinput(g,1)
  o2,g=addop(g,opX(),[i2])
  o3,g=addop(g,tprod(opI(),opI()),[o1,o2])
  s=evaluate({i1:braket([0]),i2:braket([0])},g,schedule(g))
  print(s[o3].mat)
  assert_allclose(s[o3].mat,[0.,1./sqrt(2),0.,1./sqrt(2)])

def test_core_223():
  g=QGraph({})
  i1,g=addinput(g,2)
  o1,g=addop(g,opCNOT(),[i1])
  s=evaluate({i1:braket([1,1])},g,schedule(g))
  print(s[o1].mat)
  assert_allclose(s[o1].mat,braket([1,0]).mat)


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
  c.initialize([1,1])
  c.cnot.on([0,1])
  state = c.execute()
  assert_allclose(state.mat,braket([1,0]).mat)
  print(state.mat)

def test_api1_notcnot():
  c = circuit(qbit_count=2)
  c.initialize([1,1])
  c.x.on([0])
  c.cnot.on([0,1])
  state = c.execute()
  # assert_allclose(state.mat,braket([1,0]).mat)
  print(state.mat)

def test_api1_3():
  c = circuit(qbit_count=1)
  c.initialize([0])
  c.x.on(0)
  c.h.on(0)
  state = c.execute()
  print(state.mat)
  assert_allclose(state.mat,[1./sqrt(2),-1./sqrt(2)])

