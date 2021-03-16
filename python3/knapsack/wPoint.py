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


class wPoint:
    def __init__(self, dimensions):
        self.dimensions = tuple(dimensions)
        self.dimHash = 397 ^ hash(self.dimensions)

    def createNew(self, tuples):
        return wPoint(tuples)

    def getDimension(self, index):
        return self.dimensions[index]

    def getDimensions(self):
        return self.dimensions

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

    def adjustMin(self, other):
        l = len(self.dimensions)

        newDim = [0] * l

        for i in range(l):
            newDim[i] = min(self.dimensions[i], other.dimensions[i])

        return wPoint(newDim)

    def __truediv__(self, other):
        l = len(self.dimensions)

        newDim = [0] * l

        for i in range(l):
            newDim[i] = self.dimensions[i] / other

        return wPoint(newDim)

    def __rtruediv__(self, other):

        l = len(self.dimensions)

        newDim = [0] * l

        for i in range(l):
            newDim[i] = other / self.dimensions[i]

        return wPoint(newDim)

    def __add__(self, item):

        l = len(self.dimensions)

        newDim = [0] * l

        for i in range(l):
            newDim[i] = self.dimensions[i] + item.getDimension(i)

        return wPoint(newDim)

    def __sub__(self, item):

        l = len(self.dimensions)
        newDim = [0] * l

        for i in range(l):
            newDim[i] = self.dimensions[i] - item.getDimension(i)

        return wPoint(newDim)

        # <

    def __lt__(self, other):
        l = len(self.dimensions)

        allLess = False
        for i in range(l):

            if self.dimensions[i] == other.getDimension(i):
                continue

            if self.dimensions[i] < other.getDimension(i):
                allLess = True
            else:
                return False

        return allLess

        # <=

    def __le__(self, other):

        l = len(self.dimensions)
        for i in range(l):

            if self.dimensions[i] > other.getDimension(i):
                return False

        return True
        # >

    def __gt__(self, other):
        l = len(self.dimensions)

        allGreater = False
        for i in range(l):

            if self.dimensions[i] == other.getDimension(i):
                continue

            if other.dimensions[i] < self.getDimension(i):
                allGreater = True
            else:
                return False

        return allGreater
        # >=

    def __ge__(self, other):
        l = len(self.dimensions)
        for i in range(l):

            if self.dimensions[i] < other.getDimension(i):
                return False

        return True

    def __eq__(self, other):
        return self.dimensions == other.getDimensions()

    def __hash__(self):
        return self.dimHash


class wPoint2:
    def __init__(self, dim1, dim2):
        self.dim1 = dim1
        self.dim2 = dim2
        self.dimHash = 397 ^ hash(self.dim1) ^ hash(self.dim2)

    def createNew(self, tuples):
        return wPoint2(tuples[0], tuples[1])

    def getDimension(self, index):
        return self.dim1 if index == 0 else self.dim2

    def getDimensions(self):
        return (self.dim1, self.dim2)

    def __str__(self):
        return f"[{self.dim1},{self.dim2}]"

    def __repr__(self):
        return f"[{self.dim1},{self.dim2}]"

    def firstDimensionEqual(self, number):
        return self.dim1 == number

    def getSize(self):
        return 2

    def divideBy(self, number):
        return wPoint2(self.dim1 / number, self.dim2 / number)

    def adjustMin(self, other):
        return wPoint2(min(self.dim1, other.dim1), min(self.dim2, other.dim2))

    def __truediv__(self, other):
        return wPoint2(self.dim1 / other, self.dim2 / other)

    def __rtruediv__(self, other):
        return wPoint2(other / self.dim1, other / self.dim2)

    def __add__(self, item):
        return wPoint2(self.dim1 + item.dim1, self.dim2 + item.dim2)

    def __sub__(self, item):
        return wPoint2(self.dim1 - item.dim1, self.dim2 - item.dim2)

    # <
    def __lt__(self, other):

        if self.dim1 <= other.dim1 and self.dim2 < other.dim2:
            return True

        if self.dim2 <= other.dim2 and self.dim1 < other.dim1:
            return True

        return False

    # <=
    def __le__(self, other):
        return self.dim1 <= other.dim1 and self.dim2 <= other.dim2

    # >
    def __gt__(self, other):
        return self == other or (not self < other)

    # >=
    def __ge__(self, other):

        return not self < other

    def __eq__(self, other):
        return self.dim1 == other.dim1 and self.dim2 == other.dim2

    def __hash__(self):
        return self.dimHash


class wPoint1:
    def __init__(self, dimensions):
        self.dimensions = dimensions
        self.dimHash = 397 ^ hash(self.dimensions)

    def createNew(self, tuples):
        return wPoint1(tuples[0])

    def getDimension(self, index):
        return self.dimensions

    def getDimensions(self):
        return (self.dimensions)

    def __str__(self):
        return f"[{self.dimensions}]"

    def __repr__(self):
        return f"[{self.dimensions}]"

    def firstDimensionEqual(self, number):
        return self.dimensions == number

    def getSize(self):
        return 1

    def divideBy(self, number):
        return wPoint1(self.dimensions / number)

    def adjustMin(self, other):
        return wPoint1(min(self.dimensions, other.getDimension(0)))

    def __truediv__(self, other):
        return wPoint1(self.dimensions / other)

    def __rtruediv__(self, other):
        return wPoint1(other / self.dimensions)

    def __add__(self, item):
        return wPoint1(self.dimensions + item.getDimension(0))

    def __sub__(self, item):
        return wPoint1(self.dimensions - item.getDimension(0))

    # <
    def __lt__(self, other):
        return self.dimensions < other.getDimension(0)

    # <=
    def __le__(self, other):
        return self.dimensions <= other.getDimension(0)

    # >
    def __gt__(self, other):
        return self.dimensions > other.getDimension(0)

    # >=
    def __ge__(self, other):
        return self.dimensions >= other.getDimension(0)

    def __eq__(self, other):
        return self.dimensions == other.getDimension(0)

    def __hash__(self):
        return self.dimHash
