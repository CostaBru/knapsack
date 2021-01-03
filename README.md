# Knapsack and Set Partitions

Polynomial time algorithms for unbounded 1-0 knapsack problems up to N dimensions, algorithms for N way sum partition and strict N partition problems.

# Abstract

The knapsack problem is well known and described in many articles and books. The goal of this work is not to repeat it so the intro is going to be a very briefly.

The classical knapsack problem is defined as follows: 

We are given a set of N items, each item J having an integer Pj and an integer weight Wj . The problem is to choose a subset of the
items such that their overall profit is maximized, while the overall weight does not exceed a given capacity C [6].

Let's consider classical bottom-up dynamic programing solution for unbounded knapsack problem. Let's call it DPS. Bounded version of that problem has known way of reduction to unbounded one [5].

It uses recurrent formula to calculate maximum value going through item weights array and checks every weight possible using DP table from 1 to size of knapsack. 
DPS algorithm is very efficient on small numbers. It has a limitation to use only positive integers as input. Time and memory Complexity is O(N * M) which is known as pseudopolynomial.

During solving the multiway number partition problem [7] using knapsack, I noticed that classical algorithm did extra work by considering possibilities those never would be a part of the optimal solution.

Classic DP works in integer set 1..S integer numbers, where S is size of knapsack. [1] 

But the optimal solution can be only in subset W, where W contains items and sums of all items that less than the size of knapsack. (Axiom 1)

When weight considered is not a part of sum of items then classic DP algorithm compares and copies maximum value reached to next DP table cell. 

# Motivation

Of course, the main driver is curiosity, an attempt to answer the question "What if?", and the kind of math intuition. I had a strong feeling that knapsack should have a polynomial time algorithm. Because it uses addition which is commutative, meaning that order does not matter, and it is associative, and subtraction, which is inverse operation for addition, to locate the optimal solution. 

The goal of this work to enhance the classical solution and make the knapsack 1-0 algorithm be the true polynomial.

# The main idea

Due to Axiom 1, let's consider only weights and sums of weights. We will perform the DP algorithm over that collection for each item. Doing this we get polynomial time and space algorithm. (Teor 1)

Let's call the sum of weight visited with current weight a point. We are going to generate the set of W point for each knapsack item. We will provide the current weight and sum of current item weight with all visited points before. And use classic DP formula for that new set. 

That growing collection gives as next recurrent expression for inner loop for Nth iteration [ Wi + ((Wi + Wi-1) + (Wi + Wi-2) + ... + (Wi + Wi-n)) ], where W is the weight, and I is the index in collection of given items.
At each N iteration we have expected maximum numbers of item weights we need to visit to reach optimal solution. The first numbers of that growing sequence are the following:

