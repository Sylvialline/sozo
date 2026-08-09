from pathlib import Path
import reference_solver as s

ROOT = Path(__file__).resolve().parents[1]

# Structural parse checks.
for c in 'abc':
    s.parse_inequalities(ROOT / f'data1{c}.txt')
    s.parse_program(ROOT / f'data2{c}.txt')
for q in range(3, 8):
    for c in 'abc':
        s.parse_program(ROOT / f'data{q}{c}1.txt')
        s.parse_inequalities(ROOT / f'data{q}{c}2.txt')

# Expected answers, frozen here as a second guard against accidental edits.
assert s.q1(ROOT/'data1a.txt') == [(7, 1, 950)]
assert s.q1(ROOT/'data1b.txt') == [(1, 0, 999), (2, 0, 999)]
assert s.q1(ROOT/'data1c.txt') == [(250, 10, 875), (500, 0, 865)]
assert s.q2(ROOT/'data2a.txt') == [7, 11]
assert s.q2(ROOT/'data2b.txt') == [999]
assert s.q2(ROOT/'data2c.txt') == [0, 500, 999]
assert s.q3(ROOT/'data3a1.txt', ROOT/'data3a2.txt') == {31:(1,3),41:(5,9),51:(1,3)}
assert s.q3(ROOT/'data3b1.txt', ROOT/'data3b2.txt') == {31:(0,100),41:(0,100),51:None}
assert s.q3(ROOT/'data3c1.txt', ROOT/'data3c2.txt') == {31:(10,20),41:(10,20),51:(100,110)}
assert s.q4(ROOT/'data4a1.txt', ROOT/'data4a2.txt') == {31:(1,30),41:(5,30),51:(1,3)}
assert s.q4(ROOT/'data4b1.txt', ROOT/'data4b2.txt') == {31:(1,450),41:(400,450),51:(700,710)}
assert s.q4(ROOT/'data4c1.txt', ROOT/'data4c2.txt') == {31:(0,950),41:(0,950),51:(10,950)}
assert s.q5(ROOT/'data5a1.txt', ROOT/'data5a2.txt') == []
assert s.q5(ROOT/'data5b1.txt', ROOT/'data5b2.txt') == [31,41]
assert s.q5(ROOT/'data5c1.txt', ROOT/'data5c2.txt') == [5,9]
assert s.q6(ROOT/'data6a1.txt', ROOT/'data6a2.txt') == [(11,10)]
assert s.q6(ROOT/'data6b1.txt', ROOT/'data6b2.txt') == [(3,2),(1,5)]
assert s.q6(ROOT/'data6c1.txt', ROOT/'data6c2.txt') == []
assert s.q7(ROOT/'data7a1.txt', ROOT/'data7a2.txt') == {2:(0,100),3:(0,100),5:(0,999),7:(40,60)}
assert s.q7(ROOT/'data7b1.txt', ROOT/'data7b2.txt') == {10:(100,200),11:(100,200),12:(100,200),30:(0,999),31:(0,999)}
assert s.q7(ROOT/'data7c1.txt', ROOT/'data7c2.txt') is None

print('All dataset files and reference answers validated successfully.')
