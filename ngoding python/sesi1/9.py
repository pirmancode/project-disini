import math
# Data sampel (berat, tekstur) dan label (1: Apel, 0: Jeruk)
data = [
    (150, 'halus', 1),   # Apel
    (170, 'halus', 1),   # Apel
    (140, 'kasar', 0),   # Jeruk
    (130, 'kasar', 0)    # Jeruk
]

# Fungsi untuk menghitung jarak Euclidean antara dua titik
def euclidean_distance(point1, point2):
    weight_diff = point1[0] - point2[0]
    texture_diff = 0 if point1[1] == point2[1] else 1  # 0 jika teksturnya sama, 1 jika berbeda
    return math.sqrt(weight_diff ** 2 + texture_diff ** 2)

# Fungsi KNN
def knn_classify(new_data, k=3):
    # Menghitung jarak antara data baru dan semua data yang ada
    distances = []
    for d in data:
        distance = euclidean_distance(new_data, d)
        distances.append((distance, d[2]))
    
    # Urutkan berdasarkan jarak terpendek
    distances.sort(key=lambda x: x[0])
    
    # Ambil k tetangga terdekat
    neighbors = distances[:k]
    
    # Voting mayoritas
    votes = {0: 0, 1: 0}
    for neighbor in neighbors:
        votes[neighbor[1]] += 1
    
    # Mengembalikan hasil klasifikasi (kelas dengan suara terbanyak)
    return max(votes, key=votes.get)

# Data baru yang akan diklasifikasikan (berat, tekstur)
new_fruit = (160, 'halus')

# Mengklasifikasikan data baru
result = knn_classify(new_fruit)
label = 'Apel' if result == 1 else 'Jeruk'

print(f'Buah baru ini diprediksi sebagai: {label}')
