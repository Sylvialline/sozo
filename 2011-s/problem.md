# 東京大学 情報理工学系研究科 創造情報学専攻

## 2011年度 夏季入試（2010年8月実施） プログラミング実技試験

## Problem

### Game description

A game board is represented by a rectangular grid consisting of four
segments: A is the upper horizontal edge, B is the left vertical edge,
C is the lower horizontal edge, and D is the right vertical edge. The
target moves on the board and the player controls a gun on segment C.

The reflective index of segments B and D is 1.0. The target rebounds
with the angle of reflection identical to the angle of incidence. When
the target reaches segment C, the target becomes lost and the score
remains unchanged.

The player controls the gun and fires by pressing the `i`, `j`, `k`, or
`l` key. Only one key is pressed at a time.

-   `i`: fire a bullet from the gun, then update the board.
-   `j`: move the gun one grid position left on segment C, then update
    the board. If already at the left-most position, do not move.
-   `k`: update the board without operating the gun.
-   `l`: move the gun one grid position right on segment C, then update
    the board. If already at the right-most position, do not move.

Other keys are ignored.

The board may be displayed either graphically or using characters.

Character representation:

-   Segment A: `-`
-   Segment B: `|`
-   Segment C: `.`
-   Segment D: `|`
-   Current launch point on segment A: `V`
-   Target: `O`
-   Gun: `X`
-   Bullet: `e`

## Target and bullet movement

Initially there is no target. When the board is updated and no target
exists, a new target is thrown from point V.

The target moves one vertical grid coordinate and one horizontal grid
coordinate at every board update.

When the player presses `i`, a bullet is fired from the gun. The bullet
moves upward one grid coordinate per board update.

If the bullet collides with the target:

-   both bullet and target disappear;
-   the score increases by one.

If the bullet reaches segment A without hitting the target, it is lost.

Two bullets can be fired for one target.

Game over occurs when the player fails to hit the target and the target
becomes lost on segment C five times. The program terminates after
displaying the score.

## Tasks

### (1)

Make a program that displays the board excluding bullets and targets.

### (2)

Make a program that throws a target from the center of segment A toward
the lower-right direction at a 45 degree angle, and moves it downward
every board update.

When the target reaches segment C, it becomes lost. When no target
exists, throw a new target from the center of segment A.

### (3)

Make a program that fires a bullet vertically upward from the gun at the
center of segment C by pressing `i`.

Move the bullet upward one grid coordinate every board update. When it
collides with the target, erase both and increase the score by one.

### (4)

Modify (3) so that the target is thrown from a randomly selected point
on segment A instead of always the center.

### (5)

Create a program where:

-   `j` and `l` move the gun on segment C.
-   `i` fires a bullet.

### (6)

The current program updates the board synchronously with key operations,
making the game inconvenient.

Modify it so that:

-   board updates occur periodically and independently of player
    operations;
-   key operations directly control gun movement and firing.

Describe the required modifications.

### (7)

Modify the program so that:

-   the board is updated approximately once every 0.5 seconds;
-   pressing `j` or `l` moves the gun one grid position;
-   pressing `i` fires a bullet;
-   these operations work independently from the timing of board
    updates.
