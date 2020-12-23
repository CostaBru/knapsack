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

def partitionN(A, n, groupSize ,O):

    def checkBorderCases(A, n, count, maxElement,  O):

        if n == 1 and maxElement == 1:
            return 1

        if sumOfItems % n != 0:
            return 0

        size = sumOfItems // n

        if maxElement > size:
            return 0

        return None

    def prepareGrouping(A, count, O):

        maxElement = 0
        sumOfItems = 0

        group = defaultdict(list)

        for c in A:
            sumOfItems += c
            group[c].append(c)        
            if c > maxElement:
                maxElement = c
        
        O[0] += count

        return group, maxElement, sumOfItems
    
    def groupItems(group, O):

        allUnique = True
        nonUniqueList = defaultdict(int)

        for k in group.keys():        

            nonUniqueList[k] += len(group[k])
            
            if len(group[k]) > 1:
                allUnique = False

        O[0] += len(group)

        return allUnique, nonUniqueList

    count = len(A)

    if  count < n:
        return 0
    
    group, maxElement, sumOfItems = prepareGrouping(A, count, O)

    borderCaseCheck = checkBorderCases(A, n, count, maxElement, O)

    if borderCaseCheck is not None:
        return borderCaseCheck

    size = sumOfItems // n

    allUnique, nonUniqueList = groupItems(group, O)

    A0 = []

    if  allUnique:

        A.sort(reverse=True)
        O[0] += count * math.log2(count)

        if groupSize > 0:
            A0 = [1] * count

        return partitionRecursive(A, n, count, maxElement, size, A0, groupSize, O)
    
    elif len(nonUniqueList) == 1:

        if groupSize == 0:
            return 1 if count % n == 0 else 0 
        else:
            return 1 if count % n == 0 and count % groupSize == 0 else 0   
    else:

        if len(nonUniqueList) > n:
            partResult = partitionOverSameCountDuplicates(nonUniqueList, n, maxElement, size, groupSize, O)

            if partResult:
                return partResult

        sortedDuplicates = sortDuplicatesForPartitioning(group, count, nonUniqueList, O)

        if groupSize > 0:
            A0 = [1] * count

        return partitionRecursive(sortedDuplicates, n, count, maxElement, size, A0, groupSize, O)
   
    return 0  

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

        size = sum(nonUKeys) // n
        O[0] += newLen

        A0 = [1] * newLen

        return partitionRecursive(nonUKeys, n, newLen, maxElement, size, A0, groupSize, O)
    
    return None

def partitionRecursive(A, n, count, maxEl, size, A0, groupSize, O):    

    if  count < n:
        return 0
    
    result = 0

    if groupSize > 0:

        optW, optV, optWeights, optVolumes, optValues = knapsack3d(size, groupSize, A, A0, A, O)

        removedCount = len(optWeights)

        if  optW == size and optV == groupSize:            

            for toRemove in optWeights:
                A.remove(toRemove)
                A0.pop() 

            O[0] += removedCount

            newLen = count - removedCount

            if n == 2:
                O[0] += newLen
                return 1 if sum(A) == size and len(A) == groupSize else 0

            result = partitionRecursive(A, n - 1, newLen, maxEl, size, A0, groupSize, O)    
    else:

        optimal, optimalList = knapsack1d(size, A, O)

        if  optimal == size:            
            removedCount = len(optimalList)

            for toRemove in optimalList:
                A.remove(toRemove)  
            O[0] += removedCount

            newLen = count - removedCount

            if n == 2:
                O[0] += newLen

                n2Sum = sum(A)
                result = 1 if n2Sum == size else 0

                return result

            result = partitionRecursive(A, n - 1, newLen, maxEl, size, A0, groupSize, O)    
    return result

def canPartitionTwoFastFalsePositive(A, n, sum, O):
    
    if sum % 2 != 0 or n < 2:
        return False

    half = sum // 2
    highSum = A[0]
    
    if highSum == half:
        return True
    
    for i in range(1, n):
        presum = highSum
        for j in range(i, n):
            O[0] += 1
            presum = A[j] + presum
            if presum > half:
                presum -= A[j]
            elif presum == half:
                return True
    return False

