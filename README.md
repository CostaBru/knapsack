# Rethinking the knapsack and set partitions. 

The 1-0 unbounded knapsack problem, a classic problem in dynamic programming, was extended to incorporate rational numbers and multiple dimensions. 
Special cases were solved using polynomial time and integrated into a new partition algorithm. 

Additionally, the algorithm for the equal subset problem was optimized to exhibit exponential complexity only in terms of the number of partitions. 
The restriction on integer input types was also removed. 
This research includes the implementation of the algorithms in both ``python`` and ``cpp``, as well as performance analysis and reports.
- The polynomial time and space algorithm for unbounded subset sum knapsack problem for positive integer and rational numbers. 

- The enhanced exponential implementation of Nemhauser-Ullmann ``NU`` algorithm.

- The exponential ``KB`` algorithm for unbounded 1-0 knapsack problem for positive integer and rational weights and profits.

- The comparison of the ``NU`` with new ``KB``.

- The polynomial hybrid ``KB-NU`` algorithm for unbounded 1-0 knapsack problem for positive integer and rational weights and profits.

- The exponential algorithm for ``T`` independent dimensions unbounded 1-0 knapsack problem. The counting and non increasing order cases were solved in polynomial time. A non exact greedy algorithm was introduced for general case.

- The greedy ``M`` independent dimension knapsack algorithm that exponential in reduced ``N`` that depends on given constraint.
  
- The ``M`` equal-subset-sum of ``N`` integer number set that is exponential in ``M`` only.

- The algorithms for multiple knapsack that is exponential in numbers of knapsacks.

- ``M`` strict partition problem solver. The run time complexity is exponential in number of partition. That algorithm runtime is ``M`` times slower than the subset sum problem.

- Test cases and iteration reports.

# Python implementation and usage 

The ``API/main.py`` file has API for described algorithms. 

The ``tests`` directory has tests, and performance report generators.  

The ``Out`` folder is considered as output for tests and reports if ``flags/flags.py`` printToFile set to true.

There are 8 python methods to use:

- ``partitionN``, which gets number set to partition, partitions number or list of particular sizes of each partition, strict partition group size.

- ``hybridPartitionN``, which gets number set to partition, partitions number or list of particular sizes of each partition, strict partition group size.

	The result is tuple of quotients, reminder, optimizationCount. Hybrid partition uses KB-NU algorithm as grouping operator.
  
- ``subsKnapsack``, which used in partitionN as set grouping operator. It requires the following parameters: size of knapsack, items, iterator counter array.

	The result is tuple of bestValue, bestItems.
- ``knapsack``, gets size of knapsack, items, values, iterator counter array. Which used in greedy solver in knapsackNd.

	The result is tuple of bestValue, bestSize, bestItems, bestValues.
- ``knapsackNd``, expects the single tuple as size constrains of knapsack, items as tuples of dimensions, values, iterator counter array. It is used in partitionN method in the strict group size case.

	The result is tuple of bestValue, bestSize, bestItems, bestValues.
- ``paretoKnapsack`` is implementation of KB-Nemhauser-Ullman algorithm. Gets size of knapsack, items, values, iterator counter array. It used in hybrid knapsack, and as greedy solver in knapsackNd.

	The result is tuple of bestValue, bestSize, bestItems, bestValues.	
- ``hybridKnapsack`` is hybrid of KB and NU.

    The result is tuple of bestValue, bestSize, bestItems, bestValues.	
- ``hybridKnapsackNd`` NU algorithm called for worst exponential case of KB.

	The result is tuple of bestValue, bestSize, bestItems, bestValues.

- ``greedyKnapsackNd`` Non exact greedy N dimensional knapsack solver.
  
	The result is tuple of bestValue, bestSize, bestItems, bestValues.
	
	<details>
		<summary> Example </summary>
  
	```python
	
	IC = [0]
	
	partN, A  = 3, list(range(1, (81 * 9) + 1))
	 
	quotients, reminder, optCount = partitionN(items = A, sizesOrPartitions = partN, groupSize = 0, iterCounter=IC, optimizationLimit = -1)

    assert len(reminder) == 0 and len(quotients) == partN

    s, A = Decimal("10.5"), list(reversed([Decimal("0.2"), Decimal("1.200001"), Decimal("2.9000001"), Decimal("3.30000009"), Decimal("4.3"), Decimal("5.5"), Decimal("6.6"), Decimal("7.7"), Decimal("8.8"), Decimal("9.8")]))

    expectedValue = Decimal("10.20000109")    

    bestProfitD2, optDimD2, optItemsD2, optValuesD2 = knapsackNd(constraints = wPoint((s, s)), items = [wPoint((a, a)) for a in A], values = A, iterCounter=IC)
    assert expectedValue == bestProfitD2

    bestProfit10, optDim10, optItems10, optValues10 = knapsack(size = s, items = A, values = A, iterCounter=IC)
    assert expectedValue == bestProfit10

    bestProfitP, optDimP, optItemsP, optValuesP = paretoKnapsack(size = s, items = A, values = A, iterCounter=IC)
    assert expectedValue == bestProfitP

    bestProfitS, optItemsS = subsKnapsack(size = s, items = A, iterCounter=IC)   
    assert expectedValue == bestProfitS
	
	```
	</details>
	
	Please see more test cases for examples of usage.

# C++ port

There are ``super-increasing``, ``kb limit``, ``pareto``, and ``N dimension greedy`` knapsack solvers ported. The library was built using ``CLion``, ``mingw64`` (9.0) and ``g++`` (Rev9, Built by MSYS2 project) 10.2.0.

Right now it performs up to ``10x`` faster than python implementation, and it is the subject for further optimizations.

<details>
		<summary> Subset sum example </summary>

  ```cpp

    std::vector<double> A = { 0.2,
                              1.200001,
                              2.9000001,
                              3.30000009,
                              4.3,
                              5.5,
                              6.6,
                              7.7,
                              8.8,
                              9.8};

    std::sort(A.begin(), A.end(), std::greater());

    double s = 10.5;
    double expectedValue = 10.20000109;

    std::vector<int> indexes(A.size(), 0);
    std::iota(indexes.begin(), indexes.end(), 0);

    auto result = kb_knapsack::knapsack1(s, A, A, indexes);

    auto opt1    = std::get<0>(result);
    auto optSize = std::get<1>(result);

    boost::ut::expect(opt1 == expectedValue) << "Not equal ";
    boost::ut::expect(optSize <= s) << "Greater than size ";

   ```

</details>	

Please see more test cases for examples of usage in ``./cpp/knapsack_tests``.

We used Pybind11 ``https://github.com/pybind/pybind11`` to prepare an experimental python API.  

Please refer to ``python3/tests/test_cpp_apy.py``. First of all, you need to build the ``cpp`` sources, then ``knapsack_python_api.{your platform}.pyd`` extention file appears in ``python3/tests/`` folder and you will be able to run api tests.

You might have below error while you are importing ``pyd`` file:
``ImportError: DLL load failed: The specified module could not be found.``

To overcome it, you can try out ``https://github.com/lucasg/Dependencies`` tool.
It shows all dependencies your pyd file has at the moment. And, you will be able to locate 
those dependency paths, register it via ``os.add_dll_directory("your dlls path")`` 
right before importing ``knapsack_python_api`` extension in your python script.
# Introduction

The knapsack problem is defined as follows: 

We are given a set of ``N`` items, each item ``J`` having a ``Pj`` value and a weight ``Wj`` . The problem is to choose a subset of the
items such that their overall profit is maximized, while the overall weight does not exceed a given capacity ``C`` [6].

Let's consider classical bottom-up dynamic programming solution for unbounded knapsack problem. Let's call it ``DPS``. 

Bounded version of that problem has known way of reduction to unbounded one [5].

The ``DPS`` algorithm uses a recurrent formula to calculate the maximum value by iterating through the item weights array and evaluating every possible weight using a DP table. 
This algorithm is efficient for small numbers, but it has a limitation of only being able to use positive integers as input. The time and memory complexity of the ``DPS`` algorithm is ``O(N * M)`` which is known as pseudopolynomial.

