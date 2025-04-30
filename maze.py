from pygame import *

# --- Налаштування ---
win_width = 700
win_height = 500
FPS = 60

# --- Ініціалізація ---
init()
mixer.init()
font.init()

# --- Вікно гри ---
window = display.set_mode((win_width, win_height))
display.set_caption("Maze")

background = transform.scale(image.load("background.jpg"), (win_width, win_height))

# --- Звуки ---
mixer.music.load('jungles.ogg')
money = mixer.Sound('money.ogg')
kick = mixer.Sound('kick.ogg')
stun_sound = mixer.Sound('stun.mp3')

# --- Шрифти ---
font_main = font.Font(None, 70)
font_hint = font.Font(None, 40)
win_text = font_main.render("YOU WIN!", True, (0, 0, 0))
lose_text = font_main.render("YOU LOSE!", True, (0, 0, 0))

# --- Класи ---
class GameSprite(sprite.Sprite):
    def __init__(self, player_image, player_x, player_y, player_speed):
        super().__init__()
        self.image = transform.scale(image.load(player_image), (65, 65))
        self.speed = player_speed
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y

    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

class Player(GameSprite):
    def update(self):
        keys = key.get_pressed()
        if keys[K_LEFT] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys[K_RIGHT] and self.rect.x < win_width - 80:
            self.rect.x += self.speed
        if keys[K_UP] and self.rect.y > 5:
            self.rect.y -= self.speed
        if keys[K_DOWN] and self.rect.y < win_height - 80:
            self.rect.y += self.speed

class Enemy(GameSprite):
    def __init__(self, player_image, player_x, player_y, player_speed, patrol_left, patrol_right):
        super().__init__(player_image, player_x, player_y, player_speed)
        self.direction = "left"
        self.patrol_left = patrol_left
        self.patrol_right = patrol_right
        self.vision_rect = Rect(0, 0, 80, 65)
        self.stun_zone = Rect(0, 0, 70, 70)
        self.update_vision()
        self.stunned = False

    def update(self):
        if not self.stunned:
            if self.rect.x <= self.patrol_left:
                self.direction = "right"
            if self.rect.x >= self.patrol_right:
                self.direction = "left"

            if self.direction == "left":
                self.rect.x -= self.speed
            else:
                self.rect.x += self.speed

            self.update_vision()

    def update_vision(self):
        if self.direction == "left":
            self.vision_rect.x = self.rect.x - 80
            self.stun_zone.x = self.rect.x + 65
        else:
            self.vision_rect.x = self.rect.x + 65
            self.stun_zone.x = self.rect.x - 70

        self.vision_rect.y = self.rect.y
        self.vision_rect.width = 80
        self.vision_rect.height = 65

        self.stun_zone.y = self.rect.y - 10
        self.stun_zone.width = 70
        self.stun_zone.height = 70

    def draw_vision(self):
        if not self.stunned:
            surface = Surface((self.vision_rect.width, self.vision_rect.height), SRCALPHA)
            surface.fill((255, 0, 0, 100))
            window.blit(surface, (self.vision_rect.x, self.vision_rect.y))

    def draw_stun_zone(self):
        if not self.stunned:
            surface = Surface((self.stun_zone.width, self.stun_zone.height), SRCALPHA)
            surface.fill((0, 255, 0, 100))
            window.blit(surface, (self.stun_zone.x, self.stun_zone.y))

