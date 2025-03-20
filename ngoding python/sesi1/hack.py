import random
import sys
import time
import shutil

GREEN = "\033[92m"
RESET = "\033[0m"

def hacker_matrix():
    columns = shutil.get_terminal_size().columns
    chars = "0123456789ABCDEF#$&@"
    
    while True:
        line = "".join(random.choice(chars) for _ in range(columns))
        sys.stdout.write(GREEN + line + RESET + "\n")
        sys.stdout.flush()
        time.sleep(0.05)

try:
    hacker_matrix()
except KeyboardInterrupt:
    print("\n[!] Exiting...")