While working on the equal subset sum problem, I discovered that the ``DPS`` algorithm performs extra calculations for possibilities that would never be part of the optimal solution. The classic ``DPS`` algorithm works with integers from the set ``1`` to ``C``, where ``C`` is the size of the knapsack.
However, we observed that the optimal solution exists in a subset ``W``, where ``W`` contains items and sums of all items that are less than ``C``. This property addresses the weakness of the ``DPS`` algorithm in terms of large memory requirements.
Classic ``DPS`` works in integer set ``1..C`` integer numbers, where ``C`` is size of knapsack. [1]

I observed that the optimal solution exists in subset ``W``, where ``W`` contains items and sums of all items that less than ``C``. This property solves weakness property of ``DPS`` algorithm - large memory requirements.  

When weight considered is not a part of sum of items then classic ``DPS`` algorithm compares and copies maximum value reached to next DP table cell. 

# The main idea of KB knapsack

`` Axiom 1. The optimal solution for the knapsack problem can be found within the set of all possible sums of the item weights.`` 

This is a logical conclusion as the optimal solution must only consist of the given items. 

Given `` Axiom 1``, that the optimal solution can be found within the set of all possible sums of the item weights, we can focus on this set of weights and sums of weights when solving the knapsack problem. To accomplish this, we will perform the dynamic programming algorithm over this collection for each item.

We will refer to the sum of weight visited with the current weight as a ``w point``. To solve the problem, we will generate the set of weight points for each knapsack item.

This approach involves providing the current weight and sum of the current item's weight along with all previously visited weight points. Then, we will apply the recurrent formula for the dynamic programming algorithm to this new set.

That growing collection gives as next recurrent expression for inner loop for ``Nth`` iteration:

``[ Wi + ((Wi + Wi-1) + (Wi + Wi-2) + ... + (Wi + Wi-n)) ]``, 

where ``W`` is the weight, and ``I`` is the index in collection of given items. At each ``N`` iteration we have expected maximum numbers of item weights we need to visit to reach optimal solution. 

The recurrent formula for that collection is ``(2 ** N) - 1``. Which is exponential in ``N``. That exponent is limited by ``C`` the size of knapsack. 

Taking into account that the size of ``w points`` subset is less then set ``1..C`` the new algorithm requires less iterations and memory to find the optimal solution.

The primary factor contributing to the exponential growth of the algorithm is the increasing number of distinct sums generated after each iteration of the ``Nth`` item.

As the partition function of each existing sum increases exponentially with respect to the square root of its argument, the likelihood of generating a new, unique sum diminishes as the number of sums increases.

This non-linear limitation of the algorithm is an area for further study.

In case of ``T`` dimensional knapsack, each new dimension added decreases this limitation effect significantly. 

Having that, we can state that the best case for knapsack is all duplicate weights in given set. The complexity is ``O(N**2)``,  in that case. 

On the other hand, the super-increasing sequence of weights [10] can be solved in ``O(N LogN)`` in case of a single dimension.

<details>
  <summary> Super-increasing sequence definition </summary>

Number sequence is called super-increasing if every element of the sequence is greater than the sum of all previous elements in the sequence.

</details>

The worst case scenario for the algorithm is when the set of items contains as many unique weights as possible. 
In this case, the algorithm performance is the worst, particularly when the set of items is almost super-increasing, where each sum of the previous ``N `` items minus one is equal to the next N item in the ordered set.

The traditional DPS algorithm accumulates the result in a ``[N x C]`` DP table, where ``C`` is the capacity of the knapsack. 
However, the proposed new algorithm does not visit all possible weights from ``1`` to ``C``, but only the sums and weights themselves. 
In this approach, we keep track of the maximum weight and value achieved for each w point visited. 
When all ``w points`` have been processed or when the optimal solution is found earlier (if the item weight is equal to the item value), we can backtrace the optimal solution using the filled-out ``DP`` table.

The proposed algorithm utilizes an array of maps to store the set of `w points` for each item in the knapsack problem. 
The use of a map allows for efficient access time to specific `w points` in the set, while also providing a mechanism to check for the distinctness of newly generated sums. 
To ensure that the dynamic programming algorithm is able to process the `w points` in increasing order, a merge operation is performed between the previous set of `w points` and the newly generated set. 
This merge operation is performed in a time complexity of `O(N + M)`, where N is the number of previous `w points` and `M` is the number of new `w points` generated by the current item's weight. 
This approach allows for efficient processing of the knapsack problem while also ensuring the correctness of the dynamic programming algorithm.

Classic ``DPS`` uses recurrent formula: 

``max(value + DP[i][j - weight], DP[i][j])``.

In our solution, DP table contains the values for processed points only. 

However, the case ``[j - weight]`` can give a point that does not belong to set ``W``, that means it would never contribute to the optimal solution (``Axiom 1``), and we can assign 0 value for that outsider point. 

# Three kind of knapsacks

First one is knapsack, where the item value and the item weight are the same, which is known as subset sum problem. That one and 1-0 knapsack problems are known as ``weakly NP hard`` problems in case of integer numbers.[2]

``N`` dimensional knapsack has ``N`` constrains, ``M`` items and ``M`` values, where ``Mth`` item is the vector of item dimensions of size ``N``. The multi-dimensional knapsacks are computationally harder than knapsack; even for ``D=2``, the problem does not have EPTAS unless ``P=NP``. [1]

## New subset sum knapsack algorithm

The proposed new subset sum knapsack algorithm is simpler than existing ones, as it can terminate execution once a solution equal to the knapsack size has been found. The algorithm includes several improvements aimed at reducing the speed of collection growth.

In particular, certain new points and old points at a given step may not contribute to the optimal solution. This is due to the depth of the execution tree and the growing speed of the sum starting from the current one.

To improve the algorithm, a pre-processing step is applied to determine the input characteristics such as whether the collection of items is in increasing or decreasing order, whether the given dimensions form a super-increasing set, whether all values are equal, and whether the values are equal to the first item dimension.

If the given collection is sorted, additional flags for super-increasing items and partial sums for each item are also collected.

Based on the order of the given items, three limitation factors are defined to restrict the growing collection of "w point" sets:

The first factor, ``NL`` is equal to ``C - Ith partial sum``,  where ``C`` is the size of the knapsack.
If an item is super-increasing compared to the previous one, a second factor, ``OL`` is defined as the lower bound factor, equal to ``NL + current item``.
The third factor ``PS`` is the partial sum for that item. If ``PS >= C/2`` where ``C`` is the size of the knapsack, this item itself can be skipped as we are only interested in its contribution to existing sums.
``OL`` is equal to ``NL`` if the item is not super-increasing compared to the previous one.

Considering items in non-increasing order, it can be observed that for super-increasing cases, the part of optimal solutions can be generated by ``w points`` that are greater than ``OL``. To speed up runtime, old points out of this consideration are skipped.

The ``NL`` factor allows for the omission of new points without loss of optimality.

A sliding window is defined where the optimal solution exists and all points outside this window will not contribute to the optimal solution.

It is important to note that, even if the items are partially sorted, these limitation factors will still work but may not guarantee the optimal solution for all inputs. The more ordered the given items, the more accurate the result will be. If the items are not sorted, the limitation factors ``NL``, ``OL``, and ``PS`` cannot be used to obtain an exact optima, and only distinct sums will work, resulting in an exponential growth.

This optimization can be applied in cases of subset sum knapsack with equal value knapsack items and when the value is equal to the first dimension, regardless of the number of knapsack dimensions. The main prerequisite is that the items are given in increasing or decreasing order.

## 1-0 and N dimension knapsacks

The introduction of the concept of ``w points`` allows us to extend the traditional 1-0 knapsack problem to an N-dimensional space. Each added dimension increases the memory requirements for storing the point list and map keys, as well as the computational complexity for comparing new dimensions. As a result, the performance of the N-dimensional algorithm is ``N`` times slower than that of the single-dimensional algorithm.

In addition, by using ``w points`` as keys to access the profit values in the ``DP`` table, and by storing the dimensions in the ``DP`` map, the proposed algorithm can be applied to all positive rational numbers, without the need to convert the knapsack constraints and item dimensions to integers. This solves the knapsack problem for rational numbers, which is known to be ``NP-complete``. https://en.wikipedia.org/wiki/Knapsack_problem#cite_note-Wojtczak18-12

# The Nemhauser-Ullman algorithm

