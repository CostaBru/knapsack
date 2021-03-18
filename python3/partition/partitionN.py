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
import random
import sys
from collections import defaultdict
from decimal import Decimal

from knapsack.knapsackNd import knapsackNSolver
from knapsack.paretoKnapsack import knapsackParetoSolver
from knapsack.paretoPoint import paretoPoint0, paretoPoint2
from knapsack.subsKnapsack import subsetSumKnapsackSolver
from knapsack.wPoint import wPoint1, wPoint2


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


class partitionSolver:

    def __init__(self, items, sizesOrPartitions, groupSize, iterCounter, optimizationLimit) -> None:
        self.items = items
        self.sizesOrPartitions = sizesOrPartitions
        self.groupSize = groupSize
        self.iterCounter = iterCounter
        self.useHybridParetoGrouping = True
        self.optimizationLimit = optimizationLimit
        self.printInfo = False
        self.printOptimizationInfo = False

    def prepareGrouping(self, A, iterCounter):

        group = defaultdict(list)

        for c in A:
            group[c].append(c)
       
        iterCounter[0] += len(A)

        return group
   
    def groupItems(self, group, iterCounter):

        allUnique = True
        nonUniqueList = defaultdict(int)

        for k in group.keys():        

            nonUniqueList[k] += len(group[k])
           
            if len(group[k]) > 1:
                allUnique = False

        iterCounter[0] += len(group)

        return allUnique, nonUniqueList


    def getSingleDuplicatePartitions(self, items, count, sizes, groupSize, iterCounter):

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

    def optimizePartitions(self, quotients, remainder, sizes, groupSize, optimizationLimit, iterCounter):

        def mergeTwoSorted(itemSet1, itemSet2):

            result = []

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
                    if val1 < val2:
                        result.append(val1)
                        moveL1 = True
                        moveL2 = False                        
                    elif val2 < val1:
                        result.append(val2) 
                        moveL1 = False
                        moveL2 = True                            
                    else:
                        result.append(val1)
                        result.append(val2)
                        moveL1 = True
                        moveL2 = True
                elif n1 and not n2:
                    result.append(val1)
                    moveL1 = True
                    moveL2 = False
                elif n2 and not n1:
                    result.append(val2) 
                    moveL1 = False
                    moveL2 = True  
            return result

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
               
                resultIndexes.update(item.Indexes)

                resultSizes += item.Sizes

                resultSet = mergeTwoSorted(self.Items, item.Items)

                return partitionPoint(resultSet, resultSizes, resultIndexes)        
           
            def __eq__(self, other):
                return self.Items == other.Items and self.Sizes == other.Sizes

            def __hash__(self):
                return hash(self.Items)

        def optimize(p, remainderItem, groupSize, limit, iterCounter):

            newSet = []
            newSizes = []
           
            if limit <= 2:
                newSet   += mergeTwoSorted(remainderItem.Items, p.Items)
                newSizes += remainderItem.Sizes
                newSizes += p.Sizes

                iterCounter[0] += len(p.Items) + len(remainderItem.Items)
                iterCounter[0] += len(p.Sizes) + len(remainderItem.Sizes)

            elif limit == 3:
                newSet += remainderItem.Items
                newSizes += remainderItem.Sizes

                random.shuffle(newSet)
                random.shuffle(newSizes)

                for s in reversed(p.Sizes):
                    newSizes.append(s)
               
                for r in reversed(p.Items):
                    newSet.append(r)

                iterCounter[0] += len(p.Items) + len(remainderItem.Items)
                iterCounter[0] += len(p.Sizes) + len(remainderItem.Sizes)
            else:
                newSizes += p.Sizes
                newSizes += remainderItem.Sizes
               
                newSet += p.Items
                newSet += remainderItem.Items
               
                random.shuffle(newSet)
                random.shuffle(newSizes)

                iterCounter[0] += (len(p.Items) + len(remainderItem.Items)) * 2
                iterCounter[0] += (len(p.Sizes) + len(remainderItem.Sizes)) * 2

            return  self.divideSet(newSet, newSizes, groupSize, iterCounter)

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

        def incOForPoint(iterCounter, p):
            iterCounter[0] += 1
            iterCounter[0] += len(p.Items)
            iterCounter[0] += len(p.Sizes)
            iterCounter[0] += len(p.Indexes)

        def backTrace(optimizationsMade, remainderItem, originalQuotient, originalRemainder, optimizationCount, iterCounter):

            if len(optimizationsMade) == 0:
                return originalQuotient, originalRemainder, optimizationCount

            bestPartition = list()
            skipIndexes = set()

            for optPoint in optimizationsMade:
                skipIndexes.update(optPoint.Indexes)
                iterCounter[0] += 2 * len(optPoint.Items)
                bestPartition.append(partitionItem(list(reversed(optPoint.Items)), optPoint.Sizes))
                incOForPoint(iterCounter, optPoint)

            optimizationCount += len(optimizationsMade)
           
            for i in range(len(originalQuotient)):
                if i in skipIndexes:
                    continue
                it = originalQuotient[i]
                bestPartition.append(it)
                iterCounter[0] += 1

            return bestPartition, remainderItem, optimizationCount

        def incOForPartition(iterCounter, optItem):
            iterCounter[0] += 1
            iterCounter[0] += len(optItem.Items)
            iterCounter[0] += len(optItem.Sizes)

        def prepareQuotientsAndRemainder(quotients, groupSize, remainder, limit, iterCounter):

            if limit == 0:

                remainder.Items.sort()

                iterCounter[0] += len(remainder.Items) * math.log2(len(remainder.Items))
                iterCounter[0] += 1

                for q in quotients:
                    q.Items.sort()

                    iterCounter[0] += len( q.Items) * math.log2(len(q.Items))
                    iterCounter[0] += 1

            elif limit > 2:
                random.shuffle(quotients)
                random.shuffle(remainder.Items)

                iterCounter[0] += len(quotients)
                iterCounter[0] += len(remainder.Items)
            else:
                random.shuffle(quotients)
                random.shuffle(remainder.Items)

                iterCounter[0] += len(quotients)
                iterCounter[0] += len(remainder.Items)
           
        prepareQuotientsAndRemainder(quotients, groupSize, remainder,  0, iterCounter)

        remainderItem = remainder

        startLayer = 1
        endLayer = startLayer + (len(sizes) // 2)

        if optimizationLimit > 0:
            endLayer = optimizationLimit

        optimizationCount = 0

        for limit in range(startLayer, endLayer):
           
            optimizedIndexes,  uniqueSet = set(), set()
            optimizationsMade, newPoints = [], []

            remainderItem = remainder
            minReminderLen = len(remainderItem)

            if self.printOptimizationInfo:
                print(f"performing optimizations at the same time is limited by: {limit}; quotients: {len(quotients)} reminder len {len(remainder)}")

            for i in range(len(quotients)):

                item = quotients[i]

                uniqueSet.update(newPoints)
                newPoints.clear()

                for p in getPoints(i, item, uniqueSet, limit):          

                    if len(optimizedIndexes) > 0 and not p.Indexes.isdisjoint(optimizedIndexes):
                        continue

                    optQuotient, optReminder, _ = optimize(p, remainderItem, groupSize, limit, iterCounter)

                    incOForPoint(iterCounter, p)

                    if  len(optReminder) < minReminderLen or len(optReminder.Sizes) < len(remainderItem.Sizes):
                       
                        for optItem in optQuotient:
                            optimizationsMade.append(partitionPoint(optItem.Items, optItem.Sizes, p.Indexes))
                            optimizedIndexes.update(p.Indexes)
                            incOForPartition(iterCounter, optItem)
                       
                        remainderItem = optReminder
                        minReminderLen = len(remainderItem)

                        if len(optReminder.Sizes) == 0:
                            return backTrace(optimizationsMade, remainderItem, quotients, remainder, optimizationCount, iterCounter)
                    else:
                        newPoints.append(p)

                    if  minReminderLen == 0:
                        return backTrace(optimizationsMade, remainderItem, quotients, remainder, optimizationCount, iterCounter)

            if len(optimizedIndexes) > 0:
                quotients, remainder, optimizations = backTrace(optimizationsMade, remainderItem, quotients, remainder, optimizationCount, iterCounter)
                optimizationCount += optimizations
           
            prepareQuotientsAndRemainder(quotients, groupSize, remainder, limit, iterCounter)
               
        return  quotients, remainder, optimizationCount


    def sortDuplicatesForPartitioning(self, group, count, nonUniqueList, iterCounter):
        A_sort = []

        keys = list(group.keys())
        keysCount = len(keys)
        iterCounter[0] += keysCount

        keys.sort()
        iterCounter[0] += keysCount * math.log2(keysCount)

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
               
        iterCounter[0] += count

        return A_sort

    def partitionOverSameCountDuplicates(self, nonUniqueList, sizes, groupSize, optimizationLimit, iterCounter):

        sameCount = True

        cnt = next(iter(nonUniqueList.values()))

        for k in nonUniqueList.keys():
            if nonUniqueList[k] != cnt:
                sameCount = False
                iterCounter[0] += 1
                break

        if sameCount:

            nonUKeys = list(nonUniqueList.keys())
            newLen = len(nonUKeys)
            iterCounter[0] += newLen

            nonUKeys.sort(reverse=True)
            iterCounter[0] += newLen * math.log2(newLen)

            s = sum(nonUKeys)
            n = len(sizes)

            newN = n // cnt

            if isinstance(s, int):
                size = sum(nonUKeys) // newN
                newSizes = [size] * newN
            else:
                size = Decimal(Decimal(s) / Decimal(Decimal(n) / Decimal(cnt)))
                newSizes = [size] * newN

            iterCounter[0] += newLen
           
            quotients, remainder, optCount = self.divideSet(nonUKeys, newSizes, groupSize, iterCounter)

            quotientResult, remainderResult  = [], []

            for i in range(cnt):
                for item in quotients:
                    quotientResult.append(item.Items)
                for rem in remainder.Items:
                    remainderResult.append(rem)

            if  len(remainderResult) == 0 or len(quotientResult) == len(sizes) or len(quotients) == 0:
                return quotientResult, remainderResult, optCount

            return self.optimizePartitions(remainderResult, quotientResult, sizes, groupSize, optimizationLimit, iterCounter)

        return None

    def paretoGroupingOperator(self, size, reminderItems, forceUseLimits, iterCounter):
        paretoItems = [wPoint1(item) for item in reminderItems]
   
        solver = knapsackParetoSolver(paretoItems, reminderItems, range(0, len(reminderItems)), wPoint1(size), paretoPoint0(0), wPoint1(0), iterCounter)
   
        solver.printInfo = self.printInfo
        solver.forceUseLimits = forceUseLimits
        solver.forceUsePareto = False
        solver.subsetSum = True
   
        bestValue, bestSize, bestItems, bestValues, bestIndexes = solver.solve()

        return  bestValue, bestValues
   
    def dpGroupingOperator(self, size, reminderItems, forceUseLimits, iterCounter):
   
        solver = subsetSumKnapsackSolver(size, reminderItems, iterCounter)
   
        solver.printInfo = self.printInfo
        solver.forceUseLimits = forceUseLimits
        bestValue, bestItems = solver.solve()

        return  bestValue, bestItems

    def paretoGrouping2dOperator(self, size, reminderItems, groupSize, forceUseLimits, iterCounter):
        paretoItems, constraints = [wPoint2(item, 1) for item in reminderItems], wPoint2(size, groupSize)
        iterCounter[0] += len(reminderItems)

        solver = knapsackParetoSolver(paretoItems, reminderItems, range(0, len(reminderItems)), constraints, paretoPoint2(0, 0, 0), wPoint2(0, 0), iterCounter)
   
        solver.printInfo = self.printInfo
        solver.forceUseLimits = forceUseLimits
        solver.forceUsePareto = False
        solver.canBackTraceWhenSizeReached = True
   
        _, bestSize, __, bestValues, ___ = solver.solve()

        return  bestSize, bestValues
   
    def dpGrouping2dOperator(self, size, reminderItems, groupSize, forceUseLimits, iterCounter):
   
        dimensions, constraints  = [wPoint2(item, 1) for item in reminderItems], wPoint2(size, groupSize)
        iterCounter[0] += len(reminderItems)

        solver = knapsackNSolver(constraints, dimensions, reminderItems, iterCounter, wPoint2(0, 0), forceUseLimits)
   
        solver.printInfo = self.printInfo
        solver.printDpInfo =  self.printInfo
        solver.forceUseLimits = forceUseLimits
        solver.canBackTraceWhenSizeReached = True
   
        _, optDims, __, optValues =  solver.solve()

        return  optDims, optValues

    def divideSet(self, items, sizes, groupSize, iterCounter, forceUseLimits = False):

        quotients = []
        reminderSizes = []
        reminderItems = items

        subsDivider       = self.paretoGroupingOperator   if self.useHybridParetoGrouping else self.dpGroupingOperator
        knapsack2dDivider = self.paretoGrouping2dOperator if self.useHybridParetoGrouping else self.dpGrouping2dOperator

        ls = len(sizes)

        for n in range(ls, 0, -1):

            size = sizes[n - 1]

            if groupSize > 0:

                if n == 1:

                    iterCounter[0] += len(reminderItems)

                    remSum = sum(reminderItems)

                    if remSum == size and len(reminderItems) == groupSize:
                        quotients.append(partitionItem(list(reminderItems), [size]))
                        reminderItems.clear()
                        break  
                    elif remSum < size:
                        reminderSizes.append(size)
                        break  

                optDims, optValues = knapsack2dDivider(size, reminderItems, groupSize, forceUseLimits, iterCounter)

                if optDims.getDimension(0) == size and optDims.getDimension(1) == groupSize:

                    quotients.append(partitionItem(optValues, [size]))

                    for toRemove in optValues:
                        reminderItems.remove(toRemove)

                    iterCounter[0] += len(optValues)
                else:
                    reminderSizes.append(size)
            else:

                if n == 1:

                    iterCounter[0] += len(reminderItems)

                    remSum = sum(reminderItems)

                    if remSum == size:
                        quotients.append(partitionItem(list(reminderItems), [size]))
                        reminderItems.clear()
                        break  
                    elif remSum < size:
                        reminderSizes.append(size)
                        break

                optimal, optimalList = subsDivider(size, reminderItems, forceUseLimits, iterCounter)

                if optimal == size:          

                    quotients.append(partitionItem(optimalList, [size]))

                    for toRemove in optimalList:
                        reminderItems.remove(toRemove)  

                    iterCounter[0] += len(optimalList)
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

        items, sizesOrPartitions, groupSize, iterCounter, optimizationLimit = self.items, self.sizesOrPartitions, self.groupSize, self.iterCounter, self.optimizationLimit

        count = len(items)
        sizes, sameSizes = self.getSizes(items, sizesOrPartitions)

        if  count < len(sizes):
            return [], [], 0
       
        group = self.prepareGrouping(items, iterCounter)
        allUnique, nonUniqueList = self.groupItems(group, iterCounter)

        if len(nonUniqueList) == 1:
            return self.getSingleDuplicatePartitions(items, count, sizes, groupSize, iterCounter)

        quotients, remainder, optCount = [], [], 0

        if  allUnique:

            items = list(items)
            items.sort()

            iterCounter[0] += count * math.log2(count)
            iterCounter[0] += count

            quotients, remainder, optCount = self.divideSet(items, sizes, groupSize, iterCounter)
        else:
            if  len(nonUniqueList) > len(sizes) and groupSize == 0 and sameSizes:
                partResult = self.partitionOverSameCountDuplicates(nonUniqueList, sizes, 0, optimizationLimit, iterCounter)
                if partResult:
                    return partResult

            sortedDuplicates = self.sortDuplicatesForPartitioning(group, count, nonUniqueList, iterCounter)
            quotients, remainder, optCount = self.divideSet(sortedDuplicates, sizes, groupSize, iterCounter, forceUseLimits=True)
   
        if  len(remainder) == 0 or len(quotients) == len(sizes) or len(quotients) == 0:
            return quotients, remainder, optCount

        return self.optimizePartitions(quotients, remainder, sizes, groupSize, optimizationLimit, iterCounter)
