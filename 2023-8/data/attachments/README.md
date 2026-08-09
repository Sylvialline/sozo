# 2023-8 Programming generated dataset v2

Scale convention
- a: hand-checkable small input.
- b: large input with strong corner-case bias; major program files use 250,000 assignments.
- c: performance/stress input; major program files use 1,000,000 assignments.
- Large inequality companions use 20,000 triples for b and 100,000 triples for c.

Covered traps
- rightmost inequality is the only effective one;
- duplicate and overwritten inequalities;
- exact ties in (1) and (2);
- missing inequalities and the [0,100] default;
- first RHS use / lazy initialization;
- self assignments, repeated assignments, long chains, branching and cycles;
- variables appearing on only one side;
- repeated problematic assignment statements in (6), which must be reported once;
- (7b): large feasible constraint-propagation case;
- (7c): 1,000,000 assignments with a contradiction visible only through a long transitive path.

Reference answers are computed by reference_solver.py.
