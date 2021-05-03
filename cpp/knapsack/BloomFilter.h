#pragma once

#include <vector>
#include <bitset>
#include <random>
#include <stdexcept>
#include <functional>
#include <cstddef>

namespace mvorbrodt  {

    static_assert(
            ((SIZE_MAX == 0xFFFFFFFF) || (SIZE_MAX == 0xFFFFFFFFFFFFFFFF)) &&
            ((sizeof(std::size_t) * CHAR_BIT) == 32) || ((sizeof(std::size_t) * CHAR_BIT) == 64),
            "std::size_t is neither 32 nor 64 bit");

#if SIZE_MAX == 0xFFFFFFFF
    using random_generator_bits_t = std::mt19937;
#elif SIZE_MAX == 0xFFFFFFFFFFFFFFFF
    using random_generator_bits_t = std::mt19937_64;
#else
#error "std::size_t is neither 32 nor 64 bit"
#endif

    template<typename Key, std::size_t HashN, typename Hash = std::hash<Key>>
    inline auto hashNT(const Key& key)
    {
        random_generator_bits_t rng(Hash{}(key));
        std::array<std::size_t, HashN> hashes{};
        std::generate(std::begin(hashes), std::end(hashes), rng);
        return hashes;
    }

    template<typename Key, std::size_t HashN, typename Hash = std::hash<Key>>
    class bloom_filter {
    public:
        static_assert(HashN > 0, "HashN must be greater than zero!");

        bloom_filter(std::size_t size, std::vector<Key> &keys)
                : m_bits(size) {
            if (!size)
                throw std::invalid_argument("Size must be greater than zero!");
        }

        void insert(const Key &key) {
            auto hv = hashNT<Key, HashN, Hash>(key);
            for (std::size_t i = 0; i < HashN; ++i)
                m_bits[hv[i] % m_bits.size()] = true;
        }

        bool contains(const Key &key) const {
            auto hv = hashNT<Key, HashN, Hash>(key);
            for (std::size_t i = 0; i < HashN; ++i)
                if (!m_bits[hv[i] % m_bits.size()])
                    return false;
            return true;
        }

    private:
        std::vector<bool> m_bits;
    };

    template<typename Key, std::size_t Size, std::size_t HashN, typename Hash = std::hash<Key>>
    class fixed_bloom_filter {
    public:
        static_assert(Size > 0, "Size must be greater than zero!");

        void add(const Key &key) {
            auto hv = hashNT<HashN, std::size_t>(key);
            for (std::size_t i = 0; i < HashN; ++i)
                m_bits[hv[i] % Size] = true;
        }

        bool contains(const Key &key) const {
            auto hv = hashNT<HashN, std::size_t>(key);
            for (std::size_t i = 0; i < HashN; ++i)
                if (!m_bits[hv[i] % Size])
                    return false;
            return true;
        }

    private:
        std::bitset<Size> m_bits;
    };
}