#ifndef knapsack_H
#define knapsack_H

#include "fast_map.h"
#include "defines.h"
#include "w_point_dim1.h"
#include "w_point_dimN.h"
#include "w_point.h"
#include "tools.h"
#include "source_link.h"

#include "knapsack_greedy_top_down_solver.h"
#include "knapsack_limits_solver.h"
#include "knapsack_pareto_solver.h"
#include "knapsack_superincreasing_solver.h"

#include <vector>
#include <tuple>
#include <cmath>
#include <deque>
#include <numeric>
#include <ranges>

namespace kb_knapsack {

    template<typename T, typename W, int N, template<typename DIM_TYPE, typename VALUE_TYPE, int DIM_LEN> class DIM>
    class knapsack_solver {
    public:
        knapsack_solver(std::vector<TD> & Dimensions, std::vector<W> & Values,  std::vector<int> & Ids) :
            Dimensions(Dimensions),
            Values(Values),
            Ids(Ids) {
        }

        TD Constraints;

        std::vector<TD>  Dimensions;
        std::vector<W>   Values;
        std::vector<int> Ids;

        TD EmptyDimension;
        W  EmptyValue;

        W MinValue;

        bool DoSolveSuperInc  = true;
        bool DoUseLimits      = true;
        bool UseRatioSort     = false;

        bool ForceUsePareto   = false;
        bool ForceUseLimits   = false;

        bool CanBackTraceWhenSizeReached  = false;

        bool PrepareSearchIndex = false;

        bool SolvedBySuperIncreasingSolverAsc  = false;
        bool SolvedBySuperIncreasingSolverDesc = false;
        bool SolvedByCornerCaseCheck = false;
        TD   SolvedByConstraint;

        W_POINT_LIST MaxProfitPointIndex;
        SOURCE_LINK_LIST SourcePoints;

        KNAPSACK_RESULT Solve(){

            SolvedByConstraint = EmptyDimension;

            return Solve(Constraints);
        }

        KNAPSACK_RESULT Solve(TD searchConstraint){

            if (Dimensions.size() != Values.size() || Ids.size() != Dimensions.size()) {

                throw std::invalid_argument("Sizes of dimensions, values and ids given should be equal.");
            }

            if (searchConstraint == EmptyDimension) {

                searchConstraint = SolvedByConstraint;

                if (searchConstraint == EmptyDimension) {

                    searchConstraint = Constraints;
                }
            }

            auto canTryBinarySearch = not MaxProfitPointIndex.empty() || SolvedBySuperIncreasingSolverAsc || SolvedBySuperIncreasingSolverDesc;

            if (canTryBinarySearch and searchConstraint <= SolvedByConstraint) {

                return binarySearchMaxProfit(searchConstraint);
            }

            auto canTrySolveUsingDp = not ForceUsePareto && (DoUseLimits || DoSolveSuperInc || ForceUseLimits || CanBackTraceWhenSizeReached);

            std::vector<TD>  lessSizeItems;
            std::vector<W>   lessSizeValues;
            std::vector<int> lessSizeItemsIndex;

            TD constraints = Constraints;

            if (canTrySolveUsingDp) {

                std::vector<TD> partialSums;
                std::vector<bool> superIncreasingItems;

                auto params = preProcess(Constraints,
                                         Dimensions,
                                         Values,
                                         ForceUseLimits,
                                         lessSizeItems,
                                         lessSizeValues,
                                         lessSizeItemsIndex,
                                         partialSums,
                                         superIncreasingItems);

                constraints = std::get<0>(params);

                auto count = std::get<1>(params);
                auto itemSum = std::get<2>(params);
                auto lessCountSum = std::get<3>(params);
                auto lessCountValuesSum = std::get<4>(params);
                auto isSuperIncreasing = std::get<5>(params);
                auto allAsc = std::get<6>(params);
                auto allDesc = std::get<7>(params);
                auto canUsePartialSums = std::get<8>(params);

                auto cornerCasesCheck = checkCornerCases(
                        constraints,
                        lessSizeItems,
                        lessSizeValues,
                        lessSizeItemsIndex,
                        lessCountSum,
                        itemSum,
                        lessCountValuesSum);

                auto isCornerCase = std::get<0>(cornerCasesCheck);

                if (isCornerCase) {

                    SolvedByCornerCaseCheck = true;
                    SolvedByConstraint = Constraints;

                    auto cornerCaseResult = std::get<1>(cornerCasesCheck);
                    return cornerCaseResult;
                }

                if (DoSolveSuperInc && isSuperIncreasing) {

                    auto superIncSolver = knapsack_superincreasing_solver<T, W, N, DIM>();

                    SolvedBySuperIncreasingSolverAsc  =  allAsc;
                    SolvedBySuperIncreasingSolverDesc = !allAsc;
                    SolvedByConstraint = Constraints;

                    superIncSolver.EmptyDimension = EmptyDimension;
                    superIncSolver.EmptyValue = EmptyValue;

                    return superIncSolver.Solve(constraints,
                                                lessSizeItems,
                                                lessSizeValues,
                                                lessSizeItemsIndex,
                                                count,
                                                allAsc);
                }

                bool canSolveUsingDp = not ForceUsePareto && (ForceUseLimits || CanBackTraceWhenSizeReached || canUsePartialSums);

                if (canSolveUsingDp) {

                    auto limitSolver = knapsack_limit_solver<T, W, N, DIM>(Dimensions, Values, Ids);

                    limitSolver.EmptyDimension = EmptyDimension;
                    limitSolver.EmptyValue = EmptyValue;

                    limitSolver.DoUseLimits = DoUseLimits and not PrepareSearchIndex;
                    limitSolver.DoSolveSuperInc = DoSolveSuperInc;
                    limitSolver.CanBackTraceWhenSizeReached = CanBackTraceWhenSizeReached;

                    auto limitResult = limitSolver.Solve(constraints,
                                                         lessSizeItems,
                                                         lessSizeValues,
                                                         lessSizeItemsIndex,
                                                         allAsc,
                                                         partialSums,
                                                         superIncreasingItems,
                                                         canUsePartialSums);

                    if (PrepareSearchIndex){
                        buildSearchIndexLimit(limitSolver.CircularPointQueue, limitSolver.SourcePoints);

                    }

                    SolvedByConstraint = Constraints;

                    return limitResult;
                }
            } else {

                lessSizeItems = Dimensions;
                lessSizeValues = Values;
                lessSizeItemsIndex = Ids;
            }

            auto paretoSolver = knapsack_pareto_solver<T, W, N, DIM>(Dimensions, Values, Ids);

            paretoSolver.EmptyDimension = EmptyDimension;
            paretoSolver.EmptyValue = EmptyValue;
            paretoSolver.MinValue = MinValue;

            paretoSolver.UseRatioSort = UseRatioSort;
            paretoSolver.CanBackTraceWhenSizeReached = CanBackTraceWhenSizeReached;

            auto paretoResult = paretoSolver.Solve(constraints, lessSizeItems, lessSizeValues, lessSizeItemsIndex);

            if (PrepareSearchIndex){
                buildSearchIndexPareto(paretoSolver.ParetoOptimal, paretoSolver.SourcePoints);
            }

            SolvedByConstraint = Constraints;

            return paretoResult;
        }

