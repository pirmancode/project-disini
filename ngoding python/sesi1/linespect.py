import os
import re
import sys
import time
import itertools

# Warna untuk terminal
GREEN = "\033[92m"
RESET = "\033[0m"

# Kata kunci yang dianggap mencurigakan
SUSPICIOUS_KEYWORDS = [
    r"exec\(", r"eval\(", r"subprocess\.", r"os\.system\(", r"socket\.",
    r"open\(", r"import\s+base64", r"pickle\.loads\(", r"shutil\.rmtree\("
]

def loading_animation(text="Scanning"):
    """ Efek loading ala hacker """
    for _ in range(10):
        for char in itertools.cycle(["|", "/", "-", "\\"]):
            sys.stdout.write(f"\r{GREEN}{text} {char}{RESET}")
            sys.stdout.flush()
            time.sleep(0.1)
    sys.stdout.write("\r" + " " * 50 + "\r")  # Hapus loading

def inspect_file(filename):
    """ Menganalisis file Python dan mencari kode mencurigakan """
    if not os.path.exists(filename):
        print(f"{GREEN}[ERROR] File not found: {filename}{RESET}")
        return

    print(f"{GREEN}[INFO] Inspecting {filename}...{RESET}")
    loading_animation()

    with open(filename, "r", encoding="utf-8") as file:
        lines = file.readlines()

    suspicious_lines = []
    for i, line in enumerate(lines, start=1):
        for pattern in SUSPICIOUS_KEYWORDS:
            if re.search(pattern, line):
                suspicious_lines.append((i, line.strip()))

    if suspicious_lines:
        print(f"{GREEN}[ALERT] Suspicious code detected!{RESET}")
        for line_no, code in suspicious_lines:
            print(f"{GREEN}Line {line_no}: {code}{RESET}")
    else:
        print(f"{GREEN}[SAFE] No suspicious code found.{RESET}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"{GREEN}Usage: python {sys.argv[0]} <filename>{RESET}")
        sys.exit(1)
    
    inspect_file(sys.argv[1])
