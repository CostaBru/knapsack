# Rethinking the knapsack and set partitions

This work contains the list of algorithms, performance analysis and reports:

- An exponental algorithm that has the polynominal time\space runtime for unbounded 1-0 knapsack problem. The comparison of the Nemhauser-Ullmann Algorithm [12] with that one.

- An exponental algorithm for abstract up to ``T`` dimensions unbounded 1-0 knapsack problem.

- ``M`` equal-subset-sum of ``N`` integer number set that is exponental in ``M`` only.

- Algorithm for multiple knapsack and ``M`` strict partition problem.

- Test cases and iteration reports.

# Abstract

The knapsack problem is well known and described in many articles and books. 

The classical knapsack problem is defined as follows: 

We are given a set of ``N`` items, each item ``J`` having a ``Pj`` value and a weight ``Wj`` . The problem is to choose a subset of the
items such that their overall profit is maximized, while the overall weight does not exceed a given capacity ``C`` [6].

Let's consider classical bottom-up dynamic programing solution for unbounded knapsack problem. Let's call it ``DPS``. Bounded version of that problem has known way of reduction to unbounded one [5].

It uses recurrent formula to calculate maximum value going through item weights array and checks every weight possible, using DP table from 1 to size of knapsack. 
``DPS`` algorithm is very efficient on small numbers. It has a known limitation to use only positive integers as input. Time and memory Complexity is ``O(N * M)`` which is known as pseudopolynomial.

During solving the equal subset sum problem [7] using knapsack, I noticed that ``DPS`` did extra work by considering possibilities those never would be a part of the optimal solution.

Classic ``DPS`` works in integer set ``1..S`` integer numbers, where ``S`` is size of knapsack. [1] 

But the optimal solution can be only in subset ``W``, where ``W`` contains items and sums of all items that less than the size of knapsack. (``Axiom 1``)

When weight considered is not a part of sum of items then classic ``DPS`` algorithm compares and copies maximum value reached to next DP table cell. 

# The main idea

Due to ``Axiom 1``, let's consider only weights and sums of weights. We will perform the DP algorithm over that collection for each item. 

Let's call the sum of weight visited with current weight a ``w point``. We are going to generate the set of ``w points`` for each knapsack item. We will provide the current weight and sum of current item weight with all visited points before. And use DP recurrent formula for that new set. 

That growing collection gives as next recurrent expression for inner loop for ``Nth`` iteration:

``[ Wi + ((Wi + Wi-1) + (Wi + Wi-2) + ... + (Wi + Wi-n)) ]``, 

where ``W`` is the weight, and ``I`` is the index in collection of given items. At each ``N`` iteration we have expected maximum numbers of item weights we need to visit to reach optimal solution. 

The recurrent formula for that collection is ``(2 ** N) - 1``. Which is exponental in ``N``. That exponent is limited by ``C`` the size of knapsack.

The main driver of that exponental growth is the count of new distinct sums generated after each iteration of ``Nth`` item. Because the patrition function of each existing sum grows as an exponential function of the square root of its argument, the probabilty of new sum generated be an unuque falls down dramatically when count of sums grows up. 

On the othen hand, each new dimension added to the knapsack problem decreases the limitiation effect. 

The best case for knapsack is all duplicate weights in given set. The compexity is ``O(N)`` in that case. Superincreasing sequence of weights [10] can be solved in ``O(N LogN)``. The worst case for the algorithm is considering as much possible of unique weights as possible. We can state that the superincreasing set of prime numbers is the worst case, where each sums for previous ``N`` numbers grater than next ``N item`` in the ordered set.  

As soon we are not going to visit all weights possible from 1 to knapsack size, but only sums and weights itself, we should keep track of maximum weight and value we have archived for each point visited. When we processed all items points or found optimal solution earlier (in case of item weight is equal item value) we can backtrace items using DP table in the same way as in ``DPS``. 

Instead of array of array as DP table, we are going to use array of map to keep ``O(1)`` access time for points that belong to ``W`` set, and to check whether new sum is distinct.
The map key is point visited, the map value is accumulated weight and value for that key.
We are going to process points in ASC order. We will merge two sorted list into single one in ``O(N + M)``, where ``N`` previous point count, ``M`` is new points created. Hence the previous list has been ordered already and the new one we get from previous list using current weight addition. 

