#ifndef KB_KNAPSACK_PARTITION_SOLUTION_TOOLS_HPP
#define KB_KNAPSACK_PARTITION_SOLUTION_TOOLS_HPP

#include "fast_map.h"
#include "defines.h"
#include "w_point_dim1.hpp"
#include "w_point_dimN.hpp"
#include "w_point.hpp"
#include "source_link.hpp"

#include <vector>
#include <tuple>
#include <cmath>
#include <deque>
#include <numeric>
#include <ranges>

namespace kb_knapsack {

    namespace tools {


        template<typename T, typename W>
        void sortReverse(std::vector<T> &dimensions, std::vector<W> &values, std::vector<int> &indexes) {

            std::vector<size_t> p(dimensions.size(), 0);

            // Sort
            std::iota(p.begin(), p.end(), 0);
            std::sort(p.begin(), p.end(),
                      [&](size_t i, size_t j) { return dimensions[i] > dimensions[j]; });

            applySort3<T, W, int>(dimensions, values, indexes, p.size(), p);
        }

        template<class K, class T1, class T2>
        void applySort3(std::vector<K> &keys, std::vector<T1> &data1, std::vector<T2> &data2, size_t size,
                        std::vector<size_t> p) {
            std::vector<size_t> rp(size);
            std::vector<bool> sorted(size, false);
            size_t i = 0;

            // ----------- Apply permutation in-place ---------- //

            // Get reverse permutation item>position
            for (i = 0; i < size; ++i) {
                rp[p[i]] = i;
            }

            i = 0;
            K savedKey;
            T1 savedData1;
            T2 savedData2;

            while (i < size) {
                size_t pos = i;
                // Save This element;
                if (!sorted[pos]) {
                    savedKey = keys[p[pos]];
                    savedData1 = data1[p[pos]];
                    savedData2 = data2[p[pos]];
                }
                while (!sorted[pos]) {
                    // Hold item to be replaced
                    K heldKey = keys[pos];
                    T1 heldData1 = data1[pos];
                    T2 heldData2 = data2[pos];
                    // Save where it should go
                    size_t heldPos = rp[pos];

                    // Replace
                    keys[pos] = savedKey;
                    data1[pos] = savedData1;
                    data2[pos] = savedData2;

                    // Get last item to be the pivot
                    savedKey = heldKey;
                    savedData1 = heldData1;
                    savedData2 = heldData2;

                    // Mark this item as sorted
                    sorted[pos] = true;

                    // Go to the held item proper location
                    pos = heldPos;
                }
                ++i;
            }
        }

        template<typename T, typename W, int N, template<typename DIM_TYPE, typename VALUE_TYPE, int DIM_LEN> class DIM>
        KNAPSACK_RESULT backTraceItems(
                W                & emptyValue,
                TD               & emptyDimension,
                W_POINT          & maxProfitPoint,
                SOURCE_LINK_LIST & sourcePoints,
                std::vector<TD > & dimensions,
                std::vector<W>   & values,
                std::vector<int> & ids) {

            W zeroProfit = emptyValue;
            std::vector<TD > optItems;
            std::vector<W> optValues;
            std::vector<int> optIndexes;

            auto optSize = emptyDimension;

            if (maxProfitPoint.profit > 0) {

                W maxProfit = maxProfitPoint.profit;

                source_link pointLink = sourcePoints[maxProfitPoint.id];

                while (true) {

                    optItems  .emplace_back(dimensions[pointLink.itemId]);
                    optValues .emplace_back(values[pointLink.itemId]);
                    optIndexes.emplace_back(ids[pointLink.itemId]);

                    optSize +=   dimensions[pointLink.itemId];

                    if (!pointLink.hasParent()) {
                        break;
                    }

                    pointLink = sourcePoints[pointLink.parentId];
                }

                return std::make_tuple(maxProfit, optSize, optItems, optValues, optIndexes);
            }

            return std::make_tuple(zeroProfit, emptyDimension, optItems, optValues, optIndexes);
        }
    }
}

#endif //KB_KNAPSACK_PARTITION_SOLUTION_TOOLS_HPP
