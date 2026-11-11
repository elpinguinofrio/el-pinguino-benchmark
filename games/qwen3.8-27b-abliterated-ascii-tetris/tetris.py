#!/usr/bin/env python3
"""ASCII Tetris for the terminal (no sound).

Controls:
  <-/->    move
  up / x   rotate clockwise
  z        rotate counter-clockwise
  down     soft drop
  space    hard drop
  h        hold
  p        pause
  q        quit
"""
import curses
import random
import sys
import time

COLS, ROWS = 10, 20
TICK = 0.03
LOCK_DELAY = 0.3
LINE_SCORE = [0, 100, 300, 500, 800]

SHAPES = {
    "I": [[0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0]],
    "O": [[1, 1], [1, 1]],
    "T": [[0, 1, 0], [1, 1, 1], [0, 0, 0]],
    "S": [[0, 1, 1], [1, 1, 0], [0, 0, 0]],
    "Z": [[1, 1, 0], [0, 1, 1], [0, 0, 0]],
    "J": [[1, 0, 0], [1, 1, 1], [0, 0, 0]],
    "L": [[0, 0, 1], [1, 1, 1], [0, 0, 0]],
}
CHARS = {"I": "i", "O": "o", "T": "t", "S": "s", "Z": "z", "J": "j", "L": "l"}
FG = {
    "I": curses.COLOR_CYAN,
    "O": curses.COLOR_YELLOW,
    "T": curses.COLOR_MAGENTA,
    "S": curses.COLOR_GREEN,
    "Z": curses.COLOR_RED,
    "J": curses.COLOR_BLUE,
    "L": curses.COLOR_WHITE,
}


class Piece:
    __slots__ = ("kind", "m", "x", "y")

    def __init__(self, kind, m, x, y):
        self.kind, self.m, self.x, self.y = kind, m, x, y

    def cells(self):
        for r, row in enumerate(self.m):
            for c, v in enumerate(row):
                if v:
                    yield self.y + r, self.x + c

    def rotate(self, d):
        m = self.m
        rows, cols = len(m), len(m[0])
        if d > 0:  # clockwise
            nm = [[0] * rows for _ in range(cols)]
            for r in range(rows):
                for c in range(cols):
                    nm[c][rows - 1 - r] = m[r][c]
        else:      # counter-clockwise
            nm = [[0] * cols for _ in range(rows)]
            for r in range(rows):
                for c in range(cols):
                    nm[cols - 1 - c][c] = m[r][c]
        return nm


