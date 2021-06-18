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

os.add_dll_directory("C:\\msys64\\mingw64\\bin")

import knapsack_python_api

class PythonKnapsackCppApiTests(unittest.TestCase):

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

    def test_8_multidimensional_100(self):

        lConstraint = 20789
        wConstraint = 23681
        greedyOptimumValue = 121105212
        actualOptima = 121147356
        dimensionMultiplier = 1

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
        items = [((p[0] * dimensionMultiplier, p[1] * dimensionMultiplier)) for p in lwData100]
        constraints = ((lConstraint * dimensionMultiplier, wConstraint * dimensionMultiplier))

        Ids = list(range(len(values)))

        bestValue, bestSize, bestItems, bestValues, bestIds = knapsack_python_api.solve_greedy_2d_int(constraints, items, values, Ids)

        opt, optDims, optItems, optValues = bestValue, bestSize, bestItems, bestValues

        self.assertTrue(opt >= greedyOptimumValue and tuple(optDims) <= constraints)
