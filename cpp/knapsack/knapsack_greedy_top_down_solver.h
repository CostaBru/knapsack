#ifndef KB_KNAPSACK_PARTITION_SOLUTION_KNAPSACK_GREEDY_TOP_DOWN_SOLVER_H
#define KB_KNAPSACK_PARTITION_SOLUTION_KNAPSACK_GREEDY_TOP_DOWN_SOLVER_H


#include <knapsack_solver.h>
#include <fast_map.h>

namespace kb_knapsack {

#define KNAPSACK knapsack_solver<T, W, 1, kb_knapsack::w_point_dim1>

    template<typename T, typename W, int N, template<typename DIM_TYPE, typename VALUE_TYPE, int DIM_LEN> class DIM>
    class knapsack_greedy_top_down_solver {

    public:

        knapsack_greedy_top_down_solver(std::vector<TD> & Dimensions, std::vector<W> & Values,  std::vector<int> & Ids) :
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

        TD  SolvedByConstraint;

        KNAPSACK_RESULT Solve(){

            SolvedByConstraint = EmptyDimension;

            return Solve(Constraints);
        }

        KNAPSACK_RESULT Solve(TD searchConstraint){

            if (Dimensions.size() != Values.size() || Ids.size() != Dimensions.size()) {

                throw std::invalid_argument("Sizes of dimensions, values and ids given should be equal.");
            }

            int size = N;

            W maxN = MinValue;
            TD maxDimN = EmptyDimension;

            std::vector<TD> maxNItems;
            std::vector<W> maxNValues;
            std::vector<int> maxNIds;

            std::vector<std::vector<int>> dimDescSortedIndex(size);

            std::vector<int> dimStairSteps(size);
            std::vector<int> dimStairDownCursors(size);
            std::vector<int> dimStairDownCursorStartings(size);

            std::vector<KNAPSACK> solvers(size);

            std::vector<int> dimensionIndexes(size, 0);
            std::iota(dimensionIndexes.begin(), dimensionIndexes.end(), 0);

            std::sort(dimensionIndexes.begin(), dimensionIndexes.end(),
                      [&](size_t i, size_t j) { return Constraints.getDimension(i) < Constraints.getDimension(j); });

            for(int i = 0; i < size; ++i) {

                int dimensionIndex = dimensionIndexes[i];
                int dimOrderIndex = dimensionIndexes[dimensionIndex];

                std::vector<kb_knapsack::w_point_dim1<T, W, 1>> descDim;
                std::vector<W> descValues(Values);
                std::vector<int> descIndex(Dimensions.size(), 0);

                std::iota(descIndex.begin(), descIndex.end(), 0);

                for (int j = 0; j < Dimensions.size(); ++j) {

                    descDim.emplace_back(kb_knapsack::w_point_dim1<T, W, 1>(Dimensions[j].getDimension(dimOrderIndex)));
                }

                dimDescSortedIndex[dimensionIndex] = descIndex;

                dimStairSteps[dimensionIndex] = Dimensions[Dimensions.size() - 1].getDimension(dimOrderIndex);
                dimStairDownCursors[dimensionIndex] = Constraints.getDimension(dimOrderIndex);
                dimStairDownCursorStartings[dimensionIndex] = Constraints.getDimension(dimOrderIndex);

                KNAPSACK solver = KNAPSACK(descDim, descValues, descIndex);

                solver.EmptyDimension = kb_knapsack::w_point_dim1<T, W, 1>(0);
                solver.EmptyValue = EmptyValue;
                solver.MinValue = MinValue;

                solver.Constraints = kb_knapsack::w_point_dim1<T, W, 1>(Constraints.getDimension(dimOrderIndex));

                solver.ForceUsePareto = true;
                solver.PrepareSearchIndex = true;

                solvers[dimOrderIndex] = solver;
            }

            auto optimizeIterIndex = 0;

            auto anyGreaterThanStep = true;

            while (anyGreaterThanStep) {

                robin_hood::unordered_set<int> optimizedIndexes;

                for(int dimensionIndex = 0; dimensionIndex < size; ++dimensionIndex) {

                    auto currentDimLimit = dimStairDownCursors[dimensionIndex];

                    auto singleDimRes = solvers[dimensionIndex].Solve(kb_knapsack::w_point_dim1<T, W, 1>(currentDimLimit));

                    for(auto oi: std::get<4>(singleDimRes)) {

                        auto itemIndex = dimDescSortedIndex[dimensionIndex][oi];

                        optimizedIndexes.insert(itemIndex);
                    }
                }

                std::vector<TD> descNewDims;
                std::vector<W> descNewVals;
                std::vector<int> descNewIndex;

                W sumOfNewValues = EmptyValue;

                for(auto itemIndex: optimizedIndexes) {

                    descNewDims.emplace_back(Dimensions[itemIndex]);
                    descNewVals.emplace_back(Values[itemIndex]);
                    descNewIndex.emplace_back(itemIndex);

                    sumOfNewValues += Values[itemIndex];
                }

                if (sumOfNewValues > maxN) {

                    tools::sortReverse(descNewDims, descNewVals, descNewIndex);

                    auto fullResult = solveKnapsackNd(Constraints, descNewDims, descNewVals, descNewIndex);

                    auto optN = std::get<0>(fullResult);

                    if (maxN < optN) {

                        maxN = optN;
                        maxDimN = std::get<1>(fullResult);
                        maxNItems = std::get<2>(fullResult);
                        maxNValues = std::get<3>(fullResult);
                        maxNIds =std::get<4>(fullResult);
                    }
                }
                else {

                    break;
                }

                auto decIndex = (optimizeIterIndex) % size;

                if (dimStairDownCursors[decIndex] >= dimStairSteps[decIndex]) {

                    dimStairDownCursors[decIndex] -= dimStairSteps[decIndex];
                }

                for(int dimensionIndex = 0 ; dimensionIndex < size; ++dimensionIndex) {

                    auto anyGreaterThanStep = dimStairDownCursors[dimensionIndex] >= dimStairSteps[dimensionIndex];

                    if (anyGreaterThanStep) {

                        break;
                    }

                    optimizeIterIndex += 1;
                }
            }

            SolvedByConstraint = Constraints;

            return std::make_tuple(maxN, maxDimN, maxNItems, maxNValues, maxNIds);
        }

    private:

        std::tuple<W, TD, std::vector<TD>, std::vector<W>, std::vector<int>>
        solveKnapsackNd(TD         & constraint,
                  std::vector<TD>  & dimensions,
                  std::vector<W>   & values,
                  std::vector<int> & indexes) {

            kb_knapsack::knapsack_solver<T, W, N, kb_knapsack::w_point_dimN> solver(dimensions, values, indexes);

            std::array<T, N> emptyDim;

            for (int i = 0; i < N; ++i) {
                emptyDim[i] = 0;
            }

            solver.EmptyDimension = kb_knapsack::w_point_dimN<T, W, N>(emptyDim);
            solver.EmptyValue = EmptyValue;
            solver.MinValue = MinValue;
            solver.ForceUseLimits = true;

            solver.Constraints = kb_knapsack::w_point_dimN<T, W, N>(constraint);

            return solver.Solve();
        }
    };
}

#endif //KB_KNAPSACK_PARTITION_SOLUTION_KNAPSACK_GREEDY_TOP_DOWN_SOLVER_H
