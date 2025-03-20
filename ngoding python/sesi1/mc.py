

# Inisialisasi Pygame
pygame.init()

# Konstanta
WIDTH, HEIGHT = 800, 600
BLOCK_SIZE = 40
GRAVITY = 1
JUMP_STRENGTH = -15

# Warna
BROWN = (139, 69, 19)
GREEN = (34, 139, 34)
BLUE = (135, 206, 250)

# Inisialisasi layar
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Minecraft 2D")

# Player
player = pygame.Rect(100, 500, BLOCK_SIZE, BLOCK_SIZE)
player_vel_y = 0
on_ground = False

# Blok dunia (x, y)
blocks = {(i * BLOCK_SIZE, HEIGHT - BLOCK_SIZE) for i in range(WIDTH // BLOCK_SIZE)}

# Game loop
running = True
while running:
    screen.fill(BLUE)  # Latar belakang langit
    
    # Event handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:  # Klik mouse untuk tambahkan blok
            x, y = event.pos
            x = x // BLOCK_SIZE * BLOCK_SIZE
            y = y // BLOCK_SIZE * BLOCK_SIZE
            if (x, y) in blocks:
                blocks.remove((x, y))  # Hancurkan blok
            else:
                blocks.add((x, y))  # Tambahkan blok
    
    # Kontrol keyboard
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player.x -= 5
    if keys[pygame.K_RIGHT]:
        player.x += 5
    if keys[pygame.K_SPACE] and on_ground:
        player_vel_y = JUMP_STRENGTH  # Lompat
    
    # Gravitasi
    player_vel_y += GRAVITY
    player.y += player_vel_y

    # Cek lantai
    on_ground = False
    for block in blocks:
        bx, by = block
        if player.colliderect(pygame.Rect(bx, by, BLOCK_SIZE, BLOCK_SIZE)):
            player.y = by - BLOCK_SIZE  # Tetap di atas blok
            player_vel_y = 0
            on_ground = True

    # Gambar blok
    for block in blocks:
        pygame.draw.rect(screen, BROWN, (*block, BLOCK_SIZE, BLOCK_SIZE))

    # Gambar pemain
    pygame.draw.rect(screen, GREEN, player)

    pygame.display.flip()
    pygame.time.delay(30)

pygame.quit()
