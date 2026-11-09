// Verify solver scores against "moves score" test files.
#include "../src/cx_core.h"
#include <stdio.h>
using namespace cx;
int main(int argc, char** argv) {
  Solver S; S.init(24);
  char seq[128]; int expect, n = 0, bad = 0; double tmax = 0, tsum = 0;
  FILE* f = fopen(argv[1], "r");
  while (fscanf(f, "%127s %d", seq, &expect) == 2) {
    Position P;
    for (char* p = seq; *p; p++) P.play_col(*p - '1');
    S.tt.clear();
    double t0 = now_sec();
    int s = S.solve(P);
    double dt = now_sec() - t0; tsum += dt; if (dt > tmax) tmax = dt;
    if (s != expect) { bad++; if (bad < 5) printf("MISMATCH %s got %d expect %d\n", seq, s, expect); }
    n++;
  }
  printf("%s: %d positions, %d mismatches, mean %.5fs max %.4fs\n", argv[1], n, bad, tsum / n, tmax);
  return bad != 0;
}
