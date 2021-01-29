# Rethinking the knapsack and set partitions. (Not released yet).

The classic dynamic programing algorithm for 1-0 unbounded knapsack problem was extended to work with rational numbers, and to has any number of independent dimensions. 

New knapsack algorithms were tested on the open source test datasets, and as a core part of equal subset problem algorithm. 

The algorithm for equal subset problem complexity was improved to be exponential in number of partitions only. The integer input type limitation was removed. That new algorithm was tested on integer partition generator data, and on integer optimization tests.

This work contains the source code of new ``KB`` knapsack and partition algorithms, performance analysis and reports:

- The polynomial algorithm for unbounded 1-0 knapsack problem. The comparison of the Nemhauser-Ullmann ``NU`` Algorithm [12] with that one.

- The exponential algorithm for abstract up to ``T`` dimensions unbounded 1-0 knapsack problem that performs as polynomial in most cases.

- The ``M`` equal-subset-sum of ``N`` integer number set that is exponential in ``M`` only.

- The algorithms for multiple knapsack and ``M`` strict partition problems. The run time complexity is exponential in number of partition, too. 

- Test cases and iteration reports.

# Abstract

The knapsack problem is defined as follows: 

We are given a set of ``N`` items, each item ``J`` having a ``Pj`` value and a weight ``Wj`` . The problem is to choose a subset of the
items such that their overall profit is maximized, while the overall weight does not exceed a given capacity ``C`` [6].

Let's consider classical bottom-up dynamic programing solution for unbounded knapsack problem. Let's call it ``DPS``. 

Bounded version of that problem has known way of reduction to unbounded one [5].

It uses recurrent formula to calculate maximum value going through item weights array and checks every weight possible, using DP table from 1 to size of knapsack. 
``DPS`` algorithm is very efficient on small numbers. It has a known limitation to use only positive integers as input. Time and memory Complexity is ``O(N * M)`` which is known as pseudopolynomial.

During solving the equal subset sum problem [7] using knapsack, I noticed that ``DPS`` did extra work by considering possibilities those never would be a part of the optimal solution.

Classic ``DPS`` works in integer set ``1..S`` integer numbers, where ``S`` is size of knapsack. [1]

But the optimal solution can be only in subset ``W``, where ``W`` contains items and sums of all items that less than the size of knapsack. 

When weight considered is not a part of sum of items then classic ``DPS`` algorithm compares and copies maximum value reached to next DP table cell. 

# The main idea of KB knapsack algorithm

### Axiom 1

The optimal solution could be found in set of all sums of items weights only. It is self-evident, because the optimal solution contains given items only. 

Due to ``Axiom 1``, let's consider only weights and sums of weights. We will perform the DP algorithm over that collection for each item. 

Let's call the sum of weight visited with current weight a ``w point``. We are going to generate the set of ``w points`` for each knapsack item. 

We will provide the current weight and sum of current item weight with all visited points before. Then, use DP recurrent formula for that new set. 

That growing collection gives as next recurrent expression for inner loop for ``Nth`` iteration:

``[ Wi + ((Wi + Wi-1) + (Wi + Wi-2) + ... + (Wi + Wi-n)) ]``, 

where ``W`` is the weight, and ``I`` is the index in collection of given items. At each ``N`` iteration we have expected maximum numbers of item weights we need to visit to reach optimal solution. 

The recurrent formula for that collection is ``(2 ** N) - 1``. Which is exponential in ``N``. That exponent is limited by ``C`` the size of knapsack.

The main driver of that exponential growth is the count of new distinct sums generated after each iteration of ``Nth`` item. 

Because the partition function of each existing sum grows as an exponential function of the square root of its argument, the probability of new sum generated be an unique falls down dramatically when count of sums grows up. This limitation function is non linear and it is the subject for further work.

In case of ``T`` dimensional knapsack, each new dimension added decreases this limitation effect. 

The best case for knapsack is all duplicate weights in given set. The complexity is ``O(N**2)``,  in that case. 

Super-increasing sequence of weights [10] can be solved in ``O(N LogN)``.

<details>
  <summary> Super-increasing sequence definition </summary>

Number sequence is called super-increasing if every element of the sequence is greater than the sum of all previous elements in the sequence.

</details>

