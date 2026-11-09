// Test-only imperfect opponent: depth-limited alpha-beta with a threat-count evaluation and
// random tie-breaking. Built as a separate .so; never part of the submission.
#include "../src/cx_core.h"

using namespace cx;

static uint64_t rng_state = 1;
static inline uint32_t rnd() {
  rng_state ^= rng_state << 13; rng_state ^= rng_state >> 7; rng_state ^= rng_state << 17;
  return (uint32_t)rng_state;
}

static int evaluate(const Position& P) {
  // threats of side to move minus opponent's, low threats weigh more
  uint64_t a = P.winning(), b = P.opp_winning();
  return 2 * (popcount(a) - popcount(b)) + (popcount(a & P.possible()) - popcount(b & P.possible()));
}

static int search(const Position& P, int depth, int alpha, int beta) {
  if (P.can_win_next()) return 1000 - P.moves;
  uint64_t nl = P.non_losing();
  if (!nl) return -(1000 - P.moves - 1);
  if (P.moves >= SIZE - 1) return 0;
  if (depth == 0) return evaluate(P);
  for (int i = 0; i < W; i++) {
    uint64_t m = nl & col_mask(ORDER[i]);
    if (!m) continue;
    Position P2(P);
    P2.play_bit(m);
    int s = -search(P2, depth - 1, -beta, -alpha);
    if (s >= beta) return s;
    if (s > alpha) alpha = s;
  }
  return alpha;
}

extern "C" __attribute__((visibility("default"))) int opp_move(const int* board, int mark, int depth,
                                                               unsigned seed) {
  Position P;
  if (!from_board(board, mark, P)) return -1;
  rng_state = seed * 2654435761ULL + 1;
  int best = -100000, bc[W], nb = 0;
  for (int c = 0; c < W; c++) {
    if (!P.can_play(c)) continue;
    int s;
    if (P.is_winning_col(c)) s = 100000;
    else {
      Position P2(P);
      P2.play_col(c);
      s = -search(P2, depth - 1, -100000, 100000);
    }
    if (s > best) { best = s; nb = 0; }
    if (s == best) bc[nb++] = c;
  }
  return nb ? bc[rnd() % nb] : -1;
}
