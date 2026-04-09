import pygame
import random

pygame.init()

# KONFIGURASI LAYAR
WIDTH = 500
HEIGHT = 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Car Game - Day & Night Cycle')

# WARNA-WARNA (RGB)
COLORS = {
    'GRAY': (100, 100, 100),
    'GREEN': (76, 208, 56),
    'RED': (200, 0, 0),
    'WHITE': (255, 255, 255),
    'YELLOW': (255, 232, 0),
    'BLACK': (0, 0, 0)
}

# PENGATURAN JALAN DAN MARKA
ROAD_WIDTH = 300
MARKER_WIDTH = 10
MARKER_HEIGHT = 50

# Koordinat jalur
LEFT_LANE = 150
CENTER_LANE = 250
RIGHT_LANE = 350
LANES = [LEFT_LANE, CENTER_LANE, RIGHT_LANE]

# Area jalan dan pinggir jalan
road_rect = (100, 0, ROAD_WIDTH, HEIGHT)
left_edge_rect = (95, 0, MARKER_WIDTH, HEIGHT)
right_edge_rect = (395, 0, MARKER_WIDTH, HEIGHT)

# PENGATURAN MOBIL PEMAIN
PLAYER_START_X = 250
PLAYER_START_Y = 400

# PENGATURAN FRAME DAN GAME
clock = pygame.time.Clock()
FPS = 120

# Variabel game
game_over = False
game_speed = 2
player_score = 0

# FITUR SIKLUS SIANG-MALAM
is_night_mode = False
cycle_timer = 0
CYCLE_DURATION = 10

# Font untuk teks
main_font = pygame.font.Font(pygame.font.get_default_font(), 16)
small_font = pygame.font.Font(pygame.font.get_default_font(), 12)


# CLASS VEHICLE (KENDARAAN)
class Vehicle(pygame.sprite.Sprite):
    """Class dasar untuk semua kendaraan"""

    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self)

        # Skalakan gambar agar muat di jalur
        scale_factor = 45 / image.get_rect().width
        new_width = image.get_rect().width * scale_factor
        new_height = image.get_rect().height * scale_factor
        self.image = pygame.transform.scale(image, (new_width, new_height))

        self.rect = self.image.get_rect()
        self.rect.center = [x, y]


class PlayerVehicle(Vehicle):
    """Class khusus untuk mobil pemain"""

    def __init__(self, x, y):
        player_image = pygame.image.load('images/car.png')
        super().__init__(player_image, x, y)

# MEMUAT SEMUA GAMBAR
player_group = pygame.sprite.Group()
vehicle_group = pygame.sprite.Group()

# Membuat mobil pemain
player = PlayerVehicle(PLAYER_START_X, PLAYER_START_Y)
player_group.add(player)

# Memuat gambar mobil lawan
enemy_images = []
enemy_filenames = ['pickup_truck.png', 'semi_trailer.png', 'taxi.png', 'van.png']
for filename in enemy_filenames:
    img = pygame.image.load('images/' + filename)
    enemy_images.append(img)

# Memuat gambar tabrakan
crash_img = pygame.image.load('images/crash.png')
crash_rect = crash_img.get_rect()

# FUNGSI-FUNGSI BANTUAN
def update_day_night_cycle():
    """Update timer dan ganti mode siang/malam jika perlu"""
    global is_night_mode, cycle_timer

    if not game_over:
        cycle_timer += 1 / FPS

        if cycle_timer >= CYCLE_DURATION:
            cycle_timer = 0
            is_night_mode = not is_night_mode


def draw_grass():
    """Gambar rumput (hijau saat siang, hitam saat malam)"""
    if is_night_mode and not game_over:
        screen.fill(COLORS['BLACK'])
    else:
        screen.fill(COLORS['GREEN'])


def draw_road():
    """Gambar jalan dan marka"""
    pygame.draw.rect(screen, COLORS['GRAY'], road_rect)
    pygame.draw.rect(screen, COLORS['YELLOW'], left_edge_rect)
    pygame.draw.rect(screen, COLORS['YELLOW'], right_edge_rect)


def draw_lane_markers():
    """Gambar marka putus-putus di jalur"""
    global lane_marker_move_y

    lane_marker_move_y += game_speed * 2
    if lane_marker_move_y >= MARKER_HEIGHT * 2:
        lane_marker_move_y = 0

    for y in range(MARKER_HEIGHT * -2, HEIGHT, MARKER_HEIGHT * 2):
        pygame.draw.rect(screen, COLORS['WHITE'],
                         (LEFT_LANE + 45, y + lane_marker_move_y, MARKER_WIDTH, MARKER_HEIGHT))
        pygame.draw.rect(screen, COLORS['WHITE'],
                         (CENTER_LANE + 45, y + lane_marker_move_y, MARKER_WIDTH, MARKER_HEIGHT))