The worst case for the algorithm is considering as much possible of unique weights as possible. We can state that the almost super-increasing set is the worst case, where each sums for previous ``N`` numbers minus one is equal to next ``N item`` in the ordered set.  

``DPS`` algorithm accumulates the result in ``[N x C]`` DP table, where ``C`` is size of knapsack. This new algorithm are not going to visit all weights possible from 1 to ``C``, but only sums and weights itself. To gather the result from DP table, we should keep track of maximum weight and value, we have archived for each ``w point`` visited. When all ``w points`` have processed, or we found optimal solution earlier (in case of item weight is equal item value) we can backtrace items using DP table in the same way as in ``DPS``. 

Instead of array of array as DP table, we are going to use array of map to keep ``O(1)`` access time for points that belong to ``W`` set, and to check whether new sum is distinct. The map key is ``w point``, the map value is accumulated weight (dimension) and value.
We are going to process ``w points`` in ASC order. We will merge two sorted list into single one in ``O(N + M)``, where ``N`` previous point count, ``M`` is count of new points created. Hence the previous list has been ordered already, and the new one we get from previous list using current weight (dimension) addition. 

Classic ``DPS`` uses recurrent formula: 

``max(value + DP[i][j - weight], DP[i][j])``.

In our solution DP table contains values for processed points only. 

The case ``[j - weight]`` can give a point that does not belong to set ``W``, that means it would never contribute to the optimal solution (``Axiom 1``), and we can assign 0 value for that outsider point. 

# Three kind of problem

First one is knapsack where the item value and the item weight are the same, which is known as subset sum problem. That one and 1-0 knapsack problems are known as ``weakly NP hard`` problems in case of integer numbers.[2]

``N`` dimensional knapsack has ``N`` constrains, ``M`` items and ``M`` values, where ``Mth`` item is the vector of item dimensions of size ``N``. The multi-dimensional knapsacks are computationally harder than knapsack; even for ``D=2``, the problem does not have EPTAS unless ``P=NP``. [1]

## New subset sum knapsack algorithm

It is simpler than others, because we can terminate execution once we have found a solution equal to knapsack size. Here we can reduce the ``w point`` collection growing speed, because some new points created will not contribute to the optimal solution. The reason of it is the depth of execution tree and growing speed of the sum starting from current one. 

Let's denote ``partial sum`` is the number we get for some ``Ith`` element from maximum item to current item. 

If our new algorithm gets items given in DESC then the highest and the first ``Nth`` partial sum is going to be equal ``Nth`` weight (dimension), for ``Nth + 1`` it is equal to ``[ S(N - 1) = S(N) +  Ith weight]`` and so on. of

ASC order items will reverse partial sums array. 

We spend a single iteration through ``M`` items to know:
- the order of collection, 
- given dimensions is super-increasing set or not,
- values are equal in case of MKS,
- values are equal to first item dimension in case of MKS.

If given collection is sorted we also collect:
- the flags for super-increasing items,
- partial sums for each item.

In case of sorted items we can define three limitation factors for growing collection of ``w point``. 

- First one is ``NL``, is equal to ``C - Ith partial sum``, where ``C`` is size of knapsack. 
- If item is super-increasing to previous one we will define ``OL`` lower bound factor. In case of DESC order it will be equal to ``C - previous item`` else if the order is ASC then ``NL - next item''. 
- Third factor is ``PS`` which is partial sum for that item. If ``PS >= C/2`` where C is size of knapsack, then this item itself can be skipped. We are interested in contribution of this item to existing sums. 

``OL`` is equal to ``NL`` if item is not super-increasing to previous one. All new generated points those less than ``NL`` will be skipped. All previous point those less than ``OL`` will be skipped as well. 

Having those factors, we will define the sliding window where optimal solution is exist. All points that are out of our window will not contribute to optimal solution. 

When items are non sorted we cannot use ``NL``, ``OL``, and ``PS`` limitation factors. Only distinct sums will work in that case and will give exponential grow up to ``M/2`` where M is items count.

That optimization can be used in case of subset sum knapsack, equal values knapsacks, and when value is equal to first dimension, no matter of knapsack dimension count. The main prerequisite is DESC or ASC order of items given.

## 1-0 and N dimension knapsacks

Here we accumulate profit\dimension sum reached for each ``W point`` using the same DP recurrent formula. 

