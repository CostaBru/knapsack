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

import math
import sys
from collections import deque


class knapsackParetoSolver:

    def __init__(self, dimensions, values, indexes, constraint, emptyPoint, emptyDimension, iterCounter):
        self.dimensions = dimensions
        self.values = values
        self.indexes = indexes
        self.constraint = constraint
        self.emptyPoint = emptyPoint
        self.emptyDimension = emptyDimension
        self.forceUseLimits = False
        self.forceUsePareto = True
        self.iterCounter = iterCounter
        self.totalPointCount = 0
        self.skippedPointsBySize = 0
        self.skippedPointsByMap = 0
        self.skippedPointsByPareto = 0
        self.skippedPointsByLimits = 0
        self.skippedPointsBySize = 0
        self.printInfo = False
        self.printSuperIncreasingInfo = False
        self.doSolveSuperInc = True
        self.doUseLimits = True
        self.canBackTraceWhenSizeReached = False  
        self.useRatioSort = False
        self.prepareSearchIndex = False
        self.maxProfitPointIndex = []
        self.solvedConstraint = None
        self.solvedBySuperIncreasingSolverAsc = False
        self.solvedBySuperIncreasingSolverDesc = False
        self.cornerCaseSolved = False
        self.keepCircularPointQueueSorted = True

    def createNewPoint(self, values, profit, id):
        return self.emptyPoint.createNew(values.getDimensions(), profit, id)

    def indexLargestLessThan(self,  items, item, lo, hi, iterCounter):

        ans = -1

        while lo <= hi:
            iterCounter[0] += 1
            mid = (lo + hi) // 2

            val = items[mid]
       
            if val.getProfit() > item:
                hi = mid - 1
                ans = mid
            else:
                lo = mid + 1

        return ans

    def findLargerProfit(self, items, profitMax, iterCounter):
        index = self.indexLargestLessThan(items, profitMax, 0, len(items) - 1, iterCounter)

        if index >= 0 and items[index].getProfit() > profitMax:
            return index
        else:
            return None
   
    def mergeDiscardingDominated(self, oldList, newList, iterCounter):

        result = []
        profitMax = -sys.maxsize

        while True:

            iterCounter[0] += 1

            oldPointIndex = self.findLargerProfit(oldList, profitMax, iterCounter)
            newPointIndex = self.findLargerProfit(newList, profitMax, iterCounter)

            if oldPointIndex is None:

                if newPointIndex is not None:

                    for ind in range(newPointIndex, len(newList)):
                        newPoint = newList[ind]
                        result.append(newPoint)

                        iterCounter[0] += 1

                break

            if newPointIndex is None:

                if oldPointIndex is not None:

                    for ind in range(oldPointIndex, len(oldList)):
                        result.append(oldList[ind])
                        iterCounter[0] += 1

                break

            oldPoint = oldList[oldPointIndex]
            newPoint = newList[newPointIndex]

            if oldPoint < newPoint or (oldPoint == newPoint and oldPoint.getProfit() > newPoint.getProfit()):
                result.append(oldPoint)
                profitMax = oldPoint.getProfit()              
            else:
                result.append(newPoint)
                profitMax = newPoint.getProfit()
               
        return result

    def sortByRatio(self, w, v, t, iterCounter):
        if len(w) > 0:
            sorted_pairs = sorted(zip(w, v, t), key=lambda t: (t[1] / t[0], t[1], t[0]))
            tuples = zip(*sorted_pairs)
            iterCounter[0] += len(w) * math.log2(len(w))
            return [list(tuple) for tuple in  tuples]
       
        return w, v, t

    def sortByDims(self, w, v, t, iterCounter):
        if len(w) > 0:
            sorted_pairs = sorted(zip(w, v, t), key=lambda t: (t[0], t[0] / t[1]))
            tuples = zip(*sorted_pairs)
            iterCounter[0] += len(w) * math.log2(len(w))
            return [list(tuple) for tuple in  tuples]
       
        return w, v, t

    def backTraceItemsLimits(self, constraint, circularPointQueue, maxProfitPoint, count, iterCounter):
        if self.prepareSearchIndex:
            orderedDims = list(circularPointQueue)
            orderedDims.sort(key=lambda x: x.dimensions)
            self.buildSearchIndex(orderedDims)

        self.solvedConstraint = constraint

        return self.backTraceItemsCore(maxProfitPoint, count, iterCounter)

    def backTraceItemsPareto(self, constraint, paretoOptimal, maxProfitPoint, count, iterCounter):
        if self.prepareSearchIndex:
            paretoOptimal.sort(key=lambda x: x.dimensions)
            self.buildSearchIndex(paretoOptimal)

        self.solvedConstraint = constraint

        return self.backTraceItemsCore(maxProfitPoint, count, iterCounter)

    def buildSearchIndex(self, orderedByDimPoints):
        '''
        The index accuracy depends on which limits were used, and what original constraint was.
        It make sense to use it in 3/4 to constraint window if it was solved by limits.
        For pareto solver it works for full range, because we do not skip points.
        For limit solver to gave exact index it should be build without limit using.
        If less it gives some optima but not the best value.
        '''

        maxByDims = []
        nextMaxProfitPoint = self.emptyPoint

        for p in orderedByDimPoints:
            if p.getProfit() > nextMaxProfitPoint.getProfit():
                nextMaxProfitPoint = p
                maxByDims.append(nextMaxProfitPoint)

        self.maxProfitPointIndex = maxByDims

    def backTraceItemsCore(self, maxProfitPoint, count, iterCounter):
        if maxProfitPoint:

            optSize = self.emptyDimension
            optItems, optValues, optIndexes  = [], [], []

            maxProfit = 0

            for id in maxProfitPoint.getItemIds():
                optItems.append(self.dimensions[id])
                optValues.append(self.values[id])
                optIndexes.append(self.indexes[id])
                optSize += self.dimensions[id]
                maxProfit += self.values[id]

            iterCounter[0] += len(optItems)

            if self.printInfo:
                print(f"Skipped points by MAP: {self.skippedPointsByMap}, by LIMITS: {self.skippedPointsByLimits}; by SIZE: {self.skippedPointsBySize}; by PARETO: {self.skippedPointsByPareto}; Total points: {self.totalPointCount}; N={count};")

            return maxProfit, optSize, optItems, optValues, optIndexes
        return 0, self.emptyPoint, [], [], []

    def preProcess(self, constraints, items, values, forceUseLimits, iterCounter):
       
        count = len(items)
        itemSum1, itemSum2, lessCountSum = self.emptyDimension, self.emptyDimension, self.emptyDimension
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

        if count > 0 :
           
            prevItem1 = items[-1]
            prevValue1 = values[-1]

            for i in range(0, count):

                item2 = items[i]
                itemValue2 = values[i]

                iBack = count - i - 1

                item1 = items[iBack]              
                itemValue1 = values[iBack]              

                superIncreasingItem1, superIncreasingItem2 = False, False

                if  item1 <= constraints:

                    if item1 < itemSum1:
                        isSuperIncreasing1 = False
                    else:
                        superIncreasingItem1 = True

                    if itemValue1 < valuesSum1:
                        isSuperIncreasingValues1 = False
                        superIncreasingItem1 = False
               
                if  item2 <= constraints:

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
                    superIncreasingItems1.append(superIncreasingItem1)
                    superIncreasingItems2.append(superIncreasingItem2)

                if  item2 <= constraints:
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

            canUsePartialSums = allValuesEqual or allValuesEqualToConstraints or (isSuperIncreasingValues1 and allDescValues) or (isSuperIncreasingValues2 and allAscValues)

            if allAsc and canUsePartialSums:
                partialSums = partialSums2
                superIncreasingItems = superIncreasingItems2
                isSuperIncreasing = isSuperIncreasing2
                itemSum = itemSum2    

            elif  (allDesc and canUsePartialSums) or forceUseLimits:
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
                    partialSums.reverse()
                    superIncreasingItems = superIncreasingItems2
                    superIncreasingItems.reverse()
                    canUsePartialSums = True
                elif allDesc and allDescValues:
                    itemSum = itemSum1
                    partialSums = partialSums1
                    partialSums.reverse()
                    superIncreasingItems = superIncreasingItems1
                    superIncreasingItems.reverse()
                    canUsePartialSums = True
                else:
                    superIncreasingItems = []
                    if not canUsePartialSums:
                        partialSums = []
                        canUsePartialSums = False
                    else:
                        partialSums = partialSums2
                        partialSums.reverse()
        else:
            partialSums = []
            superIncreasingItems = []
            isSuperIncreasing = False
            itemSum = itemSum2

        constraints = constraints.adjustMin(itemSum)
       
        iterCounter[0] += count
        return constraints, lessCount,  lessSizeItems, lessSizeValues, lessSizeItemsIndex, itemSum, lessCountSum, lessCountValuesSum, partialSums, isSuperIncreasing, superIncreasingItems, allAsc, allDesc, canUsePartialSums

    def checkCornerCases(self, constraints, lessSizeItems, lessSizeValues, lessSizeItemsIndex, lessCountSum, itemSum, lessCountValuesSum):        

        if  lessCountSum == self.emptyDimension:
            return 0, self.emptyDimension, [], [], []
       
        if  lessCountSum <= constraints:
            return lessCountValuesSum, lessCountSum, lessSizeItems, lessSizeValues, lessSizeItemsIndex

        if  itemSum <= constraints:
            return lessCountValuesSum, itemSum, lessSizeItems, lessSizeValues, lessSizeItemsIndex

        return None      

    def solveSuperIncreasing(self, size, items, values, itemsIndex, count, allAsc, iterCounter):

        def indexLargestLessThanAsc(items, item, lo, hi, iterCounter):

            if item == self.emptyDimension:
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

            if item == self.emptyDimension:
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
        resultItemSum = self.emptyDimension
        index = binSearch(items, size, starting - 1, count - 1, iterCounter)

        self.solvedBySuperIncreasingSolverAsc = allAsc
        self.solvedBySuperIncreasingSolverDesc = not allAsc
        self.solvedConstraint = size

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
            print(f"Superincreasing pareto solver called for size {size} and count {count}.  ASC={allAsc}")
       
        return resultSum, resultItemSum, resultItems, resultValues, resultIndex

    def getLimits(self, constraints, i, items, partialSums, superIncreasingItems, canUsePartialSums):

        if not self.doUseLimits or not canUsePartialSums or self.prepareSearchIndex:
            return None, None, None, 0

        skipCount = 2 ** (len(items) - (i + 1)) if self.printInfo else 0

        partSumForItem = partialSums[i]
        superIncreasingItem = superIncreasingItems[i] if len(superIncreasingItems) > 0 else None
     
        newPointLimit = constraints - partSumForItem if partSumForItem else None
        oldPointLimit = newPointLimit
     
        if self.doSolveSuperInc and newPointLimit and superIncreasingItem:
            oldPointLimit = newPointLimit + items[i]

        return partSumForItem, oldPointLimit, newPointLimit, skipCount
   
    def iterateOrPushBack(self, circularPointQueue, newPoint,  greaterQu, distinctPoints2):

        if self.keepCircularPointQueueSorted and len(circularPointQueue) > 0:
            peek = circularPointQueue[0]

            if newPoint <= peek:
                circularPointQueue.append(newPoint)
                distinctPoints2.add(newPoint)              
            else:

                greaterQuPeek = greaterQu[0] if len(greaterQu) > 0 else None
               
                if greaterQuPeek and newPoint <= greaterQuPeek:
                    greaterQu.insert(0, newPoint)
                else:
                    greaterQu.append(newPoint)
        else:
            circularPointQueue.append(newPoint)
            distinctPoints2.add(newPoint)

    def iterateLessThanOldPoint(self, oldPoint, circularPointQueue, canUseLimits, greaterQu, oldPointLimit, skipCount, distinctPoints2):

        while len(greaterQu) > 0 and greaterQu[0] < oldPoint:

            quPoint = greaterQu.popleft()          
            distinctPoints2.add(quPoint)
            circularPointQueue.append(quPoint)

        if not canUseLimits or not oldPointLimit or not oldPoint < oldPointLimit:
            self.iterateOrPushBack(circularPointQueue, oldPoint, greaterQu, distinctPoints2)
        else:
            self.skippedPointsByLimits += skipCount

    def iterateGreaterPoints(self, greaterQu, circularPointQueue, distinctPoints2):
        while len(greaterQu) > 0:
            quPoint = greaterQu.popleft()
            circularPointQueue.append(quPoint)
            distinctPoints2.add(quPoint)
 
    def getItemIndex(self, count, i, allAsc):
        return count - i if allAsc else i - 1

    def iteratePoints(self, i,  itemDimensions, itemProfit, itemId, constraintPoint, maxProfitPoint, circularPointQueue, prevCyclePointCount, halfConstraint, itemLimit, oldPointLimit, newPointLimit, distinctPoints1,  distinctPoints2, skipCount, canUseLimits, iterCounter):
       
        # merges ordered visited points with new points with keeping order in iterCounter(N) using single circular queue.
        # each getPoints method call starts fetching visited points from qu start, pops visited point and pushes new point and visited to the end of qu in ASC order.
        # we skip new point if it in list already
        # skips points if they will not contribute to optimal solution (in case of desc flow and (equal values or values equal to first dimension))

        greaterQu = deque()

        skipLimitCheck = not canUseLimits

        itemPoint = self.createNewPoint(itemDimensions, itemProfit, itemId)

        useItemItself = True

        if useItemItself:

            if  itemPoint not in distinctPoints1:
                self.iterateOrPushBack(circularPointQueue, itemPoint, greaterQu, distinctPoints2)

                if maxProfitPoint.getProfit() <= itemPoint.getProfit():
                    maxProfitPoint = itemPoint  
            else:            
                self.skippedPointsByMap += skipCount
        else:
            self.skippedPointsByLimits += skipCount

        for pi in range(prevCyclePointCount):

            oldPoint = circularPointQueue.popleft()

            self.iterateLessThanOldPoint(oldPoint, circularPointQueue, canUseLimits, greaterQu, oldPointLimit, skipCount, distinctPoints2)

            newPoint = oldPoint + itemPoint

            if not skipLimitCheck and (newPointLimit and  newPoint < newPointLimit):
                self.skippedPointsByLimits += skipCount
                continue

            if  newPoint <= constraintPoint:

                if  newPoint not in distinctPoints1:

                    self.iterateOrPushBack(circularPointQueue, newPoint, greaterQu, distinctPoints2)

                    if maxProfitPoint.getProfit() <= newPoint.getProfit():

                        if maxProfitPoint < newPoint:
                            maxProfitPoint = newPoint
                else:
                    self.skippedPointsByMap += skipCount
            else:
                self.skippedPointsBySize += skipCount

        self.iterateGreaterPoints(greaterQu, circularPointQueue, distinctPoints2)

        newPointCount = len(circularPointQueue)

        iterCounter[0] += newPointCount + 1

        if self.printInfo:
            self.totalPointCount += newPointCount
            print(f"| {i - 1} | {newPointCount} | {round(iterCounter[0])} |")

        return newPointCount, maxProfitPoint

    def solveUsingLimitsOnly(self, constraint, lessSizeItems, lessSizeValues, lessSizeItemsIndex, allAsc, partialSums, superIncreasingItems, canUsePartialSums):

        sortedItems, sortedValues, sortedIndexes = lessSizeItems, lessSizeValues, lessSizeItemsIndex
   
        distinctPoints1 = set()

        i, itemsCount = 1, len(sortedItems)

        maxProfitPoint = self.emptyPoint

        circularPointQueue = deque()

        prevPointCount, newPointCount = 0, 0

        halfConstraint = constraint.divideBy(2)

        for i in range(1, itemsCount + 1):

            itemIndex = self.getItemIndex(itemsCount, i, allAsc)

            itemDimensions, itemProfit, itemId = sortedItems[itemIndex], sortedValues[itemIndex], sortedIndexes[itemIndex]

            itemLimit, oldPointLimit, newPointLimit, skipCount = self.getLimits(constraint, itemIndex, sortedItems, partialSums, superIncreasingItems, canUsePartialSums)

            newPointCount, maxProfitPoint = self.iteratePoints(i, itemDimensions, itemProfit, itemId, constraint, maxProfitPoint, circularPointQueue, prevPointCount, halfConstraint, itemLimit,  oldPointLimit, newPointLimit, distinctPoints1,  distinctPoints1, skipCount, canUsePartialSums, self.iterCounter)
         
            if self.canBackTraceWhenSizeReached and maxProfitPoint.isDimensionEquals(constraint):
                return self.backTraceItemsLimits(constraint, circularPointQueue, maxProfitPoint, itemsCount, self.iterCounter)

            prevPointCount = newPointCount

        return self.backTraceItemsLimits(constraint, circularPointQueue, maxProfitPoint, itemsCount, self.iterCounter)

    def getNewPoints(self, i, maxProfitPoint, itemDimensions, itemProfit, itemId, oldPoints, constraint, prevDistinctPoints, newDistinctPoints, skipCount, iterCounter):

        result = []

        itemPoint = self.createNewPoint(itemDimensions, itemProfit, itemId)
       
        for oldPoint in oldPoints:

            newPoint  = oldPoint + itemPoint

            if newPoint <= constraint:

                if newPoint not in prevDistinctPoints:
                    newDistinctPoints.add(newPoint)
                    result.append(newPoint)
                else:
                    self.skippedPointsByMap += skipCount

                if maxProfitPoint.getProfit() <= newPoint.getProfit():

                    if self.useRatioSort and maxProfitPoint.getProfit() == newPoint.getProfit():
                        if maxProfitPoint.dimensions < newPoint.dimensions:
                            maxProfitPoint = newPoint
                    else:
                        maxProfitPoint = newPoint
            else:
                self.skippedPointsBySize += skipCount

        newPointCount = len(oldPoints)

        iterCounter[0] += len(oldPoints) + 1

        if self.printInfo:
            self.totalPointCount += newPointCount
            print(f"| {i - 1} | {newPointCount} | {round(iterCounter[0])} |")

        return result, maxProfitPoint

    def solvePareto(self, constraint, sortedItems, sortedValues, sortedIndexes, iterCounter):

        maxProfitPoint, emptyPoint = self.emptyPoint, self.emptyPoint

        distinctPoints = set()

        oldPoints = [emptyPoint]
        newPoints = []      

        itemsCount = len(sortedItems)

        for i in range(1, itemsCount + 1):

            skipCount = 2 ** (itemsCount - i)  if self.printInfo else 0

            itemDimensions, itemProfit, itemId = sortedItems[i - 1], sortedValues[i - 1], sortedIndexes[i - 1]

            newPoints, maxProfitPoint = self.getNewPoints(i, maxProfitPoint, itemDimensions, itemProfit, itemId, oldPoints, constraint, distinctPoints, distinctPoints, skipCount, iterCounter)
         
            # Point A is dominated by point B if B achieves a larger profit with the same or less weight than A.
            paretoOptimal = self.mergeDiscardingDominated(oldPoints, newPoints, iterCounter)

            if self.canBackTraceWhenSizeReached and maxProfitPoint.isDimensionEquals(constraint):
                return self.backTraceItemsPareto(constraint, paretoOptimal, maxProfitPoint, itemsCount, iterCounter)

            oldPoints = paretoOptimal

        return self.backTraceItemsPareto(constraint, oldPoints, maxProfitPoint, itemsCount, iterCounter)

    def binarySearchMaxProfit(self, constraint):

        def indexLargestLessThanAsc(items, item, lo, hi, iterCounter):

            if item == self.emptyDimension:
                return None

            while lo <= hi:
                iterCounter[0] += 1
                mid = (lo + hi) // 2

                val = items[mid]

                if item.dimensions == val.dimensions:
                    return mid

                if val.dimensions < item.dimensions:
                    lo = mid + 1
                else:
                    hi = mid - 1

            if hi >= 0 and item.dimensions >= items[hi].dimensions:
                return hi
            else:
                return None

        if self.solvedBySuperIncreasingSolverAsc or self.solvedBySuperIncreasingSolverDesc:
            return self.solveSuperIncreasing(constraint,
                                             self.dimensions,
                                             self.values,
                                             self.indexes,
                                             len(self.values),
                                             self.solvedBySuperIncreasingSolverAsc,
                                             self.iterCounter)

        if constraint > self.solvedConstraint:
            raise ValueError(
                f"The constraint given ({constraint}) should be less or equal than index built constraint ({self.solvedConstraint})).")

        if self.printInfo:
            print(f"KB pareto knapsack solver: binary search using {constraint} given. Index was built for {self.solvedConstraint} constraint.")

        count = len(self.maxProfitPointIndex)

        if count == 0:
            raise ValueError(
                f"Search index wasn't built for '{self.solvedConstraint}' constraint. So the binary search using given '{constraint}' constraint is not possible.")

        index = indexLargestLessThanAsc(self.maxProfitPointIndex, constraint, 0, len(self.maxProfitPointIndex) - 1, self.iterCounter)

        maxProfitPoint = None

        if index >= 0:
            maxProfitPoint = self.maxProfitPointIndex[index]

        return self.backTraceItemsCore(maxProfitPoint, count, self.iterCounter)

    def solve(self, searchConstraint=None):

        """
        Solves current instance using given search or the init constraint value.

        If the prepareSearchIndex property is set then it will build the index for fast seek the max profit point
        that less than constraint used to build the index. Limits checking feature would be turned off in this case.
        It will use O(N) to prepare the index, where N is number of points generated during solving the problem.

        :param searchConstraint: searchConstraint
        :type searchConstraint: wPoint

        :return: bestValue, bestSize, bestItems, bestValues, bestIndexes
        """

        if not searchConstraint:
            searchConstraint = self.solvedConstraint

            if not searchConstraint:
                searchConstraint = self.constraint

        canTryBinarySearch = len(self.maxProfitPointIndex) > 0 or self.solvedBySuperIncreasingSolverAsc or self.solvedBySuperIncreasingSolverDesc

        if canTryBinarySearch and searchConstraint <= self.solvedConstraint:
            return self.binarySearchMaxProfit(searchConstraint)

        canTrySolveUsingDp = not self.forceUsePareto and (self.doUseLimits or self.doSolveSuperInc or self.forceUseLimits or self.canBackTraceWhenSizeReached)

        canSolveUsingDp = False

        if canTrySolveUsingDp:

            constraint, \
            count,\
            lessSizeItems, \
            lessSizeValues, \
            lessSizeItemsIndex,\
            itemSum, \
            lessCountSum, \
            lessCountValuesSum, \
            partialSums, \
            superIncreasing, \
            superIncreasingItems, \
            allAsc, \
            allDesc, \
            canUsePartialSums = \
                self.preProcess(searchConstraint, self.dimensions, self.values, self.forceUseLimits, self.iterCounter)

            cornerCasesCheck = self.checkCornerCases(constraint, lessSizeItems, lessSizeValues, lessSizeItemsIndex, lessCountSum, itemSum, lessCountValuesSum)

            if  cornerCasesCheck:
                self.cornerCaseSolved = True
                return cornerCasesCheck

            if self.doSolveSuperInc and superIncreasing:
                return self.solveSuperIncreasing(constraint, lessSizeItems, lessSizeValues, lessSizeItemsIndex, count, allAsc, self.iterCounter)

            canSolveUsingDp = not self.forceUsePareto and (self.forceUseLimits or self.canBackTraceWhenSizeReached or canUsePartialSums)

            if canSolveUsingDp:

                if self.printInfo:
                    print(f"KB pareto DP knapsack solver: N={count}; canUsePartialSums={canUsePartialSums}; forceUseLimits={self.forceUseLimits}")

                return  self.solveUsingLimitsOnly(constraint, lessSizeItems, lessSizeValues, lessSizeItemsIndex, allAsc, partialSums, superIncreasingItems, canUsePartialSums)
        else:
            constraint, lessSizeItems, lessSizeValues, lessSizeItemsIndex = searchConstraint, self.dimensions, self.values, self.indexes

        if self.printInfo:
            print(f"KB pareto knapsack solver: N={len(lessSizeItems)}; canTrySolveUsingDp={canTrySolveUsingDp}; canSolveUsingDp={canSolveUsingDp}")

        sortingFunc = self.sortByRatio if self.useRatioSort else self.sortByDims

        sortedItems, sortedValues, sortedIndexes = sortingFunc(lessSizeItems, lessSizeValues, lessSizeItemsIndex, self.iterCounter)

        return self.solvePareto(constraint, sortedItems, sortedValues, sortedIndexes, self.iterCounter)