class Tetris:
    """Pure game logic (curses-free, so it can be unit-tested)."""

    def __init__(self):
        self.grid = [[None] * COLS for _ in range(ROWS)]
        self.bag = []
        self.score = 0
        self.level = 1
        self.lines = 0
        self.hold_kind = None
        self.can_hold = True
        self.over = False
        self.grav_t = 0.0
        self.lock_t = 0.0
        self.next_kind = self._pull()
        self.piece = None
        self.spawn()

    def _pull(self):
        if not self.bag:
            self.bag = list(SHAPES)
            random.shuffle(self.bag)
        return self.bag.pop()

    @property
    def fall_delay(self):
        return max(0.05, 0.7 * (0.82 ** (self.level - 1)))

    def _fits(self, m, x, y):
        for r, row in enumerate(m):
            for c, v in enumerate(row):
                if not v:
                    continue
                ax, ay = x + c, y + r
                if ax < 0 or ax >= COLS or ay >= ROWS:
                    return False
                if ay >= 0 and self.grid[ay][ax] is not None:
                    return False
        return True

    def spawn(self, kind=None):
        kind = kind or self.next_kind
        self.next_kind = self._pull()
        m = [row[:] for row in SHAPES[kind]]
        x = (COLS - len(m[0])) // 2
        y = -1 if kind == "I" else 0
        p = Piece(kind, m, x, y)
        self.can_hold = True
        self.grav_t = 0.0
        self.lock_t = 0.0
        self.piece = p
        if not self._fits(m, x, y):
            self.over = True

    def try_move(self, dx):
        p = self.piece
        if self.over or p is None:
            return False
        if self._fits(p.m, p.x + dx, p.y):
            p.x += dx
            self.lock_t = 0.0
            return True
        return False

    def try_rotate(self, d):
        p = self.piece
        if self.over or p is None:
            return False
        nm = p.rotate(d)
        for dx in (0, -1, 1, -2, 2):  # simple wall kick
            if self._fits(nm, p.x + dx, p.y):
                p.m, p.x = nm, p.x + dx
                self.lock_t = 0.0
                return True
        return False

    def _can_down(self):
        p = self.piece
        return self._fits(p.m, p.x, p.y + 1)

    def soft_drop(self):
        if self.over or not self._can_down():
            return
        self.piece.y += 1
        self.grav_t = 0.0
        self.lock_t = 0.0
        self.score += 1

    def hard_drop(self):
        if self.over:
            return
        d = 0
        while self._can_down():
            self.piece.y += 1
            d += 1
        self.score += 2 * d
        self._lock()

    def ghost_y(self):
        p = self.piece
        gy = p.y
        while self._fits(p.m, p.x, gy + 1):
            gy += 1
        return gy

    def hold(self):
        if self.over or not self.can_hold:
            return
        cur = self.piece.kind
        if self.hold_kind is None:
            self.hold_kind = cur
            self.spawn()
        else:
            kh = self.hold_kind
            self.hold_kind = cur
            self.spawn(kind=kh)
        self.can_hold = False

    def update(self, dt):
        if self.over:
            return
        if self._can_down():
            self.lock_t = 0.0
            self.grav_t += dt
            if self.grav_t >= self.fall_delay:
                self.grav_t = 0.0
                self.piece.y += 1
        else:
            self.lock_t += dt
            if self.lock_t >= LOCK_DELAY:
                self._lock()

    def _lock(self):
        p = self.piece
        top_out = False
        for r, c in p.cells():
            if r < 0:
                top_out = True
                continue
            self.grid[r][c] = p.kind
        self.piece = None
        if top_out:
            self.over = True
            return
        kept = [row for row in self.grid if any(cell is None for cell in row)]
        n = ROWS - len(kept)
        if n:
            self.score += LINE_SCORE[n] * self.level
            self.lines += n
            self.level = self.lines // 10 + 1
            while len(kept) < ROWS:
                kept.insert(0, [None] * COLS)
            self.grid = kept
        self.spawn()


def selftest():
    random.seed(42)
    g = Tetris()
    acts = (lambda: g.try_move(-1), lambda: g.try_move(1),
            lambda: g.try_rotate(1), lambda: g.try_rotate(-1),
            lambda: g.hold())
    games = 1
    drops = 0
    while drops < 500:
        if g.over:
            g = Tetris()
            games += 1
            continue
        random.choice(acts)()
        g.hard_drop()
        drops += 1
    print(f"selftest ok: games={games} score={g.score} "
          f"lines={g.lines} level={g.level}")


# ---------------------------------------------------------------- curses UI

HAS_COLOR = False
PAIR_OF = {}


def _init_colors():
    global HAS_COLOR
    if not curses.has_colors():
        return
    curses.start_color()
    try:
        curses.use_default_colors()
    except curses.error:
        pass
    for i, (k, col) in enumerate(FG.items(), start=1):
        curses.init_pair(i, col, -1)
        PAIR_OF[k] = curses.color_pair(i)
    HAS_COLOR = True


def put(win, y, x, text, attr=0):
    h, w = win.getmaxyx()
    if 0 <= y < h and 0 <= x < w:
        try:
            win.addstr(y, x, text, attr)
        except curses.error:
            pass


def trimmed(m):
    rows = [i for i, row in enumerate(m) if any(row)]
    cols = [j for j in range(len(m[0])) if any(m[i][j] for i in range(len(m)))]
    return [[m[i][j] for j in cols] for i in rows]