Classic ``DPS`` uses recurrent formula: 

``max(value + DP[i][j - weight], DP[i][j])``.

In our solution DP table contains values for processed points only. 
The case ``[j - weight]`` can give a point that does not belong to set ``W``, that means that point would never contribute to the optimal solution (``Axiom 1``), and we can assign 0 value for outsider point. 

# Three kind of problem

We are going to investigate three kinds of knapsack problems.
First one is knapsack where the item value and the item weight are the same which is known as subset sum problem. It and 1-0 knapsack problems are known as ``weakly NP hard`` problems in case of integer numbers.[2]

``N`` dimensional knapsack has ``N`` constrains, ``M`` items and ``M`` values, where ``Mth`` item is the vector of item dimensions of size ``N``. The multi-dimensional knapsacks are computationally harder than knapsack; even for ``D=2``, the problem does not have EPTAS unless ``P=NP``. [1]

## Subset sum knapsack

It is simpler than others, because we can terminate execution once we have found a solution equal to knapsack size. 
We are going to use this property in ``M`` equal-subset-sum problem. Here we can reduce the point collection growing speed, because some new points created will not contribute to the optimal solution. The reason of it is the depth of execution tree and growing speed of the sum starting from current one. 


Let's call a partial sum is the number we get for some ``Ith`` element from maximum item to current item. Here we expect knapsack items in DESC order, so the highest and the first ``Nth`` partial sum is going to be equal ``Nth`` weight, for ``Nth + 1`` it is equal to ``[ S(N - 1) = S(N) +  Ith weight]`` and so on. 

We are going to use that partial sum and the knowledge of desc iteration flow to skip new points from growing collection.
We use partial sum to decide to do we need add this weight or just use created new points. In addition, we could skip new sum point if that sum is less then knapsack size minus partial sum. (``Lemma 1``) 

That optimization can be used in case of subset sum knapsack, or equal values knapsacks no metter of it dimension count.

## 1-0 and N dimension knapsacks

They are required to visit all dimension sums and cannot skip any of them in case of non equal profits. We use dimensions as ``W points`` and accumulate profit\weight\volume reached for that ``W point`` using the same DP recurrent formula. 
Each new dimension requires more memory for storing that dimension in point list and in DP table map keys collection, and we need to compare more numbers as well. 

Once we get rid of integer indexes in the DP table, using a ``w point`` as key to access the profit value, and dimensions in DP map, we can use described algorithms for ``all positive rational numbers`` without converting knapsack constrains and item dimensions given to integers.

Above solutions solve the knapsack problems which are strongly ``NP-complete`` if the weights and profits are given as rational numbers. https://en.wikipedia.org/wiki/Knapsack_problem#cite_note-Wojtczak18-12

### Axiom 1

The optimal solution could be found in set of all sums of items weights only. It is self-evident, because the optimal solution contains given items only.

### Teor 1

The dynamic programing recurrent formula ``max(DP[i], DP[i - w] + v)`` works for set of sums. Prof: Because the set ``W`` is existing in set ``S``, where set ``W`` are the items and sums, where set ``S`` are numbers starting 1 up to knapsack size,
then ``DPS`` recurrent formula ``max(DP[i], DP[i - w] + v)`` works for ``W`` points as well. if ``[i - w]`` is not the sum of items it will not be in optimal solution anyway due to ``Axiom 1``, and we consider 0 value for that point-outsider.

### Lemma 1 for subset sum knapsack: 

If current ``partial sum`` is less than size of ``knapsack // 2`` then that item itself cannot be a first item of optimal solution. 
It may be a part of solution, so we can consider only distinct previous points sums with this item. 

### Lemma 2 for subset sum knapsack or equal profits case:

We can consider the starting way of each point and the full way from that point to knapsack size as part of other sums.
The ``W point`` cannot reach the size of knapsack as part of sums of next algorithm iterations and will not contribute to optimal solution if it less than ``knapsack size`` minus ``partial sum`` for current item.  

# Nemhauser-Ullman

The Nemhauser-Ullman algorithm [12] for the knapsack problem computes the Pareto curve and returns the best solution from the curve.

