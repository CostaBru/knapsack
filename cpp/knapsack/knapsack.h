#ifndef knapsack_H
#define knapsack_H

#define PARETO_SET robin_hood::unordered_set<pareto_point<T, W>, pareto_point_hash<T, W>, pareto_point_key_equals<T, W>>

#define PARETO_DEQUEUE std::deque<pareto_point<T, W>>

#define PARETO_POINT pareto_point<T, W>

#define PARETO_LIST std::vector<pareto_point<T, W>>

#define KNAPSACK_RESULT std::tuple<W, T, std::vector<T>, std::vector<W>, std::vector<int>>

#include "fast_map.h"
#include <vector>
#include <tuple>
#include <cmath>
#include <deque>
#include <numeric>
#include <ranges>

namespace kb_knapsack {

    template<typename T>
    struct w_point {
    public:
        T value;

        w_point(){
        }

        w_point(T dim){
            value = dim;
        }

        w_point adjustMin(w_point p){
            if (p.value < value){
                return w_point(p.value);
            }

            return w_point(value);
        }

        w_point divideBy(){
            return w_point(value/2);
        }

        friend bool operator>(const w_point &c1, const w_point &c2) {
            return c1.value > c2.value;
        }

        friend bool operator<=(const w_point &c1, const w_point &c2) {
            return c1.value <= c2.value;
        }

        friend bool operator<(const w_point &c1, const w_point &c2) {
            return c1.value < c2.value;
        }

        friend bool operator>=(const w_point &c1, const w_point &c2) {
            return c1.value >= c2.value;
        }

        friend bool operator==(const w_point &c1, const w_point &c2) {
            return c1.value == c2.value;
        }

        friend bool operator!=(const w_point &c1, const w_point &c2) {
            return c1.value != c2.value;
        }

        friend bool operator+(const w_point &c1, const w_point &c2) {
            return w_point(c1.value + c2.value);
        }
    };


    template<typename T, typename W>
    class pareto_point {
    public:
        T dimensions;
        W profit;
        int itemId = 0;
        const pareto_point<T, W>* source = nullptr;

        pareto_point(){
        }

        pareto_point(T dims, W value, int id){
            dimensions = dims;
            profit = value;
            itemId = id;
        }

        W getProfit(){
            return profit;
        }

        bool hasSource(){
            return source != nullptr;
        }

        bool isDimensionEquals(T dim){
            return dimensions == dim;
        }

        friend pareto_point operator+(const pareto_point &c1, const pareto_point &c2) {
            auto p = pareto_point(c1.dimensions + c2.dimensions, c1.profit + c2.profit, c2.itemId);
            p.source = &c1;
            return p;
        }
    };

    template<typename T, typename W>
    struct pareto_point_hash
    {
        std::size_t operator()(const pareto_point<T, W>& k) const
        {
            using std::hash;

            return ((hash<T>()(k.dimensions) ^ (hash<W>()(k.profit) << 1)) >> 1);
        }
    };

    template<typename T, typename W>
    struct pareto_point_key_equals
    {
        bool operator()(const pareto_point<T, W>& k1, const pareto_point<T, W>& k2) const
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

        T m_constraints;
        T m_emptyDimension;
        W m_emptyValue;
        std::vector<T> m_dimensions;
        std::vector<W> m_values;
        std::vector<int> m_indexes;
        bool m_forceUseLimits = false;
        bool m_doSolveSuperInc = true;
        bool m_doUseLimits= true;
        bool m_useRatioSort= true;
        bool m_canBackTraceWhenSizeReached = false;
        bool m_forceUsePareto = false;

        void sortByRatio(std::vector<T>& dimensions, std::vector<W>& values, std::vector<int>& indexes){

            std::vector<size_t> p(dimensions.size(), 0);

            // Sort
            std::iota(p.begin(), p.end(), 0);
            std::sort(p.begin(), p.end(),
                      [&](size_t i, size_t j){ return ((values[i] / dimensions[i]) < (values[j] / dimensions[j])); });

            applySort3<T, W, int>(dimensions, values, indexes, p.size(), p);
        }

