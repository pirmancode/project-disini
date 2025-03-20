
import tkinter as tk
import math
import random

def draw_heart(canvas, t, width, height, color):
    x_center, y_center = width // 2, height // 2
    scale = 20

    x = 16 * (math.sin(t) ** 3)
    y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)

    x = x_center + scale * x
    y = y_center - scale * y

    canvas.create_oval(x - 2, y - 2, x + 2, y + 2, fill=color, outline=color)

def create_(canvas, width, height, t_values, color):
    canvas.delete("all")
    for t in t_values:
        draw_heart(canvas, t, width, height, color)

    # Menambahkan teks "Love You"
    canvas.create_text(width // 2, height - 30, text="Love You", font=("Helvetica", 24), fill=color)

def update_canvas():
    global img_index, t_values, canvas, width, height, colors

    color = random.choice(colors)
    create_heart(canvas, width, height, t_values, color)
    
    root.after(500, update_canvas)

# Membuat jendela utama
root = tk.Tk()
root.title("Love You")
width, height = 400, 400
root.geometry(f"{width}x{height+50}")

# Membuat canvas
canvas = tk.Canvas(root, width=width, height=height)
canvas.pack()

# Warna-warna yang akan digunakan untuk bunga
colors = ['red', 'pink', 'purple', 'orange', 'blue', 'green', 'yellow']

# Membuat t_values
t_values = [i * 0.01 for i in range(0, 628)]  # Nilai dari 0 hingga 2*pi

# Menampilkan frame pertama
img_index = 0

# Menjalankan animasi
update_canvas()

# Menjalankan loop utama tkinter
root.mainloop()
