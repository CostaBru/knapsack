from knapsack.knapsack import knapsackSolver, knapsackParetoSolver
from knapsack.knapsackNd import knapsackNSolver
from knapsack.paretoPoint import paretoPoint1, paretoPoint0
from knapsack.subsKnapsack import subsetSumKnapsackSolver
from knapsack.wPoint import wPoint1, wPoint
from partition.partitionN import partitionSolver


def subsKnapsack(size, items, O, printPct=False, doSolveSuperInc=True, doUseLimits=True):
    solver = subsetSumKnapsackSolver(size, items, O, forceUseLimits=False)

    solver.printInfo = printPct
    solver.printSuperIncreasingInfo = True
    solver.doSolveSuperInc = doSolveSuperInc
    solver.doUseLimits = doUseLimits

    bestValue, bestItems = solver.solve()
    return bestValue, bestItems


def knapsack(size, items, values, O, printPct=False, doSolveSuperInc=True, doUseLimits=True):
    solver = knapsackSolver(size, items, values, O, forceUseLimits=False)

    solver.forceUseDpSolver = True
    solver.printInfo = printPct
    solver.printSuperIncreasingInfo = True
    solver.doSolveSuperInc = doSolveSuperInc
    solver.doUseLimits = doUseLimits

    bestValue, bestSize, bestItems, bestValues, bestIndexes = solver.solve()
    return bestValue, bestSize, bestItems, bestValues


def hybridKnapsack(size, items, values, O, printPct=False, doSolveSuperInc=True, doUseLimits=True):
    solver = knapsackSolver(size, items, values, O, forceUseLimits=False)

    solver.forceUseDpSolver = False
    solver.printInfo = printPct
    solver.printSuperIncreasingInfo = True
    solver.doSolveSuperInc = doSolveSuperInc
    solver.doUseLimits = doUseLimits

    bestValue, bestSize, bestItems, bestValues, bestIndexes = solver.solve()
    return bestValue, bestSize, bestItems, bestValues


def paretoKnapsack(size, items, values, O,
                   useRatioSort=False,
                   printPct=False,
                   doSolveSuperInc=True,
                   doUseLimits=True):
    paretoItems = [wPoint1(item) for item in items]

    solver = knapsackParetoSolver(paretoItems, values, range(len(values)), wPoint1(size), paretoPoint1(0, 0),
                                  wPoint1(0), O)

    solver.printInfo = printPct
    solver.forceUsePareto = True
    solver.useRatioSort = useRatioSort

    bestValue, bestSize, bestItems, bestValues, bestIndexes = solver.solve()
    return bestValue, bestSize.getDimension(0), bestItems, bestValues


def hybridParetoKnapsack(size, items, values, O,
                         useRatioSort=False,
                         printPct=False,
                         doSolveSuperInc=True,
                         doUseLimits=True,
                         forceUsePareto=False
                         ):
    paretoItems = [wPoint1(item) for item in items]

    solver = knapsackParetoSolver(paretoItems, values, range(len(values)), wPoint1(size), paretoPoint1(0, 0),
                                  wPoint1(0), O)

    solver.printInfo = printPct
    solver.forceUsePareto = forceUsePareto
    solver.useRatioSort = useRatioSort

    bestValue, bestSize, bestItems, bestValues, bestIndexes = solver.solve()
    return bestValue, bestSize.getDimension(0), bestItems, bestValues


def subsParetoKnapsack(size, items, O,
                       printPct=False,
                       doSolveSuperInc=True,
                       doUseLimits=True):
    paretoItems = [wPoint1(item) for item in items]

    O[0] += len(paretoItems)

    solver = knapsackParetoSolver(paretoItems, items, range(len(items)), wPoint1(size), paretoPoint0(0), wPoint1(0),
                                  O)

    solver.printInfo = printPct
    solver.doUseLimits = doUseLimits
    solver.canBackTraceWhenSizeReached = True

    bestValue, bestSize, bestItems, bestValues, bestIndexes = solver.solve()
    return bestValue, bestItems


def knapsackNd(constraints, items, values, O,
               printPct=False,
               doSolveSuperInc=True,
               doUseLimits=True
               ):
    solver = knapsackNSolver(constraints, items, values, O, wPoint([0] * constraints.getSize()),
                             forceUseLimits=False)

    solver.forceUseDpSolver = True
    solver.printInfo = printPct
    solver.printDpInfo = printPct
    solver.printSuperIncreasingInfo = True
    solver.doSolveSuperInc = doSolveSuperInc
    solver.doUseLimits = doUseLimits

    bestValue, bestSize, bestItems, bestValues = solver.solve()
    return bestValue, bestSize, bestItems, bestValues


def hybridKnapsackNd(constraints, items, values, O,
                     printPct=False,
                     doSolveSuperInc=True,
                     doUseLimits=True
                     ):
    solver = knapsackNSolver(constraints, items, values, O, wPoint([0] * constraints.getSize()),
                             forceUseLimits=False)

    solver.forceUseDpSolver = False
    solver.useParetoAsNGreedySolver = True
    solver.printInfo = printPct
    solver.printSuperIncreasingInfo = True
    solver.doSolveSuperInc = doSolveSuperInc
    solver.doUseLimits = doUseLimits

    bestValue, bestSize, bestItems, bestValues = solver.solve()
    return bestValue, bestSize, bestItems, bestValues


def partitionN(items, sizesOrPartitions, groupSize, O,
               optimizationLimit=-1,
               printPct=False
               ):
    solver = partitionSolver(items, sizesOrPartitions, groupSize, O, optimizationLimit)

    solver.printOptimizationInfo = True
    solver.printInfo = printPct
    solver.useHybridParetoGrouping = False

    quotients, reminder, optimizationCount = solver.solve()
    return quotients, reminder, optimizationCount


def hybridPartitionN(items, sizesOrPartitions, groupSize, O,
                     optimizationLimit=-1,
                     printPct=False
                     ):
    solver = partitionSolver(items, sizesOrPartitions, groupSize, O, optimizationLimit)

    solver.printOptimizationInfo = True
    solver.printInfo = printPct
    solver.useHybridParetoGrouping = True

    quotients, reminder, optimizationCount = solver.solve()
    return quotients, reminder, optimizationCount
