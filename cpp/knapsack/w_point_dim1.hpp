#ifndef KB_KNAPSACK_PARTITION_SOLUTION_W_POINT_DIM1_HPP
#define KB_KNAPSACK_PARTITION_SOLUTION_W_POINT_DIM1_HPP

#include "fast_map.h"
#include "defines.h"

#include <vector>
#include <tuple>
#include <cmath>
#include <deque>
#include <numeric>
#include <ranges>


namespace kb_knapsack {

    template<typename T, typename W, int N>
    struct w_point_dim1 {
    public:
        T value;

        w_point_dim1(){
        }

        w_point_dim1(const T &dim) : value(dim){
        }

        w_point_dim1(const w_point_dim1 &that) : value(that.value)
        {
        }

        w_point_dim1& operator=(const w_point_dim1& that)
        {
            if (this != &that)
            {
                value = that.value;
            }
            return *this;
        }

        T getDimension(int index) const{
            return value;
        }

        std::array<T, 1> getDimensions() {
            return {value};
        }

        bool firstDimensionEqual(W &val){
            return value == val;
        }

        w_point_dim1 adjustMin(w_point_dim1& p){
            if (p.value < value){
                return w_point_dim1(p.value);
            }

            return w_point_dim1(value);
        }

        w_point_dim1 half(){
            return w_point_dim1(value / 2);
        }

        w_point_dim1 divide(W& c){
            return w_point_dim1(c / value);
        }

        friend bool operator>(const w_point_dim1 &c1, const w_point_dim1 &c2) {
            return c1.value > c2.value;
        }

        friend bool operator<=(const w_point_dim1 &c1, const w_point_dim1 &c2) {
            return c1.value <= c2.value;
        }

        friend bool operator<(const w_point_dim1 &c1, const w_point_dim1 &c2) {
            return c1.value < c2.value;
        }

        friend bool operator>=(const w_point_dim1 &c1, const w_point_dim1 &c2) {
            return c1.value >= c2.value;
        }

        friend bool operator==(const w_point_dim1 &c1, const w_point_dim1 &c2) {
            return c1.value == c2.value;
        }

        friend bool operator!=(const w_point_dim1 &c1, const w_point_dim1 &c2) {
            return c1.value != c2.value;
        }

        friend w_point_dim1 operator+(const w_point_dim1 &c1, const w_point_dim1 &c2) {
            return w_point_dim1(c1.value + c2.value);
        }

        friend w_point_dim1 operator-(const w_point_dim1 &c1, const w_point_dim1 &c2) {
            return w_point_dim1(c1.value - c2.value);
        }

        friend void operator+=(w_point_dim1 &c1, const w_point_dim1 &c2) {
            c1 = w_point_dim1(c1.value + c2.value);
        }
    };
}

#endif //KB_KNAPSACK_PARTITION_SOLUTION_W_POINT_DIM1_HPP
