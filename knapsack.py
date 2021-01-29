from collections import defaultdict
from collections import deque
from decimal import Decimal
from typing import List 

import statistics
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

def partitionN(items, sizesOrPartitions, groupSize, O, optimizationLimit = -1):

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

    def prepareGrouping(A, O):

        group = defaultdict(list)

        for c in A:
            group[c].append(c)   
        
        O[0] += len(A)

        return group
    
    def groupItems(group, O):

        allUnique = True
        nonUniqueList = defaultdict(int)

        for k in group.keys():        

            nonUniqueList[k] += len(group[k])
            
            if len(group[k]) > 1:
                allUnique = False

        O[0] += len(group)

        return allUnique, nonUniqueList

    def getSingleDuplicatePartitions(items, count, sizes, groupSize, O):

        quotientResult, remainderResult  = [], []

        if groupSize == 0:
            stack = list(items)
            currentQuotient = []
            ls = list(sizes)

            while len(ls) > 0:
                size = ls.pop()
                qs = 0
                while len(stack) > 0:
                    item = stack.pop()

                    qs += item

                    if qs <= size:
                        currentQuotient.append(item)
                    
                    if qs >= size:
                        qs = 0
                        quotientResult.append(currentQuotient)
                        currentQuotient = []

            remainderResult = currentQuotient 

            for item in stack:
                remainderResult.append(item)
                      
        else:

            stack = list(items)
            currentQuotient = []

            while len(stack) > 0:
                item = stack.pop()
                if len(currentQuotient) < groupSize:
                    currentQuotient.append(item)
                    if len(currentQuotient) == groupSize:
                        quotientResult.append(currentQuotient)
                        currentQuotient = []  

            remainderResult = currentQuotient 

            for item in stack:
                remainderResult.append(item)

        return  quotientResult, remainderResult, 0 

    def optimizePartitions(quotients, remainder, sizes, groupSize, optimizationLimit, O):

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

            if limit == 1:
                newSet = list(mergeTwoSortedReversedIter(remainderItem.Items, p.Items))
                newSizes = list(remainderItem.Sizes)

                for s in p.Sizes:
                    newSizes.append(s)

                O[0] += len(p.Items) + len(remainderItem.Items)
                O[0] += len(p.Sizes) + len(remainderItem.Sizes)  

            elif limit == 2:
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

            return  divideSet(newSet, newSizes, groupSize, O)

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

            if verbose and limit > 4:
                print(f"performimg optimizations at the same time is limited by: {limit}; quotients: {len(quotients)} reminder len {len(remainder)}")

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

    def sortDuplicatesForPartitioning(group, count, nonUniqueList, O):
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

    def partitionOverSameCountDuplicates(nonUniqueList, sizes, groupSize, optimizationLimit, O):

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
            
            quotient, remainder, optCount = divideSet(nonUKeys, newSizes, groupSize, O)

            quotientResult, remainderResult  = [], []

            for i in range(cnt):
                for item in quotient:
                    quotientResult.append(item.Items)
                for rem in remainder.Items:
                    remainderResult.append(rem)

            if  len(remainderResult) == 0 or len(quotientResult) == len(sizes) or len(quotients) == 0:
                return quotientResult, remainderResult, optCount

            return optimizePartitions(remainderResult, quotientResult, sizes, groupSize, optimizationLimit, O)

        return None

    def divideSet(items, sizes, groupSize, O):    

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

                dimensions, constrains  = [wPoint((item, 1)) for item in reminderItems], wPoint((size, groupSize))
                O[0] += len(reminderItems)              

                opt, optDims, optValues = knapsackNd(constrains, dimensions, reminderItems, O)

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

                optimal, optimalList = subsKnapsack(size, reminderItems,  O)

                if optimal == size:          

                    quotients.append(partitionItem(optimalList, [size]))

                    for toRemove in optimalList:
                        reminderItems.remove(toRemove)  

                    O[0] += len(optimalList)    
                else:
                    reminderSizes.append(size)

        return quotients, partitionItem(reminderItems, reminderSizes), 0

    def getSizes(sizesOrPartitions):
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

    count = len(items)
    sizes, sameSizes = getSizes(sizesOrPartitions)

    if  count < len(sizes):
        return [], [], 0
    
    group = prepareGrouping(items, O)   
    allUnique, nonUniqueList = groupItems(group, O)

    if len(nonUniqueList) == 1:
        return getSingleDuplicatePartitions(items, count, sizes, groupSize, O)

    quotients, remainder, optCount = [], [], 0

    if  allUnique:
        items.sort(reverse = True)
        O[0] += count * math.log2(count)

        quotients, remainder, optCount = divideSet(items, sizes, groupSize, O)
    else:
        if  len(nonUniqueList) > len(sizes) and groupSize == 0 and sameSizes:
            partResult = partitionOverSameCountDuplicates(nonUniqueList, sizes, 0, optimizationLimit, O)
            if partResult:
                return partResult

        sortedDuplicates = sortDuplicatesForPartitioning(group, count, nonUniqueList, O)
        quotients, remainder, optCount = divideSet(sortedDuplicates, sizes, groupSize, O)    
   
    if  len(remainder) == 0 or len(quotients) == len(sizes) or len(quotients) == 0:
        return quotients, remainder, optCount

    return optimizePartitions(quotients, remainder, sizes, groupSize, optimizationLimit, O)   

