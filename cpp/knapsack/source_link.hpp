#ifndef KB_KNAPSACK_PARTITION_SOLUTION_SOURCE_LINK_HPP
#define KB_KNAPSACK_PARTITION_SOLUTION_SOURCE_LINK_HPP


#include "fast_map.h"
#include "defines.h"
#include "w_point_dim1.hpp"
#include "w_point_dimN.hpp"
#include "w_point.hpp"

#include <vector>
#include <tuple>
#include <cmath>
#include <deque>
#include <numeric>
#include <ranges>

namespace kb_knapsack {

    struct source_link{
        int itemId = -1;
        long parentId = -1;

        source_link(int itemId, long parentId) :
            itemId(itemId),
            parentId(parentId) {
        }

        bool hasParent(){
            return parentId >= 0;
        }
    };
}

#endif //KB_KNAPSACK_PARTITION_SOLUTION_SOURCE_LINK_HPP
