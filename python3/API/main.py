"""
Copyright Feb 2021 Konstantin Briukhnov (kooltew at gmail.com) (@CostaBru). San-Francisco Bay Area.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from knapsack.greedyNdKnapsack import greedyKnapsackNdSolver
from knapsack.paretoPoint import paretoPoint0
from knapsack.subsKnapsack import *
from knapsack.knapsack import *
from knapsack.knapsackNd import *
from knapsack.subsetSumParetoSolver import subsetSumParetoSolver
from knapsack.wPoint import *
from flags.flags import *

# < PUBLIC API >
from partition.partitionN import partitionSolver


def subsKnapsack(size, items, iterCounter):
    """
    The subset sum knapsack API.

    :param size: size of knapsack
    :type size: int
    :param items: knapsack items
    :type items: items int or decimal
    :param iterCounter: iteration counter
    :type iterCounter: array

    :return: bestValue, bestItems
    """
    solver = subsetSumKnapsackSolver(size, items, iterCounter, forceUseLimits=False)

    solver.printInfo = printPct
    solver.printSuperIncreasingInfo = verbose
    solver.doSolveSuperInc = doSolveSuperInc
    solver.doUseLimits = doUseLimits

    bestValue, bestItems = solver.solve()
    return bestValue, bestItems

def knapsack(size, items, values, iterCounter):
    """
    The 1/0 knapsack API.

    :param size: size of knapsack
    :type size: int

    :param items: knapsack items
    :type items: items int or decimal

    :param values: knapsack values
    :type values: items int or decimal

    :param iterCounter: iteration counter
    :type iterCounter: array

    :return: bestValue, bestSize, bestItems, bestValues
    """

    solver = knapsackSolver(size, items, values, iterCounter, forceUseLimits=False)

    solver.forceUseDpSolver = True
    solver.printInfo = printPct
    solver.printSuperIncreasingInfo = verbose
    solver.doSolveSuperInc = doSolveSuperInc
    solver.doUseLimits = doUseLimits

    bestValue, bestSize, bestItems, bestValues, bestIndexes = solver.solve()
    return bestValue, bestSize, bestItems, bestValues


def hybridKnapsack(size, items, values, iterCounter):
    """
    The KB hybrid 1/0 knapsack API. For worst case it calls Pareto solver.

    :param size: size of knapsack
    :type size: int

    :param items: knapsack items
    :type items: items int or decimal

    :param values: knapsack values
    :type values: items int or decimal

    :param iterCounter: iteration counter
    :type iterCounter: array

    :return: bestValue, bestSize, bestItems, bestValues
    """

    solver = knapsackSolver(size, items, values, iterCounter, forceUseLimits=False)

    solver.forceUseDpSolver = False
    solver.printInfo = printPct
    solver.printSuperIncreasingInfo = verbose
    solver.doSolveSuperInc = doSolveSuperInc
    solver.doUseLimits = doUseLimits

    bestValue, bestSize, bestItems, bestValues, bestIndexes = solver.solve()
    return bestValue, bestSize, bestItems, bestValues


def paretoKnapsack(size, items, values, iterCounter, useRatioSort=False):
    """
    The KB Pareto solver API.

    :param size: size of knapsack
    :type size: int

    :param items: knapsack items
    :type items: items int or decimal

    :param values: knapsack values
    :type values: items int or decimal

    :param iterCounter: iteration counter
    :type iterCounter: array

    :param useRatioSort: which sorting behaviour use ratio or dimension ASC
    :type useRatioSort: bool

    :return: bestValue, bestSize, bestItems, bestValues, bestIndexes
    """

    paretoItems = [wPoint1(item) for item in items]

    solver = knapsackParetoSolver(paretoItems, values, range(len(values)), wPoint1(size), paretoPoint1(0, 0),
                                  wPoint1(0), iterCounter)

    solver.printInfo = printPct
    solver.forceUsePareto = True
    solver.useRatioSort = useRatioSort

    bestValue, bestSize, bestItems, bestValues, bestIndexes = solver.solve()
    return bestValue, bestSize.getDimension(0), bestItems, bestValues


def hybridParetoKnapsack(size, items, values, iterCounter, useRatioSort=False):
    """
    The hybrid KB/Pareto solver API. It calls KB solver for worst cases of Pareto.

    :param size: size of knapsack
    :type size: int

    :param items: knapsack items
    :type items: items int or decimal

    :param values: knapsack values
    :type values: items int or decimal

    :param iterCounter: iteration counter
    :type iterCounter: array

    :param useRatioSort: which sorting behaviour use ratio or dimension ASC
    :type useRatioSort: bool

    :return: bestValue, bestSize, bestItems, bestValues, bestIndexes
    """

    paretoItems = [wPoint1(item) for item in items]

    solver = knapsackParetoSolver(paretoItems, values, range(len(values)), wPoint1(size), paretoPoint1(0, 0),
                                  wPoint1(0), iterCounter)

    solver.printInfo = printPct
    solver.forceUsePareto = False
    solver.useRatioSort = useRatioSort

    bestValue, bestSize, bestItems, bestValues, bestIndexes = solver.solve()
    return bestValue, bestSize.getDimension(0), bestItems, bestValues


def subsParetoKnapsack(size, items, iterCounter):
    """
    The subset sum knapsack KB pareto API.

    :param size: size of knapsack
    :type size: int
    :param items: knapsack items
    :type items: items int or decimal
    :param iterCounter: iteration counter
    :type iterCounter: array

    :return: bestValue, bestItems
    """

    solver = subsetSumParetoSolver(size, items, iterCounter, forceUseLimits=False)

    solver.printInfo = printPct
    solver.printSuperIncreasingInfo = verbose
    solver.doSolveSuperInc = doSolveSuperInc
    solver.doUseLimits = doUseLimits

    bestValue, bestItems = solver.solve()
    return bestValue, bestItems


def knapsackNd(constraints, items, values, iterCounter):
    """
    The N dimensional DP knapsack solver API.

    :param constraints: size of N dim knapsack
    :type constraints: wPoint

    :param items: knapsack items
    :type items: array of wPoint

    :param values: N dim knapsack values
    :type values: items int or decimal

    :param iterCounter: iteration counter
    :type iterCounter: array

    :return: bestValue, bestSize, bestItems, bestValues
    """

    solver = knapsackNSolver(constraints, items, values, iterCounter, wPoint([0] * constraints.getSize()), forceUseLimits=False)

    solver.forceUseDpSolver = True
    solver.printInfo = printPct
    solver.printDpInfo = printPct
    solver.printSuperIncreasingInfo = verbose
    solver.doSolveSuperInc = doSolveSuperInc
    solver.doUseLimits = doUseLimits

    bestValue, bestSize, bestItems, bestValues = solver.solve()
    return bestValue, bestSize, bestItems, bestValues


def hybridKnapsackNd(constraints, items, values, iterCounter):
    """
    The N dimensional DP knapsack solver API. For worst case calls the pareto solvers for each dimension and performs DP
    over union of each dimension results. Exits when each dimension gives less than maximum found.

    :param constraints: size of N dim knapsack
    :type constraints: wPoint

    :param items: knapsack items
    :type items: array of wPoint

    :param values: N dim knapsack values
    :type values: items int or decimal

    :param iterCounter: iteration counter
    :type iterCounter: array

    :return: bestValue, bestSize, bestItems, bestValues
    """

    solver = knapsackNSolver(constraints, items, values, iterCounter, wPoint([0] * constraints.getSize()), forceUseLimits=False)

    solver.forceUseDpSolver = False
    solver.useParetoAsNGreedySolver = True
    solver.printInfo = printPct
    solver.printSuperIncreasingInfo = verbose
    solver.doSolveSuperInc = doSolveSuperInc
    solver.doUseLimits = doUseLimits

    bestValue, bestSize, bestItems, bestValues = solver.solve()
    return bestValue, bestSize, bestItems, bestValues

def greedyKnapsackNd(constraints, items, values, iterCounter):
    """
    The N dimensional greedy knapsack solver API.

    :param constraints: size of N dim knapsack
    :type constraints: wPoint

    :param items: knapsack items
    :type items: array of wPoint

    :param values: N dim knapsack values
    :type values: items int or decimal

    :param iterCounter: iteration counter
    :type iterCounter: array

    :return: bestValue, bestSize, bestItems, bestValues
    """

    solver = greedyKnapsackNdSolver(constraints, items, values, iterCounter, wPoint([0] * constraints.getSize()))

    solver.printInfo = printPct
    solver.printSuperIncreasingInfo = verbose
    solver.doSolveSuperInc = doSolveSuperInc
    solver.doUseLimits = doUseLimits

    bestValue, bestSize, bestItems, bestValues = solver.solve()
    return bestValue, bestSize, bestItems, bestValues


def partitionN(items, sizesOrPartitions, groupSize, iterCounter, optimizationLimit=-1):
    """
    The N partition solver API. It divides items given by equal sums. Number of partitions with equal sums is given by parameter.
    The array of custom sums can be passed instead of partitions. We can set up the count of items in group via parameter.

    :param items: items to partition
    :type items: wPoint

    :param sizesOrPartitions: int number of equal sums, int array of sums
    :type sizesOrPartitions: int or array of int

    :param groupSize: group size count
    :type groupSize: int

    :param iterCounter: iteration counter
    :type iterCounter: array

    :param optimizationLimit: iteration counter
    :type optimizationLimit: int

    :return: quotients, reminder, optimizationCount
    """

    solver = partitionSolver(items, sizesOrPartitions, groupSize, iterCounter, optimizationLimit)

    solver.printOptimizationInfo = True
    solver.printInfo = printPct
    solver.useHybridParetoGrouping = False

    quotients, reminder, optimizationCount = solver.solve()
    return quotients, reminder, optimizationCount


def hybridPartitionN(items, sizesOrPartitions, groupSize, iterCounter, optimizationLimit=-1):
    """
    The N hybrid partition solver API. It divides items given by equal sums. Number of partitions with equal sums is given by parameter.
    The array of custom sums can be passed instead of partitions. We can set up the count of items in group via parameter.

    :param items: items to partition
    :type items: wPoint

    :param sizesOrPartitions: int number of equal sums, int array of sums
    :type sizesOrPartitions: int or array of int

    :param groupSize: group size count
    :type groupSize: int

    :param iterCounter: iteration counter
    :type iterCounter: array

    :param optimizationLimit: iteration counter
    :type optimizationLimit: int

    :return: quotients, reminder, optimizationCount
    """
    solver = partitionSolver(items, sizesOrPartitions, groupSize, iterCounter, optimizationLimit)

    solver.printOptimizationInfo = True
    solver.printInfo = printPct
    solver.useHybridParetoGrouping = True

    quotients, reminder, optimizationCount = solver.solve()
    return quotients, reminder, optimizationCount

# </ PUBLIC API >