The ``Nemhauser-Ullman`` (``NU``) algorithm is a method for solving the knapsack problem that computes the ``Pareto curve``, which is a set of optimal solutions for the problem, and returns the best solution from the curve. The algorithm works by creating a list of Pareto points for subsets of items, where each point is a (weight, profit) pair. 
The points are listed in increasing order of their weights. The algorithm then iteratively builds the list of Pareto points for the next subset of items by duplicating the previous list and adding the new item, then merging and removing dominated solutions. The time complexity of the algorithm is ``O(n^4)`` when profits are chosen according to a uniform distribution over ``[0,1]``, as proven by ``Rene Beier`` and ``Berthold Vocking`` [14].

One of the strengths of the ``NU`` algorithm is its ability to omit points that are dominated by other solutions, which can greatly reduce the complexity of the problem. However, if the profits are greater than or equal to the weights, the algorithm becomes exponential, similar to the traditional knapsack algorithm (``KB``).

Our implementation of the ``NU`` algorithm was inspired by ``Darius Arnold's`` code in ``Python 3`` [13]. We were able to reduce the run time complexity from ``(2^N)*((2^N) + 1)`` to ``(2^N)*log(N)`` and the space complexity from ``(2^(N+1))`` to ``2^N`` by using a linked list to store only one index per point and using binary search for next maximum profit point look-up. 
Additionally, we applied the KB distinct sum optimization to further reduce complexity in cases where many duplicated points are present.

# KB and NU analysis and comparison 

Here are the ``w point`` growing speed table on each ``Nth`` iteration. 

- ``KB sums`` is new algorithm subset sum knapsack.
- ``KB 1-0`` is new algorithm 1-0 knapsack.
- ``NU`` is Nemhauser-Ullman algorithm implementation.

The values are the same as dimensions for following cases for ``KB 1-0`` and ``NU``. 

<details>
  <summary> Iteration table #1. [1..51]. `[N=50] </summary>

|  N  | KB sums | KB iter |     |  KB 1-0 | NU iter |      |  NU sums | NU iter |
|-----|---------|---------|-----|--------------|---------|------|----------|---------|
| 0 | 0 | 100 |   | 0 | 150 |      | 1 | 4 |
| 1 | 1 | 101 |   | 1 | 151 |      | 2 | 15 |
| 2 | 2 | 103 |   | 2 | 153 |      | 3 | 34 |
| 3 | 3 | 106 |   | 3 | 156 |      | 4 | 61 |
| 4 | 3 | 109 |   | 3 | 159 |      | 5 | 97 |
| 5 | 4 | 113 |   | 4 | 163 |      | 6 | 142 |
| 6 | 3 | 116 |   | 3 | 166 |      | 7 | 197 |
| 7 | 4 | 120 |   | 4 | 170 |      | 8 | 262 |
| 8 | 3 | 123 |   | 3 | 173 |      | 9 | 337 |
| 9 | 4 | 127 |   | 4 | 177 |      | 10 | 423 |
| 10 | 3 | 130 |   | 3 | 180 |     | 11 | 520 |
| 11 | 4 | 134 |   | 4 | 184 |     | 12 | 628 |
| 12 | 3 | 137 |   | 3 | 187 |     | 13 | 748 |
| 13 | 4 | 141 |   | 4 | 191 |     | 14 | 879 |
| 14 | 3 | 144 |   | 3 | 194 |     | 15 | 1022 |
| 15 | 4 | 148 |   | 4 | 198 |     | 16 | 1177 |
| 16 | 3 | 151 |   | 3 | 201 |     | 17 | 1344 |
| 17 | 4 | 155 |   | 4 | 205 |     | 18 | 1524 |
| 18 | 3 | 158 |   | 3 | 208 |     | 19 | 1716 |
| 19 | 4 | 162 |   | 4 | 212 |     | 20 | 1920 |
| 20 | 3 | 165 |   | 3 | 215 |     | 21 | 2138 |
| 21 | 4 | 169 |   | 4 | 219 |     | 22 | 2368 |
| 22 | 3 | 172 |   | 3 | 222 |     | 23 | 2611 |
| 23 | 4 | 176 |   | 4 | 226 |     | 24 | 2867 |
| 24 | 3 | 179 |   | 3 | 229 |     | 25 | 3137 |
| 25 | 4 | 183 |   | 4 | 233 |     | 26 | 3419 |
| 26 | 3 | 186 |   | 3 | 236 |     | 27 | 3716 |
| 27 | 4 | 190 |   | 4 | 240 |     | 28 | 4025 |
| 28 | 3 | 193 |   | 3 | 243 |     | 29 | 4349 |
| 29 | 3 | 196 |   | 3 | 246 |     | 30 | 4686 |
| 30 | 3 | 199 |   | 3 | 249 |     | 31 | 5037 |
| 31 | 3 | 202 |   | 3 | 252 |     | 32 | 5402 |
| 32 | 3 | 205 |   | 3 | 255 |     | 33 | 5781 |
| 33 | 3 | 208 |   | 3 | 258 |     | 34 | 6174 |
| 34 | 3 | 211 |   | 3 | 261 |     | 35 | 6582 |
| 35 | 3 | 214 |   | 3 | 264 |     | 36 | 7003 |
| 36 | 3 | 217 |   | 3 | 267 |     | 37 | 7439 |
| 37 | 3 | 220 |   | 3 | 270 |     | 38 | 7889 |
| 38 | 3 | 223 |   | 3 | 273 |     | 39 | 8354 |
| 39 | 3 | 226 |   | 3 | 276 |     | 40 | 8834 |
| 40 | 3 | 229 |   | 3 | 279 |     | 41 | 9328 |
| 41 | 3 | 232 |   | 3 | 282 |     | 42 | 9837 |
| 42 | 3 | 235 |   | 3 | 285 |     | 43 | 10360 |
| 43 | 3 | 238 |   | 3 | 288 |     | 44 | 10898 |
| 44 | 3 | 241 |   | 3 | 291 |     | 45 | 11452 |
| 45 | 3 | 244 |   | 3 | 294 |     | 46 | 12020 |
| 46 | 3 | 247 |   | 3 | 297 |     | 47 | 12603 |
| 47 | 3 | 250 |   | 3 | 300 |     | 48 | 13201 |
| 48 | 3 | 253 |   | 3 | 303 |     | 49 | 13815 |
|    |   |     |   | 2 | 305 |     | 50 | 14444 |

</details>

Table 1 reports proof of the best case and shows that the both ``KB`` knapsack performs significantly better than ``NU``.

<details>
  <summary> Iteration table #2. Iteration table. 1 and 2 values. [N=50] </summary>

