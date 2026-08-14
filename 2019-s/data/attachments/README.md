# 2019-s generated data and reference answers

The local booklet is titled **2020 Summer Entrance Examination**. The repository
directory is named `2019-s` because the examination was held in summer 2019.
The booklet contains five questions about six-bit text encoding, a custom byte
compression format, substitution ciphers, and RSA-style encryption.

This package was reconstructed from the English statement in
`fy2019_s_program.pdf`. No existing solution, old answer file, or old test data
under `2019-s/` was read or used while producing it.

## Layout

Only the ten statement-named input files are placed at the root of `data/`:

```text
2019-s/data/
├─ data1.txt
├─ data2a.bin
├─ data2b.bin
├─ data2c.bin
├─ data3a.txt
├─ data3b.png
├─ data3c.txt
├─ data4.txt
├─ data4dict.txt
├─ data5.txt
└─ attachments/
   ├─ README.md
   ├─ answers.json
   ├─ answers.txt
   ├─ dataset_summary.json
   ├─ generate_data.py
   ├─ manifest.sha256.tsv
   ├─ reference_solver.py
   ├─ test_reference_solver.py
   └─ reference_outputs/
      ├─ data2a.txt
      ├─ data2b.tif
      ├─ data2c.txt
      ├─ data3a.bin
      ├─ data3b.bin
      └─ data3c.bin
```

The files under `reference_outputs/` are the restored files required by
question (2) and one canonical minimum-size compressed file for each input in
question (3). They are kept below `attachments/` so they cannot be confused
with exam inputs.

## Statement constraints represented by the data

The original statement does not give explicit upper bounds on file sizes. This
package therefore enforces the stated format and the conditions needed for each
answer to exist, without presenting generated size choices as official bounds.

1. `data1.txt` uses exactly the 64-symbol alphabet
   `A-Z`, `a-z`, `0-9`, `@`, `#`. Each symbol encodes one six-bit number, so the
   represented bit length is a multiple of six. The file contains enough bits
   to query inclusive positions 310 through 320, with the leftmost bit numbered
   zero.
2. Each `data2*.bin` is a valid stream of literals and three-byte commands
   `(0, p, d)`. `p` and `d` are unsigned bytes and satisfy
   `256 > p >= d >= 0`. A command with `d = 0` restores one zero byte; otherwise
   its source range is wholly inside the already restored prefix. The three
   restored outputs are UTF-8/ASCII text, a valid baseline RGB TIFF, and UTF-8
   text, respectively.
3. `data3a.txt`, `data3b.png`, and `data3c.txt` are arbitrary binary inputs to
   be compressed with exactly the decoder from question (2). `data3b.png` is a
   valid 48 by 36 RGB PNG. The reference compressor uses dynamic programming to
   minimize encoded byte length globally; it does not rely on a longest-match
   greedy choice.
4. The plaintext behind `data4.txt` contains only lower-case `a-z`, ASCII
   spaces, and periods, and ends in a period. A fixed one-to-one substitution is
   used. `data4dict.txt` is a space-separated exact set of all plaintext words.
   The generated instance has one substitution solution.
5. `data5.txt` contains whitespace-separated decimal ciphertext integers. The
   original byte length is a multiple of four, each four-byte value is read in
   big-endian order, and the restored bytes are valid UTF-8 text. The constants
   `e` and `n` are exactly those printed in the statement.

## Reference solution

`reference_solver.py` is standard-library-only and provides separate functions
for all five questions. Its question (3) compressor first computes every
position's longest legal non-overlapping match in `O(255*n)`, then uses dynamic
programming over all legal copy lengths. This proves the reported encoded size
is minimal for the specified format.

For question (4), the solver treats the encrypted representations of the space
and period as unknown and solves the bijective character constraints against
the supplied dictionary. For question (5), it uses

```text
p*q = n
e*d = (p-1)*(q-1)+1
```

to obtain the finite bound on `d`, recover `p`, `q`, and `d`, and decrypt every
four-byte chunk.

Run it from any working directory:

```powershell
python -B C:\Users\l50062268\Desktop\prog\2019-s\data\attachments\reference_solver.py
```

`answers.txt` is the concise human-readable answer sheet. `answers.json` also
records output filenames, sizes, and SHA-256 hashes. For question (3), different
minimum encodings can be equally correct; the answer is the minimum size plus a
round-trip-valid compressed file. The hashes identify this package's canonical
reference files, not the only acceptable byte representation.

## Reproduction and checks

Python 3.10 or newer is sufficient; there are no third-party dependencies.
From `attachments/`:

```powershell
python -B generate_data.py
python -B test_reference_solver.py
```

The generator uses the fixed seed `20190825`, rewrites only the named generated
inputs and answer artifacts, and regenerates `manifest.sha256.tsv`. The test
suite includes the statement examples, an independent decoder, exhaustive
minimum-size checks on hundreds of small inputs, full delivery round trips,
PNG structure checks, substitution consistency, RSA relations, and manifest
hashes. It does not read or run any pre-existing implementation in `2019-s/`.

`manifest.sha256.tsv` intentionally excludes itself. `dataset_summary.json`
records generated sizes, hashes, and the boundary features covered by each
question.