def subsKnapsack(size, items, O):

    def prepare(size, items, O):
        
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
                      
            if allDesc:
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
        
        O[0] += count
        return count, itemSum, lessCountSum, partialSums, starting, ending, isSuperIncreasing, superIncreasingItems, allDesc

    def checkCornerCases(size, items, sum, lessCountSum, O):        

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
  
    def yieldOrPushBack(circularPointQuene, newPoint, greaterQu):
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

    def getPoints(itemWeight, size, circularPointQuene, itemLimit, oldPointLimit, newPointLimit, prevCyclePointCount, uniquePointSet):
       

        # merges ordered visited points with new points with keeping order in O(N) using single circular queue. 
        # each getPoints method call starts fetching visited points from qu start, pops visited point and pushes new point and visited to the end of qu in ASC order.
        # we skip new point if it in list already
        # skips points if they will not contribute to optimal solution

        greaterQu = deque()

        useItemItself = itemLimit >= size // 2

        if useItemItself and not itemWeight in uniquePointSet:
            for p in yieldOrPushBack(circularPointQuene, itemWeight, greaterQu):
                yield p

        for i in range(prevCyclePointCount):

            oldPoint = circularPointQuene.popleft()             

            while len(greaterQu) > 0 and greaterQu[0] < oldPoint:

                quPoint = greaterQu.popleft()
               
                yield quPoint 
                circularPointQuene.append(quPoint)

            if  oldPoint >= oldPointLimit:

                for p in yieldOrPushBack(circularPointQuene, oldPoint, greaterQu):
                    yield p
         
            newPoint = oldPoint + itemWeight

            if  newPoint < newPointLimit:
                continue

            if newPoint <= size and not newPoint in uniquePointSet:   

                for p in yieldOrPushBack(circularPointQuene, newPoint, greaterQu):
                    yield p
        
        while len(greaterQu) > 0:

            quPoint = greaterQu.popleft()

            yield quPoint 
            circularPointQuene.append(quPoint)    

    def getValue(point, dp):

        if point in dp:
           return dp[point]
        
        return 0
    
    def getPossibleValue(point, itemValue, dp):

        if point in dp:
           return dp[point] + itemValue

        if point < 0:
            return None
        
        return itemValue

    def setValue(curDP, p, curVal, O):
        curDP[p] = curVal     
        O[0] += 1

    def backTraceItems(DP, resultI, resultP, items, O):
        opt = 0
        res = DP[resultI][resultP]
        optWeights = []
        point = resultP
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

    def createDP(count, starting):
        DP    = [None] * (count + 1)
        for i in range(starting):
            DP[i] = defaultdict(int)
        return DP

    def solveSuperIncreasing(size, items, starting, ending, count, desc, O):

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

        binSearch = indexLargestLessThanDesc if desc else indexLargestLessThanAsc

        resultItems = []
        resultSum = 0
        index = binSearch(items, size, starting - 1, ending - 1, O) 

        while index is not None:
            value = items[index]
            resultItems.append(value)
            resultSum += value
            if desc:
                index = binSearch(items, size - resultSum, index + 1, ending - 1, O)
            else:
                index = binSearch(items, size - resultSum, starting - 1, index - 1, O)
            O[0] += 1
        
        if verbose:
            print(f"Superincreasing solver called for size {size} and count {count}. desc={desc}")
        
        return resultSum, resultItems

    def getLimits(size, i, items, partialSums, superIncreasingItems, allDesc):

        partSumForItem = partialSums[i - 1]
        superIncreasingItem = superIncreasingItems[i - 1]

        newPointLimit = size - partSumForItem
        oldPointLimit = newPointLimit

        if doSolveSuperInc and superIncreasingItem:
            oldPointLimit = size - items[i - 2] if allDesc else newPointLimit - items[i] if i < len(items) else newPointLimit

        return partSumForItem, oldPointLimit, newPointLimit  
    
    count, sum, lessCountSum, partialSums, starting, ending, isSuperIncreasing, superIncreasingItems, allDesc  = prepare(size, items, O)

    cornerCasesCheck = checkCornerCases(size, items, sum, lessCountSum, O)

    if  cornerCasesCheck:
        return cornerCasesCheck

    if doSolveSuperInc and isSuperIncreasing:
        return solveSuperIncreasing(size, items, starting, ending, count, allDesc, O) 

    DP = createDP(count, starting)

    resultI, resultP = 1, 1

    circularPointQuene = deque()

    maxValue, prevPointCount, newPointCount = -sys.maxsize, 0, 0

    for i in range(starting, ending + 1):
      
        DP[i] = defaultdict()

        prevPointCount, newPointCount = newPointCount, prevPointCount
        newPointCount = 0

        if printPct and i > 1:
            print(f"| {i} | {prevPointCount} | {round(O[0])} |")

        itemValue, itemWeight = items       [i - 1], items[i - 1]
        prevDP,    curDP      = DP          [i - 1],    DP[i]

        itemLimit, oldPointLimit, newPointLimit    = getLimits(size, i, items, partialSums, superIncreasingItems, allDesc)

        for p in getPoints(itemWeight, size, circularPointQuene, itemLimit, oldPointLimit, newPointLimit, prevPointCount, prevDP):          

            curValue    =  getValue(p,              prevDP)  
            posblValue  =  getPossibleValue(p - itemWeight, itemValue, prevDP) 

            if posblValue and curValue < posblValue and posblValue <= size:
                curValue = posblValue

            setValue(curDP, p, curValue, O)

            if  maxValue < curValue:
                resultP = p
                resultI = i
                maxValue = curValue            

            if  size == curValue:
                return backTraceItems(DP, resultI, resultP, items, O)  

            newPointCount += 1 

    return backTraceItems(DP, resultI, resultP, items, O)

