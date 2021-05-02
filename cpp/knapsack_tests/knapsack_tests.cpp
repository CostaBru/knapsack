#include "ut.h"
#include <knapsack.h>
#include "Paths.h"
#include <string>
#include <fstream>
#include <filesystem>

//https://github.com/boost-ext/ut#tutorial

void print(std::string str){
    std::cout << str << std::endl;
}

template<typename T, typename W>
std::tuple<W, T, std::vector<T>, std::vector<W>, std::vector<int>> knapsack(T constraint,
                                                                            std::vector<T>& dimensions,
                                                                            std::vector<W>& values,
                                                                            std::vector<int>& indexes,
                                                                            bool doSolveSuperInc = true) {

    kb_knapsack::knapsack_solver<T, W> solver;

    solver.EmptyDimension = 0;
    solver.EmptyValue = 0;
    solver.MinValue = -999999999;

    solver.Constrains = constraint;
    solver.Dimensions = dimensions;
    solver.Values = values;
    solver.Ids = indexes;

    solver.DoSolveSuperInc = doSolveSuperInc;

    std::tuple<W, T, std::vector<T>, std::vector<W>, std::vector<int>> rez = solver.Solve();

    return rez;
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
        print("Rational numbers tests for 1-0 knapsack.");
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

    auto result = knapsack(s, A, A, indexes);

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

    kb_knapsack::sortReverse(ws, vs, indexes);

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

    auto result = knapsack(c, ws, vs, indexes);

    auto opt1 = std::get<0>(result);

    boost::ut::expect(opt1 == expectedSV) << "Not equal ";
}


void test_6_Silvano_Paolo_1_0_knapsack(){
    if (verbose){
        print("1-0 knapsack solver for Silvano Martello and Paolo Toth 1990 tests.");
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

            auto expectedResult = knapsack(s, test, test, indexes, false);

            auto opt1 = std::get<0>(expectedResult);
            auto expected = std::get<2>(expectedResult);

            auto testResult = knapsack(s, test, test, indexes);

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
        tokens.push_back(token);
    }
    return tokens;
}

void test_8_equal_subset_sum_files(std::filesystem::path testDir) {

    if (verbose) {
        print("Run equal-subset-sum knapsack for hardinstances_pisinger subset sum test dataset.");
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
                row.push_back(word);
            }

            if (row[0] == "-----") {

                std::sort(testCase.begin(), testCase.end());

                if (verbose) {
                    std::cout << f << " case " << caseNumber << std::endl;
                }

                std::vector<int> indexes(testCase.size(), 0);
                std::iota(indexes.begin(), indexes.end(), 0);

                auto testResult = knapsack(testKnapsack, testCase, testCase, indexes);

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
                testCase.push_back(stoi(row[1]));

                if (row[3] == "1") {
                    testExpected.push_back(stoi(row[1]));
                }
            }
        }

        fin.close();
    }

    boost::ut::expect(allGood) << "Some tests failed";
}


void test_8_knapsack_1_0_files(std::filesystem::path testDir) {

    if (verbose) {
        print("Run 1-0 knapsack for hardinstances_pisinger test dataset.");
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
                row.push_back(word);
            }

            if (row[0] == "-----") {

                std::vector<int> indexes(testCaseW.size(), 0);
                std::iota(indexes.begin(), indexes.end(), 0);

                kb_knapsack::sortReverse(testCaseW, testCaseV, indexes);

                if (verbose) {
                    std::cout << f << " case " << caseNumber << std::endl;
                }

                auto testResult = knapsack(testKnapsack, testCaseW, testCaseV, indexes);

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
                testCaseW.push_back(stoi(row[2]));
                testCaseV.push_back(stoi(row[1]));

                if (row[3] == "1") {
                    testExpected.push_back(stoi(row[1]));
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

    test_8_knapsack_1_0_files(testDir);
    test_8_equal_subset_sum_files(testDir);

    test_2_superincreasing();
    test_1_rational_numbers();
    test_6_Silvano_Paolo_1_0_knapsack();
}