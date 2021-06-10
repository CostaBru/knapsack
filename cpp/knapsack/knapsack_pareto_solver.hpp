#ifndef KB_KNAPSACK_PARTITION_SOLUTION_KNAPSACK_PARETO_SOLVER_HPP
#define KB_KNAPSACK_PARTITION_SOLUTION_KNAPSACK_PARETO_SOLVER_HPP

#include "fast_map.h"
#include "defines.h"
#include "w_point_dim1.hpp"
#include "w_point_dimN.hpp"
#include "w_point.hpp"
#include "tools.hpp"
#include "source_link.hpp"

#include <vector>
#include <tuple>
#include <cmath>
#include <deque>
#include <numeric>
#include <ranges>

namespace kb_knapsack {

    template<typename T, typename W, int N, template<typename DIM_TYPE, typename VALUE_TYPE, int DIM_LEN> class DIM>
    class knapsack_pareto_solver {
    public:

        TD EmptyDimension;
        W  EmptyValue;

        W  MinValue;

        bool UseRatioSort                = true;
        bool CanBackTraceWhenSizeReached = true;

        std::vector<TD>  Dimensions;
        std::vector<W>   Values;
        std::vector<int> Ids;

        W_POINT_LIST ParetoOptimal;
        SOURCE_LINK_LIST SourcePoints;

        knapsack_pareto_solver(std::vector<TD> & Dimensions, std::vector<W> & Values, std::vector<int> & Ids) :
            Dimensions(Dimensions),
            Values(Values),
            Ids(Ids) {
        }

        KNAPSACK_RESULT Solve(
                TD               & constraint,
                std::vector<TD>  & items,
                std::vector<W>   & values,
                std::vector<int> & itemsIndex) {

            std::vector<TD>  sortedItems(items);
            std::vector<W>   sortedValues(values);
            std::vector<int> sortedIndexes(itemsIndex);

            if (UseRatioSort){

                sortByRatio(sortedItems, sortedValues, sortedIndexes);
            } else {

                sortByDims(sortedItems, sortedValues, sortedIndexes);
            }

            W_POINT maxProfitPoint(EmptyDimension, EmptyValue);
            W_POINT emptyPoint(EmptyDimension, EmptyValue);

            ParetoOptimal = {emptyPoint};

            W_POINT_SET distinctPoints;

            W_POINT_LIST newPoints;
            W_POINT_LIST newParetoOptimal;

            auto expectedN = sortedItems.size() * sortedItems.size();

            SourcePoints.reserve(expectedN);
            ParetoOptimal.reserve(expectedN);

            auto itemsCount = sortedItems.size();

            for(int i = 1; i < itemsCount + 1; ++i) {

                auto itemDimensions = sortedItems[i - 1];
                auto itemProfit = sortedValues[i - 1];
                auto itemId = sortedIndexes[i - 1];

                newPoints.clear();

                getNewPoints(i,
                              maxProfitPoint,
                              itemDimensions,
                              itemProfit,
                              itemId,
                             ParetoOptimal,
                              newPoints,
                              constraint,
                              distinctPoints,
                              distinctPoints);

                newParetoOptimal.clear();

                // Point A is dominated by point B if B achieves a larger profit with the same or less weight than A.
                mergeDiscardingDominated(newParetoOptimal, ParetoOptimal, newPoints);

                if (CanBackTraceWhenSizeReached and maxProfitPoint.dimensions == constraint) {

                    return tools::backTraceItems(EmptyValue, EmptyDimension, maxProfitPoint, SourcePoints, Dimensions, Values, Ids);
                }

                ParetoOptimal.swap(newParetoOptimal); // oldPoints = newParetoOptimal;
            }

            return tools::backTraceItems(EmptyValue, EmptyDimension, maxProfitPoint, SourcePoints, Dimensions, Values, Ids);
        }
    private:

        inline void sortByRatio(std::vector<TD> & dimensions, std::vector<W> & values, std::vector<int> & indexes){

            std::vector<size_t> p(dimensions.size(), 0);

            // Sort
            std::iota(p.begin(), p.end(), 0);
            std::sort(p.begin(), p.end(),
                      [&](size_t i, size_t j){ return dimensions[i].divide(values[i]) < dimensions[j].divide(values[j]); });

            tools::applySort3<TD, W, int>(dimensions, values, indexes, p.size(), p);
        }

