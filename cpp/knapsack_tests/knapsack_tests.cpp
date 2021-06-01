#include "ut.h"
#include <API.h>
#include "paths.h"
#include <string>
#include <fstream>
#include <filesystem>
#include <experimental/array>
#include <chrono>

#define make_arr std::experimental::make_array

void print(std::string str){
    std::cout << str << std::endl;
}


template<typename T, typename W, int N>
std::tuple<W, std::array<T, N>, std::vector<std::array<T, N>>, std::vector<W>, std::vector<int>>
                                knapsackN(std::array<T, N>& constraint,
                                          std::vector<std::array<T, N>>& dimensions,
                                          std::vector<W>& values,
                                          std::vector<int>& indexes,
                                          bool doSolveSuperInc = true,
                                          bool doUseLimits = true,
                                          bool canBackTraceWhenSizeReached = false) {

    auto dims = std::vector<kb_knapsack::w_point_dimN<T, W, N>>();

    for(auto i = 0; i < dimensions.size(); ++i){

        dims.emplace_back(kb_knapsack::w_point_dimN<T, W, N>(dimensions[i]));
    }

    kb_knapsack::knapsack_solver<T, W, N, kb_knapsack::w_point_dimN> solver(dims, values, indexes);

    std::array<T, N> emptyDim;

    for (int i = 0; i < N; ++i) {
        emptyDim[i] = 0;
    }

    solver.EmptyDimension = kb_knapsack::w_point_dimN<T, W, N>(emptyDim);
    solver.EmptyValue = 0;
    solver.MinValue = -999999999;

    solver.Constraints = kb_knapsack::w_point_dimN<T, W, N>(constraint);

    solver.DoSolveSuperInc = doSolveSuperInc;
    solver.DoUseLimits = doUseLimits;
    solver.CanBackTraceWhenSizeReached = canBackTraceWhenSizeReached;

    auto rez = solver.Solve();

    auto optValue =   std::get<0>(rez);
    auto optSize =    std::get<1>(rez);
    auto optDim =     std::get<2>(rez);
    auto optValue2 =  std::get<3>(rez);
    auto optIndexes = std::get<4>(rez);

    std::vector<std::array<T, N>> optDimRez(optDim.size());

    for(auto i = 0; i < optDim.size(); ++i){
        optDimRez[i] = optDim[i].value;
    }

    return std::make_tuple(optValue, optSize.value, optDimRez, optValue2, optIndexes);
}

template<typename T>
bool listValuesEqual(std::vector<T> &l1, std::vector<T>& l2) {
    std::sort(l1.begin(), l1.end());
    std::sort(l2.begin(), l2.end());

    bool good = l1.size() == l2.size();

    for (int i = 0; i < l1.size() && i < l2.size(); ++i) {

        auto eq = l1[i] == l2[i];

        if (!eq) {
            std::cout << "Not eq" << i << " " << l1[i] << "!=" << l2[i] << std::endl;
        }

        good = eq && good;
    }
    return good;
}

bool verbose = true;

void test_1_rational_numbers() {
    if (verbose)
    {
        print("Rational numbers tests for 1-0 knapsack1.");
    }

    std::vector<double> A = { 0.2,
                              1.200001,
                              2.9000001,
                              3.30000009,
                              4.3,
                              5.5,
                              6.6,
                              7.7,
                              8.8,
                              9.8};

    std::sort(A.begin(), A.end(), std::greater());

    double s = 10.5;
    double expectedValue = 10.20000109;

    std::vector<int> indexes(A.size(), 0);
    std::iota(indexes.begin(), indexes.end(), 0);

    auto result = kb_knapsack::knapsack1(s, A, A, indexes);

    auto opt1 = std::get<0>(result);
    auto optSize = std::get<1>(result);

    boost::ut::expect(opt1 == expectedValue) << "Not equal ";
    boost::ut::expect(optSize <= s) << "Greater than size ";
}

void testSilvano(std::vector<int> W, std::vector<int> V, std::vector<int> R, int c){
    std::vector<int> ws(W);
    std::vector<int> vs(V);
    std::vector<int> indexes(W.size(), 0);
    std::iota(indexes.begin(), indexes.end(), 0);

    kb_knapsack::tools::sortReverse(ws, vs, indexes);

    int expectedSV = 0;
    int expectedSW = 0;

    int ind = 0;
    for(int i : R) {
        if (i == 1) {
            expectedSV += V[ind];
            expectedSW += W[ind];
        }
        ind += 1;
    }

    auto result = kb_knapsack::knapsack1(c, ws, vs, indexes);

    auto opt1 = std::get<0>(result);

    boost::ut::expect(opt1 == expectedSV) << "Not equal ";
}

