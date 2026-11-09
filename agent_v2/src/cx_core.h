// Connect 4 (7x6) exact solver core: bitboard + negamax/alpha-beta + TT.
// No STL / no libstdc++ runtime needed, so the shared library stays portable.
#pragma once
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

namespace cx {

constexpr int W = 7, H = 6, SIZE = W * H;
constexpr int MIN_SCORE = -(W * H) / 2 + 3;
constexpr int MAX_SCORE = (W * H + 1) / 2 - 3;
constexpr int INVALID = -1000;

constexpr uint64_t bottom_rec(int w) { return w == 0 ? 0 : bottom_rec(w - 1) | 1ULL << (w - 1) * (H + 1); }
constexpr uint64_t BOTTOM = bottom_rec(W);
constexpr uint64_t BOARD = BOTTOM * ((1ULL << H) - 1);

// center-first column order
constexpr int ORDER[W] = {3, 2, 4, 1, 5, 0, 6};

static inline uint64_t top_col(int c) { return 1ULL << ((H - 1) + c * (H + 1)); }
static inline uint64_t bottom_col(int c) { return 1ULL << c * (H + 1); }
static inline uint64_t col_mask(int c) { return ((1ULL << H) - 1) << c * (H + 1); }
static inline int popcount(uint64_t x) { return __builtin_popcountll(x); }

// Empty cells that would complete a 4-in-a-row for `pos`.
static inline uint64_t winning_cells(uint64_t pos, uint64_t mask) {
  uint64_t r = (pos << 1) & (pos << 2) & (pos << 3);  // vertical
  uint64_t p;
  const int S[3] = {H + 1, H, H + 2};  // horizontal, diag /, diag \ .
  for (int i = 0; i < 3; i++) {
    const int s = S[i];
    p = (pos << s) & (pos << 2 * s);
    r |= p & (pos << 3 * s);
    r |= p & (pos >> s);
    p = (pos >> s) & (pos >> 2 * s);
    r |= p & (pos << s);
    r |= p & (pos >> 3 * s);
  }
  return r & (BOARD ^ mask);
}

struct Position {
  uint64_t cur = 0;   // stones of the side to move
  uint64_t mask = 0;  // all stones
  int moves = 0;

  bool can_play(int c) const { return (mask & top_col(c)) == 0; }
  void play_bit(uint64_t m) { cur ^= mask; mask |= m; moves++; }
  uint64_t col_bit(int c) const { return (mask + bottom_col(c)) & col_mask(c); }
  void play_col(int c) { play_bit(col_bit(c)); }
  uint64_t key() const { return cur + mask; }
  uint64_t possible() const { return (mask + BOTTOM) & BOARD; }
  uint64_t winning() const { return winning_cells(cur, mask); }
  uint64_t opp_winning() const { return winning_cells(cur ^ mask, mask); }
  bool can_win_next() const { return winning() & possible(); }
  bool is_winning_col(int c) const { return winning() & possible() & col_mask(c); }
  // Moves that do not hand the opponent an immediate win (0 if none).
  uint64_t non_losing() const {
    uint64_t pm = possible();
    uint64_t ow = opp_winning();
    uint64_t forced = pm & ow;
    if (forced) {
      if (forced & (forced - 1)) return 0;  // two threats: lost
      pm = forced;
    }
    return pm & ~(ow >> 1);
  }
  int move_score(uint64_t m) const { return popcount(winning_cells(cur | m, mask)); }
};

// Mirror a key (or any column-local bitboard) left<->right.
static inline uint64_t mirror(uint64_t k) {
  uint64_t r = 0;
  for (int c = 0; c < W; c++) r |= ((k >> (c * (H + 1))) & 0x7F) << ((W - 1 - c) * (H + 1));
  return r;
}

static inline int bit_col(uint64_t m) { return __builtin_ctzll(m) / (H + 1); }

struct MoveSorter {
  struct E { uint64_t m; int s; } e[W];
  int n = 0;
  void add(uint64_t m, int s) {
    int p = n++;
    for (; p && e[p - 1].s > s; --p) e[p] = e[p - 1];
    e[p].m = m; e[p].s = s;
  }
  uint64_t next() { return n ? e[--n].m : 0; }
};

// Transposition table: exact keys via (key mod prime, low 32 bits).
struct TT {
  uint32_t* K = nullptr;
  uint8_t* V = nullptr;
  uint64_t size = 0;