|  N  | KB sums | KB iter |     |  KB 1-0 | NU iter |      |  NU sums | NU iter |
|-----|---------|---------|-----|--------------|---------|------|----------|---------|
| 0 | 0 | 100 |    | 0 | 150 |   | 1 | 4 |
| 1 | 1 | 101 |    | 1 | 151 |   | 2 | 15 |
| 2 | 2 | 103 |    | 2 | 153 |   | 3 | 34 |
| 3 | 3 | 106 |    | 3 | 156 |   | 4 | 61 |
| 4 | 4 | 110 |    | 4 | 160 |   | 5 | 97 |
| 5 | 4 | 114 |    | 4 | 164 |   | 6 | 142 |
| 6 | 6 | 120 |    | 6 | 170 |   | 7 | 197 |
| 7 | 5 | 125 |    | 5 | 175 |   | 8 | 262 |
| 8 | 7 | 132 |    | 7 | 182 |   | 9 | 337 |
| 9 | 6 | 138 |    | 6 | 188 |   | 10 | 423 |
| 10 | 8 | 146 |    | 8 | 196 |  | 11 | 520 |
| 11 | 7 | 153 |    | 7 | 203 |  | 12 | 628 |
| 12 | 9 | 162 |    | 9 | 212 |  | 13 | 748 |
| 13 | 8 | 170 |    | 8 | 220 |  | 14 | 879 |
| 14 | 10 | 180 |   | 10 | 230   | 15 | 1022 |
| 15 | 9 | 189 |    | 9 | 239 |  | 16 | 1177 |
| 16 | 11 | 200 |   | 11 | 250   | 17 | 1344 |
| 17 | 10 | 210 |   | 10 | 260   | 18 | 1524 |
| 18 | 12 | 222 |   | 12 | 272   | 19 | 1716 |
| 19 | 11 | 233 |   | 11 | 283   | 20 | 1920 |
| 20 | 13 | 246 |   | 13 | 296   | 21 | 2138 |
| 21 | 12 | 258 |   | 12 | 308   | 22 | 2368 |
| 22 | 14 | 272 |   | 14 | 322   | 23 | 2611 |
| 23 | 13 | 285 |   | 13 | 335   | 24 | 2867 |
| 24 | 15 | 300 |   | 15 | 350   | 25 | 3137 |
| 25 | 14 | 314 |   | 14 | 364   | 26 | 3420 |
| 26 | 29 | 343 |   | 29 | 393   | 28 | 3731 |
| 27 | 27 | 370 |   | 27 | 420   | 30 | 4069 |
| 28 | 27 | 397 |   | 27 | 447   | 32 | 4435 |
| 29 | 25 | 422 |   | 25 | 472   | 34 | 4830 |
| 30 | 25 | 447 |   | 25 | 497   | 36 | 5252 |
| 31 | 23 | 470 |   | 23 | 520   | 38 | 5703 |
| 32 | 23 | 493 |   | 23 | 543   | 40 | 6184 |
| 33 | 21 | 514 |   | 21 | 564   | 42 | 6694 |
| 34 | 20 | 534 |   | 20 | 584   | 44 | 7233 |
| 35 | 19 | 553 |   | 19 | 603   | 46 | 7802 |
| 36 | 18 | 571 |   | 18 | 621   | 48 | 8401 |
| 37 | 17 | 588 |   | 17 | 638   | 50 | 9031 |
| 38 | 16 | 604 |   | 16 | 654   | 52 | 9691 |
| 39 | 15 | 619 |   | 15 | 669   | 54 | 10382 |
| 40 | 14 | 633 |   | 14 | 683   | 56 | 11104 |
| 41 | 13 | 646 |   | 13 | 696   | 58 | 11858 |
| 42 | 12 | 658 |   | 12 | 708   | 60 | 12642 |
| 43 | 11 | 669 |   | 11 | 719   | 62 | 13459 |
| 44 | 10 | 679 |   | 10 | 729   | 64 | 14307 |
| 45 | 9 | 688 |    | 9 | 738 |  | 66 | 15187 |
| 46 | 8 | 696 |    | 8 | 746 |  | 68 | 16099 |
| 47 | 7 | 703 |    | 7 | 753 |  | 70 | 17043 |
| 48 | 6 | 709 |    | 6 | 759 |  | 72 | 18020 |
|    |   |     |    | 4 | 763 |  | 74 | 19029 |

</details> 

The same results for the repeated items case.

<details>
  <summary> Iteration table #3. Iteration table for [1..50] numbers. [N=50] </summary>
  
|  N  | KB sums | KB iter |     |  KB 1-0 | NU iter |      |  NU sums | NU iter |
|-----|---------|---------|-----|--------------|---------|------|----------|---------|
| 0 | 0 | 100 |      | 0 | 150 |        | 1 | 4 |
| 1 | 1 | 101 |      | 1 | 151 |        | 2 | 16 |
| 2 | 3 | 104 |      | 3 | 154 |        | 4 | 45 |
| 3 | 7 | 111 |      | 7 | 161 |        | 7 | 103 |
| 4 | 14 | 125 |     | 14 | 175 |       | 11 | 204 |
| 5 | 25 | 150 |     | 25 | 200 |       | 16 | 364 |
| 6 | 41 | 191 |     | 41 | 241 |       | 22 | 600 |
| 7 | 63 | 254 |     | 63 | 304 |       | 29 | 931 |
| 8 | 92 | 346 |     | 92 | 396 |       | 37 | 1374 |
| 9 | 129 | 475 |    | 129 | 525 |      | 46 | 1952 |
| 10 | 173 | 648 |    | 173 | 698 |     | 56 | 2683 |
| 11 | 220 | 868 |    | 220 | 918 |     | 67 | 3589 |
| 12 | 284 | 1152 |   | 284 | 1202 |    | 79 | 4691 |
| 13 | 360 | 1512 |   | 360 | 1562 |    | 92 | 6013 |
| 14 | 418 | 1930 |   | 418 | 1980 |    | 106 | 7575 |
| 15 | 459 | 2389 |   | 459 | 2439 |    | 121 | 9403 |
| 16 | 500 | 2889 |   | 500 | 2939 |    | 137 | 11518 |
| 17 | 524 | 3413 |   | 524 | 3463 |    | 154 | 13944 |
| 18 | 547 | 3960 |   | 547 | 4010 |    | 172 | 16707 |
| 19 | 566 | 4526 |   | 566 | 4576 |    | 191 | 19830 |
| 20 | 581 | 5107 |   | 581 | 5157 |    | 211 | 23337 |
| 21 | 594 | 5701 |   | 594 | 5751 |    | 232 | 27255 |
| 22 | 605 | 6306 |   | 605 | 6356 |    | 254 | 31608 |
| 23 | 614 | 6920 |   | 614 | 6970 |    | 277 | 36423 |
| 24 | 621 | 7541 |   | 621 | 7591 |    | 301 | 41724 |
| 25 | 626 | 8167 |   | 626 | 8217 |    | 326 | 47538 |
| 26 | 629 | 8796 |   | 629 | 8846 |    | 352 | 53891 |
| 27 | 628 | 9424 |   | 628 | 9474 |    | 379 | 60810 |
| 28 | 625 | 10049 |  | 625 | 10099 |   | 407 | 68322 |
| 29 | 620 | 10669 |  | 620 | 10719 |   | 436 | 76454 |
| 30 | 613 | 11282 |  | 613 | 11332 |   | 466 | 85232 |
| 31 | 604 | 11886 |  | 604 | 11936 |   | 497 | 94684 |
| 32 | 593 | 12479 |  | 593 | 12529 |   | 529 | 104838 |
| 33 | 580 | 13059 |  | 580 | 13109 |   | 562 | 115721 |
| 34 | 565 | 13624 |  | 565 | 13674 |   | 596 | 127362 |
| 35 | 548 | 14172 |  | 548 | 14222 |   | 631 | 139788 |
| 36 | 529 | 14701 |  | 529 | 14751 |   | 667 | 153028 |
| 37 | 507 | 15208 |  | 507 | 15258 |   | 704 | 167110 |
| 38 | 484 | 15692 |  | 484 | 15742 |   | 742 | 182062 |
| 39 | 459 | 16151 |  | 459 | 16201 |   | 781 | 197914 |
| 40 | 432 | 16583 |  | 432 | 16633 |   | 821 | 214694 |
| 41 | 403 | 16986 |  | 403 | 17036 |   | 862 | 232431 |
| 42 | 372 | 17358 |  | 372 | 17408 |   | 904 | 251155 |
| 43 | 339 | 17697 |  | 339 | 17747 |   | 947 | 270894 |
| 44 | 304 | 18001 |  | 304 | 18051 |   | 991 | 291678 |
| 45 | 267 | 18268 |  | 267 | 18318 |   | 1036 | 313537 |
| 46 | 228 | 18496 |  | 228 | 18546 |   | 1082 | 336500 |
| 47 | 187 | 18683 |  | 187 | 18733 |   | 1129 | 360597 |
| 48 | 141 | 18824 |  | 141 | 18874 |   | 1177 | 385859 |
|    |     |       |  | 97 | 18971 |    | 1226 | 412314 |

</details> 

For the sake of brevity, the proof is reported in Table 3 confirms that both ``KB`` over-perform ``NU`` in increasing number set case.

<details>
  <summary> Iteration table #4. 50 random numbers in [1..1000] range, ASC</summary>
  
