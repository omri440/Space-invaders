import pygame
import sys
import random
import time
# Initialize Pygame
pygame.init()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Set up the game window
window_width = 800
window_height = 600
window = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption('Space Shooter')
rect = pygame.Rect(25, 25, 25, 25)
# Load player image (spaceship)
player_image = pygame.image.load('spaceship.jpg')
player_image = pygame.transform.scale(player_image, (50, 50))  # Resize the image
image_part_player = player_image.subsurface(rect)

# Load enemy image (enemy spaceship)
enemy_image = pygame.image.load('enemy.jpg')
Boss_image = pygame.image.load('boss_enemy.jpg')
Boss_image_scale = pygame.transform.scale(Boss_image , (250, 250)) 
life_image = pygame.image.load('life_image.jpg')
explosion_image = pygame.image.load('explosion_transparent.png')
enemy_image = pygame.transform.scale(enemy_image, (50, 50))  # Resize the image
explosion_image_scale = pygame.transform.scale(explosion_image, (50, 50))  # Resize the image
life_image_scale = pygame.transform.scale(life_image, (50, 50))  # Resize the image
explosion_sound = pygame.mixer.Sound('explosion.wav')

# Player position and speed
player_x = window_width // 2 - player_image.get_width() // 2
player_y = window_height - player_image.get_height() - 10
player_speed_x = 0
player_speed_y = 0
speed = 5  # Speed of movement
game_active = True
game_over = False
bullets = []
enemies = []
lifes_images = []
explosions = []
Boss_list = []
enemy_spawn_timer = 0  # Timer to control enemy spawn frequency
explosion_spawn_timer = 0  # Timer to control enemy spawn frequency
score = 0
lifes = 3
last_boss_spawn_score = 0
# Set the frame rate
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 55)
font_Of_text = pygame.font.SysFont(None, 30)


def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect(center=(x, y))
    surface.blit(text_obj, text_rect)

# Bullet class
class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 7  # Speed of the bullet

    def move(self):
        self.y -= self.speed  # Move the bullet upward

    def draw(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y, 2, 6))  # Draw the bullet

# Enemy class
class Enemy:
    def __init__(self):
        self.x = random.randint(0, window_width - 50)  # Random x position
        self.y = -50  # Start above the top of the screen
        self.speed = 3  # Speed at which the enemy moves down

    def move(self):
        self.y += self.speed  # Move enemy down the screen

    def draw(self, window,Image):
        # Draw the enemy spaceship
        window.blit(Image, (self.x, self.y))


class Enemy_Boss(Enemy):
    def __init__(self):
        super().__init__()
        self.x = random.randint(0, window_width - 250)
        self.y = 0  # Start off-screen at the top
        self.health = 100
        self.speed = 5
        self.dir_x = random.choice([-1, 1])  # Random initial direction
        self.dir_y = 1  # Boss always starts moving down

    def move(self):
        # Move boss horizontally
        self.x += self.dir_x * self.speed
        # Move boss vertically
        self.y += self.dir_y * self.speed

        # Reverse direction when hitting the screen edges
        if self.x <= 0 or self.x >= window_width - 250:
            self.dir_x *= -1  # Reverse horizontal direction
        if self.y <= 0 or self.y >= window_height - 250:
            self.dir_y *= -1  # Reverse vertical direction

    def draw(self, window):
        window.blit(Boss_image_scale, (self.x, self.y))


class Explosion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.creation_time = time.time()

    def draw(self, window):
        window.blit(explosion_image_scale, (self.x, self.y))


# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if game_over:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    # Reset the game here
                    game_active = True
                    game_over = False
                    while enemies:
                        enemies.pop()
                    while bullets:
                        bullets.pop()
                    if Boss_list:
                        Boss_list.pop()
                    lifes = 3
                    score = 0  # Reset score

    # Get the keys that are being pressed
    keys = pygame.key.get_pressed()

    # Reset movement speed
    player_speed_x = 0
    player_speed_y = 0
    if game_active:
        # Fill the window with black color at the start of the game loop
        window.fill(WHITE)  # Ensure this happens before drawing text or game elements

        for i in range(lifes):
            window.blit(life_image_scale, (window_width - 50 - 50 * i, 0))
        
        # Draw text first
        draw_text(f"Score: {score}", font_Of_text, BLACK, window, 50, 50)  # Drawing the score

        # Handle movement based on arrow keys
        if keys[pygame.K_LEFT]:
            player_speed_x = -speed  # Move left
        if keys[pygame.K_RIGHT]:
            player_speed_x = speed  # Move right
        if keys[pygame.K_UP]:
            player_speed_y = -speed  # Move up
        if keys[pygame.K_DOWN]:
            player_speed_y = speed  # Move down

        # Update player position
        player_x += player_speed_x
        player_y += player_speed_y

        # Prevent the player from going off the screen (boundary check)
        if player_x < 0:
            player_x = 0
        if player_x > window_width - player_image.get_width():
            player_x = window_width - player_image.get_width()
        if player_y < 0:
            player_y = 0
        if player_y > window_height - player_image.get_height():
            player_y = window_height - player_image.get_height()

        # Fire bullet when spacebar is pressed
        if keys[pygame.K_SPACE]:
            bullet = Bullet(player_x + player_image.get_width() // 2 - 2, player_y)
            bullets.append(bullet)

        # Spawn enemies periodically
        enemy_spawn_timer += 1
        if enemy_spawn_timer > 60:  # Spawn an enemy every 60 frames (~1 second)
            enemies.append(Enemy())
            enemy_spawn_timer = 0

        # Boss spawn logic: spawn boss when score is multiple of 50 and no boss is present
        if score % 20 == 0 and score > 0 and not Boss_list and score > last_boss_spawn_score:
            Boss_list.append(Enemy_Boss())
            last_boss_spawn_score = score  # Update the last boss spawn score

        # Boss movement and collision logic
        if Boss_list:
            boss = Boss_list[0]
            boss.move()
            boss.draw(window)

            # Check for boss collision with bullets
            boss_rect = pygame.Rect(boss.x, boss.y, 250, 250)
            for bullet in bullets[:]:
                bullet_rect = pygame.Rect(bullet.x, bullet.y, 2, 6)
                if bullet_rect.colliderect(boss_rect):
                    bullets.remove(bullet)
                    boss.health -= 10  # Reduce boss health when hit
                    explosions.append(Explosion(boss.x, boss.y))
                    explosion_sound.play()

            # Remove boss when health is 0
            if boss.health <= 0:
                Boss_list.pop()  # Remove the defeated boss
                score += 50  # Bonus points for defeating the boss
            player_rect = pygame.Rect(player_x, player_y, 50, 50)
            if player_rect.colliderect(boss_rect):
                explosions.append(Explosion(boss.x, boss.y))
                explosion_sound.play()
                lifes = 0

        # Draw the player (spaceship)
        window.blit(player_image, (player_x, player_y))

        # Update and draw bullets, remove them when off-screen
        for bullet in bullets[:]:
            bullet.move()
            if bullet.y < 0:
                bullets.remove(bullet)
            else:
                bullet.draw(window)

        # Move and draw enemies, remove them when off-screen
        for enemy in enemies[:]:
            enemy.move()
            if enemy.y > window_height:
                enemies.remove(enemy)
            else:
                enemy.draw(window, enemy_image)

        # Check for bullet-enemy collisions
        for bullet in bullets[:]:
            for enemy in enemies[:]:
                bullet_rect = pygame.Rect(bullet.x, bullet.y, 2, 6)
                enemy_rect = pygame.Rect(enemy.x, enemy.y, 50, 50)
                if bullet_rect.colliderect(enemy_rect):
                    bullets.remove(bullet)
                    enemies.remove(enemy)
                    score += 5
                    explosions.append(Explosion(enemy.x, enemy.y))
                    explosion_sound.play()

        # Check for player-enemy collision
        player_rect = pygame.Rect(player_x, player_y, 50, 50)
        for enemy in enemies[:]:
            enemy_rect = pygame.Rect(enemy.x, enemy.y, 50, 50)
            if player_rect.colliderect(enemy_rect):
                lifes -= 1
                enemies.remove(enemy)
            if lifes <= 0:
                game_active = False
                game_over = True

        # Handle explosions (remove after 1 second)
        for explosion in explosions[:]:
            if time.time() - explosion.creation_time < 1:
                explosion.draw(window)
            else:
                explosions.remove(explosion)

    else:
        # Game over screen
        window.fill(WHITE)
        draw_text("YOU LOSE", font, BLACK, window, window_width // 2, window_height // 2 - 50)
        draw_text("Game end, for new game press A", font, BLACK, window, window_width // 2, window_height // 2 + 50)
        draw_text(f"Score: {score}", font, BLACK, window, window_width // 2, window_height // 2 + 100)

    pygame.display.update()

    # Control the frame rate
    clock.tick(60)  # 60 frames per second