For now, github has two implementations of this algorithm. One of them which is written by ``Darius Arnold`` in python3, was included in knapsack.py with paretoKnapsack method. The code was modifeid a little bit to count interations and some corner cases patches applied to make it works on test dataset. 

Please see and star https://github.com/dariusarnold/knapsack-problem repository.

# Analysis

Here are the ``w point`` growing speed table on each ``Nth`` iteration where ``N=100`` and the ``C`` is sum of all minus two. 

- ``N`` is iteration number, 
- P1 is the case of the same value. Total sum is 100, ``C`` is 98.
- I1 total iteration to that ``N`` for P1
- P2 is the case where two different values and its duplicates.  Total sum is 150, ``C ``is 148.
- I2 total iteration to that ``N`` for P2
- P3 the integet numbers from 1 to 101. Total sum is 5050, ``C`` is 5048.
- I3 total iteration to that ``N`` for P3
- P4 random numbers in 1-1000 range.  Total sum is 51280, ``C`` is 51278.
- I4 total iteration to that ``N ``for P4

<details>
  <summary> Iteration table 1 </summary>


|  N  | P1  |  I1   |  |  P2  |  I2  |  |  P3 |    I3    |  |  P4 |    I4    |
|-----|-----|-------|--|------|------|--|-----|----------|--|-----|----------|
| 2 | 1 |101 ||  1 |101 ||   1 |101 ||1 |101 |
| 3 | 2 |103 ||  2 |103 ||   3 |104 ||2 |103 |
| 4 | 3 |106 ||  3 |106 ||   7 |111 ||3 |106 |
| 5 | 4 |110 ||  4 |110 ||   14 |125 ||6 |112 |
| 6 | 4 |114 ||  5 |115 ||   25 |150 ||7 |119 |
| 7 | 5 |119 ||  5 |120 ||   41 |191 ||8 |127 |
| 8 | 5 |124 ||  7 |127 ||   63 |254 ||12 |139 |
| 9 | 6 |130 ||  6 |133 ||   92 |346 ||14 |153 |
| 10 | 6 |136 ||  8 |141 ||   129 |475 || 22 |175 |
| 11 | 7 |143 ||  8 |149 ||   175 |650 || 32 |207 |
| 12 | 7 |150 ||  10 |159 ||  231 |881 || 46 |253 |
| 13 | 8 |158 ||  9 |168 ||   298 |1179 || 60 |313 |
| 14 | 8 |166 ||  11 |179 ||  377 |1556 || 86 |399 |
| 15 | 9 |175 ||  11 |190 ||  468 |2024 || 125 |524 |


|  N  | P1  |  I1   |  |  P2  |  I2  |  |  P3 |    I3    |  |  P4 |    I4    |
|-----|-----|-------|--|------|------|--|-----|----------|--|-----|----------|
| 16 | 9 |184 ||  13 |203 ||  560 |2584 || 162 |686 |
| 17 | 10 |194 || 12 |215 ||  678 |3262 || 229 |915 |
| 18 | 10 |204 || 14 |229 ||  812 |4074 || 315 |1230 |
| 19 | 11 |215 || 14 |243 ||  963 |5037 || 492 |1722 |
| 20 | 11 |226 || 16 |259 ||  1131 |6168 || 537 |2259 |
| 21 | 12 |238 || 15 |274 ||  1257 |7425 || 680 |2939 |
| 22 | 12 |250 || 17 |291 ||  1366 |8791 || 589 |3528 |
| 23 | 13 |263 || 17 |308 ||  1477 |10268 || 910 |4438 |
| 24 | 13 |276 || 19 |327 ||  1575 |11843 || 979 |5417 |
| 25 | 14 |290 || 18 |345 ||  1650 |13493 || 715 |6132 |
| 26 | 14 |304 || 20 |365 ||  1714 |15207 || 1008 |7140 |
| 27 | 15 |319 || 20 |385 ||  1796 |17003 || 1221 |8361 |
| 28 | 15 |334 || 22 |407 ||  1855 |18858 || 1170 |9531 |
| 29 | 16 |350 || 21 |428 ||  1911 |20769 || 1379 |10910 |
| 30 | 16 |366 || 23 |451 ||  1962 |22731 || 1093 |12003 |


