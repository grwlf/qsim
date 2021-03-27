# QSim

\[EN\]\[[RU](./README-RU.md)\]

QSim - is a simple quantum simulator, written in Python3 with the
extensive use of [MyPy](https://github.com/python/mypy) static typing.
This project was originally a part of a job interview.

QSim consists of the following modules:

  - [qsim.types](./src/qsim/types.py) Data type declaration.
  - [qsim.core](./src/qsim/core.py) Core functional API.
  - [qsim.api1](./src/qsim/api1.py) Object-oriented API wrapper.

The tests are in [./tests/test\_all.py](./tests/test_all.py)

# Contents

1.  [Install](#install)
2.  [Examples](#examples)
3.  [Details](#details)
4.  [References](#references)

# Install

  - Use standard Python tools to install this project: `python3 setup.py
    install`.
  - It is possible to use this package in-place `export
    PYTHONPATH=$(pwd)/src:$PYTHONPATH`.
  - README files are to be compiled with the `codebraid` utility. Use
    the Makefile rule to do it `make README.md`
  - To run the tests use `pytest`.
  - The project also contains [expressions](./shell.nix) for the
    [Nix](https://nixos.org/nix) package manager. One could use its
    `nix-shell` command to enter the development environment with all
    the dependencies installed.

# Examples

### Object oriented API

``` python numberLines
from qsim import circuit
c = circuit(qbit_count=2)
c.initialize([1,0])
c.h.on(0)
c.x.on(1)
c.execute()
print(c.opmatrix(0,1).mat)
```

``` stdout
[[ 0.          0.70710678  0.          0.70710678]
 [ 0.70710678  0.          0.70710678  0.        ]
 [ 0.          0.70710678 -0.         -0.70710678]
 [ 0.70710678  0.         -0.70710678 -0.        ]]
```

*Note: the result differs from the specification. The reason is probably
in the qubit numbering scheme:*

``` python numberLines
print(c.opmatrix(1,0).mat)
```

``` stdout
[[ 0.          0.          0.70710678  0.70710678]
 [ 0.         -0.          0.70710678 -0.70710678]
 [ 0.70710678  0.70710678  0.          0.        ]
 [ 0.70710678 -0.70710678  0.         -0.        ]]
```

### Parametrized operations

``` python numberLines
from math import pi
c = circuit(qbit_count=1)
c.initialize([1])
c.r(pi/2).on(0)
s = c.execute()
print(s[0].mat)
```

``` stdout
[0.000000e+00+0.j 6.123234e-17+1.j]
```

### 2-qubit operations

``` python numberLines
c = circuit(qbit_count=2)
c.initialize([1,1])
c.cnot.on([0,1])
s = c.execute()
print(s[(0,1)].mat)
```

``` stdout
[0. 0. 1. 0.]
```

#### Functional API

``` python numberLines
from qsim import QGraph, addinput, addop, opX, opH, schedule, opmatrix, pairop
g=QGraph({})
i1,g=addinput(g,2)
o1,g=addop(g,pairop(opH(),opX()),[i1])
s=opmatrix(g,schedule(g))
print(s[o1].mat)
```

``` stdout
[[ 0.          0.70710678  0.          0.70710678]
 [ 0.70710678  0.          0.70710678  0.        ]
 [ 0.          0.70710678  0.         -0.70710678]
 [ 0.70710678  0.         -0.70710678  0.        ]]
```

# Details

## Data types

Simulator uses the following data types:

1.  Data types for the input data:
    
    ``` python numberLines
    
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
    ```
    
      - `QVec` encodes qubit states and operation state matrices. The
        elemenents describe basis multiplying coefficients. To descibe N
        qubits, the lengs of the state vector should have the length of
        `2**N`. Example: the elements of `QVec([a,b,c,d])` correspond to
        the multipliers of `|00>`, `|01>`, `|10>`, `|11>` basis vectors,
        in this order.
      - `QVecOp` is an alias describing the union of the following
        types:
          - `QBitOp` direclty declares an operation using the operation
            matrix
          - `QTProd` describes a tensor product of two qubit operation

2.  Data types to handle the simulation process
    
    ``` python numberLines
    
    QId=NewType('QId',int)
    
    @dataclass(frozen=True, eq=True)
    class QInput:
      nqbits:int
    
    @dataclass(frozen=True, eq=True)
    class QGraph:
      graph:Dict[QId, Tuple[Union[QVecOp,QInput], List[QId]]]
    ```
    
      - `QGraph` declares the directed graph of quantum operations.
          - `QId` - the integer identifier of a node, to aid the static
            typing.
          - `QInput` - type of input nodes which don’t carry associated
            operations.

## Functional API

The QSim base functions reside in the `qsim.core`. One could split it
into the following logical parts:

1.  Functions for defining input conditions.
    
    1.  Functions for setting up state vectors. One could create qubit
        state vectors with `mkvec` and `braket`. For operations, ,
        `pairop` to combine operations using the Kronecker product.
        
        `braket` function is currently limited to accept only `0` and
        `1` values.
        
        Example: different initializions of the 2 qubit state vector
        
        ``` python numberLines
        from qsim.core import braket
        for q0 in [0,1]:
          for q1 in [0,1]:
            print(q0, q1, ':', braket([q0,q1]))
        ```
        
        ``` stdout
        0 0 : QVec(mat=array([1., 0., 0., 0.]))
        0 1 : QVec(mat=array([0., 1., 0., 0.]))
        1 0 : QVec(mat=array([0., 0., 1., 0.]))
        1 1 : QVec(mat=array([0., 0., 0., 1.]))
        ```
    
    2.  Functions for manipulating operations. One could create simple
        operation with `qbitop` or combine several operations into one
        with `pairop`. `nqbitsOp` could be used to get the required
        number of input qubits.

2.  Functions for defining the graph of quantum operations. Base API
    contains basic methods of creation, planning and execution of the
    simulation.
    
    1.  Functions `addinput` and `addop` create nodes of the computaion
        graph. Example: 2-qubit operation with two 1-qubit inputs.
        
        ``` python numberLines
        from qsim import QGraph, addinput, addop, opX, opH, opI, pairop
        g=QGraph({})
        i1,g=addinput(g,1)
        i2,g=addinput(g,1)
        o1,g=addop(g,pairop(opH(),opX()),[i1,i2])
        print(g)
        ```
        
        ``` stdout
        QGraph(graph={0: (QInput(nqbits=1), []), 1: (QInput(nqbits=1), []), 2: (QTProd(a=QBitOp(mat=array([[ 0.70710678,  0.70710678],
               [ 0.70710678, -0.70710678]])), b=QBitOp(mat=array([[0., 1.],
               [1., 0.]]))), [0, 1])})
        ```
    
    2.  Scheduling the computation is performed by the `schedule`
        function. It is a simple algorithm which runs the topological
        sort and returns the list of nodes in the order of execution.
    
    3.  `evaluate` and `opmatrix` run the simulation and compute the
        operation state matrix. They could be used independently from
        each other.

3.  There following operations are pre-defined:
    
    ``` python numberLines
    
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
    ```

## Object oriented API

OO API adds the following new type for referencing the qubit states.

``` python numberLines

InputId = Union[int,tuple]
```

Example:

``` python numberLines
0           # Refers to the state of qubit 0
1           # Refers to the state of qubit 1
(0,1)       # Refers to the entangled state of qubits 0 and 1
((0,1),2)   # Entangled state for the qubits 0,1 and 2
```

State names specifiy the state to modify next:

``` python numberLines
c = circuit(qbit_count=3)
c.initialize([0,0,0])
c.x.on([0])               # Apply X to the state 0
c.cnot.on([0,1])          # Apply CNOT to the entangled state of  (0,1)

opI3 = pairop(opI(),pairop(opI(),opI()))
c.op(opI3).on([(0,1),2])  # Apply 3-qubit ID to the state of 0,1 and 2
```

OO API prevents user from accessing qubits which are already entangled:

``` python numberLines
try:
  c.cnot.on([0,1])
  assert False, "This should not happen"
except KeyError:
  pass
```

# References

1.  [Linear Algebra for Quantum
    Computation](https://link.springer.com/content/pdf/bbm%3A978-1-4614-6336-8%2F1.pdf)
2.  [ScyPy](https://docs.sympy.org/latest/modules/physics/quantum/tensorproduct.html)
3.  [Numpy Kron
    documentation](https://numpy.org/doc/stable/reference/generated/numpy.kron.html)
