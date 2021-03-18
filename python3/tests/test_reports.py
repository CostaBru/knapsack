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

import unittest
from datetime import datetime, timedelta
from random import random, sample, randint
import time

from tAPI import *
from flags.flags import verbose
from tests import dtNow, try_redirect_out, restore_out
from tests.helpers import sortReverseBoth


class ReportsTests(unittest.TestCase):

    def setUp(self):
        try_redirect_out("reports", self._testMethodName)

    def tearDown(self):
        restore_out()

    # KB knapsacks and pareto reports for [1] * 50
    # @unittest.skip("temp")
    def test_knapsacks_and_pareto_1_50(self):

        if verbose:
            print("KB knapsacks and pareto reports for [1] * 50")

        numbers = [1] * 50

        if verbose:
            print(f"len {len(numbers)} sum {sum(numbers)}")

        if True:

            iterCounter = [0]

            prevIters = 0
            prevPareto = 0

            if True:

                s = sum(numbers) - 1

                iterCounter[0] = 0

                t1 = time.perf_counter()

                opt1, optItems1 = subsKnapsack(s, numbers, iterCounter, printPct=True)

                subsTime = time.perf_counter() - t1

                o1 = round(iterCounter[0])

                iterCounter[0] = 0

                t1 = time.perf_counter()

                opt2, optDim2, optItems2, optVal2 = knapsack(s, numbers, numbers, iterCounter, printPct=True)

                knapTime = time.perf_counter() - t1

                o2 = round(iterCounter[0])

                iterCounter[0] = 0

                t1 = time.perf_counter()

                opt3, optDim3, optItems3, optVal3 = paretoKnapsack(s, numbers, numbers, iterCounter, printPct=True)

                paretoTime = time.perf_counter() - t1

                oP = round(iterCounter[0])

                iterCounter[0] = 0

                t1 = time.perf_counter()

                opt4, optDim4, optItems4, optVal4 = hybridParetoKnapsack(s, numbers, numbers, iterCounter, printPct=True)

                paretoHTime = time.perf_counter() - t1

                oH = round(iterCounter[0])

                if opt1 != opt2 or opt2 != opt3 or opt1 != opt4:
                    print(f"ERROR: {opt1} - {opt2} - {opt3} - {opt4}, size {s}")
                    self.assertTrue(False)

                prevIters = o1
                prevPareto = o2

    # KB knapsacks and pareto reports for ([1] * 25) + ([2] * 25)
    # @unittest.skip("temp")
    def test_knapsacks_and_pareto_1_25_2_25(self):
        if verbose:
            print("KB knapsacks and pareto reports for ([1] * 25) + ([2] * 25)")

        numbers = ([1] * 25) + ([2] * 25)

        if verbose:
            print(f"len {len(numbers)} sum {sum(numbers)}")

        if True:

            iterCounter = [0]

            prevIters = 0
            prevPareto = 0

            if True:

                s = sum(numbers) - 1

                iterCounter[0] = 0

                opt, optItems1 = subsKnapsack(s, numbers, iterCounter, printPct=True)

                o1 = round(iterCounter[0])

                iterCounter[0] = 0

                t1 = time.perf_counter()

                opt2, optDim2, optItems2, optVal3 = knapsack(s, numbers, numbers, iterCounter, printPct=True)

                knapTime = time.perf_counter() - t1

                o2 = round(iterCounter[0])

                iterCounter[0] = 0

                opt3, optDim3, optItems3, optVal3 = paretoKnapsack(s, numbers, numbers, iterCounter, printPct=True)

                o2 = round(iterCounter[0])

                iterCounter[0] = 0

                t1 = time.perf_counter()

                opt4, optDim4, optItems4, optVal4 = hybridParetoKnapsack(s, numbers, numbers, iterCounter, printPct=True)

                paretoHTime = time.perf_counter() - t1

                oH = round(iterCounter[0])

                if opt != opt2 or opt != opt3 or opt4 != opt:
                    print(f"ERROR: {opt} - {opt2} - {opt3} - {opt4}, size {s}")
                    self.assertTrue(False)

                prevIters = o1
                prevPareto = o2

    # KB knapsacks and pareto reports for list(range(1, 51))
    # @unittest.skip("temp")
    def test_knapsacks_and_pareto_range_1_50(self):

        if verbose:
            print("KB knapsacks and pareto reports for list(range(1, 51))")

        numbers = list(range(1, 51))

        if verbose:
            print(f"len {len(numbers)} sum {sum(numbers)}")

        if True:

            iterCounter = [0]

            prevIters = 0
            prevPareto = 0

            if True:

                s = sum(numbers) - 1

                iterCounter[0] = 0

                opt, optItems1 = subsKnapsack(s, numbers, iterCounter, printPct=True)

                print(s)

                o1 = round(iterCounter[0])

                iterCounter[0] = 0

                t1 = time.perf_counter()

                opt2, optDim2, optItems2, optVal3 = knapsack(s, numbers, numbers, iterCounter, printPct=True)

                knapTime = time.perf_counter() - t1

                o2 = round(iterCounter[0])

                iterCounter[0] = 0

                opt3, optDim3, optItems3, optVal3 = paretoKnapsack(s, numbers, numbers, iterCounter, printPct=True)

                o3 = round(iterCounter[0])

                iterCounter[0] = 0

                t1 = time.perf_counter()

                opt4, optDim4, optItems4, optVal4 = hybridParetoKnapsack(s, numbers, numbers, iterCounter, printPct=True)

                paretoHTime = time.perf_counter() - t1

                oH = round(iterCounter[0])

                if opt != opt2 or opt != opt3 or opt4 != opt:
                    print(f"ERROR: {opt} - {opt2} - {opt3} - {opt4}, size {s}")
                    self.assertTrue(False)

                prevIters = o1
                prevPareto = o2

    # KB knapsacks and pareto reports for random.sample(range(1, 1000), 50)
    # @unittest.skip("temp")
    def test_knapsacks_and_pareto_random_1_1000_50(self):

        if verbose:
            print("KB knapsacks and pareto reports for random.sample(range(1, 1000), 50)")

        numbers = sample(range(1, 1000), 50)
        numbers.sort(reverse=False)

        if verbose:
            print(f"len {len(numbers)} sum {sum(numbers)}")

        if True:
            iterCounter = [0]

            prevIters = 0
            prevPareto = 0

            if True:

                s = sum(numbers) - 1

                iterCounter[0] = 0

                opt, optItems1 = subsKnapsack(s, numbers, iterCounter, printPct=True)

                print(s)

                o1 = round(iterCounter[0])

                iterCounter[0] = 0

                t1 = time.perf_counter()

                opt2, optDim2, optItems2, optVal3 = knapsack(s, numbers, numbers, iterCounter, printPct=True)

                knapTime = time.perf_counter() - t1

                o2 = round(iterCounter[0])

                iterCounter[0] = 0

                opt3, optDim3, optItems3, optVal3 = paretoKnapsack(s, numbers, numbers, iterCounter, printPct=True)

                o3 = round(iterCounter[0])

                iterCounter[0] = 0

                t1 = time.perf_counter()

                opt4, optDim4, optItems4, optVal4 = hybridParetoKnapsack(s, numbers, numbers, iterCounter, printPct=True)

                paretoHTime = time.perf_counter() - t1

                oH = round(iterCounter[0])

                if opt != opt2 or (opt != opt3) or opt4 != opt:
                    print(f"ERROR: {opt} - {opt2} - {opt3} - {opt4}size {s}")
                    self.assertTrue(False)

                prevIters = o1
                prevPareto = o2

    # KB knapsacks and pareto reports for random.sample(range(1, 10000000000000000), 10)
    # @unittest.skip("temp")
    def test_knapsacks_and_pareto_random_1_10000000000000000_10(self):

        if verbose:
            print("KB knapsacks and pareto reports for random.sample(range(1, 10000000000000000), 10)")

        numbers = sample(range(1, 10000000000000000), 10)
        numbers.sort()

        if verbose:
            print(f"len {len(numbers)} sum {sum(numbers)}")

        for i in range(10):

            newSeed = dtNow + timedelta(seconds=i)

            iterCounter = [0]

            prevIters = 0
            prevPareto = 0

            if True:

                s = sum(numbers) - 1

                iterCounter[0] = 0

                opt, optItems1 = subsKnapsack(s, numbers, iterCounter, printPct=True)

                print(s)

                o1 = round(iterCounter[0])

                iterCounter[0] = 0

                t1 = time.perf_counter()

                opt2, optDim2, optItems2, optVal3 = knapsack(s, numbers, numbers, iterCounter, printPct=True)

                knapTime = time.perf_counter() - t1

                o2 = round(iterCounter[0])

                iterCounter[0] = 0

                opt3, optDim3, optItems3, optVal3 = paretoKnapsack(s, numbers, numbers, iterCounter, printPct=True)

                o3 = round(iterCounter[0])

                iterCounter[0] = 0

                t1 = time.perf_counter()

                opt4, optDim4, optItems4, optVal4 = hybridParetoKnapsack(s, numbers, numbers, iterCounter, printPct=True)

                paretoHTime = time.perf_counter() - t1

                oH = round(iterCounter[0])

                if opt != opt2 or (opt != opt3) or opt4 != opt:
                    print(f"ERROR: {opt} - {opt2} - {opt3} - {opt4}, size {s}, numbers: {numbers}")
                    self.assertTrue(False)

                prevIters = o1
                prevPareto = o2

    # KB knapsacks and pareto reports for geometric progression numbers = [10000] * 10; numbers[i] *= (int(numbers[i - 1] * 2) - 1)
    # @unittest.skip("temp")
    def test_knapsacks_and_pareto_geometric_progression_10(self):

        if verbose:
            print(
                "KB knapsacks and pareto reports for geometric progression numbers = [10000] * 10; numbers[i] *= (int(numbers[i - 1] * 2) - 1)")

        numbers = [10000] * 10

        for i in range(1, 10):
            numbers[i] = (int(numbers[i - 1] * 2) - 1)

        numbers.append(numbers[len(numbers) // 2])

        numbers.sort()

        if verbose:
            print("len " + str(len(numbers)))
            print("sum " + str(sum(numbers)))

        if True:

            iterCounter = [0]

            prevIters = 0
            prevPareto = 0

            if True:
                s = sum(numbers) - 1

                iterCounter[0] = 0

                opt1, optItems1 = subsKnapsack(s, numbers, iterCounter, printPct=True)

                o1 = round(iterCounter[0])

                print(o1)

                iterCounter[0] = 0

                t1 = time.perf_counter()

                opt2, optDim2, optItems2, optVal3 = knapsack(s, numbers, numbers, iterCounter, printPct=True)

                knapTime = time.perf_counter() - t1

                o2 = round(iterCounter[0])

                iterCounter[0] = 0

                opt3, optDim3, optItems3, optVal3 = paretoKnapsack(s, numbers, numbers, iterCounter, printPct=True)

                o3 = round(iterCounter[0])

                iterCounter[0] = 0

                t1 = time.perf_counter()

                opt4, optDim4, optItems4, optVal4 = hybridParetoKnapsack(s, numbers, numbers, iterCounter, printPct=True)

                paretoHTime = time.perf_counter() - t1

                oH = round(iterCounter[0])

                if opt1 != opt2 or opt1 != opt3 or opt4 != opt1:
                    print(f"ERROR: {opt1} - {opt2} - {opt3} - {opt4}, size {s}")
                    self.assertTrue(False)

                prevIters = o1
                prevPareto = o2

    # KB knapsacks and pareto reports for geometric progression numbers = [1] * 10; numbers[i] *= (int(numbers[i - 1] * 2) - 1); values are random in [1..1000]
    # @unittest.skip("temp")
    def test_knapsacks_and_pareto_geometric_progression_10_values_random(self):
        if verbose:
            print(
                "reports for geometric progression numbers = [1] * 10; numbers[i] *= (int(numbers[i - 1] * 2) - 1); values are random in [1..1000]")

        numbers = [1000] * 10
        values = [1] * 10

        for i in range(1, 10):
            numbers[i] = (int(numbers[i - 1] * 2) - 1)
            values[i] = randint(1, 1000)

        if verbose:
            print(f"len {len(numbers)}")
            print(f"sum {sum(numbers)}")

        if True:

            iterCounter = [0]

            if True:

                sumCases = [(sum(numbers) // 2) - 1, ((sum(numbers) // 4) * 3 - 1), sum(numbers) - 1, ]

                for s in sumCases:

                    print(f"case size {s}")

                    iterCounter[0] = 0

                    opt3, optDim3, optItems3, optVal3 = paretoKnapsack(s, numbers, values, iterCounter, printPct=True)

                    o3 = round(iterCounter[0])

                    iterCounter[0] = 0

                    t1 = time.perf_counter()

                    opt2, optDim2, optItems2, optVal2 = knapsack(s, numbers, values, iterCounter, printPct=True)

                    knapTime = time.perf_counter() - t1

                    o2 = round(iterCounter[0])

                    iterCounter[0] = 0

                    t1 = time.perf_counter()

                    opt4, optDim4, optItems4, optVal4 = hybridParetoKnapsack(s, numbers, values, iterCounter, printPct=True)

                    paretoHTime = time.perf_counter() - t1

                    oH = round(iterCounter[0])

                    if opt2 != opt3 or opt4 != opt2:
                        print(f"ERROR: {opt2} - {opt3} - {opt4}, size {s}, numbers: {numbers}, values = {values}")
                        self.assertTrue(False)

    # Exponential: reports KB NU for geometric progression numbers and values, non equals case
    # @unittest.skip("temp")
    def test_knapsacks_and_pareto_geometric_progression_random_non_equals_case(self):

        if verbose:
            print("reports KB NU for geometric progression numbers and values, non equals case")

        numbers = [1000] * 10
        values = [1000] * 10

        for i in range(1, 10):
            numbers[i] = (int(numbers[i - 1] * 2) - 1)
            values[i] = (int(numbers[i - 1] * 2) - 2)

        numbers.append(numbers[len(numbers) // 2])
        values.append(values[len(values) // 2])

        numbers, values = sortReverseBoth(numbers, values, reverse=False)

        if verbose:
            print(f"len {len(numbers)}")
            print(f"sum {sum(numbers)}")

        if True:

            iterCounter = [0]

            if True:

                sumCases = [(sum(numbers) // 2) - 1, ((sum(numbers) // 4) * 3 - 1), sum(numbers) - 1, ]

                for s in sumCases:

                    print(f"case size {s}")

                    iterCounter[0] = 0

                    opt3, optDim3, optItems3, optVal3 = paretoKnapsack(s, numbers, values, iterCounter, printPct=True)

                    o3 = round(iterCounter[0])

                    iterCounter[0] = 0

                    t1 = time.perf_counter()

                    opt2, optDim2, optItems2, optVal2 = knapsack(s, numbers, values, iterCounter, printPct=True)

                    knapTime = time.perf_counter() - t1

                    o2 = round(iterCounter[0])

                    iterCounter[0] = 0

                    t1 = time.perf_counter()

                    opt4, optDim4, optItems4, optVal4 = hybridParetoKnapsack(s, numbers, values, iterCounter, printPct=True)

                    paretoHTime = time.perf_counter() - t1

                    oH = round(iterCounter[0])

                    if opt2 != opt3 or opt4 != opt2:
                        print(f"ERROR: {opt2} - {opt3}, size {s}, numbers: {numbers}, values = {values}")
                        self.assertTrue(False)

    # KB knapsacks and pareto reports for 25 random numbers in range(9500, 10000), values are random in [1..1000]
    # @unittest.skip("temp")
    def test_knapsacks_and_pareto_geometric_progression_9500_10000_25_values_random(self):
        if verbose:
            print(
                "KB knapsacks and pareto reports for 25 random numbers in range(9500, 10000), values are random in [1..1000]")

        numbers = list(sorted(sample(range(9500, 10000), 25), reverse=True))

        values = sample(range(1, 100000), 25)

        if verbose:
            print(f"len {len(numbers)}")
            print(f"sum {sum(numbers)}")

        if True:

            iterCounter = [0]

            if True:

                sumCases = [sum(numbers) // 2, (sum(numbers) // 4) * 3, sum(numbers) - 1, ]

                for s in sumCases:

                    print(f"case size {s}")

                    iterCounter[0] = 0

                    t1 = time.perf_counter()

                    opt2, optDim2, optItems2, optVal2 = knapsack(s, numbers, values, iterCounter, printPct=True)

                    knapTime = time.perf_counter() - t1

                    o2 = round(iterCounter[0])

                    optValSum2 = sum(optVal2)

                    iterCounter[0] = 0

                    opt3, optDim3, optItems3, optVal3 = paretoKnapsack(s, numbers, values, iterCounter, printPct=True)

                    o3 = round(iterCounter[0])

                    iterCounter[0] = 0

                    t1 = time.perf_counter()

                    opt4, optDim4, optItems4, optVal4 = hybridParetoKnapsack(s, numbers, values, iterCounter, printPct=True)

                    paretoHTime = time.perf_counter() - t1

                    oH = round(iterCounter[0])

                    if opt2 != opt3 or opt4 != opt2:
                        print(f"ERROR: {opt2} - {opt3}, size {s}, numbers: {numbers}, values = {values}")
                        self.assertTrue(False)