  static bool is_prime(uint64_t n) {
    if (n < 2) return false;
    for (uint64_t d = 2; d * d <= n; d++) if (n % d == 0) return false;
    return true;
  }
  bool init(int log2) {
    free(K); free(V);
    size = (1ULL << log2) + 1;
    while (!is_prime(size)) size++;
    K = (uint32_t*)calloc(size, sizeof(uint32_t));
    V = (uint8_t*)calloc(size, 1);
    return K && V;
  }
  void clear() { memset(K, 0, size * sizeof(uint32_t)); memset(V, 0, size); }
  void put(uint64_t k, uint8_t v) { uint64_t i = k % size; K[i] = (uint32_t)k; V[i] = v; }
  uint8_t get(uint64_t k) const { uint64_t i = k % size; return K[i] == (uint32_t)k ? V[i] : 0; }
};

static inline double now_sec() {
  struct timespec ts;
  clock_gettime(CLOCK_MONOTONIC, &ts);
  return ts.tv_sec + ts.tv_nsec * 1e-9;
}

struct Solver {
  TT tt;
  uint64_t nodes = 0;
  double deadline = 0;  // 0 = no limit
  bool aborted = false;

  bool init(int log2) { return tt.init(log2); }

  // Precondition: side to move cannot win immediately.
  int negamax(const Position& P, int alpha, int beta) {
    if ((++nodes & 1023) == 0 && deadline > 0 && now_sec() > deadline) aborted = true;
    if (aborted) return 0;

    uint64_t next = P.non_losing();
    if (next == 0) return -(SIZE - P.moves) / 2;
    if (P.moves >= SIZE - 2) return 0;

    int lo = -(SIZE - 2 - P.moves) / 2;
    if (alpha < lo) { alpha = lo; if (alpha >= beta) return alpha; }
    int hi = (SIZE - 1 - P.moves) / 2;
    if (beta > hi) { beta = hi; if (alpha >= beta) return beta; }

    const uint64_t key = P.key();
    if (int v = tt.get(key)) {
      if (v > MAX_SCORE - MIN_SCORE + 1) {  // lower bound
        lo = v + 2 * MIN_SCORE - MAX_SCORE - 2;
        if (alpha < lo) { alpha = lo; if (alpha >= beta) return alpha; }
      } else {  // upper bound
        hi = v + MIN_SCORE - 1;
        if (beta > hi) { beta = hi; if (alpha >= beta) return beta; }
      }
    }

    MoveSorter ms;
    for (int i = W; i--;)
      if (uint64_t m = next & col_mask(ORDER[i])) ms.add(m, P.move_score(m));

    while (uint64_t m = ms.next()) {
      Position P2(P);
      P2.play_bit(m);
      int s = -negamax(P2, -beta, -alpha);
      if (aborted) return 0;
      if (s >= beta) {
        tt.put(key, (uint8_t)(s + MAX_SCORE - 2 * MIN_SCORE + 2));
        return s;
      }
      if (s > alpha) alpha = s;
    }
    tt.put(key, (uint8_t)(alpha - MIN_SCORE + 1));
    return alpha;
  }

  // Exact score of P (positive: side to move wins; larger = sooner).
  int solve(const Position& P) {
    if (P.can_win_next()) return (SIZE + 1 - P.moves) / 2;
    int lo = -(SIZE - P.moves) / 2, hi = (SIZE + 1 - P.moves) / 2;
    while (lo < hi) {
      int med = lo + (hi - lo) / 2;
      if (med <= 0 && lo / 2 < med) med = lo / 2;
      else if (med >= 0 && hi / 2 > med) med = hi / 2;
      int r = negamax(P, med, med + 1);
      if (aborted) return 0;
      if (r <= med) hi = r; else lo = r;
    }
    return lo;
  }

  // Candidate non-losing moves in search order (best heuristic first).
  int ordered_moves(const Position& P, uint64_t next, int out[W]) {
    MoveSorter ms;
    for (int i = W; i--;)
      if (uint64_t m = next & col_mask(ORDER[i])) ms.add(m, P.move_score(m));
    int n = 0;
    while (uint64_t m = ms.next()) out[n++] = bit_col(m);
    return n;
  }

  // Outcome class (-1/0/1) of P for the side to move.
  int outcome(const Position& P) {
    if (P.moves >= SIZE) return 0;
    if (P.can_win_next()) return 1;
    if (P.non_losing() == 0) return -1;
    int r = negamax(P, 0, 1);
    if (r > 0) return 1;
    return negamax(P, -1, 0) < 0 ? -1 : 0;
  }

