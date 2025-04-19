from pygame import *


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

class Playar(GameSprite):
    def update(self):
        keys = key.get_pressed()
        if keys[K_LEFT] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys[K_RIGHT] and self.rect.x < win_width - 80:
            self.rect.x += self.speed
        if keys[K_UP] and self.rect.y > 5:
            self.rect.y -= self.speed  # <-- Исправлено движение вверх
        if keys[K_DOWN] and self.rect.y < win_height - 80:
            self.rect.y += self.speed


class Enemy(GameSprite):
    def __init__(self, player_image, player_x, player_y, player_speed):
        super().__init__(player_image, player_x, player_y, player_speed)
        self.direction = 'left'

    def update(self):
        if self.rect.x <= 450:
            self.direction = 'right'
        if self.rect.x >= 600:
            self.direction = 'left'

        if self.direction == 'left':
            self.rect.x -= self.speed
        else:
            self.rect.x += self.speed



win_width = 700
win_height = 500


window = display.set_mode((win_width, win_height))
display.set_caption("Maze")
background = transform.scale(image.load("background.jpg"), (win_width, win_height))
 

player = Playar("hero.png", 100, 100, 10)
cyborg = Enemy("cyborg.png", 600, 300, 2)
final = GameSprite("treasure.png", 300, 300, 0)




 
game = True
clock = time.Clock()
FPS = 144
#музика
mixer.init()
mixer.music.load('jungles.ogg')
mixer.music.play()
 
while game:
    for e in event.get():
        if e.type == QUIT:
            game = False

    
    window.blit(background,(0, 0))
    player.update()
    cyborg.update()
    player.reset()
    cyborg.reset()
    final.reset()
    
    display.update()
    clock.tick(FPS)