def add_enemy_vehicle():
    """Tambahkan mobil lawan secara acak"""
    if len(vehicle_group) < 2:
        can_add = True
        for vehicle in vehicle_group:
            if vehicle.rect.top < vehicle.rect.height * 1.5:
                can_add = False

        if can_add:
            lane = random.choice(LANES)
            image = random.choice(enemy_images)
            new_vehicle = Vehicle(image, lane, HEIGHT / -2)
            vehicle_group.add(new_vehicle)


def move_enemy_vehicles():
    """Gerakkan semua mobil lawan dan update score"""
    global player_score, game_speed

    for vehicle in vehicle_group:
        vehicle.rect.y += game_speed

        if vehicle.rect.top >= HEIGHT:
            vehicle.kill()
            player_score += 1

            if player_score > 0 and player_score % 5 == 0:
                game_speed += 1


def draw_night_effect():
    """Gambar efek gelap saat mode malam"""
    if is_night_mode and not game_over:
        darkness = pygame.Surface((WIDTH, HEIGHT))
        darkness.set_alpha(150)
        darkness.fill(COLORS['BLACK'])
        screen.blit(darkness, (0, 0))

def draw_mode_indicator():
    """Tampilkan indikator mode siang/malam di layar"""
    if not game_over:
        if is_night_mode:
            mode_text = small_font.render('🌙 NIGHT TIME', True, COLORS['YELLOW'])
        else:
            mode_text = small_font.render('☀️ DAY TIME', True, COLORS['WHITE'])
        mode_rect = mode_text.get_rect(center=(WIDTH / 2, 20))
        screen.blit(mode_text, mode_rect)

        time_left = int(CYCLE_DURATION - cycle_timer)
        if is_night_mode:
            timer_text = small_font.render(f'Day in: {time_left}s', True, COLORS['YELLOW'])
        else:
            timer_text = small_font.render(f'Night in: {time_left}s', True, COLORS['WHITE'])
        timer_rect = timer_text.get_rect(center=(WIDTH / 2, 40))
        screen.blit(timer_text, timer_rect)


def draw_score():
    """Tampilkan skor di layar"""
    score_text = main_font.render(f'Score: {player_score}', True, COLORS['WHITE'])
    score_rect = score_text.get_rect()
    score_rect.center = (50, 400)
    screen.blit(score_text, score_rect)


def handle_collision(event_key=None):
    """Handle tabrakan dengan mobil lain"""
    global game_over

    for vehicle in vehicle_group:
        if pygame.sprite.collide_rect(player, vehicle):
            game_over = True

            if event_key == pygame.K_LEFT:
                player.rect.left = vehicle.rect.right
                crash_rect.center = [player.rect.left,
                                     (player.rect.center[1] + vehicle.rect.center[1]) / 2]
            elif event_key == pygame.K_RIGHT:
                player.rect.right = vehicle.rect.left
                crash_rect.center = [player.rect.right,
                                     (player.rect.center[1] + vehicle.rect.center[1]) / 2]
            else:
                crash_rect.center = [player.rect.center[0], player.rect.top]

            return True
    return False


def reset_game():
    """Reset semua variabel game ke awal"""
    global game_over, game_speed, player_score, is_night_mode, cycle_timer

    game_over = False
    game_speed = 2
    player_score = 0
    is_night_mode = False
    cycle_timer = 0

    vehicle_group.empty()
    player.rect.center = [PLAYER_START_X, PLAYER_START_Y]


def draw_game_over():
    """Tampilkan layar game over"""
    screen.blit(crash_img, crash_rect)
    pygame.draw.rect(screen, COLORS['RED'], (0, 50, WIDTH, 100))

    text = main_font.render('Game over. Play again? (Y/N)', True, COLORS['WHITE'])
    text_rect = text.get_rect()
    text_rect.center = (WIDTH / 2, 100)
    screen.blit(text, text_rect)
    pygame.display.update()


def handle_game_over():
    """Handle input saat game over (Y = main lagi, N = keluar)"""
    global game_over, running

    waiting = True
    while waiting:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = False
                waiting = False
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    reset_game()
                    waiting = False
                    return True
                elif event.key == pygame.K_n:
                    game_over = False
                    waiting = False
                    return False
    return True

# GAME LOOP UTAMA
running = True
lane_marker_move_y = 0

while running:

    clock.tick(FPS)
    update_day_night_cycle()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT and player.rect.center[0] > LEFT_LANE:
                player.rect.x -= 100
                handle_collision(event.key)
            elif event.key == pygame.K_RIGHT and player.rect.center[0] < RIGHT_LANE:
                player.rect.x += 100
                handle_collision(event.key)

    draw_grass()
    draw_road()
    draw_lane_markers()

    player_group.draw(screen)

    add_enemy_vehicle()
    move_enemy_vehicles()

    vehicle_group.draw(screen)

    draw_night_effect()
    draw_mode_indicator()
    draw_score()

    if pygame.sprite.spritecollide(player, vehicle_group, False):
        handle_collision()

    if game_over:
        draw_game_over()
        running = handle_game_over()

    pygame.display.update()

pygame.quit()