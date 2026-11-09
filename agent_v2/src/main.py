# ConnectX agent: opening book + C++ exact solver (ctypes), pure-Python fallback.
import os
import sys
import time
import array
import bisect
import ctypes
import platform

_BOOK_NAME = "cx_book.bin"
_TRAP_NAME = "cx_traps.bin"  # positions from recorded games where opponents later erred
_LIB_NAMES = ("cx_solver_v2.so", "cx_solver_v1.so")  # v2 = popcnt build, v1 = baseline x86-64
_MOVE_BUDGET = 0.75  # seconds per move, hard cap for all search
_ORDER7 = (3, 2, 4, 1, 5, 0, 6)


def _find_dir():
    cands = []
    try:
        cands.append(os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        pass
    cands += [p for p in reversed(sys.path) if isinstance(p, str) and p]
    cands += ["/kaggle_simulations/agent", os.getcwd()]
    for d in cands:
        try:
            if os.path.isfile(os.path.join(d, _BOOK_NAME)) or any(
                os.path.isfile(os.path.join(d, n)) for n in _LIB_NAMES
            ):
                return d
        except Exception:
            pass
    return None


def _has_popcnt():
    try:
        with open("/proc/cpuinfo") as f:
            for line in f:
                if line.startswith("flags"):
                    return " popcnt" in line
    except Exception:
        pass
    return False


def _load_lib(d):
    if d is None or platform.machine().lower() not in ("x86_64", "amd64"):
        return None
    names = _LIB_NAMES if _has_popcnt() else _LIB_NAMES[1:]
    for n in names:
        p = os.path.join(d, n)
        if not os.path.isfile(p):
            continue
        try:
            lib = ctypes.CDLL(p)
            lib.cx_init.argtypes = [ctypes.c_int]
            lib.cx_init.restype = ctypes.c_int
            lib.cx_best_move2.argtypes = [
                ctypes.POINTER(ctypes.c_int), ctypes.c_int, ctypes.c_double, ctypes.c_int, ctypes.c_int,
                ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                ctypes.POINTER(ctypes.c_longlong),
            ]
            lib.cx_best_move2.restype = ctypes.c_int
            if lib.cx_version() == 2 and lib.cx_init(23) == 1:
                return lib
        except Exception:
            pass
    return None


def _load_book(d, name=_BOOK_NAME):
    if d is None:
        return None
    try:
        a = array.array("Q")
        with open(os.path.join(d, name), "rb") as f:
            a.frombytes(f.read())
        if sys.byteorder != "little":
            a.byteswap()
        return a
    except Exception:
        return None


class PySolver:
    """Generic bitboard solver for any (W, H, K): exact negamax + heuristic fallback."""

    def __init__(self, W, H, K):
        self.W, self.H, self.K = W, H, K
        self.SIZE = W * H
        H1 = H + 1
        self.bottom = sum(1 << (c * H1) for c in range(W))
        self.board = self.bottom * ((1 << H) - 1)
        self.colmask = [((1 << H) - 1) << (c * H1) for c in range(W)]
        self.top = [1 << (H - 1 + c * H1) for c in range(W)]
        self.order = sorted(range(W), key=lambda c: (abs(2 * c - (W - 1)), c))
        # (shift, sign) pairs: for every window offset, shifts that must all hit own stones
        dirs = (1, H1, H, H + 2)
        self.patterns = []
        for s in dirs:
            if K == 1:
                break
            for j in range(K):
                self.patterns.append([(i - j) * s for i in range(K) if i != j])
        self.tt = {}
        self.deadline = None
        self.nodes = 0

    def win_cells(self, pos, mask):
        if self.K == 1:
            return self.board ^ mask
        r = 0
        for pat in self.patterns:
            p = -1
            for d in pat:
                p &= (pos >> d) if d > 0 else (pos << -d)
                if not p:
                    break
            r |= p
        return r & (self.board ^ mask)

    def possible(self, mask):
        return (mask + self.bottom) & self.board

    def non_losing(self, cur, mask):
        pm = self.possible(mask)
        ow = self.win_cells(cur ^ mask, mask)
        forced = pm & ow
        if forced:
            if forced & (forced - 1):
                return 0
            pm = forced
        return pm & ~(ow >> 1)

    def ordered(self, cur, mask, nxt):
        mv = []
        for i, c in enumerate(self.order):
            m = nxt & self.colmask[c]
            if m:
                sc = bin(self.win_cells(cur | m, mask)).count("1")
                mv.append((-sc, i, m, c))
        mv.sort()
        return mv

    class Timeout(Exception):
        pass

    def negamax(self, cur, mask, moves, alpha, beta):
        self.nodes += 1
        if (self.nodes & 255) == 0 and self.deadline is not None and time.perf_counter() > self.deadline:
            raise PySolver.Timeout()
        nxt = self.non_losing(cur, mask)
        if not nxt:
            return -((self.SIZE - moves) // 2)
        if moves >= self.SIZE - 2:
            return 0
        lo = -((self.SIZE - 2 - moves) // 2)
        if alpha < lo:
            alpha = lo
            if alpha >= beta:
                return alpha
        hi = (self.SIZE - 1 - moves) // 2
        if beta > hi:
            beta = hi
            if alpha >= beta:
                return beta
        key = cur + mask
        e = self.tt.get(key)
        if e is not None:
            if e[0] == 0:  # lower bound
                if e[1] > alpha:
                    alpha = e[1]
                    if alpha >= beta:
                        return alpha
            elif e[1] < beta:  # upper bound
                beta = e[1]
                if alpha >= beta:
                    return beta
        for _, _, m, _ in self.ordered(cur, mask, nxt):
            s = -self.negamax(cur ^ mask, mask | m, moves + 1, -beta, -alpha)
            if s >= beta:
                self.tt[key] = (0, s)  # lower bound
                return s
            if s > alpha:
                alpha = s
        self.tt[key] = (1, alpha)  # upper bound
        return alpha

    def solve(self, cur, mask, moves):
        lo = -((self.SIZE - moves) // 2)
        hi = (self.SIZE + 1 - moves) // 2
        while lo < hi:
            med = lo + (hi - lo) // 2
            if med <= 0 and int(lo / 2) < med:
                med = int(lo / 2)
            elif med >= 0 and int(hi / 2) > med:
                med = int(hi / 2)
            r = self.negamax(cur, mask, moves, med, med + 1)
            if r <= med:
                hi = r
            else:
                lo = r
        return lo

    # depth-limited search with a simple threat-count evaluation
    def heur(self, cur, mask, moves, depth, alpha, beta):
        self.nodes += 1
        if (self.nodes & 255) == 0 and time.perf_counter() > self.deadline:
            raise PySolver.Timeout()
        pm = self.possible(mask)
        if self.win_cells(cur, mask) & pm:
            return 1000 - moves
        nxt = self.non_losing(cur, mask)
        if not nxt:
            return -(1000 - moves - 1)
        if moves >= self.SIZE - 2:
            return 0
        if depth == 0:
            a = bin(self.win_cells(cur, mask)).count("1")
            b = bin(self.win_cells(cur ^ mask, mask)).count("1")
            return a - b
        for _, _, m, _ in self.ordered(cur, mask, nxt):
            s = -self.heur(cur ^ mask, mask | m, moves + 1, depth - 1, -beta, -alpha)
            if s >= beta:
                return s
            if s > alpha:
                alpha = s
        return alpha

    def best_move(self, cur, mask, moves, deadline, prefer=None):
        legal = [c for c in self.order if not (mask & self.top[c])]
        if not legal:
            return None
        pm = self.possible(mask)
        w = self.win_cells(cur, mask) & pm
        for c in legal:
            if w & self.colmask[c]:
                return c
        nxt = self.non_losing(cur, mask)
        if not nxt:
            forced = pm & self.win_cells(cur ^ mask, mask)
            for c in legal:
                if forced & self.colmask[c]:
                    return c
            return legal[0]
        cand = self.ordered(cur, mask, nxt)
        cand.sort(key=lambda t: t[3] != prefer)  # preferred column is tried first
        if len(cand) == 1:
            return cand[0][3]
        self.deadline = deadline
        if len(self.tt) > 2000000:
            self.tt.clear()
        try:  # exact
            s = self.solve(cur, mask, moves)
            for _, _, m, c in cand:
                r = self.negamax(cur ^ mask, mask | m, moves + 1, -s, -s + 1)
                if r <= -s:
                    return c
        except PySolver.Timeout:
            pass
        best = cand[0][3]
        try:  # iterative deepening fallback
            d = 2
            while d <= self.SIZE - moves:
                self.deadline = deadline
                bs, bc = None, None
                for _, _, m, c in cand:
                    s = -self.heur(cur ^ mask, mask | m, moves + 1, d - 1, -10 ** 6, 10 ** 6)
                    if bs is None or s > bs:
                        bs, bc = s, c
                best = bc
                d += 2
        except PySolver.Timeout:
            pass
        return best


def _board_to_bits(board, W, H, mark):
    cur = mask = moves = 0
    H1 = H + 1
    for c in range(W):
        gap = False
        for r in range(H - 1, -1, -1):
            v = board[r * W + c]
            if v == 0:
                gap = True
                continue
            if gap:
                return None
            b = 1 << (c * H1 + (H - 1 - r))
            mask |= b
            if v == mark:
                cur |= b
            moves += 1
    return cur, mask, moves


def _mirror7(k):
    r = 0
    for c in range(7):
        r |= ((k >> (c * 7)) & 0x7F) << ((6 - c) * 7)
    return r


def _book_lookup(book, cur, mask):
    if not book:
        return None
    k = cur + mask
    mk = _mirror7(k)
    mir = mk < k
    ck = mk if mir else k
    i = bisect.bisect_left(book, ck << 3)
    if i < len(book) and (book[i] >> 3) == ck:
        c = book[i] & 7
        return 6 - c if mir else c
    return None


def _get(obj, name, default=None):
    try:
        v = obj[name]
        return default if v is None else v
    except Exception:
        v = getattr(obj, name, None)
        return default if v is None else v


_DIR = _find_dir()
_STATE = {"lib": _load_lib(_DIR), "book": _load_book(_DIR), "traps": _load_book(_DIR, _TRAP_NAME),
          "py": {}, "last": ""}


def agent(observation, configuration):
    t0 = time.perf_counter()
    board = list(_get(observation, "board", []))
    mark = int(_get(observation, "mark", 1))
    W = int(_get(configuration, "columns", 7))
    H = int(_get(configuration, "rows", 6))
    K = int(_get(configuration, "inarow", 4))
    legal = sorted((c for c in range(W) if c < len(board) and board[c] == 0),
                   key=lambda c: (abs(2 * c - (W - 1)), c))
    if not legal:
        return 0
    try:
        bits = _board_to_bits(board, W, H, mark) if len(board) == W * H else None
        if bits is None:
            _STATE["last"] = "malformed"
            return legal[0]
        cur, mask, moves = bits
        prefer = None
        if (W, H, K) == (7, 6, 4):
            prefer = _book_lookup(_STATE["traps"], cur, mask)
            # book entries are exact best moves (positions with an instant win are never stored)
            c = _book_lookup(_STATE["book"], cur, mask)
            if c is not None and c in legal:
                _STATE["last"] = "book"
                return c
            lib = _STATE["lib"]
            if lib is not None:
                arr = (ctypes.c_int * 42)(*board)
                sc, fl, nd = ctypes.c_int(0), ctypes.c_int(0), ctypes.c_longlong(0)
                left = _MOVE_BUDGET - (time.perf_counter() - t0)
                r = lib.cx_best_move2(arr, mark, max(0.05, left), -1 if prefer is None else prefer, 1,
                                      ctypes.byref(sc), ctypes.byref(fl), ctypes.byref(nd))
                if r in legal:
                    _STATE["last"] = "cpp:%d:%d:%d" % (fl.value, sc.value, nd.value)
                    return r
        key = (W, H, K)
        ps = _STATE["py"].get(key)
        if ps is None:
            ps = _STATE["py"][key] = PySolver(W, H, K)
        deadline = t0 + _MOVE_BUDGET
        r = ps.best_move(cur, mask, moves, deadline, prefer)
        if r in legal:
            _STATE["last"] = "py"
            return r
    except Exception as e:
        _STATE["last"] = "error:%r" % (e,)
    return legal[0]