def draw(stdscr, g, paused):
    stdscr.erase()
    h, w = stdscr.getmaxyx()
    MIN_H, MIN_W = ROWS + 3, 34
    if h < MIN_H or w < MIN_W:
        put(stdscr, 0, 0, f"Terminal too small: need at least {MIN_W}x{MIN_H}")
        put(stdscr, 1, 0, "press q to quit")
        stdscr.refresh()
        return

    bx, by = 1, 1
    put(stdscr, by, bx, "#" * (COLS + 2))

    occ = {}
    if g.piece and not g.over:
        m, kind = g.piece.m, g.piece.kind
        gy = g.ghost_y()
        for r, row in enumerate(m):
            for c, v in enumerate(row):
                if v:
                    occ[gy + r, g.piece.x + c] = (kind, True)    # ghost
                    occ[g.piece.y + r, g.piece.x + c] = (kind, False)

    for r in range(ROWS):
        put(stdscr, by + 1 + r, bx, "#")
        for c in range(COLS):
            ch, attr = " ", 0
            entry = occ.get((r, c))
            if entry is not None:
                k, ghost = entry
                ch = CHARS[k]
                attr = PAIR_OF.get(k, 0)
                if ghost:
                    if not HAS_COLOR:
                        ch = "."
                    attr |= curses.A_DIM
            put(stdscr, by + 1 + r, bx + 1 + c, ch, attr)
        put(stdscr, by + 1 + r, bx + 1 + COLS, "#")
    put(stdscr, by + 1 + ROWS, bx, "#" * (COLS + 2))

    # side panel
    px = bx + COLS + 3
    put(stdscr, by, px, "TETRIS", curses.A_BOLD)
    y = by + 2
    put(stdscr, y, px, "NEXT")
    for i, row in enumerate(trimmed(SHAPES[g.next_kind])):
        for j, v in enumerate(row):
            if v:
                put(stdscr, y + 1 + i, px + j, CHARS[g.next_kind],
                    PAIR_OF.get(g.next_kind, 0))
    y += 5
    put(stdscr, y, px, "HOLD")
    if g.hold_kind:
        attr = PAIR_OF.get(g.hold_kind, 0)
        if not g.can_hold:
            attr |= curses.A_DIM
        for i, row in enumerate(trimmed(SHAPES[g.hold_kind])):
            for j, v in enumerate(row):
                if v:
                    put(stdscr, y + 1 + i, px + j, CHARS[g.hold_kind], attr)
    y += 5
    put(stdscr, y, px, f"SCORE {g.score}")
    put(stdscr, y + 1, px, f"LEVEL {g.level}")
    put(stdscr, y + 2, px, f"LINES {g.lines}")
    y += 4
    for t in ("<- ->   move",
              "up / x  rotate cw",
              "z       rotate ccw",
              "down    soft drop",
              "space   hard drop",
              "h       hold",
              "p       pause   q quit"):
        put(stdscr, y, px, t)
        y += 1

    if g.over:
        msgs = ["GAME OVER", f"Score {g.score}", "", "r restart   q quit"]
        oy = by + ROWS // 2 - 2
        for i, m in enumerate(msgs):
            put(stdscr, oy + i, bx + 1, m, curses.A_BOLD)
    elif paused:
        put(stdscr, by + ROWS // 2, bx + 1, "PAUSED", curses.A_BOLD)
    stdscr.refresh()


def run(stdscr):
    curses.curs_set(0)
    stdscr.keypad(True)
    stdscr.nodelay(True)
    _init_colors()
    g = Tetris()
    paused = False
    last = time.monotonic()
    while True:
        now = time.monotonic()
        dt = min(now - last, 0.25)
        last = now

        quit = False
        while True:
            k = stdscr.getch()
            if k == -1:
                break
            if k in (ord("q"), ord("Q"), 27):
                quit = True
                break
            if g.over:
                if k in (ord("r"), ord("R")):
                    g, paused = Tetris(), False
                continue
            if k in (ord("p"), ord("P")):
                paused = not paused
                continue
            if paused:
                continue
            if k == curses.KEY_LEFT:
                g.try_move(-1)
            elif k == curses.KEY_RIGHT:
                g.try_move(1)
            elif k == curses.KEY_DOWN:
                g.soft_drop()
            elif k in (curses.KEY_UP, ord("x"), ord("X")):
                g.try_rotate(1)
            elif k in (ord("z"), ord("Z")):
                g.try_rotate(-1)
            elif k == curses.KEY_SPACE:
                g.hard_drop()
            elif k in (ord("h"), ord("H")):
                g.hold()
        if quit:
            return
        if not paused and not g.over:
            g.update(dt)
        draw(stdscr, g, paused)
        time.sleep(TICK)


def main():
    if "--test" in sys.argv:
        selftest()
        return
    try:
        curses.wrapper(run)
    except KeyboardInterrupt:
        pass
    print("Thanks for playing!")


if __name__ == "__main__":
    main()
