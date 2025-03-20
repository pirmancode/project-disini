import matplotlib.pyplot as plt

# Data sampel (x: suhu, y: penjualan es krim)
x = [30, 35, 40, 45, 50, 55, 60]
y = [100, 150, 200, 220, 240, 300, 350]

# Menghitung rata-rata
def mean(values):
    return sum(values) / len(values)

# Fungsi untuk menghitung m (slope) dan c (intercept)
def linear_regression(x, y):
    n = len(x)
    mean_x = mean(x)
    mean_y = mean(y)
    
    # Menghitung numerator dan denominator untuk mendapatkan m
    numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
    denominator = sum((x[i] - mean_x) ** 2 for i in range(n))
    
    m = numerator / denominator
    c = mean_y - m * mean_x
    
    return m, c

# Memanggil fungsi regresi linier
m, c = linear_regression(x, y)

# Menampilkan persamaan regresi
print(f"Persamaan regresi: y = {m:.2f}x + {c:.2f}")

# Membuat prediksi berdasarkan model regresi
y_pred = [m * xi + c for xi in x]

# Plot data asli dan garis regresi
plt.scatter(x, y, color='blue', label='Data Aktual')
plt.plot(x, y_pred, color='red', label='Garis Regresi')
plt.xlabel('Suhu (°C)')
plt.ylabel('Penjualan Es Krim')
plt.title('Regresi Linier Sederhana')
plt.legend()
plt.show()