    private:

        void buildSearchIndexLimit(W_POINT_DEQUEUE & pointDequeue, SOURCE_LINK_LIST & sourcePoints){

            SourcePoints.swap(sourcePoints);

            W_POINT_LIST pointList;

            pointList.reserve(pointDequeue.size());

            for(auto & p : pointDequeue){
                pointList.emplace_back(p);
            }

            fillSearchIndex(pointList);
        }

        void buildSearchIndexPareto(W_POINT_LIST & pointList, SOURCE_LINK_LIST & sourcePoints){

            SourcePoints.swap(sourcePoints);

            fillSearchIndex(pointList);
        }

        void fillSearchIndex(W_POINT_LIST & pointList){

            std::sort(pointList.begin(), pointList.end(), [&](W_POINT x, W_POINT y) { return x.dimensions < y.dimensions;});

            MaxProfitPointIndex.clear();
            W_POINT nextMaxProfitPoint(EmptyDimension, EmptyValue);

            for(auto & p: pointList) {

                if(p.profit > nextMaxProfitPoint.profit) {

                    nextMaxProfitPoint = p;
                    MaxProfitPointIndex.emplace_back(nextMaxProfitPoint);
                }
            }
        }

        int indexLargestLessThanAsc(W_POINT_LIST & items, TD & item, int lo, int hi) {

            if (item == EmptyDimension) {
                return -1;
            }

            while (lo <= hi) {

                auto mid = int((lo + hi) / 2);

                if (item == items[mid].dimensions) {
                    return mid;
                }

                if (items[mid].dimensions < item) {
                    lo = mid + 1;
                } else {
                    hi = mid - 1;
                }
            }

            if (hi >= 0 && item >= items[hi].dimensions) {

                return hi;
            }
            else{

                return -1;
            }
        }

