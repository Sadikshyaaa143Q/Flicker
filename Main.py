import math
import pygame
import random
from pygame import mixer


# Intialize the pygame
pygame.init()

screen = pygame.display.set_mode((800, 600))  # pygame gives us the module display width = 800 and height 600

# pressing the close button will exit the game this is an event

# Background
background = pygame.image.load('background.png')  # loading the background image
# background sound
mixer.music.load('background.wav')
mixer.music.play(-1)  # play the background sound on loop

# Title and icon
pygame.display.set_caption("Flicker")
icon = pygame.image.load('lamp.png')  # loading the icon image
pygame.display.set_icon(icon)

font = pygame.font.Font('freesansbold.ttf', 32)
small_font = pygame.font.Font('freesansbold.ttf', 24)

WHITE = (255, 255, 255)
GRAY = (150, 150, 150)
ACCENT = (255, 176, 59)

# Lamp
lamp = pygame.image.load('lamp.png')  # loading the lamp image
lampX = 320
lampY = 0

# moth
no_of_moths = 3
moth_base_img = pygame.image.load('moth.png')  # loading the moth image once, reused everywhere
mothImg = []
mothX = []
mothY = []
moth_alive = []

# adjust these once you see your actual lamp.png dimensions on screen
moth_positions = [
    (330, 20),   
    (370, 55),   
    (330, 90),  
]

for i in range(no_of_moths):
    mothImg.append(moth_base_img)
    mothX.append(moth_positions[i][0])
    mothY.append(moth_positions[i][1])
    moth_alive.append(True)

# Player
# top left corner of the game window is (0,0) and bottom right corner is (800,600)
playerImg = pygame.image.load('Player.png')
playerX = random.randint(0, 672)  # random position of the player on the x-axis
playerY = 480
playerX_change = 0

# bullet
bulletImg = pygame.image.load('bullet.png')
bulletX = 0
bulletY = 480  # bullet should be fired from the player
bulletY_change = 10
bullet_state = "ready"  # ready - you can't see the bullet on the screen, fire - the bullet is currently moving

game_state = "level1_intro"

target_number = random.randint(1, 7)
target_bits = [int(x) for x in format(target_number, '03b')]  # Convert target number to 3-bit binary representation

button_width = 140
button_height = 70
start_x = 130
button_y = 250
button_gap = 60

button_rects = []
red_centers = []
green_centers = []
button_state = [0, 0, 0]
level2_brightness = 0  # 0 = black, 255 = fully lit
brighten_speed = 4

for i in range(3):
    x = start_x + i * (button_width + button_gap)
    rect = pygame.Rect(x, button_y, button_width, button_height)
    button_rects.append(rect)
    red_centers.append((rect.left + 35, rect.centery))
    green_centers.append((rect.right - 35, rect.centery))

circle_radius = 22
click_radius = 22



