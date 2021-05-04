#ifndef knapsack_H
#define knapsack_H

#define W_POINT w_point<T, W>

#define W_POINT_SET robin_hood::unordered_set<W_POINT, w_point_hash<T, W>, w_point_key_equals<T, W>>

#define W_POINT_DEQUEUE std::deque<W_POINT>

#define W_POINT_LIST std::vector<W_POINT>

#define KNAPSACK_RESULT std::tuple<W, T, std::vector<T>, std::vector<W>, std::vector<int>>

#define SOURCE_LINK_LIST std::vector<source_link>

#include "fast_map.h"
#include <vector>
#include <tuple>
#include <cmath>
#include <deque>
#include <numeric>
#include <ranges>

namespace kb_knapsack {

    template<typename T>
    struct w_point_dim {
    public:
        T value;

        w_point_dim(){
        }

        w_point_dim(T dim){
            value = dim;
        }

        w_point_dim adjustMin(w_point_dim p){
            if (p.value < value){
                return w_point_dim(p.value);
            }

            return w_point_dim(value);
        }

        w_point_dim divideBy(){
            return w_point_dim(value / 2);
        }

        friend bool operator>(const w_point_dim &c1, const w_point_dim &c2) {
            return c1.value > c2.value;
        }

        friend bool operator<=(const w_point_dim &c1, const w_point_dim &c2) {
            return c1.value <= c2.value;
        }

        friend bool operator<(const w_point_dim &c1, const w_point_dim &c2) {
            return c1.value < c2.value;
        }

        friend bool operator>=(const w_point_dim &c1, const w_point_dim &c2) {
            return c1.value >= c2.value;
        }

        friend bool operator==(const w_point_dim &c1, const w_point_dim &c2) {
            return c1.value == c2.value;
        }

        friend bool operator!=(const w_point_dim &c1, const w_point_dim &c2) {
            return c1.value != c2.value;
        }

        friend bool operator+(const w_point_dim &c1, const w_point_dim &c2) {
            return w_point_dim(c1.value + c2.value);
        }
    };

    template<typename T, typename W>
    struct w_point {
    public:
        T dimensions;
        W profit;
        long id = -1;

        w_point(){
        }

        w_point(T dims, W value){
            dimensions = dims;
            profit = value;
        }

        bool isDimensionEquals(T dim){
            return dimensions == dim;
        }

        friend w_point operator+(w_point &c1, w_point &c2) {
            return w_point(c1.dimensions + c2.dimensions, c1.profit + c2.profit);
        }

        w_point(const w_point& that)
        {
            dimensions = that.dimensions;
            profit = that.profit;
            id = that.id;
        }

        w_point& operator=(const w_point& that)
        {
            if (this != &that)
            {
                dimensions = that.dimensions;
                profit = that.profit;
                id = that.id;
            }
            return *this;
        }

        friend std::ostream& operator<<(std::ostream &strm, const w_point<T, W> &a) {
            return strm << "p(" << a.dimensions << "-" << a.profit << ")";
        }
    };

    struct source_link{
        int itemId = -1;
        long parentId = -1;

        source_link(int _itemId, long sourceLinkId){
            itemId = _itemId;
            parentId = sourceLinkId;
        }

        bool hasParent(){
            return parentId >= 0;
        }
    };

    template<typename T, typename W>
    struct w_point_hash
    {
        std::size_t operator()(const w_point<T, W>& k) const
        {
            std::size_t h1 = (robin_hood::hash<T>()(k.dimensions));
            std::size_t h2 = (std::hash<W>()(k.profit));

            return 397 ^ h1 ^ h2;
        }
    };

    template<typename T, typename W>
    struct w_point_key_equals
    {
        bool operator()(const w_point<T, W>& k1, const w_point<T, W>& k2) const
        {
            return k1.dimensions == k2.dimensions && k1.profit == k2.profit;
        }
    };

    template <typename T, typename W>
    void sortReverse(std::vector<T>& dimensions, std::vector<W>& values, std::vector<int>& indexes){

        std::vector<size_t> p(dimensions.size(), 0);

        // Sort
        std::iota(p.begin(), p.end(), 0);
        std::sort(p.begin(), p.end(),
                  [&](size_t i, size_t j){ return dimensions[i] > dimensions[j]; });

        applySort3<T, W, int>(dimensions, values, indexes, p.size(), p);
    }