        inline void sortByDims(std::vector<TD> & dimensions, std::vector<W> & values, std::vector<int> & indexes){

            std::vector<size_t> p(dimensions.size(), 0);

            // Sort
            std::iota(p.begin(), p.end(), 0);
            std::sort(p.begin(), p.end(),
                      [&](size_t i, size_t j){

                          if (dimensions[i] == dimensions[j]) {

                              return dimensions[i].divide(values[i]) < dimensions[j].divide(values[j]);
                          }

                          return (dimensions[i] < dimensions[j]);
                      });

            tools::applySort3<TD, W, int>(dimensions, values, indexes,  p.size(), p);
        }

        void getNewPoints(
                int & i,
                W_POINT & maxProfitPoint,
                TD & itemDimensions,
                W & itemProfit,
                int & itemId,
                W_POINT_LIST & oldPoints,
                W_POINT_LIST & result,
                TD & constraint,
                W_POINT_SET & prevDistinctPoints,
                W_POINT_SET & newDistinctPoints) {

            W_POINT itemPoint = W_POINT(itemDimensions, itemProfit);

            for(auto& oldPoint : oldPoints) {

                if (oldPoint.dimensions + itemPoint.dimensions <= constraint) {

                    auto newPoint = oldPoint + itemPoint;

                    newPoint.id = SourcePoints.size();
                    source_link link(itemId, oldPoint.id);
                    SourcePoints.emplace_back(link);

                    if (prevDistinctPoints.contains(newPoint) == false) {

                        newDistinctPoints.insert(newPoint);
                        result.emplace_back(newPoint);
                    }

                    if (maxProfitPoint.profit <= newPoint.profit) {

                        if (UseRatioSort && maxProfitPoint.profit == newPoint.profit) {

                            if (maxProfitPoint.dimensions < newPoint.dimensions) {

                                maxProfitPoint = newPoint;
                            }
                        } else {

                            maxProfitPoint = newPoint;
                        }
                    }
                }
            }
        }

        inline int indexLargestLessThan(W_POINT_LIST & items, W & item, int lo, int hi){

            int ans = -1;

            while (lo <= hi) {

                int mid = (lo + hi) / 2;

                if (items[mid].profit > item) {

                    hi = mid - 1;
                    ans = mid;
                } else {

                    lo = mid + 1;
                }
            }

            return ans;
        }

        inline int findLargerProfit(W_POINT_LIST & items, W & profitMax) {

            auto index = indexLargestLessThan(items, profitMax, 0, items.size() - 1);

            if (index >= 0 && items[index].profit > profitMax) {
                return index;
            }
            else {
                return -1;
            }
        }

        void mergeDiscardingDominated(W_POINT_LIST & result, W_POINT_LIST & oldList, W_POINT_LIST & newList) {

            W profitMax = MinValue;

            while(true) {

                auto oldPointIndex = findLargerProfit(oldList, profitMax);
                auto newPointIndex = findLargerProfit(newList, profitMax);

                if (oldPointIndex == -1) {

                    if (newPointIndex >= 0) {

                        for (int ind = newPointIndex; ind < newList.size(); ++ind) {

                            result.emplace_back(newList[ind]);
                        }
                    }
                    break;
                }

                if (newPointIndex == -1) {

                    if (oldPointIndex >= 0) {

                        for (int ind = oldPointIndex; ind < oldList.size(); ++ind) {

                            result.emplace_back(oldList[ind]);
                        }
                    }
                    break;
                }

                W_POINT& oldPoint = oldList[oldPointIndex];
                W_POINT& newPoint = newList[newPointIndex];

                if (oldPoint.dimensions < newPoint.dimensions
                    || (oldPoint.dimensions == newPoint.dimensions && oldPoint.profit > newPoint.profit)) {

                    result.emplace_back(oldPoint);
                    profitMax = oldPoint.profit;
                } else {

                    result.emplace_back(newPoint);
                    profitMax = newPoint.profit;
                }
            }
        }
    };
}
#endif //KB_KNAPSACK_PARTITION_SOLUTION_KNAPSACK_PARETO_SOLVER_HPP
