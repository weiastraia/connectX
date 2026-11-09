// Opening book generator.
// Book = every position (up to maxply) where "we" are to move, reachable when we follow the
// book and the opponent plays anything. Entry: (canonical_key << 3) | best_col (canonical frame).
//
// usage:
//   bookgen shallow <side> <split> <out_frontier> <out_entries>      (phase 1, single process)
//   bookgen deep <side> <maxply> <frontier> <wid> <nworkers> <out_entries> [tt_log2]
#include "../src/cx_core.h"
#include <stdio.h>
#include <string>
#include <vector>
#include <unordered_set>
#include <unordered_map>

using namespace cx;

static Solver S;
static std::unordered_set<uint64_t> seen;
static std::vector<uint64_t> entries;
static long long solved = 0;
static double t_start;
static std::unordered_map<uint64_t, int> traps;  // canonical key -> preferred col (canonical frame)
static bool tiebreak = true;

static uint64_t canon(const Position& P, bool* mirrored) {
  uint64_t k = P.key(), m = mirror(k);
  *mirrored = m < k;
  return *mirrored ? m : k;
}

static Position mirror_pos(const Position& P) {
  Position Q;
  Q.cur = mirror(P.cur); Q.mask = mirror(P.mask); Q.moves = P.moves;
  return Q;
}

// Best move for P computed in the canonical frame; records an entry when a search was needed.
static int book_move(const Position& P, bool record) {
  bool mir;
  uint64_t k = canon(P, &mir);
  Position Q = mir ? mirror_pos(P) : P;
  int sc, fl;
  auto it = traps.find(k);
  int c = S.best_move(Q, 0, &sc, &fl, it == traps.end() ? -1 : it->second, tiebreak);
  if (c < 0) return -1;
  if (record && fl == 0) entries.push_back(k << 3 | (uint64_t)c);
  solved++;
  if ((solved & 4095) == 0) {
    fprintf(stderr, "  solved=%lld entries=%zu t=%.0fs\n", solved, entries.size(), now_sec() - t_start);
  }
  return mir ? W - 1 - c : c;
}

static bool is_our_turn(const Position& P, int side) { return (P.moves % 2) == (side - 1); }

// Expand: at our turn play book move; at opponent turn try all moves.
// frontier != nullptr: stop at our-turn nodes with moves >= split and collect them.
static void dfs(const Position& P, int side, int maxply, int split, std::vector<uint64_t>* frontier) {
  if (P.moves >= SIZE) return;
  if (is_our_turn(P, side)) {
    if (P.moves > maxply) return;
    bool mir;
    uint64_t k = canon(P, &mir);
    if (!seen.insert(k).second) return;
    if (frontier && P.moves >= split) {
      frontier->push_back(P.cur);
      frontier->push_back(P.mask);
      return;
    }
    if (P.can_win_next()) return;  // trivial win, game ends
    int c = book_move(P, true);
    if (c < 0) return;
    Position P2(P);
    P2.play_col(c);
    dfs(P2, side, maxply, split, frontier);
  } else {
    for (int i = 0; i < W; i++) {
      int c = ORDER[i];
      if (!P.can_play(c) || P.is_winning_col(c)) continue;  // opponent win ends the game
      Position P2(P);
      P2.play_col(c);
      dfs(P2, side, maxply, split, frontier);
    }
  }
}

static void write_u64(const char* path, const std::vector<uint64_t>& v) {
  FILE* f = fopen(path, "wb");
  fwrite(v.data(), 8, v.size(), f);
  fclose(f);
}

static std::vector<uint64_t> read_u64(const char* path) {
  std::vector<uint64_t> v;
  FILE* f = fopen(path, "rb");
  uint64_t x;
  while (fread(&x, 8, 1, f) == 1) v.push_back(x);
  fclose(f);
  return v;
}

int main(int argc, char** argv) {
  t_start = now_sec();
  // optional env: CX_TRAPS=<file of (key<<3|col)>, CX_TIEBREAK=0 for the old policy
  if (const char* tf = getenv("CX_TRAPS")) {
    FILE* f = fopen(tf, "rb");
    uint64_t x;
    while (f && fread(&x, 8, 1, f) == 1) traps[x >> 3] = (int)(x & 7);
    if (f) fclose(f);
    fprintf(stderr, "loaded %zu traps\n", traps.size());
  }
  if (const char* tb = getenv("CX_TIEBREAK")) tiebreak = atoi(tb) != 0;
  std::string mode = argv[1];
  int side = atoi(argv[2]);
  if (mode == "shallow") {
    int split = atoi(argv[3]);
    S.init(27);
    std::vector<uint64_t> frontier;
    dfs(Position(), side, 99, split, &frontier);
    write_u64(argv[4], frontier);
    write_u64(argv[5], entries);
    fprintf(stderr, "shallow side=%d frontier=%zu entries=%zu t=%.1fs\n", side, frontier.size() / 2,
            entries.size(), now_sec() - t_start);
  } else {
    int maxply = atoi(argv[3]);
    std::vector<uint64_t> fr = read_u64(argv[4]);
    int wid = atoi(argv[5]), nw = atoi(argv[6]);
    int tlog = argc > 8 ? atoi(argv[8]) : 26;
    S.init(tlog);
    size_t nf = fr.size() / 2;
    for (size_t i = wid; i < nf; i += nw) {
      Position P;
      P.cur = fr[2 * i]; P.mask = fr[2 * i + 1]; P.moves = popcount(P.mask);
      if (P.can_win_next()) continue;
      int c = book_move(P, true);
      if (c < 0) continue;
      Position P2(P);
      P2.play_col(c);
      dfs(P2, side, maxply, 0, nullptr);
      fprintf(stderr, "[w%d] frontier %zu/%zu done, entries=%zu t=%.0fs\n", wid, i + 1, nf, entries.size(),
              now_sec() - t_start);
    }
    write_u64(argv[7], entries);
    fprintf(stderr, "[w%d] finished entries=%zu solved=%lld t=%.0fs\n", wid, entries.size(), solved,
            now_sec() - t_start);
  }
}