0, 1, 3, 7, 14, 25, 41, 63, 92, 129, 175, 231, 298, 377, 469, 575, 696, 833, 987, 1159. That sequence is known as A004006 (https://oeis.org/A004006)

The Nth element can be calculated by following formula: 

A(n) = C(n,1) + C(n,2) + C(n,3), or n*(n ** 2 + 5)/6. 

The sum of N elements is equal to (n ** 4 + 10 * n ** 2) // 24. The complexity in big O notation is equal to O(N ** 4). 

As soon we are not going to visit all weights possible from 1 to knapsack size, but only sums and weights itself, we should keep track of maximum weight and value we have archived for each point visited. When we processed all items points or found optimal solution earlier (in case of item weight is equal item value) we can backtrace items using DP table in the same way as in classical dynamic programing solution. 

Instead of array of array as DP table, we are going to use array of map to keep O(1) access time for points that belong to W set.
The map key is point visited, the map value is accumulated weight and value for that key.
We are going to process points in ASC order. We will merge two sorted list into single one in O(N + M), where N previous point count, M is new points created. Hence the previous list has been ordered already and the new one we get from previous list using current weight addition. 
Classic DPS uses recurrent formula: 

max(value + DP[i][j - weight], DP[i][j]).

In our solution DP table contains values for processed points only. 
The case [j - weight] can give a point that does not belong to set W, that means that point would never contribute to the optimal solution (Axiom 1), and we can assign 0 value for outsider point. 

# Three kind of problem

We are going to investigate three kinds of knapsack problems.
First one is knapsack where the item value and the item weight are the same. Let's call it 1D knapsack problem. The knapsack problem where value and weight are different is 2D problem. 1D and 2D knapsack problems are known as weakly NP hard problems in case of integer numbers.[2]
N dimensional knapsack has N constrains, M items and M values, where Mth item is the vector of item dimensions of size N. The multi-dimensional knapsacks are computationally harder than knapsack; even for D=2, the problem does not have EPTAS unless P=NP. [1]

## 1D knapsack

It is simpler than others, because we can terminate execution once we have found a solution equal to knapsack size. 
We are going to use this property in N subset sum problem. 
Also, here we can reduce the point collection growing speed, because some new points created will not contribute to the optimal solution. The reason of it is the depth of execution tree and growing speed of the sum starting from current one. 
Let's call a partial sum is the number we get for some Ith element from minimum item to current item. Here we expect knapsack items in DESC order, so the smallest and the last Nth partial sum is going to be equal Nth weight, for Nth - 1 it is equal to [ S(N - 1) = S(N) +  Ith weight] and so on. 
We are going to use that partial sum and the knowledge of desc iteration flow to skip new points from growing collection.
We use partial sum to decide to do we need add this weight or just use created new points. In addition, we could skip new sum point if that sum is less then knapsack size minus partial sum. (Lemma 1)
In fact, the 1D knapsack problem time and space complexity begin to fall from O(N**4) to O(N**3) starting Ith item iteration where knapsack size is less that size // 2. (Teor 2) 

## 2D and N dimension knapsacks

They are required to visit all sums and cannot skip any of them. We use both weights\volume as W point and accumulate value\weight\volume reached for the W point using the same DP recurrent formula. 
Each new dimension requires more memory for storing that dimension in point list and in DP table map keys collection, and we need to compare more numbers as well. P knapsack time and space complexity are not greater than O( ( N * P ) ** 4), where P number of knapsack constrains, N count of knapsack items. 
Because of unique point processing and cutting new points by knapsack constrains the average complexity is near O(C * (( N * P ) ** 3)), where C is constant that dependents on N.  C falls for large N. N = 20 C is 10; for N = 500 C is 3.

Once we get rid of integer indexes in the DP table, using a point as key to access the value, weight and volume in DP map, we can use described algorithms for all positive rational numbers without converting knapsack constrains and item weights given to integers.
Above solutions solve the knapsack problems which are strongly NP-complete if the weights and profits are given as rational numbers. https://en.wikipedia.org/wiki/Knapsack_problem#cite_note-Wojtczak18-12

### Axiom 1

The optimal solution could be found in set of all sums of items weights only. It is self-evident, because the optimal solution contains given items only.

### Teor 1

The dynamic programing recurrent formula max(DP[i], DP[i - w] + v) works for set of sums. Prof: Because the set W is existing in set S, where set W are the items and sums, where set S are numbers starting 1 up to knapsack size,
then DPS recurrent formula max(DP[i], DP[i - w] + v) works for W points as well. if [i - w] is not the sum of items it will not be in optimal solution anyway due to Axiom 1, 
and we consider 0 value for that point-outsider.

### Lemma 1 for 1D knapsack: 

If partial sum is less than size of knapsack // 2 then that item itself cannot be a first item of optimal solution. 
It may be a part of solution, so we can consider only sums previous points with this item. 

### Lemma 2 for 1D knapsack:

We can consider the starting way of each point and the full way from that point to knapsack size as part of other sums.
The W point cannot reach the size of knapsack as part of sums of next algorithm iterations and will not contribute to optimal solution if it less than knapsack size minus partial sum for current item.  

### Teor 2 for 1D knapsack: 

The 1-0 knapsack problem where p = w has O(C * (N ** 3)) time and space complexity. 
Prof: Growing speed without addition item weight itself to the W point is less that O (N ** 4).
The first items are the following: 1, 3, 7, 11, 16, 22, 30, 38, 47, 57, 69, 81, 94, 108, 124, 140, 157, 175, 195, 215, 236, 258. 
That is known as A082644 integer number sequence. https://oeis.org/A082644. 
The n'ht element can be calculated by next formula: n * (n - 1/2 ) / 2.  
Sum of N is (n ** 3) // 6 - (n ** 2) // 8. Which is O(N ** 3). 

# Analysis

Let's consider 1D knapsack and calculate the number of iterations needed to find a optimal solution for three types of input data: prime numbers, non-prime numbers, and the integer sequence from 2 to 101. 

- Set 1: [3, 7, 13, 31, 37, 43, 67, 73, 79, 127, 151, 163, 193, 211, 223, 241, 283, 307, 331, 349, 367, 409, 421, 433, 463, 487, 541, 577, 601, 613, 619, 631, 643, 673, 727, 739, 769, 787, 823, 883, 937, 991, 997]
- Set 2: [Set 1] + 1
- Set 3: Integer numbers in 2-101 range.
 
So far, we can state that the worst case for the algorithm described is considering all numbers of the sums. The prime numbers as input weights is the worst case. 
On the other hand, the duplicates given as input will give the minimum number of iterations. 
To calculate the actual number of iterations we will pass the range 1..[sum of weights - 1] as knapsack sizes in a row and perform the algorithm for given input data.

The results are following:
Primes and Primes plus one. N is 43. The knapsack size and number iteration table below.

| Size   | Prime    | Non prime|
|--------|----------|----------|
| 18 061 | 184 463 | 117 100  |
| 10 182 | 58  615 | 11  422  |
| 4  546 | 18  389 |  9  232  |
| 1  435 | 4   815 | 10  034  |
|   445  | 1   518 | 1   418  |
|   295  |     926 |     719  |
|    53  |      91 |      85  |

N ** 4 is 3 418 801 and N ** 3 is 79 507, so the worst-case iteration number is not exceeding (N ** 3) * 10 for N = 43

Iteration table for set 3. N is 99.
| Size   |  Iter   |
|--------|---------|
| 5 048  | 166 482 |
| 4 546  | 148 566 |
| 2 749  |  39 836 |
| 1 435  |   6 038 |
|   445  |     891 |
|   295  |     130 |
|    53  |     103 |

N ** 4 is 96 059 601 and N ** 3 is 970 299, so the worst-case iteration number does not exceed (N ** 3) for N = 99

# Polynomial partitions algorithms

Partition is only weakly NP-hard - it is hard only when the numbers are encoded in non-unary system, and have value exponential in n.
When the values are polynomial in N, Partition can be solved in polynomial time using the pseudopolynomial time number partitioning algorithm.

We are going to use new knapsack solution to create the polynomial algorithm for all positive numbers. 

Let's consider input numbers as sequence we should divide into N groups. Let's call a knapsack solver a grouping operator that returns first group that met sum and group count contrains. To solve that problem we need to run that grouping operations N times. If we get an empty reminder at the end then the problem is solved. 

The knapsack solver over distinct desc sorted numbers divides the set into N partitions if and only if that N partitions are exist. We can consider sums like a hashing. Hence each unique number leave a unique trace in the point sums and we know that knapsack search terminates execution once the size of knapsack has reached. Then we can backtrace those unique numbers and remove it from the input set and perform knapsack again and again until the set is not empty. If it is an empty that means we found the solution.

For case where duplicates are exist in the input set we will spread non distinct numbers into the pseudo descending set. Each duplicate should be in its own desc ordered cluster when we perform knapsack over full collection and take items out. That is a good heuristics that gives 99% good partitions in tests provided. 

If reminder is not empty then we need to optimize its size to 0. At this point we have a quotient and reminder, quotient has M groups, reminder has T numbers. 

Let's call an exisiting group a partion point. It contains the number of partition, the set of numbers, and the indexes of quotient item. We will define addition operation for the partition point. It unions both groups given, preserves quotient indexes and adds group partitions. 

We sorts quotient groups by its length in descending order of N way partition problem case. It is more likly that group that have more items combined with reminder can be splited into new groups by knapsack solver.

So far, we have a collection of partition points and the reminder partition point. To optimize reminder we need to union reminder number set with other partition points and theirs sums and call knapsack solver for it. 

We are going to loop over the partition points and increase the limit of same time partition optimization. So the limit is going to be an iterator counter M. After all point processed for current M, we check the reminder lenght. If the length is decreased we set up new quotient and new reminder for next M loop interation. Once Log(M) partiton combinations visited we have an optimal solution.

We can use the same approach to solve the strict 3 partition problem as well. That problem is NP complete in strong sense. https://en.wikipedia.org/wiki/3-partition_problem#cite_note-3. We will use knapsack with 2 constrains as a grouping operator. The second constrain is group size which is 3. We apply two modifications to our algorithm to do not allow fall into local maximum. We add shuffling reminder set before union with partition point and shuffling new quotient we got after each optimization iteration.

Time and space complexity for M partition for N items problem is the following: O(M * LOG(M) * ( N/M ) ** 3). 
For strict T groups M partitions for N items is O(M * LOG(M) * ((T * N)/M) ** 3).

# Partition performance

Therea are several iteration counter tables for integer partition generator tests. Max iterations calculates by following expression: len(subSet)) ** 3 + (partition ** 3)