class Wall(sprite.Sprite):
    def __init__(self, wall_x, wall_y, wall_width, wall_height):
        super().__init__()
        self.image = Surface((wall_width, wall_height))
        self.image.fill((154, 205, 50))
        self.rect = self.image.get_rect()
        self.rect.x = wall_x
        self.rect.y = wall_y

    def draw_wall(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

def is_visible(player, enemy, walls):
    start = enemy.rect.center
    end = player.rect.center
    for wall in walls:
        if wall.rect.clipline(start, end):
            return False
    return True

# --- Рівні з кількома ворогами ---
levels = [
    {
        "player_pos": (5, win_height - 80),
        "final_pos": (win_width - 700, win_height - 150),
        "enemies": [
            
            {"pos": (500, 280), "patrol": (480, 620)}
        ],
        "walls": [
            (0, 0, 700, 10),
            (690, 0, 10, 500),
            (0, 490, 700, 10),
            (100, 0, 10, 350),
            (250, 150, 10, 350),
            (400, 0, 10, 400),
            (100, 150, 80, 10),
            (400, 150, 150, 10),
            (330, 250, 80, 10),
            (250, 370, 80, 10),
        ]
    },
    {
        "player_pos": (600, 40),
        "final_pos": (600, 400),
        "enemies": [
            {"pos": (200, 240), "patrol": (210, 350)}
        ],
        "walls": [
            (0, 0, 700, 10),
            (0, 0, 10, 500),
            (690, 0, 10, 500),
            (0, 490, 700, 10),
            (100, 120, 600, 10),
            (100, 0, 10, 50),
            (200, 80, 10, 50),
            (300, 0, 10, 50),
            (400, 80, 10, 50),
            (500, 0, 10, 50),
            (100, 120, 10, 100),
            (100, 300, 10, 200),
        ]
    }
]


# --- Завантаження рівня ---
def load_level(index):
    level = levels[index]
    player = Player('hero.png', *level["player_pos"], 3)
    final = GameSprite('treasure.png', *level["final_pos"], 0)
    walls = [Wall(*w) for w in level["walls"]]
    enemies = []
    for enemy_data in level["enemies"]:
        x, y = enemy_data["pos"]
        patrol_left, patrol_right = enemy_data["patrol"]
        enemy = Enemy('cyborg.png', x, y, 2, patrol_left, patrol_right)
        enemies.append(enemy)
    return player, enemies, final, walls

# --- Ігрові змінні ---
current_level = 0
player, enemies, final, walls = load_level(current_level)
game = True
finish = False
clock = time.Clock()

# --- Ігровий цикл ---
while game:
    for e in event.get():
        if e.type == QUIT:
            game = False
        if e.type == KEYDOWN and finish and e.key == K_r:
            current_level = 0
            player, enemies, final, walls = load_level(current_level)
            finish = False
            #mixer.music.play(-1)

    if not finish:
        player.update()
        for enemy in enemies:
            enemy.update()

        keys = key.get_pressed()
        for enemy in enemies:
            if keys[K_SPACE] and not enemy.stunned and enemy.stun_zone.colliderect(player.rect):
                enemy.stunned = True
                stun_sound.play(maxtime=300)

            if not enemy.stunned and enemy.vision_rect.colliderect(player.rect):
                if is_visible(player, enemy, walls):
                    finish = True
                    result = "lose"
                    kick.play()

            if not enemy.stunned and not enemy.stun_zone.colliderect(player.rect) and sprite.collide_rect(player, enemy):
                finish = True
                result = "lose"
                kick.play()

        for wall in walls:
            if player.rect.colliderect(wall.rect):
                finish = True
                result = "lose"
                kick.play()
                break

        if sprite.collide_rect(player, final):
            current_level += 1
            if current_level < len(levels):
                player, enemies, final, walls = load_level(current_level)
                finish = False
                continue
            else:
                finish = True
                result = "win"
                money.play()

        window.blit(background, (0, 0))
        player.reset()
        for enemy in enemies:
            if not enemy.stunned:
                enemy.reset()
                enemy.draw_vision()
                enemy.draw_stun_zone()
                if enemy.stun_zone.colliderect(player.rect):
                    hint = font_hint.render("Press SPACE!", True, (255, 255, 255))
                    window.blit(hint, (enemy.rect.x - 20, enemy.rect.y - 30))
        final.reset()
        for wall in walls:
            wall.draw_wall()
    else:
        window.blit(background, (0, 0))
        if result == "win":
            window.blit(win_text, (200, 200))
        else:
            window.blit(lose_text, (200, 200))
        restart_hint = font_hint.render("Press R to restart", True, (0, 0, 0))
        window.blit(restart_hint, (200, 300))

    display.update()
    clock.tick(FPS)
