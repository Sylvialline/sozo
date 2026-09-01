# Standard Answers

## Q1

```text
24
```

There are 6 choices for the original face placed at U. After fixing it, there are 4 choices for the adjacent face placed at R. Hence the number of orientations is $6\times4=24$.

## Q2

```text
p4 p1 b4 w2
p3 p2 b3 w3
w1 g2 r1 r2
w4 g3 r4 r3
y1 y2 b1 b2
g1 g4 y4 y3
```

Circle the following three facelets of the U-R-F invariant cubicle:

```text
r3 y2 b1
```

## Q3

### Q3-1

```text
UL: UB UB
FU: FR UB
RU: FR UB FR
BU: FR UB FR FR
LD: FR UB UB UB FR
```

### Q3-2

Each line contains a replacement followed by its inverse.

```text
UF UB
UL UL
UB UF
RU RU
RF FU
RD LU
RB BU
FU RF
FR BR
FD LB
FL FL
DR DR
DF DF
DL DL
DB DB
LU RD
LF BD
LD LD
LB FD
BU RB
BR FR
BD LF
BL BL
```

## Q4

### Q4-1

Store the 24 facelets in a one-dimensional array, in the face order U, R, F, D, L, B and row-major order within each 2 x 2 face. Represent each basic rotation by a permutation p of 0,...,23, where the facelet at old position i moves to position p[i]. Apply a move by writing new[p[i]] = old[i] for every i. Obtain X2 and X3 by applying the quarter-turn permutation X once more or twice more.

### Q4-2

#### U1

```text
p p b w
p p b w
w g r r
w g r r
y y b b
g g y y
```

#### R1

```text
p g w w
p g w w
r r b b
g g r r
y y b p
y y b p
```

#### F1

```text
p p w w
y y p p
g g w r
g g w r
r y b b
r y b b
```

### Q4-3

#### Sequence 1: `R1 U3 F2`

```text
g g r w
b r y b
g y p b
r y p r
g y b p
w p w w
```

#### Sequence 2: `U1 R2 F3 U2`

```text
b w r b
r p g r
y g y p
g w g r
p y b w
w p y b
```

#### Sequence 3: `F1 R3 U2 F2 R1`

```text
b g r r
g r w p
b g w g
y b p r
y y b y
p w p w
```

#### Sequence 4: `U3 F1 R2 U1 F3 R1`

```text
y w p w
y g w p
r b y b
p w b r
r y b p
g g r g
```

## Q5

Each line gives one shortest solution. Rotations on the same line are applied from left to right.

```text
data1.txt: U2 R3
data2.txt: U3 F2 U1
data3.txt: U1 F1 U1 F3
data4.txt: U3 R1 F1 R1 F3
data5.txt: R1 U2 R3 F2 U3 F3
```