def knapsack(size, weights, values, O):
    
    def prepare(constraints, items, values, O):
        
        count = len(items)
        itemSum1, itemSum2, lessCountSum = 0, 0, 0

        lessSizeItems, lessSizeValues = [], []

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

                if allValuesEqual or allValuesEqualToConstraints:
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
            
            partialSums = []
            superIncreasingItems = []
            isSuperIncreasing = False
            itemSum = itemSum2

            canUsePartialSums = allValuesEqual or allValuesEqualToConstraints
        
            if allDesc and canUsePartialSums:
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
        
        O[0] += count
        return lessCount,  lessSizeItems, lessSizeValues, itemSum, lessCountSum, partialSums, isSuperIncreasing, superIncreasingItems, allDesc

    def checkCornerCases(size, lessSizeItems, lessSizeValues, lessCountSum, itemSum):        

        if  lessCountSum == 0:
            return 0,[],[]
        
        if  lessCountSum <= size:
            return lessCountSum, lessSizeItems, lessSizeValues

        if  itemSum <= size:
            return itemSum, lessSizeItems, lessSizeValues 

        return None      
     
    def yieldOrPushBack(circularPointQuene, newPoint, greaterQu):
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

    def getPoints(itemWeight, size, circularPointQuene, itemLimit, oldPointLimit, newPointLimit, prevCyclePointCount, uniquePointSet):
        
        # merges ordered visited points with new points with keeping order in O(N) using single circular queue. 
        # each getPoints method call starts fetching visited points from qu start, pops visited point and pushes new point and visited to the end of qu in ASC order.
        # we skip new point if it in list already

        useItemItself = itemLimit >= size // 2

        greaterQu = deque()

        if useItemItself and not itemWeight in uniquePointSet:         
            for p in yieldOrPushBack(circularPointQuene, itemWeight, greaterQu):
                yield p

        for i in range(prevCyclePointCount):

            oldPoint = circularPointQuene.popleft()             

            while len(greaterQu) > 0 and greaterQu[0] < oldPoint:

                quPoint = greaterQu.popleft()
               
                yield quPoint 
                circularPointQuene.append(quPoint)

            if  oldPoint >= oldPointLimit:

                for p in yieldOrPushBack(circularPointQuene, oldPoint, greaterQu):
                    yield p

            newPoint = oldPoint + itemWeight

            if  newPoint < newPointLimit:
                continue

            if newPoint <= size and not newPoint in uniquePointSet: 

                for p in yieldOrPushBack(circularPointQuene, newPoint, greaterQu):
                    yield p
        
        while len(greaterQu) > 0:

            quPoint = greaterQu.popleft()

            yield quPoint 
            circularPointQuene.append(quPoint)

    def getValue(p, prevDP):

        if p in prevDP:
            cur = prevDP[p]
            return cur[0], cur[1]
      
        return 0, 0
      
    def getPossibleValue(point, itemValue, itemWeight,  dp):

        if point in dp:
            cur = prevDP[point]
            return cur[0] + itemValue, cur[1] + itemWeight

        if point < 0:
            return None, None
        
        return itemValue, itemWeight

    def setValue(curDP, p, curVal, curW,  O):
        curDP[p] = (curVal, curW)               
        O[0] += 1

    def backTraceItems(DP, resultI, resultP, weights, values, O):
        opt = 0
        res = DP[resultI][resultP][0]
        optWeights, optValues = [], []
        point = resultP

        for i in range(resultI, 0, -1): 
           
            O[0] += 1

            if res <= 0: 
                break      

            dpw = DP[i - 1]

            skip = False

            if point in dpw:
                skip = res == dpw[point][0] 

            if not skip:       
                itemWeight, itemValue = weights[i - 1], values[i - 1]    

                optWeights.append(itemWeight)
                optValues.append(itemValue)

                res   -= itemValue
                point -= itemWeight

                opt += itemWeight

        return opt, optWeights, optValues

    def createDP(count):
        DP    = [None] * (count + 1)
        DP[0] = defaultdict()
        return DP

    def solveSuperIncreasing(size, items, values, count, desc, O):

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

            cnt = len(items)

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
       
        binSearch = indexLargestLessThanDesc if desc else indexLargestLessThanAsc

        starting = 1
        resultItems = []
        resultValues = []
        resultSum = 0
        index = binSearch(items, size, starting - 1, count - 1, O)

        while index is not None:
            item = items[index]
            value = values[index]
            resultItems.append(item)
            resultValues.append(value)
            resultSum += value
            if desc:
                index = binSearch(items, size - resultSum, index + 1, count - 1, O)
            else:
                index = binSearch(items, size - resultSum, starting - 1, index - 1, O)
            O[0] += 1

        if verbose:
            print(f"Superincreasing solver called for size {size} and count {count}.  desc={desc}")
        
        return resultSum, resultItems, resultValues

    def getLimits(size, i, items, partialSums, superIncreasingItems, allDesc):

        partSumForItem = partialSums[i - 1]
        superIncreasingItem = superIncreasingItems[i - 1]

        newPointLimit = size - partSumForItem
        oldPointLimit = newPointLimit

        if doSolveSuperInc and superIncreasingItem:
            oldPointLimit = size - items[i - 2] if allDesc else newPointLimit - items[i] if i < len(items) else newPointLimit

        return partSumForItem, oldPointLimit, newPointLimit  

    count, lessSizeItems, lessSizeValues, itemSum, lessCountSum, partialSums, superIncreasing, superIncreasingItems, allDesc = prepare(size, weights, values, O)

    cornerCasesCheck = checkCornerCases(size, lessSizeItems, lessSizeValues, lessCountSum, itemSum)

    if  cornerCasesCheck:
        return cornerCasesCheck

    if doSolveSuperInc and superIncreasing:
        return solveSuperIncreasing(size, lessSizeItems, lessSizeValues, count, allDesc, O)

    DP = createDP(count)

    resultI, resultP = 1, 1

    circularPointQuene = deque()

    maxValue, prevPointCount, newPointCount = -sys.maxsize, 0, 0

    for i in range(1, count + 1):

        DP[i] = defaultdict()

        itemValue, itemWeight   = lessSizeValues[i - 1], lessSizeItems[i - 1]
        prevDP,    curDP        = DP    [i - 1],      DP[i]       

        itemLimit, oldPointLimit, newPointLimit   = getLimits(size, i, lessSizeItems, partialSums, superIncreasingItems, allDesc)

        prevPointCount, newPointCount = newPointCount, prevPointCount
        newPointCount = 0

        for p in getPoints(itemWeight, size, circularPointQuene, itemLimit, oldPointLimit, newPointLimit, prevPointCount, prevDP):          

            curValue,   curWeight   =  getValue(p,              prevDP) 
            posblValue, posblWeight =  getPossibleValue(p - itemWeight, itemValue, itemWeight, prevDP) 

            if posblValue and curValue < posblValue and posblWeight <= size:
                curValue = posblValue
                curWeight = posblWeight
               
            setValue(curDP, p, curValue, curWeight, O)

            if  maxValue < curValue:
                resultP = p
                resultI = i
                maxValue = curValue
            
            newPointCount += 1

    return backTraceItems(DP, resultI, resultP, lessSizeItems, lessSizeValues, O) 

class wPoint:
    def __init__(self, dimensions):
        self.dimensions = tuple(dimensions)

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

        anyLess = False
        for i in range(l):

            if self.dimensions[i] == other.dimensions[i]:
                continue

            if self.dimensions[i] < other.dimensions[i]:                 
                anyLess = True
            else:
                break

        return anyLess  
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

        anyLess = False
        for i in range(l):

            if self.dimensions[i] == other.dimensions[i]:
                continue

            if other.dimensions[i] < self.dimensions[i]:                 
                anyLess = True
            else:
                break

        return anyLess  
    # >=
    def __ge__(self, other):
        l = len(self.dimensions)
        for i in range(l):
            
            if other.dimensions[i] > self.dimensions[i]: 
                return False

        return True   
    
    def __eq__(self, other):
        return self.dimensions == other.dimensions

    def __hash__(self):
        return hash(self.dimensions)

