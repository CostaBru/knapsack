#ifndef KB_KNAPSACK_PARTITION_SOLUTION_W_POINT_H
#define KB_KNAPSACK_PARTITION_SOLUTION_W_POINT_H

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

    template<typename T, typename W, int N, template<typename DIM_TYPE, typename VALUE_TYPE, int DIM_LEN> class DIM>
    struct w_point {
    public:
        TD dimensions;
        W profit;
        long id = -1;

        w_point(){
        }

        T getDimension(int i) const {
            return dimensions.getDimension(i);
        }

        w_point(TD dims, W value) : dimensions(dims){
            profit = value;
        }

        friend w_point operator+(w_point &c1, w_point &c2) {
            return w_point(c1.dimensions + c2.dimensions, c1.profit + c2.profit);
        }

        w_point(const w_point& that) : dimensions(that.dimensions)
        {
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

        friend std::ostream& operator<<(std::ostream &strm, const w_point<T, W, N, DIM> &a) {
            return strm << "p(" << a.dimensions << "-" << a.profit << ")";
        }
    };


    template<typename T, typename W, int N, template<typename DIM_TYPE, typename VALUE_TYPE, int DIM_LEN> class DIM>
    struct w_point_hash
    {
        std::size_t operator()(const W_POINT& k) const
        {
            std::size_t hashCode = (robin_hood::hash<T>()(k.getDimension(0)));

            for(int i = 1; i < N; ++i){
                hashCode ^= (robin_hood::hash<T>()(k.getDimension(i)));
            }

            std::size_t h2 = (std::hash<W>()(k.profit));

            return 397 ^ hashCode ^ h2;
        }
    };

    template<typename T, typename W, int N, template<typename DIM_TYPE, typename VALUE_TYPE, int DIM_LEN> class DIM>
    struct w_point_key_equals
    {
        bool operator()(const W_POINT& k1, const W_POINT& k2) const
        {
            return k1.dimensions == k2.dimensions && k1.profit == k2.profit;
        }
    };

}

#endif //KB_KNAPSACK_PARTITION_SOLUTION_W_POINT_H
