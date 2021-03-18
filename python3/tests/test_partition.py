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

from random import shuffle, randint, seed, sample

import unittest
import datetime
import time
import math
import csv
import os

from flags.flags import verbose
from tests import randomTestCount, dtNow, script_dir, out_dir, try_redirect_out, restore_out
from tests.tAPI import partitionN, hybridPartitionN


class PartitionTests(unittest.TestCase):

    def setUp(self):
        try_redirect_out("partition", self._testMethodName)

    def tearDown(self):
        restore_out()

    # NP complete: N equal-subset-sum tests.
    # @unittest.skip("temp")
    def test_n_equal_subset_sum_integer(self):

        if verbose:
            print("N equal-subset-sum integer tests.")

        iterCounter = [0]

        tests = []

        A, NU = [3, 383, 401, 405, 580, 659, 730, 1024, 1100, 1175, 1601, 2299, 3908, 4391, 4485, 5524], 4
        tests.append((A, NU))
        A, NU = [4, 5, 3, 2, 5, 5, 5, 1, 5, 5, 5, 5, 3, 5, 5, 2], 13
        tests.append((A, NU))
        A, NU = [4, 4, 6, 2, 3, 8, 10, 2, 10, 7], 4
        tests.append((A, NU))
        A, NU = [4, 15, 1, 1, 1, 1, 3, 11, 1, 10], 3
        tests.append((A, NU))
        A, NU = [20, 23, 25, 49, 45, 27, 40, 22, 19], 3
        tests.append((A, NU))
        A, NU = [20, 23, 25, 49, 45, 27, 40, 22, 19, 20, 23, 25, 49, 45, 27, 40, 22, 19], 6
        tests.append((A, NU))
        A, NU = [27, 9, 9, 9, 9, 9, 3, 3, 3], 3
        tests.append((A, NU))
        A, NU = [10, 10, 10, 7, 7, 7, 7, 7, 7, 6, 6, 6], 3
        tests.append((A, NU))
        A, NU = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 3
        tests.append((A, NU))
        A, NU = [10, 12, 1, 2, 10, 7, 5, 19, 13, 1], 4
        tests.append((A, NU))
        A, NU = [1, 2, 3, 4, 5, 6, 7, 8, 9], 3
        tests.append((A, NU))
        A, NU = [780, 935, 2439, 444, 513, 1603, 504, 2162, 432, 110, 1856, 575, 172, 367, 288, 316], 4
        tests.append((A, NU))
        # https://web.stanford.edu/class/archive/cs/cs103/cs103.1132/lectures/27/Small27.pdf
        A, NU = [13, 137, 56, 42, 103, 58, 271], 2
        tests.append((A, NU))
        A, NU = list(range(1, 100)), 3
        tests.append((A, NU))
        # http://people.brunel.ac.uk/~mastjjb/jeb/orlib/files/bills_snowflake.txt
        A, NU = [1, 62, 34, 38, 39, 43, 62, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82,
                 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106,
                 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119], 3
        tests.append((A, NU))
        A, NU = [1, 156, 2, 3, 4, 350, 427, 428, 429, 430, 431, 432, 433, 434, 435, 436, 437, 438, 439, 440, 441, 442,
                 443, 444, 445, 446, 447, 448, 449, 450, 451, 452, 453, 454, 455, 456, 457, 458, 459, 460, 461, 462,
                 463, 464, 465, 466, 467, 468, 469, 470, 471, 472, 473, 474, 475, 476, 477, 478, 479, 480, 481, 482,
                 483, 484, 485, 486, 487, 488, 489, 490, 491, 492, 493, 494, 495, 496, 497, 498, 499, 500, 501, 502,
                 503, 504, 505, 506, 507, 508, 509, 510, 511, 512, 513, 514, 515, 516, 517, 518, 519, 520, 521, 522,
                 523, 524, 525, 526, 527, 528, 529, 530, 531, 532, 533, 534, 535, 536, 537, 538, 539, 540, 541, 542,
                 543, 544, 545, 546, 547, 548, 549, 550, 551, 552, 553, 554, 555, 556, 557, 558, 559, 560, 561, 562,
                 563, 564, 565, 566, 567, 568, 569, 570, 571, 572, 573, 574, 575, 576, 577, 578], 3
        tests.append((A, NU))
        A, NU = list(range(1, (81 * 9) + 1)), 3
        tests.append((A, NU))

        for i in range(randomTestCount):

            newSeed = dtNow + datetime.timedelta(seconds=i)

            seed(newSeed)

            if verbose:
                print(f"random seed is {newSeed}")

            case = 0

            for A, NU in tests:

                case += 1

                iterCounter[0] = 0

                if verbose:
                    print(f"case {case}", end=" ")

                t1 = time.perf_counter()

                partResult, reminder, optCount = partitionN(A, NU, 0, iterCounter)

                tt = round(time.perf_counter() - t1, 4)

                print(f" time {tt}")

                if len(reminder) != 0 or len(partResult) != NU:

                    if verbose:
                        print(f"case {case}")
                        print(f"items {A}")
                        print(f"part result {partResult}")
                        print(f"part reminder  {reminder}")
                        print(f"optCount {optCount}")
                        print(f"len {len(A)}")
                        print(f"sum {sum(A)}")
                        print(f"iter {iterCounter[0]}")

                    self.assertTrue(False)

        seed(dtNow)

        if verbose:
            print("N equal-subset-sum rational numbers tests.")

        for i in range(randomTestCount):

            newSeed = dtNow + datetime.timedelta(seconds=i)

            seed(newSeed)

            if verbose:
                print(f"random seed is {newSeed}")

            case = 0

            for A, NU in tests:

                break

                case += 1

                iterCounter[0] = 0

                if verbose:
                    print(f"case {case}", end=" ")

                decA = list(A)

                DecimalArray(decA)

                t1 = time.perf_counter()

                partResult, reminder, optCount = partitionN(decA, NU, 0, iterCounter)

                tt = round(time.perf_counter() - t1, 4)

                print(f" time {tt}")

                if len(reminder) != 0 or len(partResult) != NU:

                    if verbose:
                        print(f"case {case}")
                        print(f"items {A}")
                        print(f"part result {partResult}")
                        print(f"part reminder  {reminder}")
                        print(f"optCount {optCount}")
                        print(f"len {len(A)}")
                        print(f"sum {sum(A)}")
                        print(f"iter {iterCounter[0]}")

                    self.assertTrue(False)

    # NP weak: N equal-subset-sum using integer partition generator.
    # @unittest.skip("temp")
    def test_n_equal_subset_sum_using_integer_partition_generator(self):

        def generate_partition(number, limitCount):
            answer = set()
            answer.add((number,))
            for x in range(number - 1, 0, -1):
                for y in generate_partition(number - x, limitCount):
                    answer.add(tuple(sorted((x,) + y)))
                    if len(answer) >= limitCount:
                        return answer
            return answer

        if verbose:
            print("N equal-subset-sum using integer partition generator.")

        with open(os.path.join(f"{out_dir}", "partition.perf.over.intpart.csv"), 'w', newline='') as csvfile:

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

                        iterCounter = [0]

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
                                print(
                                    f"item = {item}, case i {i}, case part limit {partLimit}, n = {len(subSet)}, partition {partition} ",
                                    end="")

                            t1 = time.perf_counter()

                            partResult, resultReminder, optCount = partitionN(subSet, partition, 0, iterCounter)

                            t2 = time.perf_counter()

                            if verbose:
                                print(f"iter {round(iterCounter[0])}, optimizations {optCount}, dt {t2 - t1}")

                            resultPart = len(partResult)

                            rezSum = 0
                            for sub in partResult:
                                rezSum += sum(sub.Items)

                            good = True

                            if resultPart < partition or rezSum != expectedSum or len(resultReminder) > 0:
                                allGood = False

                                good = False

                                badItems.append((item, i))

                                sumRem = sum(resultReminder.Items)

                                print(
                                    f"ERROR: integer partiton: item = {item}, case i {i}, case part limit {partLimit}, n = {len(subSet)}, rezult partition {resultPart}, expected partition {partition}, rez sum {rezSum}, total sum {rezSum + sumRem}, expected sum {expectedSum} , iter {round(iterCounter[0])}")

                            writer.writerow({'item': str(item), 'case': str(i), 'limit': str(partLimit),
                                             'partition': str(partition), 'N': str(len(subSet)),
                                             'optimizations': str(optCount), 'iter': str(round(iterCounter[0])),
                                             'max iter': str(((partition) ** 3) * ((len(subSet) // partition) ** 4)),
                                             'good': str(good)})

                            if not allGood:
                                break

            if len(badItems) > 0:
                print(badItems)

            self.assertTrue(allGood)


    # NP hard: integer partition optimization tests. randomTestCount * 200
    # @unittest.skip("temp")
    def test_integer_partition_optimization(self):

        if verbose:
            print("NP hard partition optimization integer tests.")

        iterCounter = [0]
        tests = []

        A, NU = [3, 383, 401, 405, 580, 659, 730, 1024, 1100, 1175, 1601, 2299, 3908, 4391, 4485, 5524], 4
        tests.append((A, NU))
        A, NU = [4, 5, 3, 2, 5, 5, 5, 1, 5, 5, 5, 5, 3, 5, 5, 2], 13
        tests.append((A, NU))
        A, NU = [4, 4, 6, 2, 3, 8, 10, 2, 10, 7], 4
        tests.append((A, NU))
        A, NU = [4, 15, 1, 1, 1, 1, 3, 11, 1, 10], 3
        tests.append((A, NU))
        A, NU = [20, 23, 25, 49, 45, 27, 40, 22, 19], 3
        tests.append((A, NU))
        A, NU = [20, 23, 25, 49, 45, 27, 40, 22, 19, 20, 23, 25, 49, 45, 27, 40, 22, 19], 6
        tests.append((A, NU))
        A, NU = [27, 9, 9, 9, 9, 9, 3, 3, 3], 3
        tests.append((A, NU))
        A, NU = [10, 10, 10, 7, 7, 7, 7, 7, 7, 6, 6, 6], 3
        tests.append((A, NU))
        A, NU = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 3
        tests.append((A, NU))
        A, NU = [10, 12, 1, 2, 10, 7, 5, 19, 13, 1], 4
        tests.append((A, NU))
        A, NU = [1, 2, 3, 4, 5, 6, 7, 8, 9], 3
        tests.append((A, NU))

        for i in range(randomTestCount * 200):

            newSeed = dtNow + datetime.timedelta(seconds=i)

            seed(newSeed)

            if verbose:
                print(f"random seed is {newSeed}")

            case = 0

            for A, NU in tests:

                case += 1

                iterCounter[0] = 0

                if verbose:
                    print(f"case {case} ", end="")

                testCase = list(A)

                size = sum(A) // NU

                singleTestSizes = []

                for i in range(NU):
                    singleTestSizes.append(size)

                reminderItemCnt = randint(1, len(A))

                minI, maxI = max(min(A) + 1, 1), max(max(A) - 1, 1)

                minI, maxI = min(minI, maxI), max(minI, maxI)

                sampleList = list(range(minI, maxI))

                reminderItems = sample(sampleList, min(len(sampleList), reminderItemCnt))

                testCase += reminderItems

                t1 = time.perf_counter()

                partResult, reminder, optCount = partitionN(testCase, singleTestSizes, 0, iterCounter, 1000)

                tt = round(time.perf_counter() - t1, 4)

                pIter = iterCounter[0]

                iterCounter[0] = 0

                t1 = time.perf_counter()

                partResultH, reminderH, optCountH = hybridPartitionN(testCase, singleTestSizes, 0, iterCounter, 1000)

                htt = round(time.perf_counter() - t1, 4)

                hIter = iterCounter[0]

                if verbose:
                    print(
                        f" time {tt}, hybrid time {htt}, opt count {optCount}, hybrid opt count {optCountH}, pIter={pIter}, hIter = {hIter}")

                optD = NU - len(partResult)

                if len(reminder) == 0 or optD > 0:

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

                optDH = NU - len(partResultH)

                if len(reminderH) == 0 or optDH > 0:

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

    # NP complete: Multiple knapsack sizes integer tests.
    # @unittest.skip("temp")
    def test_multiple_knapsack_sizes(self):

        if verbose:
            print("Multiple knapsack sizes integer tests.")

        mksTests = []

        A, NU = [3, 383, 401, 405, 580, 659, 730, 1024, 1100, 1175, 1601, 2299, 3908, 4391, 4485, 5524], 4
        mksTests.append((A, NU))
        A, NU = [4, 5, 3, 2, 5, 5, 5, 1, 5, 5, 5, 5, 3, 5, 5, 2], 13
        mksTests.append((A, NU))
        A, NU = [4, 4, 6, 2, 3, 8, 10, 2, 10, 7], 4
        mksTests.append((A, NU))
        A, NU = [4, 15, 1, 1, 1, 1, 3, 11, 1, 10], 3
        mksTests.append((A, NU))
        A, NU = [20, 23, 25, 49, 45, 27, 40, 22, 19], 3
        mksTests.append((A, NU))
        A, NU = [20, 23, 25, 49, 45, 27, 40, 22, 19, 20, 23, 25, 49, 45, 27, 40, 22, 19], 6
        mksTests.append((A, NU))
        A, NU = [27, 9, 9, 9, 9, 9, 3, 3, 3], 3
        mksTests.append((A, NU))
        A, NU = [10, 10, 10, 7, 7, 7, 7, 7, 7, 6, 6, 6], 3
        mksTests.append((A, NU))
        A, NU = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 3
        mksTests.append((A, NU))
        A, NU = [10, 12, 1, 2, 10, 7, 5, 19, 13, 1], 4
        mksTests.append((A, NU))
        A, NU = [1, 2, 3, 4, 5, 6, 7, 8, 9], 3
        mksTests.append((A, NU))

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

        iterCounter = [0]

        shuffle(singleTest)
        shuffle(singleTestSizes)

        for i in range(randomTestCount):

            newSeed = dtNow + datetime.timedelta(seconds=i)

            seed(newSeed)

            if verbose:
                print(f"random seed is {newSeed}")

            t1 = time.perf_counter()

            partResult, reminder, optCount = partitionN(singleTest, singleTestSizes, 0, iterCounter)

            tt = round(time.perf_counter() - t1, 4)

            pIter = iterCounter[0]

            iterCounter[0] = 0

            if len(reminder) != 0:

                if verbose:
                    print(f"items {A}")
                    print(f"part result {partResult}")
                    print(f"part reminder  {reminder}")
                    print(f"optCount {optCount}")
                    print(f"len {len(A)}")
                    print(f"sum {sum(A)}")
                    print(f"iter {pIter}")

                assert False

            t1 = time.perf_counter()

            partResultH, reminderH, optCountH = hybridPartitionN(singleTest, singleTestSizes, 0, iterCounter)

            htt = round(time.perf_counter() - t1, 4)

            hIter = iterCounter[0]

            print(f" time {tt}, hybrid {htt}, pIter = {pIter} hIter = {hIter}")

            if len(reminderH) != 0:

                if verbose:
                    print(f"items {A}")
                    print(f"part result {partResult}")
                    print(f"part reminder  {reminder}")
                    print(f"optCount {optCount}")
                    print(f"len {len(A)}")
                    print(f"sum {sum(A)}")
                    print(f"iter {hIter}")

                self.assertTrue(False)

        seed(dtNow)
