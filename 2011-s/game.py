import curses
from curses import window
from random import randint
from time import monotonic

WIDTH = 9
HEIGHT = 15
MAX_BULLETS = 2
FPS = 2
POLL_MS = 10

class State:

    def __init__(self, screen: window) -> None:
        self.screen = screen
        self.origin = (0, WIDTH // 2)
        self.gun = (HEIGHT - 1, 5)
        self.target = None # (y, x, d=1/-1)
        self.bullets = []
        self.score = 0
        self.lives = 5
        self.remain = MAX_BULLETS

    def draw(self):
        self.screen.erase()
        
        self.screen.addstr(0, 0, "-" * WIDTH)
        self.screen.addstr(HEIGHT - 1, 0, "." * WIDTH)
        for i in range(HEIGHT):
            self.screen.addch(i, 0, '|')
            self.screen.addch(i, WIDTH - 1, '|')

        self.screen.addch(self.gun[0], self.gun[1], 'X')
        self.screen.addch(self.origin[0], self.origin[1], 'V')

        if self.target:
            target_y, target_x, _ = self.target
            self.screen.addch(target_y, target_x, 'O')

        for bullet in self.bullets:
            self.screen.addch(bullet[0], bullet[1], 'e')

        self.screen.addstr(HEIGHT, 0, f"Score: {self.score}, Lives: {self.lives}, Bullets Remain: {self.remain}")

        self.screen.refresh()

    def reset_target(self):
        x = randint(0, WIDTH - 1)
        self.origin = (0, x)
        self.target = (0, x, 1)
        self.remain = MAX_BULLETS

    def update(self):
        if not self.target:
            self.reset_target()
        tar_y, tar_x, d = self.target
        if tar_x + d >= WIDTH or tar_x + d < 0:
            d = -d
        self.target = (tar_y + 1, tar_x + d, d)
        if self.target[0] == HEIGHT - 1:
            self.target = None
            self.lives -= 1

        bullets = []
        for y, x in self.bullets:
            if y == 1:
                continue
            b = (y - 1, x)
            if self.target and b == self.target[:-1]:
                self.target = None
                self.score += 1
            else:
                bullets.append(b)

        self.bullets = bullets

    def fire(self):
        if self.remain:
            self.bullets.append(self.gun)
            self.remain -= 1

    def move(self, d):
        y, x = self.gun
        if 0 <= x + d < WIDTH:
           self.gun = (y, x + d)

VALID_KEYS = (ord('q'), ord('i'), ord('j'), ord('k'), ord('l'))

def main_sync(screen: window):
    curses.curs_set(0)
    state = State(screen)
    
    state.draw()
    while True:
        while (key := screen.getch()) not in VALID_KEYS:
            pass
        if key == ord('q'):
            break
        elif key == ord('i'):
            state.fire()
        elif key == ord('j'):
            state.move(-1)
        elif key == ord('l'):
            state.move(1)
        state.update()
        state.draw()
        if state.lives == 0:
            print("Game over!")
            break

    print(f"Final score: {state.score}")

def main_async(screen: window):
    curses.curs_set(0)
    state = State(screen)
    screen.timeout(POLL_MS)
    
    state.draw()
    deadline = monotonic() + 1 / FPS
    while True:
        key = screen.getch()
        if key == ord('q'):
            break
        elif key == ord('i'):
            state.fire()
            state.draw()
        elif key == ord('j'):
            state.move(-1)
            state.draw()
        elif key == ord('l'):
            state.move(1)
            state.draw()

        if monotonic() >= deadline:
            state.update()
            state.draw()
            deadline += 1 / FPS

        if state.lives == 0:
            print("Game over!")
            break

    print(f"Final score: {state.score}")

curses.wrapper(main_async)