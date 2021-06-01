#ifndef KB_KNAPSACK_PARTITION_SOLUTION_API_H
#define KB_KNAPSACK_PARTITION_SOLUTION_API_H

#include <knapsack_solver.h>
#include <knapsack_greedy_top_down_solver.h>

namespace kb_knapsack {

    template<typename T, typename W>
    std::tuple<W, T, std::vector<T>, std::vector<W>, std::vector<int>>
    knapsack1(T                               & constraint,
             std::vector<T>                   & dimensions,
             std::vector<W>                   & values,
             std::vector<int>                 & indexes,
             bool doSolveSuperInc             = true,
             bool doUseLimits                 = true,
             bool canBackTraceWhenSizeReached = false) {

        auto dims = std::vector<kb_knapsack::w_point_dim1<T, W, 1>>();

        for(auto i = 0; i < dimensions.size(); ++i){

            dims.emplace_back(kb_knapsack::w_point_dim1<T, W, 1>(dimensions[i]));
        }

        kb_knapsack::knapsack_solver<T, W, 1, kb_knapsack::w_point_dim1> solver(dims, values, indexes);

        solver.EmptyDimension = kb_knapsack::w_point_dim1<T, W, 1>(0);
        solver.EmptyValue = 0;
        solver.MinValue = -999999999;

        solver.Constraints = kb_knapsack::w_point_dim1<T, W, 1>(constraint);

        solver.DoSolveSuperInc = doSolveSuperInc;
        solver.DoUseLimits = doUseLimits;
        solver.CanBackTraceWhenSizeReached = canBackTraceWhenSizeReached;

        auto rez = solver.Solve();

        auto optValue =   std::get<0>(rez);
        auto optSize =    std::get<1>(rez);
        auto optDim =     std::get<2>(rez);
        auto optValue2 =  std::get<3>(rez);
        auto optIndexes = std::get<4>(rez);

        std::vector<T> optDimRez(optDim.size());

        for(auto i = 0; i < optDim.size(); ++i){

            optDimRez[i] = optDim[i].value;
        }

        return std::make_tuple(optValue, optSize.value, optDimRez, optValue2, optIndexes);
    }


    template<typename T, typename W, int N>
    std::tuple<W, std::array<T, N>, std::vector<std::array<T, N>>, std::vector<W>, std::vector<int>>
    knapsackN(std::array<T, N>                 & constraint,
              std::vector<std::array<T, N>>    & dimensions,
              std::vector<W>                   & values,
              std::vector<int>                 & indexes,
              bool doSolveSuperInc             = true,
              bool doUseLimits                 = true,
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

        auto optValue =    std::get<0>(rez);
        auto optSize =     std::get<1>(rez);
        auto optDim =      std::get<2>(rez);
        auto optValue2 =   std::get<3>(rez);
        auto optIndexes =  std::get<4>(rez);

        std::vector<std::array<T, N>> optDimRez(optDim.size());

        for(auto i = 0; i < optDim.size(); ++i){

            optDimRez[i] = optDim[i].value;
        }

        return std::make_tuple(optValue, optSize.value, optDimRez, optValue2, optIndexes);
    }

    template<typename T, typename W, int N>
    std::tuple<W, std::array<T, N>, std::vector<std::array<T, N>>, std::vector<W>>
    greedyKnapsackN(std::array<T, N>              & constraint,
                    std::vector<std::array<T, N>> & dimensions,
                    std::vector<W>                & values,
                    std::vector<int>              & indexes) {

        auto dims = std::vector<kb_knapsack::w_point_dimN<T, W, N>>();

        for(auto i = 0; i < dimensions.size(); ++i){

            dims.emplace_back(kb_knapsack::w_point_dimN<T, W, N>(dimensions[i]));
        }

        kb_knapsack::knapsack_greedy_top_down_solver<T, W, N, kb_knapsack::w_point_dimN> solver(dims, values, indexes);

        std::array<T, N> emptyDim;

        for (int i = 0; i < N; ++i) {

            emptyDim[i] = 0;
        }

        solver.EmptyDimension = kb_knapsack::w_point_dimN<T, W, N>(emptyDim);
        solver.EmptyValue = 0;
        solver.MinValue = -999999999;

        solver.Constraints = kb_knapsack::w_point_dimN<T, W, N>(constraint);

        auto rez = solver.Solve();

        auto optValue =   std::get<0>(rez);
        auto optSize =    std::get<1>(rez);
        auto optDim =     std::get<2>(rez);
        auto optValue2 =  std::get<3>(rez);

        std::vector<std::array<T, N>> optDimRez(optDim.size());

        for(auto i = 0; i < optDim.size(); ++i){

            optDimRez[i] = optDim[i].value;
        }

        return std::make_tuple(optValue, optSize.value, optDimRez, optValue2);
    }
}

#endif //KB_KNAPSACK_PARTITION_SOLUTION_API_H