        KNAPSACK_RESULT binarySearchMaxProfit(TD & constraint) {

            if (SolvedBySuperIncreasingSolverAsc || SolvedBySuperIncreasingSolverDesc){

                auto superIncSolver = knapsack_superincreasing_solver<T, W, N, DIM>();

                return superIncSolver.Solve(constraint,
                                            Dimensions,
                                            Values,
                                            Ids,
                                            Values.size(),
                                            SolvedBySuperIncreasingSolverAsc);
            }

            if (constraint > SolvedByConstraint)
            {
                std::invalid_argument("The constraint given should be less or equal than index built constraint.");
            }

            auto count = MaxProfitPointIndex.size();

            if (count == 0) {
                std::invalid_argument("The binary search using given constraint is not possible.");
            }

            auto index = indexLargestLessThanAsc(MaxProfitPointIndex, constraint, 0, count - 1);

            W_POINT maxProfitPoint(EmptyDimension, EmptyValue);

            if (index >= 0) {
                maxProfitPoint = MaxProfitPointIndex[index];
            }

            return tools::backTraceItems(EmptyValue,
                                  EmptyDimension,
                                  maxProfitPoint,
                                  SourcePoints,
                                  Dimensions,
                                  Values,
                                  Ids);
        }

        std::tuple<
        /* 0 constraints */         TD,
        /* 1 lessCount */          int,
        /* 2 itemSum */             TD,
        /* 3 lessCountSum */        TD,
        /* 4 lessCountValuesSum */   W,
        /* 5 isSuperIncreasing */  bool,
        /* 6 allAsc */             bool,
        /* 7 allDesc */            bool,
        /* 8 canUsePartialSums */  bool
        >
                preProcess(
                        TD &constraints,
                        std::vector<TD> &items,
                        std::vector<W> &values,
                        bool &forceUseLimits,
                        std::vector<TD> &lessSizeItems,
                        std::vector<W> &lessSizeValues,
                        std::vector<int> &lessSizeItemsIndex,
                        std::vector<TD> &partialSums,
                        std::vector<bool> &superIncreasingItems
                        ){

            auto count = items.size();

            auto itemSum1 = EmptyDimension;
            auto itemSum2 = EmptyDimension;
            auto lessCountSum = EmptyDimension;

            W valuesSum1;
            W valuesSum2;
            W lessCountValuesSum;

            std::vector<TD> partialSums1;
            std::vector<bool> superIncreasingItems1 = {false};
            std::vector<TD> partialSums2;
            std::vector<bool> superIncreasingItems2 = {false};

            auto isSuperIncreasing1 = true; auto isSuperIncreasing2 = true;
            auto isSuperIncreasingValues1 = true; auto isSuperIncreasingValues2 = true;
            auto allValuesEqual = true; auto allValuesEqualToConstraints = true;
            auto allDesc = true; auto allAsc = true; auto allDescValues = true; auto allAscValues = true;

            auto canUsePartialSums = false;

            auto lessCount = 0;

            auto itemSum = EmptyDimension;
            bool isSuperIncreasing = false;

            if (count > 0) {

                auto prevItem1 = items[count - 1];
                auto prevValue1 = values[count - 1];

                for (auto i = 0; i < count; ++i) {

                    auto &item2 = items[i];
                    auto &itemValue2 = values[i];

                    auto iBack = count - i - 1;

                    auto &item1 = items[iBack];
                    auto &itemValue1 = values[iBack];

                    auto superIncreasingItem1 = false;
                    auto superIncreasingItem2 = false;

                    if (item1 <= constraints) {

                        if (item1 < itemSum1) {
                            isSuperIncreasing1 = false;
                        } else {
                            superIncreasingItem1 = true;
                        }

                        if (itemValue1 < valuesSum1) {
                            isSuperIncreasingValues1 = false;
                            superIncreasingItem1 = false;
                        }
                    }

                    if (item2 <= constraints) {

                        if (item2 < itemSum2) {
                            isSuperIncreasing2 = false;
                        } else {
                            superIncreasingItem2 = true;
                        }

                        if (itemValue2 < valuesSum2) {
                            isSuperIncreasingValues2 = false;
                            superIncreasingItem2 = false;
                        }
                    }

                    if (allValuesEqual && prevValue1 != itemValue2) {
                        allValuesEqual = false;
                    }

                    if (allValuesEqualToConstraints && item2.firstDimensionEqual(itemValue2) == false) {
                        allValuesEqualToConstraints = false;
                    }

                    itemSum1 += item1;
                    itemSum2 += item2;

                    valuesSum1 += itemValue1;
                    valuesSum2 += itemValue2;

                    partialSums1.emplace_back(itemSum2);
                    partialSums2.emplace_back(itemSum1);

                    if (allDesc) {
                        if (!(prevItem1 <= item1)) {
                            allDesc = false;
                        }
                    }

                    if (allAsc) {
                        if (prevItem1 < item1) {
                            allAsc = false;
                        }
                    }

                    if (allDescValues) {
                        if (!prevValue1 <= itemValue1) {
                            allDescValues = false;
                        }
                    }

                    if (allAscValues) {
                        if (prevValue1 < itemValue1) {
                            allAscValues = false;
                        }
                    }

                    if (i > 0) {
                        superIncreasingItems1.emplace_back(superIncreasingItem1);
                        superIncreasingItems2.emplace_back(superIncreasingItem2);
                    }

                    if (item2 <= constraints) {
                        lessSizeItems.emplace_back(item2);
                        lessSizeValues.emplace_back(itemValue2);
                        lessSizeItemsIndex.emplace_back(i);
                        lessCountValuesSum += itemValue2;
                        lessCountSum += item2;
                        lessCount += 1;
                    }
                    prevItem1 = item1;
                    prevValue1 = itemValue1;
                }

                canUsePartialSums = allValuesEqual ||
                                    allValuesEqualToConstraints ||
                                    (isSuperIncreasingValues1 && allDescValues) ||
                                    (isSuperIncreasingValues2 && allAscValues);

                if (allAsc && canUsePartialSums) {
                    partialSums.swap(partialSums2);
                    superIncreasingItems.swap(superIncreasingItems2);
                    isSuperIncreasing = isSuperIncreasing2;
                    itemSum = itemSum2;
                } else if ((allDesc && canUsePartialSums) || forceUseLimits) {
                    partialSums.swap(partialSums1);
                    superIncreasingItems.swap(superIncreasingItems1);
                    isSuperIncreasing = isSuperIncreasing1;
                    itemSum = itemSum1;

                    std::reverse(partialSums.begin(), partialSums.end());
                    std::reverse(superIncreasingItems.begin(), superIncreasingItems.end());
                } else {
                    if (allAsc and allAscValues) {
                        itemSum = itemSum2;
                        partialSums.swap(partialSums2);
                        std::reverse(partialSums.begin(), partialSums.end());
                        superIncreasingItems.swap(superIncreasingItems2);
                        std::reverse(superIncreasingItems.begin(), superIncreasingItems.end());
                        canUsePartialSums = true;
                    } else if (allDesc and allDescValues) {
                        itemSum = itemSum1;
                        partialSums.swap(partialSums1);
                        std::reverse(partialSums.begin(), partialSums.end());
                        superIncreasingItems.swap(superIncreasingItems1);
                        std::reverse(superIncreasingItems.begin(), superIncreasingItems.end());
                        canUsePartialSums = true;
                    } else {
                        itemSum = itemSum2;
                        superIncreasingItems = {};
                        if (!canUsePartialSums) {
                            partialSums = {};
                            canUsePartialSums = false;
                        } else {
                            partialSums.swap(partialSums2);
                            std::reverse(partialSums.begin(), partialSums.end());
                        }
                    }
                }
            }
            else{

                partialSums = {};
                superIncreasingItems = {};
                isSuperIncreasing = false;
                itemSum = itemSum2;
            }

            constraints = constraints.adjustMin(itemSum);

            return std::make_tuple(constraints,
                                   lessCount,
                                   itemSum,
                                   lessCountSum,
                                   lessCountValuesSum,
                                   isSuperIncreasing,
                                   allAsc,
                                   allDesc,
                                   canUsePartialSums);
        }

        inline std::tuple<bool, KNAPSACK_RESULT> checkCornerCases(
                TD& constraints,
                std::vector<TD>& lessSizeItems,
                std::vector<W>& lessSizeValues,
                std::vector<int>& lessSizeItemsIndex,
                TD& lessCountSum,
                TD& itemSum,
                W& lessCountValuesSum){

            W zero = EmptyValue;
            std::vector<TD> emptyItems;
            std::vector<W> emptyValues;
            std::vector<int> emptyIndexes;

            if  (lessCountSum == EmptyDimension) {

                return std::make_tuple(true, std::make_tuple(zero, EmptyDimension, emptyItems, emptyValues, emptyIndexes));
            }

            if  (lessCountSum <= constraints) {

                return std::make_tuple(true, std::make_tuple(lessCountValuesSum, lessCountSum, lessSizeItems, lessSizeValues, lessSizeItemsIndex));
            }

            if  (itemSum <= constraints) {

                return std::make_tuple(true, std::make_tuple(lessCountValuesSum, itemSum, lessSizeItems, lessSizeValues, lessSizeItemsIndex));
            }

            return std::make_tuple(false, std::make_tuple(zero, EmptyDimension, emptyItems, emptyValues, emptyIndexes));
        }
    };
}
#endif
