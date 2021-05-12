#ifndef KB_KNAPSACK_PARTITION_SOLUTION_W_POINT_DIMN_H
#define KB_KNAPSACK_PARTITION_SOLUTION_W_POINT_DIMN_H

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
    struct w_point_dimN {
    public:
        std::array<T, N> value;

        w_point_dimN(){
        }

        w_point_dimN(const std::array<T, N> &dim) : value(dim){
        }

        w_point_dimN(const w_point_dimN &that) : value(that.value)
        {
        }

        w_point_dimN& operator=(const w_point_dimN &that)
        {
            if (this != &that)
            {
                value = that.value;
            }
            return *this;
        }

        bool firstDimensionEqual(W &val){
            return value[0] == val;
        }

        T getDimension(int index) const {
            return value[index];
        }

        std::array<T, N> getDimensions() {
            return value;
        }

        w_point_dimN adjustMin(w_point_dimN& p){

            std::array<T, N> result;

            for(int i = 0; i < N; ++i){
                result[i] = std::min(p.value[i], value[i]);
            }

            return w_point_dimN(result);
        }

        w_point_dimN half(){

            std::array<T, N> result;

            for(int i = 0; i < N; ++i){
                result[i] = value[i] / 2;
            }

            return w_point_dimN(result);
        }

        w_point_dimN divide(W& c){

            std::array<T, N> result;

            for(int i = 0; i < N; ++i){
                result[i] = c / value[i];
            }

            return w_point_dimN(result);
        }

        friend bool operator>(const w_point_dimN &c1, const w_point_dimN &c2) {

            bool allGreater = false;

            for(int i = 0; i < N; ++i) {

                if (c2.value[i] < c1.value[i]) {
                    allGreater = true;
                } else {
                    return false;
                }
            }

            return allGreater;
        }

        friend bool operator>=(const w_point_dimN &c1, const w_point_dimN &c2) {
            for(int i = 0; i < N; ++i) {

                if (c1.value[i] < c2.value[i])  return false;
            }

            return true;
        }

        friend bool operator<=(const w_point_dimN &c1, const w_point_dimN &c2) {
            for(int i = 0; i < N; ++i) {
                if (c1.value[i] > c2.value[i])
                {
                    return false;
                }
            }
            return true;
        }

        friend bool operator<(const w_point_dimN &c1, const w_point_dimN &c2) {

            bool allLess = false;
            for(int i = 0; i < N; ++i) {

                if (c1.value[i] == c2.value[i]) continue;

                if (c1.value[i] < c2.value[i])
                {
                    allLess = true;
                }
                else {
                    return false;
                }
            }

            return allLess;
        }

        friend bool operator==(const w_point_dimN &c1, const w_point_dimN &c2) {
            for(int i = 0; i < N; ++i) {

                if (c1.value[i] != c2.value[i])
                    return false;
            }

            return true;
        }

        friend bool operator!=(const w_point_dimN &c1, const w_point_dimN &c2) {
            for(int i = 0; i < N; ++i) {

                if (c1.value[i] == c2.value[i])
                    return false;
            }

            return true;
        }

        friend w_point_dimN operator+(const w_point_dimN &c1, const w_point_dimN &c2) {
            std::array<T, N> result;

            for(int i = 0; i < N; ++i){
                result[i] = c1.value[i] + c2.value[i];
            }

            return w_point_dimN(result);
        }

        friend w_point_dimN operator-(const w_point_dimN &c1, const w_point_dimN &c2) {
            std::array<T, N> result;

            for(int i = 0; i < N; ++i){
                result[i] = c1.value[i] - c2.value[i];
            }

            return w_point_dimN(result);
        }

        friend void operator+=(w_point_dimN &c1, const w_point_dimN &c2) {

            std::array<T, N> result;

            for(int i = 0; i < N; ++i){
                result[i] += c2.value[i];
            }

            c1 = w_point_dimN(result);
        }
    };

}

#endif //KB_KNAPSACK_PARTITION_SOLUTION_W_POINT_DIMN_H