|  N  | P1  |  I1   |  |  P2  |  I2  |  |  P3 |    I3    |  |  P4 |    I4    |
|-----|-----|-------|--|------|------|--|-----|----------|--|-----|----------|
| 31 | 17 |383 || 23 |474 ||  2010 |24741 || 747 |12750 |
| 32 | 17 |400 || 25 |499 ||  2056 |26797 || 1247 |13997 |
| 33 | 18 |418 || 24 |523 ||  2101 |28898 || 925 |14922 |
| 34 | 18 |436 || 26 |549 ||  2143 |31041 || 1182 |16104 |
| 35 | 19 |455 || 26 |575 ||  2184 |33225 || 1425 |17529 |
| 36 | 19 |474 || 28 |603 ||  2223 |35448 || 1521 |19050 |
| 37 | 20 |494 || 27 |630 ||  2257 |37705 || 1982 |21032 |
| 38 | 20 |514 || 29 |659 ||  2289 |39994 || 1756 |22788 |
| 39 | 21 |535 || 29 |688 ||  2318 |42312 || 2265 |25053 |
| 40 | 21 |556 || 31 |719 ||  2346 |44658 || 1866 |26919 |
| 41 | 22 |578 || 30 |749 ||  2372 |47030 || 2163 |29082 |
| 42 | 22 |600 || 32 |781 ||  2395 |49425 || 2204 |31286 |
| 43 | 23 |623 || 32 |813 ||  2417 |51842 || 1863 |33149 |
| 44 | 23 |646 || 34 |847 ||  2437 |54279 || 2215 |35364 |
| 45 | 24 |670 || 33 |880 ||  2455 |56734 || 2297 |37661 


|  N  | P1  |  I1   |  |  P2  |  I2  |  |  P3 |    I3    |  |  P4 |    I4    |
|-----|-----|-------|--|------|------|--|-----|----------|--|-----|----------|
| 46 | 24 |694 || 35 |915 ||  2470 |59204 || 1742 |39403 |
| 47 | 25 |719 || 35 |950 ||  2484 |61688 || 2048 |41451 |
| 48 | 25 |744 || 37 |987 ||  2496 |64184 || 2690 |44141 |
| 49 | 26 |770 || 36 |1023 || 2506 |66690 || 3257 |47398 |
| 50 | 26 |796 || 38 |1061 || 2514 |69204 || 2594 |49992 |
| 51 | 27 |823 || 38 |1099 || 2520 |71724 || 2792 |52784 |
| 52 | 27 |850 || 66 |1165 || 2524 |74248 || 2793 |55577 |
| 53 | 28 |878 || 65 |1230 || 2524 |76772 || 2597 |58174 |
| 54 | 4 |882 ||  65 |1295 || 2522 |79294 || 3269 |61443 |
| 55 | 4 |886 ||  64 |1359 || 2518 |81812 || 2711 |64154 |
| 56 | 4 |890 ||  64 |1423 || 2512 |84324 || 2119 |66273 |
| 57 | 4 |894 ||  63 |1486 || 2504 |86828 || 1824 |68097 |
| 58 | 4 |898 ||  63 |1549 || 2494 |89322 || 2421 |70518 |
| 59 | 4 |902 ||  62 |1611 || 2482 |91804 || 2339 |72857 |
| 60 | 4 |906 ||  62 |1673 || 2468 |94272 || 1988 |74845 |


|  N  | P1  |  I1   |  |  P2  |  I2  |  |  P3 |    I3    |  |  P4 |    I4    |
|-----|-----|-------|--|------|------|--|-----|----------|--|-----|----------|
| 61 | 4 |910 ||  61 |1734 || 2452 |96724 || 2396 |77241 |
| 62 | 4 |914 ||  61 |1795 || 2434 |99158 || 2363 |79604 |
| 63 | 4 |918 ||  60 |1855 || 2414 |101572 || 2067 |81671 |
| 64 | 4 |922 ||  60 |1915 || 2392 |103964 || 2517 |84188 |
| 65 | 4 |926 ||  59 |1974 || 2368 |106332 || 2006 |86194 |
| 66 | 4 |930 ||  40 |2014 || 2342 |108674 || 2273 |88467 |
| 67 | 4 |934 ||  39 |2053 || 2314 |110988 || 1808 |90275 |
| 68 | 4 |938 ||  38 |2091 || 2284 |113272 || 1811 |92086 |
| 69 | 4 |942 ||  37 |2128 || 2252 |115524 || 1703 |93789 |
| 70 | 4 |946 ||  36 |2164 || 2218 |117742 || 1042 |94831 |
| 71 | 4 |950 ||  35 |2199 || 2182 |119924 || 1905 |96736 |
| 72 | 4 |954 ||  34 |2233 || 2144 |122068 || 1144 |97880 |
| 73 | 4 |958 ||  33 |2266 || 2063 |124131 || 1524 |99404 |
| 74 | 4 |962 ||  32 |2298 || 2020 |126151 || 1844 |101248 |
| 75 | 4 |966 ||  31 |2329 || 1975 |128126 || 1619 |102867 |