template<typename T, int N, int FIELD>
struct fieldFunctor : public std::binary_function<T, std::array<T, N> , T>
{
    T operator()(T total, const std::array<T, N>& elem) const
    {
        return total + elem[FIELD];
    }
};

template<typename T, int N>
bool allLessOrEqual(std::array<T, N> &arr1, std::array<T, N> &arr2){
    for(int i = 0; i < N; ++i) {
        if (arr1[i] > arr1[i])
        {
            return false;
        }
    }
    return true;
}

template<typename T, int N>
std::string printArr(std::array<T, N> &arr){

    std::string s = "{ ";
    for(int i = 0; i < N; ++i) {
        s += arr[i];
    }
    s += " }";

    return s;
}

void test_3_search_index() {

    if (verbose) {
        print("test building and using max profit point index");
    }

    std::vector<std::array<int, 2>> mixDimData =
            {
                    make_arr(2000, 100),
                    make_arr(1976, 100),
                    make_arr(1702, 100),
                    make_arr(1702, 100),
                    make_arr(1638, 100),
                    make_arr(1633, 100),
                    make_arr(1633, 100),
                    make_arr(1144, 100),
                    make_arr(1143, 100),
                    make_arr(1086, 100),
                    make_arr(976, 100),
                    make_arr(822, 100),
                    make_arr(821, 100),
                    make_arr(718, 100),
                    make_arr(702, 100),
                    make_arr(701, 100),
                    make_arr(701, 100),
                    make_arr(640, 100),
                    make_arr(634, 100),
                    make_arr(291, 100),
                    make_arr(291, 100),
                    make_arr(124, 100),
                    make_arr(100, 100),
            };

    std::vector<int> values(mixDimData.size());

    for (int i = 0; i < mixDimData.size(); ++i) {
        values[i] = std::get<1>(mixDimData[i]);
    }

    std::vector<int> dimensions(mixDimData.size());

    for (int i = 0; i < mixDimData.size(); ++i) {
        dimensions[i] = std::get<0>(mixDimData[i]);
    }

    std::vector<int> indexes(mixDimData.size(), 0);
    std::iota(indexes.begin(), indexes.end(), 0);

    auto sumOfAll = std::accumulate(mixDimData.begin(), mixDimData.end(), 0, fieldFunctor<int, 2, 0>());

    auto lambda = [](auto a, auto b) {
        return a[0] < b[0];
    };

    auto m = std::min_element(mixDimData.begin(), mixDimData.end(), lambda);

    int minItem = m[0][0] - 1;

    std::vector<int> indexConstraints = {sumOfAll, sumOfAll / 2};

    for (auto indexConstr : indexConstraints) {

        for (auto s = 1; s < 3; ++s) {

            auto testDescValues = std::vector<int>(values);

            auto sameProfit = s % 2 == 0;

            if (not sameProfit) {
                testDescValues[0] -= 1;
            }

            for (auto j = 1; j < 3; ++j) {

                auto forceUsePareto = j % 2 == 0;

                auto dims = std::vector<kb_knapsack::w_point_dim1<int, int, 1>>();

                for (auto i = 0; i < dimensions.size(); ++i) {
                    dims.emplace_back(kb_knapsack::w_point_dim1<int, int, 1>(dimensions[i]));
                }

                kb_knapsack::knapsack_solver<int, int, 1, kb_knapsack::w_point_dim1> binSearchSolver(
                        dims, values,indexes);

                binSearchSolver.PrepareSearchIndex = true;

                binSearchSolver.Constraints = kb_knapsack::w_point_dim1<int, int, 1>(indexConstr - 1);

                binSearchSolver.ForceUsePareto = forceUsePareto;

                binSearchSolver.EmptyDimension = kb_knapsack::w_point_dim1<int, int, 1>(0);
                binSearchSolver.EmptyValue = 0;
                binSearchSolver.MinValue = -999999999;

                binSearchSolver.Solve();

                for (auto constraint = minItem; constraint < indexConstr; constraint = constraint + minItem - 1) {

                    auto constraintPoint = kb_knapsack::w_point_dim1<int, int, 1>(constraint);

                    auto fullResult = kb_knapsack::knapsack1(constraint, dimensions, values, indexes);

                    auto testResult = binSearchSolver.Solve(constraintPoint);

                    auto opt = std::get<0>(fullResult);
                    auto testOpt = std::get<0>(testResult);

                    auto testOptSize = std::get<1>(testResult);

                    auto good = opt == testOpt and testOptSize <= constraint;

                    boost::ut::expect(good) << "test_3_search_index: indexConstr=" << indexConstr << "; constraint="
                                            << constraint << "; forceUsePareto="
                                            << forceUsePareto << "; sameProfit=" << sameProfit
                                            << "; expected - optimized: " << opt - testOpt;
                }
            }
        }
    }
}