def knapsackNd(constraints, items, values, O):

    emptyPoint = wPoint([0] * constraints.getSize())
    
    def prepare(constraints, items, values, O):
        
        count = len(items)
        itemSum1, itemSum2, lessCountSum = emptyPoint, emptyPoint, emptyPoint

        lessSizeItems, lessSizeValues = [], []

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
                
                if allValuesEqualToConstraints and not item2.firstDimensionEqual(itemValue2):
                    allValuesEqualToConstraints = False

                itemSum1 += item1
                itemSum2 += item2

                if allValuesEqual or allValuesEqualToConstraints:
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
            
            partialSums = []
            superIncreasingItems = []
            isSuperIncreasing = False
            itemSum = itemSum2

            canUsePartialSums = allValuesEqual or allValuesEqualToConstraints
        
            if allDesc and canUsePartialSums:
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
        
        O[0] += count
        return lessCount,  lessSizeItems, lessSizeValues, itemSum, lessCountSum, partialSums, isSuperIncreasing, superIncreasingItems, allDesc

    def checkCornerCases(constraints, lessSizeItems, lessSizeValues, lessCountSum, itemSum):        

        if  lessCountSum == emptyPoint:
            return emptyPoint.dimensions, [],[]
        
        if  lessCountSum <= constraints:
            return lessCountSum.dimensions, lessSizeItems, lessSizeValues

        if  itemSum <= constraints:
            return itemSum.dimensions, lessSizeItems, lessSizeValues 

        return None   
    
    def yieldOrPushBack(circularPointQuene, newPoint, greaterQu):
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
  
    def getPoints(itemDimensions, constraintPoint, circularPointQuene, halfConstraint, itemLimit, oldPointLimit, newPointLimit, prevCyclePointCount, uniquePointSet):
        
        # merges ordered visited points with new points with keeping order in O(N) using single circular queue. 
        # each getPoints method call starts fetching visited points from qu start, pops visited point and pushes new point and visited to the end of qu in ASC order.
        # we skip new point if it in list already
        # skips points if they will not contribute to optimal solution (in case of desc flow and (equal values or values equal to first dimension))

        greaterQu = deque()

        useItemItself = itemLimit is None or itemLimit >= halfConstraint
        
        if useItemItself and not itemDimensions in uniquePointSet:

            for p in yieldOrPushBack(circularPointQuene, itemDimensions, greaterQu):
                yield p

        for i in range(prevCyclePointCount):

            oldPoint = circularPointQuene.popleft()             

            while len(greaterQu) > 0 and greaterQu[0] < oldPoint:

                quPoint = greaterQu.popleft()

                yield quPoint 
                circularPointQuene.append(quPoint)

            if not oldPointLimit or oldPoint >= oldPointLimit:

                for p in yieldOrPushBack(circularPointQuene, oldPoint, greaterQu):
                    yield p

            newPoint = oldPoint + itemDimensions

            if newPointLimit and newPoint < newPointLimit:
                continue

            if newPoint <= constraintPoint: 

                if not newPoint in uniquePointSet:   

                    for p in yieldOrPushBack(circularPointQuene, newPoint, greaterQu):
                        yield p
        
        while len(greaterQu) > 0:

            quPoint = greaterQu.popleft()

            yield quPoint 
            circularPointQuene.append(quPoint)

    def getValue(p, prevDP):

        if p in prevDP:
            cur = prevDP[p]
            return cur[0], cur[1]

        return  0, emptyPoint

    def getPossibleValue(point, itemValue, itemDims,  dp):

        if point in dp:
            cur = prevDP[point]
            return cur[0] + itemValue, cur[1] + itemDims

        if point < emptyPoint:
            return None, emptyPoint
        
        return itemValue, itemDims

    def setValue(curDP, p, curVal, curDimensions, O):
        curDP[p] = (curVal, curDimensions)               
        O[0] += 1

    def backTraceItems(DP, resultI, resultP, items, values, n, O):
        res = DP[resultI][resultP][0]
        optItems, optValues = [], []
        point = resultP
        opt = emptyPoint

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

                optItems.append(item.dimensions)
                optValues.append(itemValue)

                res   -= itemValue
                point -= item
                opt   += item

        O[0] *= n

        return opt.dimensions, optItems, optValues

    def createDP(count):
        DP    = [None] * (count + 1)
        DP[0] = defaultdict()
        return DP
       
    def solveSuperIncreasing(size, items, values, count, desc, O):

        def indexLargestLessThanDesc(items, item, lo, hi, O):   

            if item == emptyPoint:
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

            if item == emptyPoint:
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
       
        binSearch = indexLargestLessThanDesc if desc else indexLargestLessThanAsc

        starting = 1
        resultItems = []
        resultValues = []
        resultSum = emptyPoint
        index = binSearch(items, size, starting - 1, count - 1, O)

        while index is not None:
            item = items[index]
            value = values[index]
            resultItems.append(item)
            resultValues.append(value)
            resultSum += item
            if desc:
                index = binSearch(items, size - resultSum, index + 1, count - 1, O)
            else:
                index = binSearch(items, size - resultSum, starting - 1, index - 1, O)
            O[0] += 1

        if verbose:
            print(f"Superincreasing solver called for size {size} and count {count}.  desc={desc}")
        
        return resultSum.dimensions, resultItems, resultValues
   
    def getLimits(size, i, items, partialSums, superIncreasingItems, allDesc):

        partSumForItem = partialSums[i - 1]
        superIncreasingItem = superIncreasingItems[i - 1]

        newPointLimit = size - partSumForItem if partSumForItem else None
        oldPointLimit = newPointLimit

        if doSolveSuperInc and superIncreasingItem:
            oldPointLimit = size - items[i - 2] if allDesc else newPointLimit - items[i] if i < len(items) else newPointLimit

        return partSumForItem, oldPointLimit, newPointLimit  

    count, lessSizeItems, lessSizeValues, itemSum, lessCountSum, partialSums, superIncreasing, superIncreasingItems, allDesc = prepare(constraints, items, values, O)

    cornerCasesCheck = checkCornerCases(constraints, lessSizeItems, lessSizeValues, lessCountSum, itemSum)

    if  cornerCasesCheck:
        return cornerCasesCheck

    if doSolveSuperInc and superIncreasing:
        return solveSuperIncreasing(constraints, lessSizeItems, lessSizeValues, count, allDesc, O)

    DP = createDP(count)

    resultI, resultP = 1, emptyPoint

    circularPointQuene = deque()

    maxValue, prevPointCount, newPointCount = -sys.maxsize, 0, 0

    halfConstraint = constraints.divideBy(2)

    for i in range(1, count + 1):

        DP[i] = defaultdict()

        itemValue, item   = lessSizeValues[i - 1], lessSizeItems[i - 1]
        prevDP,    curDP  = DP[i - 1], DP[i]

        if printPct and i > 1:
            print(f"| {i} | {prevPointCount} | {round(O[0])} |")
        
        itemLimit, oldPointLimit, newPointLimit  = getLimits(constraints, i, lessSizeItems, partialSums, superIncreasingItems, allDesc)

        prevPointCount, newPointCount = newPointCount, prevPointCount
        newPointCount = 0

        for p in getPoints(item, constraints, circularPointQuene, halfConstraint, itemLimit, oldPointLimit, newPointLimit, prevPointCount, prevDP):          

            curValue,    curDim   =  getValue(p,        prevDP) 
            posblValue,  posblDim =  getPossibleValue(p - item, itemValue, item, prevDP) 

            if  posblValue and curValue <= posblValue and posblDim <= constraints:
                curValue = posblValue
                curDim   = posblDim
               
            setValue(curDP, p, curValue, curDim, O)

            if  maxValue <= curValue:
                resultP = p
                resultI = i
                maxValue = curValue
            
            newPointCount += 1

    return backTraceItems(DP, resultI, resultP, lessSizeItems, lessSizeValues, constraints.getSize(), O) 

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
    # add items to possible pareto optimal sets one by one, but merge by only keeping the optimal points
    for item in items:
        O[0] += 1
        # filter out item combinations that lie above the weight limit
        content_next = [point + item for point in content]
        content = merge(content, content_next, weight_limit, O)

        if printPct and i > 1:
            print(f"| {len(content_next)} | {round(O[0])} |")
        i += 1

    best_combination_below_limit = content[find_max_or_equal_below(content, weight_limit, O)]
    #print(f"Best set: {best_combination_below_limit}")
    return best_combination_below_limit.item_ids