| item | integer | generator limit | partitions |     N      |  sum  |  iterations  |  max iterations |
|------|---------|-----------------|------------|------------|-------|--------------|-----------------|
|1|30|20|20|63|600|1633|258047|
|1|50|20|20|63|1000|1633|258047|
|1|30|50|50|201|1500|10710|8245601|
|1|54|100|100|462|5400|46059|99611128|
|1|54|200|200|1047|10800|189199|1155730823|
|1|54|300|300|1648|16200|421012|4502809792|
|1|54|500|500|2996|27000|1204989|27017143936|
|1|31|1000|1000|6662|31000|5121601|296674509528|
|1|54|1000|1000|6658|54000|5835656|296142242312|
|1|30|2000|2000|14824|60000|21843987|3265588468224|
|1|31|2000|2000|14743|62000|21857184|3212480230407|
|1|32|2000|2000|14667|64000|21959736|3163178078963|
|1|33|2000|2000|14639|66000|21997810|3145142399119|
|1|34|2000|2000|14605|68000|22244327|3123334495125|
|1|35|2000|2000|14579|70000|22197294|3106726226539|
|1|36|2000|2000|14564|72000|22590997|3097171438144|
|1|37|2000|2000|14556|74000|22641850|3092083591616|
|1|38|2000|2000|14546|76000|23408940|3085731643336|
|1|39|2000|2000|14546|78000|101183731|3085731643336|
|1|40|2000|2000|14546|80000|118185589|3085731643336|
|1|41|2000|2000|14546|82000|30166858|3085731643336|
|1|42|2000|2000|14546|84000|131310271|3085731643336|
|1|43|2000|2000|14546|86000|134634125|3085731643336|
|1|44|2000|2000|14546|88000|28293240|3085731643336|
|1|45|2000|2000|14546|90000|206177280|3085731643336|
|1|46|2000|2000|14546|92000|27931092|3085731643336|
|1|54|2000|2000|14546|108000|24767996|3085731643336|

