// C ABI for ctypes.
#include "cx_core.h"

static cx::Solver g_solver;
static bool g_ready = false;

#define API __attribute__((visibility("default")))
extern "C" {

// Allocate the transposition table (2^log2 entries, 5 bytes each). Returns 1 on success.
API int cx_init(int log2) {
  if (log2 < 18) log2 = 18;
  if (log2 > 30) log2 = 30;
  g_ready = g_solver.init(log2);
  return g_ready ? 1 : 0;
}

// board: 42 ints row-major (row 0 = top), 0 empty / 1 / 2. `mark` is the side to move.
// Returns column, or -1 on error. score/flag/nodes are optional outputs.
API int cx_best_move(const int* board, int mark, double time_limit, int* score, int* flag, long long* nodes) {
  if (!g_ready && !cx_init(23)) return -1;
  cx::Position P;
  if (!cx::from_board(board, mark, P)) return -1;
  g_solver.nodes = 0;
  int c = g_solver.best_move(P, time_limit, score, flag, -1, false);
  if (nodes) *nodes = (long long)g_solver.nodes;
  return c;
}

// Same, with a preferred column (-1 = none; used only if it is optimal) and tie-break switch.
API int cx_best_move2(const int* board, int mark, double time_limit, int prefer, int tiebreak, int* score,
                      int* flag, long long* nodes) {
  if (!g_ready && !cx_init(23)) return -1;
  cx::Position P;
  if (!cx::from_board(board, mark, P)) return -1;
  g_solver.nodes = 0;
  int c = g_solver.best_move(P, time_limit, score, flag, prefer, tiebreak != 0);
  if (nodes) *nodes = (long long)g_solver.nodes;
  return c;
}

// Exact score for each of the 7 columns (-1000 = illegal). Returns 0 on success.
API int cx_analyze(const int* board, int mark, int* scores) {
  if (!g_ready && !cx_init(23)) return -1;
  cx::Position P;
  if (!cx::from_board(board, mark, P)) return -1;
  g_solver.analyze(P, scores);
  return 0;
}

// Solve a position given as a move string of columns '1'..'7'. Returns score (or -1000).
API int cx_solve_moves(const char* seq) {
  if (!g_ready && !cx_init(23)) return cx::INVALID;
  cx::Position P;
  for (const char* p = seq; *p; p++) {
    int c = *p - '1';
    if (c < 0 || c >= cx::W || !P.can_play(c) || P.is_winning_col(c)) return cx::INVALID;
    P.play_col(c);
  }
  return g_solver.solve(P);
}

API void cx_clear(void) { if (g_ready) g_solver.tt.clear(); }

API int cx_version(void) { return 2; }
}
