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

import sys

from collections import defaultdict
from collections import deque

from flags.flags import doUseLimits


class subsetSumKnapsackSolver:

    def __init__(self, size, items, iterCounter, forceUseLimits = False):
        self.size = size
        self.items = items
        self.iterCounter = iterCounter
        self.forceUseLimits = forceUseLimits
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

    def preProcess(self, size, items, forceUseLimits, iterCounter):
       
        count = len(items)
        itemSum1, itemSum2, lessCountSum = 0, 0, 0

        partialSums1, superIncreasingItems1 = [sys.maxsize] * count, [False] * count
        partialSums2, superIncreasingItems2 = [sys.maxsize] * count, [False] * count
        isSuperIncreasing1, isSuperIncreasing2 = True, True
        allDesc, allAsc = True, True
        starting, ending = 1, count

        if count > 0 :
           
            i = 0
            prevItem1 = items[-1]

            for item2 in items:
                iBack = count - i - 1

                item1 = items[iBack]              

                superIncreasingItem1 = False
                superIncreasingItem2 = False

                if item1 <= size:

                    if item1 < itemSum1:
                        isSuperIncreasing1 = False
                    else:
                        superIncreasingItem1 = True
               
                if item2 <= size:

                    if item2 < itemSum2:
                        isSuperIncreasing2 = False
                    else:
                        superIncreasingItem2 = True

                itemSum1 += item1
                itemSum2 += item2

                partialSums1[iBack] = itemSum2  
                partialSums2[i] = itemSum1  

                if allDesc:
                    if not prevItem1 <= item1:
                        allDesc = False
               
                if allAsc:
                    if prevItem1 < item1:
                        allAsc = False

                if i > 0:
                    superIncreasingItems1[iBack] = superIncreasingItem2
                    superIncreasingItems2[iBack] = superIncreasingItem1

                if item2 <= size:
                    lessCountSum += item2  
                elif allDesc:
                    starting += 1
                elif allAsc:
                    ending = min(i, ending)

                prevItem1 = item1
               
                i += 1
           
            partialSums = []
            superIncreasingItems = []
            isSuperIncreasing = False
            itemSum = itemSum2      

            if allAsc:                
                partialSums = partialSums2
                superIncreasingItems = superIncreasingItems2
                isSuperIncreasing = isSuperIncreasing2
                itemSum = itemSum2  
            elif allDesc or forceUseLimits:
                partialSums = partialSums1
                superIncreasingItems = superIncreasingItems1
                isSuperIncreasing = isSuperIncreasing1
                itemSum = itemSum1

            else:
                starting = 1
                ending = count
                partialSums = [sys.maxsize] * count
                superIncreasingItems = [False] * count
        else:
            partialSums = []
            superIncreasingItems = []
            isSuperIncreasing = False
            itemSum = 0    

        size = min(itemSum, size)    
       
        iterCounter[0] += count
        return size, count, itemSum, lessCountSum, partialSums, starting, ending, isSuperIncreasing, superIncreasingItems, allAsc, allDesc

    def checkCornerCases(self, size, items, sum, lessCountSum, iterCounter):

        if  lessCountSum == 0:
            return [0,[]]
       
        if  lessCountSum <= size:
           
            lessCountItems = []

            for item in items:
                itemWeight = item

                if itemWeight <= size:
                    lessCountItems.append(itemWeight)

            iterCounter[0] += len(lessCountItems)

            return [lessCountSum, lessCountItems]

        if  sum <= size:
            return [sum, items]  

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

    def getPoints(self, itemWeight, size, circularPointQueue, itemLimit, oldPointLimit, newPointLimit, prevCyclePointCount, uniquePointSet, skipCount, iterCounter):
       
        # merges ordered visited points with new points with keeping order in iterCounter(N) using single circular queue.
        # each getPoints method call starts fetching visited points from qu start, pops visited point and pushes new point and visited to the end of qu in ASC order.
        # we skip new point if it in list already
        # skips points if they will not contribute to optimal solution

        greaterQu = deque()

        useItemItself = itemLimit >= size // 2

        if useItemItself and not itemWeight in uniquePointSet:
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

            if  oldPoint >= oldPointLimit:
                for p in self.yieldOrPushBack(circularPointQueue, oldPoint, greaterQu, iterCounter):
                    yield p
            else:
                self.skippedPointsByLimits  += skipCount  
         
            newPoint = oldPoint + itemWeight

            if  newPoint < newPointLimit:
                self.skippedPointsByLimits += skipCount
                continue

            if newPoint <= size:  

                if not newPoint in uniquePointSet:
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

    def getValue(self, point, dp):

        if point in dp:
           return dp[point]
       
        return 0
   
    def getPossibleValue(self, point, itemValue, dp):

        if point in dp:
           return dp[point] + itemValue

        if point < 0:
            return None
       
        return itemValue

    def setValue(self, curDP, p, curVal, iterCounter):
        curDP[p] = curVal    
        iterCounter[0] += 1

    def backTraceItems(self, DP, resultI, resultP, items, lessItemsRange, allAsc, iterCounter):
       
        opt = 0
        res = DP[resultI][resultP]
        optWeights = []
        point = resultP

        self.totalPointCount += len(DP[resultI])

        if self.printInfo:
            print(f"Skipped points by MAP: {self.skippedPointsByMap}, by LIMITS: {self.skippedPointsByLimits}; by SIZE: {self.skippedPointsBySize};  Max points: {(2 ** len(items)) if len(items) < 15 else -1}; Total points: {self.totalPointCount}; N={len(items)}, Use limits: {doUseLimits};")

        for i in range(resultI, 0, -1):
           
            iterCounter[0] += 1

            if res <= 0:
                break      

            prevDP = DP[i - 1]

            skip = False

            if point in prevDP:
                skip = res == prevDP[point]
           
            if not skip:    

                itemIndex = self.getItemIndex(lessItemsRange, i, allAsc)
                item = items[itemIndex]
                optWeights.append(item)  

                res   -= item
                point -= item
               
                opt += item

        return opt, optWeights

    def createDP(self, count, starting):
        self.DP    = [None] * (count + 1)
        self.DP[starting - 1] = defaultdict()
        return self.DP

    def solveSuperIncreasing(self, size, items, starting, ending, count, allAsc, iterCounter):

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

        binSearch = indexLargestLessThanAsc if allAsc else indexLargestLessThanDesc

        resultItems = []
        resultSum = 0
        index = binSearch(items, size, starting - 1, ending - 1, iterCounter)

        while index is not None:
            value = items[index]
            resultItems.append(value)
            resultSum += value
            if allAsc:
                index = binSearch(items, size - resultSum, starting - 1, index - 1, iterCounter)
            else:
                index = binSearch(items, size - resultSum, index + 1, ending - 1, iterCounter)
            iterCounter[0] += 1
       
        if self.printSuperIncreasingInfo:
            print(f"Superincreasing subset sum solver called for size {size} and count {count}. ASC={allAsc}")
       
        return resultSum, resultItems
   
    def getLimits(self, size, itemIndex, items, partialSums, superIncreasingItems):

        if not self.doUseLimits:
            return sys.maxsize, -sys.maxsize, -sys.maxsize, 0

        skipCount = 2 ** (len(items) - (itemIndex + 1)) if self.printInfo else 0

        partSumForItem = partialSums[itemIndex]
        superIncreasingItem = superIncreasingItems[itemIndex]

        newPointLimit = size - partSumForItem
        oldPointLimit = newPointLimit

        if self.doSolveSuperInc and superIncreasingItem:
            oldPointLimit = newPointLimit + items[itemIndex]
       
        return partSumForItem, oldPointLimit, newPointLimit, skipCount
   
    def getItemIndex(self, lessItemsRange, i, allAsc):
        return lessItemsRange - i if allAsc else i - 1

    def solve(self):

        size, items, forceUseLimits, iterCounter = self.size, self.items, self.forceUseLimits, self.iterCounter

        size, count, sum, lessCountSum, partialSums, starting, ending, isSuperIncreasing, superIncreasingItems, allAsc, allDesc  = self.preProcess(size, items, forceUseLimits, iterCounter)

        cornerCasesCheck = self.checkCornerCases(size, items, sum, lessCountSum, iterCounter)

        if  cornerCasesCheck:
            return cornerCasesCheck

        if self.doSolveSuperInc and isSuperIncreasing:
            return self.solveSuperIncreasing(size, items, starting, ending, count, allAsc, iterCounter)

        lessItemsRange = 0

        if allAsc:
            lessItemsRange = ending + 1 - starting

        DP = self.createDP(count, starting)

        resultI, resultP = 1, 1

        circularPointQueue = deque()

        maxValue, prevPointCount, newPointCount = -sys.maxsize, 0, 0

        if self.printInfo:
            print(f"1-0 knapsack: N={count}, Use limits={doUseLimits}, allAsc={allAsc}, allDesc={allDesc}, forceUseLimits={forceUseLimits}")

        for i in range(starting, ending + 1):

            itemIndex = self.getItemIndex(lessItemsRange, i, allAsc)

            DP[i] = defaultdict()

            prevPointCount, newPointCount = newPointCount, prevPointCount
            newPointCount = 0    

            itemValue, itemWeight = items       [itemIndex], items[itemIndex]
            prevDP,    curDP      = DP          [i - 1],    DP[i]

            self.totalPointCount += prevPointCount

            itemLimit, oldPointLimit, newPointLimit, skipCount  = self.getLimits(size, itemIndex, items, partialSums, superIncreasingItems)
           
            for p in self.getPoints(itemWeight, size, circularPointQueue, itemLimit, oldPointLimit, newPointLimit, prevPointCount, prevDP, skipCount, iterCounter):

                curValue    =  self.getValue(p, prevDP)  
                posblValue  =  self.getPossibleValue(p - itemWeight, itemValue, prevDP)

                if posblValue and curValue < posblValue and posblValue <= size:
                    curValue = posblValue

                self.setValue(curDP, p, curValue, iterCounter)

                if  maxValue < curValue:
                    resultP = p
                    resultI = i
                    maxValue = curValue            

                if  size == curValue:
                    return self.backTraceItems(DP, resultI, resultP, items, lessItemsRange, allAsc, iterCounter)

                newPointCount += 1
           
            if self.printInfo:
                print(f"| {i - 1} | {newPointCount} | {round(iterCounter[0])} |")

        return  self.backTraceItems(DP, resultI, resultP, items, lessItemsRange, allAsc, iterCounter)