Each new dimension requires more memory for storing it in point list and in DP table map keys collection. We also need to compare more numbers. 

Once we get rid of integer indexes in the DP table, using a ``w point`` as key to access the profit value, and dimensions in DP map, we can use described algorithms for ``all positive rational numbers`` without converting knapsack constrains and item dimensions given to integers.

Above solutions solve the knapsack problems which are strongly ``NP-complete`` if the weights and profits are given as rational numbers. https://en.wikipedia.org/wiki/Knapsack_problem#cite_note-Wojtczak18-12

# The Nemhauser-Ullman algorithm

The Nemhauser-Ullman algorithm [12] for the knapsack problem computes the Pareto curve and returns the best solution from the curve.

For now, the GitHub has two implementations of this algorithm. One of them which is written by ``Darius Arnold`` in python3, was included in knapsack.py with paretoKnapsack method. The code was modifeid a little bit to count interations and some corner cases patches applied to make it works on test dataset. 

Please see and star https://github.com/dariusarnold/knapsack-problem repository.

# Analysis and comparison

Here are the ``w point`` growing speed table on each ``Nth`` iteration. 

- ``KB`` is new algorithm.
- ``NU`` is Nemhauser-Ullman algorithm.

Larger profit point search complexity for NU was considered as ``Log2N``, but was implemented by ``Darius Arnold`` in ``N``.

<details>
  <summary> Iteration table ASC. 1..50. ``N``=50 </summary>

|  N  | KB sums | KB iter |     |  NU sums | NU iter |
|-----|---------|---------|-----|----------|---------|
| 2 | 1 | 51 |     | 2 | 15 |
| 3 | 2 | 53 |     | 3 | 34 |
| 4 | 3 | 56 |     | 4 | 61 |
| 5 | 3 | 59 |     | 5 | 97 |
| 6 | 4 | 63 |     | 6 | 142 |
| 7 | 3 | 66 |     | 7 | 197 |
| 8 | 4 | 70 |     | 8 | 262 |
| 9 | 3 | 73 |     | 9 | 337 |
| 10 | 4 | 77 |    | 10 | 423 |
| 11 | 3 | 80 |    | 11 | 520 |
| 12 | 4 | 84 |    | 12 | 628 |
| 13 | 3 | 87 |    | 13 | 748 |
| 14 | 4 | 91 |    | 14 | 879 |
| 15 | 3 | 94 |    | 15 | 1022 |
| 16 | 4 | 98 |    | 16 | 1177 |
| 17 | 3 | 101 |   | 17 | 1344 |
| 18 | 4 | 105 |   | 18 | 1524 |
| 19 | 3 | 108 |   | 19 | 1716 |
| 20 | 4 | 112 |   | 20 | 1920 |
| 21 | 3 | 115 |   | 21 | 2138 |
| 22 | 4 | 119 |   | 22 | 2368 |
| 23 | 3 | 122 |   | 23 | 2611 |
| 24 | 4 | 126 |   | 24 | 2867 |
| 25 | 3 | 129 |   | 25 | 3137 |
| 26 | 4 | 133 |   | 26 | 3419 |
| 27 | 3 | 136 |   | 27 | 3716 |
| 28 | 4 | 140 |   | 28 | 4025 |
| 29 | 3 | 143 |   | 29 | 4349 |
| 30 | 3 | 146 |   | 30 | 4686 |
| 31 | 3 | 149 |   | 31 | 5037 |
| 32 | 3 | 152 |   | 32 | 5402 |
| 33 | 3 | 155 |   | 33 | 5781 |
| 34 | 3 | 158 |   | 34 | 6174 |
| 35 | 3 | 161 |   | 35 | 6582 |
| 36 | 3 | 164 |   | 36 | 7003 |
| 37 | 3 | 167 |   | 37 | 7439 |
| 38 | 3 | 170 |   | 38 | 7889 |
| 39 | 3 | 173 |   | 39 | 8354 |
| 40 | 3 | 176 |   | 40 | 8834 |
| 41 | 3 | 179 |   | 41 | 9328 |
| 42 | 3 | 182 |   | 42 | 9837 |
| 43 | 3 | 185 |   | 43 | 10360 |
| 44 | 3 | 188 |   | 44 | 10898 |
| 45 | 3 | 191 |   | 45 | 11452 |
| 46 | 3 | 194 |   | 46 | 12020 |
| 47 | 3 | 197 |   | 47 | 12603 |
| 48 | 3 | 200 |   | 48 | 13201 |
| 49 | 3 | 203 |   | 49 | 13815 |

