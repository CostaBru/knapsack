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

from collections import deque


class subsetSumParetoSolver:

    def __init__(self, constraint, dimensions, iterCounter, forceUseLimits=False):
        self.dimensions = dimensions
        self.constraint = constraint
        self.emptyPoint = 0
        self.emptyDimension = 0
        self.forceUseLimits = forceUseLimits
        self.iterCounter = iterCounter
        self.totalPointCount = 0
        self.skippedPointsBySize = 0
        self.skippedPointsByMap = 0
        self.skippedPointsByLimits = 0
        self.skippedPointsBySize = 0
        self.printInfo = False
        self.printSuperIncreasingInfo = False
        self.doSolveSuperInc = True
        self.doUseLimits = True

    def backTraceItems(self, maxProfitPoint, count, pointSources, pointIds, iterCounter):

        def getItemIds(point, pointIds):
            if pointIds[point] is not None:
                yield pointIds[point]

            if pointSources[point] is not None:
                for id in getItemIds(pointSources[point], pointIds):
                    yield id

        if maxProfitPoint is not None:

            optSize = self.emptyDimension
            optItems  = []

            for id in getItemIds(maxProfitPoint, pointIds):
                optItems.append(self.dimensions[id])
                optSize += self.dimensions[id]

            iterCounter[0] += len(optItems)

            if self.printInfo:
                print(f"Skipped points by MAP: {self.skippedPointsByMap}, by LIMITS: {self.skippedPointsByLimits}; by SIZE: {self.skippedPointsBySize}; Total points: {self.totalPointCount}; N={count};")

            return optSize, optItems

        return 0, []

    def preProcess(self, constraints, items, forceUseLimits, iterCounter):
       
        count = len(items)
        itemSum1, itemSum2, lessCountSum = self.emptyDimension, self.emptyDimension, self.emptyDimension

        lessSizeItems = []

        partialSums1, superIncreasingItems1 = [], [False]
        partialSums2, superIncreasingItems2 = [], [False]

        isSuperIncreasing1, isSuperIncreasing2 = True, True
        allDesc, allAsc = True, True

        canUsePartialSums = False

        lessCount = 0

        if count > 0:
           
            prevItem1 = items[-1]

            for i in range(0, count):

                iBack = count - i - 1

                item1, item2 = items[iBack], items[i]
                superIncreasingItem1, superIncreasingItem2 = False, False

                if  item1 <= constraints:
                    if item1 < itemSum1:
                        isSuperIncreasing1 = False
                    else:
                        superIncreasingItem1 = True

                if  item2 <= constraints:
                    if item2 < itemSum2:
                        isSuperIncreasing2 = False
                    else:
                        superIncreasingItem2 = True

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

                if i > 0:
                    superIncreasingItems1.append(superIncreasingItem1)
                    superIncreasingItems2.append(superIncreasingItem2)

                if  item2 <= constraints:
                    lessSizeItems.append(item2)                
                    lessCountSum += item2
                    lessCount += 1  

                prevItem1 = item1

            isSuperIncreasing = False
            itemSum = itemSum2

            if allAsc:
                partialSums = partialSums2
                superIncreasingItems = superIncreasingItems2
                isSuperIncreasing = isSuperIncreasing2
                itemSum = itemSum2
                canUsePartialSums = True

            elif  allDesc or forceUseLimits:
                partialSums = partialSums1
                superIncreasingItems = superIncreasingItems1
                isSuperIncreasing = isSuperIncreasing1
                itemSum = itemSum1
                canUsePartialSums = True
                partialSums.reverse()
                superIncreasingItems.reverse()           
            else:
                superIncreasingItems = []
                partialSums = partialSums2
                partialSums.reverse()
        else:
            partialSums = []
            superIncreasingItems = []
            isSuperIncreasing = False
            itemSum = itemSum2

        constraints = min(constraints, itemSum)
       
        iterCounter[0] += count
        return constraints, lessCount,  lessSizeItems, itemSum, lessCountSum, partialSums, isSuperIncreasing, superIncreasingItems, allAsc, allDesc, canUsePartialSums

    def checkCornerCases(self, constraints, lessSizeItems, lessCountSum, itemSum):

        if  lessCountSum == self.emptyDimension:
            return 0, []
       
        if  lessCountSum <= constraints:
            return  lessCountSum, lessSizeItems

        if  itemSum <= constraints:
            return  itemSum, lessSizeItems

        return None      

    def solveSuperIncreasing(self, size, items, count, allAsc, iterCounter):

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
        resultItemSum = self.emptyDimension
        index = binSearch(items, size, starting - 1, count - 1, iterCounter)

        while index is not None:
            item = items[index]
            resultItems.append(item)
            resultItemSum += item
            if allAsc:
                index = binSearch(items, size - resultItemSum, starting - 1, index - 1, iterCounter)
            else:
                index = binSearch(items, size - resultItemSum, index + 1, count - 1, iterCounter)

            iterCounter[0] += 1

        if self.printSuperIncreasingInfo:
            print(f"Superincreasing subset sum pareto solver called for size {size} and count {count}.  ASC={allAsc}")
       
        return  resultItemSum, resultItems

    def getLimits(self, constraints, i, items, partialSums, superIncreasingItems, canUsePartialSums):

        if not self.doUseLimits or not canUsePartialSums:
            return self.emptyPoint, self.emptyPoint, self.emptyPoint, self.emptyPoint

        skipCount = 2 ** (len(items) - (i + 1)) if self.printInfo else 0

        partSumForItem = partialSums[i]
        superIncreasingItem = superIncreasingItems[i] if len(superIncreasingItems) > 0 else None
     
        newPointLimit = constraints - partSumForItem if partSumForItem else None
        oldPointLimit = newPointLimit
     
        if self.doSolveSuperInc and newPointLimit and superIncreasingItem:
            oldPointLimit = newPointLimit + items[i]

        return partSumForItem, oldPointLimit, newPointLimit, skipCount

    def iterateOrPushBack(self, circularPointQueue, newPoint, pointValues, greaterQu, distinctPoints2):

        if len(circularPointQueue) > 0:
            peek = circularPointQueue[0]

            if pointValues[newPoint] <= pointValues[peek]:
                circularPointQueue.append(newPoint)
                distinctPoints2.add(pointValues[newPoint])
            else:
                greaterQuPeek = greaterQu[0] if len(greaterQu) > 0 else None

                if greaterQuPeek and pointValues[newPoint] <= pointValues[greaterQuPeek]:
                    greaterQu.insert(0, newPoint)
                else:
                    greaterQu.append(newPoint)
        else:
            circularPointQueue.append(newPoint)
            distinctPoints2.add(newPoint)

    def iterateLessThanOldPoint(self, oldPoint, pointValues, circularPointQueue, canUseLimits, greaterQu,
                                oldPointLimit, skipCount, distinctPoints2):

        while len(greaterQu) > 0 and pointValues[greaterQu[0]] < pointValues[oldPoint]:

            quPoint = greaterQu.popleft()          
            distinctPoints2.add(pointValues[quPoint])
            circularPointQueue.append(quPoint)

        if not canUseLimits or not oldPointLimit or not pointValues[oldPoint] < oldPointLimit:
            self.iterateOrPushBack(circularPointQueue, oldPoint, pointValues, greaterQu, distinctPoints2)
        else:
            self.skippedPointsByLimits += skipCount

        return True

    def iterateGreaterPoints(self, greaterQu, circularPointQueue, pointValues, distinctPoints2):
        while len(greaterQu) > 0:
            quPoint = greaterQu.popleft()
            circularPointQueue.append(quPoint)
            distinctPoints2.add(pointValues[quPoint])
 
    def getItemIndex(self, count, i, allAsc):
        return count - i if allAsc else i - 1

    def iteratePoints(self, i, itemId, itemDimensions, pointValues, pointSources, pointIds, constraintPoint,
                      maxProfitPoint, circularPointQueue, prevCyclePointCount, halfConstraint, itemLimit, oldPointLimit,
                      newPointLimit, distinctPoints1,  distinctPoints2, skipCount, canUseLimits, iterCounter):
       
        # merges ordered visited points with new points with keeping order in iterCounter(N) using single circular queue.
        # each getPoints method call starts fetching visited points from qu start, pops visited point and pushes new point and visited to the end of qu in ASC order.
        # we skip new point if it in list already
        # skips points if they will not contribute to optimal solution

        greaterQu = deque()

        skipLimitCheck = not canUseLimits

        itemPoint = len(pointSources)

        pointValues.append(itemDimensions)
        pointIds.append(itemId)
        pointSources.append(None)

        useItemItself = skipLimitCheck or itemLimit >= halfConstraint

        if useItemItself:
            if  itemDimensions not in distinctPoints1:
                self.iterateOrPushBack(circularPointQueue, itemPoint, pointValues, greaterQu, distinctPoints2)

                if maxProfitPoint < itemDimensions:  maxProfitPoint = itemPoint

            else: self.skippedPointsByMap += skipCount
        else:     self.skippedPointsByLimits += skipCount

        for pi in range(prevCyclePointCount):

            oldPoint = circularPointQueue.popleft()    

            self.iterateLessThanOldPoint(oldPoint, pointValues, circularPointQueue, canUseLimits, greaterQu, oldPointLimit, skipCount, distinctPoints2)

            newPointDim = pointValues[oldPoint] + itemDimensions
            newPoint = len(pointValues)

            if skipLimitCheck and (newPointLimit and newPointDim < newPointLimit):
                self.skippedPointsByLimits += skipCount
                continue

            if  newPointDim <= constraintPoint:
                if  newPointDim not in distinctPoints1:

                    pointValues.append(newPointDim)
                    pointIds.append(itemId)
                    pointSources.append(oldPoint)

                    self.iterateOrPushBack(circularPointQueue, newPoint, pointValues, greaterQu, distinctPoints2)

                    if pointValues[maxProfitPoint] < newPointDim:   maxProfitPoint = newPoint

                else:  self.skippedPointsByMap += skipCount
            else:      self.skippedPointsBySize += skipCount

        self.iterateGreaterPoints(greaterQu, circularPointQueue, pointValues, distinctPoints2)

        newPointCount = len(circularPointQueue)

        iterCounter[0] += newPointCount + 1

        if self.printInfo:
            self.totalPointCount += newPointCount
            print(f"| {i - 1} | {newPointCount} | {round(iterCounter[0])} |")

        return newPointCount, maxProfitPoint

    def solveUsingLimitsOnly(self, constraint, lessSizeItems, allAsc, partialSums, superIncreasingItems, canUsePartialSums):

        sortedItems = lessSizeItems
   
        distinctPoints1, distinctPoints2 = set(), set()

        i, itemsCount = 1, len(sortedItems)

        maxProfitPoint = self.emptyPoint

        circularPointQueue = deque()

        prevPointCount, newPointCount = 0, 0

        halfConstraint = constraint // 2

        pointValues, pointSources, pointIds = [], [], []

        for i in range(1, itemsCount + 1):

            distinctPoints1, distinctPoints2 = distinctPoints2, distinctPoints1
            distinctPoints2.clear()

            itemIndex = self.getItemIndex(itemsCount, i, allAsc)

            itemDimensions = sortedItems[itemIndex]

            itemLimit, oldPointLimit, newPointLimit, skipCount = self.getLimits(constraint, itemIndex, sortedItems, partialSums, superIncreasingItems, canUsePartialSums)

            newPointCount, maxProfitPoint = self.iteratePoints(i, itemIndex, itemDimensions, pointValues, pointSources, pointIds, constraint, maxProfitPoint, circularPointQueue, prevPointCount, halfConstraint, itemLimit,  oldPointLimit, newPointLimit, distinctPoints1,  distinctPoints2, skipCount, canUsePartialSums, self.iterCounter)
         
            if  pointValues[maxProfitPoint] == constraint:
                return self.backTraceItems(maxProfitPoint, itemsCount, pointSources, pointIds, self.iterCounter)

            prevPointCount = newPointCount        

        return self.backTraceItems(maxProfitPoint, itemsCount, pointSources, pointIds, self.iterCounter)

    def solve(self):

        constraints, count,  lessSizeItems, itemSum, lessCountSum, partialSums, isSuperIncreasing, superIncreasingItems, allAsc, allDesc, canUsePartialSums = self.preProcess(self.constraint, self.dimensions, self.forceUseLimits, self.iterCounter)

        cornerCasesCheck = self.checkCornerCases(constraints, lessSizeItems, lessCountSum, itemSum)

        if  cornerCasesCheck:
            return cornerCasesCheck

        if self.doSolveSuperInc and isSuperIncreasing:
            return self.solveSuperIncreasing(constraints, lessSizeItems, count, allAsc, self.iterCounter)

        if self.printInfo:
            print(f"KB subset-sum pareto knapsack solver: N={count}; canUsePartialSums={canUsePartialSums}; forceUseLimits={self.forceUseLimits}")

        return  self.solveUsingLimitsOnly(constraints, lessSizeItems, allAsc, partialSums, superIncreasingItems, canUsePartialSums)