dtNow = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
random.seed(dtNow)
randomTestCount = 20

if verbose:
    print(f"Initial random seed is {dtNow}")

script_dir = os.path.dirname(__file__) # <-- absolute dir the script is in

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

    opt, optWeights, optValues2 = knapsack(s, A, A, O)
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


        nLogN = len(A) * math.log2(len(A))

        for s in range(sum(A)):

            doSolveSuperInc = False 

            opt1, expected = subsKnapsack(s, A, O)  

            doSolveSuperInc = True

            O[0] = 0
            opt2, optValues1 = subsKnapsack(s, A, O) 

            assert listValuesEqual(optValues1, expected)
            assert O[0] <= 10 * len(A) + nLogN
           
            O[0] = 0
            opt, optItems, optValues2 = knapsack(s, A, A, O)  
            assert  listValuesEqual(optValues2, expected)
            assert O[0] <= 10 * len(A) + nLogN 

            
            O[0] = 0
            opt, optItems3, optValues3 = knapsackNd(wPoint((s, s)), [wPoint((a, a)) for a in A], A, O)  
            assert  listValuesEqual(optValues3, expected)
            assert O[0] <= 10 * nLogN
             

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
        opt, decOptItems, decOptValues2 = knapsack(decS, decA, decA, O)  
        assert  listValuesEqual(decOptValues2, expected)
        assert O[0] <=  10 * len(A) + nLogN
        
        O[0] = 0
        opt, decOptItems3, optValues3 = knapsackNd(wPoint((decS, decS)), [wPoint((da, da)) for da in decA], decA, O)  
        assert  listValuesEqual(optValues3, expected)
        assert O[0] <=  10 * nLogN
    
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
                    print(f"s = {s},  reverse = {revers}, index {i}")

                O[0] = 0
                opt1, optValues1 = subsKnapsack(s, testCase, O) 
                assert listValuesEqual(optValues1, expected) or sum(expected) == sum(optValues1)         
                
                O[0] = 0
                opt2, optItems, optValues2 = knapsack(s, testCase, testCase, O)  
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
            opt2, optItems, optValues2 = knapsack(s, testCase, testCase, O)  
            assert  listValuesEqual(optValues2, expected)
            
            t3 = time.perf_counter()

            O[0] = 0
            opt3, optItems3, optValues3 = knapsackNd(wPoint((s, s)), [wPoint((a, a)) for a in testCase], testCase, O)  
            assert  listValuesEqual(optValues3, expected)

            t4 = time.perf_counter()

            print(f"geo: base {base}, size {s}, subs {round(t2 - t1, 4)}, 1-0 {round(t3 - t2, 4)}, 2D {round(t4 - t3, 4)}.")