</details>

<details>
  <summary> Iteration table ASC. Iteration table. 1 and 2 values. ``N``=50 </summary>

|  N  | KB sums | KB iter |     |  NU CNT | NU sums |
|-----|---------|---------|-----|---------|---------|
| 2 | 1 | 51 |    | 2 | 15 | 
| 3 | 2 | 53 |    | 3 | 34 |
| 4 | 3 | 56 |    | 4 | 61 |
| 5 | 3 | 59 |    | 5 | 97 |
| 6 | 4 | 63 |    | 6 | 142 |
| 7 | 3 | 66 |    | 7 | 197 |
| 8 | 4 | 70 |    | 8 | 262 |
| 9 | 3 | 73 |    | 9 | 337 |
| 10 | 4 | 77 |   | 10 | 423 |
| 11 | 3 | 80 |   | 11 | 520 |
| 12 | 4 | 84 |   | 12 | 628 |
| 13 | 3 | 87 |   | 13 | 748 |
| 14 | 4 | 91 |   | 14 | 879 |
| 15 | 3 | 94 |   | 15 | 1022 |
| 16 | 4 | 98 |   | 16 | 1177 |
| 17 | 3 | 101 |  | 17 | 1344 |
| 18 | 4 | 105 |  | 18 | 1524 |
| 19 | 3 | 108 |  | 19 | 1716 |
| 20 | 4 | 112 |  | 20 | 1920 |
| 21 | 3 | 115 |  | 21 | 2138 |
| 22 | 4 | 119 |  | 22 | 2368 |
| 23 | 3 | 122 |  | 23 | 2611 |
| 24 | 4 | 126 |  | 24 | 2867 |
| 25 | 3 | 129 |  | 25 | 3137 |
| 26 | 4 | 133 |  | 26 | 3420 |
| 27 | 5 | 138 |  | 28 | 3731 |
| 28 | 4 | 142 |  | 30 | 4069 |
| 29 | 5 | 147 |  | 32 | 4435 |
| 30 | 4 | 151 |  | 34 | 4830 |
| 31 | 5 | 156 |  | 36 | 5252 |
| 32 | 4 | 160 |  | 38 | 5703 |
| 33 | 5 | 165 |  | 40 | 6184 |
| 34 | 4 | 169 |  | 42 | 6694 |
| 35 | 4 | 173 |  | 44 | 7233 |
| 36 | 4 | 177 |  | 46 | 7802 |
| 37 | 4 | 181 |  | 48 | 8401 |
| 38 | 4 | 185 |  | 50 | 9031 |
| 39 | 4 | 189 |  | 52 | 9691 |
| 40 | 4 | 193 |  | 54 | 10382 |
| 41 | 4 | 197 |  | 56 | 11104 |
| 42 | 4 | 201 |  | 58 | 11858 |
| 43 | 4 | 205 |  | 60 | 12642 |
| 44 | 4 | 209 |  | 62 | 13459 |
| 45 | 4 | 213 |  | 64 | 14307 |
| 46 | 4 | 217 |  | 66 | 15187 |
| 47 | 4 | 221 |  | 68 | 16099 |
| 48 | 4 | 225 |  | 70 | 17043 |
| 49 | 4 | 229 |  | 72 | 18020 |
| 50 | 6 | 235 |  | 74 | 19029 |

</details> 

<details>
  <summary> Iteration table ASC. Iteration table ``1..50`` numbers. ``N``=50 </summary>
  
