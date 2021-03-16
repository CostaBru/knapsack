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


from collections import defaultdict


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