| item | integer | generator limit | partitions |     N      |  sum  |  iterations  |  max iterations |
|------|---------|-----------------|------------|------------|-------|--------------|-----------------|
|2|54|20|20|63|1080|1633|258047|
|2|54|50|50|201|2700|10711|8245601|
|2|54|100|100|462|5400|46059|99611128|
|2|54|200|200|1047|10800|189199|1155730823|
|2|54|300|300|1648|16200|421012|4502809792|
|2|54|500|500|2996|27000|1204989|27017143936|
|2|30|1000|1000|6665|30000|5133383|297074129625|
|2|54|1000|1000|6658|54000|5835521|296142242312|
|2|30|2000|2000|14824|60000|21843987|3265588468224|
|2|32|2000|2000|14667|64000|21959736|3163178078963|
|2|34|2000|2000|14605|68000|22244327|3123334495125|
|2|36|2000|2000|14564|72000|22590997|3097171438144|
|2|54|2000|2000|14546|108000|24768025|3085731643336|

| item | integer | generator limit | partitions |     N      |  sum  |  iterations  |  max iterations |
|------|---------|-----------------|------------|------------|-------|--------------|-----------------|
|3|54|20|20|63|1080|1633|258047|
|3|54|50|50|201|2700|10711|8245601|
|3|54|100|100|462|5400|46059|99611128|
|3|54|200|200|1047|10800|189199|1155730823|
|3|30|300|300|1648|9000|732097|4502809792|
|3|54|300|300|1648|16200|421012|4502809792|
|3|54|500|500|2996|27000|1204989|27017143936|
|3|30|1000|1000|6665|30000|5133383|297074129625|
|3|54|1000|1000|6658|54000|5835556|296142242312|
|3|30|2000|2000|14824|60000|21843987|3265588468224|
|3|33|2000|2000|14639|66000|21997810|3145142399119|
|3|36|2000|2000|14564|72000|22590997|3097171438144|
|3|54|2000|2000|14546|108000|24767977|3085731643336|

| item | integer | generator limit | partitions |     N      |  sum  |  iterations  |  max iterations |
|------|---------|-----------------|------------|------------|-------|--------------|-----------------|
|5|50|20|20|63|1000|1633|258047|
|5|50|50|50|201|2500|10711|8245601|
|5|50|100|100|462|5000|46048|99611128|
|5|50|200|200|1047|10000|189060|1155730823|
|5|50|300|300|1648|15000|453346|4502809792|
|5|50|500|500|2996|25000|1207938|27017143936|
|5|30|1000|1000|6665|30000|5133383|297074129625|
|5|50|1000|1000|6658|50000|5842996|296142242312|
|5|30|2000|2000|14824|60000|21843987|3265588468224|
|5|35|2000|2000|14579|70000|22197294|3106726226539|
|5|50|2000|2000|14546|100000|25420670|3085731643336|

