# QSim

## Общее описание

Данный репозиторий содержит простой квантовый симулятор, написанный на
языке Python3 с использованием библиотеки статической типизации
[MyPy](https://github.com/python/mypy).

Симулятор состоит из трех основных модулей:

  - [qsim.types](./src/qsim/types.py) Объявления типов данных.
  - [qsim.core](./src/qsim/core.py) Базовый функцинальный API.
  - [qsim.api1](./src/qsim/api1.py) Oбъектно-ориентированный API.

## Типы данных

В симуляторе используются следующие группы данных:

1.  Типы данных для задания условий симуляции:
    
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
    
      - `QVec` служит для задания векторов состояний
      - `QVecOp` тип-синоним, перечисляющий варианты описания квантовых
        операций:
          - `QBitOp` в виде матрицы
          - `QTProd` в виде вертикальной комбинации других операций

2.  Типы данных для выполнения симуляции:
    
    ``` python numberLines
    
    QId=NewType('QId',int)
    
    @dataclass(frozen=True, eq=True)
    class QInput:
      nqbits:int
    
    @dataclass(frozen=True, eq=True)
    class QGraph:
      graph:Dict[QId, Tuple[Union[QVecOp,QInput], List[QId]]]
    ```
    
      - `QGraph` Описывает граф квантовых операций, граф задан
        перечислением вершин и рёбер. С уздами графа
        ассоциированы квантовые операции. Вспомогательные типы
        данных:
          - `QId` - Идентификатор узла. Тип-обертка над числом для
            удобства статической типизации.
          - `QInput` - Тип входного узла.

## Базовые функции

Основной функционал реализован в модуле `qsim.core`. Также как и с
типами, можно выделить две основные группы функций:

1.  Функции для задания условий симуляции
2.  Функции для выполнения расчетов

## Примеры

### Использование объектно-ориентированного API

#### Обзор ОО-API

Соответствует пп.2.1 (основная задача),2.2.1(установка количества кубит
в стартовом состоянии)

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

*Замечание: результат отличается от примера в п.2.1 условия. Вероятно,
разница в порядке нумерации кубитов. Изменим порядок нумерации:*

``` python numberLines
print(c.opmatrix(1,0).mat)
```

``` stdout
[[ 0.          0.          0.70710678  0.70710678]
 [ 0.         -0.          0.70710678 -0.70710678]
 [ 0.70710678  0.70710678  0.          0.        ]
 [ 0.70710678 -0.70710678  0.         -0.        ]]
```

### Параметризирвоанные операции

Соответствует пп.2.2.2

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

### Двухкубитные операции

Соответствует пп.2.2.3

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

### Использование базового функционального API

Соответствует пп.2.2.4

#### Расчет матрицы комбинированной операции `X * H`.

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

# References

1.  [Linear Algebra for Quantum
    Computation](https://link.springer.com/content/pdf/bbm%3A978-1-4614-6336-8%2F1.pdf)
2.  [ScyPy](https://docs.sympy.org/latest/modules/physics/quantum/tensorproduct.html)
3.  [Numpy Kron
    documentation](https://numpy.org/doc/stable/reference/generated/numpy.kron.html)