        void sortByDims(std::vector<T>& dimensions, std::vector<W>& values, std::vector<int>& indexes){

            std::vector<size_t> p(dimensions.size(), 0);

            // Sort
            std::iota(p.begin(), p.end(), 0);
            std::sort(p.begin(), p.end(),
                      [&](size_t i, size_t j){ return (dimensions[i] < dimensions[j]); });

            applySort3<T, W, int>(dimensions, values, indexes,  p.size(), p);
        }

        KNAPSACK_RESULT Solve(){

            auto canTrySolveUsingDp = not m_forceUsePareto and (m_doUseLimits or m_doSolveSuperInc or m_forceUseLimits or m_canBackTraceWhenSizeReached);

            auto canSolveUsingDp = false;
            auto lessSizeItems = m_dimensions;
            auto lessSizeValues = m_values;
            auto lessSizeItemsIndex = m_indexes;

            T constraints = m_constraints;

            if (canTrySolveUsingDp) {

                auto params = preProcess(m_constraints, m_dimensions, m_values, m_forceUseLimits);

                constraints = std::get<0>(params);
                auto count = std::get<1>(params);
                lessSizeItems = std::get<2>(params);
                lessSizeValues = std::get<3>(params);
                lessSizeItemsIndex = std::get<4>(params);
                auto lessCountSum = std::get<5>(params);
                auto itemSum = std::get<6>(params);
                auto lessCountValuesSum = std::get<7>(params);
                auto partialSums = std::get<8>(params);
                auto isSuperIncreasing = std::get<9>(params);
                auto superIncreasingItems = std::get<10>(params);
                auto allAsc = std::get<11>(params);
                auto allDesc = std::get<12>(params);
                auto canUsePartialSums = std::get<13>(params);

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

                if (m_doSolveSuperInc && isSuperIncreasing) {

                    return solveSuperIncreasing(constraints,
                                                lessSizeItems,
                                                lessSizeValues,
                                                lessSizeItemsIndex,
                                                count,
                                                allAsc);
                }

                bool canSolveUsingDp = ! m_forceUsePareto && (m_forceUseLimits || m_canBackTraceWhenSizeReached || canUsePartialSums);

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
            }

            std::vector<T> sortedItems(lessSizeItems);
            std::vector<W> sortedValues(lessSizeValues);
            std::vector<int> sortedIndexes(lessSizeItemsIndex);

            if (m_useRatioSort){
                sortByRatio(sortedItems, sortedValues, sortedIndexes);
            } else {
                sortByDims(sortedItems, sortedValues, sortedIndexes);
            }

            return solvePareto(constraints, sortedItems, sortedValues, sortedIndexes);
        }