|  N  | KB sums | KB iter |     |  KB 1-0 | NU iter |      |  NU sums | NU iter |
|-----|---------|---------|-----|--------------|---------|------|----------|---------|
| 0 | 0 | 100 |           | 0 | 0 | 150 |          | 1 | 4 |
| 1 | 1 | 101 |           | 1 | 1 | 151 |          | 2 | 16 |
| 2 | 3 | 104 |           | 2 | 3 | 154 |          | 4 | 46 |
| 3 | 7 | 111 |           | 3 | 7 | 161 |          | 8 | 118 |
| 4 | 15 | 126 |          | 4 | 15 | 176 |         | 16 | 344 |
| 5 | 31 | 157 |          | 5 | 31 | 207 |         | 32 | 842 |
| 6 | 63 | 220 |          | 6 | 63 | 270 |         | 56 | 2044 |
| 7 | 127 | 347 |         | 7 | 127 | 397 |        | 108 | 4745 |
| 8 | 251 | 598 |         | 8 | 251 | 648 |        | 200 | 9997 |
| 9 | 485 | 1083 |        | 9 | 485 | 1133 |       | 343 | 18519 |
| 10 | 861 | 1944 |       | 10 | 861 | 1994 |      | 502 | 33097 |
| 11 | 1374 | 3318 |      | 11 | 1374 | 3368 |     | 813 | 54690 |
| 12 | 2397 | 5715 |      | 12 | 2397 | 5765 |     | 1116 | 83067 |
| 13 | 3637 | 9352 |      | 13 | 3637 | 9402 |     | 1425 | 119197 |
| 14 | 4979 | 14331 |     | 14 | 4979 | 14381 |    | 1743 | 163479 |
| 15 | 6466 | 20797 |     | 15 | 6466 | 20847 |    | 2072 | 216439 |
| 16 | 7565 | 28362 |     | 16 | 7565 | 28412 |    | 2457 | 279615 |
| 17 | 8528 | 36890 |     | 17 | 8528 | 36940 |    | 2851 | 353430 |
| 18 | 9274 | 46164 |     | 18 | 9274 | 46214 |    | 3274 | 438775 |
| 19 | 9785 | 55949 |     | 19 | 9785 | 55999 |    | 3699 | 535867 |
| 20 | 10276 | 66225 |    | 20 | 10276 | 66275 |   | 4139 | 645260 |
| 21 | 10573 | 76798 |    | 21 | 10573 | 76848 |   | 4596 | 767570 |
| 22 | 10782 | 87580 |    | 22 | 10782 | 87630 |   | 5075 | 903533 |
| 23 | 10974 | 98554 |    | 23 | 10974 | 98604 |   | 5557 | 1053363 |
| 24 | 11117 | 109671 |   | 24 | 11117 | 109721 |  | 6045 | 1217345 |
| 25 | 11216 | 120887 |   | 25 | 11216 | 120937 |  | 6534 | 1395624 |
| 26 | 11278 | 132165 |   | 26 | 11278 | 132215 |  | 7030 | 1588505 |
| 27 | 11297 | 143462 |   | 27 | 11297 | 143512 |  | 7527 | 1796118 |
| 28 | 11297 | 154759 |   | 28 | 11297 | 154809 |  | 8030 | 2018734 |
| 29 | 11233 | 165992 |   | 29 | 11233 | 166042 |  | 8538 | 2256592 |
| 30 | 11158 | 177150 |   | 30 | 11158 | 177200 |  | 9050 | 2509918 |
| 31 | 11044 | 188194 |   | 31 | 11044 | 188244 |  | 9587 | 2779553 |
| 32 | 10886 | 199080 |   | 32 | 10886 | 199130 |  | 10149 | 3066331 |
| 33 | 10713 | 209793 |   | 33 | 10713 | 209843 |  | 10720 | 3370635 |
| 34 | 10509 | 220302 |   | 34 | 10509 | 220352 |  | 11318 | 3693448 |
| 35 | 10203 | 230505 |   | 35 | 10203 | 230555 |  | 12008 | 4037636 |
| 36 | 9842 | 240347 |    | 36 | 9842 | 240397 |   | 12711 | 4403711 |
| 37 | 9411 | 249758 |    | 37 | 9411 | 249808 |   | 13422 | 4792047 |
| 38 | 8940 | 258698 |    | 38 | 8940 | 258748 |   | 14152 | 5203347 |
| 39 | 8458 | 267156 |    | 39 | 8458 | 267206 |   | 14900 | 5638353 |
| 40 | 7953 | 275109 |    | 40 | 7953 | 275159 |   | 15731 | 6099743 |
| 41 | 7380 | 282489 |    | 41 | 7380 | 282539 |   | 16576 | 6588098 |
| 42 | 6791 | 289280 |    | 42 | 6791 | 289330 |   | 17444 | 7104262 |
| 43 | 6174 | 295454 |    | 43 | 6174 | 295504 |   | 18319 | 7648595 |
| 44 | 5543 | 300997 |    | 44 | 5543 | 301047 |   | 19211 | 8221762 |
| 45 | 4885 | 305882 |    | 45 | 4885 | 305932 |   | 20115 | 8824279 |
| 46 | 4197 | 310079 |    | 46 | 4197 | 310129 |   | 21040 | 9456954 |
| 47 | 3437 | 313516 |    | 47 | 3437 | 313566 |   | 21993 | 10120802 |
| 48 | 2573 | 316089 |    | 48 | 2573 | 316139 |   | 22954 | 10816205 |
| 49 | 1714 | 317803 |    | 49 | 1714 | 317853 |   | 23924 | 11543572 |
</details> 

The difference between number of iterations reached is significant. It is shown that both ``KB`` solvers performs much faster in term of iterations and runtime.

<details>
  <summary> Iteration table #5. Random numbers in [1...10000000000000000]. [N=15] </summary>
	
|  N  | KB sums | KB iter |     |  KB 1-0 | NU iter |      |  NU sums | NU iter |
|-----|---------|---------|-----|--------------|---------|------|----------|---------|
| 0 | 0 | 30 |      | 0 | 45 |        | 1 | 4 |
| 1 | 1 | 31 |      | 1 | 46 |        | 2 | 16 |
| 2 | 3 | 34 |      | 3 | 49 |        | 4 | 46 |
| 3 | 7 | 41 |      | 7 | 56 |        | 8 | 124 |
| 4 | 15 | 56 |     | 15 | 71 |       | 16 | 342 |
| 5 | 31 | 87 |     | 31 | 102 |      | 32 | 878 |
| 6 | 60 | 147 |    | 60 | 162 |      | 64 | 2304 |
| 7 | 117 | 264 |   | 117 | 279 |     | 128 | 5838 |
| 8 | 222 | 486 |   | 222 | 501 |     | 256 | 13968 |
| 9 | 409 | 895 |   | 409 | 910 |     | 512 | 32724 |
| 10 | 713 | 1608 |  | 713 | 1623 |   | 1024 | 74854 |
| 11 | 1112 | 2720 | | 1112 | 2735 |  | 2048 | 168030 |
| 12 | 1537 | 4257 | | 1537 | 4272 |  | 4096 | 371536 |
| 13 | 1606 | 5863 | | 1606 | 5878 |  | 8192 | 810214 |
| 14 | 1380 | 7243 | | 1380 | 7258 |  | 16384 | 1749064 |
	
</details>

``NU`` shows exponential grow. ``KB`` behaves polynomial which confirms the effectives of ``LO`` limitation factor.

<details>
  <summary> Iteration table #6. Geometric progression with factor equals to 2.  [N=15 + 1]. Median item is duplicated to do not fall to superincreasing case. </summary>
	
|  N  | KB sums | KB iter |     |  KB 1-0 | NU iter |      |  NU sums | NU iter |
|-----|---------|---------|-----|--------------|---------|------|----------|---------|
| 0 | 0 | 32 |         | 0 | 0 | 48 |         | 1 | 4 |
| 1 | 1 | 33 |         | 1 | 1 | 49 |         | 2 | 16 |
| 2 | 3 | 36 |         | 2 | 3 | 52 |         | 4 | 46 |
| 3 | 7 | 43 |         | 3 | 7 | 59 |         | 8 | 118 |
| 4 | 15 | 58 |        | 4 | 15 | 74 |        | 16 | 288 |
| 5 | 31 | 89 |        | 5 | 31 | 105 |       | 32 | 684 |
| 6 | 63 | 152 |       | 6 | 63 | 168 |       | 64 | 1594 |
| 7 | 127 | 279 |      | 7 | 127 | 295 |      | 128 | 3658 |
| 8 | 255 | 534 |      | 8 | 255 | 550 |      | 256 | 8156 |
| 9 | 381 | 915 |      | 9 | 381 | 931 |      | 384 | 17734 |
| 10 | 760 | 1675 |    | 10 | 760 | 1691 |    | 768 | 36468 |
| 11 | 1508 | 3183 |   | 11 | 1508 | 3199 |   | 1536 | 74790 |
| 12 | 2968 | 6151 |   | 12 | 2968 | 6167 |   | 3072 | 155102 |
| 13 | 5744 | 11895 |  | 13 | 5744 | 11911 |  | 6144 | 325283 |
| 14 | 10720 | 22615 | | 14 | 10720 | 22631 | | 12288 | 687230 |
| 15 | 18368 | 40983 | | 15 | 18368 | 40999 | | 24576 | 1457027 |

