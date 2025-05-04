from pygame import *

# --- Настройки ---
win_width = 700
win_height = 500
FPS = 60

# --- Инициализация ---
init()
mixer.init()
font.init()

window = display.set_mode((win_width, win_height))
display.set_caption("Maze")

background = transform.scale(image.load("pol1.png"), (win_width, win_height))

mixer.music.load('labyrinth.mp3')
mixer.music.play(-1)
mixer.music.set_volume(0.2)
money = mixer.Sound('money.ogg')
kick = mixer.Sound('kick.ogg')
stun_sound = mixer.Sound('stun.mp3')
step_sound = mixer.Sound('beg.mp3')
vrag = mixer.Sound('vrag.mp3')
vrag.set_volume(0.3)

stena = image.load("stena.jpg")

font_main = font.Font(None, 70)
font_hint = font.Font(None, 40)
win_text = font_main.render("YOU WIN!", True, (0, 0, 0))
lose_text = font_main.render("YOU LOSE!", True, (0, 0, 0))

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
    def __init__(self, player_image, player_x, player_y, player_speed):
        super().__init__(player_image, player_x, player_y, player_speed)
        self.direction = 'down'
        self.anim_index = 0
        self.anim_counter = 0
        self.stunned = False
        self.stun_timer = 0
        self.walk_left = [transform.scale(image.load(f"player_left/player_left{i}.png").convert_alpha(), (65, 65)) for i in range(1, 5)]
        self.walk_right = [transform.scale(image.load(f"player_right/player_right{i}.png").convert_alpha(), (65, 65)) for i in range(1, 5)]
        self.walk_up = [transform.scale(image.load(f"player_up/player_up{i}.png").convert_alpha(), (65, 65)) for i in range(1, 5)]
        self.walk_down = [transform.scale(image.load(f"player_down/player_down{i}.png").convert_alpha(), (65, 65)) for i in range(1, 5)]
        self.stun_left = [transform.scale(image.load(f"player_stun_left/stun{i}.png").convert_alpha(), (65, 65)) for i in range(1, 4)]
        self.stun_right = [transform.scale(image.load(f"player_stun_right/stun{i}.png").convert_alpha(), (65, 65)) for i in range(1, 4)]
        self.stun_up = [transform.scale(image.load(f"player_stun_up/stun{i}.png").convert_alpha(), (65, 65)) for i in range(1, 4)]
        self.stun_down = [transform.scale(image.load(f"player_stun_down/stun{i}.png").convert_alpha(), (65, 65)) for i in range(1, 4)]

    def update(self):
        if self.stunned:
            self.stun_timer -= 1
            if self.stun_timer <= 0:
                self.stunned = False
            self.anim_counter += 1
            if self.anim_counter >= 10:
                self.anim_counter = 0
                self.anim_index = (self.anim_index + 1) % 3
            return
        keys = key.get_pressed()
        moving = False
        if keys[K_LEFT] and self.rect.x > 5:
            self.rect.x -= self.speed
            self.direction = 'left'
            moving = True
        elif keys[K_RIGHT] and self.rect.x < win_width - 80:
            self.rect.x += self.speed
            self.direction = 'right'
            moving = True
        elif keys[K_UP] and self.rect.y > 5:
            self.rect.y -= self.speed
            self.direction = 'up'
            moving = True
        elif keys[K_DOWN] and self.rect.y < win_height - 80:
            self.rect.y += self.speed
            self.direction = 'down'
            moving = True
        if moving:
            if not step_sound.get_num_channels():
                step_sound.play(-1)
            self.anim_counter += 1
            if self.anim_counter >= 10:
                self.anim_counter = 0
                self.anim_index = (self.anim_index + 1) % 4
        else:
            step_sound.stop()
            self.anim_index = 0

    def reset(self):
        if self.stunned:
            if self.direction == 'left':
                self.image = self.stun_left[self.anim_index % 3]
            elif self.direction == 'right':
                self.image = self.stun_right[self.anim_index % 3]
            elif self.direction == 'up':
                self.image = self.stun_up[self.anim_index % 3]
            elif self.direction == 'down':
                self.image = self.stun_down[self.anim_index % 3]
        else:
            if self.direction == 'left':
                self.image = self.walk_left[self.anim_index]
            elif self.direction == 'right':
                self.image = self.walk_right[self.anim_index]
            elif self.direction == 'up':
                self.image = self.walk_up[self.anim_index]
            elif self.direction == 'down':
                self.image = self.walk_down[self.anim_index]
        window.blit(self.image, (self.rect.x, self.rect.y))

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
        if self.stunned:
            return
        if self.rect.x <= self.patrol_left:
            self.direction = "right"
        if self.rect.x >= self.patrol_right:
            self.direction = "left"
        if self.direction == "left":
            self.rect.x -= self.speed
        else:
            self.rect.x += self.speed
        self.update_vision()
        if not vrag.get_num_channels():
            vrag.play(-1)

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

