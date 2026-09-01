# Standard Answers

Each block is the exact content of the corresponding output file.

## Q1 - `q1.out`

```text
3
5
4
645
```

The lines are maximum thickness, cluster count, maximum cluster size, and maximum cluster area.

## Q2 - `q2.out`

```text
1456830
```

## Q3 - `q3.out`

```text
400
3
400
40000
```

The lines have the same order as Q1.

## Q4 - `q4.out`

```text
3186
209
```

The first line is the number of placements that raise the maximum thickness by one. The second line is the number of placements attaining the largest possible maximum cluster area. That largest area is `80050`.

## Q5 - `q5.out`

```text
137
```

The reference solver uses an x-coordinate sweep and a range-add/range-maximum segment tree over compressed y-intervals, requiring $O(n\log n)$ time and $O(n)$ space.
