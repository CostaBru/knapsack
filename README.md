# Rethinking the knapsack and set partitions. (Not released yet).

The classic dynamic programing algorithm for 1-0 unbounded knapsack problem was extended to work with rational numbers, and to has any number of independent dimensions. Special cases were solved in polynomial time and used as part of new partition algorithm.

New algorithms were tested on the open source test datasets, and as a core part of equal subset problem algorithm. 

The algorithm for equal subset problem complexity was improved to be exponential in number of partitions only. The integer input type limitation was removed. That new algorithm was tested on integer partition generator data, and on integer optimization tests.

This work contains the source code of new ``KB`` knapsack and partition algorithms, performance analysis and reports:

- The polynomial time and space algorithm for unbounded subset sum knapsack problem for positive integer and rational numbers. 

- The exponential algorithm for unbounded 1-0 knapsack problem for positive integer and rational weights and profits, that performs in polynomial time\space for practical instances;

- The comparison of the Nemhauser-Ullmann ``NU`` Algorithm [12] with new 1-0 knapsack algorithm.

- The exponential algorithm for ``T`` independent dimensions unbounded 1-0 knapsack problem. The counting and non increasing order cases were solved in polynomial time. Non exact greedy algorithm was introduced for general case.

- The ``M`` equal-subset-sum of ``N`` integer number set that is exponential in ``M`` only.

- The algorithms for multiple knapsack that is exponential in numbers of knapsacks.

- ``M`` strict partition problem. The run time complexity is exponential in number of partition. That algorithm runtime is ``M`` times slower than the subset sum problem.

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

Let's call the sum of weight visited with current weight a ``w point``. Here we are going to generate the set of ``w points`` for each knapsack item. 

We will provide the current weight and sum of current item weight with all visited points before. Then, use DP recurrent formula for that new set. 

That growing collection gives as next recurrent expression for inner loop for ``Nth`` iteration:

``[ Wi + ((Wi + Wi-1) + (Wi + Wi-2) + ... + (Wi + Wi-n)) ]``, 

where ``W`` is the weight, and ``I`` is the index in collection of given items. At each ``N`` iteration we have expected maximum numbers of item weights we need to visit to reach optimal solution. 

The recurrent formula for that collection is ``(2 ** N) - 1``. Which is exponential in ``N``. That exponent is limited by ``C`` the size of knapsack. 

Since the size of ``w points`` subset is less then set ``1..C``. New algorithm requires less iterations to find the optimal solution.

The main driver of exponential growth is the count of new distinct sums generated after each iteration of ``Nth`` item. 

Because the partition function of each existing sum grows as an exponential function of the square root of its argument, the probability of new sum generated be an unique falls down dramatically when count of sums grows up. 

This limitation function is non linear and it is the subject for further work.

In case of ``T`` dimensional knapsack, each new dimension added decreases this limitation effect significantly. 

Having that we can state that the best case for knapsack is all duplicate weights in given set. The complexity is ``O(N**2)``,  in that case. 

Super-increasing sequence of weights [10] can be solved in ``O(N LogN)``.

<details>
  <summary> Super-increasing sequence definition </summary>

Number sequence is called super-increasing if every element of the sequence is greater than the sum of all previous elements in the sequence.

</details>

The worst case for the algorithm is considering as much possible of unique weights as possible. We can state that the almost super-increasing set is the worst case, where each sums for previous ``N`` numbers minus one is equal to next ``N item`` in the ordered set.  

``DPS`` algorithm accumulates the result in ``[N x C]`` DP table, where ``C`` is size of knapsack. This new algorithm are not going to visit all weights possible from 1 to ``C``, but only sums and weights itself. To gather the result from DP table, we should keep track of maximum weight and value,
 we have archived for each ``w point`` visited. When all ``w points`` have processed, or we found optimal solution earlier (in case of item weight is equal item value) we can backtrace items using DP table in the same way as in ``DPS``. 

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