|  N  | P1  |  I1   |  |  P2  |  I2  |  |  P3 |    I3    |  |  P4 |    I4    |
|-----|-----|-------|--|------|------|--|-----|----------|--|-----|----------|
| 76 | 4 |970 ||  30 |2359 || 1928 |130054 || 1749 |104616 |
| 77 | 4 |974 ||  29 |2388 || 1879 |131933 || 1581 |106197 |
| 78 | 4 |978 ||  28 |2416 || 1828 |133761 || 1142 |107339 |
| 79 | 4 |982 ||             1775 |135536 || 1709 |109048 |
| 80 | 4 |986 ||  26 |2469 || 1720 |137256 || 1823 |110871 |
| 81 | 4 |990 ||  25 |2494 || 1663 |138919 || 1159 |112030 |
| 82 | 4 |994 ||  24 |2518 || 1604 |140523 || 1325 |113355 |
| 83 | 4 |998 ||  23 |2541 || 1543 |142066 || 1404 |114759 |
| 84 | 4 |1002 ||            1480 |143546 || 1808 |116567 |
| 85 | 4 |1006 || 21 |2584 || 1415 |144961 || 1168 |117735 |
| 86 | 4 |1010 || 20 |2604 || 1348 |146309 || 1583 |119318 |

|  N  | P1  |  I1   |  |  P2  |  I2  |  |  P3 |    I3    |  |  P4 |    I4    |
|-----|-----|-------|--|------|------|--|-----|----------|--|-----|----------|
| 87 | 4 |1014 || 19 |2623 || 1279 |147588 || 1030 |120348 |
| 88 | 4 |1018 || 18 |2641 || 1208 |148796 || 1283 |121631 |
| 89 | 4 |1022 || 17 |2658 || 1135 |149931 || 910 |122541 |
| 90 | 4 |1026 || 16 |2674 || 1060 |150991 || 1301 |123842 |
| 91 | 4 |1030 || 15 |2689 || 983 |151974 || 1544 |125386 |
| 92 | 4 |1034 || 14 |2703 || 904 |152878 || 1412 |126798 |
| 93 | 4 |1038 || 13 |2716 || 823 |153701 || 1266 |128064 |
| 94 | 4 |1042 || 12 |2728 || 740 |154441 || 851 |128915 |
| 95 | 4 |1046 || 11 |2739 || 655 |155096 || 439 |129354 |
| 96 | 4 |1050 || 10 |2749 || 568 |155664 || 242 |129596 |
| 97 | 4 |1054 || 9 |2758 ||  479 |156143 || 242 |129838 |
| 98 | 4 |1058 || 8 |2766 ||  388 |156531 || 242 |130080 |

</details>

The following table shows the worst case described above. The almost superincreasing prime numbers sequence and random numbers.

P1 is prime numbers:

 ``[3, 5, 17, 31, 41, 59, 67, 83, 109, 211, 353, 709, 1409, 1471, 4349, 7517, 17509, 82339, 539111, 965801, 9121667, 36068261, 95937757, 99491389, 99942569111] ``

P2 is random numbers 3 up to 99,942,569,111. Total sum is 1,127,081,334,901. C is 1,127,081,334,899

<details>
  <summary> Iteration table 2 </summary>
	