class Level3:
    """Rotate the fixed mirror to reflect the beam onto each remaining moth."""

    def __init__(self):
        self.source = pygame.Vector2(400, 40)
        self.beam_dir = pygame.Vector2(0, 1)
        self.mirror_pos = pygame.Vector2(400, 300)
        self.angle = 20.0
        self.speed = 70.0
        self.angle_change = 0.0

        positions = [(120, 470), (660, 500), (250, 130), (560, 200)]
        self.moth_count = len(positions)
        self.moth_pos = [pygame.Vector2(p) for p in positions]
        self.moth_alive = [True] * self.moth_count
        self.cleared = False

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.angle_change = -self.speed
            elif event.key == pygame.K_RIGHT:
                self.angle_change = self.speed
        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                self.angle_change = 0.0

    def _mirror_normal(self):
        rad = math.radians(self.angle)
        surface_dir = pygame.Vector2(math.cos(rad), math.sin(rad))
        return pygame.Vector2(-surface_dir.y, surface_dir.x)

    def _reflected_ray(self):
        n = self._mirror_normal()
        d = self.beam_dir
        return (d - 2 * d.dot(n) * n).normalize()

    def update(self, dt):
        if self.cleared:
            return

        self.angle += self.angle_change * dt
        self.angle = max(-70, min(70, self.angle))

        r = self._reflected_ray()
        far = self.mirror_pos + r * 1200
        for i in range(self.moth_count):
            if not self.moth_alive[i]:
                continue
            rect = pygame.Rect(0, 0, 32, 32)
            rect.center = self.moth_pos[i]
            if rect.clipline(self.mirror_pos, far):
                self.moth_alive[i] = False
                explosion_sound = mixer.Sound('explosion.wav')
                explosion_sound.play()

        self.cleared = not any(self.moth_alive)

    def draw(self, surface):
        pygame.draw.circle(surface, (255, 250, 235), self.source, 9)
        pygame.draw.line(surface, (200, 200, 200), self.source, self.mirror_pos, 2)

        r = self._reflected_ray()
        far = self.mirror_pos + r * 1200
        pygame.draw.line(surface, ACCENT, self.mirror_pos, far, 3)

        rad = math.radians(self.angle)
        d = pygame.Vector2(math.cos(rad), math.sin(rad)) * 55
        p1, p2 = self.mirror_pos - d, self.mirror_pos + d
        pygame.draw.line(surface, (60, 60, 64), p1, p2, 12)
        pygame.draw.line(surface, WHITE, p1, p2, 7)

        for i in range(self.moth_count):
            if self.moth_alive[i]:
                pos = self.moth_pos[i]
                surface.blit(moth_base_img, moth_base_img.get_rect(center=pos))

        hint = small_font.render("Left / Right to rotate mirror onto moths", True, GRAY)
        surface.blit(hint, (400 - hint.get_width() // 2, 570))


level3_instance = None
clock = pygame.time.Clock()


def draw_lamp(x, y):
    screen.blit(lamp, (x, y))  # draw the lamp image at the specified coordinates


def draw_moth(x, y, i):
    screen.blit(mothImg[i], (x, y))  # draw the moth image at the specified coordinates


def draw_player(x, y):
    screen.blit(playerImg, (x, y))  # draw the player image at the specified coordinates


def fire_bullet(x, y):
    global bullet_state
    if bullet_state != "finished":
        bullet_state = "fire"  # change the bullet state to fire
        screen.blit(bulletImg, (x + 16, y + 10))  # draw the bullet image at the specified coordinates


def isCollision(mothImg_i, mothX, mothY, bulletImg, bulletX, bulletY):
    moth_rect = mothImg_i.get_rect(topleft=(mothX, mothY)).inflate(-8, -8)  
    bullet_rect = bulletImg.get_rect(topleft=(bulletX, bulletY)).inflate(-4, -4)
    return moth_rect.colliderect(bullet_rect)


def draw_glow(center, color, base_radius):
    # soft layered glow to make the active circle look lit
    glow_surface = pygame.Surface((base_radius * 4, base_radius * 4), pygame.SRCALPHA)
    for r, alpha in [(base_radius * 2, 40), (int(base_radius * 1.5), 80), (base_radius, 255)]:
        pygame.draw.circle(glow_surface, (*color, alpha), (base_radius * 2, base_radius * 2), r)
    screen.blit(glow_surface, (center[0] - base_radius * 2, center[1] - base_radius * 2))


def draw_button(i):
    rect = button_rects[i]
    pygame.draw.rect(screen, (45, 45, 50), rect, border_radius=10)
    pygame.draw.rect(screen, (90, 90, 96), rect, width=3, border_radius=10)

    is_on = button_state[i] == 1

    # red circle (off) 
    if is_on:
        pygame.draw.circle(screen, (80, 40, 40), red_centers[i], circle_radius)
    else:
        draw_glow(red_centers[i], (255, 99, 71), circle_radius)

    # green circle (on) 
    if is_on:
        draw_glow(green_centers[i], (64, 214, 158), circle_radius)
    else:
        pygame.draw.circle(screen, (30, 70, 60), green_centers[i], circle_radius)

    label = font.render(str(button_state[i]), True, (230, 230, 230))
    screen.blit(label, (rect.centerx - 8, rect.bottom + 10))


def draw_l1_intro_popup():
    dim = pygame.Surface((800, 600), pygame.SRCALPHA)
    dim.fill((0, 0, 0, 180))
    screen.blit(dim, (0, 0))

    box_rect = pygame.Rect(100, 150, 600, 340)
    pygame.draw.rect(screen, (40, 40, 40), box_rect, border_radius=15)
    pygame.draw.rect(screen, (200, 200, 200), box_rect, width=3, border_radius=15)

    lines = [
        "LEVEL 1",
        "",
        "Moths have swarmed the lamp",
        "and blocked its light.",
        "",
        "Left / Right to move, Space to shoot them down.",
        "",
        "Click anywhere to begin."
    ]

    for idx, line in enumerate(lines):
        text_surface = small_font.render(line, True, WHITE)
        screen.blit(text_surface, (box_rect.x + 30, box_rect.y + 30 + idx * 30))


def draw_intro_popup():
    # dim the whole screen behind the popup
    dim = pygame.Surface((800, 600), pygame.SRCALPHA)
    dim.fill((0, 0, 0, 180))
    screen.blit(dim, (0, 0))

    box_rect = pygame.Rect(100, 150, 660, 340)
    pygame.draw.rect(screen, (40, 40, 40), box_rect, border_radius=15)
    pygame.draw.rect(screen, (200, 200, 200), box_rect, width=3, border_radius=15)

    lines = [
        "Oh, hello. You've reached the next level.",
        "",
        "Three switches.",
        "Each one is either on or off.",
        "There's a hidden combination "
        "that unlocks the room. ",
        "Watch the lights,"
        "and figure out the right pattern.",
        "",
        "Click anywhere to begin."
    ]

    for idx, line in enumerate(lines):
        text_surface = small_font.render(line, True, WHITE)
        screen.blit(text_surface, (box_rect.x + 30, box_rect.y + 30 + idx * 30))


def draw_l3_intro_popup():
    dim = pygame.Surface((800, 600), pygame.SRCALPHA)
    dim.fill((0, 0, 0, 180))
    screen.blit(dim, (0, 0))

    box_rect = pygame.Rect(100, 150, 600, 340)
    pygame.draw.rect(screen, (40, 40, 40), box_rect, border_radius=15)
    pygame.draw.rect(screen, (200, 200, 200), box_rect, width=3, border_radius=15)

    lines = [
        "LEVEL 3",
        "",
        "The gun is gone. In its place, a beam that never",
        "moves - and a mirror that you do control.",
        "",
        "Left / Right to rotate the mirror onto the moths.",
        "",
        "Click anywhere to begin."
    ]

    for idx, line in enumerate(lines):
        text_surface = small_font.render(line, True, WHITE)
        screen.blit(text_surface, (box_rect.x + 30, box_rect.y + 30 + idx * 30))

def draw_level3_win_text():
    win_str = "LEVEL 3 COMPLETED"
    win_text = font.render(win_str, True, (255, 245, 220))

    # gentle pulse so it feels alive rather than static
    pulse = 0.75 + 0.25 * math.sin(pygame.time.get_ticks() * 0.004)

    card_w = win_text.get_width() + 80
    card_h = win_text.get_height() + 50
    card_rect = pygame.Rect(0, 0, card_w, card_h)
    card_rect.center = (400, 300)

    # warm glow behind the card, pulsing
    glow = pygame.Surface((card_w + 80, card_h + 80), pygame.SRCALPHA)
    glow_alpha = int(90 * pulse)
    pygame.draw.rect(glow, (255, 176, 59, glow_alpha), glow.get_rect(), border_radius=28)
    screen.blit(glow, (card_rect.x - 40, card_rect.y - 40))

    # dark card with warm accent border
    card = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
    pygame.draw.rect(card, (20, 18, 22, 235), card.get_rect(), border_radius=18)
    pygame.draw.rect(card, (255, 176, 59), card.get_rect(), width=2, border_radius=18)
    screen.blit(card, card_rect.topleft)

    win_text.set_alpha(int(255 * pulse))
    screen.blit(win_text, (card_rect.centerx - win_text.get_width() // 2, card_rect.centery - win_text.get_height() // 2))
    
def show_win_text():
    win_str = "LEVEL 2 COMPLETE"
    win_text = font.render(win_str, True, (235, 235, 235))

    card_w = win_text.get_width() + 60
    card_h = win_text.get_height() + 36
    card_rect = pygame.Rect(0, 0, card_w, card_h)
    card_rect.center = (400, 130)

    # soft glow behind the card
    glow = pygame.Surface((card_w + 40, card_h + 40), pygame.SRCALPHA)
    pygame.draw.rect(glow, (64, 214, 158, 60), glow.get_rect(), border_radius=20)
    screen.blit(glow, (card_rect.x - 20, card_rect.y - 20))

    card = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
    pygame.draw.rect(card, (24, 24, 28, 235), card.get_rect(), border_radius=14)
    pygame.draw.rect(card, (64, 214, 158), card.get_rect(), width=2, border_radius=14)
    screen.blit(card, card_rect.topleft)

    screen.blit(win_text, (card_rect.centerx - win_text.get_width() // 2, card_rect.centery - win_text.get_height() // 2))

level2_complete = False
def reset_game():
    global playerX, playerY, playerX_change
    global bulletX, bulletY, bullet_state
    global mothX, mothY, moth_alive
    global button_state, target_number, target_bits, level2_complete
    global level3_instance, game_state

    # Level 1 reset
    playerX = random.randint(0, 672)
    playerY = 480
    playerX_change = 0

    bulletX = 0
    bulletY = 480
    bullet_state = "ready"

    for i in range(no_of_moths):
        mothX[i] = moth_positions[i][0]
        mothY[i] = moth_positions[i][1]
        moth_alive[i] = True

    # Level 2 reset
    button_state = [0, 0, 0]
    target_number = random.randint(1, 7)
    target_bits = [int(x) for x in format(target_number, '03b')]
    level2_complete = False

    # Level 3 reset
    level3_instance = None

    game_state = "level1"

# Game loop- infinite loop that will keep the game running until the user closes it
running = True
while running:
    dt = clock.tick(60) / 1000.0
    screen.fill((0, 0, 0))
    screen.blit(background, (0, 0))

    if game_state == "level2" and not level2_complete:
        # keep it fully black while unsolved
        dark_overlay = pygame.Surface((800, 600))
        dark_overlay.fill((0, 0, 0))
        screen.blit(dark_overlay, (0, 0))
    elif game_state == "level2" and level2_complete:
        if level2_brightness < 255:
            level2_brightness += brighten_speed
        dark_overlay = pygame.Surface((800, 600), pygame.SRCALPHA)
        dark_overlay.fill((0, 0, 0, max(0, 255 - level2_brightness)))
        screen.blit(dark_overlay, (0, 0))
    

    for event in pygame.event.get():  # all the events that are happening in the game will be stored in the event variable
        if event.type == pygame.QUIT:  # if close button is pressed then the game will exit
            running = False

        if game_state == "level1_intro":
            if event.type == pygame.MOUSEBUTTONDOWN:
                game_state = "level1"

        elif game_state == "level1":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    playerX_change = -3
                if event.key == pygame.K_RIGHT:
                    playerX_change = 3
                if event.key == pygame.K_SPACE:
                    if bullet_state == "ready":
                        bulletX = playerX
                        fire_bullet(bulletX, bulletY)
                        laser_sound = mixer.Sound('laser.wav')  # load the laser sound
                        laser_sound.play()  # play the laser sound but not on loop

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    playerX_change = 0

        elif game_state == "level2_intro":
            if event.type == pygame.MOUSEBUTTONDOWN:
                game_state = "level2"

        elif game_state == "level2" and not level2_complete:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                for i in range(3):
                    rx, ry = red_centers[i]
                    gx, gy = green_centers[i]
                    if ((mx - rx) ** 2 + (my - ry) ** 2) ** 0.5 <= click_radius:
                        button_state[i] = 0
                        click_sound = mixer.Sound('click.wav')
                        click_sound.play()
                    elif ((mx - gx) ** 2 + (my - gy) ** 2) ** 0.5 <= click_radius:
                        button_state[i] = 1
                        click_sound = mixer.Sound('click.wav')
                        click_sound.play()

        elif game_state == "level3_intro":
            if event.type == pygame.MOUSEBUTTONDOWN:
                level3_instance = Level3()
                game_state = "level3"

        elif game_state == "level3" and level3_instance:
            level3_instance.handle_event(event)

    if game_state == "level1_intro":
        draw_l1_intro_popup()

    elif game_state == "level1":
        draw_lamp(lampX, lampY)

        # moth image
        for i in range(3):
            if moth_alive[i]:
                collision = isCollision(mothImg[i], mothX[i], mothY[i], bulletImg, bulletX+16, bulletY+10)
                if collision:
                    explosion_sound = mixer.Sound('explosion.wav')  # load the explosion sound
                    explosion_sound.play()  # play the explosion sound but not on loop
                    bulletY = 480  # reset the bullet position to the spaceship
                    bullet_state = "ready"  # change the state of the bullet to ready so that it can be fired again
                    mothX[i] = 2000
                    mothY[i] = 2000
                    moth_alive[i] = False
                    break
                draw_moth(mothX[i], mothY[i], i)

        playerX += playerX_change  # update the player position based on the change value
        if playerX <= 0:  # if the player goes beyond the left boundary of the screen
            playerX = 0  # set the player position to the left boundary
        elif playerX >= 672:  # if the player goes beyond the right boundary of the screen
            playerX = 672  # image is 128*128

        # Bullet movement
        if bulletY <= 0:  # if the bullet goes beyond the top boundary of the screen
            bulletY = 480  # reset the bullet position to the player position
            bullet_state = "ready"  # change the state of the bullet to ready so that it can be fired again
        if bullet_state == "fire":
            fire_bullet(bulletX, bulletY)
            bulletY -= bulletY_change  # move the bullet up the screen

        draw_player(playerX, playerY)

        if not any(moth_alive):
            game_state = "level2_intro"

    elif game_state == "level2_intro":
        draw_intro_popup()

    elif game_state == "level2":
        for i in range(3):
            draw_button(i)

        if button_state == target_bits:
            level2_complete = True
            show_win_text()
            pygame.display.update()
            pygame.time.delay(1200)
            game_state = "level3_intro"

    elif game_state == "level3_intro":
        draw_l3_intro_popup()

    elif game_state == "level3" and level3_instance:
        level3_instance.update(dt)
        level3_instance.draw(screen)

        if level3_instance.cleared:
            draw_level3_win_text()
            hint = small_font.render("click anywhere to play again", True, WHITE)
            screen.blit(hint, (400 - hint.get_width() // 2, 420))

            if event.type == pygame.MOUSEBUTTONDOWN:
                reset_game()
            else:
                level3_instance.handle_event(event)

    # to update the display window-game window
    pygame.display.update()

pygame.quit()