import sys
for char in iter(lambda: sys.stdin.read(1), b''):
    sys.stdout.write(char)
    sys.stdout.flush()