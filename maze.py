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

# --- Фонова музика ---
mixer.music.load('jungles.ogg')
# mixer.music.play(-1)

money = mixer.Sound('money.ogg')
kick = mixer.Sound('kick.ogg')

# --- Шрифти ---
font_main = font.Font(None, 70)
font_hint = font.Font(None, 40)  # Шрифт для подсказки
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
    direction = "left"

    def __init__(self, player_image, player_x, player_y, player_speed):
        super().__init__(player_image, player_x, player_y, player_speed)
        self.vision_rect = Rect(0, 0, 80, 65)
        self.stun_zone = Rect(0, 0, 70, 70)  # Зона оглушения
        self.update_vision()
        self.stunned = False

    def update(self):
        if not self.stunned:
            if self.rect.x <= 470:
                self.direction = "right"
            if self.rect.x >= win_width - 85:
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
        self.width = wall_width
        self.height = wall_height
        self.image = Surface((self.width, self.height))
        self.color = (0, 0, 0)
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.rect.x = wall_x
        self.rect.y = wall_y

    def draw_wall(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

    def set_color(self, color_1, color_2, color_3):
        self.color = (color_1, color_2, color_3)
        self.image.fill(self.color)

# --- Об'єкти ---
player = Player('hero.png', 5, win_height - 80, 3)
monster = Enemy('cyborg.png', win_width - 80, 280, 2)
final = GameSprite('treasure.png', win_width - 270, win_height - 450, 0)

# --- Стіни лабіринту ---
walls = [
    Wall(0, 0, 700, 10),
    Wall(690, 0, 10, 500),
    Wall(0, 490, 700, 10),
    Wall(100, 0, 10, 350),
    Wall(250, 150, 10, 350),
    Wall(400, 0, 10, 400),
    Wall(100, 150, 80, 10),
    Wall(400, 150, 150, 10),
    Wall(330, 250, 80, 10),
    Wall(250, 370, 80, 10),
]

for wall in walls:
    wall.set_color(154, 205, 50)

# --- Ігрові змінні ---
game = True
finish = False
clock = time.Clock()

# --- Ігровий цикл ---
while game:
    for e in event.get():
        if e.type == QUIT:
            game = False

    if not finish:
        player.update()
        monster.update()

        keys = key.get_pressed()

        # --- Оглушение врага на кнопку SPACE ---
        if keys[K_SPACE] and not monster.stunned:
            if monster.stun_zone.colliderect(player.rect):
                monster.stunned = True

        # --- Проверка проигрыша ---
        player_in_stun_zone = monster.stun_zone.colliderect(player.rect)

        # Проверка проигрыша при касании монстра или стены
        if not monster.stunned and not player_in_stun_zone:
            if sprite.collide_rect(player, monster):
                finish = True
                result = "lose"
                kick.play()

        if any(sprite.collide_rect(player, wall) for wall in walls):
            finish = True
            result = "lose"
            kick.play()

        # --- Проверка победы ---
        if sprite.collide_rect(player, final):
            finish = True
            result = "win"
            money.play()

        # --- Рисуем игру ---
        window.blit(background, (0, 0))
        player.reset()
        if not monster.stunned:
            monster.reset()
            monster.draw_vision()
            monster.draw_stun_zone()

            if monster.stun_zone.colliderect(player.rect):
                hint_text = font_hint.render("Press SPACE!", True, (255, 255, 255))
                window.blit(hint_text, (monster.rect.x - 20, monster.rect.y - 30))

        final.reset()
        for wall in walls:
            wall.draw_wall()

    else:
        window.blit(background, (0, 0))
        if result == "win":
            window.blit(win_text, (200, 200))
        else:
            window.blit(lose_text, (200, 200))

    display.update()
    clock.tick(FPS)