|  N  | KB sums | KB iter |     |  NU CNT | NU sums |
|-----|---------|---------|-----|---------|---------|
| 2 | 1 | 51 |      | 2 | 16 |
| 3 | 3 | 54 |      | 4 | 45 |
| 4 | 5 | 59 |      | 7 | 103 |
| 5 | 6 | 65 |      | 11 | 204 |
| 6 | 7 | 72 |      | 16 | 364 |
| 7 | 9 | 81 |      | 22 | 600 |
| 8 | 10 | 91 |     | 29 | 931 |
| 9 | 11 | 102 |    | 37 | 1374 |
| 10 | 12 | 114 |   | 46 | 1952 |
| 11 | 13 | 127 |   | 56 | 2683 |
| 12 | 14 | 141 |   | 67 | 3589 |
| 13 | 15 | 156 |   | 79 | 4691 |
| 14 | 16 | 172 |   | 92 | 6013 |
| 15 | 17 | 189 |   | 106 | 7575 |
| 16 | 18 | 207 |   | 121 | 9403 |
| 17 | 19 | 226 |   | 137 | 11518 |
| 18 | 20 | 246 |   | 154 | 13944 |
| 19 | 21 | 267 |   | 172 | 16707 |
| 20 | 22 | 289 |   | 191 | 19830 |
| 21 | 23 | 312 |   | 211 | 23337 |
| 22 | 24 | 336 |   | 232 | 27255 |
| 23 | 25 | 361 |   | 254 | 31608 |
| 24 | 26 | 387 |   | 277 | 36423 |
| 25 | 27 | 414 |   | 301 | 41724 |
| 26 | 28 | 442 |   | 326 | 47538 |
| 27 | 29 | 471 |   | 352 | 53891 |
| 28 | 30 | 501 |   | 379 | 60810 |
| 29 | 31 | 532 |   | 407 | 68322 |
| 30 | 32 | 564 |   | 436 | 76454 |
| 31 | 33 | 597 |   | 466 | 85232 |
| 32 | 34 | 631 |   | 497 | 94684 |
| 33 | 35 | 666 |   | 529 | 104838 |
| 34 | 36 | 702 |   | 562 | 115721 |
| 35 | 37 | 739 |   | 596 | 127362 |
| 36 | 38 | 777 |   | 631 | 139788 |
| 37 | 39 | 816 |   | 667 | 153028 |
| 38 | 39 | 855 |   | 704 | 167110 |
| 39 | 40 | 895 |   | 742 | 182062 |
| 40 | 41 | 936 |   | 781 | 197914 |
| 41 | 42 | 978 |   | 821 | 214694 |
| 42 | 43 | 1021 |  | 862 | 232431 |
| 43 | 44 | 1065 |  | 904 | 251155 |
| 44 | 45 | 1110 |  | 947 | 270894 |
| 45 | 46 | 1156 |  | 991 | 291678 |
| 46 | 47 | 1203 |  | 1036 | 313537 |
| 47 | 48 | 1251 |  | 1082 | 336500 |
| 48 | 49 | 1300 |  | 1129 | 360597 |
| 49 | 97 | 1397 |  | 1177 | 385859 |
| 50 | 101 | 1498 | | 1226 | 412314 |

</details> 

<details>
  <summary> Iteration table ASC. 50 random numbers in ``1..1000`` range</summary>
  
