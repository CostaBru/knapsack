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

from flags.flags import doUseLimits, doSolveSuperInc
from .knapsack import knapsackSolver

from .paretoKnapsack import *

from collections import defaultdict
from collections import deque
from decimal import Decimal

import time
import math
import sys


class knapsackNSolver:

    def __init__(self, constraints, items, values, O, emptyPoint, forceUseLimits=False, forceUseDpSolver=False):
        self.constraints = constraints
        self.items = items
        self.values = values
        self.O = O
        self.forceUseLimits = forceUseLimits
        self.forceUseDpSolver = forceUseDpSolver
        self.emptyPoint = emptyPoint
        self.worstCaseExpLimit = 25
        self.size = constraints.getSize()
        # NON exact pareto greedy works much faster than greedy optimizer but gives less optimal result
        self.useParetoGreedy = False
        # If true uses pareto greedy as N solver for merging different dimension optimization else uses DP solver which gives optmal but works much slowly.
        self.useParetoAsNGreedySolver = True
        self.DP = None
        # inner stat for DP solver
        self.skippedPointsByMap = 0
        self.skippedPointsByLimits = 0
        self.skippedPointsBySize = 0
        self.totalPointCount = 0
        self.printDpInfo = False
        self.printGreedyInfo = False
        self.printSuperIncreasingInfo = False
        self.doSolveSuperInc = True
        self.doUseLimits = True
        self.canBackTraceWhenSizeReached = False
        self.useRatioSortForPareto = False

    def createNewPoint(self, tuples):
        return self.emptyPoint.createNew(tuples)

    def preProcess(self, constraints, items, values, forceUseLimits, O):

        count = len(items)

        itemSum1, itemSum2, lessCountSum = self.emptyPoint, self.emptyPoint, self.emptyPoint
        valuesSum1, valuesSum2, lessCountValuesSum = 0, 0, 0

        lessSizeItems, lessSizeValues = [], []

        partialSums1, superIncreasingItems1 = [], [False]
        partialSums2, superIncreasingItems2 = [], [False]

        isSuperIncreasing1, isSuperIncreasing2 = True, True
        isSuperIncreasingValues1, isSuperIncreasingValues2 = True, True
        allValuesEqual, allValuesEqualToConstraints = True, True
        allDesc, allAsc, allDescValues, allAscValues = True, True, True, True

        canUsePartialSums = False

        lessCount = 0

        if count > 0:

            prevItem1 = items[-1]
            prevValue1 = values[-1]

            for i in range(0, count):

                item2 = items[i]
                itemValue2 = values[i]

                iBack = count - i - 1
                item1 = items[iBack]
                itemValue1 = values[iBack]
                superIncreasingItem1, superIncreasingItem2 = False, False

                if item1 <= constraints:

                    if item1 < itemSum1:
                        isSuperIncreasing1 = False
                    else:
                        superIncreasingItem1 = True

                    if itemValue1 < valuesSum1:
                        isSuperIncreasingValues1 = False
                        superIncreasingItem1 = False

                if item2 <= constraints:

                    if item2 < itemSum2:
                        isSuperIncreasing2 = False
                    else:
                        superIncreasingItem2 = True

                    if itemValue2 < valuesSum2:
                        isSuperIncreasingValues2 = False
                        superIncreasingItem2 = False

                if allValuesEqual and prevValue1 != itemValue2:
                    allValuesEqual = False

                if allValuesEqualToConstraints and not item2.firstDimensionEqual(itemValue2):
                    allValuesEqualToConstraints = False

                itemSum1 += item1
                itemSum2 += item2

                partialSums1.append(itemSum2)
                partialSums2.append(itemSum1)

                if allDesc:
                    if not prevItem1 <= item1:
                        allDesc = False

                if allAsc:
                    if prevItem1 < item1:
                        allAsc = False

                if allDescValues:
                    if not prevValue1 <= itemValue1:
                        allDescValues = False

                if allAscValues:
                    if prevValue1 < itemValue1:
                        allAscValues = False

                if i > 0:
                    superIncreasingItems1.append(superIncreasingItem1)
                    superIncreasingItems2.append(superIncreasingItem2)

                if item2 <= constraints:
                    lessSizeItems.append(item2)
                    lessSizeValues.append(itemValue2)
                    lessCountValuesSum += itemValue2

                    lessCountSum += item2
                    lessCount += 1

                prevItem1 = item1
                prevValue1 = itemValue1

            canUsePartialSums = allValuesEqual or allValuesEqualToConstraints or (
                        isSuperIncreasingValues1 and allDescValues) or (isSuperIncreasingValues2 and allAscValues)

            partialSums = []
            superIncreasingItems = []
            isSuperIncreasing = False
            itemSum = itemSum2

            if allAsc and canUsePartialSums:
                partialSums = partialSums2
                superIncreasingItems = superIncreasingItems2
                isSuperIncreasing = isSuperIncreasing2
                itemSum = itemSum2
            elif allDesc and canUsePartialSums or forceUseLimits:
                partialSums = partialSums1
                superIncreasingItems = superIncreasingItems1
                isSuperIncreasing = isSuperIncreasing1
                itemSum = itemSum1

                partialSums.reverse()
                superIncreasingItems.reverse()
            else:
                if allAsc and allAscValues:
                    itemSum = itemSum2
                    superIncreasingItems = superIncreasingItems2
                    canUsePartialSums = True
                elif allDesc and allDescValues:
                    itemSum = itemSum1
                    superIncreasingItems = superIncreasingItems1
                    canUsePartialSums = True
                    partialSums.reverse()
                    superIncreasingItems.reverse()
                else:
                    superIncreasingItems = [False] * lessCount
                    partialSums = [None] * lessCount
                    canUsePartialSums = False
        else:
            partialSums = []
            superIncreasingItems = []
            isSuperIncreasing = False
            itemSum = self.emptyPoint
            canUsePartialSums = False

        O[0] += count * constraints.getSize()
        updatedConstraint = constraints.adjustMin(itemSum)
        return updatedConstraint, lessCount, lessSizeItems, lessSizeValues, itemSum, lessCountSum, partialSums, isSuperIncreasing, superIncreasingItems, allAsc, allDesc, canUsePartialSums

    def checkCornerCases(self, constraints, lessSizeItems, lessSizeValues, lessCountSum, itemSum):

        if lessCountSum == self.emptyPoint:
            return 0, self.emptyPoint, [], []

        if lessCountSum <= constraints:
            return sum(lessSizeValues), lessCountSum, lessSizeItems, lessSizeValues

        if itemSum <= constraints:
            return sum(lessSizeValues), itemSum, lessSizeItems, lessSizeValues

        return None

    def yieldOrPushBack(self, circularPointQueue, newPoint, greaterQu, O):
        if len(circularPointQueue) > 0:
            peek = circularPointQueue[0]

            if newPoint < peek:
                yield newPoint
                circularPointQueue.append(newPoint)
            else:

                O[0] += 1

                if len(greaterQu) > 0 and newPoint < greaterQu[0]:
                    greaterQu.insert(0, newPoint)
                else:
                    greaterQu.append(newPoint)
        else:
            yield newPoint
            circularPointQueue.append(newPoint)

    def getPoints(self, itemDimensions, constraintPoint, circularPointQueue, halfConstraint, itemLimit, oldPointLimit,
                  newPointLimit, prevCyclePointCount, uniquePointSet, skipCount, O):

        # merges ordered visited points with new points with keeping order in O(N) using single circular queue.
        # each getPoints method call starts fetching visited points from qu start, pops visited point and pushes new point and visited to the end of qu in ASC order.
        # we skip new point if it in list already
        # skips points if they will not contribute to optimal solution (in case of desc flow and (equal values or values equal to first dimension))

        greaterQu = deque()

        if not itemDimensions in uniquePointSet:

            for p in self.yieldOrPushBack(circularPointQueue, itemDimensions, greaterQu, O):
                yield p

        else:
            self.skippedPointsByMap += skipCount

        for i in range(prevCyclePointCount):

            oldPoint = circularPointQueue.popleft()

            while len(greaterQu) > 0 and greaterQu[0] < oldPoint:
                quPoint = greaterQu.popleft()

                yield quPoint
                circularPointQueue.append(quPoint)

            if not oldPointLimit or not oldPoint <= oldPointLimit:
                for p in self.yieldOrPushBack(circularPointQueue, oldPoint, greaterQu, O):
                    yield p

            else:
                self.skippedPointsByLimits += skipCount

            newPoint = oldPoint + itemDimensions

            if newPointLimit and newPoint < newPointLimit:
                self.skippedPointsByLimits += skipCount
                continue

            if newPoint <= constraintPoint:

                if not newPoint in uniquePointSet:

                    for p in self.yieldOrPushBack(circularPointQueue, newPoint, greaterQu, O):
                        yield p

                else:
                    self.skippedPointsByMap += skipCount
            else:
                self.skippedPointsBySize += skipCount

        while len(greaterQu) > 0:
            quPoint = greaterQu.popleft()

            yield quPoint
            circularPointQueue.append(quPoint)

    def getValue(self, p, prevDP):

        if p in prevDP:
            cur = prevDP[p]
            return cur[0], cur[1]

        return 0, self.emptyPoint

    def getPossibleValue(self, point, itemValue, itemDims, dp, O):

        if point in dp:
            cur = dp[point]
            O[0] += self.size
            return cur[0] + itemValue, cur[1] + itemDims

        if point < self.emptyPoint:
            return None, self.emptyPoint

        return itemValue, itemDims

    def setValue(self, curDP, p, curVal, curDimensions, O):
        curDP[p] = (curVal, curDimensions)
        O[0] += self.size

    def backTraceItems(self, DP, resultI, resultP, items, values, allAsc, O):
        res = DP[resultI][resultP][0]
        optItems, optValues = [], []
        point = resultP
        optDims = self.emptyPoint
        opt = 0

        count = len(items)

        self.totalPointCount += len(DP[resultI])

        if self.printDpInfo:
            print(
                f"Skipped points by MAP: {self.skippedPointsByMap}, by LIMITS: {self.skippedPointsByLimits}; by SIZE: {self.skippedPointsBySize};  Max points: {(2 ** len(items)) if len(items) < 15 else -1}; Total points: {self.totalPointCount};")

        for i in range(resultI, 0, -1):

            O[0] += 1

            if res <= 0:
                break

            dpw = DP[i - 1]

            skip = False

            if point in dpw:
                skip = res == dpw[point][0]

            if not skip:
                itemIndex = self.getItemIndex(count, i, allAsc)
                item, itemValue = items[itemIndex], values[itemIndex]

                optItems.append(item.getDimensions())
                optValues.append(itemValue)

                res -= itemValue
                point -= item
                opt += itemValue
                optDims += item

        return opt, optDims, optItems, optValues

    def createDP(self, count):
        self.DP = [None] * (count + 1)
        self.DP[0] = defaultdict()
        return self.DP

    def solveSuperIncreasing(self, size, items, values, count, allAsc, O):

        def indexLargestLessThanDesc(items, item, lo, hi, O):

            if item == self.emptyPoint:
                return None

            cnt = len(items)

            while lo <= hi:
                O[0] += 1
                mid = (lo + hi) // 2

                val = items[mid]

                if item == val:
                    return mid

                if val > item:
                    lo = mid + 1
                else:
                    hi = mid - 1

            if lo < cnt and item >= items[lo]:
                return lo
            else:
                return None

        def indexLargestLessThanAsc(items, item, lo, hi, O):

            if item == self.emptyPoint:
                return None

            while lo <= hi:
                O[0] += 1
                mid = (lo + hi) // 2

                val = items[mid]

                if item == val:
                    return mid

                if val < item:
                    lo = mid + 1
                else:
                    hi = mid - 1

            if hi >= 0 and item >= items[hi]:
                return hi
            else:
                return None

        binSearch = indexLargestLessThanAsc if allAsc else indexLargestLessThanDesc

        starting = 1
        resultItems = []
        resultValues = []
        resultSum = 0
        resultItemSum = self.emptyPoint
        index = binSearch(items, size, starting - 1, count - 1, O)

        while index is not None:
            item = items[index]
            value = values[index]
            resultItems.append(item)
            resultValues.append(value)
            resultSum += value
            resultItemSum += item

            if allAsc:
                index = binSearch(items, size - resultItemSum, starting - 1, index - 1, O)
            else:
                index = binSearch(items, size - resultItemSum, index + 1, count - 1, O)

            O[0] += 1

        if self.printSuperIncreasingInfo:
            print(f"Superincreasing {size.getSize()}D solver called for size {size} and count {count}.  ASC={allAsc}")

        return resultSum, resultItemSum, resultItems, resultValues

    def getLimits(self, constraints, itemIndex, items, partialSums, superIncreasingItems, canUsePartialSums):

        if not self.doUseLimits or not canUsePartialSums:
            return None, None, None, 0

        skipCount = 2 ** (len(items) - itemIndex + 1) if self.printDpInfo else 0

        partSumForItem = partialSums[itemIndex]
        superIncreasingItem = superIncreasingItems[itemIndex]

        newPointLimit = constraints - partSumForItem if partSumForItem else None
        oldPointLimit = newPointLimit

        if self.doSolveSuperInc and newPointLimit and superIncreasingItem:
            oldPointLimit = newPointLimit + items[itemIndex]

        return partSumForItem, oldPointLimit, newPointLimit, skipCount

    def getItemIndex(self, count, i, allAsc):
        return count - i if allAsc else i - 1

    def solveByDynamicPrograming(self, constraints, count, lessSizeItems, lessSizeValues, partialSums,
                                 superIncreasingItems, allAsc, allDesc, forceUseLimits, canUsePartialSums, O):

        DP = self.createDP(count)

        resultI, resultP = 1, self.emptyPoint

        circularPointQueue = deque()

        maxValue, prevPointCount, newPointCount = -sys.maxsize, 0, 0

        halfConstraint = constraints.divideBy(2)

        if self.printDpInfo:
            worstCase = not allAsc and not allDesc and not canUsePartialSums
            print(
                f"{constraints.getSize()}D knapsack: N={count}, Use limits={doUseLimits}, allAsc={allAsc}, allDesc={allDesc}, forceUseLimits={forceUseLimits}, worstCaseExpLimit={self.worstCaseExpLimit}, canUsePartialSums={canUsePartialSums}, worstCase={worstCase}")

        for i in range(1, count + 1):

            itemIndex = self.getItemIndex(count, i, allAsc)

            DP[i] = defaultdict()

            itemValue, item = lessSizeValues[itemIndex], lessSizeItems[itemIndex]
            prevDP, curDP = DP[i - 1], DP[i]

            prevPointCount, newPointCount = newPointCount, prevPointCount
            newPointCount = 0

            self.totalPointCount += prevPointCount

            itemLimit, oldPointLimit, newPointLimit, skipCount = self.getLimits(constraints, itemIndex, lessSizeItems,
                                                                                partialSums, superIncreasingItems,
                                                                                canUsePartialSums)

            for p in self.getPoints(item, constraints, circularPointQueue, halfConstraint, itemLimit, oldPointLimit,
                                    newPointLimit, prevPointCount, prevDP, skipCount, O):

                curValue, curDim = self.getValue(p, prevDP)
                posblValue, posblDim = self.getPossibleValue(p - item, itemValue, item, prevDP, O)

                if posblValue and curValue <= posblValue and posblDim <= constraints:
                    curValue = posblValue
                    curDim = posblDim

                self.setValue(curDP, p, curValue, curDim, O)

                if maxValue <= curValue:
                    resultP = p
                    resultI = i
                    maxValue = curValue

                if self.canBackTraceWhenSizeReached and curDim == constraints:
                    return self.backTraceItems(DP, resultI, resultP, lessSizeItems, lessSizeValues, allAsc, O)

                newPointCount += 1

            if self.printDpInfo:
                print(f"| {i - 1} | {prevPointCount} | {round(O[0])} |")

        return self.backTraceItems(DP, resultI, resultP, lessSizeItems, lessSizeValues, allAsc, O)

    def solveByGreedyTopDown(self, constraints, points, values, doSolveSuperInc, forceUseLimits, O):

        def sortBoth(w, v, reverse=True):
            sorted_pairs = sorted(zip(w, v), reverse=reverse, key=lambda t: (t[0], t[1]))
            tuples = zip(*sorted_pairs)
            return [list(tuple) for tuple in tuples]

        def sortReverse3Both(w, v, x):
            sorted_pairs = sorted(zip(w, v, x), reverse=True, key=lambda t: (t[0], t[1]))
            tuples = zip(*sorted_pairs)
            return [list(tuple) for tuple in tuples]

        def solveKnapsackNd(constraints, descNewDims, descNewVals, doSolveSuperInc, forceUseLimits, O):

            constraints, count, lessSizeItems, lessSizeValues, itemSum, lessCountSum, partialSums, superIncreasing, superIncreasingItems, allAsc, allDesc, canUsePartialSums = self.preProcess(
                constraints, descNewDims, descNewVals, forceUseLimits, O)

            cornerCasesCheck = self.checkCornerCases(constraints, lessSizeItems, lessSizeValues, lessCountSum, itemSum)

            if cornerCasesCheck:
                return cornerCasesCheck

            if doSolveSuperInc and superIncreasing:
                return self.solveSuperIncreasing(constraints, lessSizeItems, lessSizeValues, count, allAsc, O)

            if allAsc:
                lessSizeItems = list(reversed(lessSizeItems))
                lessSizeValues = list(reversed(lessSizeValues))
                O[0] += len(lessSizeItems) * 2

            if self.useParetoAsNGreedySolver:
                return self.solveByPareto(constraints, lessSizeItems, lessSizeValues, O)

            return self.solveByDynamicPrograming(constraints, count, lessSizeItems, lessSizeValues, partialSums,
                                                 superIncreasingItems, allAsc, allDesc, forceUseLimits,
                                                 canUsePartialSums, O)

        size = constraints.getSize()

        maxN = -sys.maxsize
        maxDimN = self.emptyPoint
        maxNItems = []
        maxNValues = []

        dimDescSortedItems = [None] * size
        dimStairSteps = [None] * size
        dimStairDownCursors = [0] * size
        dimStairDownCursorStartings = [0] * size
        optimizeCacheItems = [None] * size

        estimatedAttemptsCount = 0

        _, dimensionIndexes = sortBoth(constraints.getDimensions(), range(size), reverse=False)

        for dimensionIndex in range(size):
            dimOrderIndex = dimensionIndexes[dimensionIndex]

            dim = [p.getDimension(dimOrderIndex) for p in points]

            descDim, descValues, descIndex = sortReverse3Both(dim, values, list(range(len(values))))
            O[0] += (len(descDim) * math.log2(len(descDim)))

            dimDescSortedItems[dimensionIndex] = (descDim, descValues, descIndex)
            dimStairSteps[dimensionIndex] = descDim[-1]
            dimStairDownCursors[dimensionIndex] = constraints.getDimension(dimOrderIndex)
            dimStairDownCursorStartings[dimensionIndex] = constraints.getDimension(dimOrderIndex)
            optimizeCacheItems[dimensionIndex] = {}

            estimatedAttemptsCount += dimStairDownCursors[dimensionIndex] // dimStairSteps[dimensionIndex]

        if self.printGreedyInfo:
            print(
                f"The NON exact {size}D greedyTopDown knapsack solver called for N = {len(points)}. Estimated attempts: {estimatedAttemptsCount}.")

        O[0] += size

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

                    dimItem = dimDescSortedItems[dimensionIndex]

                    dimItems = dimItem[0]
                    dimValues = dimItem[1]
                    dimIndex = dimItem[2]

                    _, __, ___, ____, optIndex = knapsackSolver(currentDimLimit, dimItems, dimValues, O,
                                                                forceUseLimits).solve()

                    dimCacheItems = []

                    for oi in optIndex:
                        itemIndex = dimIndex[oi]

                        dimCacheItems.append(itemIndex)
                        optimizedIndexes.add(itemIndex)

                    O[0] += len(optIndex)

                    optimizeCacheItems[dimensionIndex][currentDimLimit] = dimCacheItems
                else:
                    optimizedIndexes.update(optimizeCacheItems[dimensionIndex][currentDimLimit])
                    O[0] += len(optimizeCacheItems[dimensionIndex])

            newData = []
            newValues = []

            optTuple = tuple(optimizedIndexes)

            if optTuple not in prevOptimizedIndexes:

                sumOfNewValues = 0

                for itemIndex in optimizedIndexes:

                    nDims = [0] * size

                    for dimensionIndex in range(size):
                        dimIndex = dimensionIndexes[dimensionIndex]
                        nDims[dimIndex] = points[itemIndex].getDimension(dimIndex)

                    newData.append(self.createNewPoint(nDims))
                    newValues.append(values[itemIndex])

                    sumOfNewValues += values[itemIndex]

                O[0] += len(optimizedIndexes) * size

                if sumOfNewValues > maxN:

                    descNewDims, descNewVals = sortBoth(newData, newValues)
                    O[0] += (len(descNewDims) * math.log2(len(descNewDims)))

                    optN, optDimN, optItemsN, optValuesN = solveKnapsackNd(constraints, descNewDims, descNewVals,
                                                                           doSolveSuperInc, forceUseLimits, O)

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
                                f"The NON exact {size}D greedyTopDown knapsack solver:  attempt {optimizeIterIndex}, some max value {maxN} has been found, time {attemptTimeS}, total time {round(time.perf_counter() - t0, 4)}, total iters {round(O[0])}.")

                    elif self.printGreedyInfo and attemptTimeS > 2:
                        print(
                            f"The NON exact {size}D greedyTopDown knapsack solver: attempt {optimizeIterIndex}, delta max {maxN - optN}, time {attemptTimeS}, total time {round(time.perf_counter() - t0, 4)}, total iters {round(O[0])}")

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

    def solveByPareto(self, constraints, lessSizeItems, lessSizeValues, O):

        if self.printGreedyInfo:
            print(f"{constraints.getSize()}D  knapsack NON exact pareto solver: N {len(lessSizeItems)}")

        paretoSolver = knapsackParetoSolver(lessSizeItems, lessSizeValues, range(len(lessSizeValues)), constraints,
                                            paretoPoint(self.emptyPoint.getDimensions(), 0), self.emptyPoint, O)

        paretoSolver.printInfo = self.printDpInfo
        paretoSolver.canBackTraceWhenSizeReached = self.canBackTraceWhenSizeReached
        paretoSolver.useRatioSort = self.useRatioSortForPareto

        opt, optDims, optItems, optValues, optIndex = paretoSolver.solve()
        return opt, optDims, optItems, optValues

    def solve(self):

        constraints, items, values, forceUseLimits, O = self.constraints, self.items, self.values, self.forceUseLimits, self.O

        constraints, count, lessSizeItems, lessSizeValues, itemSum, lessCountSum, partialSums, superIncreasing, superIncreasingItems, allAsc, allDesc, canUsePartialSums = self.preProcess(
            constraints, items, values, forceUseLimits, O)

        cornerCasesCheck = self.checkCornerCases(constraints, lessSizeItems, lessSizeValues, lessCountSum, itemSum)

        if cornerCasesCheck:
            return cornerCasesCheck

        if self.doSolveSuperInc and superIncreasing:
            return self.solveSuperIncreasing(constraints, lessSizeItems, lessSizeValues, count, allAsc, O)

        if len(items) <= self.worstCaseExpLimit or (
                (allAsc or allDesc) and canUsePartialSums) or self.forceUseDpSolver or self.forceUseLimits:
            return self.solveByDynamicPrograming(constraints, count, lessSizeItems, lessSizeValues, partialSums,
                                                 superIncreasingItems, allAsc, allDesc, forceUseLimits,
                                                 canUsePartialSums, O)

        if self.useParetoGreedy:
            return self.solveByPareto(constraints, lessSizeItems, lessSizeValues, O)

        return self.solveByGreedyTopDown(constraints, lessSizeItems, lessSizeValues, doSolveSuperInc, False, O)
