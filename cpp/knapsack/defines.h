#ifndef KB_KNAPSACK_PARTITION_SOLUTION_DEFINES_H
#define KB_KNAPSACK_PARTITION_SOLUTION_DEFINES_H

#define TD DIM<T, W, N>

#define W_POINT w_point<T, W, N, DIM>

#define W_POINT_SET robin_hood::unordered_set<W_POINT, w_point_hash<T, W, N, DIM>, w_point_key_equals<T, W, N, DIM>>

#define W_POINT_DEQUEUE std::deque<W_POINT>

#define W_POINT_LIST std::vector<W_POINT>

#define KNAPSACK_RESULT std::tuple<W, TD, std::vector<TD>, std::vector<W>, std::vector<int>>

#define SOURCE_LINK_LIST std::vector<source_link>

#endif //KB_KNAPSACK_PARTITION_SOLUTION_DEFINES_H