class VerticalEnemy(Enemy):
    def __init__(self, player_image, player_x, player_y, player_speed, patrol_top, patrol_bottom):
        super().__init__(player_image, player_x, player_y, player_speed, 0, 0)
        self.direction = "up"
        self.patrol_top = patrol_top
        self.patrol_bottom = patrol_bottom

    def update(self):
        if self.stunned:
            return
        if self.rect.y <= self.patrol_top:
            self.direction = "down"
        if self.rect.y >= self.patrol_bottom:
            self.direction = "up"
        if self.direction == "up":
            self.rect.y -= self.speed
        else:
            self.rect.y += self.speed
        self.update_vision()
        if not vrag.get_num_channels():
            vrag.play(-1)

    def update_vision(self):
        if self.direction == "up":
            self.vision_rect.y = self.rect.y - 80
            self.stun_zone.y = self.rect.y + 65
        else:
            self.vision_rect.y = self.rect.y + 65
            self.stun_zone.y = self.rect.y - 70
        self.vision_rect.x = self.rect.x
        self.vision_rect.width = 65
        self.vision_rect.height = 80
        self.stun_zone.x = self.rect.x - 10
        self.stun_zone.width = 70
        self.stun_zone.height = 70

def is_visible(player, enemy, walls):
    start = enemy.rect.center
    end = player.rect.center
    for wall in walls:
        if wall.rect.clipline(start, end):
            return False
    return True