if True: # NP complete: 2D knapsack matching with classic DP solution results.

    if verbose:
        print("2D knapsack matching with classic DP solution results.")

    def knapsack2d_dp(weightSize, volumeSize, weights, volumes, values):
   
        table = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

        for i in range(len(weights)): 

            thingValue = values[i]
            thingConstraint1 = weights[i]
            thingConstraint2 = volumes[i]

            #rewriting the values from the previous line
            for j in range(weightSize + 1):
                for c in range(volumeSize + 1):
                    table[i + 1][j][c] = table[i][j][c]
                

            for j in range(thingConstraint1, weightSize + 1):
                for k in range(thingConstraint2, volumeSize + 1):
                    table[i + 1][j][k] = max(thingValue + table[i][j - thingConstraint1][k - thingConstraint2], table[i][j][k])

        w1 = table[len(weights)]
        v1 = w1[weightSize]
        vv1 = v1[volumeSize]

        return vv1

    O = [0]

    testCaseW =   [5,  3,   2,  5,  3,  4,  5, 6]
    testCaseV =   [8,  4,  12, 18,  5,  2,  1, 4]
    testCaseVal = [50, 30, 20, 50, 30, 40, 50, 60]

    s_weights, s_volumes, s_values = sortReverese3Both(testCaseW, testCaseV, testCaseVal)
 
    if True:

        for testKnapsackWeight in range(min(testCaseW), sum(testCaseW) - 1):
            for testKnapsackVolume in range(min(testCaseV), sum(testCaseV) - 1):

                dpRes = knapsack2d_dp(testKnapsackWeight, testKnapsackVolume, testCaseW, testCaseV, testCaseVal)

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

    dims = [wPoint((p[0], p[1])) for p in data]
    values = [p[2] for p in data]

    descDims, descValues = sortRevereseBoth(dims, values)
    constr = wPoint((12210, Decimal(12)))

    if verbose:
        print(f"Integer and Decimal mixed multidimensional knapsack problem (MKP) test. N {len(data)}")

    O = [0]

    t1 = time.perf_counter()

    optValue, optItems, optValues = knapsackNd(constr, descDims, descValues, O)

    t2 = time.perf_counter()

    optRez = sum(optValues)

    good = optRez >= genExpectedValue and optValue <= constr.dimensions

    iterMax = 2 ** (len(data))
    iterRez = round(O[0])

    if verbose:
        print(f"MKP time: {round(t2 - t1, 4)}, optimized - genetic expected: {optRez - genExpectedValue}, iter: {iterRez}, iterMax: {iterMax}, dIter: {iterMax - iterRez}")

    assert good

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

    def testSilvano(W, V, R, c):
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

        opt1, optW1, optV1 = knapsack(c, ws, vs, O)
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
        
        fieldnames = ['file', 'case', 'size', 'N', 'iter asc', 'iter desc', 'iter non', 'max iter expected', 'asc time', 'desc time', 'non time', 'best iter', 'best time', 'good']
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()

        testCase = list()
        testExpected = list()
        testKnapsack = 0
        rowToSkip = 0

        #files = ["knapPI_16_20_1000", "knapPI_16_50_1000", "knapPI_16_100_1000"]
        files = ["knapPI_16_20_1000", "knapPI_16_50_1000", "knapPI_16_100_1000", "knapPI_16_200_1000", "knapPI_16_500_1000"]

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

                        rezIterDesc = O[0]

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

                        testCase.reverse()

                        t3 = time.perf_counter()

                        optAsc, optItemsAsc = subsKnapsack(testKnapsack, testCase, O)

                        t4 = time.perf_counter()

                        rezSAsc = sum(optItemsAsc) 

                        ascTime = (round(t4 - t3, 4), "asc")

                        rezIterAsc = O[0]
                        
                        if  rezSAsc < expS or optAsc > testKnapsack:
                            good = False
                            allGood = False
                            if verbose:
                                print(f" ASC rez opt: {optAsc}, test opt: {testKnapsack}, rez values: {rezSAsc}, test values: {expS}", end=" ")
                        
                        if rezIterAsc > maxIter:
                            if verbose:
                                print(f" ASC max iter exceeded: {maxIter} rez iter: {rezIterAsc}", end=" ")
                        
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

                        bestTime = min([descTime, ascTime, nonTime], key=lambda t : t[0])[1]

                        descIterItem = (rezIterDesc, "desc")
                        ascIterItem  = (rezIterAsc, "asc")
                        nonIterItem  = (rezIterNon, "non")

                        bestIter = min([descIterItem, ascIterItem, nonIterItem], key=lambda t : t[0])[1]

                        if verbose:
                            print(f" DESC {descTime[0]} ASC {ascTime[0]} NON {nonTime[0]} ")
        
                        writer.writerow({'file': str(f), 'case': str(caseNumber), 'size': str(testKnapsack), 'iter asc':  str(rezIterAsc), 'iter desc':  str(rezIterDesc), 'iter non':  str(rezIterNon), 'max iter expected': str(maxIter), 'N': str(len(testCase)), 'asc time': str(ascTime[0]),  'desc time': str(descTime[0]),  'non time': str(nonTime[0]), 'best iter': bestIter, 'best time': bestTime, 'good': str(good)})

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
        
        fieldnames = ['file', 'case', 'size', 'iter asc', 'iter desc', 'iter non',  'max iter expected', 'N', 'asc time', 'desc time', 'non time', 'best iter', 'best time', 'good']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()

        testCaseW = list()
        testCaseV = list()
        testExpected = list()
        testKnapsack = 0
        rowToSkip = 0

        #files = ["knapPI_11_20_1000", "knapPI_11_50_1000"]
        files = ["knapPI_11_20_1000", "knapPI_11_50_1000", "knapPI_11_100_1000", "knapPI_11_200_1000"]

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

                        opt1Desc, optWeights1, optValues1 = knapsack(testKnapsack, w, v, O)

                        t2 = time.perf_counter()

                        descTime = (round(t2 - t1, 4), "desc")

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

                        if rezSDesc2d < expS or opt2dDesc > nTestKnapsack.dimensions:
                            good = False

                            if verbose:
                                print(f"{caseNumber}  DESC 2D rez opt: {opt2dDesc}, test size: {testKnapsack}, rez values: {rezSDesc2d},  test values: {expS}", end=" ")

                            assert False
                        
                        O = [0]

                        ascW = list(reversed(w))
                        ascV = list(reversed(v))

                        t1 = time.perf_counter()

                        nTestKnapsack = wPoint((testKnapsack, testKnapsack))

                        opt2dAsc, optWeights2dAsc, optValues2dAsc = knapsackNd(nTestKnapsack, [wPoint((a, a)) for a in ascW], ascV, O)

                        t2 = time.perf_counter()

                        rezIter2DAsc = O[0]

                        asc2dTime = (round(t2 - t1, 4), "asc")
                        rezSAsc2d = sum(optValues2dAsc) 

                        if rezSAsc2d < expS or opt2dAsc > nTestKnapsack.dimensions:
                            good = False

                            if verbose:
                                print(f"{caseNumber}  ASC 2D rez opt: {rezSAsc2d}, test size: {testKnapsack}, rez values: {rezSDesc2d},  test values: {expS}", end=" ")

                            assert False

                        O = [0]

                        nonW, nonV = shuffleBoth(w, v)
                        t1 = time.perf_counter()

                        nTestKnapsack = wPoint((testKnapsack, testKnapsack))

                        opt2dNon, optWeights2dNon, optValues2dNon = knapsackNd(nTestKnapsack, [wPoint((a, a)) for a in nonW], nonV, O)

                        t2 = time.perf_counter()

                        rezIter2Dnon = O[0]

                        non2dTime = (round(t2 - t1, 4), "non")
                        nonSAsc2d = sum(optValues2dNon) 

                        if nonSAsc2d < expS or opt2dNon > nTestKnapsack.dimensions:
                            good = False

                            if verbose:
                                print(f"{caseNumber}  ASC 2D rez opt: {nonSAsc2d}, test size: {testKnapsack}, rez values: {nonSAsc2d},  test values: {expS}", end=" ")

                            assert False
                        
                        O = [0]

                        t5 = time.perf_counter()

                        ascW = list(reversed(w))
                        ascV = list(reversed(v))

                        opt1Asc, optWeightsAsc, optValuesAsc = knapsack(testKnapsack, ascW, ascV, O)

                        t6 = time.perf_counter()

                        ascTime = (round(t6 - t5, 4), "asc")

                        rezIterAsc = O[0]

                        rezSAsc = sum(optValuesAsc) 
                        rezWSAsc = sum(optWeightsAsc) 

                        if rezSAsc < expS or rezWSAsc > testKnapsack:
                            good = False

                            if verbose:
                                print(f"{caseNumber} ASC rez opt: {rezSAsc}, test size: {testKnapsack}, rez weights: {rezWSAsc},  test values: {expS}", end=" ")

                            assert False

                        O = [0]

                        t7 = time.perf_counter()

                        nonW, nonV = shuffleBoth(w, v)

                        opt1Non, optWeightsNon, optValuesNon = knapsack(testKnapsack, nonW, nonV, O)

                        t8 = time.perf_counter()

                        nonTime = (round(t8 - t7, 4), "non")

                        if verbose:
                            print(f" INT DESC {descTime[0]} ASC {ascTime[0]} NON {nonTime[0]} DESC 2D {desc2dTime[0]} ASC 2D {asc2dTime[0]} NON 2D {non2dTime[0]}")

                        rezIterAsc = O[0]

                        rezSNon = sum(optValuesNon) 
                        rezWSNon = sum(optWeightsNon) 

                        if rezSNon < expS or rezWSNon > testKnapsack:
                            good = False

                            if verbose:
                                print(f"{caseNumber} ASC rez opt: {opt1Non}, test size: {testKnapsack}, rez weights: {rezWSNon},  test values: {expS}", end=" ")

                            assert False

                        rezIterNon = O[0]

                        bestTime = min([descTime, ascTime, nonTime], key=lambda t : t[0])[1]

                        descIterItem = (rezIterDesc, "desc")
                        ascIterItem  = (rezIterAsc, "asc")
                        nonIterItem  = (rezIterNon, "non")

                        bestIter = min([descIterItem, ascIterItem, nonIterItem], key=lambda t : t[0])[1] 
                    
                        #fieldnames = ['file', 'case', 'size', 'iter asc', 'iter desc', 'iter non',  'max iter', 'N', 'asc time', 'desc time', 'non time', 'best iter', 'best time', 'good']
        
                        writer.writerow({'file': str(f), 'case': str(caseNumber), 'size': str(testKnapsack), 'iter asc':  str(rezIterAsc), 'iter desc':  str(rezIterDesc), 'iter non':  str(rezIterNon), 'max iter expected': str(maxIter), 'N': str(len(testCaseW)), 'asc time': str(ascTime[0]),  'desc time': str(descTime[0]),  'non time': str(nonTime[0]), 'best iter': bestIter, 'best time': bestTime, 'good': str(good)})

                        decimalW = list(w)

                        DecimalArray(decimalW)

                        testKnapsackDecimal = DecimalData(testKnapsack)      

                        O = [0]

                        t1 = time.perf_counter()

                        optDec, optWeightsDec, optValuesDec = knapsack(testKnapsackDecimal, decimalW, v, O)

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
        #maxIntPart = [20, 50, 100, 200, 300, 500]
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