</details>

Both ``KB`` algorithms performs better than ``NU`` does.


<details>
  <summary> Iteration table #7. Factorial numbers [numbers[i] *= (int(numbers[i - 1]) - 1)]. Random values in [1..1000] [N=15 + 1]. </summary>
	
|  N  | KB 1-0 | KB iter |     |  NU CNT | NU sums |
|-----|---------|---------|-----|---------|---------|
| 0 | 0 | 60 |           | 1 | 4 |
| 1 | 1 | 61 |           | 2 | 13 |
| 2 | 3 | 64 |           | 3 | 30 |
| 3 | 7 | 71 |           | 5 | 61 |
| 4 | 15 | 86 |          | 6 | 101 |
| 5 | 31 | 117 |         | 7 | 151 |
| 6 | 63 | 180 |         | 9 | 222 |
| 7 | 127 | 307 |        | 12 | 323 |
| 8 | 255 | 562 |        | 13 | 437 |
| 9 | 511 | 1073 |       | 16 | 584 |
| 10 | 1023 | 2096 |     | 17 | 744 |
| 11 | 2047 | 4143 |     | 19 | 932 |
| 12 | 4095 | 8238 |     | 24 | 1182 |
| 13 | 8191 | 16429 |    | 28 | 1489 |
| 14 | 16383 | 32812 |   | 36 | 1904 |
| 15 | 32767 | 65579 |   | 41 | 2392 |
| 16 | 65535 | 131114 |  | 46 | 2953 |
| 17 | 131071 | 262185 | | 51 | 3592 |
| 18 | 262143 | 524328 | | 59 | 4357 |
| 19 | 524287 | 1048615 || 68 | 5257 |
	
</details>

Above table shows exponential case for new ``KB`` algorithm. ``NU`` works as polynomial.

<details>
  <summary> Iteration table #8. Factorial numbers [9500..10000]. [N=25]. Values in [1..100000] </summary>
	
|  N  | KB 1-0 | KB iter |     |  NU | NU iter |
|-----|---------|---------|-----|---------|---------|
| 0 | 0 | 25 |          | 1 | 4 |
| 1 | 1 | 26 |          | 2 | 18 |
| 2 | 3 | 29 |          | 4 | 45 |
| 3 | 7 | 36 |          | 5 | 78 |
| 4 | 15 | 51 |         | 8 | 139 |
| 5 | 31 | 82 |         | 11 | 239 |
| 6 | 63 | 145 |        | 15 | 386 |
| 7 | 127 | 272 |       | 20 | 560 |
| 8 | 255 | 527 |       | 25 | 796 |
| 9 | 511 | 1038 |      | 29 | 1111 |
| 10 | 970 | 2008 |     | 32 | 1438 |
| 11 | 1737 | 3745 |    | 35 | 1797 |
| 12 | 2798 | 6543 |    | 39 | 2268 |
| 13 | 4341 | 10884 |   | 46 | 2891 |
| 14 | 5978 | 16862 |   | 57 | 3584 |
| 15 | 7587 | 24449 |   | 61 | 4412 |
| 16 | 9830 | 34279 |   | 67 | 5308 |
| 17 | 12305 | 46584 |  | 69 | 6152 |
| 18 | 14595 | 61179 |  | 73 | 7141 |
| 19 | 17425 | 78604 |  | 83 | 8344 |
| 20 | 19929 | 98533 |  | 92 | 9889 |
| 21 | 23927 | 122460 | | 121 | 11751 |
| 22 | 26414 | 148874 | | 130 | 13693 |
| 23 | 29959 | 178833 | | 142 | 16011 |
| 24 | 33500 | 212333 | | 157 | 18602 |	
</details>

``NU`` performance wins new ``KB`` algorithm in 2 times.

<details>
  <summary> Iteration table #9. KB subset sum knapsack solver for knapPI_16_2000_1000 dataset first 46 cases. N=2000, Max iter is 32 000 000 000. </summary>

|case|DESC time | NON time | DESC iter | NON  iter |
|----|----------|----------|-----------|-----------|
| 1  | 0.2424   | 3.3361   |  54945    | 148876    | 
| 2  | 1.6517   | 8.5564   |  91425    | 923351    |
| 3  | 2.7569   | 16.8475  |  128038   | 1702076   |
| 4  | 6.6732   | 27.5882  |  156978   | 4091615   |
| 5  | 11.6644  | 37.5579  |  183168   | 6340710   |
| 6  | 26.5512  | 49.2542  |  207443   | 14740102  |
| 7  | 28.9394  | 56.5968  |  234277   | 15870541  |
| 8  | 39.8948  | 67.7686  |  260203   | 24391156  |
| 9  | 45.8787  | 79.3859  |  282929   | 28719576  |
| 10 | 54.0926  | 94.004   |  307593   | 33701765  |
| 11 | 58.2498  | 108.8225 |  326782   | 36370599  |
| 12 | 71.8397  | 121.8941 |  352753   | 45070849  |
| 13 | 79.9757  | 143.2815 |  375038   | 49864002  |
| 14 | 95.1115  | 158.2778 |  392950   | 59586574  |
| 15 | 104.4229 | 175.7065 |  413574   | 65494253  |
| 16 | 115.1729 | 188.5035 |  432623   | 72061493  |
| 17 | 130.5489 | 205.1563 |  448467   | 81376516  |
| 18 | 146.7837 | 223.0166 |  469817   | 91673876  |
| 19 | 160.9478 | 244.5821 |  489675   | 100456993 |
| 20 | 171.4131 | 266.9605 |  511186   | 106871247 |
| 21 | 181.935  | 292.8429 |  528004   | 113334352 |
| 22 | 214.73   | 336.2358 |  546090   | 123148863 |
| 23 | 242.1276 | 354.1652 |  562431   | 137254853 |
| 24 | 248.1751 | 384.5739 |  582780   | 141525413 |
| 25 | 268.6782 | 375.8657 |  598119   | 152336246 |
| 26 | 269.373  | 398.2895 |  616681   | 165227416 |
| 27 | 281.0691 | 416.9376 |  634056   | 173225466 |
| 28 | 298.1874 | 430.437  |  650829   | 183414846 |
| 29 | 319.3805 | 472.7862 |  671667   | 199222941 |
| 30 | 332.0522 | 475.4337 |  684437   | 207509403 |
| 31 | 352.5451 | 501.6223 |  693662   | 217596170 |
| 32 | 368.8739 | 521.6603 |  716842   | 227591352 |
| 33 | 393.8193 | 544.1014 |  733624   | 242347547 |
| 34 | 426.6387 | 591.6319 |  750366   | 256815542 |
| 35 | 499.7592 | 696.0972 |  768899   | 268092391 |
| 36 | 521.1272 | 705.6635 |  773135   | 275870027 |
| 37 | 559.0725 | 748.5348 |  798349   | 292842730 |
| 38 | 567.7962 | 788.1777 |  810165   | 298058910 |
| 39 | 590.6815 | 818.0995 |  832406   | 313295674 |
| 40 | 626.8576 | 846.153  |  848798   | 329185013 |
| 41 | 656.6782 | 860.9435 |  859222   | 342417857 |
| 42 | 674.9245 | 930.0941 |  871932   | 359051526 |
| 43 | 713.3769 | 960.3015 |  887674   | 371668680 |
| 44 | 741.9356 | 1030.2002 | 907063   | 388248777 |
| 45 | 772.3906 | 1045.7318 | 916815   | 401892112 |
| 46 | 786.0283 | 1081.9096 | 931870   | 412463986 |

</details>

Here we can see that new ``KB`` algorithm can solve large instances as well.

## N dimensional KB knapsack

<details>
<summary> 2D knapsack test dataset, N = 28, integer and decimal numbers used as dimensions.</summary>

	(821, 0.8, 118), 
	(1144, 1, 322), 
	(634, 0.7, 166), 
	(701, 0.9, 195),
	(291, 0.9, 100), 
	(1702, 0.8, 142), 
	(1633, 0.7, 100), 
	(1086, 0.6, 145),
	(124, 0.6, 100), 
	(718, 0.9, 208), 
	(976, 0.6, 100), 
	(1438, 0.7, 312),
	(910, 1, 198), 
	(148, 0.7, 171), 
	(1636, 0.9, 117), 
	(237, 0.6, 100),
	(771, 0.9, 329), 
	(604, 0.6, 391), 
	(1078, 0.6, 100), 
	(640, 0.8, 120),
	(1510, 1, 188), 
	(741, 0.6, 271), 
	(1358, 0.9, 334), 
	(1682, 0.7, 153),
	(993, 0.7, 130), 
	(99, 0.7, 100), 
	(1068, 0.8, 154), 
	(1669, 1, 289)

