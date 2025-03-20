import time
import http.client
import json
import random

# Fungsi untuk mensimulasikan deteksi gerakan
def detect_motion():
    # Simulasi deteksi gerakan setiap beberapa detik
    return random.choice([True, False])

# Fungsi untuk mengirim data gerakan ke server melalui HTTP POST
def send_motion_detected():
    # Pengaturan koneksi ke server
    conn = http.client.HTTPConnection("localhost", 8000)
    
    # Data yang akan dikirim dalam format JSON
    payload = json.dumps({"motion": True})
    
    # Header permintaan
    headers = {"Content-type": "application/json"}
    
    # Mengirim permintaan POST ke server
    conn.request("POST", "/motion", payload, headers)
    
    # Mendapatkan respons dari server
    response = conn.getresponse()
    print(response.status, response.reason)
    
    # Menutup koneksi
    conn.close()

# Fungsi utama untuk mendeteksi gerakan dan mengirimkan data
def main():
    print("Starting simulated motion detection...")
    try:
        while True:
            # Simulasi deteksi gerakan
            motion_detected = detect_motion()
            
            if motion_detected:
                print("Motion detected!")
                send_motion_detected()
                
            # Menunggu 1 detik sebelum pengecekan ulang
            time.sleep(1)
    except KeyboardInterrupt:
        print("Program stopped")

if __name__ == "__main__":
    main()