printPct = True

if False: # Polynominal: subsKnapsack report for [1] * 50
    numbers = [1] * 50

    if verbose:
        print(f"len {len(numbers)} sum {sum(numbers)}")

    if True:

        with open(script_dir + '\knapsack.paretoKnapsack.1.csv', 'w', newline='') as csvfile:
            
            O = [0]

            fieldnames = ['size', 'iter', 'delta', 'pareto iter', 'pareto delta']
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()

            prevO = 0
            prevPareto = 0

            if True:

                s = sum(numbers) - 1

                O[0] = 0

                t1 = time.perf_counter()

                opt, optItems1 = subsKnapsack(s, numbers, O)

                subsTime = time.perf_counter() - t1

                print(s)

                o1 = round(O[0])
                
                O[0] = 0

                ids = paretoKnapsack(numbers, numbers, s, O)

                o2 = round(O[0])

                optItems2 = [numbers[id] for id in ids]
                opt2 = sum(optItems2)

                if opt != opt2:
                    print(f"{opt} - {opt2} size {s}")

                writer.writerow({'size': str(s), 'iter':  str(round(o1)), 'delta': str(round(o1 - prevO)), 'pareto iter':  str(round(o2)), 'pareto delta': str(round(o2 - prevPareto))})

                prevO = o1
                prevPareto = o2

if False: # Polynominal: subsKnapsack report for ([1] * 25) + ([2] * 25)
    numbers = ([1] * 25) + ([2] * 25)

    if verbose:
        print(f"len {len(numbers)} sum {sum(numbers)}")

    if True:

        with open(script_dir + '\knapsack.paretoKnapsack.1and2.csv', 'w', newline='') as csvfile:
            
            O = [0]

            fieldnames = ['size', 'iter', 'delta', 'pareto iter', 'pareto delta']
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()

            prevO = 0
            prevPareto = 0

            if True:

                s = sum(numbers) - 1

                O[0] = 0

                opt, optItems1 = subsKnapsack(s, numbers, O)

                print(s)

                o1 = round(O[0])
                
                O[0] = 0

                ids = paretoKnapsack(numbers, numbers, s, O)

                o2 = round(O[0])

                optItems2 = [numbers[id] for id in ids]
                opt2 = sum(optItems2)

                if opt != opt2:
                    print(f"{opt} - {opt2} size {s}")

                writer.writerow({'size': str(s), 'iter':  str(round(o1)), 'delta': str(round(o1 - prevO)), 'pareto iter':  str(round(o2)), 'pareto delta': str(round(o2 - prevPareto))})

                prevO = o1
                prevPareto = o2