void test_8_T_partition_grouping_operator() {

    if (verbose){
        print("MKS N partition 2d matching results with limits turned off");
    }

    std::vector<std::array<int, 2>> mixDimData = {
                                                    make_arr(1702, 1),
                                                    make_arr(1633, 1),
                                                    make_arr(1438, 1),
                                                    make_arr(1144, 1),
                                                    make_arr(1086, 1),
                                                    make_arr(976, 1),
                                                    make_arr(821, 1),
                                                    make_arr(718, 1),
                                                    make_arr(701, 1),
                                                    make_arr(634, 1),
                                                    make_arr(291, 1),
                                                    make_arr(124, 1),
    };


    std::vector<int> values(mixDimData.size());

    for (int i = 0; i < mixDimData.size(); ++i) {
        values[i] = std::get<0>(mixDimData[i]);
    }

    std::vector<int> indexes(mixDimData.size(), 0);
    std::iota(indexes.begin(), indexes.end(), 0);

    auto sumOfAll = std::accumulate(mixDimData.begin(), mixDimData.end(), 0, fieldFunctor<int, 2, 0>());

    auto lambda = [](auto a, auto b) {
        return a[0] < b[0];
    };

    auto m = std::min_element(mixDimData.begin(), mixDimData.end(), lambda);

    int minItem = m[0][0] - 1;

    for(auto i = 1; i < 3; ++i){

        auto ascOrder = i % 2 == 0;

        for(auto constraint1 = minItem; constraint1 < sumOfAll; constraint1 += int(minItem / 2)){

            for(auto constraint2  = 1; constraint2 < mixDimData.size(); ++constraint2){

                std::vector<std::array<int, 2>> testDescDims(mixDimData);
                std::vector<int> testDescValues(values);
                std::vector<int> testDescIndex(indexes);

                if (ascOrder){
                    std::reverse(testDescDims.begin(), testDescDims.end());
                    std::reverse(testDescValues.begin(), testDescValues.end());
                    std::reverse(testDescIndex.begin(), testDescIndex.end());
                }

                std::array<int, 2> constraint = make_arr(constraint1, constraint2);

                auto noLimResult = knapsackN<int, int, 2>(constraint, testDescDims, testDescValues, testDescIndex, true, false);
                auto testResult = knapsackN<int, int, 2>(constraint, testDescDims, testDescValues, testDescIndex);

                auto optValueExpected = std::get<0>(noLimResult);
                auto optValueTest = std::get<0>(testResult);

                auto optSizeExpected = std::get<1>(noLimResult);
                auto optSizeTest = std::get<1>(testResult);

                auto goodVal = optValueTest >= optValueExpected;
                auto goodSize = allLessOrEqual<int, 2>(optSizeTest, constraint) && allLessOrEqual<int, 2>(optSizeExpected, constraint);

                boost::ut::expect(goodVal) << "Not equal val. Expected: " << optValueExpected << ", but was: " << optValueTest << "; at case: ASC=" << ascOrder << " constraint1=" << constraint1 << " constraint2=" << constraint2;
                boost::ut::expect(goodSize) << "Not equal size. Expected: " << printArr<int, 2>(optSizeExpected) << ", but was: " << printArr<int, 2>(optSizeTest) << "; at case: ASC=" << ascOrder << " constraint1=" << constraint1 << " constraint2=" << constraint2;
            }
        }
    }
}

void test_6_Silvano_Paolo_1_0_knapsack(){
    if (verbose){
        print("1-0 knapsack1 solver for Silvano Martello and Paolo Toth 1990 tests.");
    }

    // page 42. Example 2.3

    std::vector<int> V = {50, 50, 64, 46, 50, 5};
    std::vector<int> W = {56, 59, 80, 64, 75, 17};
    std::vector<int> R = {1, 1, 0, 0, 1, 0};
    int c = 190;

    testSilvano(W, V, R, c);

    // page 47. Example 2.7

    V = {70, 20, 39, 37, 7, 5, 10};
    W = {31, 10, 20, 19, 4, 3, 6};
    R = {1, 0, 0, 1, 0, 0, 0};
    c = 50;

    testSilvano(W, V, R, c);
}

