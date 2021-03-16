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

from knapsack.wPoint import wPoint


class paretoPoint(wPoint):
    def __init__(self, dimensions, profit, id=None):
        self.profit = profit
        self.itemId = id
        self.source = None
        super().__init__(dimensions)

    def createNew(self, dimensions, profit, id):
        return paretoPoint(dimensions, profit, id)

    def getProfit(self):
        return self.profit

    def __add__(self, item):

        dims = [0] * len(self.dimensions)

        for i in range(len(self.dimensions)):
            dims[i] = self.dimensions[i] + item.getDimension(i)

        newPoint = paretoPoint(dims, self.profit + item.profit)
        newPoint.itemId = item.itemId
        newPoint.source = self
        return newPoint

    def getItemIds(self):

        if self.itemId is not None:
            yield self.itemId

        if self.source:
            for id in self.source.getItemIds():
                yield id

    def isDimensionEquals(self, other):
        if self.dimHash != other.dimHash:
            return False

        return super().__eq__(other)

    def __hash__(self):
        return super().__hash__() ^ hash(self.profit)

    def __eq__(self, other):
        return super().__eq__(other) and self.profit == other.profit

    def __repr__(self):
        return f"paretoPoint(dimensions={self.dimensions}, profit={self.profit}, items={list(self.getItemIds())})"


from knapsack.wPoint import *


class paretoPoint1(wPoint1):
    def __init__(self, dimensions, profit, id=None):
        self.profit = profit
        self.itemId = id
        self.source = None

        super().__init__(dimensions)

    def getProfit(self):
        return self.profit

    def createNew(self, dimensions, profit, id):
        return paretoPoint1(dimensions, profit, id)

    def isDimensionEquals(self, other):
        if self.dimHash != other.dimHash:
            return False

        return super().__eq__(other)

    def __add__(self, item):
        itemDim = item.getDimension(0)
        selfDim = self.dimensions
        newDim = selfDim + itemDim
        newPoint = paretoPoint1(newDim, self.profit + item.profit)
        newPoint.itemId = item.itemId
        newPoint.source = self
        return newPoint

    def getItemIds(self):

        if self.itemId is not None:
            yield self.itemId

        if self.source:
            for id in self.source.getItemIds():
                yield id

    def __hash__(self):
        return 397 ^ self.dimHash ^ hash(self.profit)

    def __eq__(self, other):
        if self.dimHash != other.dimHash:
            return False
        return self.dimensions == other.dimensions and self.profit == other.profit

    def __repr__(self):
        return f"paretoPoint1(dimensions={self.dimensions}, profit={self.profit}, items={list(self.getItemIds())})"


class paretoPoint2(wPoint2):

    def __init__(self, dim1, dim2, profit, id=None):
        self.profit = profit
        self.itemId = id
        self.source = None
        super().__init__(dim1, dim2)

    def getProfit(self):
        return self.profit

    def createNew(self, item, profit, id):
        return paretoPoint2(item[0], item[1], profit, id)

    def __add__(self, item):
        newPoint = paretoPoint2(self.dim1 + item.getDimension(0), self.dim2 + item.getDimension(1),
                                self.profit + item.profit)
        newPoint.itemId = item.itemId
        newPoint.source = self
        return newPoint

    def getItemIds(self):

        if self.itemId is not None:
            yield self.itemId

        if self.source:
            for id in self.source.getItemIds():
                yield id

    def isDimensionEquals(self, other):
        if self.dimHash != other.dimHash:
            return False

        return super().__eq__(other)

    def __hash__(self):
        return 397 ^ super().__hash__() ^ hash(self.profit)

    def __eq__(self, other):
        return super().__eq__(other) and self.profit == other.profit

    def __repr__(self):
        return f"paretoPoint2(dimensions={self.getDimensions()}, profit={self.profit}, items={list(self.getItemIds())})"


class paretoPoint0(wPoint1):

    def __init__(self, dimensions, id=None):
        self.itemId = id
        self.source = None
        super().__init__(dimensions)

    def getProfit(self):
        return self.dimensions

    def createNew(self, dimensions, profit, id):
        return paretoPoint0(dimensions, id)

    def __add__(self, item):
        newPoint = paretoPoint0(self.dimensions + item.dimensions)
        newPoint.itemId = item.itemId
        newPoint.source = self
        return newPoint

    def getItemIds(self):

        if self.itemId is not None:
            yield self.itemId

        if self.source:
            for id in self.source.getItemIds():
                yield id

    def isDimensionEquals(self, other):
        if self.dimHash != other.dimHash:
            return False

        return super().__eq__(other)

    def __hash__(self):
        return 397 ^ self.dimHash

    def __eq__(self, other):
        if self.dimHash != other.dimHash:
            return False
        return self.dimensions == other.dimensions

    def __repr__(self):
        return f"paretoPoint0(dimensions={self.dimensions}, items={list(self.getItemIds())})"