|  N  | KB sums | KB iter |     |  NU CNT | NU sums |
|-----|---------|---------|-----|---------|---------|
| 2 | 1 | 51 |        | 2 | 16 |
| 3 | 3 | 54 |        | 4 | 46 |
| 4 | 6 | 60 |        | 8 | 118 |
| 5 | 9 | 69 |        | 16 | 344 |
| 6 | 12 | 81 |       | 32 | 818 |
| 7 | 15 | 96 |       | 52 | 1850 |
| 8 | 17 | 113 |      | 95 | 3680 |
| 9 | 19 | 132 |      | 146 | 6587 |
| 10 | 21 | 153 |     | 216 | 11094 |
| 11 | 23 | 176 |     | 302 | 17300 |
| 12 | 25 | 201 |     | 454 | 26757 |
| 13 | 27 | 228 |     | 610 | 39694 |
| 14 | 29 | 257 |     | 777 | 56475 |
| 15 | 31 | 288 |     | 956 | 77475 |
| 16 | 32 | 320 |     | 1137 | 102836 |
| 17 | 34 | 354 |     | 1321 | 132710 |
| 18 | 36 | 390 |     | 1507 | 167234 |
| 19 | 38 | 428 |     | 1709 | 206916 |
| 20 | 40 | 468 |     | 1965 | 253170 |
| 21 | 42 | 510 |     | 2228 | 306296 |
| 22 | 44 | 554 |     | 2521 | 367216 |
| 23 | 46 | 600 |     | 2883 | 437820 |
| 24 | 48 | 648 |     | 3251 | 518396 |
| 25 | 50 | 698 |     | 3620 | 609105 |
| 26 | 52 | 750 |     | 4006 | 710525 |
| 27 | 54 | 804 |     | 4406 | 823192 |
| 28 | 56 | 860 |     | 4856 | 948602 |
| 29 | 58 | 918 |     | 5328 | 1087498 |
| 30 | 60 | 978 |     | 5815 | 1240434 |
| 31 | 62 | 1040 |    | 6319 | 1408007 |
| 32 | 64 | 1104 |    | 6824 | 1590404 |
| 33 | 66 | 1170 |    | 7371 | 1788939 |
| 34 | 68 | 1238 |    | 7925 | 2003957 |
| 35 | 70 | 1308 |    | 8507 | 2236471 |
| 36 | 72 | 1380 |    | 9176 | 2489157 |
| 37 | 74 | 1454 |    | 9868 | 2762836 |
| 38 | 76 | 1530 |    | 10561 | 3057678 |
| 39 | 77 | 1607 |    | 11258 | 3373956 |
| 40 | 79 | 1686 |    | 11975 | 3712497 |
| 41 | 81 | 1767 |    | 12797 | 4076608 |
| 42 | 83 | 1850 |    | 13635 | 4466931 |
| 43 | 85 | 1935 |    | 14475 | 4883688 |
| 44 | 87 | 2022 |    | 15330 | 5327508 |
| 45 | 89 | 2111 |    | 16213 | 5799407 |
| 46 | 90 | 2201 |    | 17109 | 6299950 |
| 47 | 180 | 2381 |   | 18029 | 6830026 |
| 48 | 186 | 2567 |   | 18956 | 7390007 |
| 49 | 192 | 2759 |   | 19900 | 7980581 |
| 50 | 198 | 2957 |   | 20867 | 8602626 |
</details> 


<details>
  <summary> Iteration table ASC. Random numbers in ``1...10000000000000000``. ``N``=15 </summary>
	
|  N  | KB sums | KB iter |     |  NU CNT | NU sums |
|-----|---------|---------|-----|---------|---------|
| 2 | 1 | 16 |     | 2 | 16 |
| 3 | 3 | 19 |     | 4 | 46 |
| 4 | 5 | 24 |     | 8 | 136 |
| 5 | 7 | 31 |     | 16 | 370 |
| 6 | 8 | 39 |     | 32 | 996 |
| 7 | 9 | 48 |     | 64 | 2470 |
| 8 | 10 | 58 |    | 128 | 5906 |
| 9 | 11 | 69 |    | 256 | 13940 |
| 10 | 12 | 81 |   | 512 | 32606 |
| 11 | 13 | 94 |   | 1024 | 74236 |
| 12 | 14 | 108 |  | 2048 | 166774 |
| 13 | 14 | 122 |  | 4096 | 369728 |
| 14 | 28 | 150 |  | 8192 | 809992 |
| 15 | 32 | 182 |  | 16384 | 1757942 |
	
</details>

<details>
  <summary> Iteration table DESC. Geometric progression with factor equal 2.  ``N``=15 + 1. Last item is middle duplicated. </summary>
	
|  N  | KB sums | KB iter |     |  NU CNT | NU sums |
|-----|---------|---------|-----|---------|---------|
| 2 | 1 | 17 |      | 2 | 16 |
| 3 | 3 | 20 |      | 4 | 46 |
| 4 | 5 | 25 |      | 8 | 118 |
| 5 | 7 | 32 |      | 16 | 288 |
| 6 | 9 | 41 |      | 32 | 684 |
| 7 | 11 | 52 |     | 64 | 1594 |
| 8 | 13 | 65 |     | 128 | 3658 |
| 9 | 15 | 80 |     | 256 | 8156 |
| 10 | 29 | 109 |   | 384 | 17734 |
| 11 | 59 | 168 |   | 768 | 36468 |
| 12 | 118 | 286 |  | 1536 | 74790 |
| 13 | 236 | 522 |  | 3072 | 155102 |
| 14 | 472 | 994 |  | 6144 | 325283 |
| 15 | 944 | 1938 | | 12288 | 687230 |
| 16 | 1888 | 3826 || 24576 | 1457027 |

</details>