If our new algorithm gets items given in non increasing order then the highest and the first ``Nth`` partial sum is going to be equal ``Nth`` weight (dimension), for ``Nth + 1`` it is equal to ``[ S(N - 1) = S(N) +  Ith weight]`` and so on. of

Increasing order items will reverse partial sums array since we are considering items in non increasing order.

We spend a single iteration through ``M`` items to know:
- the flag indicating whether collection of items is in increasing or decreasing order, 
- given dimensions is super-increasing set or not,
- are all values equal,
- are values equal to first item dimension.

If given collection is sorted order we also collect:
- the flags for super-increasing items,
- partial sums for each item.

In case of sorted items we can define three limitation factors for growing collection of ``w point``. 

- First one is ``NL``. It is equal to ``C - Ith partial sum``, where ``C`` is size of knapsack. 
- If item is super-increasing to previous one we will define ``OL`` lower bound factor. It will be equal to ``NL + current item``. 
- Third factor is ``PS`` which is partial sum for that item. If ``PS >= C/2`` where C is size of knapsack, then this item itself can be skipped. We are interested in contribution of this item to existing sums. 

``OL`` is equal to ``NL`` if item is not super-increasing to previous one. All new generated points those less than ``NL`` will be skipped. All previous point those less than ``OL`` will be skipped as well. 

Having those factors, we will define the sliding window where optimal solution is exist. All points that are out of our window will not contribute to optimal solution. 

If items are non sorted then we cannot use ``NL``, ``OL``, and ``PS`` limitation factors. Only distinct sums will work in that case and will give exponential grow up to ``M/2`` where M is items count.

That optimization can be used in case of subset sum knapsack, equal values knapsack items, and when value is equal to first dimension, no matter of knapsack dimension count. 

The main prerequisite is the increasing or decreasing order of items given.

## 1-0 and N dimension knapsacks

Here we accumulate profit\dimension sum reached for each ``W point`` using the same DP recurrent formula. 

Each new dimension requires more memory for storing it in point list and in DP table map keys collection and more CPU operations to compare new dimension as well. 

The results below shows that N dimension algorithm N times slower than single dimensional one.

Once we get rid of integer indexes in the DP table, using a ``w point`` as key to access the profit value, and dimensions in DP map, we can use described algorithms for ``all positive rational numbers`` without converting knapsack constrains and item dimensions given to integers.

Above solutions solve the knapsack problems which are strongly ``NP-complete`` if the weights and profits are given as rational numbers. https://en.wikipedia.org/wiki/Knapsack_problem#cite_note-Wojtczak18-12

# The Nemhauser-Ullman algorithm

The Nemhauser-Ullman algorithm [12] for the knapsack problem computes the Pareto curve and returns the best solution from the curve.

For now, the GitHub has two implementations of this algorithm. One of them which is written by ``Darius Arnold`` in python3, was included in knapsack.py with paretoKnapsack method. The code was modifeid a little bit to count interations and some corner cases patches applied to make it works on test dataset. 

Please see and star https://github.com/dariusarnold/knapsack-problem repository.

# KB knapsack analysis and comparison with Nemhauser-Ullman

Here are the ``w point`` growing speed table on each ``Nth`` iteration. 

- ``KB`` is new algorithm.
- ``NU`` is Nemhauser-Ullman algorithm.

Larger profit point search complexity for NU was considered as ``Log2N``, but was implemented by ``Darius Arnold`` in ``N``.

<details>
  <summary> Iteration table #1. [1..51]. `[N=50], ASC </summary>

|  N  | KB sums | KB iter |     |  NU sums | NU iter |
|-----|---------|---------|-----|----------|---------|


</details>

<details>
  <summary> Iteration table #2. Iteration table. 1 and 2 values. [N=50], ASC </summary>

|  N  | KB sums | KB iter |     |  NU CNT | NU sums |
|-----|---------|---------|-----|---------|---------|


</details> 

<details>
  <summary> Iteration table #3. Iteration table [1..50] numbers. [N=50], ASC </summary>
  