| item | integer | generator limit | partitions |     N      |  sum  |  iterations  |  max iterations |
|------|---------|-----------------|------------|------------|-------|--------------|-----------------|
|7|49|20|20|63|980|1633|258047|
|7|49|50|50|201|2450|10711|8245601|
|7|49|100|100|462|4900|46042|99611128|
|7|49|200|200|1047|9800|189004|1155730823|
|7|49|300|300|1648|14700|423507|4502809792|
|7|49|500|500|2996|24500|1206965|27017143936|
|7|49|1000|1000|6658|49000|5637168|296142242312|
|7|35|2000|2000|14579|70000|22197294|3106726226539|
|7|49|2000|2000|14546|98000|88188627|3085731643336|

| item | integer | generator limit | partitions |     N      |  sum  |  iterations  |  max iterations |
|------|---------|-----------------|------------|------------|-------|--------------|-----------------|
|8|48|20|20|63|960|1633|258047|
|8|48|50|50|201|2400|10711|8245601|
|8|48|100|100|462|4800|46038|99611128|
|8|48|200|200|1047|9600|188949|1155730823|
|8|48|300|300|1648|14400|474438|4502809792|
|8|48|500|500|2996|24000|1212399|27017143936|
|8|48|1000|1000|6658|48000|5772972|296142242312|
|8|32|2000|2000|14667|64000|21959736|3163178078963|
|8|40|2000|2000|14546|80000|118187137|3085731643336|
|8|48|2000|2000|14546|96000|27808543|3085731643336|

| item | integer | generator limit | partitions |     N      |  sum  |  iterations  |  max iterations |
|------|---------|-----------------|------------|------------|-------|--------------|-----------------|
|10|50|20|20|63|1000|1633|258047|
|10|50|50|50|201|2500|10711|8245601|
|10|50|100|100|462|5000|46048|99611128|
|10|50|200|200|1047|10000|189060|1155730823|
|10|50|300|300|1648|15000|453337|4502809792|
|10|50|500|500|2996|25000|1207938|27017143936|
|10|30|1000|1000|6665|30000|5133383|297074129625|
|10|50|1000|1000|6658|50000|5842966|296142242312|
|10|30|2000|2000|14824|60000|21843987|3265588468224|
|10|40|2000|2000|14546|80000|118196147|3085731643336|
|10|50|2000|2000|14546|100000|25420656|3085731643336|

| item | integer | generator limit | partitions |     N      |  sum  |  iterations  |  max iterations |
|------|---------|-----------------|------------|------------|-------|--------------|-----------------|
|11|44|20|20|63|880|1633|258047|
|11|44|50|50|201|2200|10711|8245601|
|11|44|100|100|462|4400|46017|99611128|
|11|44|200|200|1047|8800|211849|1155730823|
|11|44|300|300|1648|13200|424299|4502809792|
|11|44|500|500|2996|22000|1206340|27017143936|
|11|44|1000|1000|6658|44000|6451809|296142242312|
|11|33|2000|2000|14639|66000|21997810|3145142399119|
|11|44|2000|2000|14546|88000|28293299|3085731643336|


# Results validation

1D and 2D knapsack algorithms were tested on hardinstances_pisinger integer numbers test dataset [9] and gave accurate results that were equal to expected ones [4].

1D and 2D knapsack algorithms were tested on rational numbers as input weights and constrains using the same dataset. Each weight was divided by 100 000. It also gives accurate result the same as for integer numbers.

N dimension knapsack was tested along with classic 2 dimensional DP solver on integer values. It also was tested using rational numbers on one dimension dataset, and as the grouping operator in strict T group M partition solution (tests provided for T=3).

N way sum partition algorithm was tested by Leetcode test dataset https://leetcode.com/problems/partition-to-k-equal-sum-subsets/, and by testcases created by integer partition generator up to 102 549 items in the set and up to 10 000 partitions, and by rational numbers tests. First time heuristics made works fine in 95% percent cases; for worst case where a lot of duplicates are present in given set the algorithm needs 1-2 optimizations in average and up to 5 optimization iterations for some cases. As much duplicate numbers in the input set as much optimization iterations required. 

# Conclusion

Since, N dimension knapsack and 2D knapsack on rational numbers are NP complete in strong sense and the algorithm described solved that problems using polynomial time and space, I can consider, with care, that NP = P at least for weak NP problems which optimal solutions are exists in subset, that can be calculated using commutative, associative and inversing math operation, like addition and subtraction, or multiplication and division. 

# Further work

Investigate possibility of such enhancements for other kinds of problems that have known pseudo polynomial complexity and can be solved in dynamic programing way. 

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

## License
[MIT](https://choosealicense.com/licenses/mit/)