<details>
  <summary> Iteration table DESC. Factorial numbers ``numbers[i] *= (int(numbers[i - 1]) - 1)``. ``N``=15 + 1. Last item is middle duplicated. </summary>
	
|  N  | KB sums | KB iter |     |  NU CNT | NU sums |
|-----|---------|---------|-----|---------|---------|
| 2 | 1 | 17 |    | 2 | 18 |
| 3 | 3 | 20 |    | 4 | 60 |
| 4 | 5 | 25 |    | 8 | 167 |
| 5 | 7 | 32 |    | 15 | 433 |
| 6 | 9 | 41 |    | 30 | 886 |
| 7 | 11 | 52 |   | 68 | 1680 |
| 8 | 13 | 65 |   | 122 | 2858 |
| 9 | 27 | 92 |   | 192 | 4458 |
| 10 | 14 | 106 | | 278 | 6650 |
| 11 | 15 | 121 | | 388 | 9496 |
| 12 | 15 | 136 | | 522 | 13049 |
| 13 | 15 | 151 | | 680 | 17198 |
| 14 | 15 | 166 | | 854 | 21800 |
| 15 | 15 | 181 | | 1036 | 27023 |
| 16 | 15 | 196 | | 1234 | 32889 |
	
</details>

<details>
  <summary> Iteration table ASC. Factorial numbers ``numbers[i] *= (int(numbers[i - 1]) - 1)``.  ``N``=15 + 1. Last item is middle duplicated. </summary>
	
|  N  | KB sums | KB iter |     |  NU CNT | NU sums |
|-----|---------|---------|-----|---------|---------|
| 2 | 1 | 17 |         | 2 | 16 |
| 3 | 3 | 20 |         | 4 | 46 |
| 4 | 7 | 27 |         | 8 | 118 |
| 5 | 15 | 42 |        | 16 | 288 |
| 6 | 31 | 73 |        | 32 | 640 |
| 7 | 63 | 136 |       | 60 | 1239 |
| 8 | 127 | 263 |      | 101 | 2114 |
| 9 | 129 | 392 |      | 154 | 3241 |
| 10 | 257 | 649 |     | 166 | 4605 |
| 11 | 515 | 1164 |    | 241 | 6480 |
| 12 | 1031 | 2195 |   | 337 | 8935 |
| 13 | 2063 | 4258 |   | 455 | 11985 |
| 14 | 4127 | 8385 |   | 593 | 15628 |
| 15 | 8255 | 16640 |  | 749 | 19835 |
| 16 | 16511 | 33151 | | 920 | 24542 |
	
</details>

Looking at the last table we can see exponential grow for KB knapsack in case of factorial numbers and ASC order. 

That exponential grow rate is subject for further investigation and improvement. 

Those results shows that new KB knapsack algorithm performs much faster than NU and can accurate solve large number problems.

# New equal subset sum algorithm

Equal subset sum is only ``weakly NP-hard`` - it is hard only when the numbers are encoded in non-unary system, and have value exponential in ``N``.
When the values are polynomial in ``N``, Partition can be solved in polynomial time using the pseudo-polynomial time number partitioning algorithm.

We are going to use new knapsack solution to solve ``M`` equal subset sum problem which is the exponential in ``M`` only. 

Let's consider ``N`` input numbers as sequence we should divide into ``M`` groups with equal sums. Let's denote a knapsack solver be a grouping operator that returns first group that met sum and group count contrains. To solve that problem we need to run that grouping operations ``M`` times. If we get an empty ``reminder`` at the end then the problem is solved. 

The knapsack solver over distinct desc sorted numbers divides the set into ``M`` partitions if and only if that ``M`` partitions are exist. We can consider sums like a hashing. Hence each unique number leave a unique trace in the point sums, and we know that knapsack search terminates execution once the size of knapsack has reached. Then we can backtrace those unique numbers and remove it from the input set and perform knapsack again and again until the set is not empty. If it is an empty that means we found the solution.

For case where duplicates are exist in the input set we will spread non distinct numbers into the pseudo descending cluster where each 3rd cluster is in descending order. That is a good heuristics that gives 99% good partitions in tests provided. 

If ``reminder`` is not empty then we need to optimize its size to 0. 

At this point we have the ``quotients`` and ``reminder``; quotients are ``M`` groups, ``reminder`` has ``T`` numbers. 