</details>

<details>
  <summary> Iteration table #10. KB 2D dimensional knapsack. </summary>
  
|  N  | KB | KB iter |  
|-----|---------|---------|
| 0 | 0 | 56 |
| 1 | 1 | 58 |
| 2 | 3 | 66 |
| 3 | 7 | 86 |
| 4 | 15 | 130 |
| 5 | 31 | 222 |
| 6 | 63 | 410 |
| 7 | 127 | 790 |
| 8 | 255 | 1554 |
| 9 | 511 | 3086 |
| 10 | 1022 | 6150 |
| 11 | 2029 | 12220 |
| 12 | 4012 | 24240 |
| 13 | 7614 | 46894 |
| 14 | 13402 | 86828 |
| 15 | 24915 | 161432 |
| 16 | 45584 | 298108 |
| 17 | 81845 | 549430 |
| 18 | 131665 | 973058 |
| 19 | 174073 | 1541118 |
| 20 | 205927 | 2240688 |
| 21 | 245413 | 3100762 |
| 22 | 268507 | 4051662 |
| 23 | 301603 | 5138368 |
| 24 | 326110 | 6325478 |
| 25 | 351627 | 7621354 |
| 26 | 393707 | 9084722 |
| 27 | 439870 | 10727972 |
	
</details>

Result table #10 table shows that exponential grow ends at 18th element. Maximum iteration is ``2 ** N`` which is equal to 268 435 456, but actual is 10 727 972.	 

<details>
<summary> 2D knapsack counting case dataset. Second dimension is equal to 1. N=11 </summary>

[(821,  1,  821),
(1144,  1,  1144), 
(634,   1,  634), 
(701,   1, 701),
(291,   1, 291), 
(1702,  1, 1702), 
(1633,  1,  1633), 
(1086,  1,  1086),
(124,   1,  124), 
(718,   1, 718), 
(976,   1,  976), 
(1438,  1,  1438)]

</details>


<details>
  <summary> Iteration table #11. KB 2D knapsack counting case. Comparison with using and not using limit factors. </summary>

| I |no lim |iter|---| lim | iter|
|---|---|----|-------|---|----|
| 0 | 0 | 24 |       | 0 | 24 |
| 1 | 1 | 26 |       | 1 | 26 |
| 2 | 3 | 34 |       | 3 | 34 |
| 3 | 7 | 54 |       | 7 | 54 |
| 4 | 15 | 98 |      | 15 | 98 |
| 5 | 31 | 190 |     | 30 | 188 |
| 6 | 63 | 378 |     | 56 | 358 |
| 7 | 127 | 758 |    | 101 | 670 |
| 8 | 255 | 1522 |   | 175 | 1214 |
| 9 | 511 | 3054 |   | 270 | 2062 |
| 10 | 1022 | 6118 |  | 307 | 3100 |
| 11 | 2003 | 12148 | | 277 | 4026 |

</details>

On the basis of the results of Table 11, we can see that 2D dimensional knapsack can be solved in polynomial time in counting case. That case was used in new partition algorithm below.

## Performance conclusion remarks

In summary, the performance of the ``KB`` and ``NU`` algorithms for the knapsack problem can vary depending on the specific case. 
In general, the ``KB`` algorithm is faster in the worst cases of the ``NU`` algorithm, while the ``NU`` algorithm performs better in the worst cases of the ``KB`` algorithm. 
By combining these two algorithms in a hybrid ``KB-NU`` approach, it is possible to solve the unbounded 1-0 knapsack problem in polynomial time and space.

# Hybrid KB-NU knapsack

To determine which algorithm is better use, we can check input data:

- Do we have the same values.

- Is it counting case.

- Do we have full or partial super increasing weights.

After that check, we call super increasing solver, ``kb limit`` or ``pareto`` solver depends on data given. 

Please refer to  ``./cpp/knapsack/knapsack_solver.hpp`` or ``./python/knapsackNd.py``.

The cpp ``kb limit`` solver has an alternative DP implementation. It doesn't use dynamic programming procedure implemented in python. Instead of using map data structure, while generating combinations of new points, new solver is keeping track of maximum profit point, building backtrace table ``./cpp/source_link.hpp``, and filtering out old and new points using limits described in this study. 

It leads to unifying the backtrace procedure for ``pareto`` and ``kb limit`` solvers ``./cpp/tools.hpp``, and simplifying preparing search index we use in a greedy algorithm described below.

# Greedy N independent dimension knapsack algorithm

The "abstract M independent dimension knapsack" problem presents a challenge for traditional Pareto-based solutions, as it is not possible to sort items in a meaningful way. However, an exact solution can still be obtained through the use of the classic "KB" knapsack algorithm, although this approach is computationally expensive, with a time complexity of ``O(2^N)`` due to the need to check all possible combinations of items.

A new, greedy approach can provide an efficient, albeit suboptimal, solution. By breaking down the problem into ``M`` independent dimensions and using the Pareto solver on each of these dimensions, it is possible to reduce the ``N`` in the ``2^N`` expression. This can be done by repeatedly calling the Pareto solver while decreasing the constraint on the Mth dimension and combining the resulting items before calling the KB limit solver on the reduced set of items.

This approach is safe, as each greedy step reduces the size of the problem from the top constraint value by subtracting the minimal ``M``th dimension value. Additionally, by building an index on the first step of solving the single dimension problem, the next call for the decreased Mth dimension constraint can be done in O(logN) time. The main complexity driver in this algorithm is not the actual ``N``, but the given constraint. If its value includes a large proportion of the ``N`` items, the algorithm will still take an exponential amount of time.

Overall, this algorithm can be useful in practical situations where computational resources are limited and a large number of ``N ``items need to be considered.

Please take a look at ``./cpp/knapsack/knapsack_greedy_top_down_solver.hpp`` or ``./python/greedyNdKnapsack.py``.

# New equal subset sum algorithm

The Equal-Subset-Sum problem is a computer science problem that involves determining whether a given set of numbers, ``S``, can be divided into two disjoint subsets, ``A`` and ``B``, such that the sum of the elements in each subset is the same. This problem is ``NP-complete`` and the state-of-the-art algorithm runs in ``O(1.7088 ** N)`` worst case [16].

The new ``KB`` partition algorithm is designed to provide the best possible partitions of a set of numbers, ``S``, into ``M`` subsets with equal sums. The algorithm utilizes a knapsack solution to solve the ``M`` equal subset sum problem, which has a worst-case time complexity of exponential in ``M``, and an average case time complexity of ``O((M ^ 3) * (W))``, where ``W`` is the complexity of the knapsack grouping operator.

The algorithm starts by considering the input numbers as a sequence to be divided into ``M`` groups with equal sums. The knapsack solver is used as a grouping operator to find the first group that meets the sum and group count constraints. This process is repeated ``M`` times, and if an empty reminder is obtained at the end, then the problem is considered solved.

For cases where duplicates exist in the input set, the algorithm spreads non-distinct numbers into pseudo descending clusters, where each 3rd cluster is in descending order. This heuristic has been found to provide good partitions in tests with a success rate of 99%.

If a non-empty reminder is obtained, the algorithm attempts to optimize its size to ``0`` by unioning its numbers with other partition points and calling the knapsack solver on the unioned set. The algorithm loops over the partition points and increases the limit of simultaneous partition optimizations, with the number of iterations determined by the iterator counter ``H``. Once half of ``H`` partition combinations have been visited, the algorithm is considered to have reached an optimal solution.

The overall time complexity of the algorithm is ``O(2 ^ (M / 2) * (W))``, where ``M`` is the number of partitions and ``W`` is the complexity of the knapsack grouping operator. The same approach can also be used to solve the strict ``3-partition`` problem, which is ``NP-complete`` in the strong sense. This is achieved by using a counting knapsack case with two constraints as the grouping operator, and applying modifications to the algorithm to avoid falling into local maxima, such as shuffling the reminder set before unioning with partition points, and shuffling new quotients after each optimization iteration.

