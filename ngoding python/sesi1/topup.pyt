class TopUp:
    def __init__(self):
        self.topup_history = []

    def add_topup(self, amount, date):
        self.topup_history.append({'amount': amount, 'date': date})
        print(f"Top-up sebesar {amount} pada {date} berhasil ditambahkan.")

    def show_history(self):
        if not self.topup_history:
            print("Riwayat top-up kosong.")
            return
        
        print("Riwayat Top-Up:")
        for record in self.topup_history:
            print(f"Tanggal: {record['date']}, Jumlah: {record['amount']}")

def main():
    topup_manager = TopUp()
    
    while True:
        print("\nMenu:")
        print("1. Tambah Top-Up")
        print("2. Tampilkan Riwayat Top-Up")
        print("3. Keluar")
        
        choice = input("Pilih opsi (1/2/3): ")
        
        if choice == '1':
            amount = float(input("Masukkan jumlah top-up: "))
            date = input("Masukkan tanggal (YYYY-MM-DD): ")
            topup_manager.add_topup(amount, date)
        elif choice == '2':
            topup_manager.show_history()
        elif choice == '3':
            print("Keluar dari program.")
            break
        else:
            print("Opsi tidak valid. Silakan coba lagi.")

if __name__ == "__main__":
    main()