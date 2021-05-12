//
// Created by kooltew on 5/11/2021.
//

#ifndef KB_KNAPSACK_PARTITION_SOLUTION_KNAPSACK_SUPERINCREASING_SOLVER_H
#define KB_KNAPSACK_PARTITION_SOLUTION_KNAPSACK_SUPERINCREASING_SOLVER_H

#include "fast_map.h"
#include "defines.h"
#include "w_point_dim1.h"
#include "w_point_dimN.h"
#include "w_point.h"
#include "tools.h"
#include "source_link.h"

#include <vector>
#include <tuple>
#include <cmath>
#include <deque>
#include <numeric>
#include <ranges>

namespace kb_knapsack {

    template<typename T, typename W, int N, template<typename DIM_TYPE, typename VALUE_TYPE, int DIM_LEN> class DIM>
    class knapsack_superincreasing_solver {
    public:
        knapsack_superincreasing_solver() {
        }

        TD EmptyDimension;
        W EmptyValue;

        KNAPSACK_RESULT Solve(TD &size,
                              std::vector<TD > &items,
                              std::vector<W> &values,
                              std::vector<int> &itemsIndex,
                              int count,
                              bool allAsc) {

            int starting = 1;
            std::vector<TD > resultItems;
            std::vector<W> resultValues;
            std::vector<int> resultIndex;
            W resultSum = EmptyValue;
            TD resultItemSum = EmptyDimension;

            auto index = -1;

            if (allAsc) {
                index = indexLargestLessThanAsc(items, size, starting - 1, count - 1);
            } else {
                index = indexLargestLessThanDesc(items, size, starting - 1, count - 1);
            }

            while (index >= 0) {
                auto &item = items[index];
                auto &value = values[index];

                resultItems.emplace_back(item);
                resultValues.emplace_back(value);
                resultIndex.emplace_back(itemsIndex[index]);

                resultItemSum += item;
                resultSum += value;

                if (allAsc) {
                    index = indexLargestLessThanAsc(items, size - resultItemSum, starting - 1, index - 1);
                } else {
                    index = indexLargestLessThanDesc(items, size - resultItemSum, index + 1, count - 1);
                }
            }

            return std::make_tuple(resultSum, resultItemSum, resultItems, resultValues, resultIndex);
        }

    private:

        inline int indexLargestLessThanAsc(std::vector<TD > &items, TD item, int lo, int hi) {

            if (item == EmptyDimension) {
                return -1;
            }

            while (lo <= hi) {
                int mid = (lo + hi) / 2;

                auto val = items[mid];

                if (item == val) {
                    return mid;
                }

                if (val < item) {
                    lo = mid + 1;
                } else {
                    hi = mid - 1;
                }
            }

            if (hi >= 0 and item >= items[hi]) {
                return hi;
            } else {
                return -1;
            }
        }

        inline int indexLargestLessThanDesc(std::vector<TD > &items, TD item, int lo, int hi) {

            if (item == EmptyDimension) {
                return -1;
            }

            auto cnt = items.size();

            while (lo <= hi) {
                int mid = (lo + hi) / 2;

                auto val = items[mid];

                if (item == val) {
                    return mid;
                }

                if (val > item) {
                    lo = mid + 1;
                } else {
                    hi = mid - 1;
                }
            }

            if (lo < cnt && item >= items[lo]) {
                return lo;
            } else {
                return -1;
            }
        }
    };
}

#endif //KB_KNAPSACK_PARTITION_SOLUTION_KNAPSACK_SUPERINCREASING_SOLVER_H