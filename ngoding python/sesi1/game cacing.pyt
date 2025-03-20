import curses
from random import randint

def main(stdscr):
    # Inisialisasi layar dan pengaturan
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(150)

    # Ukuran window
    height, width = stdscr.getmaxyx()
    cacing = [(height // 2, width // 4)]  # Kepala cacing di posisi tengah
    arah = curses.KEY_RIGHT
    makanan = (randint(1, height - 2), randint(1, width - 2))
    
    # Tampilkan makanan awal
    stdscr.addch(makanan[0], makanan[1], curses.ACS_PI)

    # Permainan dimulai
    while True:
        # Input kontrol
        tombol = stdscr.getch()
        arah = tombol if tombol in [curses.KEY_RIGHT, curses.KEY_LEFT, curses.KEY_UP, curses.KEY_DOWN] else arah

        # Gerakkan kepala cacing
        kepala_y, kepala_x = cacing[0]
        if arah == curses.KEY_RIGHT:
            kepala_x += 1
        elif arah == curses.KEY_LEFT:
            kepala_x -= 1
        elif arah == curses.KEY_UP:
            kepala_y -= 1
        elif arah == curses.KEY_DOWN:
            kepala_y += 1

        # Cek tabrakan dinding atau tubuh sendiri
        if (
            kepala_y in [0, height] or 
            kepala_x in [0, width] or 
            (kepala_y, kepala_x) in cacing
        ):
            stdscr.addstr(height // 2, width // 4, "Game Over!")
            stdscr.refresh()
            stdscr.getch()
            break

        # Perbarui posisi cacing
        cacing.insert(0, (kepala_y, kepala_x))

        # Cek jika makan makanan
        if cacing[0] == makanan:
            makanan = None
            while makanan is None:
                nf = (randint(1, height - 2), randint(1, width - 2))
                makanan = nf if nf not in cacing else None
            stdscr.addch(makanan[0], makanan[1], curses.ACS_PI)
        else:
            # Hapus ekor cacing jika tidak makan
            stdscr.addch(cacing[-1][0], cacing[-1][1], ' ')
            cacing.pop()

        # Tampilkan kepala baru
        stdscr.addch(cacing[0][0], cacing[0][1], curses.ACS_CKBOARD)

# Jalankan permainan
curses.wrapper(main)
