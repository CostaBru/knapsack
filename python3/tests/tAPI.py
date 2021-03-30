from knapsack.knapsack import knapsackSolver, knapsackParetoSolver
from knapsack.knapsackNd import knapsackNSolver
from knapsack.paretoPoint import paretoPoint1, paretoPoint0
from knapsack.subsKnapsack import subsetSumKnapsackSolver
from knapsack.subsetSumParetoSolver import subsetSumParetoSolver
from knapsack.wPoint import wPoint1, wPoint
from partition.partitionN import partitionSolver


def subsKnapsack(size, items, iterCounter, printPct=False, doSolveSuperInc=True, doUseLimits=True):
    solver = subsetSumKnapsackSolver(size, items, iterCounter, forceUseLimits=False)

    solver.printInfo = printPct
    solver.printSuperIncreasingInfo = True
    solver.doSolveSuperInc = doSolveSuperInc
    solver.doUseLimits = doUseLimits

    bestValue, bestItems = solver.solve()
    return bestValue, bestItems


def knapsack(size, items, values, iterCounter, printPct=False, doSolveSuperInc=True, doUseLimits=True):
    solver = knapsackSolver(size, items, values, iterCounter, forceUseLimits=False)

    solver.forceUseDpSolver = True
    solver.printInfo = printPct
    solver.printSuperIncreasingInfo = True
    solver.doSolveSuperInc = doSolveSuperInc
    solver.doUseLimits = doUseLimits

    bestValue, bestSize, bestItems, bestValues, bestIndexes = solver.solve()
    return bestValue, bestSize, bestItems, bestValues


def hybridKnapsack(size, items, values, iterCounter, printPct=False, doSolveSuperInc=True, doUseLimits=True):
    solver = knapsackSolver(size, items, values, iterCounter, forceUseLimits=False)

    solver.forceUseDpSolver = False
    solver.printInfo = printPct
    solver.printSuperIncreasingInfo = True
    solver.doSolveSuperInc = doSolveSuperInc
    solver.doUseLimits = doUseLimits

    bestValue, bestSize, bestItems, bestValues, bestIndexes = solver.solve()
    return bestValue, bestSize, bestItems, bestValues


def paretoKnapsack(size, items, values, iterCounter,
                   useRatioSort=False,
                   printPct=False,
                   doSolveSuperInc=True,
                   doUseLimits=True):
    paretoItems = [wPoint1(item) for item in items]

    solver = knapsackParetoSolver(paretoItems, values, range(len(values)), wPoint1(size), paretoPoint1(0, 0),
                                  wPoint1(0), iterCounter)

    solver.printInfo = printPct
    solver.forceUsePareto = True
    solver.useRatioSort = useRatioSort

    bestValue, bestSize, bestItems, bestValues, bestIndexes = solver.solve()
    return bestValue, bestSize.getDimension(0), bestItems, bestValues


def hybridParetoKnapsack(size, items, values, iterCounter,
                         useRatioSort=False,
                         printPct=False,
                         doSolveSuperInc=True,
                         doUseLimits=True,
                         forceUsePareto=False
                         ):
    paretoItems = [wPoint1(item) for item in items]

    solver = knapsackParetoSolver(paretoItems, values, range(len(values)), wPoint1(size), paretoPoint1(0, 0),
                                  wPoint1(0), iterCounter)

    solver.printInfo = printPct
    solver.forceUsePareto = forceUsePareto
    solver.useRatioSort = useRatioSort

    bestValue, bestSize, bestItems, bestValues, bestIndexes = solver.solve()
    return bestValue, bestSize.getDimension(0), bestItems, bestValues


def subsParetoKnapsack(size, items, iterCounter,
                       printPct=False,
                       doSolveSuperInc=True,
                       doUseLimits=True):
    solver = subsetSumParetoSolver(size, items, iterCounter, forceUseLimits=False)

    solver.printInfo = printPct
    solver.printSuperIncreasingInfo = True
    solver.doSolveSuperInc = doSolveSuperInc
    solver.doUseLimits = doUseLimits

    bestValue, bestItems = solver.solve()
    return bestValue, bestItems


def knapsackNd(constraints, items, values, iterCounter,
               printPct=False,
               doSolveSuperInc=True,
               doUseLimits=True
               ):
    solver = knapsackNSolver(constraints, items, values, iterCounter, wPoint([0] * constraints.getSize()),
                             forceUseLimits=False)

    solver.forceUseDpSolver = True
    solver.printInfo = printPct
    solver.printDpInfo = printPct
    solver.printSuperIncreasingInfo = True
    solver.doSolveSuperInc = doSolveSuperInc
    solver.doUseLimits = doUseLimits

    bestValue, bestSize, bestItems, bestValues = solver.solve()
    return bestValue, bestSize, bestItems, bestValues


def hybridKnapsackNd(constraints, items, values, iterCounter,
                     printPct=False,
                     doSolveSuperInc=True,
                     doUseLimits=True
                     ):
    solver = knapsackNSolver(constraints, items, values, iterCounter, wPoint([0] * constraints.getSize()),
                             forceUseLimits=False)

    solver.forceUseDpSolver = False
    solver.useParetoAsNGreedySolver = True
    solver.printInfo = printPct
    solver.printSuperIncreasingInfo = True
    solver.doSolveSuperInc = doSolveSuperInc
    solver.doUseLimits = doUseLimits

    bestValue, bestSize, bestItems, bestValues = solver.solve()
    return bestValue, bestSize, bestItems, bestValues


def partitionN(items, sizesOrPartitions, groupSize, iterCounter,
               optimizationLimit=-1,
               printPct=False
               ):
    solver = partitionSolver(items, sizesOrPartitions, groupSize, iterCounter, optimizationLimit)

    solver.printOptimizationInfo = True
    solver.printInfo = printPct
    solver.useHybridParetoGrouping = False

    quotients, reminder, optimizationCount = solver.solve()
    return quotients, reminder, optimizationCount


def hybridPartitionN(items, sizesOrPartitions, groupSize, iterCounter,
                     optimizationLimit=-1,
                     printPct=False
                     ):
    solver = partitionSolver(items, sizesOrPartitions, groupSize, iterCounter, optimizationLimit)

    solver.printOptimizationInfo = True
    solver.printInfo = printPct
    solver.useHybridParetoGrouping = True

    quotients, reminder, optimizationCount = solver.solve()
    return quotients, reminder, optimizationCount