void test_2_superincreasing() {

    if (verbose)
    {
        print("Superincreasing integer numbers tests.");
    }

    std::vector<int> A = {1, 2, 5, 21, 69, 189, 376, 919};

    for (int i = 1; i < 3; ++i) {

        std::vector<int> test(A);

        if (i % 2 == 1) {
            std::reverse(test.begin(), test.end());
        }

        int sumA = std::accumulate(test.begin(), test.end(), 0);

        std::vector<int> indexes(test.size(), 0);
        std::iota(indexes.begin(), indexes.end(), 0);

        for(int s = 0; s < sumA; s++) {

            auto expectedResult = kb_knapsack::knapsack1(s, test, test, indexes, false);

            auto opt1 = std::get<0>(expectedResult);
            auto expected = std::get<2>(expectedResult);

            auto testResult = kb_knapsack::knapsack1(s, test, test, indexes);

            auto optTest = std::get<0>(expectedResult);
            auto optValues = std::get<2>(expectedResult);

            boost::ut::expect(listValuesEqual(expected, optValues)) << "Lists are not equal ";
        }
    }
}

bool startsWith(std::string s, std::string prefix){
    if (s.rfind(prefix, 0) == 0) {
        return true;
    }
    return false;
}

std::vector<std::string> split(const std::string& s, char delimiter)
{
    std::vector<std::string> tokens;
    std::string token;
    std::istringstream tokenStream(s);
    while (std::getline(tokenStream, token, delimiter))
    {
        tokens.emplace_back(token);
    }
    return tokens;
}

void test_8_equal_subset_sum_files(std::filesystem::path testDir) {

    if (verbose) {
        print("Run equal-subset-sum knapsack1 for hardinstances_pisinger subset sum test dataset.");
    }

    std::vector<std::string> files = {"knapPI_16_20_1000.csv", "knapPI_16_50_1000.csv", "knapPI_16_100_1000.csv", "knapPI_16_200_1000.csv", "knapPI_16_500_1000.csv"};

    int fi = 0;

    bool allGood = true;

    for (auto f : files) {

        fi += 1;

        int caseNumber = 1;

        std::filesystem::path file(f);
        std::filesystem::path full_path = testDir / file;

        std::fstream fin(full_path, std::fstream::in);
        std::vector<std::string> row;
        std::string line, word;

        std::vector<int> testCase;
        std::vector<int> testExpected;
        int testKnapsack = 0;
        int rowToSkip = 0;

        std::string temp;
        while (std::getline(fin, temp)) {

            row.clear();
            std::stringstream s(temp);

            if(temp.empty()){
                continue;
            }

            while (std::getline(s, word, ',')) {
                row.emplace_back(word);
            }

            if (row[0] == "-----") {

                std::sort(testCase.begin(), testCase.end());

                if (verbose) {
                    std::cout << f << " case " << caseNumber << std::endl;
                }

                std::vector<int> indexes(testCase.size(), 0);
                std::iota(indexes.begin(), indexes.end(), 0);

                auto testResult = kb_knapsack::knapsack1(testKnapsack, testCase, testCase, indexes, true, true, true);

                auto optVal = std::get<0>(testResult);
                auto optItems = std::get<2>(testResult);

                boost::ut::expect(optVal <= testKnapsack) << " Opt size greater than expected ";

                auto expSum = std::accumulate(testExpected.begin(), testExpected.end(), 0);
                auto testSum = std::accumulate(optItems.begin(), optItems.end(), 0);

                boost::ut::expect(testSum >= expSum) << "File:" << f << ", case: " << caseNumber << ". Test values sum less than expected: " << expSum << " but was :" << testSum;

                allGood = allGood && optVal <= testKnapsack && testSum >= expSum;

                testCase.clear();
                testExpected.clear();

                testCase = {};
                testExpected = {};
                testKnapsack = 0;

                caseNumber++;

                continue;
            }

            std::string row0 = row[0];

            if (startsWith(row0, "knapPI")) {
                rowToSkip = 6;
            }

            if (startsWith(row0, "z ")) {
                std::string r = split(row[0], ' ')[1];
                testKnapsack = stoi(r);
            }

            rowToSkip -= 1;

            if (rowToSkip <= 0) {
                testCase.emplace_back(stoi(row[1]));

                if (row[3] == "1") {
                    testExpected.emplace_back(stoi(row[1]));
                }
            }
        }

        fin.close();
    }

    boost::ut::expect(allGood) << "Some tests failed";
}


