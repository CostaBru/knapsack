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

# Copyright Dec 2020 Konstantin Briukhnov (kooltew at gmail.com) (@CostaBru). San-Francisco Bay Area.

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

verbose = True
printPct = False
doSolveSuperInc = True
doUseLimits = True
printToFile = True

def partitionN(items, sizesOrPartitions, groupSize, O, optimizationLimit = -1):
    solver = partitionSolver(items, sizesOrPartitions, groupSize, O, optimizationLimit)
    return solver.solve()

class partitionItem:
    def __init__(self, itemSet, sizes):
        self.Items = itemSet
        self.Sizes = sizes
    
    def __len__(self):
        return len(self.Items)

    def __str__(self):
        return f"| Size: {self.Sizes}, Items: {self.Items} |"

    def __repr__(self):
            return f"| Size: {self.Sizes}, Items: {self.Items} |"

class partitionSolver():

    def __init__(self, items, sizesOrPartitions, groupSize, O, optimizationLimit) -> None:
        self.items = items
        self.sizesOrPartitions = sizesOrPartitions
        self.groupSize = groupSize
        self.O = O
        self.optimizationLimit = optimizationLimit

    def prepareGrouping(self, A, O):

        group = defaultdict(list)

        for c in A:
            group[c].append(c) 
        
        O[0] += len(A)

        return group
    
    def groupItems(self, group, O):

        allUnique = True
        nonUniqueList = defaultdict(int)

        for k in group.keys():        

            nonUniqueList[k] += len(group[k])
            
            if len(group[k]) > 1:
                allUnique = False

        O[0] += len(group)

        return allUnique, nonUniqueList

    def getSingleDuplicatePartitions(self, items, count, sizes, groupSize, O):

        quotientResult, remainderResult  = [], partitionItem([], [])

        if groupSize == 0:
            stack = list(items)
            currentQuotient = []
            ls = list(sizes)

            while len(ls) > 0 and len(stack) > 0:
                size = ls.pop()
                qs = 0
                while len(stack) > 0:
                    item = stack.pop()

                    qs += item

                    if qs <= size:
                        currentQuotient.append(item)
                    
                    if qs >= size:
                        qs = 0
                        quotientResult.append(partitionItem(currentQuotient, [size]))
                        currentQuotient = []

            remainderList = currentQuotient 

            for item in stack:
                remainderList.append(item)

            remainderResult = partitionItem(remainderList, ls)

            return  quotientResult, remainderResult, 0
                      
        else:

            stack = list(items)
            currentQuotient = []

            ls = list(sizes)

            while len(stack) > 0:
                item = stack.pop()
                if len(currentQuotient) < groupSize:
                    currentQuotient.append(item)
                    if len(currentQuotient) == groupSize:
                        quotientResult.append(partitionItem(currentQuotient, [groupSize * currentQuotient[0]]))
                        currentQuotient = []  

            remainderResult = currentQuotient 

            for item in stack:
                remainderResult.append(item)

            return  quotientResult, partitionItem(remainderResult, [len(remainderResult) // groupSize]), 0 

    def optimizePartitions(self, quotients, remainder, sizes, groupSize, optimizationLimit, O):

        def mergeTwoSortedReversedIter(itemSet1, itemSet2):

            moveL1, moveL2 = True, True
            n1,     n2     = True, True

            iter_1 = iter(itemSet1) 
            iter_2 = iter(itemSet2)

            val1,   val2   = 0, 0

            while n1 or n2:      

                if moveL1:
                    val1 = next(iter_1, -sys.maxsize)
                
                if moveL2:
                    val2 = next(iter_2, -sys.maxsize)

                n1 = val1 > -sys.maxsize
                n2 = val2 > -sys.maxsize
                
                if n1 and n2:
                    if val1 > val2:
                        yield val1
                        moveL1 = True
                        moveL2 = False                        
                    elif val2 > val1:
                        yield val2
                        moveL1 = False 
                        moveL2 = True                            
                    else:
                        yield val1
                        yield val2
                        moveL1 = True
                        moveL2 = True
                elif n1 and not n2:
                    yield val1
                    moveL1 = True
                    moveL2 = False
                elif n2 and not n1:
                    yield val2
                    moveL1 = False 
                    moveL2 = True   

        class partitionPoint:
            def __init__(self, itemSet, sizes, itemIndexes=None):
                self.Items = tuple(itemSet)
                self.Sizes = sizes 
                self.Indexes = set()
                if itemIndexes:
                    self.Indexes.update(itemIndexes)   
            
            def GetPartitions(self):
                return len(self.Sizes)

            def __str__(self):
                return f"< Size: {self.Sizes}, Items: {self.Items}, QI: {self.Indexes} >"
        
            def __repr__(self):
                return f"< Size: {self.Sizes}, Items: {self.Items}, QI: {self.Indexes} >"
                
            def __add__(self, item): 

                resultIndexes = set(self.Indexes)
                resultSizes = list(self.Sizes)
                
                for ind in item.Indexes:
                    resultIndexes.add(ind)

                for s in item.Sizes:
                    resultSizes.append(s)

                iters = mergeTwoSortedReversedIter(self.Items, item.Items)

                resultSet = list(iters)

                return partitionPoint(resultSet, resultSizes, resultIndexes)        
            
            def __eq__(self, other):
                return self.Items == other.Items and self.Sizes == other.Sizes

            def __hash__(self):
                return hash(self.Items)

        def optimize(p, remainderItem, groupSize, limit, O):

            newSet = []
            newSizes = []
            
            if limit <= 2:
                newSet = list(mergeTwoSortedReversedIter(remainderItem.Items, p.Items))
                newSizes = list(remainderItem.Sizes)

                for s in p.Sizes:
                    newSizes.append(s)

                O[0] += len(p.Items) + len(remainderItem.Items)
                O[0] += len(p.Sizes) + len(remainderItem.Sizes)  

            elif limit == 3:
                newSet = list(remainderItem.Items)
                random.shuffle(newSet)

                newSizes = list(remainderItem.Sizes)
                random.shuffle(newSizes)

                for s in reversed(p.Sizes):
                    newSizes.append(s)
                
                for r in reversed(p.Items):
                    newSet.append(r) 

                O[0] += len(p.Items) + len(remainderItem.Items)
                O[0] += len(p.Sizes) + len(remainderItem.Sizes)          
            else:
                for s in p.Sizes:
                    newSizes.append(s)
                
                for s in remainderItem.Sizes:
                    newSizes.append(s)

                for r in p.Items:
                    newSet.append(r) 
                
                for r in remainderItem.Items:
                    newSet.append(r) 
                
                random.shuffle(newSet)
                random.shuffle(newSizes)

                O[0] += (len(p.Items) + len(remainderItem.Items)) * 2
                O[0] += (len(p.Sizes) + len(remainderItem.Sizes)) * 2

            return  self.divideSet(newSet, newSizes, groupSize, O)

        def getPoints(i, item, uniqueSet, limit):

            itemPoint = partitionPoint(item.Items, item.Sizes)
            itemPoint.Indexes.add(i)

            if itemPoint not in uniqueSet: 
                yield itemPoint

            for prevPoint in uniqueSet:
                if prevPoint.GetPartitions() + itemPoint.GetPartitions() < limit:                
                    newPoint = itemPoint + prevPoint
                    if newPoint not in uniqueSet:
                        yield newPoint

        def incOForPoint(O, p):
            O[0] += 1
            O[0] += len(p.Items)
            O[0] += len(p.Sizes)
            O[0] += len(p.Indexes)

        def backTrace(optimizationsMade, remainderItem, originalQuotient, originalRemainder, optimizationCount, O):

            if len(optimizationsMade) == 0:
                return originalQuotient, originalRemainder, optimizationCount

            bestPartition = list()
            skipIndexes = set()

            for optPoint in optimizationsMade:
                skipIndexes.update(optPoint.Indexes)
                O[0] += 2 * len(optPoint.Items)
                bestPartition.append(partitionItem(list(reversed(optPoint.Items)), optPoint.Sizes))
                incOForPoint(O, optPoint)

            optimizationCount += len(optimizationsMade)
            
            for i in range(len(originalQuotient)):
                if i in skipIndexes:
                    continue
                it = originalQuotient[i]
                bestPartition.append(it)
                O[0] += 1

            return bestPartition, remainderItem, optimizationCount

        def incOForPartition(O, optItem):
            O[0] += 1
            O[0] += len(optItem.Items)
            O[0] += len(optItem.Sizes)

        def prepareQuotientsAndRemainder(quotients, groupSize, remainder, limit, O):

            if limit == 0:
                if groupSize == 0:
                    remainder.Items.sort(reverse = True)

                    O[0] += len( remainder.Items) * math.log2(len( remainder.Items))
                    O[0] += 1

                for q in quotients:
                    q.Items.sort(reverse = True)

                    O[0] += len( q.Items) * math.log2(len( q.Items))
                    O[0] += 1         

            elif limit > 2:
                random.shuffle(quotients)
                random.shuffle(remainder.Items)

                O[0] += len(quotients)     
                O[0] += len(remainder.Items)     
            else: 
                random.shuffle(quotients)
                random.shuffle(remainder.Items)

                O[0] += len(quotients)       
                O[0] += len(remainder.Items)     
            
        prepareQuotientsAndRemainder(quotients, groupSize, remainder,  0, O)    

        remainderItem = remainder
        minRemiderLen = len(remainderItem) 

        startLayer = 1
        endLayer = startLayer + (len(sizes) // 2)

        if optimizationLimit > 0:
            endLayer = optimizationLimit

        optimizationCount = 0

        for limit in range(startLayer, endLayer):
            
            optimizedIndexes,  uniqueSet = set(), set()
            optimizationsMade, newPoints = [], []

            remainderItem = remainder
            minRemiderLen = len(remainderItem) 

            if verbose and limit > 0:
                print(f"performing optimizations at the same time is limited by: {limit}; quotients: {len(quotients)} reminder len {len(remainder)}")

            for i in range(len(quotients)):

                item = quotients[i]

                uniqueSet.update(newPoints)
                newPoints.clear()

                for p in getPoints(i, item, uniqueSet, limit):          

                    if len(optimizedIndexes) > 0 and not p.Indexes.isdisjoint(optimizedIndexes):
                        continue

                    optQuotient, optReminder, _ = optimize(p, remainderItem, groupSize, limit, O) 

                    incOForPoint(O, p)

                    if  len(optReminder) < minRemiderLen or len(optReminder.Sizes) < len(remainderItem.Sizes):
                       
                        for optItem in optQuotient:
                            optimizationsMade.append(partitionPoint(optItem.Items, optItem.Sizes, p.Indexes))
                            optimizedIndexes.update(p.Indexes)
                            incOForPartition(O, optItem)
                        
                        remainderItem = optReminder
                        minRemiderLen = len(remainderItem) 

                        if len(optReminder.Sizes) == 0:
                            return backTrace(optimizationsMade, remainderItem, quotients, remainder, optimizationCount, O)
                    else:
                        newPoints.append(p)

                    if  minRemiderLen == 0:
                        return backTrace(optimizationsMade, remainderItem, quotients, remainder, optimizationCount, O)

            if len(optimizedIndexes) > 0:
                quotients, remainder, optimizations = backTrace(optimizationsMade, remainderItem, quotients, remainder, optimizationCount, O)
                optimizationCount += optimizations
            
            prepareQuotientsAndRemainder(quotients, groupSize, remainder, limit, O) 
                
        return  quotients, remainder, optimizationCount

    def sortDuplicatesForPartitioning(self, group, count, nonUniqueList, O):
        A_sort = []

        keys = list(group.keys())
        keysCount = len(keys)
        O[0] += keysCount

        keys.sort(reverse=True)
        O[0] += keysCount * math.log2(keysCount)

        i = 0
        removeKeys = []
        while len(nonUniqueList) > 0:

            kl = keys if i % 3 == 0 else reversed(keys)
            i += 1

            for key in kl:

                if  key in nonUniqueList and nonUniqueList[key] > 0:
                    A_sort.append(key)
                    nonUniqueList[key] -= 1
                    
                    if  nonUniqueList[key] <= 0:
                        del nonUniqueList[key]
                        removeKeys.append(key)
            
            if len(removeKeys) > 0:
                for k in removeKeys:
                    keys.remove(k) 
                removeKeys.clear()
                
        O[0] += count

        return A_sort

    def partitionOverSameCountDuplicates(self, nonUniqueList, sizes, groupSize, optimizationLimit, O):

        sameCount = True

        cnt = next(iter(nonUniqueList.values()))

        for k in nonUniqueList.keys():
            if nonUniqueList[k] != cnt:
                sameCount = False
                O[0] += 1
                break

        if sameCount:

            nonUKeys = list(nonUniqueList.keys())
            newLen = len(nonUKeys)
            O[0] += newLen

            nonUKeys.sort(reverse=True)
            O[0] += newLen * math.log2(newLen)

            newSizes = []

            s = sum(nonUKeys)
            n = len(sizes)

            newN = n // cnt

            if isinstance(s, int):
                size = sum(nonUKeys) // newN
                newSizes = [size] * newN
            else:
                size = Decimal(Decimal(s) / Decimal(Decimal(n) / Decimal(cnt)))
                newSizes = [size] * newN

            O[0] += newLen
            
            quotients, remainder, optCount = self.divideSet(nonUKeys, newSizes, groupSize, O)

            quotientResult, remainderResult  = [], []

            for i in range(cnt):
                for item in quotients:
                    quotientResult.append(item.Items)
                for rem in remainder.Items:
                    remainderResult.append(rem)

            if  len(remainderResult) == 0 or len(quotientResult) == len(sizes) or len(quotients) == 0:
                return quotientResult, remainderResult, optCount

            return self.optimizePartitions(remainderResult, quotientResult, sizes, groupSize, optimizationLimit, O)

        return None

    def divideSet(self, items, sizes, groupSize, O, forceUseLimits = False):    

        quotients = []
        reminderSizes = []
        reminderItems = items

        ls = len(sizes)

        for n in range(ls, 0, -1):

            size = sizes[n - 1]

            if groupSize > 0:

                if n == 1:

                    O[0] += len(reminderItems)

                    remSum = sum(reminderItems)

                    if remSum == size and len(reminderItems) == groupSize:
                        quotients.append(partitionItem(list(reminderItems), [size])) 
                        reminderItems.clear()
                        break  
                    elif remSum < size:
                        reminderSizes.append(size)
                        break  

                dimensions, constraints  = [wPoint2(item, 1) for item in reminderItems], wPoint2(size, groupSize)
                O[0] += len(reminderItems)   

                opt, optDims, optValues = knapsackNSolver(constraints, dimensions, reminderItems, O, wPoint2(0, 0), forceUseLimits).solve()

                if (opt[0] == size and opt[1] == groupSize): 

                    quotients.append(partitionItem(optValues, [size]))

                    for toRemove in optValues:
                        reminderItems.remove(toRemove)

                    O[0] += len(optValues)
                else:
                    reminderSizes.append(size)
            else:

                if n == 1:

                    O[0] += len(reminderItems)

                    remSum = sum(reminderItems)

                    if remSum == size:
                        quotients.append(partitionItem(list(reminderItems), [size])) 
                        reminderItems.clear()
                        break  
                    elif remSum < size:
                        reminderSizes.append(size)
                        break

                optimal, optimalList = subsKnapsack(size, reminderItems,  O, forceUseLimits)

                if optimal == size:          

                    quotients.append(partitionItem(optimalList, [size]))

                    for toRemove in optimalList:
                        reminderItems.remove(toRemove)  

                    O[0] += len(optimalList)    
                else:
                    reminderSizes.append(size)

        return quotients, partitionItem(reminderItems, reminderSizes), 0

    def getSizes(self, items, sizesOrPartitions):
        sizes = sizesOrPartitions

        sameSizes = isinstance(sizesOrPartitions, int)

        if sameSizes:

            itemsSum = sum(items)

            if isinstance(itemsSum, int):
                size = itemsSum // sizesOrPartitions
                sizes = [size] * sizesOrPartitions
            else:
                size = Decimal(itemsSum / Decimal(sizesOrPartitions))
                sizes = [size] * sizesOrPartitions

        return sizes, sameSizes

    def solve(self):

        items, sizesOrPartitions, groupSize, O, optimizationLimit = self.items, self.sizesOrPartitions, self.groupSize, self.O, self.optimizationLimit

        count = len(items)
        sizes, sameSizes = self.getSizes(items, sizesOrPartitions)

        if  count < len(sizes):
            return [], [], 0
        
        group = self.prepareGrouping(items, O)   
        allUnique, nonUniqueList = self.groupItems(group, O)

        if len(nonUniqueList) == 1:
            return self.getSingleDuplicatePartitions(items, count, sizes, groupSize, O)

        quotients, remainder, optCount = [], [], 0

        if  allUnique:

            items = list(items)
            items.sort(reverse = True)

            O[0] += count * math.log2(count)
            O[0] += count 

            quotients, remainder, optCount = self.divideSet(items, sizes, groupSize, O)
        else:
            if  len(nonUniqueList) > len(sizes) and groupSize == 0 and sameSizes:
                partResult = self.partitionOverSameCountDuplicates(nonUniqueList, sizes, 0, optimizationLimit, O)
                if partResult:
                    return partResult

            sortedDuplicates = self.sortDuplicatesForPartitioning(group, count, nonUniqueList, O)
            quotients, remainder, optCount = self.divideSet(sortedDuplicates, sizes, groupSize, O, forceUseLimits = True)    
    
        if  len(remainder) == 0 or len(quotients) == len(sizes) or len(quotients) == 0:
            return quotients, remainder, optCount

        return self.optimizePartitions(quotients, remainder, sizes, groupSize, optimizationLimit, O)   

def subsKnapsack(size, items, O, forceUseLimits = False):
    solver = subsetSumKnapsackSolver(size, items, O, forceUseLimits)
    return solver.solve()

class subsetSumKnapsackSolver:

    def __init__(self, size, items, O, forceUseLimits = False):
        self.size = size
        self.items = items
        self.O = O
        self.forceUseLimits = forceUseLimits
        self.DP = None
        # inner stat
        self.skippedPointsByMap = 0
        self.skippedPointsByLimits = 0
        self.skippedPointsBySize = 0
        self.totalPointCount = 0

    def prepare(self, size, items, forceUseLimits, O):
        
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
                partialSums2[iBack] = itemSum1   

                if allDesc:
                    if not prevItem1 <= item1:
                        allDesc = False
                
                if allAsc:
                    if prevItem1 < item1:
                        allAsc = False

                if i > 0:
                    superIncreasingItems1[iBack] = superIncreasingItem1
                    superIncreasingItems2[iBack] = superIncreasingItem2

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
                      
            if allDesc or forceUseLimits:
                partialSums = partialSums1
                superIncreasingItems = superIncreasingItems1
                isSuperIncreasing = isSuperIncreasing1
                itemSum = itemSum1
            elif allAsc:                
                partialSums = partialSums2
                superIncreasingItems = superIncreasingItems2 
                isSuperIncreasing = isSuperIncreasing2 
                itemSum = itemSum2 
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
        
        O[0] += count
        return size, count, itemSum, lessCountSum, partialSums, starting, ending, isSuperIncreasing, superIncreasingItems, allAsc, allDesc

    def checkCornerCases(self, size, items, sum, lessCountSum, O):        

        if  lessCountSum == 0:
            return [0,[]]
        
        if  lessCountSum <= size:
            
            lessCountItems = []

            for item in items:
                itemWeight = item

                if itemWeight <= size:
                    lessCountItems.append(itemWeight)

            O[0] += len(lessCountItems)

            return [lessCountSum, lessCountItems]

        if  sum <= size:
            return [sum, items]  

        return None      
  
    def yieldOrPushBack(self, circularPointQuene, newPoint, greaterQu):
        if len(circularPointQuene) > 0:
                peek = circularPointQuene[0]

                if newPoint < peek:                   
                    yield newPoint
                    circularPointQuene.append(newPoint)
                else:
                    if len(greaterQu) > 0 and newPoint < greaterQu[0]:
                        greaterQu.insert(0, newPoint)
                    else:
                        greaterQu.append(newPoint)
        else:
            yield newPoint
            circularPointQuene.append(newPoint)         

    def getPoints(self, itemWeight, size, circularPointQuene, itemLimit, oldPointLimit, newPointLimit, prevCyclePointCount, uniquePointSet, skipCount):
       

        # merges ordered visited points with new points with keeping order in O(N) using single circular queue. 
        # each getPoints method call starts fetching visited points from qu start, pops visited point and pushes new point and visited to the end of qu in ASC order.
        # we skip new point if it in list already
        # skips points if they will not contribute to optimal solution

        greaterQu = deque()

        useItemItself = itemLimit >= size // 2

        if useItemItself and not itemWeight in uniquePointSet:
            for p in self.yieldOrPushBack(circularPointQuene, itemWeight, greaterQu):
                yield p
        else:
            if useItemItself:
                self.skippedPointsByMap += skipCount 
            else:
                self.skippedPointsByLimits += skipCount

        for i in range(prevCyclePointCount):

            oldPoint = circularPointQuene.popleft()             

            while len(greaterQu) > 0 and greaterQu[0] < oldPoint:
                quPoint = greaterQu.popleft()
               
                yield quPoint 
                circularPointQuene.append(quPoint)

            if  oldPoint >= oldPointLimit:
                for p in self.yieldOrPushBack(circularPointQuene, oldPoint, greaterQu):
                    yield p
            else:
                self.skippedPointsByLimits  += skipCount   
         
            newPoint = oldPoint + itemWeight

            if  newPoint < newPointLimit:
                self.skippedPointsByLimits += skipCount
                continue

            if newPoint <= size:   

                if not newPoint in uniquePointSet:
                    for p in self.yieldOrPushBack(circularPointQuene, newPoint, greaterQu):
                        yield p
                else:
                    self.skippedPointsByMap += skipCount
            else:
                self.skippedPointsBySize += skipCount 
        
        while len(greaterQu) > 0:

            quPoint = greaterQu.popleft()

            yield quPoint 
            circularPointQuene.append(quPoint)    

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

    def setValue(self, curDP, p, curVal, O):
        curDP[p] = curVal     
        O[0] += 1

    def backTraceItems(self, DP, resultI, resultP, items, O):
       
        opt = 0
        res = DP[resultI][resultP]
        optWeights = []
        point = resultP

        self.totalPointCount += len(DP[resultI])

        if printPct:
            print(f"Skipped points by MAP: {self.skippedPointsByMap}, by LIMITS: {self.skippedPointsByLimits}; by SIZE: {self.skippedPointsBySize};  Max points: {(2 ** len(items)) if len(items) < 15 else -1}; Total points: {self.totalPointCount}; N={len(items)}, Use limits: {doUseLimits};")

        for i in range(resultI, 0, -1): 
           
            O[0] += 1

            if res <= 0: 
                break      

            prevDP = DP[i - 1]

            skip = False

            if point in prevDP:
                skip = res == prevDP[point]
           
            if not skip:       
                item = items[i - 1] 
                optWeights.append(item)   

                res   -= item
                point -= item

               
                opt += item

        return opt, optWeights

    def createDP(self, count, starting):
        self.DP    = [None] * (count + 1)
        self.DP[starting - 1] = defaultdict()
        return self.DP

    def solveSuperIncreasing(self, size, items, starting, ending, count, allAsc, O):

        def indexLargestLessThanDesc(items, item, lo, hi, O):   

            if item == 0:
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

            if item == 0:
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

        resultItems = []
        resultSum = 0
        index = binSearch(items, size, starting - 1, ending - 1, O) 

        while index is not None:
            value = items[index]
            resultItems.append(value)
            resultSum += value
            if allAsc:
                index = binSearch(items, size - resultSum, starting - 1, index - 1, O)
            else:
                index = binSearch(items, size - resultSum, index + 1, ending - 1, O)
            O[0] += 1
        
        if verbose:
            print(f"Superincreasing subset sum solver called for size {size} and count {count}. ASC={allAsc}")
        
        return resultSum, resultItems
    
    def getLimits(self, size, i, items, partialSums, superIncreasingItems):

        skipCount = 2 ** (len(items) - i)

        if not doUseLimits:
            return sys.maxsize, -sys.maxsize, -sys.maxsize, skipCount

        partSumForItem = partialSums[i - 1]
        superIncreasingItem = superIncreasingItems[i - 1]

        newPointLimit = size - partSumForItem
        oldPointLimit = newPointLimit

        if doSolveSuperInc and superIncreasingItem:
            oldPointLimit = newPointLimit + items[i - 1]
        
        return partSumForItem, oldPointLimit, newPointLimit, skipCount
    
    def solve(self):

        size, items, forceUseLimits, O = self.size, self.items, self.forceUseLimits, self.O

        size, count, sum, lessCountSum, partialSums, starting, ending, isSuperIncreasing, superIncreasingItems, allAsc, allDesc  = self.prepare(size, items, forceUseLimits, O)

        cornerCasesCheck = self.checkCornerCases(size, items, sum, lessCountSum, O)

        if  cornerCasesCheck:
            return cornerCasesCheck

        if doSolveSuperInc and isSuperIncreasing:
            return self.solveSuperIncreasing(size, items, starting, ending, count, allAsc, O) 

        if allAsc:
            starting, ending = count - ending + 1, count
            items = list(reversed(items))
            O[0] += len(items) 

        DP = self.createDP(count, starting)

        resultI, resultP = 1, 1

        circularPointQuene = deque()

        maxValue, prevPointCount, newPointCount = -sys.maxsize, 0, 0

        if printPct:
            print(f"1-0 knapsack: N {count}, Use limits: {doUseLimits}, allAsc={allAsc}, allDesc={allDesc}, forceUseLimits={forceUseLimits}")

        for i in range(starting, ending + 1):
        
            DP[i] = defaultdict()

            prevPointCount, newPointCount = newPointCount, prevPointCount
            newPointCount = 0     

            itemValue, itemWeight = items       [i - 1], items[i - 1]
            prevDP,    curDP      = DP          [i - 1],    DP[i]

            self.totalPointCount += prevPointCount

            if printPct:
                print(f"| {i - 1} | {prevPointCount} | {round(O[0])} |")

            itemLimit, oldPointLimit, newPointLimit, skipCount  = self.getLimits(size, i, items, partialSums, superIncreasingItems)

            for p in self.getPoints(itemWeight, size, circularPointQuene, itemLimit, oldPointLimit, newPointLimit, prevPointCount, prevDP, skipCount):          

                curValue    =  self.getValue(p, prevDP)  
                posblValue  =  self.getPossibleValue(p - itemWeight, itemValue, prevDP) 

                if posblValue and curValue < posblValue and posblValue <= size:
                    curValue = posblValue

                self.setValue(curDP, p, curValue, O)

                if  maxValue < curValue:
                    resultP = p
                    resultI = i
                    maxValue = curValue            

                if  size == curValue:
                    return self.backTraceItems(DP, resultI, resultP, items, O)  

                newPointCount += 1 

        return self.backTraceItems(DP, resultI, resultP, items, O)

def knapsack(size, weights, values, O, forceUseLimits = False):
    solver = knapsackSolver(size, weights, values, O, forceUseLimits)
    return solver.solve()

class knapsackSolver:
    def __init__(self, size, weights, values, O, forceUseLimits = False):
        self.size = size
        self.weights = weights
        self.values = values
        self.O = O
        self.forceUseLimits = forceUseLimits
        self.DP = None
        # inner stat
        self.skippedPointsByMap = 0
        self.skippedPointsByLimits = 0
        self.skippedPointsBySize = 0
        self.totalPointCount = 0
    
    def prepare(self, constraints, items, values, forceUseLimits, O):
        
        count = len(items)
        itemSum1, itemSum2, lessCountSum = 0, 0, 0

        lessSizeItems, lessSizeValues, lessSizeItemsIndex = [], [], []

        partialSums1, superIncreasingItems1 = [], [False]
        partialSums2, superIncreasingItems2 = [], [False] 

        isSuperIncreasing1, isSuperIncreasing2 = True, True
        allValuesEqual, allValuesEqualToConstraints = True, True
        allDesc, allAsc = True, True

        lessCount = 0

        if count > 0 :
            
            prevItem1 = items[-1]
            prevValue1 = values[-1]

            for i in range(0, count):

                item2 = items[i]
                itemValue2 = values[i]

                iBack = count - i - 1

                item1 = items[iBack]               

                superIncreasingItem1 = False
                superIncreasingItem2 = False

                if item1 <= constraints:

                    if item1 < itemSum1:
                        isSuperIncreasing1 = False
                    else:
                        superIncreasingItem1 = True
                
                if item2 <= constraints:

                    if item2 < itemSum2:
                        isSuperIncreasing2 = False
                    else:
                        superIncreasingItem2 = True
                
                if allValuesEqual and prevValue1 != itemValue2:
                    allValuesEqual = False
                
                if allValuesEqualToConstraints and item2 != itemValue2:
                    allValuesEqualToConstraints = False

                itemSum1 += item1
                itemSum2 += item2

                if allValuesEqual or allValuesEqualToConstraints or forceUseLimits:
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

                if item2 <= constraints:
                    lessSizeItems.append(item2)                
                    lessSizeValues.append(itemValue2)  
                    lessSizeItemsIndex.append(i)

                    lessCountSum += item2
                    lessCount += 1   

                prevItem1 = item1
            
            partialSums = []
            superIncreasingItems = []
            isSuperIncreasing = False
            itemSum = itemSum2

            canUsePartialSums = allValuesEqual or allValuesEqualToConstraints or forceUseLimits
        
            if (allDesc and canUsePartialSums) or forceUseLimits:
                partialSums = partialSums1
                superIncreasingItems = superIncreasingItems1
                isSuperIncreasing = isSuperIncreasing1
                itemSum = itemSum1

                partialSums.reverse()
                superIncreasingItems.reverse()

            elif allAsc and canUsePartialSums:
                partialSums = partialSums2
                superIncreasingItems = superIncreasingItems2 
                isSuperIncreasing = isSuperIncreasing2 
                itemSum = itemSum2     
                
                partialSums.reverse()
                superIncreasingItems.reverse()             
            else:
                partialSums = [sys.maxsize] * lessCount
                superIncreasingItems = [False] * lessCount
        else:
            partialSums = []
            superIncreasingItems = []
            isSuperIncreasing = False
            itemSum = itemSum2

        constraints = min(itemSum, constraints)
        
        O[0] += count
        return constraints, lessCount,  lessSizeItems, lessSizeValues, lessSizeItemsIndex, itemSum, lessCountSum, partialSums, isSuperIncreasing, superIncreasingItems, allAsc, allDesc

    def checkCornerCases(self, size, lessSizeItems, lessSizeValues, lessSizeItemsIndex, lessCountSum, itemSum):        

        if  lessCountSum == 0:
            return 0,[],[],[]
        
        if  lessCountSum <= size:
            return lessCountSum, lessSizeItems, lessSizeValues, lessSizeItemsIndex

        if  itemSum <= size:
            return itemSum, lessSizeItems, lessSizeValues, lessSizeItemsIndex

        return None      
     
    def yieldOrPushBack(self, circularPointQuene, newPoint, greaterQu):
        if len(circularPointQuene) > 0:
                peek = circularPointQuene[0]

                if newPoint < peek:                   
                    yield newPoint
                    circularPointQuene.append(newPoint)
                else:
                    if len(greaterQu) > 0 and newPoint < greaterQu[0]:
                        greaterQu.insert(0, newPoint)
                    else:
                        greaterQu.append(newPoint)
        else:
            yield newPoint
            circularPointQuene.append(newPoint)     

    def getPoints(self, itemWeight, size, circularPointQuene, itemLimit, oldPointLimit, newPointLimit, prevCyclePointCount, uniquePointSet, skipCount):
        
        # merges ordered visited points with new points with keeping order in O(N) using single circular queue. 
        # each getPoints method call starts fetching visited points from qu start, pops visited point and pushes new point and visited to the end of qu in ASC order.
        # we skip new point if it in list already

        useItemItself = itemLimit >= size // 2

        greaterQu = deque()

        if useItemItself and not itemWeight in uniquePointSet:         
            for p in self.yieldOrPushBack(circularPointQuene, itemWeight, greaterQu):
                yield p
        else:
            if useItemItself:
                self.skippedPointsByMap += skipCount
            else:
                self.skippedPointsByLimits += skipCount

        for i in range(prevCyclePointCount):

            oldPoint = circularPointQuene.popleft()             

            while len(greaterQu) > 0 and greaterQu[0] < oldPoint:

                quPoint = greaterQu.popleft()
               
                yield quPoint 
                circularPointQuene.append(quPoint)

            if  oldPoint >= oldPointLimit:

                for p in self.yieldOrPushBack(circularPointQuene, oldPoint, greaterQu):
                    yield p

            newPoint = oldPoint + itemWeight

            if  newPoint < newPointLimit:
                self.skippedPointsByLimits += skipCount
                continue

            if newPoint <= size: 

                if not newPoint in uniquePointSet:
                    for p in self.yieldOrPushBack(circularPointQuene, newPoint, greaterQu):
                        yield p
                else:
                    self.skippedPointsByMap += skipCount
            else:
                self.skippedPointsBySize += skipCount
        
        while len(greaterQu) > 0:

            quPoint = greaterQu.popleft()

            yield quPoint 
            circularPointQuene.append(quPoint)

    def getValue(self, p, prevDP):

        if p in prevDP:
            cur = prevDP[p]
            return cur[0], cur[1]
      
        return 0, 0
      
    def getPossibleValue(self, point, itemValue, itemWeight,  dp):

        if point in dp:
            cur = dp[point]
            return cur[0] + itemValue, cur[1] + itemWeight

        if point < 0:
            return None, None
        
        return itemValue, itemWeight

    def setValue(self, curDP, p, curVal, curW,  O):
        curDP[p] = (curVal, curW)               
        O[0] += 1

    def backTraceItems(self, DP, resultI, resultP, items, values, itemsIndex, O):
        opt = 0
        res = DP[resultI][resultP][0]
        optWeights, optValues, optIndex = [], [], []
        point = resultP

        self.totalPointCount += len(DP[resultI])

        if printPct:
            print(f"Skipped points by MAP: {self.skippedPointsByMap}, by LIMITS: {self.skippedPointsByLimits}; by SIZE: {self.skippedPointsBySize};  Max points: {(2 ** len(items)) if len(items) < 15 else -1}; Total points: {self.totalPointCount};")

        for i in range(resultI, 0, -1): 
           
            O[0] += 1

            if res <= 0: 
                break      

            dpw = DP[i - 1]

            skip = False

            if point in dpw:
                skip = res == dpw[point][0] 

            if not skip:       
                itemWeight, itemValue, itemIndex = items[i - 1], values[i - 1], itemsIndex[i - 1]   

                optWeights.append(itemWeight)
                optValues.append(itemValue)
                optIndex.append(itemIndex)

                res   -= itemValue
                point -= itemWeight

                opt += itemWeight

        return opt, optWeights, optValues, optIndex

    def createDP(self, count):
        self.DP    = [None] * (count + 1)
        self.DP[0] = defaultdict()
        return self.DP

    def solveSuperIncreasing(self, size, items, values, itemsIndex, count, allAsc, O):

        def indexLargestLessThanDesc(items, item, lo, hi, O):   

            if item == 0:
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

            if item == 0:
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
        resultIndex = []
        resultSum = 0
        index = binSearch(items, size, starting - 1, count - 1, O)

        while index is not None:
            item = items[index]
            value = values[index]
            resultItems.append(item)
            resultValues.append(value)
            resultIndex.append(itemsIndex[index])
            resultSum += item
            if allAsc:
                index = binSearch(items, size - resultSum, starting - 1, index - 1, O)
            else:
                index = binSearch(items, size - resultSum, index + 1, count - 1, O)

            O[0] += 1

        if verbose:
            print(f"Superincreasing 1-0 solver called for size {size} and count {count}.  ASC={allAsc}")
        
        return resultSum, resultItems, resultValues, resultIndex

    def getLimits(self, size, i, items, partialSums, superIncreasingItems):
        
        skipCount = 2 ** (len(items) - i)

        if not doUseLimits:
            return sys.maxsize, -sys.maxsize, -sys.maxsize, skipCount

        partSumForItem = partialSums[i - 1]
        superIncreasingItem = superIncreasingItems[i - 1]

        newPointLimit = size - partSumForItem
        oldPointLimit = newPointLimit

        if doSolveSuperInc and superIncreasingItem:
            oldPointLimit = newPointLimit + items[i - 1] 

        return partSumForItem, oldPointLimit, newPointLimit, skipCount

    def solve(self):
        
        size, weights, values, forceUseLimits, O = self.size, self.weights, self.values, self.forceUseLimits, self.O

        size, count, lessSizeItems, lessSizeValues, lessSizeItemsIndex, itemSum, lessCountSum, partialSums, superIncreasing, superIncreasingItems, allAsc, allDesc = self.prepare(size, weights, values, forceUseLimits, O)

        cornerCasesCheck = self.checkCornerCases(size, lessSizeItems, lessSizeValues, lessSizeItemsIndex, lessCountSum, itemSum)

        if  cornerCasesCheck:
            return cornerCasesCheck

        if doSolveSuperInc and superIncreasing:
            return self.solveSuperIncreasing(size, lessSizeItems, lessSizeValues, lessSizeItemsIndex, count, allAsc, O)

        if allAsc:
            lessSizeItems = list(reversed(lessSizeItems))
            lessSizeValues = list(reversed(lessSizeValues))
            O[0] += len(lessSizeItems) * 2

        DP = self.createDP(count)

        resultI, resultP = 1, 1

        circularPointQuene = deque()

        maxValue, prevPointCount, newPointCount = -sys.maxsize, 0, 0

        if printPct:
            print(f"1-0 knapsack: N {count}, Use limits: {doUseLimits}, allAsc={allAsc}, allDesc={allDesc}, forceUseLimits={forceUseLimits}")

        for i in range(1, count + 1):

            DP[i] = defaultdict()

            itemValue, itemWeight   = lessSizeValues[i - 1], lessSizeItems[i - 1]
            prevDP,    curDP        = DP    [i - 1],      DP[i]       

            prevPointCount, newPointCount = newPointCount, prevPointCount
            newPointCount = 0

            self.totalPointCount += prevPointCount

            if printPct:
                print(f"| {i - 1} | {prevPointCount} | {round(O[0])} |")

            itemLimit, oldPointLimit, newPointLimit, skipCount   = self.getLimits(size, i, lessSizeItems, partialSums, superIncreasingItems)

            for p in self.getPoints(itemWeight, size, circularPointQuene, itemLimit, oldPointLimit, newPointLimit, prevPointCount, prevDP, skipCount):          

                curValue,   curWeight   =  self.getValue(p,              prevDP) 
                posblValue, posblWeight =  self.getPossibleValue(p - itemWeight, itemValue, itemWeight, prevDP) 

                if posblValue and curValue < posblValue and posblWeight <= size:
                    curValue = posblValue
                    curWeight = posblWeight
                
                self.setValue(curDP, p, curValue, curWeight, O)

                if  maxValue < curValue:
                    resultP = p
                    resultI = i
                    maxValue = curValue
                
                newPointCount += 1

        return self.backTraceItems(DP, resultI, resultP, lessSizeItems, lessSizeValues, lessSizeItemsIndex, O) 

class wPoint:
    def __init__(self, dimensions):
        self.dimensions = tuple(dimensions)

    def createNew(self, tuples):
        return wPoint(tuples)
    
    def getDimension(self, index):
        return self.dimensions[index]
    
    def getDimensions(self):
        return self.dimensions 

    def __str__(self):
        return str(self.dimensions)
    
    def __repr__(self):
        return str(self.dimensions)

    def firstDimensionEqual(self, number):
        return self.dimensions[0] == number
    
    def getSize(self):
        return len(self.dimensions)

    def divideBy(self, number):

        l = len(self.dimensions)

        newDim = [0] * l

        for i in range(l):
            newDim[i] = self.dimensions[i] / number

        return wPoint(newDim) 
    
    def adjustMin(self, other):
        l = len(self.dimensions)

        newDim = [0] * l

        for i in range(l):
            newDim[i] = min(self.dimensions[i], other.dimensions[i])
        
        return wPoint(newDim) 
    
    def __add__(self, item): 

        l = len(self.dimensions)

        newDim = [0] * l

        for i in range(l):
            newDim[i] = self.dimensions[i] + item.dimensions[i]

        return wPoint(newDim) 
    
    def __sub__(self, item): 

        l = len(self.dimensions)
        newDim = [0] * l

        for i in range(l):
            newDim[i] = self.dimensions[i] - item.dimensions[i]

        return wPoint(newDim)  
        
    # <
    def __lt__(self, other):
        l = len(self.dimensions)

        allLess = False
        for i in range(l):

            if self.dimensions[i] == other.dimensions[i]:
                continue

            if self.dimensions[i] < other.dimensions[i]:                 
                allLess = True
            else:
                return False

        return allLess  

    # <=
    def __le__(self, other):
        l = len(self.dimensions)
        for i in range(l):
            
            if self.dimensions[i] > other.dimensions[i]: 
                return False

        return True  
    # >
    def __gt__(self, other):
        l = len(self.dimensions)

        allGreater = False
        for i in range(l):

            if self.dimensions[i] == other.dimensions[i]:
                continue

            if other.dimensions[i] < self.dimensions[i]:                 
                allGreater = True
            else:
                return False

        return allGreater  
    # >=
    def __ge__(self, other):
        l = len(self.dimensions)
        for i in range(l):
            
            if self.dimensions[i] < other.dimensions[i]: 
                return False

        return True   
    
    def __eq__(self, other):
        return self.dimensions == other.dimensions

    def __hash__(self):
        return hash(self.dimensions)

class wPoint2:
    def __init__(self, dim1, dim2):
        self.dim1 = dim1
        self.dim2 = dim2

    def createNew(self, tuples):
        return wPoint2(tuples[0], tuples[1])

    def getDimension(self, index):
        return self.dim1 if index == 0 else self.dim2
    
    def getDimensions(self):
        return (self.dim1, self.dim2) 

    def __str__(self):
        return f"[{self.dim1},{self.dim2}]"
    
    def __repr__(self):
         return f"[{self.dim1},{self.dim2}]"

    def firstDimensionEqual(self, number):
        return self.dim1 == number
    
    def getSize(self):
        return 2

    def divideBy(self, number):
        return wPoint2(self.dim1/number, self.dim2/number) 
    
    def adjustMin(self, other):
        return wPoint2(min(self.dim1, other.dim1), min(self.dim2, other.dim2)) 
    
    def __add__(self, item): 
        return wPoint2(self.dim1 + item.dim1, self.dim2 + item.dim2) 
    
    def __sub__(self, item): 
        return wPoint2(self.dim1 - item.dim1, self.dim2 - item.dim2) 
        
    # <
    def __lt__(self, other):

        if self.dim1 <= other.dim1 and self.dim2 < other.dim2:
            return True

        if self.dim2 <= other.dim2 and self.dim1 < other.dim1:
             return True

        return False
    # <=
    def __le__(self, other):
        return self.dim1 <= other.dim1 and self.dim2 <= other.dim2
    # >
    def __gt__(self, other):
        return  self == other or (not self < other)
    # >=
    def __ge__(self, other):

        return not self < other
    
    def __eq__(self, other):
        return self.dim1 == other.dim1 and self.dim2 == other.dim2 

    def __hash__(self):
        return hash(self.dim1) ^ hash(self.dim2)

def knapsackNd(constraints, items, values, O, forceUseLimits = False):
    solver = knapsackNSolver(constraints, items, values, O, wPoint([0] * constraints.getSize()), forceUseLimits)
    return solver.solve()

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
        self.DP = None
        # inner stat
        self.skippedPointsByMap = 0
        self.skippedPointsByLimits = 0
        self.skippedPointsBySize = 0
        self.totalPointCount = 0
    
    def createNewPoint(self, tuples):
        return self.emptyPoint.createNew(tuples)
    
    def prepare(self, constraints, items, values, forceUseLimits, O):
        
        count = len(items)
        itemSum1, itemSum2, lessCountSum = self.emptyPoint, self.emptyPoint, self.emptyPoint

        lessSizeItems, lessSizeValues = [], []

        partialSums1, superIncreasingItems1 = [], [False]
        partialSums2, superIncreasingItems2 = [], [False] 

        isSuperIncreasing1, isSuperIncreasing2 = True, True   
        allValuesEqual, allValuesEqualToConstraints = True, True   
        allDesc, allAsc = True, True
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

                superIncreasingItem1 = False
                superIncreasingItem2 = False

                if item1 <= constraints:

                    if item1 < itemSum1:
                        isSuperIncreasing1 = False
                    else:
                        superIncreasingItem1 = True
                
                if item2 <= constraints:

                    if item2 < itemSum2:
                        isSuperIncreasing2 = False
                    else:
                        superIncreasingItem2 = True
                
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

                if i > 0:
                    superIncreasingItems1.append(superIncreasingItem1)
                    superIncreasingItems2.append(superIncreasingItem2)

                if item2 <= constraints:
                    lessSizeItems.append(item2)                
                    lessSizeValues.append(itemValue2)  

                    lessCountSum += item2
                    lessCount += 1   

                prevItem1 = item1

            canUsePartialSums = allValuesEqual or allValuesEqualToConstraints 
            
            partialSums = []
            superIncreasingItems = []
            isSuperIncreasing = False
            itemSum = itemSum2

            if (allDesc and canUsePartialSums) or forceUseLimits:
                partialSums = partialSums1
                superIncreasingItems = superIncreasingItems1
                isSuperIncreasing = isSuperIncreasing1
                itemSum = itemSum1

                partialSums.reverse()
                superIncreasingItems.reverse()

            elif allAsc and canUsePartialSums:
                partialSums = partialSums2
                superIncreasingItems = superIncreasingItems2 
                isSuperIncreasing = isSuperIncreasing2 
                itemSum = itemSum2     

                partialSums.reverse()
                superIncreasingItems.reverse()  
            else:
                partialSums = [None] * lessCount
                superIncreasingItems = [False] * lessCount
        else:
            partialSums = []
            superIncreasingItems = []
            isSuperIncreasing = False
            itemSum = self.emptyPoint

        updatedConstraint = constraints.adjustMin(itemSum)
        
        O[0] += count * constraints.getSize()
        return updatedConstraint, lessCount,  lessSizeItems, lessSizeValues, itemSum, lessCountSum, partialSums, isSuperIncreasing, superIncreasingItems, allAsc, allDesc, canUsePartialSums

    def checkCornerCases(self, constraints, lessSizeItems, lessSizeValues, lessCountSum, itemSum):        

        if  lessCountSum == self.emptyPoint:
            return self.emptyPoint.getDimensions(), [],[]
        
        if  lessCountSum <= constraints:
            return lessCountSum.getDimensions(), lessSizeItems, lessSizeValues

        if  itemSum <= constraints:
            return itemSum.getDimensions(), lessSizeItems, lessSizeValues 

        return None   
    
    def yieldOrPushBack(self, circularPointQuene, newPoint, greaterQu):
        if len(circularPointQuene) > 0:
                peek = circularPointQuene[0]

                if newPoint < peek:                   
                    yield newPoint
                    circularPointQuene.append(newPoint)
                else:
                    if len(greaterQu) > 0 and newPoint < greaterQu[0]:
                        greaterQu.insert(0, newPoint)
                    else:
                        greaterQu.append(newPoint)
        else:
            yield newPoint
            circularPointQuene.append(newPoint)    
  
    def getPoints(self, itemDimensions, constraintPoint, circularPointQuene, halfConstraint, itemLimit, oldPointLimit, newPointLimit, prevCyclePointCount, uniquePointSet, skipCount):
        
        # merges ordered visited points with new points with keeping order in O(N) using single circular queue. 
        # each getPoints method call starts fetching visited points from qu start, pops visited point and pushes new point and visited to the end of qu in ASC order.
        # we skip new point if it in list already
        # skips points if they will not contribute to optimal solution (in case of desc flow and (equal values or values equal to first dimension))

        greaterQu = deque()

        if not itemDimensions in uniquePointSet:

            for p in self.yieldOrPushBack(circularPointQuene, itemDimensions, greaterQu):
                yield p

        else:            
            self.skippedPointsByMap += skipCount

        for i in range(prevCyclePointCount):

            oldPoint = circularPointQuene.popleft()             

            while len(greaterQu) > 0 and greaterQu[0] < oldPoint:

                quPoint = greaterQu.popleft()

                yield quPoint 
                circularPointQuene.append(quPoint)

            if not oldPointLimit or not oldPoint < oldPointLimit:
                for p in self.yieldOrPushBack(circularPointQuene, oldPoint, greaterQu):
                    yield p

            else:
                self.skippedPointsByLimits += skipCount

            newPoint = oldPoint + itemDimensions

            if  newPointLimit and newPoint < newPointLimit:
                self.skippedPointsByLimits += skipCount
                continue

            if newPoint <= constraintPoint: 

                if not newPoint in uniquePointSet:   

                    for p in self.yieldOrPushBack(circularPointQuene, newPoint, greaterQu):
                        yield p

                else:
                    self.skippedPointsByMap += skipCount
            else:
                self.skippedPointsBySize += skipCount
        
        while len(greaterQu) > 0:

            quPoint = greaterQu.popleft()

            yield quPoint 
            circularPointQuene.append(quPoint)

    def getValue(self, p, prevDP):

        if p in prevDP:
            cur = prevDP[p]
            return cur[0], cur[1]

        return  0, self.emptyPoint

    def getPossibleValue(self, point, itemValue, itemDims,  dp, O):

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

    def backTraceItems(self, DP, resultI, resultP, items, values, O):
        res = DP[resultI][resultP][0]
        optItems, optValues = [], []
        point = resultP
        opt = self.emptyPoint

        self.totalPointCount += len(DP[resultI])

        if printPct:
            print(f"Skipped points by MAP: {self.skippedPointsByMap}, by LIMITS: {self.skippedPointsByLimits}; by SIZE: {self.skippedPointsBySize};  Max points: {(2 ** len(items)) if len(items) < 15 else -1}; Total points: {self.totalPointCount};")

        for i in range(resultI, 0, -1): 
           
            O[0] += 1

            if res <= 0: 
                break      

            dpw = DP[i - 1]

            skip = False

            if point in dpw:
                skip = res == dpw[point][0]

            if not skip:       
                item, itemValue = items[i - 1], values[i - 1]    

                optItems.append(item.getDimensions())
                optValues.append(itemValue)

                res   -= itemValue
                point -= item
                opt   += item

        return opt.getDimensions(), optItems, optValues

    def createDP(self, count):
        self.DP    = [None] * (count + 1)
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
        resultSum = self.emptyPoint
        index = binSearch(items, size, starting - 1, count - 1, O)

        while index is not None:
            item = items[index]
            value = values[index]
            resultItems.append(item)
            resultValues.append(value)
            resultSum += item

            if allAsc:
                index = binSearch(items, size - resultSum, starting - 1, index - 1, O)
            else:
                index = binSearch(items, size - resultSum, index + 1, count - 1, O)

            O[0] += 1

        if verbose:
            print(f"Superincreasing {size.getSize()}D solver called for size {size} and count {count}.  ASC={allAsc}")
        
        return resultSum.getDimensions(), resultItems, resultValues
   
    def getLimits(self, constraints, i, items, partialSums, superIncreasingItems):

        skipCount = 2 ** (len(items) - i)

        if not doUseLimits:
            return None, None, None, skipCount

        partSumForItem = partialSums[i - 1]
        superIncreasingItem = superIncreasingItems[i - 1]
      
        newPointLimit = constraints - partSumForItem if partSumForItem else None
        oldPointLimit = newPointLimit
      
        if doSolveSuperInc and newPointLimit and superIncreasingItem:
            oldPointLimit = newPointLimit + items[i - 1] 

        return partSumForItem, oldPointLimit, newPointLimit, skipCount

    def dynamicProgramingSolver(self, constraints, count, lessSizeItems, lessSizeValues, partialSums, superIncreasingItems, allAsc, allDesc, forceUseLimits, canUsePartialSums, O):

        DP = self.createDP(count)

        resultI, resultP = 1, self.emptyPoint

        circularPointQuene = deque()

        maxValue, prevPointCount, newPointCount = -sys.maxsize, 0, 0

        halfConstraint = constraints.divideBy(2)

        worstCase = not allAsc and not allDesc and not canUsePartialSums

        if printPct:
            print(f"{constraints.getSize()}D knapsack: N {count}, Use limits: {doUseLimits}, allAsc={allAsc}, allDesc={allDesc}, forceUseLimits={forceUseLimits}, worstCaseExpLimit={self.worstCaseExpLimit}, canUsePartialSums={canUsePartialSums}, worstCase={worstCase}")

        pointCountLimit = 0

        if worstCase:
            pointCountLimit = 2 ** self.worstCaseExpLimit

        for i in range(1, count + 1):

            DP[i] = defaultdict()

            itemValue, item   = lessSizeValues[i - 1], lessSizeItems[i - 1]
            prevDP,    curDP  = DP[i - 1], DP[i]

            prevPointCount, newPointCount = newPointCount, prevPointCount
            newPointCount = 0

            if worstCase and i >= self.worstCaseExpLimit and prevPointCount > pointCountLimit:
                prevPointCount = prevPointCount // 2

            self.totalPointCount += prevPointCount

            if printPct:
                print(f"| {i - 1} | {prevPointCount} | {round(O[0])} |")
            
            itemLimit, oldPointLimit, newPointLimit, skipCount  = self.getLimits(constraints, i, lessSizeItems, partialSums, superIncreasingItems)

            for p in self.getPoints(item, constraints, circularPointQuene, halfConstraint, itemLimit, oldPointLimit, newPointLimit, prevPointCount, prevDP, skipCount):          

                curValue,    curDim   =  self.getValue(p, prevDP) 
                posblValue,  posblDim =  self.getPossibleValue(p - item, itemValue, item, prevDP, O) 

                if  posblValue and curValue <= posblValue and posblDim <= constraints:
                    curValue = posblValue
                    curDim   = posblDim
                
                self.setValue(curDP, p, curValue, curDim, O)

                if  maxValue <= curValue:
                    resultP = p
                    resultI = i
                    maxValue = curValue
                
                newPointCount += 1

        return self.backTraceItems(DP, resultI, resultP, lessSizeItems, lessSizeValues, O) 

    def greedyTopDownSolver(self, constraints, points, values, doSolveSuperInc, forceUseLimits, O):

        def sortBoth(w, v, reverse=True):
            sorted_pairs = sorted(zip(w, v), reverse=reverse, key=lambda t: (t[0], t[1]))
            tuples = zip(*sorted_pairs)
            return [list(tuple) for tuple in  tuples]

        def sortReverese3Both(w, v, x):
            sorted_pairs = sorted( zip(w, v, x), reverse=True, key=lambda t: (t[0], t[1]))
            tuples = zip(*sorted_pairs)
            return [ list(tuple) for tuple in  tuples]

        def solveKnapsackNd(constraints, descNewDims, descNewVals, doSolveSuperInc, forceUseLimits, O):
            
            constraints, count, lessSizeItems, lessSizeValues, itemSum, lessCountSum, partialSums, superIncreasing, superIncreasingItems, allAsc, allDesc, canUsePartialSums = self.prepare(constraints, descNewDims, descNewVals, forceUseLimits, O)
            
            cornerCasesCheck = self.checkCornerCases(constraints, lessSizeItems, lessSizeValues, lessCountSum, itemSum)

            if  cornerCasesCheck:
                return cornerCasesCheck

            if doSolveSuperInc and superIncreasing:
                return self.solveSuperIncreasing(constraints, lessSizeItems, lessSizeValues, count, allAsc, O)

            if allAsc:
                lessSizeItems = list(reversed(lessSizeItems))
                lessSizeValues = list(reversed(lessSizeValues))
                O[0] += len(lessSizeItems) * 2

            return self.dynamicProgramingSolver(constraints, count, lessSizeItems, lessSizeValues, partialSums, superIncreasingItems, allAsc, allDesc, forceUseLimits, canUsePartialSums, O)

        size = constraints.getSize()

        maxN = -sys.maxsize
        maxNItems = []
        maxNValues = []
        maxNDims = tuple([])

        dimDescSortedItems = [None] * size
        dimStairSteps = [None] * size
        dimStairDownCursors = [0] * size
        dimStairDownCursorStartings = [0] * size
        optimizeCacheItems = [None] * size

        estimatedAttemptsCount = 0

        _, dimensionIndexes  = sortBoth(constraints.getDimensions(), range(size), reverse=False)

        for dimensionIndex in range(size):

            dimOrderIndex = dimensionIndexes[dimensionIndex]

            dim = [p.getDimension(dimOrderIndex) for p in points]

            descDim, descValues, descIndex = sortReverese3Both(dim, values, list(range(len(values))))
            O[0] += (len(descDim) * math.log2(len(descDim)))

            dimDescSortedItems[dimensionIndex] = (descDim, descValues, descIndex)
            dimStairSteps[dimensionIndex] = descDim[-1] 
            dimStairDownCursors[dimensionIndex] = constraints.getDimension(dimOrderIndex)
            dimStairDownCursorStartings[dimensionIndex] = constraints.getDimension(dimOrderIndex)
            optimizeCacheItems[dimensionIndex] = {}

            estimatedAttemptsCount += dimStairDownCursors[dimensionIndex] // dimStairSteps[dimensionIndex]

        if verbose: 
            print(f"The NON exact {size}D greedyTopDown knapsack solver called for N = {len(points)}. Estimated attempts: {estimatedAttemptsCount}.")

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

                    _, __, ___, optIndex = knapsack(currentDimLimit, dimItems, dimValues, O, forceUseLimits)

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

                    descNewDims, descNewVals = sortBoth(newData, newValues, reverse=True)
                    O[0] += (len(descNewDims) * math.log2(len(descNewDims)))

                    optDimN, optItemsN, optValuesN = solveKnapsackNd(constraints, descNewDims, descNewVals, doSolveSuperInc, forceUseLimits, O)

                    optSumN = sum(optValuesN)
                    O[0] += len(optValuesN)

                    attemptTimeS = round(time.perf_counter() - t1, 4)

                    if maxN < optSumN and optDimN <= constraints.getDimensions():
                        maxN = optSumN
                        maxNValues = optValuesN
                        maxNItems = optItemsN
                        maxNDims = optDimN   
                    
                        if verbose and optimizeIterIndex == 0:
                            estimatedMaxTime = estimatedAttemptsCount * Decimal(attemptTimeS)
                            print(f"The NON exact {size}D greedyTopDown knapsack solver: estimated max time {estimatedMaxTime}.")

                        if verbose: 
                            print(f"The NON exact {size}D greedyTopDown knapsack solver:  attempt {optimizeIterIndex}, some max value {maxN} has been found, time {attemptTimeS}, total time {round(time.perf_counter() - t0, 4)}, total iters {round(O[0])}.")  

                    elif verbose and attemptTimeS > 2:
                        print(f"The NON exact {size}D greedyTopDown knapsack solver: attempt {optimizeIterIndex}, delta max {maxN-optSumN}, time {attemptTimeS}, total time {round(time.perf_counter() - t0, 4)}, total iters {round(O[0])}")

                    prevOptimizedIndexes.add(optTuple)
                else:
                    print(f"The NON exact {size}D greedyTopDown knapsack solver:  attempt {optimizeIterIndex } was skipped due to less values. Exiting.")
                    break
            else:
                print(f"The NON exact {size}D greedyTopDown knapsack solver: attempt {optimizeIterIndex } was skipped.")
            
            decIndex = (optimizeIterIndex) % size

            if dimStairDownCursors[decIndex] >= dimStairSteps[decIndex]:
                dimStairDownCursors[decIndex] -= dimStairSteps[decIndex]    
               
            for dimensionIndex in range(size):
                anyGreaterThanStep = dimStairDownCursors[dimensionIndex] >= dimStairSteps[dimensionIndex]
                if anyGreaterThanStep:
                    break

            optimizeIterIndex += 1        
        
        return maxNDims, maxNItems, maxNValues

    def solve(self):

        constraints, items, values, forceUseLimits, O = self.constraints, self.items, self.values, self.forceUseLimits, self.O

        constraints, count, lessSizeItems, lessSizeValues, itemSum, lessCountSum, partialSums, superIncreasing, superIncreasingItems, allAsc, allDesc, canUsePartialSums = self.prepare(constraints, items, values, forceUseLimits, O)

        cornerCasesCheck = self.checkCornerCases(constraints, lessSizeItems, lessSizeValues, lessCountSum, itemSum)

        if  cornerCasesCheck:
            return cornerCasesCheck

        if doSolveSuperInc and superIncreasing:
            return self.solveSuperIncreasing(constraints, lessSizeItems, lessSizeValues, count, allAsc, O)

        if allAsc:
            lessSizeItems = list(reversed(lessSizeItems))
            lessSizeValues = list(reversed(lessSizeValues))
            O[0] += len(lessSizeItems) * 2       
       
        if len(items) <= self.worstCaseExpLimit or allAsc or allDesc or canUsePartialSums or self.forceUseDpSolver:
            return self.dynamicProgramingSolver(constraints, count, lessSizeItems, lessSizeValues, partialSums, superIncreasingItems, allAsc, allDesc, forceUseLimits, canUsePartialSums, O)

        return self.greedyTopDownSolver(constraints, lessSizeItems, lessSizeValues, doSolveSuperInc,  forceUseLimits, O)

def sortRevereseBoth(w, v):
    sorted_pairs = sorted(zip(w, v), reverse=True, key=lambda t: (t[0], t[1]))
    tuples = zip(*sorted_pairs)
    return [list(tuple) for tuple in  tuples]

def shuffleBoth(w, v):
    list_pairs = list(zip(w, v))
    random.shuffle(list_pairs)
    tuples = zip(*list_pairs)
    return [list(tuple) for tuple in  tuples]

def sortReverese3Both(w, v, x):
    sorted_pairs = sorted( zip(w, v, x), reverse=True, key=lambda t: (t[0], t[1], t[2]))
    tuples = zip(*sorted_pairs)
    return [ list(tuple) for tuple in  tuples]

def DecimalData(data):
    return Decimal(Decimal(data) / 100000)

def DecimalArray(data):
    for i in range(len(data)):
        data[i] = DecimalData(data[i])

def listValuesEqual(l1, l2):
        l1.sort()
        l2.sort()
        return l1 == l2

def knapsack2d_dp(weightSize, volumeSize, weights, volumes, values, O):
   
        table = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

        for i in range(len(weights)): 

            thingValue = values[i]
            thingConstraint1 = weights[i]
            thingConstraint2 = volumes[i]

            #rewriting the values from the previous line
            for j in range(weightSize + 1):
                for c in range(volumeSize + 1):
                    table[i + 1][j][c] = table[i][j][c]
                    O[0] += 1
                

            for j in range(thingConstraint1, weightSize + 1):
                for k in range(thingConstraint2, volumeSize + 1):
                    table[i + 1][j][k] = max(thingValue + table[i][j - thingConstraint1][k - thingConstraint2], table[i][j][k])
                    O[0] += 1

        w1 = table[len(weights)]
        v1 = w1[weightSize]
        vv1 = v1[volumeSize]

        return vv1

#https://github.com/dariusarnold/knapsack-problem
# Here just for generating iteration count report
def paretoKnapsack(weights, values, weight_limit, O, takeLast = False):

    class Item:
        def __init__(self, id, weight, profit):
            """
            Represent one item that can be put into the knapsack.
            :param id: Row of item in csv, int
            """
            self.id = id
            self.weight = weight
            self.profit = profit
            self.ratio = profit/weight

        def __repr__(self):
            return f"Item(id={self.id}, weight={self.weight}, profit={self.profit})"

    class Point:
        def __init__(self, weight=0., profit=0.):
            """
            Represent a point in the weight/profit diagram. A point is created by a combination of items.
            The IDs of the items used to create this point is saved in item_ids
            :param weight: Sum of the weights of all items in this set
            :param profit: Sum of the profits of all items in this set
            """
            self.weight = weight
            self.profit = profit
            self.item_ids = []

        def __add__(self, item):
            """
            Add an item to this point by adding its weight and profit to the weight and profit
            of the point and also saving its id.
            :param item:
            :return:
            """
            moved_point = Point(self.weight+item.weight, self.profit+item.profit)
            moved_point.item_ids = self.item_ids.copy()
            moved_point.item_ids.append(item.id)
            return moved_point

        def __repr__(self):
            return f"Point(weight={self.weight}, profit={self.profit}, items={self.item_ids})"

    def find(list_, criterion, default, O):
        """
        Return the index of the first item that satisfies the criterion in list_. If no item satisfies the criterion,
        the default value is returned
        :param list_: Iterable of items to search in
        :param criterion: Function that takes one element and compares true or false
        :param default: Default value to return if no item matches criterion
        :return: Index of first item for which criterion returns true
       
        """
        if takeLast:
            return list_[-1]

        ind = len(list_)
        O[0] += math.log2(ind)       
        return next((index for index, el in enumerate(list_) if criterion(el)), default)

    def find_larger_profit(list_, value, O, default=None):
        """
        Return the index of the first item in list__ whose profit is larger than value
        """
        return find(list_, lambda x: x.profit > value, default, O)

    def find_max_or_equal_below(list_, value, O, default=None):
        """
        Return the index of the item in the list whose weight is closest to, but smaller than value
        """
        ind = find(list_, lambda x: x.weight > value, default, O)

        if ind is None:
            last = list_[-1]

            if last.weight <= value:
                return len(list_) - 1
            
            return ind 
        
        else:
            while ind >= 0 and list_[ind].weight > value:
                ind -= 1

        return ind

    def merge(old_list, new_list, weight_limit, O):
        """
        Takes two lists of pareto-optimal points and merges them, discarding points that are dominated by others.
        Point A is dominated by point B if B achieves a larger profit with the same or less weight than A.
        :param old_list: Previous list of pareto optimal points
        :param new_list: New List of pareto optimal points, where one item was added to every point from the old list
        :param weight_limit: Max weight to reduce number of points
        :return: Merged list excluding points that are dominated by others
        """

        merged_list = []
        profit_max = -1
        while True:

            O[0] += 1

            old_point_index = find_larger_profit(old_list, profit_max, O)
            new_point_index = find_larger_profit(new_list, profit_max, O)

            # merge other list if one doesn't contain a point with profit above the current limit
            # or the found point is above the weight limit
            if old_point_index is None or old_list[old_point_index].weight > weight_limit:

                if not new_point_index:
                    new_point_index = 0

                merged_list += new_list[new_point_index:]
                O[0] += len(new_list) - new_point_index
                break

            if new_point_index is None or new_list[new_point_index].weight > weight_limit:

                if not old_point_index:
                    old_point_index = 0

                merged_list += old_list[old_point_index:]
                O[0] += len(old_list) - old_point_index
                break

            old_p = old_list[old_point_index]
            new_p = new_list[new_point_index]

            if old_p.weight <= weight_limit and (old_p.weight < new_p.weight or (old_p.weight == new_p.weight and old_p.profit > new_p.profit)):
                merged_list.append(old_p)
                profit_max = old_p.profit
            elif new_p.weight <= weight_limit:
                merged_list.append(new_p)
                profit_max = new_p.profit

        return merged_list

    items = []

    for i in range(len(weights)):
        items.append(Item(i, weights[i], values[i]))

    """
    Solve 01-knapsack problem for given list of items and weight limit.
    :param items: list of possible items to chose from. No multiples of one item will be taken.
    :param weight_limit: Maximim weight to fill knapsack to
    :return: Ids of items in the list of items, starting at 1 for the first item in the list
    """
    # create first pareto-optimal list which contains no items
    content = [Point()]
    i = 1
    pointCount = 0
    # add items to possible pareto optimal sets one by one, but merge by only keeping the optimal points
    for item in items:
        O[0] += 1
        # filter out item combinations that lie above the weight limit
        content_next = [point + item for point in content]
        content = merge(content, content_next, weight_limit, O)

        if printPct and i > 0:
            pointCount += len(content_next)
            print(f"| {len(content_next)} | {round(O[0])} |")
        i += 1

    best_combination_below_limit = content[find_max_or_equal_below(content, weight_limit, O)]
    #print(f"Best set: {best_combination_below_limit}")
    return best_combination_below_limit.item_ids

dtNow = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
random.seed(dtNow)
randomTestCount = 20

script_dir = os.path.dirname(__file__) # <-- absolute dir the script is in

if printToFile:
    nt = datetime.datetime.now()
    f = open(f'{__file__}.{nt.hour}-{nt.minute}.txt', 'w')
    sys.stdout = f # Change the standard output to the file we created.

if verbose:
    print(f"Initial random seed is {dtNow}")

if True: # NP complete: Rational numbers tests for equal-subset-sum knapsack, 1-0 knapsack, and N dimension knapsacks, where N 2-4.
    if verbose:
        print("Rational numbers tests for equal-subset-sum knapsack, 1-0 knapsack, and N dimension knapsacks, where N 2-4.")

    O = [0]

    A = [Decimal("0.2"), Decimal("1.200001"), Decimal("2.9000001"), Decimal("3.30000009"), Decimal("4.3"), Decimal("5.5"), Decimal("6.6"), Decimal("7.7"), Decimal("8.8"), Decimal("9.8")]
    A.sort(reverse=True)

    s = Decimal("10.5")

    expectedValue = Decimal("10.20000109")

    opt, optItems, optValuesN4 = knapsackNd(wPoint((s, s, s, s)), [wPoint((a, a, a, a)) for a in A], A, O)
    assert expectedValue == sum(optValuesN4)

    opt, optItems, optValuesN3 = knapsackNd(wPoint((s, s, s)), [wPoint((a, a, a)) for a in A], A, O)
    assert expectedValue == sum(optValuesN3)

    opt, optItems, optValuesN2 = knapsackNd(wPoint((s, s)), [wPoint((a, a)) for a in A], A, O)
    assert expectedValue == sum(optValuesN2)

    opt, optWeights, optValues2, _ = knapsack(s, A, A, O)
    assert expectedValue == sum(optValues2)

    opt, optValues1 = subsKnapsack(s, A, O)   
    assert expectedValue == sum(optValues1)

if True: # Polynominal: Superincreasing integer tests for equal-subset-sum knapsack, 1-0 knapsack, and N dimension knapsacks, where N = 2.
    if verbose:
        print("Superincreasing integer numbers tests.")

    prevDoSolveSuperInc = doSolveSuperInc

    for i in range(1, 3):

        O = [0]
        A = [1, 2, 5, 21, 69, 189, 376, 919]

        if i % 2 == 1:
            A.reverse()

        C = 10

        nLogN = len(A) * math.log2(len(A))

        for s in range(sum(A)):

            doSolveSuperInc = False 

            opt1, expected = subsKnapsack(s, A, O)  

            doSolveSuperInc = True

            O[0] = 0
            opt2, optValues1 = subsKnapsack(s, A, O) 

            assert listValuesEqual(optValues1, expected)
            assert O[0] <= C * len(A) + nLogN
           
            O[0] = 0
            opt, optItems, optValues2,_ = knapsack(s, A, A, O)  
            assert  listValuesEqual(optValues2, expected)
            assert O[0] <= C * len(A) + nLogN 

            
            O[0] = 0
            opt, optItems3, optValues3 = knapsackNd(wPoint((s, s)), [wPoint((a, a)) for a in A], A, O)  
            assert  listValuesEqual(optValues3, expected)
            assert O[0] <= 100 * nLogN
             

    doSolveSuperInc = prevDoSolveSuperInc
    
    if verbose:
        print("Superincreasing rational numbers tests.")   

    for s in range(sum(A)):

        decA = list(A)

        nLogN = len(A) * math.log2(len(A))

        DecimalArray(decA)

        decS = DecimalData(s)

        doSolveSuperInc = False 

        opt, expected = subsKnapsack(decS, decA, O)  

        doSolveSuperInc = True

        O[0] = 0
        opt, decOptValues1 = subsKnapsack(decS, decA, O)  
        assert  listValuesEqual(decOptValues1, expected)
        assert O[0] <=  10 * nLogN

        O[0] = 0
        opt, decOptItems, decOptValues2, _ = knapsack(decS, decA, decA, O)  
        assert  listValuesEqual(decOptValues2, expected)
        assert O[0] <=  10 * len(A) + nLogN
        
        O[0] = 0
        opt, decOptItems3, optValues3 = knapsackNd(wPoint((decS, decS)), [wPoint((da, da)) for da in decA], decA, O)  
        assert  listValuesEqual(optValues3, expected)
        assert O[0] <=  100 * nLogN
    
    doSolveSuperInc = prevDoSolveSuperInc   
 
if True: # Polynominal: Partial superincreasing numbers tests.
    if verbose:
        print("Partial superincreasing numbers tests.")

    O = [0]
    A = [1, 2, 5, 21, 69, 189, 376, 919, 5000]

    for attempt in range(1, 3):      

        revers = attempt % 2 == 0

        if verbose:
            print(f"reverse = {revers}")

        for i in range(2, len(A) - 1, 2):

            testCase = list(A)

            testCase.insert(i + 1, testCase[i] + 1)

            if revers:
                testCase.reverse()

            nLogN = len(testCase) * math.log2(len(testCase))

            for s in range(3, sum(testCase)):

                doSolveSuperInc = False 

                optE, expected = subsKnapsack(s, testCase, O)  

                doSolveSuperInc = True

                if verbose:
                    print(f"Partial superincreasing test: s = {s},  reverse = {revers}, index {i}")

                O[0] = 0
                opt1, optValues1 = subsKnapsack(s, testCase, O) 
                assert listValuesEqual(optValues1, expected) or sum(expected) == sum(optValues1)         
                
                O[0] = 0
                opt2, optItems, optValues2, _ = knapsack(s, testCase, testCase, O)  
                assert  listValuesEqual(optValues2, expected) or sum(expected) == sum(optValues2)         

                O[0] = 0
                opt, optItems3, optValues3 = knapsackNd(wPoint((s, s)), [wPoint((a, a)) for a in testCase], testCase, O)  
                assert  listValuesEqual(optValues3, expected) or sum(expected) == sum(optValues3) 
            
if True: # Polynominal: Partial geometric progression numbers tests.
    if verbose:
        print("Partial geometric progression numbers tests.")

    O = [0]

    for base in range(1, 15):

        A = [base] * 15

        for i in range(1, 15):
            A[i] *= int(A[i - 1] * 3)

        testCase = list(A)

        testCase.append(testCase[len(A) // 2] + 1)

        testCase.sort(reverse=True)

        nLogN = len(testCase) * math.log2(len(testCase))

        step = sum(testCase) // 100

        for s in range(step, sum(testCase), step):

            doSolveSuperInc = False 

            optE, expected = subsKnapsack(s, testCase, O)  

            doSolveSuperInc = True

            t1 = time.perf_counter()

            O[0] = 0
            opt1, optValues1 = subsKnapsack(s, testCase, O) 
            assert listValuesEqual(optValues1, expected)   

            t2 = time.perf_counter()  
            
            O[0] = 0
            opt2, optItems, optValues2, _ = knapsack(s, testCase, testCase, O)  
            assert  listValuesEqual(optValues2, expected)
            
            t3 = time.perf_counter()

            O[0] = 0
            opt3, optItems3, optValues3 = knapsackNd(wPoint((s, s)), [wPoint((a, a)) for a in testCase], testCase, O)  
            assert  listValuesEqual(optValues3, expected)

            t4 = time.perf_counter()

            print(f"Partial geometric progression test: base {base}, size {s}, subs {round(t2 - t1, 4)}, 1-0 {round(t3 - t2, 4)}, 2D {round(t4 - t3, 4)}.")

if True: # NP complete: 2D knapsack matching with classic DP solution results. N=13

    O = [0]
    O_dp = [0]

    testCaseW =   [5,  3,   2,  5,  3,  4,  5, 6,  2,  5,  1,   3,  6,  8]
    testCaseV =   [8,  4,  12, 18,  5,  2,  1, 4,  3,  2,  2,   4, 10,  9]
    testCaseVal = [50, 30, 20, 50, 30, 40, 50, 60, 10, 70, 80, 10, 15, 30]

    if verbose:
        print(f"2D knapsack matching with classic DP solution results. N={len(testCaseW)}")  

    s_weights, s_volumes, s_values = sortReverese3Both(testCaseW, testCaseV, testCaseVal)
 
    if True:

        for testKnapsackWeight in range(min(testCaseW), sum(testCaseW) - 1):
            for testKnapsackVolume in range(min(testCaseV), sum(testCaseV) - 1):

                dpRes = knapsack2d_dp(testKnapsackWeight, testKnapsackVolume, testCaseW, testCaseV, testCaseVal, O_dp)

                dims = [None] * len(s_weights)

                for i in range(len(s_weights)):
                    dims[i] = wPoint((s_weights[i], s_volumes[i]))

                opt, optItems, optValues = knapsackNd(wPoint((testKnapsackWeight, testKnapsackVolume)), dims, s_values, O)

                resVal = sum(optValues)
              
                resW = opt[0]
                resVol = opt[1]

                if resVal != dpRes or resW > testKnapsackWeight or resVol > testKnapsackVolume:
                    if verbose:
                        print(f"W: {testKnapsackWeight} V: {testKnapsackVolume}", end="")
                        print(f" k sum val : {sum(optValues)}, dp: {dpRes}  k sum vol : {resVol} k sum w : {resW}  all sum val: {sum(s_values)} all sum vol: {sum(s_volumes)} all sum w: {sum(s_weights)}")
                    assert False

if True: # NP hard: Integer and Decimal mixed multidimensional knapsack problem (MKP) test
    
    data = [(821, Decimal("0.8"), 118),
            (1144, Decimal("1"), 322), 
            (634, Decimal("0.7"), 166), 
            (701, Decimal("0.9"), 195),
            (291, Decimal("0.9"), 100), 
            (1702, Decimal("0.8"), 142), 
            (1633, Decimal("0.7"), 100), 
            (1086, Decimal("0.6"), 145),
            (124, Decimal("0.6"), 100), 
            (718, Decimal("0.9"), 208), 
            (976, Decimal("0.6"), 100), 
            (1438, Decimal("0.7"), 312),
            (910, Decimal("1"), 198), 
            (148, Decimal("0.7"), 171), 
            (1636, Decimal("0.9"), 117), 
            (237, Decimal("0.6"), 100),
            (771, Decimal("0.9"), 329), 
            (604, Decimal("0.6"), 391), 
            (1078, Decimal("0.6"), 100),
            (640, Decimal("0.8"), 120),
            (1510, Decimal("1"), 188), 
            (741, Decimal("0.6"), 271), 
            (1358, Decimal("0.9"), 334), 
            (1682, Decimal("0.7"), 153),
            (993, Decimal("0.7"), 130), 
            (99, Decimal("0.7"), 100), 
            (1068, Decimal("0.8"), 154), 
            (1669, Decimal("1"), 289)]

    # expected result was generated by genetic algo below
    genExpectedValue, genExpectedIndexes = 3531, [0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0, 0, 1, 1, 0, 0, 1, 0, 1]

    '''
    from pyeasyga import pyeasyga

    ga = pyeasyga.GeneticAlgorithm(data)        # initialise the GA with data
    ga.population_size = 200                    # increase population size to 200 (default value is 50)

    # define a fitness function
    def fitness(individual, data):
        weight, volume, price = 0, 0, 0
        for (selected, item) in zip(individual, data):
            if selected:
                weight += item[0]
                volume += item[1]
                price += item[2]
        if weight > 12210 or volume > 12:
            price = 0
        return price

    ga.fitness_function = fitness               # set the GA's fitness function
    ga.run()                                    # run the GA
    print ga.best_individual()                  # print the GA's best solution
    '''

    dims2d = [wPoint((p[0], p[1])) for p in data]
    values = [p[2] for p in data]

    descDims2d, descValues = sortRevereseBoth(dims2d, values)
    constr2d = wPoint((12210, Decimal(12)))

    if verbose:
        print(f"Integer and Decimal mixed multidimensional knapsack problem (MKP) test. N {len(data)}")

    O = [0]

    t1 = time.perf_counter()

    prevPrintPct = printPct

    solver = knapsackNSolver(constr2d, descDims2d, descValues, O)
    solver.forceUseDpSolver = True

    optValue, optItems, optValues = solver.solve()

    printPct = prevPrintPct

    t2 = time.perf_counter()

    optRez = sum(optValues)

    good = optRez >= genExpectedValue and optValue <= constr2d.getDimensions()

    iterMax = 2 ** (len(data))
    iterRez = round(O[0])

    if verbose:
        print(f"MKP time: {round(t2 - t1, 4)}, optimized - genetic expected: {optRez - genExpectedValue}, iter: {iterRez}, iterMax: {iterMax}, dIter: {iterMax - iterRez}")

    assert good

if True: # NP hard: Integer multidimensional knapsack problem (MKP) with same profit value limits tests

    mixDimData =[(821,  976,  1),
                (1144,  718,  1), 
                (634,   124,  1), 
                (701,   1086, 1),
                (291,   1633, 1), 
                (1702,  1702, 1), 
                (1633,  291,  1), 
                (1086,  701,  1),
                (124,   634,  1), 
                (718,   1144, 1), 
                (976,   821,  1), 
                (1438,  124,  1),
               ]

    cnt = len(mixDimData)

    dimsMix2d = [wPoint((p[0], p[1])) for i, p in enumerate(mixDimData)]
    mixValues2d = [p[2] for p in mixDimData]  

    descDims2d, descValues2d = sortRevereseBoth(dimsMix2d, mixValues2d) 

    sumOfAll = sum([p[0] for p in mixDimData])
    minItem = min([p[0] for p in mixDimData]) - 1

    if verbose:
        print(f"MKS 2d matching results with limits turned on")

    prevDoUseLimits = doUseLimits

    for i in range(1, 3):

        O = [0]

        ascOrder = i % 2 == 1

        for constaint1 in range(minItem, sumOfAll, minItem // 2):

            #constaint1 = 672

            for constaint2 in range(minItem, sumOfAll, minItem // 2):

                #constaint2 = 2319

                testDescDims = list(descDims2d)
                testDescValues = list(descValues2d)

                testDims = list(reversed(testDescDims)) if ascOrder else list(testDescDims)
                testValues = list(reversed(testDescValues))  if ascOrder else list(testDescValues)

                t1 = time.perf_counter()

                constr2d = wPoint((constaint1, constaint2))          
                
                doUseLimits = False

                optValue2, optItems2, optValues2 = knapsackNd(constr2d, testDescDims, testDescValues, O)

                tFull = round(time.perf_counter() - t1, 4)

                fullIterRez = O[0]
            
                O = [0]

                doUseLimits = True

                t1 = time.perf_counter()

                optValue3, optItems3, optValues3 = knapsackNd(constr2d, testDims, testValues, O)

                tLimitsOn = round(time.perf_counter() - t1, 4)

                t2 = time.perf_counter()

                iterRez = round(O[0])

                optRez2 = sum(optValues2)
                optRez3 = sum(optValues3)

                good = optRez3 == optRez2 and optValue3 <= constr2d.getDimensions()

                if verbose:
                    print(f"MKS 2d, ASC={ascOrder}, constaint1: {constaint1}, constaint2: {constaint2}, time: {round(t2 - t1, 4)}, optimized - expected: {optRez2 - optRez3}, dlen {len(optValues3)-len(optValues2)} , iter: {iterRez}, dIter: {fullIterRez - iterRez}, dt {tFull - tLimitsOn}")

                assert good

    doUseLimits = prevDoUseLimits

if True: # NP hard: Integer multidimensional knapsack problem (MKP) T partition grouping opertator tests

    mixDimData =[(821,  1,  821),
                (1144,  1,  1144), 
                (634,   1,  634), 
                (701,   1, 701),
                (291,   1, 291), 
                (1702,  1, 1702), 
                (1633,  1,  1633), 
                (1086,  1,  1086),
                (124,   1,  124), 
                (718,   1, 718), 
                (976,   1,  976), 
                (1438,  1,  1438),
               ]

    cnt = len(mixDimData)

    dimsMix2d = [wPoint((p[0], p[1])) for i, p in enumerate(mixDimData)]
    mixValues2d = [p[2] for p in mixDimData]  

    descDims2d, descValues2d = sortRevereseBoth(dimsMix2d, mixValues2d) 

    sumOfAll = sum([p[0] for p in mixDimData])
    minItem = min([p[0] for p in mixDimData]) - 1

    if verbose:
        print(f"MKS N partition 2d matching results with limits turned off")

    prevDoUseLimits = doUseLimits

    for i in range(1, 3):

        O = [0]

        ascOrder = i % 2 == 0

        for constaint1 in range(minItem, sumOfAll, minItem // 2):

            for constaint2 in range(1, len(mixDimData)):

                testDescDims = list(descDims2d)
                testDescValues = list(descValues2d)

                testDims = list(reversed(testDescDims)) if ascOrder else list(testDescDims)
                testValues = list(reversed(testDescValues))  if ascOrder else list(testDescValues)

                t1 = time.perf_counter()
                
                constr2d = wPoint((constaint1, constaint2))          
                
                doUseLimits = False

                optValue2, optItems2, optValues2 = knapsackNd(constr2d, testDescDims, testDescValues, O)

                tFull = round(time.perf_counter() - t1, 4)

                fullIterRez = O[0]
            
                O = [0]

                doUseLimits = True

                t1 = time.perf_counter()

                optValue3, optItems3, optValues3 = knapsackNd(constr2d, testDims, testValues, O)

                tLimitsOn = round(time.perf_counter() - t1, 4)

                t2 = time.perf_counter()

                iterRez = round(O[0])

                optRez2 = sum(optValues2)
                optRez3 = sum(optValues3)

                good = optRez3 == optRez2 and optValue3 <= constr2d.getDimensions()

                if verbose:
                    print(f"MKS N partition test:  ASC={ascOrder}, constaint1: {constaint1}, constaint2 {constaint2} , time: {round(t2 - t1, 4)}, optimized - expected: {optRez2 - optRez3}, dlen {len(optValues3)-len(optValues2)} , iter: {iterRez}, dIter: {fullIterRez - iterRez}, dt {tFull - tLimitsOn}")

                assert good

    doUseLimits = prevDoUseLimits

if True: # NP complete: Integer 1-0 knapsack problem limits tests

    mixDimData =[(821,  100),
                (1144,  100), 
                (634,   100), 
                (701,  100),
                (291,  100), 
                (1702, 100), 
                (1633,  100), 
                (1086,  100),
                (124,   100), 
                (718,  100), 
                (976,   100), 
                (1438,  100),               
                (822,  100),
                (1143,  100), 
                (640,   100), 
                (702,  100),
                (291,  100), 
                (1702, 100), 
                (1633,  100), 
                (2000,  100),
                (100,   100), 
                (701,  100), 
                (1976,   100), 
                (1638,  100),
               ]

    cnt = len(mixDimData)

    dimsd = [p[0] for p in mixDimData]
    values = [p[1] for p in mixDimData]  

    descDims, descValues = sortRevereseBoth(dimsd, values) 

    sumOfAll = sum([p[0] for p in mixDimData])
    minItem = min([p[0] for p in mixDimData]) - 1

    if verbose:
        print(f"Integer 1-0 knapsack problem limits tests")

    prevDoUseLimits = doUseLimits
    prevPrintPct = printPct
    printPct = False

    for i in range(1, 3):

        O = [0]

        ascOrder = i % 2 == 1

        for constraint in range(minItem, sumOfAll, minItem // 2):

            testDescDims = list(descDims)
            testDescValues = list(descValues)

            testDims = list(reversed(testDescDims)) if ascOrder else list(testDescDims)
            testValues = list(reversed(testDescValues))  if ascOrder else list(testDescValues)

            t1 = time.perf_counter()
            
            doUseLimits = False

            optValue2, optItems2, optValues2, _ = knapsack(constraint, testDescDims, testDescValues, O)

            dimSum2 = sum(optItems2)

            tFull = round(time.perf_counter() - t1, 4)

            fullIterRez = O[0]
        
            O = [0]

            doUseLimits = True

            t1 = time.perf_counter()

            optValue3, optItems3, optValues3, _ = knapsack(constraint, testDims, testValues, O)

            dimSum3 = sum(optItems3)

            tLimitsOn = round(time.perf_counter() - t1, 4)

            t2 = time.perf_counter()

            iterRez = round(O[0])

            printPct = prevPrintPct

            optRez2 = sum(optItems2)
            optRez3 = sum(optItems3)

            good = optRez3 == optRez2 and dimSum3 <= constraint and dimSum2 <= constraint

            if verbose:
                print(f"1-0 knapsack limits test:  ASC={ascOrder}, constraint: {constraint}, time: {round(t2 - t1, 4)}, optimized - expected: {optRez2 - optRez3}, dlen {len(optValues3)-len(optValues2)} , iter: {iterRez}, dIter: {fullIterRez - iterRez}, dt {tFull - tLimitsOn}")

            assert good

    doUseLimits = prevDoUseLimits
    printPct = prevPrintPct

if True: # NP complete: N equal-subset-sum tests.

    if verbose:
        print("N equal-subset-sum integer tests.")

    O = [0]

    tests = []

    A, NU = [3, 383, 401, 405, 580, 659, 730, 1024, 1100, 1175, 1601, 2299, 3908, 4391, 4485, 5524], 4
    tests.append((A, NU))
    A, NU = [4,5,3,2,5,5,5,1,5,5,5,5,3,5,5,2], 13
    tests.append((A, NU))
    A, NU = [4,4,6,2,3,8,10,2,10,7], 4
    tests.append((A, NU))
    A, NU = [4,15,1,1,1,1,3,11,1,10], 3
    tests.append((A, NU))
    A, NU =  [20, 23, 25, 49, 45, 27, 40, 22, 19], 3
    tests.append((A, NU))
    A, NU = [20, 23, 25, 49, 45, 27, 40, 22, 19, 20, 23, 25, 49, 45, 27, 40, 22, 19], 6
    tests.append((A, NU))
    A, NU =  [27, 9, 9, 9, 9, 9, 3, 3, 3], 3
    tests.append((A, NU))
    A, NU = [10,10,10,7,7,7,7,7,7,6,6,6], 3
    tests.append((A, NU))
    A, NU = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1], 3
    tests.append((A, NU))
    A, NU = [10,12,1,2,10,7,5,19,13,1],4
    tests.append((A, NU))
    A, NU = [1,2,3,4,5,6,7,8,9],3
    tests.append((A, NU))  
    A, NU = [780,935,2439,444,513,1603,504,2162,432,110,1856,575,172,367,288,316], 4
    tests.append((A, NU))
    # https://web.stanford.edu/class/archive/cs/cs103/cs103.1132/lectures/27/Small27.pdf
    A, NU = [13,137,56,42,103,58,271], 2
    tests.append((A, NU))
    A, NU = list(range(1, 100)), 3
    tests.append((A, NU))
    #http://people.brunel.ac.uk/~mastjjb/jeb/orlib/files/bills_snowflake.txt
    A, NU = [1,62,34,38,39,43,62,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119], 3
    tests.append((A, NU))
    A, NU = [1,156,2,3,4,350,427,428,429,430,431,432,433,434,435,436,437,438,439,440,441,442,443,444,445,446,447,448,449,450,451,452,453,454,455,456,457,458,459,460,461,462,463,464,465,466,467,468,469,470,471,472,473,474,475,476,477,478,479,480,481,482,483,484,485,486,487,488,489,490,491,492,493,494,495,496,497,498,499,500,501,502,503,504,505,506,507,508,509,510,511,512,513,514,515,516,517,518,519,520,521,522,523,524,525,526,527,528,529,530,531,532,533,534,535,536,537,538,539,540,541,542,543,544,545,546,547,548,549,550,551,552,553,554,555,556,557,558,559,560,561,562,563,564,565,566,567,568,569,570,571,572,573,574,575,576,577,578], 3
    tests.append((A, NU))
    A, NU = list(range(1, (81 * 9) + 1)), 3
    tests.append((A, NU))

    for i in range(randomTestCount):

        newSeed = dtNow + datetime.timedelta(seconds=i)

        random.seed(newSeed)

        if verbose:
            print(f"random seed is {newSeed}")

        case = 0

        for A, NU in tests:

            case += 1

            O[0] = 0

            if verbose:        
                print("case " + str(case))

            partResult, reminder, optCount = partitionN(list(A), NU, 0, O)

            if len(reminder) != 0 or len(partResult) != NU:

                if verbose:        
                    print("case " + str(case))
                    print("A " + str(A))
                    print("part result " + str(partResult))
                    print("part reminder  " + str(reminder))
                    print("optCount  " + str(optCount))
                    print("len " + str(len(A)))
                    print("sum " + str(sum(A)))
                    print("sum // NU" + str(sum(A) // NU))
                    print("iter " + str(O[0]))

                assert False
    
    random.seed(dtNow)

    if verbose:
        print("N equal-subset-sum rational numbers tests.")

    for i in range(randomTestCount):

        newSeed = dtNow + datetime.timedelta(seconds=i)

        random.seed(newSeed)

        if verbose:
            print(f"random seed is {newSeed}")
   
        case = 0

        for A, NU in tests:

            case += 1

            O[0] = 0

            if verbose:        
                print("case " + str(case))

            decA = list(A)

            DecimalArray(decA)

            partResult, reminder, optCount = partitionN(decA, NU, 0, O)

            if len(reminder) != 0 or len(partResult) != NU:

                if verbose:        
                    print("case " + str(case))
                    print("A " + str(decA))
                    print("part result " + str(partResult))
                    print("part reminder  " + str(reminder))
                    print("optCount  " + str(optCount))
                    print("len " + str(len(decA)))
                    print("sum " + str(sum(decA)))
                    print("sum / NU" + str(sum(decA) / NU))
                    print("iter " + str(O[0]))

                assert False

if True : # NP complete: Multiple knapsack sizes integer tests.

    if verbose:
        print("Multiple knapsack sizes integer tests.")

    mksTests = []

    A, NU = [3, 383, 401, 405, 580, 659, 730, 1024, 1100, 1175, 1601, 2299, 3908, 4391, 4485, 5524], 4
    mksTests.append((A, NU))
    A, NU = [4,5,3,2,5,5,5,1,5,5,5,5,3,5,5,2], 13
    mksTests.append((A, NU))
    A, NU = [4,4,6,2,3,8,10,2,10,7], 4
    mksTests.append((A, NU))
    A, NU = [4,15,1,1,1,1,3,11,1,10], 3
    mksTests.append((A, NU))
    A, NU =  [20, 23, 25, 49, 45, 27, 40, 22, 19], 3
    mksTests.append((A, NU))
    A, NU = [20, 23, 25, 49, 45, 27, 40, 22, 19, 20, 23, 25, 49, 45, 27, 40, 22, 19], 6
    mksTests.append((A, NU))
    A, NU =  [27, 9, 9, 9, 9, 9, 3, 3, 3], 3
    mksTests.append((A, NU))
    A, NU = [10,10,10,7,7,7,7,7,7,6,6,6], 3
    mksTests.append((A, NU))
    A, NU = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1], 3
    mksTests.append((A, NU))
    A, NU = [10,12,1,2,10,7,5,19,13,1],4
    mksTests.append((A, NU))
    A, NU = [1,2,3,4,5,6,7,8,9],3

    singleTest = []
    singleTestSizes = []

    ind = 0

    for A, NU in mksTests:

        ind += 1

        for num in A:
            singleTest.append(num)

        size = sum(A) // NU

        for i in range(NU):
           singleTestSizes.append(size)

    O = [0]

    random.shuffle(singleTest)
    random.shuffle(singleTestSizes)

    for i in range(randomTestCount):

        newSeed = dtNow + datetime.timedelta(seconds=i)

        random.seed(newSeed)

        if verbose:
            print(f"random seed is {newSeed}")

        partResult, reminder, optCount = partitionN(list(singleTest), list(singleTestSizes), 0, O)

        if len(reminder) != 0:

            if verbose:        
                print("A " + str(singleTest))
                print("part result " + str(partResult))
                print("part reminder  " + str(reminder))
                print("optCount  " + str(optCount))
                print("len " + str(len(singleTest)))
                print("sum " + str(sum(singleTest)))
                print("iter " + str(O[0]))

    random.seed(dtNow)

if True: # NP complete: Strict 3 and 6 partition problem tests.

    def unionTuples(tuples):
        rez = []
        for t in tuples:
            for tn in t:
                rez.append(tn)
        rez.sort()
        return rez
    
  
    if verbose:
        print("3-partition problem for integer numbers tests.")

    O = [0]

    tests = []
    # https://en.wikipedia.org/wiki/3-partition_problem
    AT, NU =  [(20, 25, 45), (23, 27, 40), (49, 22, 19), (30, 30, 30)], 4
    tests.append((unionTuples(AT), NU))   
    AT, NU = [(1, 5, 9), (2, 6, 7)], 2   
    tests.append((unionTuples(AT), NU))  
    # http://www.columbia.edu/~cs2035/courses/ieor4405.S17/npc-sched.pdf
    A, NU = [26, 26, 27, 28, 29, 29, 31, 33, 39, 40, 45, 47], 4 
    tests.append((A, NU))   
    AT, NU = [(1, 1, 1), (1, 1, 1), (1, 1, 1), (1, 1, 1), (1, 1, 1)], 5
    tests.append((unionTuples(AT), NU))  
    AT, NU = [(1, 1, 1), (1, 1, 1), (1, 1, 1), (1, 1, 1), (1, 1, 1), (1, 1, 1), (1, 1, 1), (1, 1, 1), (1, 1, 1), (1, 1, 1), (1, 1, 1), (1, 1, 1)], 12
    tests.append((unionTuples(AT), NU))    

    # the worst 3 partition test cases ever
    AT, NU = [(3, 3, 6), (3, 4, 5), (1, 5, 6), (1, 3, 8), (1, 4, 7), (4, 4, 4), (2, 5, 5), (1, 2, 9), (2, 3, 7), (2, 4, 6), (1, 1, 10), (2, 2, 8)], 12
    tests.append((unionTuples(AT), NU))  
    AT, NU = [(1, 2, 15), (2, 3, 13), (6, 6, 6), (4, 7, 7), (3, 3, 12), (1, 6, 11), (2, 7, 9), (3, 6, 9), (1, 1, 16), (2, 2, 14), (2, 5, 11), (5, 6, 7), (3, 5, 10), (4, 6, 8), (1, 8, 9), (1, 3, 14), (2, 4, 12), (4, 4, 10), (3, 7, 8), (1, 5, 12), (2, 6, 10), (3, 4, 11), (1, 7, 10), (1, 4, 13), (4, 5, 9), (2, 8, 8), (5, 5, 8)], 27
    tests.append((unionTuples(AT), NU))  
    AT, NU = [(2, 7, 15), (1, 3, 20), (4, 4, 16), (1, 1, 22), (6, 7, 11), (3, 5, 16), (4, 10, 10), (6, 6, 12), (4, 7, 13), (3, 4, 17), (2, 5, 17), (1, 8, 15), (1, 6, 17), (3, 10, 11), (2, 6, 16), (2, 4, 18), (2, 11, 11), (1, 7, 16), (4, 8, 12), (3, 9, 12), (5, 7, 12), (6, 8, 10), (3, 3, 18), (5, 6, 13), (2, 9, 13), (1, 5, 18), (5, 8, 11), (8, 8, 8), (2, 3, 19), (2, 10, 12), (1, 4, 19), (4, 5, 15), (1, 11, 12), (3, 8, 13), (4, 9, 11), (2, 2, 20), (7, 8, 9), (1, 10, 13), (4, 6, 14), (6, 9, 9), (3, 7, 14), (2, 8, 14), (1, 2, 21), (7, 7, 10), (1, 9, 14), (3, 6, 15), (5, 5, 14), (5, 9, 10)], 48
    tests.append((unionTuples(AT), NU))  

    for i in range(randomTestCount):

        newSeed = dtNow + datetime.timedelta(seconds=i)

        random.seed(newSeed)

        if verbose:
            print(f"random seed is {newSeed}")

        case = 0
        for A, NU in tests:

            case += 1

            O[0] = 0

            if verbose:        
                print("case " + str(case))

            partResult, reminder, optCount = partitionN(list(A), NU, 3, O)

            if len(reminder) != 0 or len(partResult) != NU:

                if verbose:        
                    print("case " + str(case))
                    print("A " + str(A))
                    print("part result " + str(partResult))
                    print("part reminder  " + str(reminder))
                    print("optCount  " + str(optCount))
                    print("len " + str(len(A)))
                    print("sum " + str(sum(A)))
                    print("sum // NU" + str(sum(A) // NU))
                    print("iter " + str(O[0]))

                assert False
    
    random.seed(dtNow)

    if verbose:
        print("6-partition problem for integer tests.")

    for i in range(randomTestCount):

        newSeed = dtNow + datetime.timedelta(seconds=i)

        random.seed(newSeed)

        if verbose:
            print(f"random seed is {newSeed}")
   
        case = 0
        for A, NU in tests:

            case += 1

            O[0] = 0

            if NU % 6 != 0:
                continue

            if verbose:        
                print("case " + str(case))

            partResult, reminder, optCount = partitionN(list(A), NU // 2, 6, O)

            if len(reminder) != 0 or len(partResult) != NU // 2:

                if verbose:        
                    print("case " + str(case))
                    print("A " + str(A))
                    print("part result " + str(partResult))
                    print("part reminder  " + str(reminder))
                    print("optCount  " + str(optCount))
                    print("len " + str(len(A)))
                    print("sum " + str(sum(A)))
                    print("sum // NU " + str(sum(A) // NU))
                    print("iter " + str(O[0]))

                assert False
    
    random.seed(dtNow)

    if verbose:
        print("3-partition problem for rational numbers tests.")  
    
    for i in range(randomTestCount):

        newSeed = dtNow + datetime.timedelta(0,i)

        random.seed(newSeed)

        if verbose:
            print(f"random seed is {newSeed}")

        case = 0
        for A, NU in tests:

            case += 1

            O[0] = 0

            if verbose:        
                print("case " + str(case))

            decA = list(A)
            DecimalArray(decA)

            partResult, reminder, optCount = partitionN(decA, NU, 3, O)

            if len(reminder) != 0 or len(partResult) != NU:

                if verbose:        
                    print("case " + str(case))
                    print("A " + str(decA))
                    print("part result " + str(partResult))
                    print("part reminder  " + str(reminder))
                    print("optCount  " + str(optCount))
                    print("len " + str(len(decA)))
                    print("sum " + str(sum(decA)))
                    print("sum / NU" + str(sum(decA) / NU))
                    print("iter " + str(O[0]))

                assert False
    
if True: # NP complete: 1-0 knapsack for Silvano Martello and Paolo Toth 1990 tests.
    if verbose:
        print("1-0 knapsack solver for Silvano Martello and Paolo Toth 1990 tests.")

    def      testSilvano(W, V, R, c):
        O = [0]

        ws, vs = sortRevereseBoth(W, V)

        expectedSV = 0
        expectedSW = 0

        ind = 0
        for i in R:
            if i == 1:
                expectedSV += V[ind]
                expectedSW += W[ind]
            ind += 1

        opt1, optW1, optV1, _ = knapsack(c, ws, vs, O)
        opt2, optW2, optV2 = knapsackNd(wPoint((c, c)), [wPoint((a, a)) for a in ws], vs, O)

        assert (expectedSV == sum(optV1))
        assert (sum(optV1) == sum(optV2))
    
    # page 42. Example 2.3 

    V = [50, 50, 64, 46, 50, 5]
    W = [56 ,59, 80, 64, 75, 17]
    R = [1,  1,   0, 0,   1, 0]
    c = 190

    testSilvano(W, V, R, c)

    # page 47. Example 2.7 

    V = [70, 20, 39, 37, 7, 5, 10]
    W = [31 ,10, 20, 19, 4, 3, 6]
    R = [1,  0,   0,  1, 0 ,0, 0]
    c = 50

    testSilvano(W, V, R, c)

if True: # NP weak: Equal-subset-sum knapsack for hardinstances_pisinger subset sum test dataset.

    if verbose:
        print("Run equal-subset-sum knapsack for hardinstances_pisinger subset sum test dataset.")

    script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in

    O = [0]

    with open(script_dir + '\hardInst.subset.sum.all.perf.csv', 'w', newline='') as csvfile:
        
        fieldnames = ['file', 'case', 'size', 'N', 'iter desc', 'iter non', 'max iter expected', 'desc time', 'non time', 'best iter', 'best time', 'good']
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()

        testCase = list()
        testExpected = list()
        testKnapsack = 0
        rowToSkip = 0

        files = ["knapPI_16_20_1000", "knapPI_16_50_1000"]
        #files = ["knapPI_16_20_1000", "knapPI_16_50_1000", "knapPI_16_100_1000", "knapPI_16_200_1000", "knapPI_16_500_1000"]

        fi = 0

        allGood = True

        for f in files:
            
            fi += 1

            caseNumber = 1

            with open(os.path.join(script_dir, "hardinstances_pisinger/" + str(f) + ".csv")) as csvfile:
                spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')

                for row in spamreader:

                    if  len(row) == 0:
                        continue

                    if row[0] == "-----":

                        O[0] = 0

                        testCase.sort(reverse=True)

                        if verbose:
                            print(f"{f} case {caseNumber}", end=" ")

                        maxIter = 4 * (len(testCase) ** 3)

                        t1 = time.perf_counter()

                        optDesc, optItemsDesc = subsKnapsack(testKnapsack, testCase, O)

                        t2 = time.perf_counter()

                        descTime = (round(t2 - t1, 4), "desc")

                        t1Full = time.perf_counter()

                        rezIterDesc = O[0]

                        O[0] = 0

                        prevUseLimits = doUseLimits

                        doUseLimits = False

                        optDescFull, optItemsDescFull = subsKnapsack(testKnapsack, testCase, O)

                        assert optDescFull == optDesc

                        doUseLimits = prevUseLimits

                        descTimeFull = (round(time.perf_counter() - t1Full, 4), "desc full")

                        rezIterDescFull = O[0]

                        O[0] = 0

                        rezS = sum(optItemsDesc) 
                        expS = sum(testExpected)

                        good = True

                        if  rezS < expS or optDesc > testKnapsack:
                            good = False
                            allGood = False
                            if verbose:
                                print(f" DESC rez opt: {optDesc}, test opt: {testKnapsack}, rez values: {rezS}, test values: {expS}", end=" ")

                        if rezIterDesc > maxIter:
                            if verbose:
                                print(f" DESC max iter exceeded: {maxIter} rez iter: {rezIterDesc}", end=" ")
                        
                        nonSortTestCase = list(testCase)

                        random.shuffle(nonSortTestCase)

                        O[0] = 0

                        t5 = time.perf_counter()

                        optNonSort, optItemstNonSort = subsKnapsack(testKnapsack, nonSortTestCase, O)

                        t6 = time.perf_counter()

                        nonTime = (round(t6 - t5, 4), "non")

                        rezSNon = sum(optItemstNonSort) 

                        rezIterNon = O[0]

                        if  rezSNon < expS or optNonSort > testKnapsack:
                            good = False
                            allGood = False
                            if verbose:
                                print(f" NON sort rez opt: {optNonSort}, test opt: {testKnapsack}, rez values: {rezSNon}, test values: {expS}", end=" ")
                        
                        if rezIterNon > 2 * maxIter:
                            if verbose:
                                print(f" NON sort  max iter exceeded: {2 * maxIter} rez iter: {rezIterNon}", end=" ")

                        bestTime = min([descTime, nonTime], key=lambda t : t[0])[1]

                        descIterItem = (rezIterDesc, "desc")    
                        nonIterItem  = (rezIterNon, "non")

                        bestIter = min([descIterItem, nonIterItem], key=lambda t : t[0])[1]

                        if verbose:
                            print(f" DESC {descTime[0]} NON {nonTime[0]} DESC FULL {descTimeFull[0]}")
        
                        writer.writerow({'file': str(f), 'case': str(caseNumber), 'size': str(testKnapsack), 'iter desc':  str(rezIterDesc), 'iter non':  str(rezIterNon), 'max iter expected': str(maxIter), 'N': str(len(testCase)), 'desc time': str(descTime[0]),  'non time': str(nonTime[0]), 'best iter': bestIter, 'best time': bestTime, 'good': str(good)})

                        testCase.clear()
                        testExpected.clear()

                        testCase = list()
                        testExpected = list()
                        testKnapsack = 0

                        caseNumber += 1                    

                        continue

                    if row[0].startswith("knapPI"):
                        rowToSkip = 6

                    if row[0].startswith("z "):
                        testKnapsack = int(row[0].split(" ")[1])            

                    rowToSkip -= 1

                    if rowToSkip <= 0:
                        testCase.append(int(row[1]))

                        if row[3] == "1":
                            testExpected.append(int(row[1]))
            assert allGood

if True: # NP complete: 1-0 knapsack for hardinstances_pisinger test dataset in case of integer and rational numbers.  

    if verbose:
        print("Run 1-0 knapsack for hardinstances_pisinger test dataset in case of integer and rational numbers.")

    with open(script_dir + '\\hardInst.2d.perf.decimal.csv', 'w', newline='') as csvfile:
        
        fieldnames = ['file', 'case', 'size', 'iter desc', 'iter non',  'max iter expected', 'N', 'desc time', 'non time', 'best iter', 'best time', 'good']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()

        testCaseW = list()
        testCaseV = list()
        testExpected = list()
        testKnapsack = 0
        rowToSkip = 0

        files = ["knapPI_11_20_1000", "knapPI_11_50_1000"]
        #files = ["knapPI_11_20_1000", "knapPI_11_50_1000", "knapPI_11_100_1000", "knapPI_11_200_1000"]

        for f in files:

            caseNumber = 1

            with open(os.path.join(script_dir, "hardinstances_pisinger/" + str(f) + ".csv")) as csvfile:
                spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')

                for row in spamreader:

                    if  len(row) == 0:
                        continue

                    if row[0] == "-----":

                        if verbose:
                            print(f"{f} case {caseNumber}", end=" ")

                        w, v = sortRevereseBoth(testCaseW, testCaseV)

                        maxIter = 10 * (len(w) ** 3)

                        expS = sum(testExpected)

                        O = [0]

                        t1 = time.perf_counter()

                        opt1Desc, optWeights1, optValues1, _ = knapsack(testKnapsack, w, v, O)

                        t2 = time.perf_counter()

                        descTime = (round(t2 - t1, 4), "desc")

                        rezIterDesc = O[0]    

                        O = [0]  

                        tFull1 = time.perf_counter()

                        prevUseLimits = doUseLimits

                        opt1DescFull, optWeights1Full, optValues1Full, _ = knapsack(testKnapsack, w, v, O)

                        doUseLimits = prevUseLimits

                        assert sum(optValues1Full) == sum(optValues1)

                        descTimeFull = (round(time.perf_counter() - tFull1, 4), "desc full")

                        rezIterDesc = O[0]                                    

                        if rezIterDesc > maxIter:
                            if verbose:
                                print(f"{caseNumber} max iter exceeded: {maxIter}  rez iter: {rezIterDesc}", end=" ")

                        rezSDesc = sum(optValues1) 
                        rezWSDesc = sum(optWeights1)

                        good = True

                        if rezSDesc < expS or rezWSDesc > testKnapsack:
                            good = False

                            if verbose:
                                print(f"{caseNumber} DESC rez opt: {opt1Desc}, test size: {testKnapsack}, rez sum weights: {rezWSDesc},  rez values: {rezSDesc},  test values: {expS}", end=" ")

                            assert False

                        O = [0]

                        t1 = time.perf_counter()

                        nTestKnapsack = wPoint((testKnapsack, testKnapsack))

                        opt2dDesc, optWeights2dDesc, optValues2dDesc = knapsackNd(nTestKnapsack, [wPoint((a, a)) for a in w], v, O)

                        t2 = time.perf_counter()

                        rezIter2DDesc = O[0]

                        desc2dTime = (round(t2 - t1, 4), "desc")
                        rezSDesc2d = sum(optValues2dDesc) 

                        if rezSDesc2d < expS or opt2dDesc > nTestKnapsack.getDimensions():
                            good = False

                            if verbose:
                                print(f"{caseNumber}  DESC 2D rez opt: {opt2dDesc}, test size: {testKnapsack}, rez values: {rezSDesc2d},  test values: {expS}", end=" ")

                            assert False

                        O = [0]

                        if len(v) <= 50: 

                            nonW, nonV = shuffleBoth(w, v)
                            t1 = time.perf_counter()

                            nTestKnapsack = wPoint((testKnapsack, testKnapsack))

                            opt2dNon, optWeights2dNon, optValues2dNon = knapsackNd(nTestKnapsack, [wPoint((a, a)) for a in nonW], nonV, O)

                            t2 = time.perf_counter()

                            rezIter2Dnon = O[0]

                            non2dTime = (round(t2 - t1, 4), "non")
                            nonSAsc2d = sum(optValues2dNon) 

                            if nonSAsc2d < expS or opt2dNon > nTestKnapsack.getDimensions():
                                good = False

                                if verbose:
                                    print(f"{caseNumber}  ASC 2D rez opt: {nonSAsc2d}, test size: {testKnapsack}, rez values: {nonSAsc2d},  test values: {expS}", end=" ")

                                assert False
                        else:
                            non2dTime = desc2dTime


                        O = [0]

                        t7 = time.perf_counter()

                        nonW, nonV = shuffleBoth(w, v)

                        opt1Non, optWeightsNon, optValuesNon, _ = knapsack(testKnapsack, nonW, nonV, O)

                        t8 = time.perf_counter()

                        nonTime = (round(t8 - t7, 4), "non")

                        if verbose:
                            print(f" INT DESC {descTime[0]} NON {nonTime[0]} DESC 2D {desc2dTime[0]} NON 2D {non2dTime[0]} DESC FULL {descTimeFull[0]}")

                        rezIterNon = O[0]

                        rezSNon = sum(optValuesNon) 
                        rezWSNon = sum(optWeightsNon) 

                        if rezSNon < expS or rezWSNon > testKnapsack:
                            good = False

                            if verbose:
                                print(f"{caseNumber} NON rez opt: {opt1Non}, test size: {testKnapsack}, rez weights: {rezWSNon},  test values: {expS}", end=" ")

                            assert False

                        bestTime = min([descTime, nonTime], key=lambda t : t[0])[1]

                        descIterItem = (rezIterDesc, "desc")
                        nonIterItem  = (rezIterNon, "non")

                        bestIter = min([descIterItem, nonIterItem], key=lambda t : t[0])[1] 
                    
                        writer.writerow({'file': str(f), 'case': str(caseNumber), 'size': str(testKnapsack), 'iter desc':  str(rezIterDesc), 'iter non':  str(rezIterNon), 'max iter expected': str(maxIter), 'N': str(len(testCaseW)), 'desc time': str(descTime[0]),  'non time': str(nonTime[0]), 'best iter': bestIter, 'best time': bestTime, 'good': str(good)})

                        decimalW = list(w)

                        DecimalArray(decimalW)

                        testKnapsackDecimal = DecimalData(testKnapsack)      

                        O = [0]

                        t1 = time.perf_counter()

                        optDec, optWeightsDec, optValuesDec, _ = knapsack(testKnapsackDecimal, decimalW, v, O)

                        t2 = time.perf_counter()

                        if verbose:
                            print(f" decimal desc dt {round(t2 - t1, 4)}")

                        rezSDecDesc = sum(optValuesDec) 
                        rezSWeightsDecDesc = sum(optWeightsDec) 

                        if rezSDecDesc != rezSDesc:
                            
                            sum_wh = 0

                            for on in optValuesDec:
                                itemIndex = v.index(on, 0, len(v))
                                wh = w[itemIndex]
                                sum_wh += wh

                            if verbose:
                                print(f"{caseNumber}  decimal values: {rezSDecDesc}, sum decimal w: {sum_wh}, test size: {testKnapsack}, test decimal size: {testKnapsackDecimal}, test values: {expS}", end=" ")
                            
                            assert False

                        testCaseW = list()
                        testCaseV = list()
                        testExpected = list()
                        testKnapsack = 0

                        caseNumber += 1
                        continue

                    if row[0].startswith("knapPI"):
                        rowToSkip = 6

                    if row[0].startswith("c "):
                        testKnapsack = int(row[0].split(" ")[1])            

                    rowToSkip -= 1

                    if rowToSkip <= 0:
                        testCaseW.append(int(row[2]))
                        testCaseV.append(int(row[1]))

                        if row[3] == "1":
                            testExpected.append(int(row[1]))

if True: # NP weak: N equal-subset-sum using integer partiton generator.

    def generate_partition(number, limitCount):
        answer = set()
        answer.add((number, ))
        for x in range(number - 1, 0, -1):
            for y in generate_partition(number - x, limitCount):
                answer.add(tuple(sorted((x, ) + y)))
                if len(answer) >= limitCount:
                    return answer
        return answer

    if verbose:
        print("N equal-subset-sum using integer partiton generator.")

    with open(script_dir + '\\partition.perf.over.intpart.csv', 'w', newline='') as csvfile:
        
        fieldnames = ['item', 'case', 'limit', 'partition', 'N', 'optimizations', 'iter', 'max iter', 'good']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()

        itemList = [1, 2, 3, 5, 7, 8, 10, 11]
        maxIntPart = [20, 50, 100, 200, 300, 500]
        caseId = 0

        allGood = True

        badItems = []

        for item in itemList:

            for partLimit in maxIntPart:

                for i in range(30, 55):

                    if i % item != 0:
                        continue

                    if caseId != 0 and caseId != i:
                        continue

                    O = [0]

                    subSet = []

                    partition = 0

                    goodSet = True

                    goodSubSet = []

                    for part in generate_partition(i, partLimit):

                        if sum(part) == i:
                            for p in part:
                                subSet.append(p)

                            goodSubSet.append(part)
                            partition += 1
                        else:
                            goodSet = False

                    if goodSet:

                        expectedSum = sum(subSet)

                        if verbose:
                            print(f"item = {item}, case i {i}, case part limit {partLimit}, n = {len(subSet)}, partition {partition} ", end ="")

                        t1 = time.perf_counter()

                        partResult, resultReminder, optCount = partitionN(subSet, partition, 0, O)

                        t2 = time.perf_counter()

                        if verbose:
                            print(f"iter {round(O[0])}, optimizations {optCount}, dt {t2-t1}")

                        resultPart = len(partResult)

                        rezSum = 0
                        for sub in partResult:
                            rezSum += sum(sub.Items)

                        good = True
                    
                        if resultPart < partition or rezSum != expectedSum or len(resultReminder) > 0:

                            allGood = False

                            good = False

                            badItems.append((item, i, ))

                            sumRem = sum(resultReminder.Items)

                            print(f"BAD: item = {item}, case i {i}, case part limit {partLimit}, n = {len(subSet)}, rezult partition {resultPart}, expected partition {partition}, rez sum {rezSum}, total sum {rezSum + sumRem}, expected sum {expectedSum} , iter {round(O[0])}")

                        writer.writerow({'item': str(item), 'case': str(i), 'limit': str(partLimit), 'partition':  str(partition), 'N': str(len(subSet)), 'optimizations': str(optCount), 'iter': str(round(O[0])), 'max iter': str(((partition) ** 3) * ((len(subSet)//partition) ** 4)), 'good': str(good)})

                        if not allGood:
                            break

        if len(badItems) > 0:
            print(badItems)

        assert allGood

if True: # NP hard: integer partition optimization tests. randomTestCount * 200

    if verbose:
        print("NP hard partition optimization integer tests.")

    O = [0]
    tests = []

    A, NU = [3, 383, 401, 405, 580, 659, 730, 1024, 1100, 1175, 1601, 2299, 3908, 4391, 4485, 5524], 4
    tests.append((A, NU))
    A, NU = [4,5,3,2,5,5,5,1,5,5,5,5,3,5,5,2], 13
    tests.append((A, NU))
    A, NU = [4,4,6,2,3,8,10,2,10,7], 4
    tests.append((A, NU))
    A, NU = [4,15,1,1,1,1,3,11,1,10], 3
    tests.append((A, NU))
    A, NU =  [20, 23, 25, 49, 45, 27, 40, 22, 19], 3
    tests.append((A, NU))
    A, NU = [20, 23, 25, 49, 45, 27, 40, 22, 19, 20, 23, 25, 49, 45, 27, 40, 22, 19], 6
    tests.append((A, NU))
    A, NU =  [27, 9, 9, 9, 9, 9, 3, 3, 3], 3
    tests.append((A, NU))
    A, NU = [10,10,10,7,7,7,7,7,7,6,6,6], 3
    tests.append((A, NU))
    A, NU = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1], 3
    tests.append((A, NU))
    A, NU = [10,12,1,2,10,7,5,19,13,1],4
    tests.append((A, NU))
    A, NU = [1,2,3,4,5,6,7,8,9],3

    for i in range(randomTestCount * 200):

        newSeed = dtNow + datetime.timedelta(seconds=i)

        random.seed(newSeed)

        if verbose:
            print(f"random seed is {newSeed}")

        case = 0

        for A, NU in tests:

            case += 1

            O[0] = 0

            if verbose:        
                print(f"case {case} ", end="")

            testCase = list(A)

            size = sum(A) // NU

            singleTestSizes = []

            for i in range(NU):
                singleTestSizes.append(size)
            
            lenT = len(testCase)

            reminderItemCnt = random.randint(1, len(A))

            sample = list(range(min(A), max(A) + 1))

            reminderItems = random.sample(sample, min(len(sample), reminderItemCnt))

            testCase += reminderItems

            t1 = time.perf_counter()

            partResult, reminder, optCount = partitionN(list(testCase), singleTestSizes, 0, O, 1000)     

            t2 = time.perf_counter()

            if verbose:  
                 print(f" time {round(t2 - t1, 2)}, opt count {optCount}")

            iterNum = O[0]

            optD = NU - len(partResult)

            if len(reminder) == 0 or optD > 0:

                if verbose:        
                    print("case " + str(case))
                    print("A " + str(A))
                    print("testCase " + str(testCase))
                    print("part result " + str(partResult))
                    print("part reminder  " + str(reminder))
                    print("reminderItems  " + str(reminderItems))
                    print("optCount  " + str(optCount))
                    print("len " + str(len(testCase)))
                    print("sum " + str(sum(testCase)))
                    print("sum // NU" + str(sum(testCase) // NU))
                    print("iter " + str(iterNum))

                assert False

if True: # NP hard: multidimensional  N=100, takes ~ 2m
    lConstraint = 20789
    wConstraint = 23681
    greedyOptimumValue  = 121105212 
    actualOptima        = 121147356
    dimensionMultiplier = 10000

    lwData100 =[[436,1490,649640   ],
                [232,1320,306240   ],
                [236,932,219952    ],
                [822,638,524436    ],
                [1004,1092,1096368 ],
                [266,1220,324520   ],
                [632,892,563744    ],
                [1110,344,381840   ],
                [598,532,318136    ],
                [658,921,606018    ],
                [732,1830,1339560  ],
                [822,1740,1430280  ],
                [932,1106,1030792  ],
                [598,732,437736    ],
                [568,1322,750896   ],
                [1792,1006,1802752 ],
                [1248,746,931008   ],
                [932,892,831344    ],
                [562,1030,578860   ],
                [722,1720,1241840  ],
                [1526,1448,2209648 ],
                [1858,2644,4912552 ],
                [1726,464,800864   ],
                [928,1672,1551616  ],
                [2028,932,1890096  ],
                [1028,1636,1681808 ],
                [756,748,565488    ],
                [926,916,848216    ],
                [2006,564,1131384  ],
                [1028,1894,1947032 ],
                [1376,1932,2658432 ],
                [726,1750,1270500  ],
                [2098,946,1984708  ],
                [1238,1208,1495504 ],
                [1026,768,787968   ],
                [1734,932,1616088  ],
                [994,2532,2516808  ],
                [1966,2422,4761652 ],
                [2828,1946,5503288 ],
                [1536,1788,2746368 ],
                [436,732,319152    ],
                [732,822,601704    ],
                [636,932,592752    ],
                [822,598,491556    ],
                [1004,568,570272   ],
                [464,794,368416    ],
                [932,648,603936    ],
                [2110,934,1970740  ],
                [598,562,336076    ],
                [656,726,476256    ],
                [926,3726,3450276  ],
                [1490,1830,2726700 ],
                [1320,1740,2296800 ],
                [932,2100,1957200  ],
                [636,732,465552    ],
                [1094,1324,1448456 ],
                [1222,2408,2942576 ],
                [894,748,668712    ],
                [548,894,489912    ],
                [532,2138,1137416  ],
                [452,642,290184    ],
                [722,1264,912608   ],
                [924,674,622776    ],
                [824,632,520768    ],
                [724,936,677664    ],
                [754,446,336284    ],
                [922,316,291352    ],
                [2002,892,1785784  ],
                [576,1932,1112832  ],
                [726,1750,1270500  ],
                [1974,944,1863456  ],
                [1234,1206,1488204 ],
                [1224,766,937584   ],
                [1734,932,1616088  ],
                [994,2532,2516808  ],
                [564,2422,1366008  ],
                [722,1944,1403568  ],
                [1536,788,1210368  ],
                [648,1232,798336   ],
                [1024,894,915456   ],
                [236,248,58528     ],
                [542,126,68292     ],
                [236,542,127912    ],
                [128,128,16384     ],
                [1026,2788,2860488 ],
                [9098,8726,79389148],
                [5468,3524,19269232],
                [1264,4524,5718336 ],
                [2354,1298,3055492 ],
                [1698,2542,4316316 ],
                [2542,5004,12720168],
                [582,894,520308    ],
                [566,894,506004    ],
                [564,1022,576408   ],
                [1254,2014,2525556 ],
                [2012,1254,2523048 ],
                [1256,1298,1630288 ],
                [2350,2366,5560100 ],
                [2502,2502,6260004 ],
                [1296,2366,3066336 ]]

  
    values = [p[2] for p in lwData100]
    items = [wPoint2(p[0] * dimensionMultiplier, p[1] * dimensionMultiplier) for p in lwData100]
    constraints =  wPoint2(lConstraint * dimensionMultiplier, wConstraint * dimensionMultiplier)

    if verbose:
        print(f"multidimensional N={len(values)} knapsack test")

    O = [0]

    t1 = time.perf_counter()

    optDims, optItems, optValues = knapsackNSolver(constraints, items, values, O, wPoint2(0, 0)).solve()

    if verbose:
        print(f"total val: {sum(values)} opt val: {sum(optValues)}, iter: {round(O[0])}, time: {time.perf_counter() - t1}, items: {optItems}")

    assert sum(optValues) >= greedyOptimumValue 
    
printPct = True

if True: # Polynominal: subsKnapsack report for [1] * 50
    
    if verbose:
        print("report:[1] * 50")
    
    numbers = [1] * 50

    if verbose:
        print(f"len {len(numbers)} sum {sum(numbers)}")

    if True:
            
        O = [0]

        prevO = 0
        prevPareto = 0

        if True:

            s = sum(numbers) - 1

            O[0] = 0

            t1 = time.perf_counter()

            opt, optItems1 = subsKnapsack(s, numbers, O)

            subsTime = time.perf_counter() - t1

            o1 = round(O[0])

            O[0] = 0

            t1 = time.perf_counter()

            opt2, optItems2, optVal3, _ = knapsack(s, numbers, numbers, O)

            knapTime = time.perf_counter() - t1

            o2 = round(O[0])
            
            O[0] = 0

            t1 = time.perf_counter()

            ids = paretoKnapsack(numbers, numbers, s, O)

            paretoTime = time.perf_counter() - t1

            o3 = round(O[0])

            optItems3 = [numbers[id] for id in ids]
            opt3 = sum(optItems2)

            if opt != opt3 or opt2 != opt3:
                print(f"{opt} - {opt2} - {opt3}, size {s}")
                assert False

            prevO = o1
            prevPareto = o2

if True: # Polynominal: subsKnapsack report for ([1] * 25) + ([2] * 25)
    if verbose:
        print("report: [1] * 25) + ([2] * 25")
    
    numbers = ([1] * 25) + ([2] * 25)

    if verbose:
        print(f"len {len(numbers)} sum {sum(numbers)}")

    if True:
            
        O = [0]

        prevO = 0
        prevPareto = 0

        if True:

            s = sum(numbers) - 1

            O[0] = 0

            opt, optItems1 = subsKnapsack(s, numbers, O)

            o1 = round(O[0])

            O[0] = 0

            t1 = time.perf_counter()

            opt2, optItems2, optVal3, _ = knapsack(s, numbers, numbers, O)

            knapTime = time.perf_counter() - t1

            o2 = round(O[0])
            
            O[0] = 0

            ids = paretoKnapsack(numbers, numbers, s, O)

            o2 = round(O[0])

            optItems3 = [numbers[id] for id in ids]
            opt3 = sum(optItems3)

            if opt != opt2 or opt != opt3:
                print(f"{opt} - {opt2} - {opt3}, size {s}")
                assert False


            prevO = o1
            prevPareto = o2

if True: # Polynominal: subsKnapsack report for list(range(1, 51))
   
    if verbose:
        print("report: list(range(1, 51))")
    
    numbers = list(range(1, 51))

    if verbose:
        print(f"len {len(numbers)} sum {sum(numbers)}")

    if True:
            
        O = [0]

        prevO = 0
        prevPareto = 0

        if True:

            s = sum(numbers) - 1

            O[0] = 0

            opt, optItems1 = subsKnapsack(s, numbers, O)

            print(s)

            o1 = round(O[0])

            O[0] = 0

            t1 = time.perf_counter()

            opt2, optItems2, optVal3, _ = knapsack(s, numbers, numbers, O)

            knapTime = time.perf_counter() - t1

            o2 = round(O[0])
            
            O[0] = 0

            ids = paretoKnapsack(numbers, numbers, s, O)

            o3 = round(O[0])

            optItems3 = [numbers[id] for id in ids]
            opt3 = sum(optItems3)

            if opt != opt2 or opt != opt3:
                print(f"{opt} - {opt2} - {opt3}, size {s}")
                assert False

            prevO = o1
            prevPareto = o2

if True: # Polynominal: subsKnapsack report for random.sample(range(1, 1000), 50)
    
    if verbose:
        print("report: random.sample(range(1, 1000), 50)")

    numbers = random.sample(range(1, 1000), 50)
    numbers.sort(reverse=True)

    if verbose:
       print(f"len {len(numbers)} sum {sum(numbers)}")

    if True:            
        O = [0]

        prevO = 0
        prevPareto = 0

        if True:

            s = sum(numbers) - 1

            O[0] = 0

            opt, optItems1 = subsKnapsack(s, numbers, O)

            print(s)

            o1 = round(O[0])

            O[0] = 0

            t1 = time.perf_counter()

            opt2, optItems2, optVal3, _ = knapsack(s, numbers, numbers, O)

            knapTime = time.perf_counter() - t1

            o2 = round(O[0])
            
            O[0] = 0

            ids = paretoKnapsack(numbers, numbers, s, O)

            o3 = round(O[0])

            optItems3 = [numbers[id] for id in ids]
            opt3 = sum(optItems3)

            if opt != opt2 or (opt != opt3 and opt3 < s):
                print(f"{opt} - {opt2} size {s}")
                assert False

            prevO = o1
            prevPareto = o2

if True: # Polynominal: subsKnapsack report for random.sample(range(1, 10000000000000000), 15)
    
    if verbose:
        print("report: random.sample(range(1, 10000000000000000), 15)")
    
    numbers = random.sample(range(1, 10000000000000000), 15)
    numbers.sort(reverse=False)
   
    if verbose:
        print(f"len {len(numbers)} sum {sum(numbers)}")

    for i in range(10):

        newSeed = dtNow + datetime.timedelta(seconds=i)
            
        O = [0]

        prevO = 0
        prevPareto = 0

        if True:

            s = sum(numbers) - 1

            O[0] = 0

            opt, optItems1 = subsKnapsack(s, numbers, O)

            print(s)

            o1 = round(O[0])

            O[0] = 0

            t1 = time.perf_counter()

            opt2, optItems2, optVal3, _ = knapsack(s, numbers, numbers, O)

            knapTime = time.perf_counter() - t1

            o2 = round(O[0])
            
            O[0] = 0

            ids = paretoKnapsack(numbers, numbers, s, O)

            o3 = round(O[0])

            optItems3 = [numbers[id] for id in ids]
            opt3 = sum(optItems3)

            if opt != opt2 or (opt != opt3 and opt3 < s):
                print(f"{opt} - {opt2} - {opt3}, size {s}, numbers: {numbers}")
                assert False

            prevO = o1
            prevPareto = o2

if True: # Polynominal: subsKnapsack report for geometric progression numbers = [10000] * 15; numbers[i] *= (int(numbers[i - 1] * 2) - 1)
    
    if verbose:
        print("report: numbers = [10000] * 15; numbers[i] *= (int(numbers[i - 1] * 2) - 1")

    numbers = [10000] * 15

    for i in range(1, 15):
        numbers[i] = (int(numbers[i - 1] * 2) - 1)

    numbers.append(numbers[len(numbers) // 2])

    numbers.sort(reverse=False)
   
    if verbose:
        print("len " + str(len(numbers)))
        print("sum " + str(sum(numbers)))        

    if True:

        O = [0]

        prevO = 0
        prevPareto = 0

        if True:
            s = sum(numbers) - 1

            O[0] = 0

            opt1, optItems1 = subsKnapsack(s, numbers, O)

            o1 = round(O[0])

            print(o1)

            O[0] = 0

            t1 = time.perf_counter()

            opt2, optItems2, optVal3, _ = knapsack(s, numbers, numbers, O)

            knapTime = time.perf_counter() - t1

            o2 = round(O[0])
            
            O[0] = 0

            ids = paretoKnapsack(numbers, numbers, s, O)

            o3 = round(O[0])

            optItems3 = [numbers[id] for id in ids]
            opt3 = sum(optItems3)

            if opt1 != opt2 or opt1 != opt3:
                print(f"{opt1} - {opt2} - {opt3}, size {s}")
                assert False

            prevO = o1
            prevPareto = o2

if True: # Exponental: 1-0 KB knapsack report for geometric progression numbers = [1] * 15; numbers[i] *= (int(numbers[i - 1] * 2) - 1); values are random in [1..1000]
    
    if verbose:
        print("report: numbers = [1] * 15; numbers[i] *= (int(numbers[i - 1] * 2) - 1); values are random in [1..1000]")

    numbers = [1000] * 20
    values = [1] * 20

    for i in range(1, 20):
        numbers[i] = (int(numbers[i - 1] * 2) - 1)
        values[i] = random.randint(1, 1000)
   
    if verbose:
        print("len " + str(len(numbers)))
        print("sum " + str(sum(numbers)))        

    if True:
            
        O = [0]

        if True:
            sumCases = [(sum(numbers) // 2) - 1, ((sum(numbers)//4) * 3 - 1), sum(numbers) - 1,]

            for s in sumCases:

                print(f"case size {s}")

                O[0] = 0

                t1 = time.perf_counter()

                opt2, optItems2, optVal2, _ = knapsack(s, numbers, values, O)

                knapTime = time.perf_counter() - t1

                o2 = round(O[0])

                optValSum2 = sum(optVal2)
                
                O[0] = 0

                print("pareto")

                ids = paretoKnapsack(numbers, values, s, O)

                o3 = round(O[0])

                optValues3 = [values[id] for id in ids]
                optValSum3 = sum(optValues3)

                if optValSum2 != optValSum3:
                    print(f"{optValSum2} - {optValSum3}, size {s}, numbers: {numbers}, values = {values}")

if True: # Polynominal: 1-0 knapsack report for range(9500, 10000), 25
   
    if verbose:
        print("report: range(9500, 10000), 25; values = random.sample(range(1, 100000), 25)")


    numbers = random.sample(range(9500, 10000), 25)
    values = random.sample(range(1, 100000), 25)
   
    if verbose:
        print("len " + str(len(numbers)))
        print("sum " + str(sum(numbers)))        

    if True:
            
        O = [0]

        if True:

            sumCases = [sum(numbers)//2,  (sum(numbers)//4) * 3, sum(numbers) - 1,]

            for s in sumCases:

                print(f"case size {s}")

                O[0] = 0

                t1 = time.perf_counter()

                opt2, optItems2, optVal2, _ = knapsack(s, numbers, values, O)

                knapTime = time.perf_counter() - t1

                o2 = round(O[0])

                optValSum2 = sum(optVal2)
                
                O[0] = 0

                ids = paretoKnapsack(numbers, values, s, O)

                o3 = round(O[0])

                optValues3 = [values[id] for id in ids]
                optValSum3 = sum(optValues3)

                if optValSum2 != optValSum3:
                    print(f"{optValSum2} - {optValSum3}, size {s}, numbers: {numbers}, values = {values}")