class Wall(sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = transform.scale(stena, (width, height))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def draw_wall(self):
        window.blit(self.image, (self.rect.x, self.rect.y))


def load_level(index):
    level = levels[index]
    player = Player('player_right/player_right1.png', *level["player_pos"], 3)
    final = GameSprite('treasure1.png', *level["final_pos"], 0)
    walls = [Wall(*w) for w in level["walls"]]
    enemies = []
    for enemy_data in level["enemies"]:
        x, y = enemy_data["pos"]
        patrol = enemy_data["patrol"]
        if enemy_data["type"] == "horizontal":
            enemy = Enemy('cyborg1.png', x, y, 2, patrol[0], patrol[1])
        elif enemy_data["type"] == "vertical":
            enemy = VerticalEnemy('cyborg1.png', x, y, 2, patrol[0], patrol[1])
        enemies.append(enemy)
    return player, enemies, final, walls


levels = [
    {
        "player_pos": (5, win_height - 80),
        "final_pos": ((win_width - 270, win_height - 450)),
        "enemies": [
            {"type": "horizontal", "pos": (500, 280), "patrol": (480, 620)}
        ],
        "walls": [
            (0, 0, 700, 10),
            (690, 0, 10, 500),
            (0, 490, 700, 10),
            (100, 0, 10, 350),
            (250, 150, 10, 350),
            (400, 0, 10, 400),
            (100, 150, 70, 10),
            (400, 150, 150, 10),
            (330, 250, 70, 10),
            (250, 370, 70, 10),
        ]
    },
    {
        "player_pos": (600, 40),
        "final_pos": (600, 400),
        "enemies": [
            {"type": "horizontal", "pos": (200, 240), "patrol": (210, 350)},
            {"type": "vertical", "pos": (580, 300), "patrol": (200, 400)}
        ],
        "walls": [
            (0, 0, 700, 10),
            (0, 0, 10, 500),
            (690, 0, 10, 500),
            (0, 490, 700, 10),
            (100, 120, 600, 10),
            (100, 0, 10, 40),
            (200, 80, 10, 40),
            (300, 0, 10, 40),
            (400, 80, 10, 40),
            (500, 0, 10, 40),
            (100, 120, 10, 70),
            (100, 300, 10, 200),
            (100, 360, 50, 10),
            (250, 360, 300, 10),
            (550, 300, 10, 100),
            (550, 130, 10, 70),
            (280, 360, 10, 50),
            (480, 360, 10, 50),
            (380, 450, 10, 50),
        ]
    },
    {
        "player_pos": (600, 400),
        "final_pos": (600, 40),
        "enemies": [
            {"type": "horizontal", "pos": (400, 400), "patrol": (210, 350)},
            {"type": "vertical", "pos": (400, 200), "patrol": (150, 300)},
            {"type": "vertical", "pos": (255, 200), "patrol": (150, 300)}
        ],
        "walls": [
            (0, 0, 700, 10),
            (0, 0, 10, 500),
            (690, 0, 10, 500),
            (0, 490, 700, 10),
            (100, 120, 600, 10),
            (100, 0, 10, 35),
            (200, 85, 10, 35),
            (300, 0, 10, 35),
            (400, 85, 10, 35),
            (500, 0, 10, 35),
            (100, 120, 10, 70),
            (100, 300, 10, 200),
            (100, 360, 50, 10),
            (250, 360, 300, 10),
            (550, 220, 10, 300),
        ]
    }
]


current_level = 0
player, enemies, final, walls = load_level(current_level)
game = True
finish = False
clock = time.Clock()
stunned_count = 0

while game:
    for e in event.get():
        if e.type == QUIT:
            game = False
        if e.type == KEYDOWN and finish and e.key == K_r:
            current_level = 0
            player, enemies, final, walls = load_level(current_level)
            mixer.music.stop()
            mixer.music.play(-1)
            finish = False
            stunned_count = 0

    if not finish:
        player.update()
        for enemy in enemies[:]:
            enemy.update()
            keys = key.get_pressed()
            if keys[K_SPACE] and not enemy.stunned and enemy.stun_zone.colliderect(player.rect) and is_visible(player, enemy, walls):
                enemy.stunned = True
                enemies.remove(enemy)
                player.stunned = True
                player.stun_timer = 30
                stun_sound.play(maxtime=300)
                stunned_count += 1

            if not enemy.stunned and enemy.vision_rect.colliderect(player.rect):
                if is_visible(player, enemy, walls):
                    finish = True
                    result = "lose"
                    kick.play()
                    step_sound.stop()

            if not enemy.stunned and not enemy.stun_zone.colliderect(player.rect) and sprite.collide_rect(player, enemy):
                finish = True
                result = "lose"
                kick.play()
                step_sound.stop()

        for wall in walls:
            if player.rect.colliderect(wall.rect):
                finish = True
                result = "lose"
                kick.play()
                step_sound.stop()
                break

        if sprite.collide_rect(player, final):
            current_level += 1
            if current_level < len(levels):
                player, enemies, final, walls = load_level(current_level)
                mixer.music.stop()
                mixer.music.play(-1)
                finish = False
                continue
            else:
                finish = True
                result = "win"
                money.play()
                step_sound.stop()

        window.blit(background, (0, 0))
        player.reset()
        for enemy in enemies:
            enemy.reset()
            enemy.draw_vision()
            enemy.draw_stun_zone()
            if enemy.stun_zone.colliderect(player.rect):
                hint = font_hint.render("Press SPACE!", True, (255, 255, 255))
                window.blit(hint, (enemy.rect.x - 20, enemy.rect.y - 30))
        final.reset()
        for wall in walls:
            wall.draw_wall()
        stun_text = font_hint.render(f"Stunned: {stunned_count}", True, (255, 255, 255))
        window.blit(stun_text, (10, 10))
    else:
        window.blit(background, (0, 0))
        if result == "win":
            window.blit(win_text, (200, 200))
        else:
            window.blit(lose_text, (200, 200))
        restart_hint = font_hint.render("Press R to restart", True, (0, 0, 0))
        window.blit(restart_hint, (200, 300))
        stun_result = font_hint.render(f"Total stunned: {stunned_count}", True, (0, 0, 0))
        window.blit(stun_result, (200, 350))
    display.update()
    clock.tick(FPS)