  // Q: opponent to move after our move; `cls` = our outcome class (-1 lost, 0 draw).
  // good = opponent replies that keep our class <= cls; plausible = replies not losing at once.
  // Returns false on timeout.
  bool reply_stats(const Position& Q, int cls, int* good, int* plausible) {
    uint64_t nl = Q.non_losing();
    *good = 0; *plausible = 0;
    for (int c = 0; c < W; c++) {
      uint64_t m = nl & col_mask(c);
      if (!m) continue;
      ++*plausible;
      Position R(Q);
      R.play_bit(m);
      int ok;
      if (R.moves >= SIZE) ok = 0 <= cls;
      else if (R.can_win_next()) ok = 0;
      else if (R.non_losing() == 0) ok = 1;
      else ok = negamax(R, cls, cls + 1) <= cls;
      if (aborted) return false;
      *good += ok;
    }
    return true;
  }

  // Best move. flag: 0 exact, 1 trivial/forced (score may be approximate), 2 timeout fallback.
  // Among moves with the optimal exact score: winning -> fastest win (first in order);
  // draw/lost -> `prefer` if optimal, else the move leaving the opponent the fewest good replies
  // (then the most plausible bad ones). tiebreak=false keeps the plain first optimal move.
  int best_move(const Position& P, double time_limit, int* score_out, int* flag_out, int prefer = -1,
                bool tiebreak = true) {
    int dummy_s, dummy_f;
    if (!score_out) score_out = &dummy_s;
    if (!flag_out) flag_out = &dummy_f;
    *flag_out = 0;
    if (P.moves >= SIZE) { *score_out = 0; return -1; }

    for (int i = 0; i < W; i++) {
      int c = ORDER[i];
      if (P.can_play(c) && P.is_winning_col(c)) { *score_out = (SIZE + 1 - P.moves) / 2; return c; }
    }
    uint64_t next = P.non_losing();
    if (next == 0) {  // lost in one: block one threat if possible, else any legal move
      *flag_out = 1;
      *score_out = -(SIZE - P.moves) / 2;
      uint64_t forced = P.possible() & P.opp_winning();
      if (forced) return bit_col(forced);
      for (int i = 0; i < W; i++) if (P.can_play(ORDER[i])) return ORDER[i];
      return -1;
    }
    int cand[W];
    int n = ordered_moves(P, next, cand);
    if (n == 1) { *flag_out = 1; *score_out = 0; return cand[0]; }  // forced

    aborted = false;
    deadline = time_limit > 0 ? now_sec() + time_limit : 0;
    int s = solve(P);
    if (!aborted) {
      int opt[W], no = 0;
      for (int i = 0; i < n; i++) {
        Position P2(P);
        P2.play_col(cand[i]);
        int r = negamax(P2, -s, -s + 1);
        if (aborted) break;
        if (r <= -s) {
          opt[no++] = cand[i];
          if (s > 0 || (!tiebreak && prefer < 0)) break;  // fastest win / plain mode
        }
      }
      if (no > 0) {
        int pick = opt[0];
        bool pref = false;
        for (int j = 0; j < no; j++) if (opt[j] == prefer) { pick = prefer; pref = true; }
        if (!pref && tiebreak && s <= 0 && no > 1 && !aborted) {
          int cls = s < 0 ? -1 : 0, bg = 99, bb = -1;
          for (int j = 0; j < no; j++) {
            Position Q(P);
            Q.play_col(opt[j]);
            int g, pl;
            if (!reply_stats(Q, cls, &g, &pl)) break;  // timeout: keep best so far
            if (g < bg || (g == bg && pl - g > bb)) { bg = g; bb = pl - g; pick = opt[j]; }
          }
        }
        deadline = 0;
        aborted = false;
        *score_out = s;
        return pick;
      }
    }
    deadline = 0;
    bool to = aborted;
    aborted = false;
    *flag_out = to ? 2 : 1;
    *score_out = to ? 0 : s;
    return cand[0];
  }

  // Exact score of every column (INVALID if not playable). Used for tests.
  void analyze(const Position& P, int scores[W]) {
    for (int c = 0; c < W; c++) {
      if (!P.can_play(c)) { scores[c] = INVALID; continue; }
      if (P.is_winning_col(c)) { scores[c] = (SIZE + 1 - P.moves) / 2; continue; }
      Position P2(P);
      P2.play_col(c);
      scores[c] = -solve(P2);
    }
  }
};

// Board (row-major, row 0 = top) -> Position with `mark` to move. Returns false if malformed.
static inline bool from_board(const int* board, int mark, Position& P) {
  P = Position();
  uint64_t mine = 0;
  for (int c = 0; c < W; c++) {
    bool gap = false;
    for (int r = H - 1; r >= 0; r--) {
      int v = board[r * W + c];
      if (v == 0) { gap = true; continue; }
      if (gap || (v != 1 && v != 2)) return false;
      uint64_t b = 1ULL << (c * (H + 1) + (H - 1 - r));
      P.mask |= b;
      if (v == mark) mine |= b;
      P.moves++;
    }
  }
  P.cur = mine;
  return true;
}

}  // namespace cx