if False: # Polynominal: subsKnapsack report for list(range(1, 51))
    numbers = list(range(1, 51))

    if verbose:
        print(f"len {len(numbers)} sum {sum(numbers)}")

    if True:

        with open(script_dir + '\knapsack.paretoKnapsack.upTo100.csv', 'w', newline='') as csvfile:
            
            O = [0]

            fieldnames = ['size', 'iter', 'delta', 'pareto iter', 'pareto delta']
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()

            prevO = 0
            prevPareto = 0

            if True:

                s = sum(numbers) - 1

                O[0] = 0

                opt, optItems1 = subsKnapsack(s, numbers, O)

                print(s)

                o1 = round(O[0])
                
                O[0] = 0

                ids = paretoKnapsack(numbers, numbers, s, O)

                o2 = round(O[0])

                optItems2 = [numbers[id] for id in ids]
                opt2 = sum(optItems2)

                if opt != opt2:
                    print(f"{opt} - {opt2} size {s}")

                writer.writerow({'size': str(s), 'iter':  str(round(o1)), 'delta': str(round(o1 - prevO)), 'pareto iter':  str(round(o2)), 'pareto delta': str(round(o2 - prevPareto))})

                prevO = o1
                prevPareto = o2

if False: # Polynominal: subsKnapsack report for random.sample(range(1, 1000), 50)
    numbers = random.sample(range(1, 1000), 50)
    numbers.sort()

    if verbose:
       print(f"len {len(numbers)} sum {sum(numbers)}")

    if True:

        with open(script_dir + '\knapsack.paretoKnapsack.rand50.csv', 'w', newline='') as csvfile:
            
            O = [0]

            fieldnames = ['size', 'iter', 'delta', 'pareto iter', 'pareto delta']
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()

            prevO = 0
            prevPareto = 0

            if True:

                s = sum(numbers) - 1

                O[0] = 0

                opt, optItems1 = subsKnapsack(s, numbers, O)

                print(s)

                o1 = round(O[0])
                
                O[0] = 0

                ids = paretoKnapsack(numbers, numbers, s, O)

                o2 = round(O[0])

                optItems2 = [numbers[id] for id in ids]
                opt2 = sum(optItems2)

                if opt != opt2:
                    print(f"{opt} - {opt2} size {s}")

                writer.writerow({'size': str(s), 'iter':  str(round(o1)), 'delta': str(round(o1 - prevO)), 'pareto iter':  str(round(o2)), 'pareto delta': str(round(o2 - prevPareto))})

                prevO = o1
                prevPareto = o2

if False: # Polynominal: subsKnapsack report for random.sample(range(1, 10000000000000000), 15)
    numbers = random.sample(range(1, 10000000000000000), 15)
    numbers.sort(reverse=False)
   
    if verbose:
        print(f"len {len(numbers)} sum {sum(numbers)}")

    if True:

        with open(script_dir + '\knapsack.paretoKnapsack.rand1.from1upto10000000000000000.csv', 'w', newline='') as csvfile:
            
            O = [0]

            fieldnames = ['size', 'iter', 'delta', 'pareto iter', 'pareto delta']
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()

            prevO = 0
            prevPareto = 0

            if True:

                s = sum(numbers) - 1

                O[0] = 0

                opt, optItems1 = subsKnapsack(s, numbers, O)

                print(s)

                o1 = round(O[0])
                
                O[0] = 0

                ids = paretoKnapsack(numbers, numbers, s, O)

                o2 = round(O[0])

                optItems2 = [numbers[id] for id in ids]
                opt2 = sum(optItems2)

                if opt != opt2:
                    print(f"{opt} - {opt2} size {s}")

                writer.writerow({'size': str(s), 'iter':  str(round(o1)), 'delta': str(round(o1 - prevO)), 'pareto iter':  str(round(o2)), 'pareto delta': str(round(o2 - prevPareto))})

                prevO = o1
                prevPareto = o2

if False: # Polynominal: subsKnapsack report for geometric progression numbers = [1] * 25; numbers[i] *= (int(numbers[i - 1] * 2) - 1)
    numbers = [10000] * 15

    for i in range(1, 15):
        numbers[i] = (int(numbers[i - 1] * 2) - 1)

    numbers.append(numbers[len(numbers) // 2])

    numbers.sort(reverse=False)
   
    if verbose:
        print("len " + str(len(numbers)))
        print("sum " + str(sum(numbers)))        

    if True:

        with open(script_dir + '\knapsack.paretoKnapsack.worstCase.csv', 'w', newline='') as csvfile:
            
            O = [0]

            fieldnames = ['size', 'iter', 'delta', 'pareto iter', 'pareto delta']
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()

            prevO = 0
            prevPareto = 0

            if True:
                s = sum(numbers) - 1

                O[0] = 0

                opt1, optItems1 = subsKnapsack(s, numbers, O)

                doSolveSuperInc = False

                o1 = round(O[0])

                print(o1)
                
                O[0] = 0

                ids = paretoKnapsack(numbers, numbers, s, O)

                o2 = round(O[0])

                optItems2 = [numbers[id] for id in ids]
                opt2 = sum(optItems2)

                writer.writerow({'size': str(s), 'iter':  str(round(o1)), 'delta': str(round(o1 - prevO)), 'pareto iter':  str(round(o2)), 'pareto delta': str(round(o2 - prevPareto))})

                prevO = o1
                prevPareto = o2

if False: # Exponental in ASC case only: subsKnapsack report for factorial numbers = [1] * 25; numbers[i] *= (numbers[i - 1] - 1) 
    numbers = [10000] * 15

    for i in range(1, 15):
        numbers[i] *= (int(numbers[i - 1]) - 1)

    numbers.append(numbers[len(numbers) // 2])

    numbers.sort(reverse=False)
   
    if verbose:
        print("len " + str(len(numbers)))
        print("sum " + str(sum(numbers)))        

    if True:

        with open(script_dir + '\knapsack.paretoKnapsack.worstCase.csv', 'w', newline='') as csvfile:
            
            O = [0]

            fieldnames = ['size', 'iter', 'delta', 'pareto iter', 'pareto delta']
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()

            prevO = 0
            prevPareto = 0

            if True:
                s = sum(numbers) - 1

                O[0] = 0

                opt1, optItems1 = subsKnapsack(s, numbers, O)

                doSolveSuperInc = False

                o1 = round(O[0])

                print(o1)
                
                O[0] = 0

                ids = paretoKnapsack(numbers, numbers, s, O)

                o2 = round(O[0])

                optItems2 = [numbers[id] for id in ids]
                opt2 = sum(optItems2)

                writer.writerow({'size': str(s), 'iter':  str(round(o1)), 'delta': str(round(o1 - prevO)), 'pareto iter':  str(round(o2)), 'pareto delta': str(round(o2 - prevPareto))})

                prevO = o1
                prevPareto = o2
