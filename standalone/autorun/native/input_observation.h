#pragma once

#include <algorithm>
#include <cstdint>

namespace AutorunInput {

constexpr std::uint64_t MaximumAgeMs = 1000;
constexpr std::uint64_t InitialObservationMs = 500;
constexpr std::uint64_t InitialObservationHits = 30;
constexpr std::uint64_t ReplacementObservationMs = 1500;
constexpr std::uint64_t ReplacementObservationHits = 60;

enum class Readiness { Ready, Missing, DifferentSession, Stale, Warming, Revalidating, Busy };

struct Snapshot {
    Readiness readiness{Readiness::Missing};
    const void* stable_input{};
    std::uint64_t hits{}, age_ms{}, idle_ms{}, replacements{};
};

class Observation {
public:
    // Returns true when the input address changed within the same world session.
    bool observe(const void* input, std::uint64_t session, std::uint64_t now) noexcept {
        if (!input || !session || !now) return false;
        if (session_ != session) {
            *this = {};
            session_ = session;
        }
        if (input_ != input) {
            const bool replaced = input_ != nullptr;
            if (replaced) ++replacements_;
            input_ = input;
            first_ms_ = last_ms_ = now;
            hits_ = 1;
            revalidating_ = replaced;
            return replaced;
        }
        // A paused producer cannot count old samples toward a new qualification.
        // Callbacks from different threads can arrive in timestamp order but
        // acquire this lock in the opposite order. Do not reset a valid source.
        if (now < last_ms_) return false;
        if (now - last_ms_ > MaximumAgeMs) {
            first_ms_ = last_ms_ = now;
            hits_ = 1;
            return false;
        }
        ++hits_;
        last_ms_ = now;
        return false;
    }

    Snapshot snapshot(std::uint64_t session, std::uint64_t now) const noexcept {
        Snapshot result{};
        result.replacements = replacements_;
        if (!session || !input_) return result;
        if (session_ != session) {
            result.readiness = Readiness::DifferentSession;
            return result;
        }
        result.hits = hits_;
        // A caller may capture now just before a callback updates last_ms_;
        // that fresh callback means the input is ready, not stale.
        const auto sampled_now = std::max(now, last_ms_);
        result.age_ms = sampled_now - first_ms_;
        result.idle_ms = sampled_now - last_ms_;
        if (result.idle_ms > MaximumAgeMs) {
            result.readiness = Readiness::Stale;
            return result;
        }
        const auto required_hits = revalidating_ ? ReplacementObservationHits : InitialObservationHits;
        const auto required_ms = revalidating_ ? ReplacementObservationMs : InitialObservationMs;
        if (hits_ < required_hits || result.age_ms < required_ms) {
            result.readiness = revalidating_ ? Readiness::Revalidating : Readiness::Warming;
            return result;
        }
        result.readiness = Readiness::Ready;
        result.stable_input = input_;
        return result;
    }

private:
    std::uint64_t session_{}, first_ms_{}, last_ms_{}, hits_{}, replacements_{};
    const void* input_{};
    bool revalidating_{};
};

} // namespace AutorunInput
