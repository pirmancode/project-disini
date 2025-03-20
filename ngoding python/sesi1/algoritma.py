
# Data sampel (x: suhu, y: penjualan es krim)
x = np.array([30, 35, 40, 45, 50, 55, 60])
y = np.array([100, 150, 200, 220, 240, 300, 350])

# Menentukan jumlah data
n = len(x)

# Menghitung rata-rata x dan y
mean_x = np.mean(x)
mean_y = np.mean(y)

# Menghitung parameter m (slope) dan c (intercept)
numerator = np.sum((x - mean_x) * (y - mean_y))
denominator = np.sum((x - mean_x) ** 2)
m = numerator / denominator
c = mean_y - m * mean_x

# Menampilkan persamaan regresi
print(f"Persamaan regresi: y = {m:.2f}x + {c:.2f}")

# Membuat prediksi berdasarkan model regresi
y_pred = m * x + c

# Plot data asli dan garis regresi
plt.scatter(x, y, color='blue', label='Data Aktual')
plt.plot(x, y_pred, color='red', label='Garis Regresi')
plt.xlabel('Suhu (°C)')
plt.ylabel('Penjualan Es Krim')
plt.title('Regresi Linier Sederhana')
plt.legend()
plt.show()