|  N  | P1  | 2**(N-1)-P1 |  I1  |      | P2  |  2**(N-1)-P2 |    I2    |
|-----|-----|-------------|------|------|-----|--------------|----------|
| 2 | 1 | 1 | 26 || 1 | 1 | 26 |
| 3 | 3 | 1 | 29 || 3 | 1 | 29 |
|   |   |   |   || 7 | 1 | 36 |
| 5 | 15 | 1 | 51 || 15 | 1 | 51 |
| 6 | 31 | 1 | 82 || 31 | 1 |82 |
| 7 | 63 | 1 | 145 || 63 | 1 |145 |
| 8 | 121 | 7 | 266 || 127 | 1 |272 |
| 9 | 242 | 14 | 508 || 252 | 4 |524 |
| 10 | 479 | 33 | 987 ||  500 | 12 |1024 |
| 11 | 942 | 82 | 1929 || 999 | 25 |2023 |
| 12 | 1868 | 180 | 3797 || 1989 | 59 |4012 |
| 13 | 3660 | 436 | 7457 || 3954 | 142 |7966 |

|  N  | P1  | 2**(N-1)-P1 |  I1  |      | P2  |  2**(N-1)-P2 |    I2    |
|-----|-----|-------------|------|------|-----|--------------|----------|
| 14 | 7130 | 1062 | 14587 || 7842 | 350 |15808 |
| 15 | 13776 | 2608 | 28363 || 15463 | 921 |31271 |
| 16 | 26359 | 6409 | 54722 ||  30257 | 2511 |61528 |
| 17 | 48779 | 16757 | 103501 || 58490 | 7046 |120018 |
| 18 | 85416 | 45656 | 188917 || 111122 | 19950 |231140 |
| 19 | 141023 | 121121 | 329940 || 200639 | 61505 |431779 |
| 20 | 172070 | 352218 | 502010 || 339778 | 184510 |771557 |
| 21 | 215806 | 832770 | 717816 || 405214 | 643362 |1176771 |
| 22 | 201721 | 1895431 | 919537 || 443753 | 1653399 |1620524 |
| 23 | 147191 | 4047113 | 1066728 || 352107 | 3842197 |1972631 |
| 24 | 75252 | 8313356 | 1141980 ||  188760 | 8199848 |2161391 |
| 25 | 16816 | 16760400 | 1158796 || 44523 | 16732693 |2205914 |
	
</details>

Looking at the table we can see negative trend of growing speed in last 1/4. 

The total iterations count for random case is 1,220,500. For primes case, it is 21,696,675. 

Those numbers confim worst case statement. The max exponental iteration count is 33,554,432 for ``N``=25. 

# Equal subset sum algorithm

Equal subsetsum is only ``weakly NP-hard`` - it is hard only when the numbers are encoded in non-unary system, and have value exponential in ``N``.
When the values are polynomial in ``N``, Partition can be solved in polynomial time using the pseudopolynomial time number partitioning algorithm.

We are going to use new knapsack solution to solve ``M`` equal subsetsum problem which is the exponental in ``M`` only. 


Let's consider ``N`` input numbers as sequence we should divide into ``M`` groups with equal sums. Let's denote a knapsack solver be a grouping operator that returns first group that met sum and group count contrains. To solve that problem we need to run that grouping operations ``M`` times. If we get an empty ``reminder`` at the end then the problem is solved. 


The knapsack solver over distinct desc sorted numbers divides the set into ``M`` partitions if and only if that ``M`` partitions are exist. We can consider sums like a hashing. Hence each unique number leave a unique trace in the point sums, and we know that knapsack search terminates execution once the size of knapsack has reached. Then we can backtrace those unique numbers and remove it from the input set and perform knapsack again and again until the set is not empty. If it is an empty that means we found the solution.

For case where duplicates are exist in the input set we will spread non distinct numbers into the pseudo descending cluster where each 3rd cluster is in descending order. That is a good heuristics that gives 99% good partitions in tests provided. 

If ``reminder`` is not empty then we need to optimize its size to 0. 

At this point we have the ``quotients`` and ``reminder``; quotients are ``M`` groups, ``reminder`` has ``T`` numbers. 

Let's call an exisiting group a ``partion point``. It contains the number of partition, the set of numbers, and the indexes of quotient item. We will define addition operation for the ``partion point``. It unions both groups given, preserves quotient indexes and adds group partitions. 

We sorts ``quotient`` groups by its length in descending order of ``N`` way partition problem case. It is more likly that group that have more items combined with ``reminder`` can be splited into new groups by knapsack solver.