void test_8_knapsack_1_0_files(std::filesystem::path testDir) {

    if (verbose) {
        print("Run 1-0 knapsack1 for hardinstances_pisinger test dataset.");
    }

    std::vector<std::string> files = { "knapPI_11_20_1000.csv", "knapPI_11_50_1000.csv", "knapPI_11_100_1000.csv", "knapPI_11_200_1000.csv" };

    int fi = 0;

    bool allGood = true;

    for (auto f : files) {

        fi += 1;

        int caseNumber = 1;

        std::filesystem::path file(f);
        std::filesystem::path full_path = testDir / file;

        std::fstream fin(full_path, std::fstream::in);
        std::vector<std::string> row;
        std::string line, word;

        std::vector<int> testCaseW;
        std::vector<int> testCaseV;
        std::vector<int> testExpected;
        int testKnapsack = 0;
        int rowToSkip = 0;

        std::string temp;
        while (std::getline(fin, temp)) {

            row.clear();
            std::stringstream s(temp);

            if(temp.empty()){
                continue;
            }

            while (std::getline(s, word, ',')) {
                row.emplace_back(word);
            }

            if (row[0] == "-----") {

                std::vector<int> indexes(testCaseW.size(), 0);
                std::iota(indexes.begin(), indexes.end(), 0);

                kb_knapsack::tools::sortReverse(testCaseW, testCaseV, indexes);

                if (verbose) {
                    std::cout << f << " case " << caseNumber << std::endl;
                }

                auto testResult = kb_knapsack::knapsack1(testKnapsack, testCaseW, testCaseV, indexes);

                auto optVal = std::get<0>(testResult);
                auto optSize = std::get<1>(testResult);
                auto optItems = std::get<2>(testResult);
                auto optValues = std::get<3>(testResult);

                boost::ut::expect(optSize <= testKnapsack) << " Opt size greater than expected ";

                auto expSum = std::accumulate(testExpected.begin(), testExpected.end(), 0);
                auto testSum = std::accumulate(optValues.begin(), optValues.end(), 0);

                boost::ut::expect(testSum >= expSum) << "File:" << f << ", case: " << caseNumber << ". Test values sum less than expected: " << expSum << " but was :" << testSum;

                allGood = allGood && optSize <= testKnapsack && testSum >= expSum;

                testCaseW.clear();
                testCaseV.clear();
                testExpected.clear();

                testCaseW = {};
                testCaseV = {};
                testExpected = {};
                testKnapsack = 0;

                caseNumber++;

                continue;
            }

            std::string row0 = row[0];

            if (startsWith(row0, "knapPI")) {
                rowToSkip = 6;
            }

            if (startsWith(row0, "c ")) {
                std::string r = split(row[0], ' ')[1];
                testKnapsack = stoi(r);
            }

            rowToSkip -= 1;

            if (rowToSkip <= 0) {
                testCaseW.emplace_back(stoi(row[2]));
                testCaseV.emplace_back(stoi(row[1]));

                if (row[3] == "1") {
                    testExpected.emplace_back(stoi(row[1]));
                }
            }
        }

        fin.close();
    }

    boost::ut::expect(allGood) << "Some tests failed";
}

int main() {

    auto execDir = MyPaths::getExecutableDir();
    std::filesystem::path script_dir (execDir);
    std::filesystem::path testData_dir ("testData/hardinstances_pisinger");

    auto testDir = script_dir.parent_path().parent_path().parent_path().parent_path() / testData_dir;

    test_3_search_index();

    test_2_superincreasing();
    test_1_rational_numbers();
    test_6_Silvano_Paolo_1_0_knapsack();

    const auto start = std::chrono::high_resolution_clock::now();

    test_8_knapsack_1_0_files(testDir);
    test_8_equal_subset_sum_files(testDir);

    const auto stop = std::chrono::high_resolution_clock::now();
    const auto s = std::chrono::duration_cast<std::chrono::seconds>(stop - start);
    std::cout << "File tests were finished using " << s.count() << " seconds." << std::endl;

    test_8_T_partition_grouping_operator();
}