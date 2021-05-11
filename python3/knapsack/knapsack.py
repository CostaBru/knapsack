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

from flags.flags import doUseLimits

from .knapsackPareto import *
from .paretoPoint import paretoPoint1
from .wPoint import *

from collections import defaultdict
from collections import deque
from decimal import Decimal
from typing import List

import datetime
import random
import time
import math
import csv
import sys
import os


class knapsackSolver:

    def __init__(self, size, weights, values, iterCounter, forceUseLimits=False):
        self.size = size
        self.weights = weights
        self.values = values
        self.iterCounter = iterCounter
        self.forceUseLimits = forceUseLimits
        self.forceUseDpSolver = False
        self.DP = None
        # inner stat
        self.skippedPointsByMap = 0
        self.skippedPointsByLimits = 0
        self.skippedPointsBySize = 0
        self.totalPointCount = 0
        self.printInfo = False
        self.printSuperIncreasingInfo = False
        self.doSolveSuperInc = True
        self.doUseLimits = True
        self.canBackTraceWhenSizeReached = False

    def preProcess(self, constraints, items, values, forceUseLimits, iterCounter):

        count = len(items)
        itemSum1, itemSum2, lessCountSum = 0, 0, 0
        valuesSum1, valuesSum2, lessCountValuesSum = 0, 0, 0

        lessSizeItems, lessSizeValues, lessSizeItemsIndex = [], [], []

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

                if allValuesEqualToConstraints and item2 != itemValue2:
                    allValuesEqualToConstraints = False

                itemSum1 += item1
                itemSum2 += item2

                valuesSum1 += itemValue1
                valuesSum2 += itemValue2

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
                    superIncreasingItems1.append(superIncreasingItem2)
                    superIncreasingItems2.append(superIncreasingItem1)

                if item2 <= constraints:
                    lessSizeItems.append(item2)
                    lessSizeValues.append(itemValue2)
                    lessSizeItemsIndex.append(i)
                    lessCountValuesSum += itemValue2
                    lessCountSum += item2
                    lessCount += 1

                prevItem1 = item1
                prevValue1 = itemValue1

            partialSums = []
            superIncreasingItems = []
            isSuperIncreasing = False
            itemSum = itemSum2

            canUsePartialSums = allValuesEqual or allValuesEqualToConstraints or (
                        isSuperIncreasingValues1 and allDescValues) or (isSuperIncreasingValues2 and allAscValues)

            if allAsc and canUsePartialSums or forceUseLimits:
                partialSums = partialSums2
                superIncreasingItems = superIncreasingItems2
                isSuperIncreasing = isSuperIncreasing2
                itemSum = itemSum2
            elif allDesc and canUsePartialSums:
                partialSums = partialSums1
                superIncreasingItems = superIncreasingItems1
                isSuperIncreasing = isSuperIncreasing1
                itemSum = itemSum1

                partialSums.reverse()
                superIncreasingItems.reverse()
            else:
                if allAsc and allAscValues:
                    itemSum = itemSum2
                    partialSums = partialSums2
                    superIncreasingItems = superIncreasingItems2
                    canUsePartialSums = True
                elif allDesc and allDescValues:
                    itemSum = itemSum1
                    partialSums = partialSums1
                    superIncreasingItems = superIncreasingItems1
                    canUsePartialSums = True
                    partialSums.reverse()
                    superIncreasingItems.reverse()
                else:
                    superIncreasingItems = [False] * lessCount
                    partialSums = [sys.maxsize] * lessCount
                    canUsePartialSums = False
        else:
            partialSums = []
            superIncreasingItems = []
            isSuperIncreasing = False
            itemSum = itemSum2

        constraints = min(itemSum, constraints)

        iterCounter[0] += count
        return constraints, lessCount, lessSizeItems, lessSizeValues, lessSizeItemsIndex, itemSum, lessCountSum, lessCountValuesSum, partialSums, isSuperIncreasing, superIncreasingItems, allAsc, allDesc, canUsePartialSums

    def checkCornerCases(self, size, lessSizeItems, lessSizeValues, lessSizeItemsIndex, lessCountSum, itemSum,
                         lessCountValuesSum):

        if lessCountSum == 0:
            return 0, 0, [], [], []

        if lessCountSum <= size:
            return lessCountValuesSum, lessCountSum, lessSizeItems, lessSizeValues, lessSizeItemsIndex

        if itemSum <= size:
            return lessCountValuesSum, itemSum, lessSizeItems, lessSizeValues, lessSizeItemsIndex

        return None

    def yieldOrPushBack(self, circularPointQueue, newPoint, greaterQu, iterCounter):
        if len(circularPointQueue) > 0:
            peek = circularPointQueue[0]

            if newPoint < peek:
                yield newPoint
                circularPointQueue.append(newPoint)
            else:

                iterCounter[0] += 1

                if len(greaterQu) > 0 and newPoint < greaterQu[0]:
                    greaterQu.insert(0, newPoint)
                else:
                    greaterQu.append(newPoint)
        else:
            yield newPoint
            circularPointQueue.append(newPoint)

    def getPoints(self, itemWeight, size, circularPointQueue, itemLimit, oldPointLimit, newPointLimit,
                  prevCyclePointCount, uniquePointSet, skipCount, canUseLimits, iterCounter):

        # merges ordered visited points with new points with keeping order in iterCounter(N) using single circular queue.
        # each getPoints method call starts fetching visited points from qu start, pops visited point and pushes new point and visited to the end of qu in ASC order.
        # we skip new point if it in list already

        skipLimitCheck = not canUseLimits

        useItemItself = skipLimitCheck or itemLimit >= size // 2

        greaterQu = deque()

        if useItemItself and itemWeight not in uniquePointSet:
            for p in self.yieldOrPushBack(circularPointQueue, itemWeight, greaterQu, iterCounter):
                yield p
        else:
            if useItemItself:
                self.skippedPointsByMap += skipCount
            else:
                self.skippedPointsByLimits += skipCount

        for i in range(prevCyclePointCount):

            oldPoint = circularPointQueue.popleft()

            while len(greaterQu) > 0 and greaterQu[0] < oldPoint:
                quPoint = greaterQu.popleft()

                yield quPoint
                circularPointQueue.append(quPoint)

            if skipLimitCheck or oldPoint >= oldPointLimit:

                for p in self.yieldOrPushBack(circularPointQueue, oldPoint, greaterQu, iterCounter):
                    yield p

            else:
                self.skippedPointsByLimits += skipCount

            newPoint = oldPoint + itemWeight

            if canUseLimits and newPoint < newPointLimit:
                self.skippedPointsByLimits += skipCount
                continue

            if newPoint <= size:

                if  newPoint not in uniquePointSet:
                    for p in self.yieldOrPushBack(circularPointQueue, newPoint, greaterQu, iterCounter):
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

        return 0, 0

    def getPossibleValue(self, point, itemValue, itemWeight, dp):

        if point in dp:
            cur = dp[point]
            return cur[0] + itemValue, cur[1] + itemWeight

        if point < 0:
            return None, None

        return itemValue, itemWeight

    def setValue(self, curDP, p, curVal, curW, iterCounter):
        curDP[p] = (curVal, curW)
        iterCounter[0] += 1

    def backTraceItems(self, DP, resultI, resultP, items, values, itemsIndex, allAsc, iterCounter):
        opt = 0
        optSize = 0
        res = DP[resultI][resultP][0]
        optWeights, optValues, optIndex = [], [], []
        point = resultP

        count = len(items)

        self.totalPointCount += len(DP[resultI])

        if self.printInfo:
            print(
                f"Skipped points by MAP: {self.skippedPointsByMap}, by LIMITS: {self.skippedPointsByLimits}; by SIZE: {self.skippedPointsBySize}; Max points: {(2 ** len(items)) if len(items) < 15 else -1}; Total points: {self.totalPointCount};")

        for i in range(resultI, 0, -1):

            iterCounter[0] += 1

            if res <= 0:
                break

            dpw = DP[i - 1]

            skip = False

            if point in dpw:
                skip = res == dpw[point][0]

            if not skip:
                itemIndex = self.getItemIndex(count, i, allAsc)

                itemWeight, itemValue, itemIndex = items[itemIndex], values[itemIndex], itemsIndex[itemIndex]

                optWeights.append(itemWeight)
                optValues.append(itemValue)
                optIndex.append(itemIndex)

                res -= itemValue
                point -= itemWeight

                opt += itemValue
                optSize += itemWeight

        return opt, optSize, optWeights, optValues, optIndex

    def createDP(self, count):
        self.DP = [None] * (count + 1)
        self.DP[0] = {}
        return self.DP

    def solveSuperIncreasing(self, size, items, values, itemsIndex, count, allAsc, iterCounter):

        def indexLargestLessThanAsc(items, item, lo, hi, iterCounter):

            if item == 0:
                return None

            while lo <= hi:
                iterCounter[0] += 1
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

        def indexLargestLessThanDesc(items, item, lo, hi, iterCounter):

            if item == 0:
                return None

            cnt = len(items)

            while lo <= hi:
                iterCounter[0] += 1
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

        binSearch = indexLargestLessThanAsc if allAsc else indexLargestLessThanDesc

        starting = 1
        resultItems = []
        resultValues = []
        resultIndex = []
        resultSum = 0
        resultItemSum = 0
        index = binSearch(items, size, starting - 1, count - 1, iterCounter)

        while index is not None:
            item = items[index]
            value = values[index]
            resultItems.append(item)
            resultValues.append(value)
            resultIndex.append(itemsIndex[index])
            resultItemSum += item
            resultSum += value
            if allAsc:
                index = binSearch(items, size - resultItemSum, starting - 1, index - 1, iterCounter)
            else:
                index = binSearch(items, size - resultItemSum, index + 1, count - 1, iterCounter)

            iterCounter[0] += 1

        if self.printSuperIncreasingInfo:
            print(f"Superincreasing 1-0 solver called for size {size} and count {count}.  ASC={allAsc}")

        return resultSum, resultItemSum, resultItems, resultValues, resultIndex

    def getLimits(self, size, itemIndex, items, partialSums, superIncreasingItems, canUsePartialSums):

        if not self.doUseLimits or not canUsePartialSums:
            return sys.maxsize, -sys.maxsize, -sys.maxsize, 0

        skipCount = 2 ** (len(items) - itemIndex + 1) if self.printInfo else 0

        partSumForItem = partialSums[itemIndex]
        superIncreasingItem = superIncreasingItems[itemIndex]

        newPointLimit = size - partSumForItem
        oldPointLimit = newPointLimit

        if self.doSolveSuperInc and superIncreasingItem:
            oldPointLimit = newPointLimit + items[itemIndex]

        return partSumForItem, oldPointLimit, newPointLimit, skipCount

    def solveByPareto(self, lessSizeItems, lessSizeValues, lessSizeItemsIndex, size, iterCounter):
        if self.printInfo:
            print(f"1-0 knapsack pareto solver: N {len(lessSizeItems)}")

        paretoItems = [wPoint1(item) for item in lessSizeItems]
        paretoSolver = knapsackParetoSolver(paretoItems, lessSizeValues, lessSizeItemsIndex, wPoint1(size),
                                            paretoPoint1(0, 0), wPoint1(0), iterCounter)
        paretoSolver.printInfo = self.printInfo
        paretoSolver.canBackTraceWhenSizeReached = self.canBackTraceWhenSizeReached

        return paretoSolver.solve()

    def getItemIndex(self, count, i, allAsc):
        return count - i if allAsc else i - 1

    def solveByDynamicPrograming(self, size, count, lessSizeItems, lessSizeValues, lessSizeItemsIndex, partialSums,
                                 superIncreasingItems, allAsc, allDesc, canUsePartialSums, iterCounter):

        DP = self.createDP(count)

        resultI, resultP = 1, 1

        circularPointQueue = deque()

        maxValue, prevPointCount, newPointCount = -sys.maxsize, 0, 0

        if self.printInfo:
            print(
                f"1-0 knapsack dynamic programing solver: N={count}, Use limits={doUseLimits}, allAsc={allAsc}, allDesc={allDesc}, canUsePartialSums={canUsePartialSums}")

        for i in range(1, count + 1):

            itemIndex = self.getItemIndex(count, i, allAsc)

            DP[i] = {}

            itemValue, itemWeight = lessSizeValues[itemIndex], lessSizeItems[itemIndex]
            prevDP, curDP = DP[i - 1], DP[i]

            prevPointCount, newPointCount = newPointCount, prevPointCount
            newPointCount = 0

            self.totalPointCount += prevPointCount

            itemLimit, oldPointLimit, newPointLimit, skipCount = self.getLimits(size, itemIndex, lessSizeItems,
                                                                                partialSums, superIncreasingItems,
                                                                                canUsePartialSums)

            for p in self.getPoints(itemWeight, size, circularPointQueue, itemLimit, oldPointLimit, newPointLimit,
                                    prevPointCount, prevDP, skipCount, canUsePartialSums, iterCounter):

                curValue, curWeight = self.getValue(p, prevDP)
                posblValue, posblWeight = self.getPossibleValue(p - itemWeight, itemValue, itemWeight, prevDP)

                if posblValue and posblWeight <= size and curValue < posblValue:
                    curValue = posblValue
                    curWeight = posblWeight

                self.setValue(curDP, p, curValue, curWeight, iterCounter)

                if maxValue < curValue:
                    resultP = p
                    resultI = i
                    maxValue = curValue

                if self.canBackTraceWhenSizeReached and curWeight == size:
                    self.backTraceItems(DP, resultI, resultP, lessSizeItems, lessSizeValues, lessSizeItemsIndex, allAsc,
                                        iterCounter)

                newPointCount += 1

            if self.printInfo:
                print(f"| {i - 1} | {prevPointCount} | {round(iterCounter[0])} |")

        return self.backTraceItems(DP, resultI, resultP, lessSizeItems, lessSizeValues, lessSizeItemsIndex, allAsc, iterCounter)

    def solve(self):

        size, weights, values, forceUseLimits, iterCounter = self.size, self.weights, self.values, self.forceUseLimits, self.iterCounter

        size, count, lessSizeItems, lessSizeValues, lessSizeItemsIndex, itemSum, lessCountSum, lessCountValuesSum, partialSums, superIncreasing, superIncreasingItems, allAsc, allDesc, canUsePartialSums = self.preProcess(
            size, weights, values, forceUseLimits, iterCounter)

        cornerCasesCheck = self.checkCornerCases(size, lessSizeItems, lessSizeValues, lessSizeItemsIndex, lessCountSum,
                                                 itemSum, lessCountValuesSum)

        if cornerCasesCheck:
            return cornerCasesCheck

        if self.doSolveSuperInc and superIncreasing:
            return self.solveSuperIncreasing(size, lessSizeItems, lessSizeValues, lessSizeItemsIndex, count, allAsc, iterCounter)

        if canUsePartialSums and (allAsc or allDesc) or self.forceUseDpSolver:
            return self.solveByDynamicPrograming(size, count, lessSizeItems, lessSizeValues, lessSizeItemsIndex,
                                                 partialSums, superIncreasingItems, allAsc, allDesc, canUsePartialSums,
                                                 iterCounter)

        return self.solveByPareto(lessSizeItems, lessSizeValues, lessSizeItemsIndex, size, iterCounter)
