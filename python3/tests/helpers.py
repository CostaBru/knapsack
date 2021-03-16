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

from decimal import Decimal
from random import shuffle


def sortReverseBoth(w, v, reverse=True):
    sorted_pairs = sorted(zip(w, v), reverse=reverse, key=lambda t: (t[0], t[1]))
    tuples = zip(*sorted_pairs)
    return [list(tuple) for tuple in tuples]


def shuffleBoth(w, v):
    list_pairs = list(zip(w, v))
    shuffle(list_pairs)
    tuples = zip(*list_pairs)
    return [list(tuple) for tuple in tuples]


def sortReverse3Both(w, v, x):
    sorted_pairs = sorted(zip(w, v, x), reverse=True, key=lambda t: (t[0], t[1], t[2]))
    tuples = zip(*sorted_pairs)
    return [list(tuple) for tuple in tuples]


def DecimalData(data):
    return Decimal(Decimal(data) / 100000)


def DecimalArray(data):
    for i in range(len(data)):
        data[i] = DecimalData(data[i])


def listValuesEqual(l1, l2):
    l1.sort()
    l2.sort()
    return l1 == l2
