from collections import Counter

def analyze_data(data):
    # Rata-rata
    mean = sum(data) / len(data)
    
    # Median
    sorted_data = sorted(data)
    n = len(sorted_data)
    if n % 2 == 0:
        median = (sorted_data[n // 2 - 1] + sorted_data[n // 2]) / 2
    else:
        median = sorted_data[n // 2]
    
    # Modus
    data_counts = Counter(data)
    max_count = max(data_counts.values())
    mode = [key for key, count in data_counts.items() if count == max_count]
    
    # Nilai maksimum dan minimum
    maximum = max(data)
    minimum = min(data)
    
    # Hasil analisis
    return {
        "Mean (Rata-rata)": mean,
        "Median": median,
        "Mode (Modus)": mode,
        "Maximum": maximum,
        "Minimum": minimum
    }

# Contoh penggunaan
if __name__ == "__main__":
    data = [12, 15, 12, 10, 20, 20, 20, 8, 15, 12]
    print("Data:", data)
    
    analysis_result = analyze_data(data)
    print("\nHasil Analisis:")
    for key, value in analysis_result.items():
        print(f"{key}: {value}")
