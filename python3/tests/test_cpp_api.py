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
import os


winPathDir3 = os.add_dll_directory("C:\\msys64\\mingw64\\bin")

import knapsack_python_api

class CppApi(unittest.TestCase):

    def test_1_rational_numbers(self):

        A = [0.2, 1.200001, 2.9000001, 3.30000009, 4.3, 5.5, 6.6, 7.7, 8.8, 9.8]

        Ids = list(range(len(A)))

        s = 10.5

        expectedValue = 10.20000109

        optVal, optSize, optItems, optValues, optIds = knapsack_python_api.solve_1d_double(s, A, A, Ids)

        self.assertTrue(expectedValue == optVal)

    def test_1_int_numbers(self):

        A = [1, 2, 5, 21, 69, 189, 376, 919]

        Ids = list(range(len(A)))

        expectedValue = 98
        s = 100

        optVal, optSize, optItems, optValues, optIds = knapsack_python_api.solve_1d_int(s, A, A, Ids)

        self.assertTrue(expectedValue == optVal)