Let's call an existing group a ``partition point``. It contains the number of partition, the set of numbers, and the indexes of quotient item. We will define addition operation for the ``partion point``. It unions both groups given, preserves quotient indexes and adds group partitions. 

We sorts ``quotient`` groups by its length in descending order of ``N`` way partition problem case. It is more likely that group that have more items combined with ``reminder`` can be splited into new groups by knapsack solver.

So far, we have a collection of ``partition points`` and the ``reminder`` partition point. To optimize ``reminder`` we need to union its number set with other ``partition`` points and theirs sums and call knapsack solver for it. 

We are going to loop over the partition points and increase the limit of same time partition optimization. So the limit is going to be an iterator counter ``H``. After all point processed for current ``H``, we check the ``reminder`` lenght. If the length is decreased we set up new ``quotients`` and new ``reminder`` for next ``H`` loop interation. Once ``half of H`` partiton combinations visited we have an optimal solution.

So far the algorithm complexity of equal subset sum problem is ``O(2 ** ( M / 2) * (W))`` where M is number of partitions, W is complexity of knapsack groping operator. W is polynomial. W could be an exponential in super-increasing non sorted set which cannot be partitioned to ``M`` groups.

We can use the same approach to solve the ``strict 3(T) partition`` problem as well. That problem is ``NP complete`` in strong sense. https://en.wikipedia.org/wiki/3-partition_problem#cite_note-3. 

We will use knapsack with ``2 constrains`` as a grouping operator. The second constrain is group size which is equal to``3(T)``. We apply two modifications to our algorithm to do not allow fall into local maximum. We add shuffling ``reminder`` set before union with partition point and shuffling new ``quotients`` we got after each optimization iteration. 

# New partition algorithm performance

Below table was generated using integer partition test. It is trimmed version to show how the iteration grow speed depends on partition and set size. The full file generated by the script ``knapsack.py``.

Max iterations calculates by following expression: 

``([P ** 3) * ((N /P) ** 4)``. where ``N`` is items number, ``P`` is number of partitions.

Optimization column is the number of new quotients generated during the reminder optimization.  

<details>
  <summary> Partition iteration table 3, TBD </summary>
	
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

The subset sum and 1-0 knapsack algorithms were tested on hardinstances_pisinger integer numbers test dataset [9] and gave accurate results that were equal to expected ones [4]. Those algorithms were tested on rational numbers as input weights and constrains using the same dataset. Each weight was divided by 100 000. It also gives accurate result the same as for integer numbers.

``N`` dimension knapsack was tested along with classic 2 dimensional ``DPS`` solver on integer values. It also was tested using rational numbers on one dimension dataset, and as the grouping operator in strict ``T group M partition`` solution (tests provided for ``T=3`` and ``T=6``).

``M`` equal subset sum algorithm was tested by Leetcode test dataset https://leetcode.com/problems/partition-to-k-equal-sum-subsets/, and by testcases created by integer partition generator up to 102 549 items in the set and up to 10 000 partitions, and by rational numbers tests as well. First time heuristics made, works fine in 95% percent cases; for worst case where a lot of duplicates are present in given set the algorithm needs 1-2 optimizations in average and up to 5 optimization iterations for some cases. As much duplicate numbers in the input set as much optimization iterations required. 

Multiple knapsack and integer optimization tests were performed as well. Optimization iteration counter didn't exceed the declared maximum.

# Implementations and usage

The single ``knapsack.py`` script has all described algorithms, tests, and performance report generators. It is copy\paste friendly without 3d party dependencies. To run all knapsack tests, please, download test cases from [9], and copy those files to /hardinstances_pisinger directory. 

There are 4 python methods to use:
- ``partitionN``, which gets number set to partition, partitions number or list of particular sizes of each partition, strict partition group size.
- ``subsKnapsack``, which used in partitionN as set grouping operator. It requires the following parameters: size of knapsack, items, iterator counter array. 
- ``knapsack``, gets size of knapsack, items, values, iterator counter array. 
- ``knapsackNd``, expects the single tuple as size constrains of knapsack, items as tuples of dimensions, values, iterator counter array. It is used in partitionN method in the strict group size case.
- ``paretoKnapsack`` is slightly modified copy of the Nemhauser-Ullman algorithm implementation by ``Darius Arnold``.

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
