// Timing benchmark: best_move on random positions at a given ply.
// usage: bench <ply> <count> [seed] [persistent_tt 0/1]
#include "../src/cx_core.h"
#include <stdio.h>
#include <random>
#include <vector>
#include <algorithm>

using namespace cx;

int main(int argc, char** argv) {
  int ply = argc > 1 ? atoi(argv[1]) : 12;
  int count = argc > 2 ? atoi(argv[2]) : 100;
  unsigned seed = argc > 3 ? atoi(argv[3]) : 1;
  bool persist = argc > 4 ? atoi(argv[4]) : 0;
  std::mt19937 rng(seed);
  Solver S;
  S.init(23);
  std::vector<double> t;
  int made = 0;
  while (made < count) {
    Position P;
    bool ok = true;
    for (int i = 0; i < ply && ok; i++) {
      int legal[W], n = 0;
      for (int c = 0; c < W; c++) if (P.can_play(c) && !P.is_winning_col(c)) legal[n++] = c;
      if (!n) { ok = false; break; }
      P.play_col(legal[rng() % n]);
    }
    if (!ok || P.non_losing() == 0) continue;
    if (!persist) S.tt.clear();
    int sc, fl;
    double t0 = now_sec();
    S.best_move(P, 0, &sc, &fl);
    t.push_back(now_sec() - t0);
    made++;
  }
  std::sort(t.begin(), t.end());
  double sum = 0;
  for (double x : t) sum += x;
  printf("ply=%d n=%d mean=%.4fs p50=%.4fs p90=%.4fs p99=%.4fs max=%.4fs\n", ply, count, sum / count,
         t[count / 2], t[count * 9 / 10], t[count * 99 / 100], t.back());
}
