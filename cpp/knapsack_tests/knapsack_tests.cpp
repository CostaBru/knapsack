#include "ut.h"
#include <knapsack.h>
#include <string>

//https://github.com/boost-ext/ut#tutorial

void print(std::string str){
    std::cout << str << std::endl;
}

template<typename T, typename W>
std::tuple<W, T, std::vector<T>, std::vector<W>, std::vector<int>> paretoKnapsack(T constraint,
        std::vector<T>& dimensions,
        std::vector<W>& values,
        std::vector<int>& indexes) {

    kb_knapsack::knapsack_solver<T, W> solver;

    solver.m_emptyDimension = 0;
    solver.m_emptyValue = 0;
    solver.m_dimensions = dimensions;
    solver.m_values = values;
    solver.m_indexes = indexes;
    solver.m_constraints = constraint;

    std::tuple<W, T, std::vector<T>, std::vector<W>, std::vector<int>> rez = solver.Solve();

    return rez;
}

bool verbose = true;

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

    auto result = paretoKnapsack(c, ws, vs, indexes);

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

int main() {
    test_6_Silvano_Paolo_1_0_knapsack();
}