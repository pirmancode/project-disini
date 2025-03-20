import time
import random
import sys
import itertools
import os
from tqdm import tqdm

# Warna terminal
GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RESET = "\033[0m"

# Simulasi loading dengan efek mengetik
def slow_print(text, delay=0.05):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

# Animasi loading
def loading_animation(text, duration=3):
    spinner = itertools.cycle(["-", "\\", "|", "/"])
    start_time = time.time()
    while time.time() - start_time < duration:
        sys.stdout.write(f"\r{text} {next(spinner)} ")
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write("\r" + " " * (len(text) + 2) + "\r")

# Simulasi booting
def boot_sequence():
    os.system("clear" if os.name == "posix" else "cls")
    slow_print(f"{GREEN}Menginisialisasi alat hacking...\n{RESET}")
    time.sleep(1)
    loading_animation("Membobol firewall", 3)
    loading_animation("Mendekripsi password", 3)
    slow_print(f"{GREEN}Akses diberikan!{RESET}\n")

# Simulasi mengambil data akun dengan alamat di Indonesia
def retrieve_fake_accounts():
    slow_print(f"{CYAN}Mengambil data pengguna...{RESET}")
    for _ in tqdm(range(30), desc="Mengambil data", ascii=True):
        time.sleep(0.1)

    fake_accounts = [
        {
            "email": "rendi.firman@gmail.com", 
            "password": "kopiluwak123", 
            "ip": "192.168.1.23", 
            "address": "Jl. Sudirman No. 45, Jakarta", 
            "last_location": "Bandung, Jawa Barat"
        },
        {
            "email": "siti_amalia@yahoo.com", 
            "password": "batikmerah", 
            "ip": "10.0.0.45", 
            "address": "Jl. Diponegoro No. 78, Surabaya", 
            "last_location": "Malang, Jawa Timur"
        },
        {
            "email": "agus_pratama@protonmail.com", 
            "password": "manggaManis!", 
            "ip": "172.16.0.12", 
            "address": "Jl. Merdeka No. 12, Yogyakarta", 
            "last_location": "Solo, Jawa Tengah"
        },
        {
            "email": "kartika_dewi@example.com", 
            "password": "nasigoreng99", 
            "ip": "192.168.43.101", 
            "address": "Jl. Asia Afrika No. 33, Bandung", 
            "last_location": "Cirebon, Jawa Barat"
        },
        {
            "email": "h4ck3r@darkweb.com", 
            "password": "satepadang", 
            "ip": "127.0.0.1", 
            "address": "Tidak Diketahui", 
            "last_location": "Dark Web"
        },
    ]

    slow_print(f"{GREEN}Ditemukan {len(fake_accounts)} akun:{RESET}")
    for account in fake_accounts:
        slow_print(f"  📧 Email: {CYAN}{account['email']}{RESET}")
        slow_print(f"  🔑 Password: {RED}{account['password']}{RESET}")
        slow_print(f"  🌍 IP Address: {CYAN}{account['ip']}{RESET}")
        slow_print(f"  🏠 Alamat: {YELLOW}{account['address']}{RESET}")
        slow_print(f"  📍 Terakhir Dilihat: {YELLOW}{account['last_location']}{RESET}\n")
        time.sleep(1)

# Simulasi eksploitasi
def exploit_vulnerabilities():
    slow_print(f"{CYAN}Mengeksploitasi kelemahan sistem...{RESET}")
    for _ in tqdm(range(50), desc="Eksploitasi", ascii=True):
        time.sleep(0.05)

    slow_print(f"{RED}Akses root diperoleh!{RESET}")
    slow_print(f"{GREEN}Sistem berhasil dikompromikan.{RESET}")

# Main function
def main():
    boot_sequence()
    retrieve_fake_accounts()
    exploit_vulnerabilities()
    slow_print(f"{GREEN}Misi selesai! Keluar dari sistem...{RESET}")

if __name__ == "__main__":
    main()