    template <class K, class T1, class T2>
    void applySort3(std::vector<K>&  keys, std::vector<T1>& data1, std::vector<T2>& data2, size_t size, std::vector<size_t> p){
        std::vector<size_t> rp(size);
        std::vector<bool> sorted(size, false);
        size_t i = 0;

        // ----------- Apply permutation in-place ---------- //

        // Get reverse permutation item>position
        for (i = 0; i < size; ++i){
            rp[p[i]] = i;
        }

        i = 0;
        K savedKey;
        T1 savedData1;
        T2 savedData2;

        while ( i < size){
            size_t pos = i;
            // Save This element;
            if ( ! sorted[pos] ){
                savedKey = keys[p[pos]];
                savedData1 = data1[p[pos]];
                savedData2 = data2[p[pos]];
            }
            while ( ! sorted[pos] ){
                // Hold item to be replaced
                K heldKey  = keys[pos];
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

    template<typename T, typename W>
    class knapsack_solver{
    public:
        knapsack_solver(){
        }

        T Constrains;
        T EmptyDimension;
        W EmptyValue;
        W MinValue;
        std::vector<T> Dimensions;
        std::vector<W> Values;
        std::vector<int> Ids;
        bool ForceUseLimits = false;
        bool DoSolveSuperInc = true;
        bool DoUseLimits= true;
        bool UseRatioSort= false;
        bool CanBackTraceWhenSizeReached = false;
        bool ForceUsePareto = false;

        KNAPSACK_RESULT Solve(){

            if (Dimensions.size() != Values.size() || Ids.size() != Dimensions.size()) {
                throw std::invalid_argument("Sizes of input dimensions, values and ids should be equal.");
            }

            auto canTrySolveUsingDp = not ForceUsePareto and (DoUseLimits or DoSolveSuperInc or ForceUseLimits or CanBackTraceWhenSizeReached);

            std::vector<T> lessSizeItems;
            std::vector<W> lessSizeValues;
            std::vector<int> lessSizeItemsIndex;

            T constraints = Constrains;

            if (canTrySolveUsingDp) {

                std::vector<T> partialSums;
                std::vector<bool> superIncreasingItems;

                auto params = preProcess(Constrains,
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

                    auto cornerCaseResult = std::get<1>(cornerCasesCheck);
                    return cornerCaseResult;
                }

                if (DoSolveSuperInc && isSuperIncreasing) {

                    return solveSuperIncreasing(constraints,
                                                lessSizeItems,
                                                lessSizeValues,
                                                lessSizeItemsIndex,
                                                count,
                                                allAsc);
                }

                bool canSolveUsingDp = ! ForceUsePareto && (ForceUseLimits || CanBackTraceWhenSizeReached || canUsePartialSums);

                if (canSolveUsingDp) {

                    return solveUsingLimitsOnly(constraints,
                                                lessSizeItems,
                                                lessSizeValues,
                                                lessSizeItemsIndex,
                                                allAsc,
                                                partialSums,
                                                superIncreasingItems,
                                                canUsePartialSums);
                }
            } else{
                auto lessSizeItems = Dimensions;
                auto lessSizeValues = Values;
                auto lessSizeItemsIndex = Ids;
            }

            std::vector<T> sortedItems(lessSizeItems);
            std::vector<W> sortedValues(lessSizeValues);
            std::vector<int> sortedIndexes(lessSizeItemsIndex);

            if (UseRatioSort){
                sortByRatio(sortedItems, sortedValues, sortedIndexes);
            } else {
                sortByDims(sortedItems, sortedValues, sortedIndexes);
            }

            return solvePareto(constraints, sortedItems, sortedValues, sortedIndexes);
        }

    private:

        inline void sortByRatio(std::vector<T>& dimensions, std::vector<W>& values, std::vector<int>& indexes){

            std::vector<size_t> p(dimensions.size(), 0);

            // Sort
            std::iota(p.begin(), p.end(), 0);
            std::sort(p.begin(), p.end(),
                      [&](size_t i, size_t j){ return ((values[i] / dimensions[i]) < (values[j] / dimensions[j])); });

            applySort3<T, W, int>(dimensions, values, indexes, p.size(), p);
        }

        inline void sortByDims(std::vector<T>& dimensions, std::vector<W>& values, std::vector<int>& indexes){

            std::vector<size_t> p(dimensions.size(), 0);

            // Sort
            std::iota(p.begin(), p.end(), 0);
            std::sort(p.begin(), p.end(),
                      [&](size_t i, size_t j){

                if (dimensions[i] == dimensions[j]) {
                    return values[i]/dimensions[i] < values[j]/dimensions[j];
                }

                return (dimensions[i] < dimensions[j]);
            });

            applySort3<T, W, int>(dimensions, values, indexes,  p.size(), p);
        }

        std::tuple<
        /* 0 constraints */ T,
        /* 1 lessCount */ int,
        /* 2 itemSum */  T,
        /* 3 lessCountSum */  T,
        /* 4 lessCountValuesSum */  W,
        /* 5 isSuperIncreasing */  bool,
        /* 6 allAsc */  bool,
        /* 7 allDesc */  bool,
        /* 8 canUsePartialSums */  bool
        >
                preProcess(
                        T& constraints,
                        std::vector<T>& items,
                        std::vector<W>& values,
                        bool& forceUseLimits,
                        std::vector<T> &lessSizeItems,
                        std::vector<W> &lessSizeValues,
                        std::vector<int> &lessSizeItemsIndex,
                        std::vector<T> &partialSums,
                        std::vector<bool> &superIncreasingItems
                        ){

            auto count = items.size();

            auto itemSum1 = EmptyDimension;
            auto itemSum2 = EmptyDimension;
            auto lessCountSum = EmptyDimension;

            W valuesSum1;
            W valuesSum2;
            W lessCountValuesSum;

            std::vector<T> partialSums1;
            std::vector<bool> superIncreasingItems1 = {false};
            std::vector<T> partialSums2;
            std::vector<bool> superIncreasingItems2 = {false};

            auto isSuperIncreasing1 = true; auto isSuperIncreasing2 = true;
            auto isSuperIncreasingValues1 = true; auto isSuperIncreasingValues2 = true;
            auto allValuesEqual = true; auto allValuesEqualToConstraints = true;
            auto allDesc = true; auto allAsc = true; auto allDescValues = true; auto allAscValues = true;

            auto canUsePartialSums = false;

            auto lessCount = 0;

            auto itemSum = EmptyDimension;
            bool isSuperIncreasing = false;

            if (count > 0)
            {
                auto prevItem1 = items[count - 1];
                auto prevValue1 = values[count - 1];

                for(auto i = 0; i < count; ++i) {

                    auto& item2 = items[i];
                    auto& itemValue2 = values[i];

                    auto iBack = count - i - 1;

                    auto& item1 = items[iBack];
                    auto& itemValue1 = values[iBack];

                    auto superIncreasingItem1 = false; auto superIncreasingItem2 = false;

                    if  (item1 <= constraints) {

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

                    if  (item2 <= constraints) {

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

                    //if (allValuesEqualToConstraints && item2.firstDimensionEqual(itemValue2) == false)
                    if (allValuesEqualToConstraints && item2 != itemValue2) {
                        allValuesEqualToConstraints = false;
                    }

                    itemSum1 += item1;
                    itemSum2 += item2;

                    valuesSum1 += itemValue1;
                    valuesSum2 += itemValue2;

                    partialSums1.push_back(itemSum2);
                    partialSums2.push_back(itemSum1);

                    if (allDesc){
                        if (! (prevItem1 <= item1)) {
                            allDesc = false;
                        }
                    }

                    if (allAsc) {
                        if (prevItem1 < item1) {
                            allAsc = false;
                        }
                    }

                    if (allDescValues) {
                        if (! prevValue1 <= itemValue1) {
                            allDescValues = false;
                        }
                    }

                    if (allAscValues) {
                        if (prevValue1 < itemValue1) {
                            allAscValues = false;
                        }
                    }

                    if (i > 0) {
                        superIncreasingItems1.push_back(superIncreasingItem1);
                        superIncreasingItems2.push_back(superIncreasingItem2);
                    }

                    if  (item2 <= constraints) {
                        lessSizeItems.push_back(item2);
                        lessSizeValues.push_back(itemValue2);
                        lessSizeItemsIndex.push_back(i);
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
                }
                else if  ((allDesc && canUsePartialSums) || forceUseLimits) {
                    partialSums.swap(partialSums1);
                    superIncreasingItems.swap(superIncreasingItems1);
                    isSuperIncreasing = isSuperIncreasing1;
                    itemSum = itemSum1;

                    std::reverse(partialSums.begin(), partialSums.end());
                    std::reverse(superIncreasingItems.begin(), superIncreasingItems.end());
                }
                else {
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

            //constraints = constraints.adjustMin(itemSum);

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
                T& constraints,
                std::vector<T>& lessSizeItems,
                std::vector<W>& lessSizeValues,
                std::vector<int>& lessSizeItemsIndex,
                T& lessCountSum,
                T& itemSum,
                W& lessCountValuesSum){

            W zero = EmptyValue;
            std::vector<T> emptyItems;
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

        inline int indexLargestLessThanAsc(std::vector<T>& items, T item, int lo, int hi) {

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

        inline int indexLargestLessThanDesc(std::vector<T>& items, T item, int lo, int hi) {

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

        KNAPSACK_RESULT  solveSuperIncreasing(T& size,
                                     std::vector<T>& items,
                                     std::vector<W>& values,
                                     std::vector<int>& itemsIndex,
                                     int count,
                                     bool allAsc) {

            int starting = 1;
            std::vector<T> resultItems;
            std::vector<W> resultValues;
            std::vector<int> resultIndex;
            W resultSum = EmptyValue;
            T resultItemSum = EmptyDimension;

            auto index = -1;

            if (allAsc) {
                index = indexLargestLessThanAsc(items, size, starting - 1, count - 1);
            } else {
                index = indexLargestLessThanDesc(items, size, starting - 1, count - 1);
            }

            while (index >= 0)
            {
                auto& item = items[index];
                auto& value = values[index];

                resultItems.push_back(item);
                resultValues.push_back(value);
                resultIndex.push_back(itemsIndex[index]);

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

        inline std::tuple<bool, T, T, T> getLimits(T& constraints,
                                            int i,
                                            std::vector<T>& items,
                                            std::vector<T>& partialSums,
                                            std::vector<bool>& superIncreasingItems,
                                            bool canUsePartialSums) {

            T partSumForItem;
            T oldPointLimit;
            T newPointLimit;

            if (!DoUseLimits || !canUsePartialSums) {
                return std::make_tuple(false, partSumForItem, oldPointLimit, newPointLimit);
            }

            partSumForItem = partialSums[i];

            bool superIncreasingItem;

            if (superIncreasingItems.size() > 0) {
                superIncreasingItem = superIncreasingItems[i];
            }

            newPointLimit = constraints - partSumForItem;
            oldPointLimit = newPointLimit;

            if (DoSolveSuperInc && newPointLimit && superIncreasingItem) {
                oldPointLimit = newPointLimit + items[i];
            }

            return std::make_tuple(true, partSumForItem, oldPointLimit, newPointLimit);
        }

        inline void iterateOrPushBack(W_POINT_DEQUEUE& circularPointQueue,
                                      W_POINT& newPoint,
                                      W_POINT_DEQUEUE& greaterQu,
                                      W_POINT_SET& distinctPoints2) {

            if (circularPointQueue.size() > 0) {

                if (newPoint.dimensions <= circularPointQueue.front().dimensions) {

                    circularPointQueue.push_back(newPoint);
                    distinctPoints2.insert(newPoint);
                } else {

                    if (greaterQu.size() > 0){

                        if (newPoint.dimensions <= greaterQu.front().dimensions)
                        {
                            greaterQu.push_front(newPoint);
                        }
                        else
                        {
                            greaterQu.push_back(newPoint);
                        }
                    }
                    else{

                        greaterQu.push_back(newPoint);
                    }
                }
            }
            else {
                circularPointQueue.push_back(newPoint);
                distinctPoints2.insert(newPoint);
            }
        }

        inline void iterateLessThanOldPoint(W_POINT& oldPoint,
                                            W_POINT_DEQUEUE& circularPointQueue,
                                            bool canUseLimits,
                                            W_POINT_DEQUEUE& greaterQu, T oldPointLimit,
                                            W_POINT_SET& distinctPoints2) {

            while (greaterQu.size() > 0 and greaterQu.front().dimensions < oldPoint.dimensions) {

                auto quPoint = greaterQu.front();
                greaterQu.pop_front();

                distinctPoints2.insert(quPoint);
                circularPointQueue.push_back(quPoint);
            }

            if ((canUseLimits == false) || (oldPoint.dimensions < oldPointLimit) == false) {
                iterateOrPushBack(circularPointQueue, oldPoint, greaterQu, distinctPoints2);
            }
        }

        inline void iterateGreaterPoints(W_POINT_DEQUEUE& greaterQu,
                                         W_POINT_DEQUEUE& circularPointQueue,
                                         W_POINT_SET& distinctPoints2){

            while (greaterQu.size() > 0) {

                auto quPoint = greaterQu.front();
                greaterQu.pop_front();

                circularPointQueue.push_back(quPoint);
                distinctPoints2.insert(quPoint);
            }
        }

        inline int getItemIndex(int count, int i, bool allAsc){

            return allAsc ? count - i : i - 1;
        }

        std::tuple<int, W_POINT> iteratePoints(
                int& i,
                SOURCE_LINK_LIST &sourcePoints,
                T& itemDimensions,
                W& itemProfit,
                int& itemId,
                T& constraintPoint,
                W_POINT& maxProfitPoint,
                W_POINT_DEQUEUE& circularPointQueue,
                int& prevCyclePointCount,
                T& halfConstraint,
                T& itemLimit,
                T& oldPointLimit,
                T& newPointLimit,
                W_POINT_SET& distinctPoints1,
                W_POINT_SET& distinctPoints2,
                bool canUseLimits) {

            // merges ordered visited points with new points with keeping order in iterCounter(N) using single circular queue.
            // getPoints method call starts fetching visited points from qu start, pops visited point and pushes new point and visited to the end of qu in ASC order.
            // skip new point if it in list already
            // points if they will not contribute to optimal solution (in case of desc flow and (equal values or values equal to first dimension))
            // also skips the same weight but less profit points

            W_POINT_DEQUEUE greaterQu;

            auto skipLimitCheck = canUseLimits == false;

            W_POINT itemPoint(itemDimensions, itemProfit);

            itemPoint.id = sourcePoints.size();
            source_link link(itemId, -1);
            sourcePoints.push_back(link);

            auto useItemItself = skipLimitCheck || itemLimit >= halfConstraint;

            if (useItemItself) {

                if  (distinctPoints1.contains(itemPoint) == false) {
                    iterateOrPushBack(circularPointQueue, itemPoint, greaterQu, distinctPoints2);
                }

                if (maxProfitPoint.profit <= itemPoint.profit) {
                    maxProfitPoint = itemPoint;
                }
            }

            for (auto pi = 0; pi < prevCyclePointCount; ++pi) {

                W_POINT oldPoint = circularPointQueue.front();

                circularPointQueue.pop_front();

                iterateLessThanOldPoint(oldPoint,
                                        circularPointQueue,
                                        canUseLimits,
                                        greaterQu,
                                        oldPointLimit,
                                        distinctPoints2);


                if (!(skipLimitCheck) && oldPoint.dimensions + itemPoint.dimensions < newPointLimit) {
                    continue;
                }

                if (oldPoint.dimensions + itemPoint.dimensions <= constraintPoint) {

                    W_POINT newPoint = oldPoint + itemPoint;

                    if (distinctPoints1.contains(newPoint) == false) {

                        newPoint.id = sourcePoints.size();
                        source_link link(itemId, oldPoint.id);
                        sourcePoints.push_back(link);

                        iterateOrPushBack(circularPointQueue, newPoint, greaterQu, distinctPoints2);

                        if (maxProfitPoint.profit <= newPoint.profit) {
                            if (maxProfitPoint.dimensions < newPoint.dimensions) {
                                maxProfitPoint = newPoint;
                            }
                        }
                    }
                }
            }

            iterateGreaterPoints(greaterQu, circularPointQueue, distinctPoints2);

            auto newPointCount = circularPointQueue.size();

            return std::make_tuple(newPointCount, maxProfitPoint);
        }

         W_POINT getNewPoints(
                int& i,
                W_POINT& maxProfitPoint,
                T& itemDimensions,
                W& itemProfit,
                int& itemId,
                W_POINT_LIST& oldPoints,
                W_POINT_LIST& result,
                T& constraint,
                W_POINT_SET& prevDistinctPoints,
                W_POINT_SET& newDistinctPoints,
                SOURCE_LINK_LIST& sourcePoints) {

            W_POINT itemPoint = W_POINT(itemDimensions, itemProfit);

            for(auto& oldPoint : oldPoints) {

                if (oldPoint.dimensions + itemPoint.dimensions <= constraint) {

                    auto newPoint = oldPoint + itemPoint;

                    newPoint.id = sourcePoints.size();
                    source_link link(itemId, oldPoint.id);
                    sourcePoints.push_back(link);

                    if (prevDistinctPoints.contains(newPoint) == false) {
                        newDistinctPoints.insert(newPoint);
                        result.push_back(newPoint);
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

            return maxProfitPoint;
        }

        KNAPSACK_RESULT solveUsingLimitsOnly(
                T constraint,
                std::vector<T> &sortedItems,
                std::vector<W> &sortedValues,
                std::vector<int> &sortedIndexes,
                bool allAsc,
                std::vector<T> &partialSums,
                std::vector<bool> &superIncreasingItems,
                bool canUsePartialSums) {

            W_POINT maxProfitPoint(EmptyDimension, EmptyValue);

            W_POINT_SET distinctPoints1;
            W_POINT_DEQUEUE circularPointQueue;

            SOURCE_LINK_LIST sourcePoints;

            sourcePoints.reserve(sortedItems.size() * sortedItems.size());

            int itemsCount = sortedItems.size();

            int prevPointCount = 0;

            auto halfConstraint = constraint / 2;

            for(int i = 1; i < itemsCount + 1; ++i) {

                auto itemIndex = getItemIndex(itemsCount, i, allAsc);

                auto itemDimensions =  sortedItems[itemIndex];
                auto itemProfit     =  sortedValues[itemIndex];
                auto itemId         =  sortedIndexes[itemIndex];

                auto limitParams = getLimits(constraint,
                                             itemIndex,
                                             sortedItems,
                                             partialSums,
                                             superIncreasingItems,
                                             canUsePartialSums);

                auto canUseLimits =  std::get<0>(limitParams);
                auto itemLimit =     std::get<1>(limitParams);
                auto oldPointLimit = std::get<2>(limitParams);
                auto newPointLimit = std::get<3>(limitParams);

                auto iterResult = iteratePoints(i,
                                                sourcePoints,
                                               itemDimensions,
                                               itemProfit,
                                               itemId,
                                               constraint,
                                               maxProfitPoint,
                                               circularPointQueue,
                                               prevPointCount,
                                               halfConstraint,
                                               itemLimit,
                                               oldPointLimit,
                                               newPointLimit,
                                               distinctPoints1,
                                               distinctPoints1,
                                              canUsePartialSums && canUseLimits
                                                              );

                auto newPointCount = std::get<0>(iterResult);
                auto maxProfitPoint = std::get<1>(iterResult);

                if (CanBackTraceWhenSizeReached && maxProfitPoint.dimensions == constraint) {
                    return backTraceItems(maxProfitPoint, sourcePoints);
                }

                prevPointCount = newPointCount;
            }

            return backTraceItems(maxProfitPoint, sourcePoints);
        }

        inline int indexLargestLessThan(W_POINT_LIST& items, W& item, int lo, int hi){

            int ans = -1;

            while (lo <= hi) {
                int mid = (lo + hi) / 2;

                auto val = items[mid];

                if (val.profit > item) {
                    hi = mid - 1;
                    ans = mid;
                } else {
                    lo = mid + 1;
                }
            }

            return ans;
        }

        inline int findLargerProfit(W_POINT_LIST& items, W& profitMax) {

            auto index = indexLargestLessThan(items, profitMax, 0, items.size() - 1);

            if (index >= 0 && items[index].profit > profitMax) {
                return index;
            }
            else {
                return -1;
            }
        }

        void mergeDiscardingDominated(W_POINT_LIST& result, W_POINT_LIST& oldList, W_POINT_LIST& newList) {

            W profitMax = MinValue;

            while(true) {

                auto oldPointIndex = findLargerProfit(oldList, profitMax);
                auto newPointIndex = findLargerProfit(newList, profitMax);

                if (oldPointIndex == -1) {
                    if (newPointIndex >= 0) {
                        for (int ind = newPointIndex; ind < newList.size(); ++ind) {

                            result.push_back(newList[ind]);
                        }
                    }
                    break;
                }

                if (newPointIndex == -1) {
                    if (oldPointIndex >= 0) {
                        for (int ind = oldPointIndex; ind < oldList.size(); ++ind) {

                            result.push_back(oldList[ind]);
                        }
                    }
                    break;
                }

                W_POINT& oldPoint = oldList[oldPointIndex];
                W_POINT& newPoint = newList[newPointIndex];

                if (oldPoint.dimensions < newPoint.dimensions
                || (oldPoint.dimensions == newPoint.dimensions && oldPoint.profit > newPoint.profit)) {

                    result.push_back(oldPoint);
                    profitMax = oldPoint.profit;
                } else {

                    result.push_back(newPoint);
                    profitMax = newPoint.profit;
                }
            }
        }

        KNAPSACK_RESULT backTraceItems(W_POINT& maxProfitPoint, SOURCE_LINK_LIST &sourcePoints) {

            W zeroProfit = EmptyValue;
            std::vector<T> optItems;
            std::vector<W> optValues;
            std::vector<int> optIndexes;

            auto optSize = EmptyDimension;

            if (maxProfitPoint.profit > 0)
            {
                auto maxProfit = maxProfitPoint.profit;

                source_link pointLink = sourcePoints[maxProfitPoint.id];

                while (true) {
                    optItems.push_back(Dimensions[pointLink.itemId]);
                    optValues.push_back(Values[pointLink.itemId]);
                    optIndexes.push_back(Ids[pointLink.itemId]);
                    optSize += Dimensions[pointLink.itemId];

                    if (!pointLink.hasParent()){
                        break;
                    }

                    pointLink = sourcePoints[pointLink.parentId];
                }

                return std::make_tuple(maxProfit, optSize, optItems, optValues, optIndexes);
            }

            return std::make_tuple(zeroProfit, EmptyDimension, optItems, optValues, optIndexes);
        }

        KNAPSACK_RESULT solvePareto(
                T& constraint,
                std::vector<T>& sortedItems,
                std::vector<W>& sortedValues,
                std::vector<int>& sortedIndexes) {

            W_POINT maxProfitPoint(EmptyDimension, EmptyValue);
            W_POINT emptyPoint(EmptyDimension, EmptyValue);

            W_POINT_SET distinctPoints;

            W_POINT_LIST oldPoints = {emptyPoint};
            W_POINT_LIST newPoints;
            W_POINT_LIST paretoOptimal;

            SOURCE_LINK_LIST sourcePoints;

            sourcePoints.reserve(sortedItems.size() * sortedItems.size());

            auto itemsCount = sortedItems.size();

            for(int i = 1; i < itemsCount + 1; ++i) {

                auto itemDimensions = sortedItems[i - 1];
                auto itemProfit = sortedValues[i - 1];
                auto itemId = sortedIndexes[i - 1];

                newPoints.clear();

                maxProfitPoint = getNewPoints(i,
                                                   maxProfitPoint,
                                                   itemDimensions,
                                                   itemProfit,
                                                   itemId,
                                                   oldPoints,
                                                   newPoints,
                                                   constraint,
                                                   distinctPoints,
                                                   distinctPoints,
                                                   sourcePoints);

                paretoOptimal.clear();

                // Point A is dominated by point B if B achieves a larger profit with the same or less weight than A.
                mergeDiscardingDominated(paretoOptimal, oldPoints, newPoints);

                if (CanBackTraceWhenSizeReached and maxProfitPoint.dimensions == constraint) {
                    return backTraceItems(maxProfitPoint, sourcePoints);
                }

                oldPoints.swap(paretoOptimal); // oldPoints = paretoOptimal;
            }

            return backTraceItems(maxProfitPoint, sourcePoints);
        }
    };
}
#endif