        std::tuple<
        /* 0 constraints */ T,
        /* 1 lessCount */ int,
        /* 2 lessSizeItems */ std::vector<T>,
        /* 3 lessSizeValues */ std::vector<W>,
        /* 4 lessSizeItemsIndex */ std::vector<int>,
        /* 5 itemSum */  T,
        /* 6 lessCountSum */  T,
        /* 7 lessCountValuesSum */  W,
        /* 8 partialSums */  std::vector<T>,
        /* 9 isSuperIncreasing */  bool,
        /* 10 superIncreasingItems */  std::vector<bool>,
        /* 11 allAsc */  bool,
        /* 12 allDesc */  bool,
        /* 13 canUsePartialSums */  bool
        >
                preProcess(T& constraints, std::vector<T>& items, std::vector<W>& values, bool& forceUseLimits){

            auto count = items.size();

            auto itemSum1 = m_emptyDimension;
            auto itemSum2 = m_emptyDimension;
            auto lessCountSum = m_emptyDimension;

            W valuesSum1;
            W valuesSum2;
            W lessCountValuesSum;

            std::vector<T> lessSizeItems;
            std::vector<W> lessSizeValues;
            std::vector<int> lessSizeItemsIndex;

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

            auto itemSum = m_emptyDimension;
            std::vector<T> partialSums;
            bool isSuperIncreasing;
            std::vector<bool> superIncreasingItems;

            if (count > 0)
            {
                auto prevItem1 = *items.end();
                auto prevValue1 = *values.end();

                for(auto i = 0; i < count; ++i) {

                    auto item2 = items[i];
                    auto itemValue2 = values[i];

                    auto iBack = count - i - 1;

                    auto item1 = items[iBack];
                    auto itemValue1 = values[iBack];

                    auto superIncreasingItem1 = false; auto superIncreasingItem2 = false;

                    if  (item1 <= constraints) {

                        if (item1 < itemSum1)
                        {
                            isSuperIncreasing1 = false;
                        }
                        else
                        {
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
                        }
                        else {
                            superIncreasingItem2 = true;
                        }

                        if (itemValue2 < valuesSum2) {
                            isSuperIncreasingValues2 = false;
                            superIncreasingItem2 = false;
                        }
                    }

                    if (allValuesEqual && prevValue1 != itemValue2)
                    {
                        allValuesEqual = false;
                    }

                    //if (allValuesEqualToConstraints && item2.firstDimensionEqual(itemValue2) == false)
                    if (allValuesEqualToConstraints && item2 != itemValue2)
                    {
                        allValuesEqualToConstraints = false;
                    }

                    itemSum1 += item1;
                    itemSum2 += item2;

                    valuesSum1 += itemValue1;
                    valuesSum2 += itemValue2;

                    partialSums1.push_back(itemSum2);
                    partialSums2.push_back(itemSum1);

                    if (allDesc){
                        if (! prevItem1 <= item1) {
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
                    partialSums = partialSums2;
                    superIncreasingItems = superIncreasingItems2;
                    isSuperIncreasing = isSuperIncreasing2;
                    itemSum = itemSum2;
                }
                else if  ((allDesc && canUsePartialSums) || forceUseLimits) {
                    partialSums = partialSums1;
                    superIncreasingItems = superIncreasingItems1;
                    isSuperIncreasing = isSuperIncreasing1;
                    itemSum = itemSum1;

                    std::reverse(partialSums.begin(), partialSums.end());
                    std::reverse(superIncreasingItems.begin(), superIncreasingItems.end());
                }
                else {
                    if (allAsc and allAscValues) {
                        itemSum = itemSum2;
                        partialSums = partialSums2;
                        std::reverse(partialSums.begin(), partialSums.end());
                        superIncreasingItems = superIncreasingItems2;
                        std::reverse(superIncreasingItems.begin(), superIncreasingItems.end());
                        canUsePartialSums = true;
                    } else if (allDesc and allDescValues) {
                        itemSum = itemSum1;
                        partialSums = partialSums1;
                        std::reverse(partialSums.begin(), partialSums.end());
                        superIncreasingItems = superIncreasingItems1;
                        std::reverse(superIncreasingItems.begin(), superIncreasingItems.end());
                        canUsePartialSums = true;
                    } else {
                        itemSum = itemSum2;
                        superIncreasingItems = {};
                        if (!canUsePartialSums) {
                            partialSums = {};
                            canUsePartialSums = false;
                        } else {
                            partialSums = partialSums2;
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
                                   lessSizeItems,
                                   lessSizeValues,
                                   lessSizeItemsIndex,
                                   itemSum,
                                   lessCountSum,
                                   lessCountValuesSum,
                                   partialSums,
                                   isSuperIncreasing,
                                   superIncreasingItems,
                                   allAsc,
                                   allDesc,
                                   canUsePartialSums);
        }

        std::tuple<bool, KNAPSACK_RESULT> checkCornerCases(
                T& constraints,
                std::vector<T>& lessSizeItems,
                std::vector<W>& lessSizeValues,
                std::vector<int>& lessSizeItemsIndex,
                T& lessCountSum,
                T& itemSum,
                W& lessCountValuesSum){

            W zero = m_emptyValue;
            std::vector<T> emptyItems;
            std::vector<W> emptyValues;
            std::vector<int> emptyIndexes;

            if  (lessCountSum == m_emptyDimension) {
                return std::make_tuple(true, std::make_tuple(zero, m_emptyDimension, emptyItems, emptyValues, emptyIndexes));
            }

            if  (lessCountSum <= constraints) {
                return std::make_tuple(true, std::make_tuple(lessCountValuesSum, lessCountSum, lessSizeItems, lessSizeValues, lessSizeItemsIndex));
            }

            if  (itemSum <= constraints) {
                return std::make_tuple(true, std::make_tuple(lessCountValuesSum, itemSum, lessSizeItems, lessSizeValues, lessSizeItemsIndex));
            }

            return std::make_tuple(false, std::make_tuple(zero, m_emptyDimension, emptyItems, emptyValues, emptyIndexes));
        }

        int indexLargestLessThanAsc(std::vector<T>& items, T item, int lo, int hi) {

            if (item == m_emptyDimension)
            {
                return -1;
            }

            while (lo <= hi) {
                int mid = (lo + hi) / 2;

                auto val = items[mid];

                if (item == val)
                {
                    return mid;
                }

                if (val < item)
                {
                    lo = mid + 1;
                }
                else
                {
                    hi = mid - 1;
                }
            }

            if (hi >= 0 and item >= items[hi])
            {
                return hi;
            }
            else
            {
                return -1;
            }
        }

        int indexLargestLessThanDesc(std::vector<T>& items, T item, int lo, int hi) {

            if (item == m_emptyDimension)
            {
                return -1;
            }

            auto cnt = items.size();

            while (lo <= hi) {
                int mid = (lo + hi) / 2;

                auto val = items[mid];

                if (item == val)
                {
                    return mid;
                }

                if (val > item)
                {
                    lo = mid + 1;
                }
                else
                {
                    hi = mid - 1;
                }
            }

            if (lo < cnt && item >= items[lo])
            {
                return lo;
            }
            else
            {
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
            W resultSum;
            T resultItemSum = m_emptyDimension;

            auto index = -1;

            if (allAsc) {
                index = indexLargestLessThanAsc(items, size, starting - 1, count - 1);
            } else {
                index = indexLargestLessThanDesc(items, size, starting - 1, count - 1);
            }

            while (index >= 0)
            {
                auto item = items[index];
                auto value = values[index];

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

        std::tuple<bool, T, T, T> getLimits(T& constraints,
                                            int i,
                                            std::vector<T>& items,
                                            std::vector<T>& partialSums,
                                            std::vector<bool>& superIncreasingItems,
                                            bool canUsePartialSums) {

            T partSumForItem;
            T oldPointLimit;
            T newPointLimit;

            if (!m_doUseLimits || !canUsePartialSums) {
                return std::make_tuple(false, partSumForItem, oldPointLimit, newPointLimit);
            }

            partSumForItem = partialSums[i];

            bool superIncreasingItem;

            if (superIncreasingItems.size() > 0) {
                superIncreasingItem = superIncreasingItems[i];
            }

            newPointLimit = constraints - partSumForItem;
            oldPointLimit = newPointLimit;

            if (m_doSolveSuperInc && newPointLimit && superIncreasingItem) {
                oldPointLimit = newPointLimit + items[i];
            }

            return std::make_tuple(true, partSumForItem, oldPointLimit, newPointLimit);
        }

        void iterateOrPushBack(PARETO_DEQUEUE& circularPointQueue,
                               PARETO_POINT& newPoint,
                               PARETO_DEQUEUE& greaterQu,
                               PARETO_SET& distinctPoints2) {

            if (circularPointQueue.size() > 0) {
                auto peek = circularPointQueue.front();

                if (newPoint.dimensions <= peek.dimensions) {

                    circularPointQueue.push_back(newPoint);
                    distinctPoints2.insert(newPoint);
                } else {

                    if (greaterQu.size() > 0){
                        auto greaterQuPeek = greaterQu.front();
                        if (newPoint.dimensions <= greaterQuPeek.dimensions)
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

        void iterateLessThanOldPoint(PARETO_POINT& oldPoint,
                                     PARETO_DEQUEUE& circularPointQueue,
                                     bool canUseLimits,
                                     PARETO_DEQUEUE& greaterQu, T oldPointLimit,
                                     PARETO_SET& distinctPoints2) {

            while (greaterQu.size() > 0 and greaterQu.front().dimensions < oldPoint.dimensions) {

                auto quPoint = greaterQu.front();
                greaterQu.pop_front();

                distinctPoints2.insert(quPoint);
                circularPointQueue.push_back(quPoint);

                if ((canUseLimits == false) || (oldPoint.dimensions < oldPointLimit) == false) {
                    iterateOrPushBack(circularPointQueue, oldPoint, greaterQu, distinctPoints2);
                }
            }
        }

        void iterateGreaterPoints(PARETO_DEQUEUE& greaterQu,
                                  PARETO_DEQUEUE& circularPointQueue,
                                  PARETO_SET& distinctPoints2){

            while (greaterQu.size() > 0) {

                auto quPoint = greaterQu.front();
                greaterQu.pop_front();

                circularPointQueue.push_back(quPoint);
                distinctPoints2.insert(quPoint);
            }
        }

        int getItemIndex(int count, int i, int allAsc){

            return allAsc ? count - i : i - 1;
        }

        std::tuple<int, PARETO_POINT> iteratePoints(
                int& i,
                T& itemDimensions,
                W& itemProfit,
                int& itemId,
                T& constraintPoint,
                PARETO_POINT& maxProfitPoint,
                PARETO_DEQUEUE& circularPointQueue,
                int& prevCyclePointCount,
                T& halfConstraint,
                T& itemLimit,
                T& oldPointLimit,
                T& newPointLimit,
                PARETO_SET& distinctPoints1,
                PARETO_SET& distinctPoints2,
                bool canUseLimits) {

            // merges ordered visited points with new points with keeping order in iterCounter(N) using single circular queue.
            // getPoints method call starts fetching visited points from qu start, pops visited point and pushes new point and visited to the end of qu in ASC order.
            // skip new point if it in list already
            // points if they will not contribute to optimal solution (in case of desc flow and (equal values or values equal to first dimension))
            // also skips the same weight but less profit points

            PARETO_DEQUEUE greaterQu;

            auto skipLimitCheck = canUseLimits == false;

            PARETO_POINT itemPoint(itemDimensions, itemProfit, itemId);

            auto useItemItself = true;

            if (useItemItself) {

                if  (distinctPoints1.contains(itemPoint) == false) {
                    iterateOrPushBack(circularPointQueue, itemPoint, greaterQu, distinctPoints2);
                }

                if (maxProfitPoint.getProfit() <= itemPoint.getProfit()) {
                    maxProfitPoint = itemPoint;
                }
            }

            for (auto pi = 0; pi < prevCyclePointCount; ++pi) {

                PARETO_POINT oldPoint = circularPointQueue.front();

                circularPointQueue.pop_front();

                iterateLessThanOldPoint(oldPoint,
                                        circularPointQueue,
                                        canUseLimits,
                                        greaterQu,
                                        oldPointLimit,
                                        distinctPoints2);

                PARETO_POINT newPoint = oldPoint + itemPoint;

                if (!(skipLimitCheck) && newPoint.dimensions < newPointLimit) {
                    continue;
                }

                if (newPoint.dimensions <= constraintPoint) {
                    if (distinctPoints1.contains(newPoint) == false) {

                        iterateOrPushBack(circularPointQueue, newPoint, greaterQu, distinctPoints2);

                        if (maxProfitPoint.getProfit() <= newPoint.getProfit()) {
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

        std::tuple<PARETO_LIST, PARETO_POINT> getNewPoints(
                int& i,
                PARETO_POINT& maxProfitPoint,
                T& itemDimensions,
                W& itemProfit,
                int& itemId,
                PARETO_LIST& oldPoints,
                T& constraint,
                PARETO_SET& prevDistinctPoints,
                PARETO_SET& newDistinctPoints) {

            PARETO_LIST result;

            PARETO_POINT itemPoint = pareto_point(itemDimensions, itemProfit, itemId);

            for(const auto oldPoint : oldPoints) {
                PARETO_POINT newPoint = oldPoint + itemPoint;

                if (newPoint.dimensions <= constraint) {

                    if (prevDistinctPoints.contains(newPoint) == false) {
                        newDistinctPoints.insert(newPoint);
                        result.push_back(newPoint);
                    }
                }

                if (m_useRatioSort) {

                    if (maxProfitPoint.getProfit() <= newPoint.getProfit() && maxProfitPoint.dimensions < newPoint.dimensions) {
                        maxProfitPoint = newPoint;
                    }

                }  else {
                    if (maxProfitPoint.getProfit() <= newPoint.getProfit()) {
                        maxProfitPoint = newPoint;
                    }
                }
            }

            return std::make_tuple(result, maxProfitPoint);
        }

        KNAPSACK_RESULT solveUsingLimitsOnly(
                T constraint,
                std::vector<T> sortedItems,
                std::vector<W> sortedValues,
                std::vector<int> sortedIndexes,
                bool allAsc,
                std::vector<T> partialSums,
                std::vector<bool> superIncreasingItems,
                bool canUsePartialSums) {

            PARETO_SET distinctPoints1;

            int itemsCount = sortedItems.size();

            W zeroValue = m_emptyValue;
            pareto_point maxProfitPoint(m_emptyDimension, zeroValue, 0);

            PARETO_DEQUEUE circularPointQueue;

            int prevPointCount = 0;

            auto halfConstraint = constraint / 2;

            for(int i = 1; i < itemsCount + 1; ++i) {

                auto itemIndex = getItemIndex(itemsCount, i, allAsc);

                auto itemDimensions =  sortedItems[itemIndex];
                auto itemProfit = sortedValues[itemIndex];
                auto itemId =  sortedIndexes[itemIndex];

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

                if (m_canBackTraceWhenSizeReached && maxProfitPoint.isDimensionEquals(constraint)) {
                    return backTraceItems(maxProfitPoint, itemsCount);
                }

                prevPointCount = newPointCount;
            }


            return backTraceItems(maxProfitPoint, itemsCount);
        }

        int indexLargestLessThan(PARETO_LIST& items, W& item, int lo, int hi){

            int ans = -1;

            while (lo <= hi) {
                int mid = (lo + hi) / 2;

                auto val = items[mid];

                if (val.getProfit() > item) {
                    hi = mid - 1;
                    ans = mid;
                } else {
                    lo = mid + 1;
                }
            }

            return ans;
        }

        int findLargerProfit(PARETO_LIST& items, W& profitMax) {

            auto index = indexLargestLessThan(items, profitMax, 0, items.size() - 1);

            if (index >= 0 && items[index].getProfit() > profitMax) {
                return index;
            }
            else {
                return -1;
            }
        }

        PARETO_LIST mergeDiscardingDominated(PARETO_LIST& oldList, PARETO_LIST& newList) {

            PARETO_LIST result;
            W profitMax;

            while(true) {

                auto oldPointIndex = findLargerProfit(oldList, profitMax);
                auto newPointIndex = findLargerProfit(newList, profitMax);

                if (oldPointIndex == -1) {

                    if (newPointIndex >= 0) {
                        for (int ind = 0; ind < newList.size(); ++ind) {

                            auto newPoint = newList[ind];
                            result.push_back(newPoint);
                        }
                    }
                    break;
                }

                if (newPointIndex == -1) {
                    if (oldPointIndex >= 0) {
                        for (int ind = oldPointIndex; ind < oldList.size(); ++ind) {

                            auto oldPoint = oldList[ind];
                            result.push_back(oldPoint);
                        }
                    }
                    break;
                }

                auto oldPoint = oldList[oldPointIndex];
                auto newPoint = newList[newPointIndex];

                if (oldPoint.dimensions < newPoint.dimensions || (oldPoint.dimensions == newPoint.dimensions && oldPoint.getProfit() > newPoint.getProfit())) {

                    result.push_back(oldPoint);
                    profitMax = oldPoint.getProfit();
                } else {

                    result.push_back(newPoint);
                    profitMax = newPoint.getProfit();
                }
            }

            return result;
        }

        KNAPSACK_RESULT backTraceItems(pareto_point<W, T>& maxProfitPoint, int count) {

            W zeroProfit = m_emptyValue;
            std::vector<T> optItems;
            std::vector<W> optValues;
            std::vector<int> optIndexes;

            auto optSize = m_emptyDimension;

            if (maxProfitPoint.getProfit() > 0)
            {
                auto maxProfit = maxProfitPoint.getProfit();

                pareto_point<W, T> point = maxProfitPoint;

                while (true) {
                    auto id = point.itemId;

                    optItems.push_back(m_dimensions[id]);
                    optValues.push_back(m_values[id]);
                    optIndexes.push_back(m_indexes[id]);
                    optSize += m_dimensions[id];

                    if (point.hasSource()) {
                        point = *point.source;
                    }
                    else{
                        break;
                    }
                }

                return std::make_tuple(maxProfit, optSize, optItems, optValues, optIndexes);
            }

            return std::make_tuple(zeroProfit, m_emptyDimension, optItems, optValues, optIndexes);
        }

        KNAPSACK_RESULT solvePareto(
                T& constraint,
                std::vector<T>& sortedItems,
                std::vector<W>& sortedValues,
                std::vector<int>& sortedIndexes) {

            W zeroValue = m_emptyValue;
            pareto_point<W, T> maxProfitPoint(m_emptyDimension, zeroValue, 0);
            pareto_point<W, T> emptyPoint(m_emptyDimension, zeroValue, 0);

            PARETO_SET distinctPoints;

            PARETO_LIST oldPoints = {emptyPoint};
            PARETO_LIST newPoints;

            auto itemsCount = sortedItems.size();

            for(int i = 1; i < itemsCount + 1; ++i) {

                auto itemDimensions = sortedItems[i - 1];
                auto itemProfit = sortedValues[i - 1];
                auto itemId = sortedIndexes[i - 1];

                auto newPointResult = getNewPoints(i,
                                                   maxProfitPoint,
                                                   itemDimensions,
                                                   itemProfit,
                                                   itemId,
                                                   oldPoints,
                                                   constraint,
                                                   distinctPoints,
                                                   distinctPoints);

                auto newPoints = std::get<0>(newPointResult);
                auto maxProfitPoint = std::get<1>(newPointResult);

                // Point A is dominated by point B if B achieves a larger profit with the same or less weight than A.
                auto paretoOptimal = mergeDiscardingDominated(oldPoints, newPoints);

                if (m_canBackTraceWhenSizeReached and maxProfitPoint.isDimensionEquals(constraint)) {
                    return backTraceItems(maxProfitPoint, itemsCount);
                }

                oldPoints = paretoOptimal;
            }

            return backTraceItems(maxProfitPoint, itemsCount);
        }
    };
}
#endif
