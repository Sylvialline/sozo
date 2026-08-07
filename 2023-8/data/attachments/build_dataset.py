from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FILES = {
    # (1) inequality-only cases
    "data1a.txt": "31,0,9,7,3,5,66,100,999,7,1,950,31,10,20,42,0,940,66,500,550",
    "data1b.txt": "1,0,999,2,0,999,3,100,200,4,20,999,3,10,900,88,400,401",
    "data1c.txt": "999,0,999,0,123,987,500,0,865,250,10,875,999,450,451",

    # (2) program-only cases
    "data2a.txt": "11,3,7,11,11,7,3,11,7,3,11,9,7,11,3,7,11,3,7,2",
    "data2b.txt": "999,1,2,999,999,3,4,999,999,5,6,999,999,7,8,999",
    "data2c.txt": "0,1,500,0,999,500,0,2,500,3,999,4,0,5,500,6,999,7,123,0,321,500,777,999",

    # (3) final-value ranges: program a1/b1/c1 + inequalities a2/b2/c2
    "data3a1.txt": "31,2,41,31,2,3,51,2,31,51",
    "data3a2.txt": "2,5,9,3,1,3,31,100,200,999,0,999",
    "data3b1.txt": "31,60,60,70,41,31,80,60",
    "data3b2.txt": "70,700,800,41,0,999,88,12,34",
    "data3c1.txt": "41,31,51,41,31,4,41,31",
    "data3c2.txt": "31,100,110,4,0,100,4,10,20,31,100,110",

    # (4) ranges during execution
    "data4a1.txt": "31,2,41,31,31,3,51,31,31,4,41,31",
    "data4a2.txt": "2,5,9,3,1,3,4,20,30,31,0,999",
    "data4b1.txt": "41,31,31,2,2,51",
    "data4b2.txt": "31,400,450,2,1,2,51,700,710",
    "data4c1.txt": "31,99,41,31,51,88,31,51,41,31,51,77",
    "data4c2.txt": "88,900,950,77,10,20,99,500,600,99,0,100",

    # (5) variables whose runtime range violates their own inequality
    "data5a1.txt": "10,3,10,7,11,10",
    "data5a2.txt": "3,5,9,7,1,3,10,1,9,11,1,3",
    "data5b1.txt": "50,41,31,2,31,3,41,31,50,31",
    "data5b2.txt": "41,20,35,31,0,50,2,10,20,3,80,90,50,0,100",
    "data5c1.txt": "5,6,5,7,8,5,9,100,100,101",
    "data5c2.txt": "5,0,999,6,35,36,7,39,45,5,30,40,8,0,100,9,10,90,101,900,999",

    # (6) inconsistent assignments under declared intervals
    "data6a1.txt": "10,3,10,7,11,10",
    "data6a2.txt": "3,5,9,7,1,3,10,1,9,11,1,3",
    "data6b1.txt": "1,2,3,2,4,5,1,5,3,2,9,5",
    "data6b2.txt": "1,0,100,2,20,30,3,0,10,4,0,999,5,500,600",
    "data6c1.txt": "10,11,11,12,12,13,13,99,99,10",
    "data6c2.txt": "10,0,10,11,2,8,12,3,7,13,5,5",

    # (7) define missing inequalities to make all assignments consistent
    "data7a1.txt": "1,2,2,3,3,4,5,4,6,7,7,8",
    "data7a2.txt": "1,0,100,4,20,30,6,40,60,8,45,50",
    "data7b1.txt": "20,10,10,11,11,12,12,11,12,13,30,31",
    "data7b2.txt": "20,100,200,13,120,130,900,0,999",
    "data7c1.txt": "1,2,2,3",
    "data7c2.txt": "1,0,10,3,20,30",
}

for name, text in FILES.items():
    (ROOT / name).write_text(text + "\n", encoding="utf-8")

print(f"wrote {len(FILES)} data files to {ROOT}")