# New partition algorithm performance

Below table was generated using integer partition test. It is trimmed version to show how the iteration grow speed depends on partition and set size. The full file generated by the script ``knapsack.py``.

Max iterations calculates by following expression: 

``([P ** 3) * ((N /P) ** 4)``. where ``N`` is items number, ``P`` is number of partitions.

Optimization column is the number of new quotients generated during the reminder optimization.  

<details>
  <summary> Partition iteration table 3 </summary>
	
| item | integer | generator limit | partitions |     N         |  optimizations  |  iterations    |  max iterations |
|------|---------|-----------------|------------|---------------|-----------------|----------------|-----------------|
|1|54|20|20|63|0|1 633|648000|
|1|54|50|50|201|0|10 711|32000000|
|1|54|100|100|462|0|46 059|256000000|
|1|41|200|200|1 047|10|224 717|5000000000|
|1|54|200|200|1 047|0|189 199|5000000000|
|1|33|300|300|1 648|12|526 629|16875000000|
|1|30|500|500|2 996|22|2 195 567|78125000000|
|1|34|1 000|1 000|6 658|0|5 490 387|1296000000000|
|1|36|1 000|1 000|6 658|28|8 170 674|1296000000000|
|1|38|2 000|2 000|14 546|0|23 408 940|19208000000000|
|1|39|2 000|2 000|14 546|32|31 673 026|19208000000000|
|1|41|2 000|2 000|14 546|38|39 922 774|19208000000000|
|1|42|2 000|2 000|14 546|37|32 511 092|19208000000000|
|1|44|2 000|2 000|14 546|35|368 387 227|19208000000000|
|1|47|2 000|2 000|14 546|41|36 358 893|19208000000000|
|1|53|2 000|2 000|14 546|26|26 244 633|19208000000000|
|1|38|3 000|3 000|23 032|0|53 197 483|64827000000000|
|1|45|3 000|3 000|23 005|81|1 659 905 427|64827000000000|
|1|46|4 000|4 000|31 775|83|153 045 373|153664000000000|
|1|49|5 000|5 000|40 791|112|552 311 469|512000000000000|

| item | integer | generator limit | partitions |     N      |  optimizations  |  iterations  |  max iterations |
|------|---------|-----------------|------------|------------|-----------------|--------------|-----------------|
|1|54|10 000|10 000|88 258|260|1 994 693 179|51200000000|

</details>

Using test iterations and optimization reports we can have 3 cases:

1. No optimization performed. This means that first heuristics sorting and single knapsack grouping solved the case. 
2. Single optimization layer. That means that first groping gives almost optimal solution, and we optimized reminder by visiting quotients without mixing it with each other.
3. Up to 4 optimization layers. First heuristics gave bad grouping. We had to regenerate old quotients by mixing it with each other to get up to 4 partitions in the optimize group.

# Results validation

The subset sum and 1-0 knapsack algorithms were evaluated using the hardinstances_pisinger integer numbers test dataset [9], and they produced accurate results that were consistent with the expected ones [4]. These algorithms were also tested using rational numbers as input weights and constraints, using the same dataset. Each weight was divided by 100,000, and the results were found to be accurate and comparable to those obtained with integer numbers.

The ``N-dimensional knapsack`` algorithm was compared to the classic 2-dimensional dynamic programming solution (DPS) for integer values, and it was found to produce equivalent results. Additionally, it was tested using rational numbers on a one-dimensional dataset, and as the grouping operator in a strict ``T-group`` ``M-partition`` solution (tests were conducted for T=3 and T=6).

The ``M equal subset sum`` algorithm was evaluated using the Leetcode test dataset (https://leetcode.com/problems/partition-to-k-equal-sum-subsets/) and test cases generated by an integer partition generator, with up to 102,549 items in the set and up to 10,000 partitions. It was also tested using rational numbers. The algorithm performed well in 95% of cases, but in worst-case scenarios with a high number of duplicates in the input set, 1-2 optimization iterations were required on average, with up to 5 iterations needed in some cases. The more duplicate numbers in the input set, the more optimization iterations were required.

Several knapsack and integer optimization tests were also conducted. The optimization iteration counter did not exceed the maximum value established in advance.

The complete list of tests:

- Rational numbers tests for equal-subset-sum knapsack, 1-0 knapsack, and N dimension knapsacks, where N 2-4.
- Super-increasing integer tests for equal-subset-sum knapsack, 1-0 knapsack, and N dimension knapsacks, where N = 2.
- Partial super-increasing numbers tests.
- Partial geometric progression numbers tests.
- 2D knapsack matching with classic DP solution results.
- Integer and Decimal mixed multidimensional knapsack problem (MKP) test
- N equal-subset-sum tests.
- Multiple knapsack sizes integer tests.
- Strict 3 and 6 partition problem tests.
- 1-0 knapsack for Silvano Martello and Paolo Toth 1990 tests.
- Equal-subset-sum knapsack for hardinstances_pisinger subset sum test dataset.
- 1-0 knapsack for hardinstances_pisinger test dataset in case of integer and rational numbers.
- N equal-subset-sum using integer partition generator.
- Integer partition optimization tests. randomTestCount * 200
- Multidimensional  N=100 non exact greedy algorithm test
- Building max profit point index for kb and pareto solvers.

c++ tests:

- Rational numbers tests for equal-subset-sum knapsack, 1-0 knapsack.
- Super-increasing integer tests for equal-subset-sum knapsack, 1-0 knapsack, and N dimension knapsacks, where N = 2.
- Partial super-increasing numbers tests.
- 1-0 knapsack for Silvano Martello and Paolo Toth 1990 tests.
- Equal-subset-sum knapsack for hardinstances_pisinger subset sum test dataset.
- 1-0 knapsack for hardinstances_pisinger test dataset.
- Multidimensional  N=100 non exact greedy algorithm test
- Counting 2 dimensional case.
- Building max profit point index for kb and pareto solvers.

# References

- [1] https://en.wikipedia.org/wiki/Knapsack_problem
- [2] https://en.wikipedia.org/wiki/Weak_NP-completeness
- [3] https://en.wikipedia.org/wiki/Strong_NP-completeness
- [4] Where are the hard knapsack problems? By David Pisinger. May 2004
- [5] The Bounded Knapsack Problem with Setups by Haldun Süral, Luk Van Wassenhove, Chris N. Potts, Jan 1999
- [6] Martello S, Toth P. Upper bounds and algorithms for hard 0–1 knapsack problems.
- [7] https://en.wikipedia.org/wiki/Multiway_number_partitioning
- [8] https://en.wikipedia.org/wiki/3-partition_problem
- [9] http://hjemmesider.diku.dk/~pisinger/codes.html
- [10] https://en.wikipedia.org/wiki/Superincreasing_sequence
- [11] http://www.cs.cmu.edu/~anupamg/advalgos15/lectures/lecture29.pdf
- [12] http://www.roeglin.org/teaching/Skripte/ProbabilisticAnalysis.pdf
- [13] https://github.com/dariusarnold/knapsack-problem
- [14] An Experimental Study of Random Knapsack Problems. By Rene Beier1 and Berthold Vocking2
- [15] R. Bellman, Notes on the theory of dynamic programming iv - maximization over discrete sets, Naval. Research Logistics Quarterly, 3 (1-2), 67-70, 1956.
- [16] Equal-Subset-Sum Faster Than the Meet-in-the-Middle. Marcin Mucha, Jesper Nederlof, Jakub Pawlewicz, Karol Węgrzycki. 3 Jul 2019. https://arxiv.org/abs/1905.02424

# Roadmap

The API of this library is frozen.

Bug fixes and performance enhancement can be expected.

New functionality might be included.

Version numbers adhere to semantic versioning: https://semver.org/

The only accepted reason to modify the API of this package is to handle issues that can't be resolved in any other reasonable way.

## How to cite ##

	@unpublished{knapsack,
	    author = {Konstantin Briukhnov (@ConstaBru)},
	    title = {Rethinking the knapsack and set partitions},
	    year = 2020,
	    note = {Available at \url{https://github.com/CostaBru/knapsack}},
	    url = {https://github.com/CostaBru/knapsack}
	}

## License

[MIT](https://choosealicense.com/licenses/mit/)