|  N  | KB sums | KB iter |     |  NU CNT | NU sums |
|-----|---------|---------|-----|---------|---------|


</details> 

<details>
  <summary> Iteration table #4. 50 random numbers in [1..1000] range, ASC</summary>
  
|  N  | KB sums | KB iter |     |  NU CNT | NU sums |
|-----|---------|---------|-----|---------|---------|

</details> 


<details>
  <summary> Iteration table #5. Random numbers in [1...10000000000000000]. [N=15], ASC </summary>
	
|  N  | KB sums | KB iter |     |  NU CNT | NU sums |
|-----|---------|---------|-----|---------|---------|

	
</details>

<details>
  <summary> Iteration table #6. Geometric progression with factor equal 2.  [N=15 + 1]. ASC. Last item is middle duplicated. </summary>
	
|  N  | KB sums | KB iter |     |  NU CNT | NU sums |
|-----|---------|---------|-----|---------|---------|


</details>

<details>
  <summary> Iteration table #7. Factorial numbers [numbers[i] *= (int(numbers[i - 1]) - 1)]. [N=15 + 1]. DESC. Last item is middle duplicated. </summary>
	
|  N  | KB sums | KB iter |     |  NU CNT | NU sums |
|-----|---------|---------|-----|---------|---------|

	
</details>

<details>
  <summary> Iteration table #8. Factorial numbers [numbers[i] *= (int(numbers[i - 1]) - 1)]. [N=15 + 1]. ASC. Last item is middle duplicated. </summary>
	
|  N  | KB sums | KB iter |     |  NU CNT | NU sums |
|-----|---------|---------|-----|---------|---------|

	
</details>

## 2D dimensional KB knapsack

<details>
<summary> Test dataset, N = 28:</summary>

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
  <summary> Iteration table #9. KB 2D dimensional knapsack. </summary>
  
|  N  | KB sums | KB iter |  
|-----|---------|---------|

	
</details>

<details>
  <summary> Iteration table #10. KB knapsack solver for knapPI_16_500_1000 dataset. N=500, Max iter is 500 000 000. </summary>

|case|size|iter asc |iter desc|iter non|asc time|desc time|non time|best iter|best time|
|----|----|---------|---------|--------|--------|---------|--------|---------|---------|

</details>

Result table #9 shows polynomial time for ``KB`` 2D knapsack with mixed integer and rational dimensions. Maximum iteration is ``2 ** N`` which is equal to 268 435 456; difference between max and actual is 262 184 958.	

Looking at the table #8, we can see exponential grow for ``KB`` knapsack in case of factorial numbers and ASC order numbers given. 

That exponential grow rate is subject for further investigation and improvement. 

Those results shows that new ``KB`` knapsack algorithm performs much faster than ``NU``, and solves large number problems in polynomial time and space.

# New equal subset sum algorithm

Equal subset sum is only ``weakly NP-hard`` - it is hard only when the numbers are encoded in non-unary system, and have value exponential in ``N``.
When the values are polynomial in ``N``, Partition can be solved in polynomial time using the pseudo-polynomial time number partitioning algorithm.

We are going to use new knapsack solution to solve ``M`` equal subset sum problem which is the exponential in ``M`` only. 

Let's consider ``N`` input numbers as sequence we should divide into ``M`` groups with equal sums. Let's denote a knapsack solver be a grouping operator that returns first group that met sum and group count contrains. To solve that problem we need to run that grouping operations ``M`` times. If we get an empty ``reminder`` at the end then the problem is solved. 

The knapsack solver over distinct sorted numbers divides the set into ``M`` partitions if and only if that ``M`` partitions are exist. We can consider sums like a hashing. Hence each unique number leave a unique trace in the point sums, and we know that knapsack search terminates execution once the size of knapsack has reached. Then we can backtrace those unique numbers and remove it from the input set and perform knapsack again and again until the set is not empty. If it is an empty that means we found the solution.

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
