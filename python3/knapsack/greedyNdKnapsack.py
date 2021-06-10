"""
Copyright Jun 2021 Konstantin Briukhnov (kooltew at gmail.com) (@CostaBru). San-Francisco Bay Area.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from flags.flags import doUseLimits, doSolveSuperInc
from .knapsack import knapsackSolver
from .knapsackNd import knapsackNSolver

from .knapsackPareto import *

from collections import defaultdict
from collections import deque
from decimal import Decimal

import time
import math
import sys

from .paretoPoint import paretoPoint, paretoPoint1
from .wPoint import wPoint1


class greedyKnapsackNdSolver:

    def __init__(self, constraints, items, values, iterCounter, emptyPoint, forceUseLimits=False, forceUseDpSolver=False):
        self.constraints = constraints
        self.items = items
        self.values = values
        self.iterCounter = iterCounter
        self.forceUseLimits = forceUseLimits
        self.emptyPoint = emptyPoint
        self.size = constraints.getSize()
        self.useParetoGreedy = False
        self.totalPointCount = 0
        self.printDpInfo = False
        self.printGreedyInfo = False
        self.printSuperIncreasingInfo = False
        self.doSolveSuperInc = True
        self.canBackTraceWhenSizeReached = False
        self.useRatioSortForPareto = False

    def createNewPoint(self, tuples):
        return self.emptyPoint.createNew(tuples)

    def sortBoth(self, w, v, reverse=True):
        sorted_pairs = sorted(zip(w, v), reverse=reverse, key=lambda t: (t[0], t[1]))
        tuples = zip(*sorted_pairs)
        return [list(tuple) for tuple in tuples]

    def sortReverse3Both(self, w, v, x):
        sorted_pairs = sorted(zip(w, v, x), reverse=True, key=lambda t: (t[0], t[1]))
        tuples = zip(*sorted_pairs)
        return [list(tuple) for tuple in tuples]

    def solveByPareto(self, constraints, lessSizeItems, lessSizeValues, iterCounter):

        if self.printGreedyInfo:
            print(f"{constraints.getSize()}D  knapsack NON exact pareto solver: N {len(lessSizeItems)}")

        paretoSolver = knapsackParetoSolver(lessSizeItems, lessSizeValues, range(len(lessSizeValues)), constraints,
                                            paretoPoint(self.emptyPoint.getDimensions(), 0), self.emptyPoint, iterCounter)

        paretoSolver.printInfo = self.printDpInfo
        paretoSolver.canBackTraceWhenSizeReached = self.canBackTraceWhenSizeReached
        paretoSolver.useRatioSort = self.useRatioSortForPareto

        opt, optDims, optItems, optValues, optIndex = paretoSolver.solve()
        return opt, optDims, optItems, optValues

    def solveKnapsackNd(self, constraints, descNewDims, descNewVals, doSolveSuperInc, forceUseLimits, iterCounter):

        limitSolver = knapsackNSolver(constraints, descNewDims, descNewVals, iterCounter, self.emptyPoint, forceUseLimits=True, forceUseDpSolver=True)

        return limitSolver.solve()


    def solve(self):

        size = self.constraints.getSize()

        maxN = -sys.maxsize
        maxDimN = self.emptyPoint
        maxNItems = []
        maxNValues = []

        dimDescSortedItems = [None] * size
        dimStairSteps =      [None] * size
        optimizeCacheItems = [None] * size
        solvers =            [None] * size

        dimStairDownCursors =         [0] * size
        dimStairDownCursorStartings = [0] * size

        estimatedAttemptsCount = 0

        _, dimensionIndexes = self.sortBoth(self.constraints.getDimensions(), range(size), reverse=False)

        for dimensionIndex in range(size):
            dimOrderIndex = dimensionIndexes[dimensionIndex]

            descDim = [p.getDimension(dimOrderIndex) for p in self.items]
            descValues = self.values
            descIndex = list(range(len(self.values)))

            self.iterCounter[0] += (len(descDim) * math.log2(len(descDim)))

            dimDescSortedItems[dimensionIndex] = (descDim, descValues, descIndex)
            dimStairSteps[dimensionIndex] = descDim[-1]
            dimStairDownCursors[dimensionIndex] = self.constraints.getDimension(dimOrderIndex)
            dimStairDownCursorStartings[dimensionIndex] = self.constraints.getDimension(dimOrderIndex)
            optimizeCacheItems[dimensionIndex] = {}

            estimatedAttemptsCount += dimStairDownCursors[dimensionIndex] // dimStairSteps[dimensionIndex]

            solver = knapsackParetoSolver([wPoint1(item) for item in descDim],
                                          descValues,
                                          range(len(descValues)),
                                          wPoint1(self.constraints.getDimension(dimOrderIndex)),
                                          paretoPoint1(0, 0),
                                          wPoint1(0),
                                          self.iterCounter)

            solver.forceUsePareto = True
            solver.prepareSearchIndex = True

            solvers[dimensionIndex] = solver

        if self.printGreedyInfo:
            print(f"The NON exact {size}D greedyTopDown knapsack solver called for N = {len(self.items)}. Estimated attempts: {estimatedAttemptsCount}.")

        self.iterCounter[0] += size

        t0 = time.perf_counter()

        optimizeIterIndex = 0

        anyGreaterThanStep = True

        prevOptimizedIndexes = set()

        while anyGreaterThanStep:

            t1 = time.perf_counter()

            optimizedIndexes = set()

            for dimensionIndex in range(size):

                currentDimLimit = dimStairDownCursors[dimensionIndex]

                if currentDimLimit not in optimizeCacheItems[dimensionIndex]:

                    _, __, ___, ____, optIndex = solvers[dimensionIndex].solve(wPoint1(currentDimLimit))

                    dimIndex = dimDescSortedItems[dimensionIndex][2]

                    dimCacheItems = []

                    for oi in optIndex:
                        itemIndex = dimIndex[oi]

                        dimCacheItems.append(itemIndex)
                        optimizedIndexes.add(itemIndex)

                    self.iterCounter[0] += len(optIndex)

                    optimizeCacheItems[dimensionIndex][currentDimLimit] = dimCacheItems
                else:
                    optimizedIndexes.update(optimizeCacheItems[dimensionIndex][currentDimLimit])
                    self.iterCounter[0] += len(optimizeCacheItems[dimensionIndex])

            newData = []
            newValues = []

            optTuple = tuple(optimizedIndexes)

            if optTuple not in prevOptimizedIndexes:

                sumOfNewValues = 0

                for itemIndex in optimizedIndexes:

                    nDims = [0] * size

                    for dimensionIndex in range(size):
                        dimIndex = dimensionIndexes[dimensionIndex]
                        nDims[dimIndex] = self.items[itemIndex].getDimension(dimIndex)

                    newData.append(self.createNewPoint(nDims))
                    newValues.append(self.values[itemIndex])

                    sumOfNewValues += self.values[itemIndex]

                self.iterCounter[0] += len(optimizedIndexes) * size

                if sumOfNewValues > maxN:

                    descNewDims, descNewVals = self.sortBoth(newData, newValues)
                    self.iterCounter[0] += (len(descNewDims) * math.log2(len(descNewDims)))

                    optN, optDimN, optItemsN, optValuesN = self.solveKnapsackNd(self.constraints,
                                                                                descNewDims,
                                                                                descNewVals,
                                                                                doSolveSuperInc,
                                                                                self.forceUseLimits,
                                                                                self.iterCounter)

                    attemptTimeS = round(time.perf_counter() - t1, 4)

                    if maxN < optN:
                        maxN = optN
                        maxDimN = optDimN
                        maxNValues = optValuesN
                        maxNItems = optItemsN

                        if self.printGreedyInfo and optimizeIterIndex == 0:
                            estimatedMaxTime = estimatedAttemptsCount * Decimal(attemptTimeS)
                            print(
                                f"The NON exact {size}D greedyTopDown knapsack solver: estimated max time {estimatedMaxTime}.")

                        if self.printGreedyInfo:
                            print(
                                f"The NON exact {size}D greedyTopDown knapsack solver:  attempt {optimizeIterIndex}, some max value {maxN} has been found, time {attemptTimeS}, total time {round(time.perf_counter() - t0, 4)}, total iters {round(self.iterCounter[0])}.")

                    elif self.printGreedyInfo and attemptTimeS > 2:
                        print(
                            f"The NON exact {size}D greedyTopDown knapsack solver: attempt {optimizeIterIndex}, delta max {maxN - optN}, time {attemptTimeS}, total time {round(time.perf_counter() - t0, 4)}, total iters {round(self.iterCounter[0])}")

                    prevOptimizedIndexes.add(optTuple)
                elif self.printGreedyInfo:
                    print(
                        f"The NON exact {size}D greedyTopDown knapsack solver:  attempt {optimizeIterIndex} was skipped due to less values. Exiting.")
                    break
            elif self.printGreedyInfo:
                print(f"The NON exact {size}D greedyTopDown knapsack solver: attempt {optimizeIterIndex} was skipped.")

            decIndex = (optimizeIterIndex) % size

            if dimStairDownCursors[decIndex] >= dimStairSteps[decIndex]:
                dimStairDownCursors[decIndex] -= dimStairSteps[decIndex]

            for dimensionIndex in range(size):
                anyGreaterThanStep = dimStairDownCursors[dimensionIndex] >= dimStairSteps[dimensionIndex]
                if anyGreaterThanStep:
                    break

            optimizeIterIndex += 1

        return maxN, maxDimN, maxNItems, maxNValues