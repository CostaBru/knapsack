//
// Created by kooltew on 5/11/2021.
//

#ifndef KB_KNAPSACK_PARTITION_SOLUTION_SOURCE_LINK_H
#define KB_KNAPSACK_PARTITION_SOLUTION_SOURCE_LINK_H


#include "fast_map.h"
#include "defines.h"
#include "w_point_dim1.h"
#include "w_point_dimN.h"
#include "w_point.h"

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

        source_link(int _itemId, long sourceLinkId){
            itemId = _itemId;
            parentId = sourceLinkId;
        }

        bool hasParent(){
            return parentId >= 0;
        }
    };
}

#endif //KB_KNAPSACK_PARTITION_SOLUTION_SOURCE_LINK_H
