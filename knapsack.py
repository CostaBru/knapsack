import sys
from collections import defaultdict
from typing import List 
from decimal import Decimal
from collections import deque
import random
import math 
import csv
import os

# Copyright Dec 2020 Konstantin Briukhnov (kooltew at gmail.com) (@CostaBru). San-Francisco Bay Area.

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

def partitionN(items, partitions, groupSize ,O):

    def checkBorderCases(A, n, count, maxElement,  O):

        if n == 1 and maxElement == 1:
            return 1

        if sumOfItems % n != 0:
            return 0

        size = sumOfItems // n

        if maxElement > size:
            return 0

        return None

    def prepareGrouping(A, count, partitions, O):

        maxElement = 0
        sumOfItems = 0

        group = defaultdict(list)

        for c in A:
            sumOfItems += c
            group[c].append(c)        
            if c > maxElement:
                maxElement = c
        
        O[0] += count

        size = sumOfItems // partitions

        return group, maxElement, sumOfItems, size
    
    def groupItems(group, O):

        allUnique = True
        nonUniqueList = defaultdict(int)

        for k in group.keys():        

            nonUniqueList[k] += len(group[k])
            
            if len(group[k]) > 1:
                allUnique = False

        O[0] += len(group)

        return allUnique, nonUniqueList

    def getSingleDuplicatePartitions(nonUniqueList, count, partitions, groupSize, O):

        quotientResult, remainderResult  = [], []
        singleItem = nonUniqueList[0]

        if groupSize == 0:
            if (count % partitions) == 0:
                for i in range(partitions):
                    quotient = [singleItem] * (count // partitions)
                    quotientResult.append(quotient)
            else:
                for i in range(partitions - 1):
                    quotient = [singleItem] * (count // partitions)
                    quotientResult.append(quotient)                
                remainderResult = [singleItem] * (count % partitions)
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

        return  quotientResult, remainderResult  

    def optimizePartitions(quotient, remainder, size, groupSize, partitions):

        class partitionPoint:
            def __init__(self, partintions, itemSet, itemIndexes=None):
                self.partintions = partintions
                self.Items = tuple(itemSet)
                self.Indexes = set()
                if itemIndexes:
                    self.Indexes.update(itemIndexes)       
            
            def __add__(self, item): 

                resultIndexes = set(self.Indexes)
                resultSet = list(self.Items)
                resultPart = self.partintions

                for ni in item.Items:
                    resultSet.append(ni)
                
                for ind in item.Indexes:
                    resultIndexes.add(ind)

                resultPart += item.partintions

                resultSet.sort(reverse=True)

                return partitionPoint(resultPart, resultSet, resultIndexes)        
            
            def __eq__(self, other):
                return self.Items == other.Items

            def __hash__(self):
                return hash(self.Items)

        def optimize(p, optimizeRemainder, groupSize, size, limit, O):

            newSet = list(optimizeRemainder.Items)

            if groupSize > 0 or limit % 2 == 0:
                random.shuffle(newSet)
        
            for r in p.Items:
                newSet.append(r) 
            
            O[0] += len(newSet)

            newPartitions = p.partintions + optimizeRemainder.partintions

            return  divideByPartitions(newSet, newPartitions, size, groupSize, False, O)

        def getPoints(i, item, uniqueSet, limit):

            itemPoint = partitionPoint(1, item)
            itemPoint.Indexes.add(i)

            if itemPoint not in uniqueSet:
                yield itemPoint

            for prevPoint in uniqueSet:
                if prevPoint.partintions + itemPoint.partintions < limit:                
                    newPoint = itemPoint + prevPoint
                    if newPoint not in uniqueSet:
                        yield newPoint

        def backTrace(optimizationsMade, bestRemainder, originalQuotient, originalRemainder, O):

            if len(optimizationsMade) == 0:
                return originalQuotient, originalRemainder

            bestPartition = list()
            skipIndexes = set()

            for optPoint in optimizationsMade:
                skipIndexes.update(optPoint.Indexes)
                bestPartition.append(optPoint.Items)
                O[0] += 1
            
            for i in range(len(originalQuotient)):
                it = originalQuotient[i]
                if i in skipIndexes:
                    continue
                bestPartition.append(it)
                O[0] += 1

            return bestPartition, bestRemainder

        if groupSize == 0:
            quotient.sort(key=lambda x: len(x), reverse = True)
            O[0] += len(quotient) * math.log2(len(quotient))        

        remainderPoint = partitionPoint(partitions - len(quotient), remainder)
        minRemiderLen = len(remainder) 

        startLayer = 1
        endLayer = max(startLayer + 1, partitions)

        for limit in range(startLayer, endLayer):

            #print("layer " + str(limit))

            optimizedIndexes,  uniqueSet = set(), set()
            optimizationsMade, newPoints = [], []

            remainderPoint = partitionPoint(partitions - len(quotient), remainder)
            minRemiderLen = len(remainder) 

            for i in range(len(quotient)):

                item = quotient[i]

                uniqueSet.update(newPoints)
                newPoints.clear()

                for p in getPoints(i, item, uniqueSet, limit):          

                    if len(p.Indexes.intersection(optimizedIndexes)) > 0:
                        continue

                    optQuotient, optReminder = optimize(p, remainderPoint, groupSize, size, limit, O) 

                    O[0] += 1

                    if  len(optReminder) < minRemiderLen:

                        for optItem in optQuotient:
                            optimizationsMade.append(partitionPoint(1, optItem, p.Indexes))
                            optimizedIndexes.update(p.Indexes)
                            O[0] += 1

                        parts = p.partintions + remainderPoint.partintions

                        remainderPoint = partitionPoint(parts - len(optQuotient), optReminder)
                        minRemiderLen = len(optReminder) 
                    else:
                        newPoints.append(p)

                    if  minRemiderLen == 0:
                        return backTrace(optimizationsMade, remainderPoint.Items, quotient, remainder, O)

            if len(optimizedIndexes) > 0:
                quotient, remainder = backTrace(optimizationsMade, remainderPoint.Items, quotient, remainder, O)
                if groupSize == 0:
                    quotient.sort(key=lambda x: len(x), reverse = True)
                    O[0] += len(quotient) * math.log2(len(quotient))
                else:
                    random.shuffle(quotient)
                    O[0] += len(quotient)
                    
        return backTrace(optimizationsMade, remainderPoint.Items, quotient, remainder, O)

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

    def partitionOverSameCountDuplicates(nonUniqueList, n, maxElement, size, groupSize, O):

        sameCount = True

        cnt = nonUniqueList[maxElement]

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

            newN = n // cnt

            size = sum(nonUKeys) // newN
            O[0] += newLen
            
            quotient, remainder = divideByPartitions(nonUKeys, newN, size, groupSize, True, O)

            quotientResult, remainderResult  = [], []

            for i in range(cnt):
                for item in quotient:
                    quotientResult.append(item)
                for rem in remainder:
                    remainderResult.append(rem)

            return quotientResult, remainderResult

        return None

    def divideByPartitions(items, partitions, size, groupSize, descOrder, O):    

        quotient = []

        for n in range(partitions, 0, -1):

            if groupSize > 0:

                dimensions, constrains  = [(item, 1) for item in items], (size, groupSize)

                opt, optDims, optValues = knapsackNd(constrains, dimensions, items, O)

                if  opt[0] == size and opt[1] == groupSize: 

                    quotient.append(optValues)

                    for toRemove in optValues:
                        items.remove(toRemove)

                    O[0] += len(optValues)

                    if n == 2:

                        O[0] += len(items)

                        if sum(items) == size and len(items) == groupSize:
                            quotient.append(list(items)) 
                            items.clear()
                            break
                else:
                    break
            else:

                optimal, optimalList = knapsack1d(size, items,  O, descOrder)

                if  optimal == size:          

                    quotient.append(optimalList)

                    for toRemove in optimalList:
                        items.remove(toRemove)  

                    O[0] += len(optimalList)

                    if n == 2:

                        O[0] += len(items)

                        if sum(items) == size:
                            quotient.append(list(items)) 
                            items.clear()
                            break
                else:
                    break

        return quotient, items

    count = len(items)

    if  count < partitions:
        return [], []
    
    group, maxElement, sumOfItems, size = prepareGrouping(items, count, partitions, O)
    
    borderCaseCheck = checkBorderCases(items, partitions, count, maxElement, O)

    if borderCaseCheck is not None:
        return borderCaseCheck

    allUnique, nonUniqueList = groupItems(group, O)

    if  allUnique:

        items.sort(reverse=True)
        O[0] += count * math.log2(count)
        return divideByPartitions(items, partitions, size, groupSize, True, O)

    elif len(nonUniqueList) == 1:

        return getSingleDuplicatePartitions(nonUniqueList, count, partitions, groupSize, O)

    else:
        if  len(nonUniqueList) > partitions and groupSize == 0:
            partResult = partitionOverSameCountDuplicates(nonUniqueList, partitions, maxElement, size, groupSize, O)
            if partResult:
                return partResult

        sortedDuplicates    = sortDuplicatesForPartitioning(group, count, nonUniqueList, O)
        quotient, remainder = divideByPartitions(sortedDuplicates, partitions, size, groupSize, False, O)
        
        if  len(remainder) == 0:
            return quotient, remainder

        return optimizePartitions(quotient, remainder, size, groupSize, partitions)
   
    return [],[]

def knapsack1d(size, items, O, desc = True):

    def prepare(size, items, desc, O):
        
        count = len(items)
        sum = 0
        lessCountSum = 0    
        partialSum09 = [0] * count
        starting = 1
        i = 0
        for item in items:

            itemWeight = item
            sum += itemWeight

            if desc:
                partialSum09[count - i - 1] = sum
            else:
                partialSum09[count - i - 1] = sys.maxsize

            if itemWeight <= size:
                lessCountSum += itemWeight  
            else:
                starting += 1
            
            i += 1

        O[0] += count
        return count, sum, lessCountSum, partialSum09, starting

    def checkCornerCases(size, items, count, sum, lessCountSum, O):        

        if  lessCountSum == 0:
            return [0,[]]
        
        if  lessCountSum < size:
            
            lessCountItems = []

            for item in items:
                itemWeight = item

                if itemWeight < size:
                    lessCountItems.append(itemWeight)

            O[0] += len(lessCountItems)

            return [lessCountSum, lessCountItems]

        if  sum <= size:
            return [sum, items]  

        return None      
  
    def getPoints(itemWeight, size, circularPointQuene, partSumForItem09, prevCyclePointCount, uniquePointSet):
       
        # merges ordered visited points with new points with keeping order in O(N) using single circular queue. 
        # each getPoints method call starts fetching visited points from qu start, pops visited point and pushes new point and visited to the end of qu in ASC order.
        # we skip new point if it in list already
        # skips points if they will not contribute to optimal solution

        greaterQu = deque()

        useItemItself = partSumForItem09 >= (size // 2)

        limit = size - partSumForItem09

        if useItemItself and not itemWeight in uniquePointSet:
            yield itemWeight
            circularPointQuene.append(itemWeight)

        for i in range(prevCyclePointCount):

            oldPoint = circularPointQuene.popleft()             

            while len(greaterQu) > 0 and greaterQu[0] < oldPoint:

                quPoint = greaterQu.popleft()
               
                yield quPoint 
                circularPointQuene.append(quPoint)

            if oldPoint >= limit:
                yield oldPoint
                circularPointQuene.append(oldPoint)

            newPoint = oldPoint + itemWeight

            if not useItemItself and newPoint < limit:
                continue

            if newPoint <= size and not newPoint in uniquePointSet:   

                peek = circularPointQuene[0]

                if newPoint < peek:                   
                    yield newPoint
                    circularPointQuene.append(newPoint)

                elif newPoint > peek:
                    greaterQu.append(newPoint)
        
        while len(greaterQu) > 0:

            quPoint = greaterQu.popleft()

            yield quPoint 
            circularPointQuene.append(quPoint)    

    def getValue(point, dp):

        if point in dp:
           return dp[point]

        return 0

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

    count, sum, lessCountSum, partialSum09, starting  = prepare(size, items, desc, O)

    cornerCasesCheck = checkCornerCases(size, items, count, sum, lessCountSum, O)

    if  cornerCasesCheck:
        return cornerCasesCheck

    DP = createDP(count, starting)

    resultI, resultP = 1, 1

    circularPointQuene = deque()

    maxValue, prevPointCount, newPointCount = 0, 0, 0

    for i in range(starting, count + 1):

        DP[i] = defaultdict()

        prevPointCount, newPointCount = newPointCount, prevPointCount
        newPointCount = 0

        itemValue, itemWeight = items       [i - 1], items[i - 1]
        partSumForItem09      = partialSum09[i - 1]
        prevDP,    curDP      = DP          [i - 1],    DP[i]

        for p in getPoints(itemWeight, size, circularPointQuene, partSumForItem09, prevPointCount, prevDP):          

            curValue    =  getValue(p,              prevDP)  
            posblValue  =  getValue(p - itemWeight, prevDP) 

            posblValue += itemValue

            if  curValue < posblValue and posblValue <= size:
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

def knapsack2d(size, weights, values, O):

    def prepare(size, weights, O):
        count = len(weights)
        sum = 0
        lessCountSum = 0    
        starting = 1
        for w in weights:

            itemWeight = w
            sum += itemWeight

            if itemWeight <= size:
                lessCountSum += itemWeight
            else:
                starting += 1
            
        O[0] += count

        return count, sum, lessCountSum, starting

    def checkCornerCases(size, weights, values, count, sum, lessCountSum, O):        

        if  lessCountSum == 0:
            return 0,[],[]
        
        if  lessCountSum < size:
            lessCountWeights = []
            lessCountValues = []

            for i in range(0, len(weights)):
                itemWeight = weights[i]
                itemValue = values[i]
                if itemWeight <= size:
                    lessCountWeights.append(itemWeight)                
                    lessCountValues.append(itemValue)                

            O[0] += count                   

            return lessCountSum, lessCountWeights, lessCountValues

        if  sum <= size:
            return sum, weights, values 

        return None      
     
    def getPoints(itemWeight, size, circularPointQuene, prevCyclePointCount, uniquePointSet):
        
        # merges ordered visited points with new points with keeping order in O(N) using single circular queue. 
        # each getPoints method call starts fetching visited points from qu start, pops visited point and pushes new point and visited to the end of qu in ASC order.
        # we skip new point if it in list already

        greaterQu = deque()

        if not itemWeight in uniquePointSet:         
            yield itemWeight
            circularPointQuene.append(itemWeight)

        for i in range(prevCyclePointCount):

            oldPoint = circularPointQuene.popleft()             

            while len(greaterQu) > 0 and greaterQu[0] < oldPoint:

                quPoint = greaterQu.popleft()
               
                yield quPoint 
                circularPointQuene.append(quPoint)

            yield oldPoint
            circularPointQuene.append(oldPoint)

            newPoint = oldPoint + itemWeight

            if newPoint <= size and not newPoint in uniquePointSet:   

                peek = circularPointQuene[0]

                if newPoint < peek:                   
                    yield newPoint
                    circularPointQuene.append(newPoint)

                elif newPoint > peek:
                    greaterQu.append(newPoint)
        
        while len(greaterQu) > 0:

            quPoint = greaterQu.popleft()

            yield quPoint 
            circularPointQuene.append(quPoint)

    def getValue(p, prevDP):

        if p in prevDP:
            cur = prevDP[p]
            return cur[0], cur[1]
      
        return 0, 0
      
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

    def createDP(count, starting):
        DP    = [None] * (count + 1)
        for i in range(starting):
            DP[i] = defaultdict()
        return DP

    count, sum, lessCountSum, starting = prepare(size, weights, O)

    cornerCasesCheck = checkCornerCases(size, weights, values, count, sum, lessCountSum, O)

    if  cornerCasesCheck:
        return cornerCasesCheck

    DP = createDP(count, starting)

    resultI, resultP = 1, 1

    circularPointQuene = deque()

    maxValue, prevPointCount, newPointCount = 0, 0, 0

    for i in range(starting, count + 1):

        DP[i] = defaultdict()

        itemValue, itemWeight   = values[i - 1], weights[i - 1]
        prevDP,    curDP        = DP    [i - 1],      DP[i]

        prevPointCount, newPointCount = newPointCount, prevPointCount
        newPointCount = 0

        for p in getPoints(itemWeight, size, circularPointQuene, prevPointCount, prevDP):          

            curValue,   curWeight   =  getValue(p,              prevDP) 
            posblValue, posblWeight =  getValue(p - itemWeight, prevDP) 

            posblValue  += itemValue
            posblWeight += itemWeight  

            if  curValue < posblValue and posblWeight <= size:
                curValue = posblValue
                curWeight = posblWeight
               
            setValue(curDP, p, curValue, curWeight, O)

            if  maxValue < curValue:
                resultP = p
                resultI = i
                maxValue = curValue
            
            newPointCount += 1

    return backTraceItems(DP, resultI, resultP, weights, values, O) 

def knapsackNd(inputConstrains, inputItems, values, O):

    class wPoint:
        def __init__(self, dimensions):
            self.dimensions = tuple(dimensions)

        def __str__(self):
            return str(self.dimensions)
        
        def __repr__(self):
            return str(self.dimensions)
        
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

    emptyPoint = wPoint([0] * len(inputConstrains))

    def prepare(constrains, items, values, O):
        count = len(items)

        lessSizeItems = []

        lessSizeValues = []
        lessCount = 0

        for i in range(0, count):

            item = wPoint(items[i])
            itemValue = values[i]
           
            if item <= constrains:

                lessSizeItems.append(item)                
                lessSizeValues.append(itemValue)   

                lessCount += 1  
            
        O[0] += count

        return lessCount, lessSizeItems, lessSizeValues

    def checkCornerCases(constrains, lessSizeItems, lessSizeValues):        

        if  len(lessSizeItems) == 0:

            return emptyPoint.dimensions, [],[]
        
        return None      
  
    def getPoints(itemDimensions, constrainPoint, circularPointQuene, prevCyclePointCount, uniquePointSet):
        
        # merges ordered visited points with new points with keeping order in O(N) using single circular queue. 
        # each getPoints method call starts fetching visited points from qu start, pops visited point and pushes new point and visited to the end of qu in ASC order.
        # we skip new point if it in list already

        greaterQu = deque()
        
        if not itemDimensions in uniquePointSet:
            yield itemDimensions
            circularPointQuene.append(itemDimensions)

        for i in range(prevCyclePointCount):

            oldPoint = circularPointQuene.popleft()             

            while len(greaterQu) > 0 and greaterQu[0] < oldPoint:

                quPoint = greaterQu.popleft()

                yield quPoint 
                circularPointQuene.append(quPoint)

            yield oldPoint
            circularPointQuene.append(oldPoint)

            newPoint = oldPoint + itemDimensions

            if newPoint <= constrainPoint: 

                if not newPoint in uniquePointSet:   

                    peek = circularPointQuene[0]

                    if newPoint < peek:
                        yield newPoint
                        circularPointQuene.append(newPoint)

                    elif newPoint > peek:
                        greaterQu.append(newPoint)
        
        while len(greaterQu) > 0:

            quPoint = greaterQu.popleft()

            yield quPoint 
            circularPointQuene.append(quPoint)

    def getValue(p, prevDP):

        if p in prevDP:
            cur = prevDP[p]
            return cur[0], cur[1]

        return  0, emptyPoint

    def setValue(curDP, p, curVal, curDimensions, O):
        curDP[p] = (curVal, curDimensions)               
        O[0] += 1

    def backTraceItems(DP, resultI, resultP, items, values, O):
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

        return opt.dimensions, optItems, optValues

    def createDP(count):
        DP    = [None] * (count + 1)
        DP[0] = defaultdict()
        return DP

    constrains = wPoint(inputConstrains)

    count, lessSizeItems, lessSizeValues = prepare(constrains, inputItems, values, O)

    cornerCasesCheck = checkCornerCases(constrains, lessSizeItems, lessSizeValues)

    if  cornerCasesCheck:
        return cornerCasesCheck

    DP = createDP(count)

    resultI, resultP = 1, emptyPoint

    circularPointQuene = deque()

    maxValue, prevPointCount, newPointCount = 0, 0, 0

    for i in range(1, count + 1):

        DP[i] = defaultdict()

        itemValue, item   = lessSizeValues[i - 1], lessSizeItems[i - 1]
        prevDP,    curDP  = DP[i - 1], DP[i]

        prevPointCount, newPointCount = newPointCount, prevPointCount
        newPointCount = 0

        for p in getPoints(item, constrains, circularPointQuene, prevPointCount, prevDP):          

            curValue,    curDim   =  getValue(p,        prevDP) 
            posblValue,  posblDim =  getValue(p - item, prevDP) 

            posblValue  += itemValue
            posblDim    += item  

            if  curValue <= posblValue and posblDim <= constrains:
                curValue = posblValue
                curDim   = posblDim
               
            setValue(curDP, p, curValue, curDim, O)

            if  maxValue <= curValue:
                resultP = p
                resultI = i
                maxValue = curValue
            
            newPointCount += 1

    return backTraceItems(DP, resultI, resultP, lessSizeItems, lessSizeValues, O) 

def sortRevereseBoth(w, v):
    zipped_lists = zip(w, v)
    sorted_pairs = sorted(zipped_lists, reverse=True, key=lambda t: (t[0], t[1]))

    tuples = zip(*sorted_pairs)
    w1, v1 = [ list(tuple) for tuple in  tuples]

    return w1, v1

def sortReverese3Both(w, v, x):
    zipped_lists = zip(w, v, x)
    sorted_pairs = sorted(zipped_lists, reverse=True, key=lambda t: (t[0], t[1], t[2]))

    tuples = zip(*sorted_pairs)
    w1, v1, x1 = [ list(tuple) for tuple in  tuples]

    return w1, v1, x1

verbose = True

if True:
    if verbose:
        print("rational numbers tests for 1D, 2D and 3D knapsacks.")

    O = [0]

    A = [Decimal("0.2"), Decimal("1.200001"), Decimal("2.9000001"), Decimal("3.30000009"), Decimal("4.3"), Decimal("5.5"), Decimal("6.6"), Decimal("7.7"), Decimal("8.8"), Decimal("9.8")]
    A.sort(reverse=True)

    s = Decimal("10.5")

    expectedValue = Decimal("10.20000109")

    opt, optItems, optValues3 = knapsackNd((s, s), [(a, a) for a in A], A, O)
    assert expectedValue == sum(optValues3)
    opt, optWeights, optValues2 = knapsack2d(s, A, A, O)
    assert expectedValue == sum(optValues2)
    opt, optValues1 = knapsack1d(s, A, O)   
    assert expectedValue == sum(optValues1)

if True:

    def knapsack3d_dp(weightSize, volumeSize, weights, volumes, values):
   
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

    if verbose:
        print("3D knapsack matching with classic DP solution results.")

    O = [0]

    testCaseW =   [5,  3,   2,  5,  3,  4,  5, 6]
    testCaseV =   [8,  4,  12, 18,  5,  2,  1, 4]
    testCaseVal = [50, 30, 20, 50, 30, 40, 50, 60]

    s_weights, s_volumes, s_values = sortReverese3Both(testCaseW, testCaseV, testCaseVal)
 
    if True:

        for testKnapsackWeight in range(min(testCaseW), sum(testCaseW) - 1):
            for testKnapsackVolume in range(min(testCaseV), sum(testCaseV) - 1):

                dpRes = knapsack3d_dp(testKnapsackWeight, testKnapsackVolume, testCaseW, testCaseV, testCaseVal)

                dims = [None] * len(s_weights)

                for i in range(len(s_weights)):
                    dims[i] = (s_weights[i], s_volumes[i])

                opt, optItems, optValues = knapsackNd((testKnapsackWeight, testKnapsackVolume), dims, s_values, O)

                resVal = sum(optValues)

                resW = opt[0]
                resVol = opt[1]

                if resVal != dpRes or resW > testKnapsackWeight or resVol > testKnapsackVolume:
                    if verbose:
                        print("W: " +str(testKnapsackWeight) +  " V: " + str(testKnapsackVolume))
                        print(" k sum val : " + str(sum(optValues)) +" dp: " + str(dpRes) + " k sum vol : " + str(resVol) + " k sum w : " + str(resW) + " all sum val: " + str(sum(s_values)) + " all sum vol: " + str(sum(s_volumes)) + " all sum w: " + str(sum(s_weights)))
                    assert False

if True:

    if verbose:
        print("N partition sum tests.")

    # N partition tests
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
    case = 0

    for A, NU in tests:

        case += 1

        O[0] = 0

        if verbose:        
            print("case " + str(case))

        partResult, reminder = partitionN(A, NU, 0, O)

        if len(reminder) != 0 or len(partResult) != NU:

            if verbose:        
                print("case " + str(case))
                print("A " + str(A))
                print("part result " + str(partResult))
                print("part reminder  " + str(reminder))
                print("len " + str(len(A)))
                print("sum " + str(sum(A)))
                print("sum // NU" + str(sum(A) // NU))
                print("iter " + str(O[0]))

            assert False

if True:

    def unionTuples(tuples):
        rez = []
        for t in tuples:
            for tn in t:
                rez.append(tn)
        rez.sort()
        return rez


    if verbose:
        print("3 partition tests.")

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

    # the worst 3 partition test cases ever
    AT, NU = [(3, 3, 6), (3, 4, 5), (1, 5, 6), (1, 3, 8), (1, 4, 7), (4, 4, 4), (2, 5, 5), (1, 2, 9), (2, 3, 7), (2, 4, 6), (1, 1, 10), (2, 2, 8)], 12
    tests.append((unionTuples(AT), NU))  
    AT, NU = [(1, 2, 15), (2, 3, 13), (6, 6, 6), (4, 7, 7), (3, 3, 12), (1, 6, 11), (2, 7, 9), (3, 6, 9), (1, 1, 16), (2, 2, 14), (2, 5, 11), (5, 6, 7), (3, 5, 10), (4, 6, 8), (1, 8, 9), (1, 3, 14), (2, 4, 12), (4, 4, 10), (3, 7, 8), (1, 5, 12), (2, 6, 10), (3, 4, 11), (1, 7, 10), (1, 4, 13), (4, 5, 9), (2, 8, 8), (5, 5, 8)], 27
    tests.append((unionTuples(AT), NU))  
    AT, NU = [(2, 7, 15), (1, 3, 20), (4, 4, 16), (1, 1, 22), (6, 7, 11), (3, 5, 16), (4, 10, 10), (6, 6, 12), (4, 7, 13), (3, 4, 17), (2, 5, 17), (1, 8, 15), (1, 6, 17), (3, 10, 11), (2, 6, 16), (2, 4, 18), (2, 11, 11), (1, 7, 16), (4, 8, 12), (3, 9, 12), (5, 7, 12), (6, 8, 10), (3, 3, 18), (5, 6, 13), (2, 9, 13), (1, 5, 18), (5, 8, 11), (8, 8, 8), (2, 3, 19), (2, 10, 12), (1, 4, 19), (4, 5, 15), (1, 11, 12), (3, 8, 13), (4, 9, 11), (2, 2, 20), (7, 8, 9), (1, 10, 13), (4, 6, 14), (6, 9, 9), (3, 7, 14), (2, 8, 14), (1, 2, 21), (7, 7, 10), (1, 9, 14), (3, 6, 15), (5, 5, 14), (5, 9, 10)], 48
    tests.append((unionTuples(AT), NU))  

    case = 0
    for A, NU in tests:

        case += 1

        O[0] = 0

        if verbose:        
            print("case " + str(case))

        partResult, reminder = partitionN(A, NU, 3, O)

        if len(reminder) != 0 or len(partResult) != NU:

            if verbose:        
                print("case " + str(case))
                print("A " + str(A))
                print("part result " + str(partResult))
                print("part reminder  " + str(reminder))
                print("len " + str(len(A)))
                print("sum " + str(sum(A)))
                print("sum // NU" + str(sum(A) // NU))
                print("iter " + str(O[0]))

            assert False
 
if True:
    if verbose:
        print("Run knapsack problems by Silvano Martello and Paolo Toth 1990.")

    def testSilvano(W, V, R, c):
        O = [0]

        ws, vs = sortRevereseBoth(W, V)

        opt, optW, optV = knapsack2d(c, ws, vs, O)

        expectedSV = 0
        expectedSW = 0

        ind = 0
        for i in R:
            if i == 1:
                expectedSV += V[ind]
                expectedSW += W[ind]
            ind += 1
        
        testSV = sum(optV)

        assert (expectedSV == testSV)
    
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

if True:

    if verbose:
        print("Run 1d knapsack for hardinstances_pisinger subset sum test dataset.")

    script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in

    O = [0]

    with open(script_dir + '\hardInst.subset.sum.all.perf.csv', 'w', newline='') as csvfile:
        
        fieldnames = ['file', 'case', 'size', 'iter', 'max iter', 'N', 'good']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()

        testCase = list()
        testExpected = list()
        testKnapsack = 0
        rowToSkip = 0

        files = ["knapPI_16_20_1000", "knapPI_16_50_1000", "knapPI_16_100_1000"]
        #files = ["knapPI_16_20_1000", "knapPI_16_50_1000", "knapPI_16_100_1000", "knapPI_16_200_1000", "knapPI_16_500_1000"]

        fi = 0

        allGood = True

        for f in files:
            
            fi += 1

            caseNumber = 1

            if verbose:
                print(f)

            with open(os.path.join(script_dir, "hardinstances_pisinger/" + str(f) + ".csv")) as csvfile:
                spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')

                for row in spamreader:

                    if  len(row) == 0:
                        continue

                    if row[0] == "-----":

                        O[0] = 0

                        testCase.sort(reverse=True)

                        if fi > 5:
                            print(caseNumber)

                        opt, optItems = knapsack1d(testKnapsack, testCase, O)

                        rezS = sum(optItems) 
                        expS = sum(testExpected)

                        good = True

                        if  rezS < expS or opt > testKnapsack:
                            good = False
                            allGood = False
                            if verbose:
                                print(str(caseNumber) + " rez opt: " + str(opt) + " test opt:" +  str(testKnapsack) + " rez values: " + str(rezS) + " test values: " + str(expS))

                        maxIter = 4 * (len(testCase) ** 3)

                        if O[0] > maxIter:
                            if verbose:
                                print(str(caseNumber) + " max iter exceeded: " + str(maxIter) + " rez iter: " + str(O[0]))

                        writer.writerow({'file': str(f), 'case': str(caseNumber), 'size': str(testKnapsack), 'iter':  str(round(O[0])), 'max iter': str(maxIter), 'N': str(len(testCase)), 'good': str(good)})

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

if True:

    def DecimalData(data):

        return Decimal(Decimal(data) / 100000)

    def DecimalArray(data):

        for i in range(len(data)):
            data[i] = DecimalData(data[i])

    if verbose:
        print("Run 2d knapsack for hardinstances_pisinger test dataset in case of integer and rational numbers.")

    script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in

    with open(script_dir + '\\hardInst.2d.perf.decimal.csv', 'w', newline='') as csvfile:
        
        fieldnames = ['file', 'case', 'size', 'iter', 'max iter', 'N', 'good']
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

            print(f)          

            with open(os.path.join(script_dir, "hardinstances_pisinger/" + str(f) + ".csv")) as csvfile:
                spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')

                for row in spamreader:

                    if  len(row) == 0:
                        continue

                    if row[0] == "-----":

                        w, v = sortRevereseBoth(testCaseW, testCaseV)

                        O = [0]

                        opt, optWeights, optValues = knapsack2d(testKnapsack, w, v, O)

                        decimalW = list(w)

                        DecimalArray(decimalW)

                        testKnapsackDecimal = DecimalData(testKnapsack)                      

                        rezS = sum(optValues) 
                     

                        rezWS = sum(optWeights)

                        expS = sum(testExpected)

                        good = True

                        if rezS < expS or rezWS > testKnapsack or opt > testKnapsack:
                            good = False

                            if verbose:
                                print(str(caseNumber) + " rez opt: " + str(opt) + " test size:" +  str(testKnapsack) + "rez sum weights: " + str(rezWS) + " rez values: " + str(rezS) + " test values: " + str(expS))

                            assert False

                        maxIter = 10 * (len(w) ** 3)
                        rezIter = O[0]

                        if rezIter > maxIter:
                            if verbose:
                                print(str(caseNumber) + " max iter exceeded: " + str(maxIter) + " rez iter: " + str(rezIter))

                        writer.writerow({'file': str(f), 'case': str(caseNumber), 'size': str(testKnapsack), 'iter':  str(round(O[0])), 'max iter': str(maxIter), 'N': str(len(w)), 'good': str(good)})

                        O = [0]

                        optDec, optWeightsDec, optValuesDec = knapsack2d(testKnapsackDecimal, decimalW, v, O)

                        rezSDec = sum(optValuesDec) 
                        rezSWeightsDec = sum(optWeightsDec) 

                        if rezSDec != rezS:
                            
                            sum_wh = 0

                            for on in optValuesDec:
                                itemIndex = v.index(on, 0, len(v))
                                wh = w[itemIndex]
                                sum_wh += wh

                            if verbose:
                                print(str(caseNumber) + " decimal values: " + str(rezSDec) +  " sum decimal w: " + str(sum_wh) + " test size:" +  str(testKnapsack) + " test decimal size:" +  str(testKnapsackDecimal) + " test values: " + str(expS))
                            
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

if False:
    # iteration investigation test generator
    a = [3, 7, 13, 31, 37, 43, 67, 73, 79, 127, 151, 163, 193, 211, 223, 241, 283, 307, 331, 349, 367, 409, 421, 433, 463, 487, 541, 577, 601, 613, 619, 631, 643, 673, 727, 739, 769, 787, 823, 883, 937, 991, 997]
    a.sort(reverse=True)

    if verbose:
        print("len " + str(len(a)))
        print("sum " + str(sum(a)))
        print("len ** 4 " + str(len(a) ** 4))
        print("len ** 3 " + str(len(a) ** 3))
        print("len ** 2 " + str(len(a) ** 2))

    if False:

        script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in

        with open(script_dir + '\prime.plus.one.perf_.csv', 'w', newline='') as csvfile:
            
            fieldnames = ['size', 'iter', 'delta']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()

            # comment to get primes
            for i in range(0, len(a)):
                a[i] += 1

            prevO = 0

            for s in range(1, sum(a) - 1):

                O[0] = 0

                opt, optItems = knapsack1d(s, a, O)

                writer.writerow({'size': str(s), 'iter':  str(round(O[0])), 'delta': str(round(O[0] - prevO))})

                prevO = O[0]

if True:

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
        print("Run N way partition using integer partiton generator.")

    script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in

    with open(script_dir + '\\partition.perf.over.intpart.csv', 'w', newline='') as csvfile:
        
        fieldnames = ['item', 'case', 'limit', 'partition', 'N', 'sum', 'iter', 'max iter', 'good']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()

        itemList = [1, 2, 3, 5, 7, 8, 10, 11]
        maxIntPart = [20, 50, 100, 200, 300, 500, 1000, 2000]
    
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

                        partResult, resultReminder = partitionN(subSet, partition, 0, O)

                        if verbose:
                            print("item = " + str(item) + ", case i " + str(i) + " , case part limit " + str(partLimit) + " , n = " + str(len(subSet))  + " , partition " + str(partition) + " , iter " + str(round(O[0])))

                        resultPart = len(partResult)

                        rezSum = 0
                        for sub in partResult:
                            rezSum += sum(sub)

                        good = True
                    
                        if resultPart < partition or rezSum != expectedSum:

                            allGood = False

                            good = False

                            badItems.append((item, i, ))

                            sumRem = sum(resultReminder)

                            print("BAD: item = " + str(item) +  ", case i " + str(i) + " , case part limit " + str(partLimit) + " , n = " + str(len(subSet))  +  " , rezult partition " + str(resultPart) + " , expected partition " + str(partition) + " , rez sum " + str(rezSum) + " , total sum " + str(rezSum + sumRem) + " , expected sum " + str(expectedSum) + " , iter " + str(round(O[0])))

                        writer.writerow({'item': str(item), 'case': str(i), 'limit': str(partLimit), 'partition':  str(partition), 'N': str(len(subSet)), 'sum': str(rezSum), 'iter': str(round(O[0])), 'max iter': str((len(subSet)) * (partition ** 3)), 'good': str(good)})

                        if not allGood:
                            break
                    


        if len(badItems) > 0:
            print(badItems)

        assert allGood
                       