def knapsack1d(size, items, O):

    def prepare(size, items, O):
        
        count = len(items)
        sum = 0
        lessCountSum = 0    
        minItem = size
        partialSum09 = [0] * count
        starting = 1
        i = 0
        for item in items:

            itemWeight = item
            sum += itemWeight

            partialSum09[count - i - 1] = sum

            if itemWeight <= size:
                lessCountSum += itemWeight  
            else:
                starting += 1

            if minItem > itemWeight:
                minItem = itemWeight
            
            i += 1

        O[0] += count
        return count, sum, lessCountSum, minItem, partialSum09, starting

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
  
    def getPoints(itemWeight, size, circularPointQuene,  minItem, partSumForItem09, prevCyclePointCount, uniquePointSet):
       
        # merges ordered visited points with new points with keeping order in O(N) using single circular queue. 
        # each getPoints method call starts fetching visited points from qu start, pops visited point and pushes new point and visited to the end of qu in ASC order.
        # we skip new point if it in list already
        # skips points if they will not contribute to optimal solution

        greaterQu = deque()

        useItemItself = partSumForItem09 >= (size // 2)

        limit = size - partSumForItem09

        if useItemItself and (itemWeight + minItem <= size or itemWeight == size) and not itemWeight in uniquePointSet:
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
            DP[i] = defaultdict()
        return DP

    count, sum, lessCountSum, minItem, partialSum09, starting  = prepare(size, items, O)

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

        for p in getPoints(itemWeight, size, circularPointQuene, minItem, partSumForItem09, prevPointCount, prevDP):          

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

def knapsack3d(weightSize, volumeSize, weights, volumes, values, O):

    def prepare(weightSize, volumeSize, weights, volumes, values, O):
        count = len(weights)
        lessCountSumWeight = 0    
        lessCountSumVolume = 0   

        lessSizeWeights = []
        lessSizeVolumes = []
        lessSizeValues = []
        lessCount = 0

        for i in range(0, len(weights)):

            itemWeight = weights[i]
            itemVolume = volumes[i]
            itemValue = values[i]
           
            if itemWeight <= weightSize and itemVolume <= volumeSize:
                lessCountSumWeight += itemWeight
                lessCountSumVolume += itemVolume

                lessSizeWeights.append(itemWeight)                
                lessSizeVolumes.append(itemVolume)                
                lessSizeValues.append(itemValue)   

                lessCount += 1  
            
        O[0] += count

        return lessCount, lessCountSumWeight, lessCountSumVolume, lessSizeWeights, lessSizeVolumes, lessSizeValues

    def checkCornerCases(weightSize, volumeSize, lessSizeWeights, lessSizeVolumes, lesSizeValues, lessSizeSumWeight, lessSizeSumVolume):        

        if  lessSizeSumWeight == 0 or lessSizeSumVolume == 0:
            return 0, 0,[],[],[]
        
        if  lessSizeSumWeight < weightSize and lessSizeSumVolume < volumeSize:
            return lessSizeSumWeight, lessSizeSumVolume, lessSizeWeights, lessSizeVolumes, lesSizeValues

        return None      
  
    def getPoints(itemWeight, itemVolume, weightSize, volumeSize, circularPointQuene, prevCyclePointCount, uniquePointSet):
        
        # merges ordered visited points with new points with keeping order in O(N) using single circular queue. 
        # each getPoints method call starts fetching visited points from qu start, pops visited point and pushes new point and visited to the end of qu in ASC order.
        # we skip new point if it in list already

        greaterQu = deque()

        newPoint = (itemWeight, itemVolume)
        
        if not newPoint in uniquePointSet:
            yield newPoint
            circularPointQuene.append(newPoint)

        for i in range(prevCyclePointCount):

            oldPoint = circularPointQuene.popleft()             

            while len(greaterQu) > 0 and greaterQu[0] < oldPoint:

                quPoint = greaterQu.popleft()

                yield quPoint 
                circularPointQuene.append(quPoint)

            yield oldPoint
            circularPointQuene.append(oldPoint)

            newPointW = oldPoint[0] + itemWeight
            newPointV = oldPoint[1] + itemVolume

            if newPointW <= weightSize and newPointV <= volumeSize: 

                newPoint = (newPointW, newPointV) 

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
            return cur[0], cur[1], cur[2]

        return  0, 0, 0

    def setValue(curDP, p, curVal, curW, curV, O):
        curDP[p] = (curVal, curW, curV)               
        O[0] += 1

    def backTraceItems(DP, resultI, resultP, weights, values, volumes, O):
        optW = 0
        optV = 0
        res = DP[resultI][resultP][0]
        optWeights, optValues, optVolumes = [], [], []
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
                itemWeight, itemValue, itemVolume = weights[i - 1], values[i - 1], volumes[i - 1]    

                optWeights.append(itemWeight)
                optValues.append(itemValue)
                optVolumes.append(itemVolume)

                res   -= itemValue

                point = (point[0] - itemWeight, point[1] - itemVolume)

                optW += itemWeight
                optV += itemVolume

        return optW, optV, optWeights, optVolumes, optValues

    def createDP(count):
        DP    = [None] * (count + 1)
        DP[0] = defaultdict()
        return DP

    count, lessSizeSumWeight, lessSizeSumVolume, lessSizeWeights, lessSizeVolumes, lessSizeValues = prepare(weightSize, volumeSize, weights, volumes, values, O)

    cornerCasesCheck = checkCornerCases(weightSize, volumeSize, lessSizeWeights, lessSizeVolumes, lessSizeValues, lessSizeSumWeight, lessSizeSumVolume)

    if  cornerCasesCheck:
        return cornerCasesCheck

    DP = createDP(count)

    resultI, resultP = 1, (0, 0)

    circularPointQuene = deque()

    maxValue, prevPointCount, newPointCount = 0, 0, 0

    for i in range(1, count + 1):

        DP[i] = defaultdict()

        itemValue, itemWeight, itemVolume   = lessSizeValues[i - 1], lessSizeWeights[i - 1], lessSizeVolumes[i - 1]
        prevDP,    curDP                    = DP    [i - 1],      DP[i]

        prevPointCount, newPointCount = newPointCount, prevPointCount
        newPointCount = 0

        for p in getPoints(itemWeight, itemVolume, weightSize, volumeSize, circularPointQuene, prevPointCount, prevDP):          

            curValue,    curWeight,   curVolume   =  getValue( p,                                     prevDP) 
            posblValue,  posblWeight, posblVolume =  getValue((p[0] - itemWeight, p[1] - itemVolume), prevDP) 

            posblValue  += itemValue
            posblWeight += itemWeight  
            posblVolume += itemVolume  

            if  curValue < posblValue and posblWeight <= weightSize and posblVolume <= volumeSize:
                curValue = posblValue
                curWeight = posblWeight
                curVolume = posblVolume
               
            setValue(curDP, p, curValue, curWeight, curVolume, O)

            if  maxValue <= curValue:
                resultP = p
                resultI = i
                maxValue = curValue
            
            newPointCount += 1

    return backTraceItems(DP, resultI, resultP, lessSizeWeights, lessSizeValues, lessSizeVolumes, O) 

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

def DecimalData(data):

        return Decimal(Decimal(data) / 100000)

def DecimalArray(data):

    for i in range(len(data)):
        data[i] = DecimalData(data[i])

verbose = True

if True:
    if verbose:
        print("rational numbers tests for 1D, 2D and 3D knapsacks.")

    O = [0]

    A = [Decimal("0.2"), Decimal("1.200001"), Decimal("2.9000001"), Decimal("3.30000009"), Decimal("4.3"), Decimal("5.5"), Decimal("6.6"), Decimal("7.7"), Decimal("8.8"), Decimal("9.8")]
    A.sort(reverse=True)

    s = Decimal("10.5")

    expectedValue = Decimal("10.20000109")

    opt, optV, optWeights, optVolumes, optValues = knapsack3d(s, s, A, A, A, O)
    assert expectedValue == sum(optValues)
    opt, optWeights, optValues = knapsack2d(s, A, A, O)
    assert expectedValue == sum(optValues)
    opt, optValues = knapsack1d(s, A, O)   
    assert expectedValue == sum(optValues)

if True:
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

                opt, optV, optWeights, optVolumes, optValues = knapsack3d(testKnapsackWeight, testKnapsackVolume, s_weights, s_volumes, s_values, O)

                resVal = sum(optValues)

                resVol = sum(optVolumes)
                resW = sum(optWeights)

                if resVal != dpRes or resW > testKnapsackWeight or resVol > testKnapsackVolume:
                    if verbose:
                        print("W: " +str(testKnapsackWeight) +  " V: " + str(testKnapsackVolume))
                        print(" k sum val : " + str(sum(optValues)) +" dp: " + str(dpRes) + "k sum vol : " + str(sum(optVolumes)) + "k sum w : " + str(sum(optWeights)) + " all sum val: " + str(sum(s_values)) + " all sum vol: " + str(sum(s_volumes)) + " all sum w: " + str(sum(s_weights)))
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
    A, NU = [20, 23, 25, 49, 45, 27, 40, 22, 19, 20, 23, 25, 49, 45, 27, 40, 22, 19], 3
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

        if partitionN(A, NU, 0, O) != 1:

            if verbose:        
                print("case " + str(case))
                print("A " + str(A))
                print("len " + str(len(A)))
                print("sum " + str(sum(A)))
                print("sum // NU" + str(sum(A) // NU))
                print("iter " + str(O[0]))

            assert False

if True:

    if verbose:
        print("3 partition tests.")

    O = [0]

    tests = []
    # https://en.wikipedia.org/wiki/3-partition_problem
    A, NU =  [20, 23, 25, 49, 45, 27, 40, 22, 19], 3
    tests.append((A, NU))   
    A, NU = [1, 2, 5, 6, 7, 9],2   
    tests.append((A, NU))  
    # http://www.columbia.edu/~cs2035/courses/ieor4405.S17/npc-sched.pdf
    A, NU = [26, 26, 27, 28, 29, 29, 31, 33, 39, 40, 45, 47], 4 
    tests.append((A, NU))   
    A, NU = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1], 3
    tests.append((A, NU))   
    case = 0

    for A, NU in tests:

        case += 1

        O[0] = 0

        if partitionN(A, NU, 3, O) != 1:

            if verbose:        
                print("case " + str(case))
                print("A " + str(A))
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
    if verbose:
        print("Run 2d knapsack for hardinstances_pisinger test dataset in case of integer and rational numbers..")

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
                
