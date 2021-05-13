#ifndef KB_KNAPSACK_PARTITION_SOLUTION_KNAPSACK_LIMITS_SOLVER_H
#define KB_KNAPSACK_PARTITION_SOLUTION_KNAPSACK_LIMITS_SOLVER_H

#include "fast_map.h"
#include "defines.h"
#include "w_point_dim1.h"
#include "w_point_dimN.h"
#include "w_point.h"
#include "source_link.h"
#include "tools.h"

#include <vector>
#include <tuple>
#include <cmath>
#include <deque>
#include <numeric>
#include <ranges>

namespace kb_knapsack {

    template<typename T, typename W, int N, template<typename DIM_TYPE, typename VALUE_TYPE, int DIM_LEN> class DIM>
    class knapsack_limit_solver {
    public:

        knapsack_limit_solver( std::vector<TD> & Dimensions, std::vector<W> & Values, std::vector<int> & Ids) :
            Dimensions(Dimensions),
            Values(Values),
            Ids(Ids) {
        }

        std::vector<TD>  Dimensions;
        std::vector<W>   Values;
        std::vector<int> Ids;

        TD EmptyDimension;
        W  EmptyValue;

        bool DoSolveSuperInc  = true;
        bool DoUseLimits      = true;

        bool CanBackTraceWhenSizeReached = false;

        W_POINT_DEQUEUE CircularPointQueue;
        SOURCE_LINK_LIST SourcePoints;

        KNAPSACK_RESULT Solve(
                TD constraint,
                std::vector<TD> & sortedItems,
                std::vector<W> & sortedValues,
                std::vector<int> & sortedIndexes,
                bool allAsc,
                std::vector<TD> & partialSums,
                std::vector<bool> & superIncreasingItems,
                bool canUsePartialSums) {

            W_POINT maxProfitPoint(EmptyDimension, EmptyValue);

            W_POINT_SET distinctPoints1;

            SourcePoints.reserve(sortedItems.size() * sortedItems.size());

            int itemsCount = sortedItems.size();

            int prevPointCount = 0;

            auto halfConstraint = constraint.half();

            for (int i = 1; i < itemsCount + 1; ++i) {

                auto itemIndex = getItemIndex(itemsCount, i, allAsc);

                auto itemDimensions = sortedItems[itemIndex];
                auto itemProfit     = sortedValues[itemIndex];
                auto itemId         = sortedIndexes[itemIndex];

                auto limitParams = getLimits(constraint,
                                             itemIndex,
                                             sortedItems,
                                             partialSums,
                                             superIncreasingItems,
                                             canUsePartialSums);

                auto canUseLimits  = std::get<0>(limitParams);
                auto itemLimit     = std::get<1>(limitParams);
                auto oldPointLimit = std::get<2>(limitParams);
                auto newPointLimit = std::get<3>(limitParams);

               iteratePoints(i,
                            itemDimensions,
                            itemProfit,
                            itemId,
                            constraint,
                            maxProfitPoint,
                            prevPointCount,
                            halfConstraint,
                            itemLimit,
                            oldPointLimit,
                            newPointLimit,
                            distinctPoints1,
                            distinctPoints1,
                            canUsePartialSums && canUseLimits
                );

                if (CanBackTraceWhenSizeReached && maxProfitPoint.dimensions == constraint) {

                    return tools::backTraceItems(EmptyValue,
                                          EmptyDimension,
                                          maxProfitPoint,
                                          SourcePoints,
                                          Dimensions,
                                          Values,
                                          Ids);
                }

                prevPointCount = CircularPointQueue.size();
            }

            return tools::backTraceItems(EmptyValue, EmptyDimension, maxProfitPoint, SourcePoints, Dimensions, Values, Ids);
        }

    private:
        inline std::tuple<bool, TD, TD, TD> getLimits(TD & constraints,
                                                      int currentItemIndex,
                                                      std::vector<TD> & items,
                                                      std::vector<TD> & partialSums,
                                                      std::vector<bool> & superIncreasingItems,
                                                      bool canUsePartialSums) {

            TD partSumForItem;
            TD oldPointLimit;
            TD newPointLimit;

            if (not DoUseLimits || not canUsePartialSums) {

                return std::make_tuple(false, partSumForItem, oldPointLimit, newPointLimit);
            }

            partSumForItem = partialSums[currentItemIndex];

            bool superIncreasingItem;

            if (not superIncreasingItems.empty()) {

                superIncreasingItem = superIncreasingItems[currentItemIndex];
            }

            newPointLimit = constraints - partSumForItem;
            oldPointLimit = newPointLimit;

            if (DoSolveSuperInc && superIncreasingItem) {

                oldPointLimit = newPointLimit + items[currentItemIndex];
            }

            return std::make_tuple(true, partSumForItem, oldPointLimit, newPointLimit);
        }

