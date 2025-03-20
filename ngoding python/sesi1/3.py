import tkinter as tk

root = tk.Tk()
root.geometry("600x540")

def iLoveYoufida(texto):
    inserirTexto.delete(1.0, "end")
    inserirTexto.insert(1.0, texto)

inserirTexto = tk.Text(root, height=30)
inserirTexto.pack()

iloveYou = '\n'.join([''.join([('fida❤'[(x-y)%len('fida❤')] if 
                                ((x*0.05)**2+(y*0.1)**2-1)**3-(x*0.05)**2*(y*0.1)**3<=0 else ' ') for x in range(-30, 30)]) 
                                for y in range(15, -15, -1)])

botao = tk.Button(root, 
                  height=1, 
                  width=10, 
                  text="I love 💖 You",
                  command=lambda:iLoveYoufida(iloveYou))
botao.pack()

root.mainloop()