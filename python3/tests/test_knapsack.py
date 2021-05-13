'''
Copyright Feb 2021 Konstantin Briukhnov (kooltew at gmail.com) (@CostaBru). San-Francisco Bay Area.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), 
to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. 
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, 
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
import sys
from random import shuffle, randint, seed

import unittest
import datetime
import time
import math
import csv
import os

from tAPI import *
from tests.helpers import *

from knapsack.knapsack2d_dp import knapsack2d_dp
from knapsack.wPoint import wPoint

from tests import randomTestCount, test_data_dir, out_dir, helpers, dtNow, try_redirect_out, restore_out
from tests.helpers import listValuesEqual, DecimalData, DecimalArray, sortReverse3Both, sortReverseBoth, shuffleBoth

from flags.flags import verbose


class KnapsackTests(unittest.TestCase):

    def setUp(self):
        try_redirect_out("knapsack", self._testMethodName)

    def tearDown(self):
        restore_out()

    # NP complete: Rational numbers tests for equal-subset-sum knapsack, 1-0 knapsack, and N dimension knapsacks, where N 2-4.
    def test_1_rational_numbers(self):
        if verbose:
            print(
                "Rational numbers tests for equal-subset-sum knapsack, 1-0 knapsack, and N dimension knapsacks, where N 2-4.")

        iterCounter = [0]

        A = [Decimal("0.2"), Decimal("1.200001"), Decimal("2.9000001"), Decimal("3.30000009"), Decimal("4.3"),
             Decimal("5.5"), Decimal("6.6"), Decimal("7.7"), Decimal("8.8"), Decimal("9.8")]

        A.sort(reverse=True)

        s = Decimal("10.5")

        expectedValue = Decimal("10.20000109")

        opt, optDim, optItems, optValuesN4 = knapsackNd(wPoint((s, s, s, s)), [wPoint((a, a, a, a)) for a in A], A, iterCounter)
        self.assertEqual(expectedValue, opt)

        opt, optDim, optItems, optValuesN3 = knapsackNd(wPoint((s, s, s)), [wPoint((a, a, a)) for a in A], A, iterCounter)
        self.assertEqual(expectedValue, opt)

        opt, optDim, optItems, optValuesN2 = knapsackNd(wPoint((s, s)), [wPoint((a, a)) for a in A], A, iterCounter)
        self.assertEqual(expectedValue, opt)

        opt, optDim, optWeights, optValues2 = knapsack(s, A, A, iterCounter)
        self.assertEqual(expectedValue, opt)

        opt, optDim, optWeights, optValuesP = paretoKnapsack(s, A, A, iterCounter)
        self.assertEqual(expectedValue, opt)

        opt, optDim, optWeights, optValuesP = hybridParetoKnapsack(s, A, A, iterCounter)
        self.assertEqual(expectedValue, opt)

        opt, optValues1 = subsKnapsack(s, A, iterCounter)
        self.assertEqual(expectedValue, opt)

        opt, optValues1 = subsParetoKnapsack(s, A, iterCounter)
        self.assertEqual(expectedValue, opt)

    # Polynomial: Superincreasing tests for equal-subset-sum knapsack, 1-0 knapsack, and N dimension knapsacks, where N = 2.
    def test_2_superincreasing(self):

        if verbose:
            print("Superincreasing integer numbers tests.")

        iterCounter = [0]
        A = [1, 2, 5, 21, 69, 189, 376, 919]

        for i in range(1, 3):

            if i % 2 == 1:
                A.reverse()

            for s in range(sum(A)):

                opt1, expected = subsKnapsack(s, A, iterCounter, doSolveSuperInc=False)

                opt2, optValues1 = subsKnapsack(s, A, iterCounter)
                self.assertTrue(listValuesEqual(optValues1, expected))

                opt, optDim, optItems, optValues2 = knapsack(s, A, A, iterCounter)
                self.assertTrue(listValuesEqual(optValues2, expected))

                opt, optDim, optItems3, optValues3 = knapsackNd(wPoint((s, s)), [wPoint((a, a)) for a in A], A, iterCounter)
                self.assertTrue(listValuesEqual(optValues3, expected))

                opt, optDim, optItems, optValuesP = paretoKnapsack(s, A, A, iterCounter)
                self.assertTrue(listValuesEqual(optValuesP, expected))

                opt, optValuesSP = subsParetoKnapsack(s, A, iterCounter)
                self.assertTrue(listValuesEqual(optValuesSP, expected))

        if verbose:
            print("Superincreasing rational numbers tests.")

        for s in range(sum(A)):
            decA = list(A)

            DecimalArray(decA)

            decS = DecimalData(s)

            opt, expected = subsKnapsack(decS, decA, iterCounter, doSolveSuperInc=False)

            opt, decOptValues1 = subsKnapsack(decS, decA, iterCounter)
            self.assertTrue(listValuesEqual(decOptValues1, expected))

            opt, decOptValuesSP = subsParetoKnapsack(decS, decA, iterCounter)
            self.assertTrue(listValuesEqual(decOptValuesSP, expected))

            opt, optDim, decOptItems, decOptValues2 = knapsack(decS, decA, decA, iterCounter)
            self.assertTrue(listValuesEqual(decOptValues2, expected))

            opt, optDim, decOptItems3, optValues3 = knapsackNd(wPoint((decS, decS)), [wPoint((da, da)) for da in decA], decA, iterCounter)
            self.assertTrue(listValuesEqual(optValues3, expected))

            opt, optDim, decOptItems, decOptValuesP = paretoKnapsack(decS, decA, decA, iterCounter)
            self.assertTrue(listValuesEqual(decOptValuesP, expected))

    # Polynomial: Partial superincreasing numbers tests.
    def test_3_partial_superincreasing(self):
        if verbose:
            print("Partial superincreasing numbers tests.")

        iterCounter = [0]
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

                for s in range(3, sum(testCase)):

                    optE, expected = subsKnapsack(s, testCase, iterCounter, doSolveSuperInc=False)

                    if verbose: print(f"Partial superincreasing test: s = {s},  reverse = {revers}, index {i}")

                    iterCounter[0] = 0
                    opt1, optValues1 = subsKnapsack(s, testCase, iterCounter)
                    self.assertTrue(listValuesEqual(optValues1, expected) or sum(expected) == opt1)

                    iterCounter[0] = 0
                    opt1, optValuesSP = subsParetoKnapsack(s, testCase, iterCounter)
                    self.assertTrue(listValuesEqual(optValuesSP, expected) or sum(optValuesSP) == opt1)

                    iterCounter[0] = 0
                    opt2, optDim, optItems, optValues2 = knapsack(s, testCase, testCase, iterCounter)
                    self.assertTrue(listValuesEqual(optValues2, expected) or sum(expected) == opt2)

                    iterCounter[0] = 0
                    opt3, optDim, optItems3, optValues3 = knapsackNd(wPoint((s, s)), [wPoint((a, a)) for a in testCase], testCase, iterCounter)
                    self.assertTrue(listValuesEqual(optValues3, expected) or sum(expected) == opt3)

                    iterCounter[0] = 0
                    opt4, optDim, optItems, optValues4 = paretoKnapsack(s, testCase, testCase, iterCounter)
                    self.assertTrue(listValuesEqual(optValues4, expected) or sum(expected) == opt4)

    # Polynomial: Partial geometric progression numbers tests.
    def test_4_partial_geometric_progression(self):

        if verbose: print("Partial geometric progression numbers tests.")

        iterCounter = [0]

        A = [2] * 10

        for i in range(1, 10):
            A[i] *= int(A[i - 1] * 3)

        for i in range(2, len(A) - 1, 2):

            testCase = list(A)

            testCase.insert(i + 1, testCase[i] + 1)

            step = sum(testCase) // 100

            for s in range(step, sum(testCase), step):

                optE, expected = subsKnapsack(s, testCase, iterCounter, doSolveSuperInc=False)

                t1 = time.perf_counter()

                opt1, optValues1 = subsKnapsack(s, testCase, iterCounter)
                self.assertTrue(listValuesEqual(optValues1, expected))

                t2 = time.perf_counter()

                opt2, optDim, optItems, optValues2 = knapsack(s, testCase, testCase, iterCounter)
                self.assertTrue(listValuesEqual(optValues2, expected))

                t3 = time.perf_counter()

                opt3, optDim, optItems3, optValues3 = knapsackNd(wPoint((s, s)), [wPoint((a, a)) for a in testCase],
                                                                 testCase, iterCounter)
                self.assertTrue(listValuesEqual(optValues3, expected))

                t4 = time.perf_counter()

                opt2, optDim, optItems, optValuesP = paretoKnapsack(s, testCase, testCase, iterCounter)
                self.assertTrue(listValuesEqual(optValuesP, expected))

                t5 = time.perf_counter()

                if verbose: print(f"Partial geometric progression test: i {i}, size {s}, subs {round(t2 - t1, 4)}, 1-0 {round(t3 - t2, 4)}, 2D {round(t4 - t3, 4)}, pareto {round(t5 - t4, 4)}.")

    # NP complete: 2D knapsack matching with classic DP solution results. N=13
    def test_5_knapsack_matching_with_dp2(self):

        iterCounter = [0]
        O_dp = [0]

        testCaseW = [5, 3, 2, 5, 3, 4, 5, 6, 2, 5, 1, 3, 6, 8]
        testCaseV = [8, 4, 12, 18, 5, 2, 1, 4, 3, 2, 2, 4, 10, 9]
        testCaseVal = [50, 30, 20, 50, 30, 40, 50, 60, 10, 70, 80, 10, 15, 30]

        if verbose: print(f"2D knapsack matching with classic DP solution results. N={len(testCaseW)}")

        s_weights, s_volumes, s_values = sortReverse3Both(testCaseW, testCaseV, testCaseVal)

        if True:

            for testKnapsackWeight in range(min(testCaseW), sum(testCaseW) - 1):
                for testKnapsackVolume in range(min(testCaseV), sum(testCaseV) - 1):

                    dpRes = knapsack2d_dp(testKnapsackWeight, testKnapsackVolume, testCaseW, testCaseV, testCaseVal, O_dp)

                    dims = [None] * len(s_weights)

                    for i in range(len(s_weights)):
                        dims[i] = wPoint((s_weights[i], s_volumes[i]))

                    constraints = wPoint((testKnapsackWeight, testKnapsackVolume))

                    opt, optDim, optItems, optValues = knapsackNd(constraints, dims, s_values, iterCounter)

                    resW = optDim.getDimension(0)
                    resVol = optDim.getDimension(1)

                    if opt != dpRes or resW > testKnapsackWeight or resVol > testKnapsackVolume:
                        if verbose:
                            print(f"W: {testKnapsackWeight} V: {testKnapsackVolume}", end="")
                            print(f" k sum val : {sum(optValues)}, dp: {dpRes}  k sum vol : {resVol} k sum w : {resW}  all sum val: {sum(s_values)} all sum vol: {sum(s_volumes)} all sum w: {sum(s_weights)}")
                        self.assertTrue(False)

    # NP hard: Integer and Decimal mixed multidimensional knapsack problem (MKP) test
    def test_91_MKP(self):

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
        genExpectedValue, genExpectedIndexes = 3531, [0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0, 0, 1,
                                                      1, 0, 0, 1, 0, 1]

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

        descDims2d, descValues = sortReverseBoth(dims2d, values)
        constr2d = wPoint((12210, Decimal(12)))

        if verbose: print(f"Integer and Decimal mixed multidimensional knapsack problem (MKP) test. N {len(data)}")

        iterCounter = [0]

        t1 = time.perf_counter()

        optValue, optDim, optItems, optValues = knapsackNd(constr2d, descDims2d, descValues, iterCounter)

        t2 = time.perf_counter()

        optRez = sum(optValues)

        good = optRez >= genExpectedValue and optDim <= constr2d

        iterMax = 2 ** (len(data))
        iterRez = round(iterCounter[0])

        if verbose: print( f"MKP time: {round(t2 - t1, 4)}, optimized - genetic expected: {optRez - genExpectedValue}, iter: {iterRez}, iterMax: {iterMax}, dIter: {iterMax - iterRez}")

        self.assertTrue(good)

    # NP hard: Integer multidimensional knapsack problem (MKP) with same profit value limits tests
    def test_7_MKP_same_profit(self):

        mixDimData = [(821, 976, 1),
                      (1144, 718, 1),
                      (634, 124, 1),
                      (701, 1086, 1),
                      (291, 1633, 1),
                      (1702, 1702, 1),
                      (1633, 291, 1),
                      (1086, 701, 1),
                      (124, 634, 1),
                      (718, 1144, 1),
                      (976, 821, 1),
                      (1438, 124, 1),
                      ]

        cnt = len(mixDimData)

        dimsMix2d = [wPoint((p[0], p[1])) for i, p in enumerate(mixDimData)]
        mixValues2d = [p[2] for p in mixDimData]

        descDims2d, descValues2d = sortReverseBoth(dimsMix2d, mixValues2d)

        sumOfAll = sum([p[0] for p in mixDimData])
        minItem = min([p[0] for p in mixDimData]) - 1

        if verbose: print(f"MKS 2d matching results with limits turned on")

        from flags.flags import doUseLimits

        prevDoUseLimits = doUseLimits

        for i in range(1, 3):

            iterCounter = [0]

            ascOrder = i % 2 == 1

            for constaint1 in range(minItem, sumOfAll, minItem // 2):

                for constaint2 in range(minItem, sumOfAll, minItem // 2):

                    testDescDims = list(descDims2d)
                    testDescValues = list(descValues2d)

                    testDims = list(reversed(testDescDims)) if ascOrder else list(testDescDims)
                    testValues = list(reversed(testDescValues)) if ascOrder else list(testDescValues)

                    t1 = time.perf_counter()

                    constr2d = wPoint((constaint1, constaint2))

                    optValue2, optDims2, optItems2, optValues2 = knapsackNd(constr2d, testDescDims, testDescValues, iterCounter,
                                                                            doUseLimits=False)

                    tFull = round(time.perf_counter() - t1, 4)

                    fullIterRez = iterCounter[0]

                    iterCounter = [0]

                    t1 = time.perf_counter()

                    optValue3, optDims3, optItems3, optValues3 = knapsackNd(constr2d, testDims, testValues, iterCounter)

                    tLimitsOn = round(time.perf_counter() - t1, 4)

                    t2 = time.perf_counter()

                    iterRez = round(iterCounter[0])

                    good = optValue3 == optValue2 and optDims3 <= constr2d and optDims2 <= constr2d

                    if verbose: print(f"MKS 2d, ASC={ascOrder}, constraint1: {constaint1}, constraint2: {constaint2}, time: {round(t2 - t1, 4)}, optimized - expected: {optValue3 - optValue2}, dlen {len(optValues3) - len(optValues2)} , iter: {iterRez}, dIter: {fullIterRez - iterRez}, dt {tFull - tLimitsOn}")

                    self.assertTrue(good)

        doUseLimits = prevDoUseLimits

    # NP hard: Integer multidimensional knapsack problem (MKP) T partition grouping operator tests
    def test_8_T_partition_grouping_operator(self):

        mixDimData = [(821, 1, 821),
                      (1144, 1, 1144),
                      (634, 1, 634),
                      (701, 1, 701),
                      (291, 1, 291),
                      (1702, 1, 1702),
                      (1633, 1, 1633),
                      (1086, 1, 1086),
                      (124, 1, 124),
                      (718, 1, 718),
                      (976, 1, 976),
                      (1438, 1, 1438),
                      ]

        cnt = len(mixDimData)

        dimsMix2d = [wPoint((p[0], p[1])) for i, p in enumerate(mixDimData)]
        mixValues2d = [p[2] for p in mixDimData]

        descDims2d, descValues2d = sortReverseBoth(dimsMix2d, mixValues2d)

        sumOfAll = sum([p[0] for p in mixDimData])
        minItem = min([p[0] for p in mixDimData]) - 1

        if verbose: print(f"MKS N partition 2d matching results with limits turned off")

        for i in range(1, 3):

            iterCounter = [0]

            ascOrder = i % 2 == 0

            for constaint1 in range(minItem, sumOfAll, minItem // 2):

                for constaint2 in range(1, len(mixDimData)):

                    #ascOrder = True
                    #constaint1 = 6711
                    #constaint2 = 6

                    testDescDims = list(descDims2d)
                    testDescValues = list(descValues2d)

                    testDims = list(reversed(testDescDims)) if ascOrder else list(testDescDims)
                    testValues = list(reversed(testDescValues)) if ascOrder else list(testDescValues)

                    t1 = time.perf_counter()

                    constr2d = wPoint((constaint1, constaint2))

                    optValue2, optDim2, optItems2, optValues2 = knapsackNd(constr2d, testDescDims, testDescValues, iterCounter, doUseLimits=False)

                    tFull = round(time.perf_counter() - t1, 4)

                    fullIterRez = iterCounter[0]

                    iterCounter = [0]

                    t1 = time.perf_counter()

                    optValue3, optDim3, optItems3, optValues3 = knapsackNd(constr2d, testDims, testValues, iterCounter)

                    tLimitsOn = round(time.perf_counter() - t1, 4)

                    t2 = time.perf_counter()

                    iterRez = round(iterCounter[0])

                    good = optValue2 == optValue3 and optDim3 <= constr2d

                    if verbose: print(f"MKS N partition test:  ASC={ascOrder}, constaint1: {constaint1}, constaint2 {constaint2} , time: {round(t2 - t1, 4)}, optimized - expected: {optValue2 - optValue3}, dlen {len(optValues3) - len(optValues2)} , iter: {iterRez}, dIter: {fullIterRez - iterRez}, dt {tFull - tLimitsOn}")

                    self.assertTrue(good)

    # NP complete: Integer 1-0 knapsack problem limits tests
    def test_8_integer_1_0_knapsack_problem_limits(self):

        mixDimData = [(821, 100),
                      (1144, 100),
                      (634, 100),
                      (701, 100),
                      (291, 100),
                      (1702, 100),
                      (1633, 100),
                      (1086, 100),
                      (124, 100),
                      (718, 100),
                      (976, 100),
                      (1438, 100),
                      (822, 100),
                      (1143, 100),
                      (640, 100),
                      (702, 100),
                      (291, 100),
                      (1702, 100),
                      (1633, 100),
                      (2000, 100),
                      (100, 100),
                      (701, 100),
                      (1976, 100),
                      (1638, 100),
                      ]

        cnt = len(mixDimData)

        dimsd = [p[0] for p in mixDimData]
        values = [p[1] for p in mixDimData]

        descDims, descValues = sortReverseBoth(dimsd, values)

        sumOfAll = sum([p[0] for p in mixDimData])
        minItem = min([p[0] for p in mixDimData]) - 1

        if verbose: print(f"Integer 1-0 knapsack problem limits tests")

        for i in range(1, 3):

            iterCounter = [0]

            ascOrder = i % 2 == 1

            for constraint in range(minItem, sumOfAll, minItem // 2):

                testDescDims = list(descDims)
                testDescValues = list(descValues)

                testDims = list(reversed(testDescDims)) if ascOrder else list(testDescDims)
                testValues = list(reversed(testDescValues)) if ascOrder else list(testDescValues)

                t1 = time.perf_counter()

                optValue2, optDims2, optItems2, optValues2 = knapsack(constraint, testDescDims, testDescValues, iterCounter, doUseLimits=False)

                tFull = round(time.perf_counter() - t1, 4)

                fullIterRez = iterCounter[0]

                iterCounter = [0]

                t1 = time.perf_counter()

                optValue3, optDims3, optItems3, optValues3 = knapsack(constraint, testDims, testValues, iterCounter)

                tLimitsOn = round(time.perf_counter() - t1, 4)

                t1 = time.perf_counter()

                optValueP, optDimsP, optItemsP, optValuesP = paretoKnapsack(constraint, testDims, testValues, iterCounter)

                tLimitsOnP = round(time.perf_counter() - t1, 4)

                t2 = time.perf_counter()

                iterRez = round(iterCounter[0])

                good = optValue3 == optValue2 and optValueP == optValue2 and optDims3 <= constraint and optDims2 <= constraint and optDimsP <= constraint

                if verbose: print(f"1-0 knapsack limits test:  ASC={ascOrder}, constraint: {constraint}, time: {round(t2 - t1, 4)}, optimized - expected: {optValue2 - optValue3}, dlen {len(optValues3) - len(optValues2)} , iter: {iterRez}, dIter: {fullIterRez - iterRez}, dt {tFull - tLimitsOn}")

                self.assertTrue(good)

    # NP complete: Strict 3 and 6 partition problem tests.
    def test_8_strict_3_and_6_partition_problem(self):
        def unionTuples(tuples):
            rez = []
            for t in tuples:
                for tn in t:
                    rez.append(tn)
            rez.sort()
            return rez

        if verbose: print("3-partition problem for integer numbers tests.")

        iterCounter = [0]

        tests = []
        # https://en.wikipedia.org/wiki/3-partition_problem
        AT, NU = [(20, 25, 45), (23, 27, 40), (49, 22, 19), (30, 30, 30)], 4
        tests.append((unionTuples(AT), NU))
        AT, NU = [(1, 5, 9), (2, 6, 7)], 2
        tests.append((unionTuples(AT), NU))
        # http://www.columbia.edu/~cs2035/courses/ieor4405.S17/npc-sched.pdf
        A, NU = [26, 26, 27, 28, 29, 29, 31, 33, 39, 40, 45, 47], 4
        tests.append((A, NU))
        AT, NU = [(1, 1, 1), (1, 1, 1), (1, 1, 1), (1, 1, 1), (1, 1, 1)], 5
        tests.append((unionTuples(AT), NU))
        AT, NU = [(1, 1, 1), (1, 1, 1), (1, 1, 1), (1, 1, 1), (1, 1, 1), (1, 1, 1), (1, 1, 1), (1, 1, 1), (1, 1, 1),
                  (1, 1, 1), (1, 1, 1), (1, 1, 1)], 12
        tests.append((unionTuples(AT), NU))

        # the worst 3 partition test cases ever
        AT, NU = [(3, 3, 6), (3, 4, 5), (1, 5, 6), (1, 3, 8), (1, 4, 7), (4, 4, 4), (2, 5, 5), (1, 2, 9), (2, 3, 7),
                  (2, 4, 6), (1, 1, 10), (2, 2, 8)], 12
        tests.append((unionTuples(AT), NU))
        AT, NU = [(1, 2, 15), (2, 3, 13), (6, 6, 6), (4, 7, 7), (3, 3, 12), (1, 6, 11), (2, 7, 9), (3, 6, 9),
                  (1, 1, 16), (2, 2, 14), (2, 5, 11), (5, 6, 7), (3, 5, 10), (4, 6, 8), (1, 8, 9), (1, 3, 14),
                  (2, 4, 12), (4, 4, 10), (3, 7, 8), (1, 5, 12), (2, 6, 10), (3, 4, 11), (1, 7, 10), (1, 4, 13),
                  (4, 5, 9), (2, 8, 8), (5, 5, 8)], 27
        tests.append((unionTuples(AT), NU))
        AT, NU = [(2, 7, 15), (1, 3, 20), (4, 4, 16), (1, 1, 22), (6, 7, 11), (3, 5, 16), (4, 10, 10), (6, 6, 12),
                  (4, 7, 13), (3, 4, 17), (2, 5, 17), (1, 8, 15), (1, 6, 17), (3, 10, 11), (2, 6, 16), (2, 4, 18),
                  (2, 11, 11), (1, 7, 16), (4, 8, 12), (3, 9, 12), (5, 7, 12), (6, 8, 10), (3, 3, 18), (5, 6, 13),
                  (2, 9, 13), (1, 5, 18), (5, 8, 11), (8, 8, 8), (2, 3, 19), (2, 10, 12), (1, 4, 19), (4, 5, 15),
                  (1, 11, 12), (3, 8, 13), (4, 9, 11), (2, 2, 20), (7, 8, 9), (1, 10, 13), (4, 6, 14), (6, 9, 9),
                  (3, 7, 14), (2, 8, 14), (1, 2, 21), (7, 7, 10), (1, 9, 14), (3, 6, 15), (5, 5, 14), (5, 9, 10)], 48
        tests.append((unionTuples(AT), NU))

        for i in range(randomTestCount):

            break

            newSeed = dtNow + datetime.timedelta(seconds=i)

            seed(newSeed)

            if verbose: print(f"random seed is {newSeed}")

            case = 0
            for A, NU in tests:

                case += 1

                iterCounter[0] = 0

                if verbose: print(f"case {case}", end=" ")

                t1 = time.perf_counter()

                partResult, reminder, optCount = partitionN(A, NU, 3, iterCounter)

                tt = round(time.perf_counter() - t1, 4)

                pIter = iterCounter[0]

                iterCounter[0] = 0

                t1 = time.perf_counter()

                partResultH, reminderH, optCountH = hybridPartitionN(A, NU, 3, iterCounter)

                htt = round(time.perf_counter() - t1, 4)

                hIter = iterCounter[0]

                if verbose:  print(f" time {tt}, hybrid {htt}, pIter = {pIter} hIter = {hIter}")

                if len(reminder) != 0 or len(partResult) != NU:

                    if verbose:
                        print(f"case {case}")
                        print(f"items {A}")
                        print(f"part result {partResult}")
                        print(f"part reminder  {reminder}")
                        print(f"optCount {optCount}")
                        print(f"len {len(A)}")
                        print(f"sum {sum(A)}")
                        print(f"iter {pIter}")

                    self.assertTrue(False)

                if len(reminderH) != 0 or len(partResultH) != NU:

                    if verbose:
                        print(f"case {case} hybrid")
                        print(f"items {A}")
                        print(f"part result {partResult}")
                        print(f"part reminder  {reminder}")
                        print(f"optCount {optCount}")
                        print(f"len {len(A)}")
                        print(f"sum {sum(A)}")
                        print(f"iter {hIter}")

                    self.assertTrue(False)

        seed(dtNow)

        if verbose:  print("6-partition problem for integer tests.")

        for i in range(randomTestCount):

            newSeed = dtNow + datetime.timedelta(seconds=i)

            seed(newSeed)

            if verbose:  print(f"random seed is {newSeed}")

            case = 0
            for A, NU in tests:

                case += 1

                iterCounter[0] = 0

                if verbose:  print(f"case {case}", end=" ")

                if NU % 6 != 0:
                    continue

                t1 = time.perf_counter()

                partResult, reminder, optCount = partitionN(A, NU // 2, 6, iterCounter)

                tt = round(time.perf_counter() - t1, 4)

                pIter = iterCounter[0]

                iterCounter[0] = 0

                t1 = time.perf_counter()

                partResultH, reminderH, optCountH = hybridPartitionN(A, NU // 2, 6, iterCounter)

                htt = round(time.perf_counter() - t1, 4)

                hIter = iterCounter[0]

                if verbose:  print(f" time {tt}, hybrid {htt}, pIter = {pIter} hIter = {hIter}")

                if len(reminder) != 0 or len(partResult) != NU // 2:

                    if verbose:
                        print(f"case {case}")
                        print(f"items {A}")
                        print(f"part result {partResult}")
                        print(f"part reminder  {reminder}")
                        print(f"optCount {optCount}")
                        print(f"len {len(A)}")
                        print(f"sum {sum(A)}")
                        print(f"iter {pIter}")

                    self.assertTrue(False)

                if len(reminderH) != 0 or len(partResultH) != NU // 2:

                    if verbose:
                        print(f"case {case} hybrid")
                        print(f"items {A}")
                        print(f"part result {partResult}")
                        print(f"part reminder  {reminder}")
                        print(f"optCount {optCount}")
                        print(f"len {len(A)}")
                        print(f"sum {sum(A)}")
                        print(f"iter {hIter}")

                    self.assertTrue(False)

        seed(dtNow)

        if verbose:  print("3-partition problem for rational numbers tests.")

        for i in range(randomTestCount):

            newSeed = dtNow + datetime.timedelta(0, i)

            seed(newSeed)

            if verbose:  print(f"random seed is {newSeed}", end="")

            case = 0
            for A, NU in tests:

                case += 1

                iterCounter[0] = 0

                if verbose:   print(f"case {case}", end=" ")

                decA = list(A)
                DecimalArray(decA)

                t1 = time.perf_counter()

                partResult, reminder, optCount = partitionN(decA, NU, 3, iterCounter)

                tt = round(time.perf_counter() - t1, 4)

                pIter = iterCounter[0]

                t1 = time.perf_counter()

                partResultH, reminderH, optCountH = hybridPartitionN(A, NU, 3, iterCounter)

                htt = round(time.perf_counter() - t1, 4)

                hIter = iterCounter[0]

                if verbose:  print(f" time {tt}, hybrid {htt}, pIter = {pIter} hIter = {hIter}")

                if len(reminder) != 0 or len(partResult) != NU:

                    if verbose:
                        print(f"case {case}")
                        print(f"items {A}")
                        print(f"part result {partResult}")
                        print(f"part reminder  {reminder}")
                        print(f"optCount {optCount}")
                        print(f"len {len(A)}")
                        print(f"sum {sum(A)}")
                        print(f"iter {pIter}")

                    self.assertTrue(False)

                if len(reminderH) != 0 or len(partResultH) != NU:

                    if verbose:
                        print(f"case {case} hybrid")
                        print(f"items {A}")
                        print(f"part result {partResult}")
                        print(f"part reminder  {reminder}")
                        print(f"optCount {optCount}")
                        print(f"len {len(A)}")
                        print(f"sum {sum(A)}")
                        print(f"iter {hIter}")

                    self.assertTrue(False)

    # NP complete: 1-0 knapsack for Silvano Martello and Paolo Toth 1990 tests.
    def test_6_Silvano_Paolo_1_0_knapsack(self):
        if verbose:   print("1-0 knapsack solver for Silvano Martello and Paolo Toth 1990 tests.")

        def testSilvano(W, V, R, c):
            iterCounter = [0]

            ws, vs = sortReverseBoth(W, V)

            expectedSV = 0
            expectedSW = 0

            ind = 0
            for i in R:
                if i == 1:
                    expectedSV += V[ind]
                    expectedSW += W[ind]
                ind += 1

            opt1, _, __, ___ = knapsack(c, ws, vs, iterCounter)
            opt2, _, __, ___ = knapsackNd(wPoint((c, c)), [wPoint((a, a)) for a in ws], vs, iterCounter)
            optP, _, __, ___ = paretoKnapsack(c, ws, vs, iterCounter)
            optPH, _, __, ___ = hybridParetoKnapsack(c, ws, vs, iterCounter)

            self.assertEqual(expectedSV, opt1)
            self.assertEqual(opt1, opt2)
            self.assertEqual(optP, opt1)
            self.assertEqual(optPH, opt1)

        # page 42. Example 2.3

        V = [50, 50, 64, 46, 50, 5]
        W = [56, 59, 80, 64, 75, 17]
        R = [1, 1, 0, 0, 1, 0]
        c = 190

        testSilvano(W, V, R, c)

        # page 47. Example 2.7

        V = [70, 20, 39, 37, 7, 5, 10]
        W = [31, 10, 20, 19, 4, 3, 6]
        R = [1, 0, 0, 1, 0, 0, 0]
        c = 50

        testSilvano(W, V, R, c)

    # NP weak: Equal-subset-sum knapsack for hardinstances_pisinger subset sum test dataset.
    # @unittest.skip("temp")
    def test_8_equal_subset_sum_files(self):
        if verbose:   print("Run equal-subset-sum knapsack for hardinstances_pisinger subset sum test dataset.")

        iterCounter = [0]

        with open(os.path.join(f"{out_dir}", "hardInst.subset.sum.all.perf.csv"), 'w', newline='') as csvfile:

            fieldnames = ['file', 'case', 'size', 'N', 'iter desc', 'iter non', 'iter h pareto desc',
                          'max iter expected', 'desc time', 'non time', 'desc h pareto time', 'best iter', 'best time',
                          'good']

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

                testFileName = os.path.join(test_data_dir, f"hardinstances_pisinger", f"{f}.csv")

                with open(testFileName, mode='r') as csvfile:
                    csvReader = csv.reader(csvfile, delimiter=',', quotechar='|')

                    for row in csvReader:

                        if len(row) == 0:
                            continue

                        if row[0] == "-----":

                            iterCounter[0] = 0

                            testCase.sort(reverse=True)

                            if verbose:  print(f"{f} case {caseNumber}", end=" ")

                            maxIter = 4 * (len(testCase) ** 3)

                            t1 = time.perf_counter()

                            optDesc, optItemsDesc = subsKnapsack(testKnapsack, testCase, iterCounter)

                            t2 = time.perf_counter()

                            descTime = (round(t2 - t1, 4), "desc")

                            t1Full = time.perf_counter()

                            rezIterDesc = iterCounter[0]

                            iterCounter[0] = 0

                            optDescFull, optItemsDescFull = subsKnapsack(testKnapsack, testCase, iterCounter)

                            self.assertEqual(optDescFull, optDesc)

                            descTimeFull = (round(time.perf_counter() - t1Full, 4), "desc full")

                            rezIterDescFull = iterCounter[0]

                            iterCounter[0] = 0

                            expS = sum(testExpected)

                            good = True

                            if optDesc < expS or optDesc > testKnapsack:
                                good = False
                                allGood = False
                                if verbose:
                                    print(
                                        f"ERROR: equal-subset-sum: DESC rez opt: {optDesc}, test opt: {testKnapsack}, test values: {expS}",
                                        end=" ")

                            if rezIterDesc > maxIter:
                                if verbose:
                                    print(f" DESC max iter exceeded: {maxIter} rez iter: {rezIterDesc}", end=" ")

                            nonSortTestCase = list(testCase)

                            shuffle(nonSortTestCase)

                            iterCounter[0] = 0

                            t5 = time.perf_counter()

                            optNonSort, optItemstNonSort = subsKnapsack(testKnapsack, nonSortTestCase, iterCounter)

                            t6 = time.perf_counter()

                            nonTime = (round(t6 - t5, 4), "non")

                            rezIterNon = iterCounter[0]

                            if optNonSort < expS or optNonSort > testKnapsack:
                                good = False
                                allGood = False
                                if verbose:
                                    print(
                                        f"ERROR: equal-subset-sum: NON sort rez opt: {optNonSort}, test opt: {testKnapsack}, test values: {expS}",
                                        end=" ")

                            if rezIterNon > 2 * maxIter:
                                if verbose:
                                    print(
                                        f"WARN: equal-subset-sum: NON sort  max iter exceeded: {2 * maxIter} rez iter: {rezIterNon}",
                                        end=" ")

                            iterCounter[0] = 0

                            t5 = time.perf_counter()

                            optDescSortH, optItemstDescSortH = subsParetoKnapsack(testKnapsack, testCase, iterCounter, printPct=False, doUseLimits=True)

                            t6 = time.perf_counter()

                            descHIter = iterCounter[0]

                            if optDescSortH < expS or optDescSortH > testKnapsack:
                                good = False
                                allGood = False
                                if verbose:
                                    print(
                                        f"ERROR: equal-subset-sum: DESC sort hybrid pareto  rez opt: {optDescSortH}, test opt: {testKnapsack}, test values: {expS}",
                                        end=" ")

                            if descHIter > maxIter:
                                if verbose:
                                    print(
                                        f"WARN: equal-subset-sum: DESC sort hybrid pareto  max iter exceeded: {2 * maxIter} rez iter: {descHIter}",
                                        end=" ")

                            descHTime = (round(t6 - t5, 4), "desc h pareto")

                            bestTime = min([descTime, nonTime, descHTime], key=lambda t: t[0])[1]

                            descIterItem = (rezIterDesc, "desc")
                            nonIterItem = (rezIterNon, "non")
                            descHIterItem = (descHIter, "desc h pareto")

                            bestIter = min([descIterItem, nonIterItem, descHIterItem], key=lambda t: t[0])[1]

                            if verbose:
                                print(   f" DESC {descTime[0]} NON {nonTime[0]} DESC FULL {descTimeFull[0]} DESC H PARETO {descHTime[0]}")

                            writer.writerow({'file': str(f), 'case': str(caseNumber), 'size': str(testKnapsack),
                                             'iter desc': str(rezIterDesc), 'iter non': str(rezIterNon),
                                             'iter h pareto desc': str(descHIter), 'max iter expected': str(maxIter),
                                             'N': str(len(testCase)), 'desc time': str(descTime[0]),
                                             'non time': str(nonTime[0]), 'desc h pareto time': str(descHTime[0]),
                                             'best iter': bestIter, 'best time': bestTime, 'good': str(good)})

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

                self.assertTrue(allGood)

    # NP complete: 1-0 knapsack for hardinstances_pisinger test dataset in case of integer and rational numbers.
    # @unittest.skip("temp")
    def test_8_knapsack_1_0_files(self):

        if verbose:
            print("Run 1-0 knapsack for hardinstances_pisinger test dataset in case of integer and rational numbers.")

        with open(os.path.join(f"{out_dir}", "hardInst.2d.perf.decimal.csv"), 'w', newline='') as csvfile:

            fieldnames = ['file', 'case', 'size', 'iter desc', 'iter non', 'iter pareto', 'max iter expected', 'N',
                          'desc time', 'non time', 'pareto time', 'best iter', 'best time', 'good']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()

            testCaseW = list()
            testCaseV = list()
            testExpected = list()
            testKnapsack = 0
            rowToSkip = 0

            # files = ["knapPI_11_20_1000", "knapPI_11_50_1000"]
            files = ["knapPI_11_20_1000", "knapPI_11_50_1000", "knapPI_11_100_1000", "knapPI_11_200_1000"]

            allGood = True

            for f in files:

                caseNumber = 1

                with open(os.path.join(test_data_dir, f"hardinstances_pisinger", f"{f}.csv"), mode='r') as csvfile:
                    spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')

                    for row in spamreader:

                        if len(row) == 0:
                            continue

                        if row[0] == "-----":

                            if verbose:
                                print(f"{f} case {caseNumber}", end=" ")

                            w, v = sortReverseBoth(testCaseW, testCaseV)

                            maxIter = 10 * (len(w) ** 3)

                            expS = sum(testExpected)

                            iterCounter = [0]

                            t1 = time.perf_counter()

                            optValDesc1, opt1Desc, optWeights1, optValues1 = knapsack(testKnapsack, w, v, iterCounter)

                            descTime = (round(time.perf_counter() - t1, 4), "desc")

                            rezIterDesc = iterCounter[0]

                            iterCounter = [0]

                            good = True

                            if optValDesc1 < expS or opt1Desc > testKnapsack:
                                good = False

                                if verbose:
                                    print(
                                        f"ERROR: 1-0:{caseNumber} DESC rez opt: {opt1Desc}, test size: {testKnapsack}, rez values: {optValDesc1},  test values: {expS}",
                                        end=" ")

                            tFull1 = time.perf_counter()

                            opt1ValDescFull, opt1DescFull, optWeights1Full, optValues1Full = \
                                knapsack(testKnapsack, w, v, iterCounter, doUseLimits=False)

                            self.assertEqual(opt1ValDescFull, optValDesc1)

                            descTimeFull = (round(time.perf_counter() - tFull1, 4), "desc full")

                            rezIterDesc = iterCounter[0]

                            if rezIterDesc > maxIter:
                                if verbose:
                                    print(
                                        f"WARN: 1-0: {caseNumber} max iter exceeded: {maxIter}  rez iter: {rezIterDesc}",
                                        end=" ")

                            iterCounter = [0]

                            t1 = time.perf_counter()

                            nTestKnapsack = wPoint((testKnapsack, testKnapsack))

                            opt2dValDesc, opt2dDesc, optWeights2dDesc, optValues2dDesc = \
                                knapsackNd(nTestKnapsack, [wPoint((a, a)) for a in w], v, iterCounter)

                            t2 = time.perf_counter()

                            rezIter2DDesc = iterCounter[0]

                            desc2dTime = (round(t2 - t1, 4), "desc")

                            if opt2dValDesc < expS or opt2dDesc > nTestKnapsack:
                                good = False

                                if verbose:
                                    print(
                                        f"ERROR: 1-0: {caseNumber}  DESC 2D rez opt: {opt2dDesc}, test size: {testKnapsack}, rez values: {opt2dValDesc},  test values: {expS}",
                                        end=" ")

                            iterCounter = [0]

                            if len(v) <= 20:

                                nonW, nonV = shuffleBoth(w, v)
                                t1 = time.perf_counter()

                                nTestKnapsack = wPoint((testKnapsack, testKnapsack))

                                opt2dValNon, opt2dNon, optWeights2dNon, optValues2dNon = \
                                    hybridKnapsackNd(nTestKnapsack,[wPoint((a, a))for a in nonW], nonV, iterCounter)

                                t2 = time.perf_counter()

                                rezIter2Dnon = iterCounter[0]

                                non2dTime = (round(t2 - t1, 4), "non")

                                if opt2dValNon < expS or opt2dNon > nTestKnapsack:
                                    good = False

                                    if verbose:
                                        print(
                                            f"ERROR: 1-0: {caseNumber}  ASC 2D rez opt: {opt2dNon}, test size: {testKnapsack}, rez values: {opt2dValNon},  test values: {expS}",
                                            end=" ")
                            else:
                                non2dTime = desc2dTime

                            iterCounter = [0]

                            t7 = time.perf_counter()

                            nonW, nonV = shuffleBoth(w, v)

                            optVal1Non, opt1Non, optWeightsNon, optValuesNon = knapsack(testKnapsack, nonW, nonV, iterCounter)

                            t8 = time.perf_counter()

                            nonTime = (round(t8 - t7, 4), "non")

                            rezIterNon = iterCounter[0]

                            if optVal1Non < expS or opt1Non > testKnapsack:
                                good = False

                                if verbose:
                                    print(
                                        f"ERROR: 1-0: {caseNumber} NON rez opt: {opt1Non}, test size: {testKnapsack}, rez weights: {optVal1Non},  test values: {expS}",
                                        end=" ")

                            iterCounter = [0]

                            t8 = time.perf_counter()

                            optValP, optP, optWeightsP, optValuesP = paretoKnapsack(testKnapsack, w, v, iterCounter)

                            t9 = time.perf_counter()

                            paretoTime = (round(t9 - t8, 4), "pareto")

                            if verbose:
                                print(
                                    f" INT DESC {descTime[0]} NON {nonTime[0]} DESC 2D {desc2dTime[0]} NON 2D {non2dTime[0]} DESC FULL {descTimeFull[0]} PARETO {paretoTime[0]}")

                            rezIterPareto = iterCounter[0]

                            if optValP < expS or optP > testKnapsack:
                                good = False

                                if verbose:
                                    print(
                                        f"ERROR: 1-0: {caseNumber} PARETO rez opt: {optP}, test size: {testKnapsack}, rez weights: {optValP},  test values: {expS}",
                                        end=" ")

                            bestTime = min([descTime, nonTime, paretoTime], key=lambda t: t[0])[1]

                            descIterItem = (rezIterDesc, "desc")
                            nonIterItem = (rezIterNon, "non")
                            paretoIterItem = (rezIterPareto, "pareto")

                            bestIter = min([descIterItem, nonIterItem, paretoIterItem], key=lambda t: t[0])[1]

                            decimalW = list(w)

                            DecimalArray(decimalW)

                            testKnapsackDecimal = DecimalData(testKnapsack)

                            iterCounter = [0]

                            t1 = time.perf_counter()

                            optValDec, optDec, optWeightsDec, optValuesDec = knapsack(testKnapsackDecimal, decimalW, v,
                                                                                      iterCounter)

                            t2 = time.perf_counter()

                            if verbose:
                                print(f" decimal desc dt {round(t2 - t1, 4)}")

                            if optValDec != optValDesc1 or optDec > testKnapsackDecimal:

                                good = False

                                if verbose:
                                    print(
                                        f"{caseNumber}  decimal values: {optValDec}, sum decimal w: {optDec}, test size: {testKnapsack}, test decimal size: {testKnapsackDecimal}, test values: {expS}",
                                        end=" ")

                            writer.writerow({'file': str(f), 'case': str(caseNumber), 'size': str(testKnapsack),
                                             'iter desc': str(rezIterDesc), 'iter non': str(rezIterNon),
                                             'iter pareto': str(round(rezIterPareto)),
                                             'max iter expected': str(maxIter), 'N': str(len(testCaseW)),
                                             'desc time': str(descTime[0]), 'non time': str(nonTime[0]),
                                             'pareto time': str(paretoTime[0]), 'best iter': bestIter,
                                             'best time': bestTime, 'good': str(good)})

                            if not good:
                                allGood = False

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

            self.assertTrue(allGood)

    # NP hard: multidimensional  N=100
    def test_8_multidimensional_100(self):

        lConstraint = 20789
        wConstraint = 23681
        greedyOptimumValue = 121105212
        actualOptima = 121147356
        dimensionMultiplier = 1000

        lwData100 = [[436, 1490, 649640], [232, 1320, 306240], [236, 932, 219952], [822, 638, 524436],
                     [1004, 1092, 1096368], [266, 1220, 324520], [632, 892, 563744], [1110, 344, 381840],
                     [598, 532, 318136], [658, 921, 606018], [732, 1830, 1339560], [822, 1740, 1430280],
                     [932, 1106, 1030792], [598, 732, 437736], [568, 1322, 750896], [1792, 1006, 1802752],
                     [1248, 746, 931008], [932, 892, 831344], [562, 1030, 578860], [722, 1720, 1241840],
                     [1526, 1448, 2209648], [1858, 2644, 4912552], [1726, 464, 800864], [928, 1672, 1551616],
                     [2028, 932, 1890096], [1028, 1636, 1681808], [756, 748, 565488], [926, 916, 848216],
                     [2006, 564, 1131384], [1028, 1894, 1947032], [1376, 1932, 2658432], [726, 1750, 1270500],
                     [2098, 946, 1984708], [1238, 1208, 1495504], [1026, 768, 787968], [1734, 932, 1616088],
                     [994, 2532, 2516808], [1966, 2422, 4761652], [2828, 1946, 5503288], [1536, 1788, 2746368],
                     [436, 732, 319152], [732, 822, 601704], [636, 932, 592752], [822, 598, 491556],
                     [1004, 568, 570272], [464, 794, 368416], [932, 648, 603936], [2110, 934, 1970740],
                     [598, 562, 336076], [656, 726, 476256], [926, 3726, 3450276], [1490, 1830, 2726700],
                     [1320, 1740, 2296800], [932, 2100, 1957200], [636, 732, 465552], [1094, 1324, 1448456],
                     [1222, 2408, 2942576], [894, 748, 668712], [548, 894, 489912], [532, 2138, 1137416],
                     [452, 642, 290184], [722, 1264, 912608], [924, 674, 622776], [824, 632, 520768],
                     [724, 936, 677664], [754, 446, 336284], [922, 316, 291352], [2002, 892, 1785784],
                     [576, 1932, 1112832], [726, 1750, 1270500], [1974, 944, 1863456], [1234, 1206, 1488204],
                     [1224, 766, 937584], [1734, 932, 1616088], [994, 2532, 2516808], [564, 2422, 1366008],
                     [722, 1944, 1403568], [1536, 788, 1210368], [648, 1232, 798336], [1024, 894, 915456],
                     [236, 248, 58528], [542, 126, 68292], [236, 542, 127912], [128, 128, 16384],
                     [1026, 2788, 2860488], [9098, 8726, 79389148], [5468, 3524, 19269232], [1264, 4524, 5718336],
                     [2354, 1298, 3055492], [1698, 2542, 4316316], [2542, 5004, 12720168], [582, 894, 520308],
                     [566, 894, 506004], [564, 1022, 576408], [1254, 2014, 2525556], [2012, 1254, 2523048],
                     [1256, 1298, 1630288], [2350, 2366, 5560100], [2502, 2502, 6260004], [1296, 2366, 3066336]]

        values = [p[2] for p in lwData100]
        items = [wPoint((p[0] * dimensionMultiplier, p[1] * dimensionMultiplier)) for p in lwData100]
        constraints = wPoint((lConstraint * dimensionMultiplier, wConstraint * dimensionMultiplier))

        if verbose:  print(f"multidimensional N={len(values)} knapsack test")

        iterCounter = [0]

        from flags.flags import printPct, doUseLimits, doSolveSuperInc

        t1 = time.perf_counter()

        solver = knapsackNSolver(constraints, items, values, iterCounter, wPoint([0] * constraints.getSize()),
                                 forceUseLimits=False)

        solver.forceUseDpSolver = False
        solver.useParetoAsNGreedySolver = True
        solver.printInfo = printPct
        solver.doSolveSuperInc = doSolveSuperInc
        solver.doUseLimits = doUseLimits
        solver.useRatioSortForPareto = True
        solver.printDpInfo = False
        solver.printGreedyInfo = verbose
        solver.printSuperIncreasingInfo = verbose

        bestValue, bestSize, bestItems, bestValues = solver.solve()

        opt, optDims, optItems, optValues = bestValue, bestSize, bestItems, bestValues

        if verbose:
            print(
                f"hybridKnapsackNd: total val: {opt} opt: {optDims}, testOpt: {greedyOptimumValue} iter: {round(iterCounter[0])}, time: {time.perf_counter() - t1}, items: {optItems}")

        self.assertTrue(opt >= greedyOptimumValue and optDims <= constraints)

    def test_3_search_index(self):

        if verbose:
            print(f"test building and using max profit point index")

        mixDimData = [(821, 100),
                      (1144, 100),
                      (634, 100),
                      (701, 100),
                      (291, 100),
                      (1702, 100),
                      (1633, 100),
                      (1086, 100),
                      (124, 100),
                      (718, 100),
                      (976, 100),
                      (1438, 100),
                      (822, 100),
                      (1143, 100),
                      (640, 100),
                      (702, 100),
                      (291, 100),
                      (1702, 100),
                      (1633, 100),
                      (2000, 100),
                      (100, 100),
                      (701, 100),
                      (1976, 100),
                      (1638, 100),
                      ]

        dimsd = [p[0] for p in mixDimData]
        values = [p[1] for p in mixDimData]

        descDims, descValues = sortReverseBoth(dimsd, values)

        sumOfAll = sum([p[0] for p in mixDimData])
        minItem = min([p[0] for p in mixDimData])
        iterCounter = [0]

        descPoints = [wPoint1(d) for d in descDims]

        indexConstraints = [ sumOfAll, sumOfAll // 2]

        for indexConstr in indexConstraints:

            for s in range(1, 3):

                testDescValues = list(descValues)

                sameProfit = s % 2 == 0

                if not sameProfit:
                    testDescValues[0] -= 1

                for j in range(1, 3):

                    forceUsePareto = j % 2 == 0

                    binSearchSolver = knapsackParetoSolver(descPoints, testDescValues, range(len(testDescValues)), wPoint1(indexConstr - 1), paretoPoint1(0, 0), wPoint1(0), iterCounter)

                    binSearchSolver.prepareSearchIndex = True

                    binSearchSolver.forceUsePareto = forceUsePareto

                    binSearchSolver.solve()

                    for constraint in range(minItem, indexConstr, minItem - 1):

                        constraintPoint = wPoint1(constraint)

                        fullSolver = knapsackParetoSolver(descPoints, testDescValues, range(len(testDescValues)), constraintPoint, paretoPoint1(0, 0), wPoint1(0), iterCounter)

                        opt, optSize, optItems, optValues, optIndex = fullSolver.solve()

                        testOpt, testOptSize, testOptItems, testOptValues, testOptIndex = binSearchSolver.solve(constraintPoint)

                        good = opt == testOpt and testOptSize <= constraintPoint

                        if verbose:
                            print(f"test_3_search_index: indexConstr={indexConstr}; constraint={constraint}; forceUsePareto={forceUsePareto}; sameProfit={sameProfit}; expected - optimized: {opt - testOpt}")

                        self.assertTrue(good)