        inline void iterateOrPushBack(W_POINT & newPoint,
                               W_POINT_DEQUEUE & greaterQu,
                               W_POINT_SET & distinctPoints2) {

            if (not CircularPointQueue.empty()) {

                if (newPoint.dimensions <= CircularPointQueue.front().dimensions) {

                    CircularPointQueue.emplace_back(newPoint);
                    distinctPoints2.insert(newPoint);
                } else {

                    if (not greaterQu.empty()){

                        if (newPoint.dimensions <= greaterQu.front().dimensions) {

                            greaterQu.emplace_front(newPoint);
                        }
                        else {

                            greaterQu.emplace_back(newPoint);
                        }
                    }
                    else{

                        greaterQu.emplace_back(newPoint);
                    }
                }
            }
            else {
                CircularPointQueue.emplace_back(newPoint);
                distinctPoints2.insert(newPoint);
            }
        }

        inline void iterateLessThanOldPoint(W_POINT & oldPoint,
                                            bool canUseLimits,
                                            W_POINT_DEQUEUE & greaterQu,
                                            TD & oldPointLimit,
                                            W_POINT_SET & distinctPoints2) {

            while (not greaterQu.empty() and greaterQu.front().dimensions < oldPoint.dimensions) {

                distinctPoints2.insert(greaterQu.front());
                CircularPointQueue.emplace_back(greaterQu.front());

                greaterQu.pop_front();
            }

            if ((canUseLimits == false) || (oldPoint.dimensions < oldPointLimit) == false) {

                iterateOrPushBack(oldPoint, greaterQu, distinctPoints2);
            }
        }

        inline void iterateGreaterPoints(W_POINT_DEQUEUE & greaterQu,
                                         W_POINT_SET & distinctPoints2){

            while (not greaterQu.empty()) {

                CircularPointQueue.emplace_back(greaterQu.front());
                distinctPoints2.insert(greaterQu.front());

                greaterQu.pop_front();
            }
        }

        inline int getItemIndex(int count, int i, bool allAsc){

            return allAsc ? count - i : i - 1;
        }

        void iteratePoints(
                int & i,
                TD & itemDimensions,
                W & itemProfit,
                int & itemId,
                TD & constraintPoint,
                W_POINT & maxProfitPoint,
                int & prevCyclePointCount,
                TD halfConstraint,
                TD & itemLimit,
                TD & oldPointLimit,
                TD & newPointLimit,
                W_POINT_SET & distinctPoints1,
                W_POINT_SET & distinctPoints2,
                bool canUseLimits) {

            // merges ordered visited points with new points with keeping order in iterCounter(N) using single circular queue.
            // getPoints method call starts fetching visited points from qu start, pops visited point and pushes new point and visited to the end of qu in ASC order.
            // skip new point if it in list already
            // points if they will not contribute to optimal solution (in case of desc flow and (equal values or values equal to first dimension))

            W_POINT_DEQUEUE greaterQu;

            auto skipLimitCheck = canUseLimits == false;

            W_POINT itemPoint(itemDimensions, itemProfit);

            itemPoint.id = SourcePoints.size();
            SourcePoints.emplace_back(source_link(itemId, -1));

            auto useItemItself = skipLimitCheck || itemLimit >= halfConstraint;

            if (useItemItself) {

                if  (distinctPoints1.contains(itemPoint) == false) {

                    iterateOrPushBack(itemPoint, greaterQu, distinctPoints2);
                }

                if (maxProfitPoint.profit <= itemPoint.profit) {

                    maxProfitPoint = itemPoint;
                }
            }

            for (auto pi = 0; pi < prevCyclePointCount; ++pi) {

                W_POINT oldPoint = CircularPointQueue.front();
                CircularPointQueue.pop_front();

                iterateLessThanOldPoint(oldPoint,
                                        canUseLimits,
                                        greaterQu,
                                        oldPointLimit,
                                        distinctPoints2);


                if (not skipLimitCheck && oldPoint.dimensions + itemPoint.dimensions < newPointLimit) {

                    continue;
                }

                if (oldPoint.dimensions + itemPoint.dimensions <= constraintPoint) {

                    W_POINT newPoint = oldPoint + itemPoint;

                    if (distinctPoints1.contains(newPoint) == false) {

                        newPoint.id = SourcePoints.size();
                        SourcePoints.emplace_back(source_link(itemId, oldPoint.id));

                        iterateOrPushBack(newPoint, greaterQu, distinctPoints2);

                        if (maxProfitPoint.profit <= newPoint.profit) {

                            maxProfitPoint = newPoint;
                        }
                    }
                }
            }

            iterateGreaterPoints(greaterQu, distinctPoints2);
        }
    };
}

#endif //KB_KNAPSACK_PARTITION_SOLUTION_KNAPSACK_LIMITS_SOLVER_H
