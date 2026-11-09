// Evaluate every position of recorded games.
// input lines: "<id> <moves 1..7>"; output lines: "<id> <ply> <wdl> <exact or 99>"
// wdl/exact are from the side-to-move's view. exact computed only when moves >= exact_from.
#include "../src/cx_core.h"
#include <stdio.h>
#include <string>
#include <unordered_map>

using namespace cx;

static Solver S;

static int weak(const Position& P) {
  if (P.can_win_next()) return 1;
  if (P.non_losing() == 0) return -1;
  int r = S.negamax(P, 0, 1);
  if (r > 0) return 1;
  r = S.negamax(P, -1, 0);
  return r < 0 ? -1 : 0;
}

int main(int argc, char** argv) {
  int exact_from = argc > 1 ? atoi(argv[1]) : 12;
  S.init(argc > 2 ? atoi(argv[2]) : 27);
  std::unordered_map<uint64_t, std::pair<int, int>> cache;
  char id[64], mv[64];
  double t0 = now_sec();
  int ng = 0;
  while (scanf("%63s %63s", id, mv) == 2) {
    Position P;
    for (int i = 0;; i++) {
      // position before move i
      uint64_t k = P.key();
      auto it = cache.find(k);
      std::pair<int, int> v;
      if (it != cache.end()) v = it->second;
      else {
        int w = P.moves >= SIZE ? 0 : weak(P);
        int e = (P.moves >= exact_from && P.moves < SIZE) ? S.solve(P) : 99;
        v = {w, e};
        cache[k] = v;
      }
      printf("%s %d %d %d\n", id, i, v.first, v.second);
      if (!mv[i]) break;
      int c = mv[i] - '1';
      if (P.is_winning_col(c)) { printf("%s %d WINMOVE\n", id, i); break; }
      P.play_col(c);
    }
    fflush(stdout);
    fprintf(stderr, "game %d done t=%.0fs\n", ++ng, now_sec() - t0);
  }
}
