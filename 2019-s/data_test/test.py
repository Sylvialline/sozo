from pathlib import Path

b = b"\x41\x42\x43\x44\x45\x46\x47\x00\x06\x05\x48"
Path("test2.bin").write_bytes(b)