So far, we have a collection of ``partition points`` and the ``reminder`` partition point. To optimize ``reminder`` we need to union its number set with other ``partition`` points and theirs sums and call knapsack solver for it. 

We are going to loop over the partition points and increase the limit of same time partition optimization. So the limit is going to be an iterator counter ``H``. After all point processed for current ``H``, we check the ``reminder`` lenght. If the length is decreased we set up new ``quotients`` and new ``reminder`` for next ``H`` loop interation. Once ``half of H`` partiton combinations visited we have an optimal solution.

So far the algorithm complexity of equal subset sum problem is ``2 ** ( M / 2) * ((N / M) ** 3)``.

We can use the same approach to solve the ``strict 3(T) partition`` problem as well. That problem is ``NP complete`` in strong sense. https://en.wikipedia.org/wiki/3-partition_problem#cite_note-3. 

We will use knapsack with ``2 constrains`` as a grouping operator. The second constrain is group size which is equal to``3(T)``. We apply two modifications to our algorithm to do not allow fall into local maximum. We add shuffling ``reminder`` set before union with partition point and shuffling new ``quotients`` we got after each optimization iteration. 

# Partition performance

Below table was generated using integer partition test. It is trimmed version to show how the iteration grow speed depends on partition and set size. The full file generated by the script ``knapsack.py``.

Max iterations calculates by following expression: 

``(len(partition) ** 3) * ((N /partition) ** 4)``. 

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
2. Single optimization layer. That means that first groping gives almost optimal solution, and we optimized reminder by visiting quotiens without mixing it with each other.
3. Up to 4 optimiaztion layers. First heuristics gave bad grouping. We had to regenerate old quotiens by mixing it with each other to get up to 4 partitions in the optimize group.

# Results validation

The subset sum and 1-0 knapsack algorithms were tested on hardinstances_pisinger integer numbers test dataset [9] and gave accurate results that were equal to expected ones [4]. Those algorithms were tested on rational numbers as input weights and constrains using the same dataset. Each weight was divided by 100 000. It also gives accurate result the same as for integer numbers.

``N`` dimension knapsack was tested along with classic 2 dimensional ``DPS`` solver on integer values. It also was tested using rational numbers on one dimension dataset, and as the grouping operator in strict ``T group M partition`` solution (tests provided for ``T=3`` and ``T=6``).

M equal subset sum algorithm was tested by Leetcode test dataset https://leetcode.com/problems/partition-to-k-equal-sum-subsets/, and by testcases created by integer partition generator up to 102 549 items in the set and up to 10 000 partitions, and by rational numbers tests as well. First time heuristics made, works fine in 95% percent cases; for worst case where a lot of duplicates are present in given set the algorithm needs 1-2 optimizations in average and up to 5 optimization iterations for some cases. As much duplicate numbers in the input set as much optimization iterations required. 

Mulitple knapsack and integer optimization tests were performed as well. Optimization iteration counter didn't exceed the declareted maximum.

# Implementations and usage

The single ``knapsack.py`` script has all described alogrithms, tests, and performance report generators. It is copy\paste friendly without 3d party dependencies. To run all knapsack tests, please, download test cases from [9], and copy those files to /hardinstances_pisinger directory. 

There are 4 python methods to use:
- partitionN, which gets number set to partition, partitions number or list of particular sizes of each partition, strict partition group size, and the iterator counter array.
- knapsack1d (subset sum), which used in partitionN as set grouping operator. It requires the following parameters: size of knapsack, items, iterator counter array, and flag indicating whether items are sorted in desc order. 
- knapsack2d (1-0 knapsack), gets size of knapsack, items, values, iterator counter array. 
- knapsackNd, expects the single tuple as size constrains of knapsack, items as tuples of dimensions, values, iterator counter array. It is used in partitionN method in the strict group size case.
- parettoKnapsack is slighly modified copy of the Nemhauser-Ullman algorithm implementation by ``Darius Arnold``.

# Conclusion

Classic ``DPS`` algorithm for 1-0 unbounded knapsack problem was extended to work with rational numbers, and to has any independend dimensions. The algorithm for equal subset problem complexity was improved to be exponental in number of partitions only.

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
