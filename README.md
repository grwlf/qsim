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
    
      - `QVec` служит для задания векторов состояний. Элементы вектора
        состояний описывают коэффициенты при базисных векторах,
        соответствующих состоянию системы из N кубитов. Длина
        вектора должна быть 2^N. Пример: элементы вектора
        `QVec([a,b,c,d])` соответствуют коэффициентам при базисных
        векторах в таком порядке: `|00>`, `|01>`, `|10>`, `|11>`.
      - `QVecOp` тип-синоним, перечисляющий варианты описания квантовых
        операций:
          - `QBitOp` для задания операции в виде матрицы
          - `QTProd` для задания операции в виде вертикальной комбинации
            других операций

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
    
      - `QGraph` Описывает направленный граф квантовых операций, граф
        задан перечислением вершин и рёбер (через идентификаторы
        входных вершин). С узлами графа ассоциированы квантовые
        операции. Вспомогательные типы данных:
          - `QId` - Идентификатор узла. Тип-обертка над числом для
            удобства статической типизации.
          - `QInput` - Тип входного узла, значение которого должно быть
            задано пользователем перед началом симуляции.

## Функции базового API

Основной функционал реализован в модуле `qsim.core`. Также как и с
типами, можно выделить следующие основные группы функций:

1.  Функции для задания условий симуляции
    
    1.  Функции для операций над векторами состояний. Вектроы состояний
        можно создать функциями `mkvec` и `braket`. Из операций в
        отдельную функцию вынесены: получение тензорного
        произведения `tprod` и получение числа кубитов,
        задаваемых данным вектромо состояний. Функция `braket`
        реализована упрощенно, поддерживаются только значения `0` и
        `1`: Пример: инициализация вектора состояний двух кубитов,
        соответствующего значениям 0 и 1.
        
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
    
    2.  Функции для операций над операциями. Простую операцию можно
        создавать из матрицы операции с помощью `qbitop` и из
        других операций с помощью `pairop`.

2.  Операции с графом квантовых вычислений. В базовом API работа с
    графом производится в три этапа: формирование, планирование,
    свертка.
    
    1.  Для формирования графа используются функции `addinput` и
        `addop`. Пример: задание графа из одной комбинированной
        2-хкубитной операции с двумя однокубитными входами.
        
        ``` python numberLines
        from qsim import QGraph, addinput, addop, opX, opH, pairop
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
    
    2.  Планирование вычислений представлено функцией `schedule` которая
        производит топологическую сортировку графа и возвращает список
        идентификаторов узлов, задавая тем самым очередность
        вычислений.
    
    3.  Выполнение вычислений производят функции `evaluate` и
        `opmatrix`. Они могут быть использованы независимо друг от
        друга.

3.  Функции предопределенных квантовых операций:
    
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

## Примеры

### Обзор ОО-API

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

#### Использование базового функционального API.

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

## Расширения

Соответствует пп.2.2.4.

### Поддержка новых типов операций

Для поддержки новых операций в базовом API достаточно описать их в виде
функции с использованием корректных типов данных.

Для добавление таких операций в объектно-ориентированное API достаточно
пронаследоваться от класса `Circuit` и доопределить в наследнике новую
функцию или свойство.

### Поддержка оптимизатора цепочек

Поскольку в качестве базовой структуры операций в данном симуляторе
используется граф, в нем легко могут быть доопределены алгоритмы из
репертуара теории графов.

``` python numberLines
g=QGraph({})
i1,g=addinput(g,2)
o1,g=addop(g,pairop(opH(),opX()),[i1])
...
g2=optimize(g) # Callable[[QGraph],QGraph]
...
s=evaluate(g2,schedule(g2))
print(s[o1].mat)
```

### Поддержка новых типов бэкендов

Для поддержки новых типов бэкендов необходимо согласованно добавить
соответствующие функции планировки и расчетов. К примеру,
вычисление на воображаемом FPGA-процессоре может быть записано
в базовом API так.

``` python numberLines
with fpga_resourse('/dev/fpga1') as r:
  g=QGraph({})
  i1,g=addinput(g,2)
  o1,g=addop(g,pairop(opH(),opX()),[i1])
  ...
  s=evaluate_FPGA(g,r,schedule_FPGA(g,r))
  print(s[o1].mat)
```

# References

1.  [Linear Algebra for Quantum
    Computation](https://link.springer.com/content/pdf/bbm%3A978-1-4614-6336-8%2F1.pdf)
2.  [ScyPy](https://docs.sympy.org/latest/modules/physics/quantum/tensorproduct.html)
3.  [Numpy Kron
    documentation](https://numpy.org/doc/stable/reference/generated/numpy.kron.html)
