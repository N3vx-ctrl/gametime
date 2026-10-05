import math
import random
import pygame

# -----------------------------
# Game configuration
# -----------------------------
WIDTH, HEIGHT = 960, 600
FPS = 60

# Colors
BLACK = (10, 12, 20)
BLUE = (66, 135, 245)
CYAN = (73, 232, 255)
PINK = (255, 102, 178)
PURPLE = (150, 104, 255)
ORANGE = (255, 174, 66)
GREEN = (100, 255, 150)
WHITE = (240, 245, 255)
RED = (255, 80, 80)

# -----------------------------
# Utility functions
# -----------------------------
def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))


def distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def normalize(x, y):
    length = math.hypot(x, y)
    if length == 0:
        return 0, 0
    return x / length, y / length


# -----------------------------
# Particle effects
# -----------------------------
class Particle:
    def __init__(self, x, y, vx, vy, color, life, size):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.life = life
        self.max_life = life
        self.size = size

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vx *= 0.98
        self.vy *= 0.98
        self.life -= dt

    def draw(self, screen):
        alpha = max(0, self.life / self.max_life)
        surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*self.color, int(255 * alpha)), (self.size, self.size), self.size)
        screen.blit(surf, (self.x - self.size, self.y - self.size))


# -----------------------------
# Player ship
# -----------------------------
class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.radius = 18
        self.speed = 310
        self.velocity_x = 0
        self.velocity_y = 0
        self.shot_cooldown = 0
        self.invuln = 0
        self.score = 0
        self.lives = 3
        self.alive = True

    def update(self, dt, keys):
        if not self.alive:
            return

        move_x = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])
        move_y = (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_w] or keys[pygame.K_UP])

        if move_x != 0 or move_y != 0:
            nx, ny = normalize(move_x, move_y)
            self.velocity_x += nx * self.speed * 1.5 * dt
            self.velocity_y += ny * self.speed * 1.5 * dt

        friction = 0.90
        self.velocity_x *= friction
        self.velocity_y *= friction

        max_speed = self.speed
        self.velocity_x = clamp(self.velocity_x, -max_speed, max_speed)
        self.velocity_y = clamp(self.velocity_y, -max_speed, max_speed)

        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt

        self.x = clamp(self.x, self.radius, WIDTH - self.radius)
        self.y = clamp(self.y, self.radius, HEIGHT - self.radius)

        if self.invuln > 0:
            self.invuln -= dt

        if self.shot_cooldown > 0:
            self.shot_cooldown -= dt

    def shoot(self, bullets):
        if self.shot_cooldown > 0:
            return

        mouse_x, mouse_y = pygame.mouse.get_pos()
        dx = mouse_x - self.x
        dy = mouse_y - self.y
        if dx == 0 and dy == 0:
            dx, dy = 1, 0
        dir_x, dir_y = normalize(dx, dy)

        speed = 700
        bullets.append(Projectile(self.x + dir_x * 20, self.y + dir_y * 20, dir_x * speed, dir_y * speed, CYAN, 8))
        self.shot_cooldown = 0.18

    def draw(self, screen):
        if not self.alive:
            return

        glow = pygame.Surface((self.radius * 4, self.radius * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow, (73, 232, 255, 40), (self.radius * 2, self.radius * 2), self.radius * 2)
        screen.blit(glow, (self.x - self.radius * 2, self.y - self.radius * 2))

        angle = math.atan2(pygame.mouse.get_pos()[1] - self.y, pygame.mouse.get_pos()[0] - self.x)
        tip_x = self.x + math.cos(angle) * (self.radius + 16)
        tip_y = self.y + math.sin(angle) * (self.radius + 16)

        left_x = self.x + math.cos(angle + 2.5) * self.radius
        left_y = self.y + math.sin(angle + 2.5) * self.radius
        right_x = self.x + math.cos(angle - 2.5) * self.radius
        right_y = self.y + math.sin(angle - 2.5) * self.radius

        body_color = (255, 255, 255) if self.invuln <= 0 else (200, 200, 255)
        pygame.draw.polygon(screen, body_color, [(tip_x, tip_y), (left_x, left_y), (right_x, right_y)])
        pygame.draw.circle(screen, CYAN, (int(self.x), int(self.y)), 7)


# -----------------------------
# Enemy
# -----------------------------
class Enemy:
    def __init__(self):
        side = random.choice(["left", "right", "top", "bottom"])
        if side == "left":
            x = -30
            y = random.randint(0, HEIGHT)
        elif side == "right":
            x = WIDTH + 30
            y = random.randint(0, HEIGHT)
        elif side == "top":
            x = random.randint(0, WIDTH)
            y = -30
        else:
            x = random.randint(0, WIDTH)
            y = HEIGHT + 30

        self.x = x
        self.y = y
        self.radius = random.randint(12, 26)
        self.speed = random.uniform(80, 180)
        self.color = random.choice([PINK, PURPLE, ORANGE, RED, GREEN])
        self.spin = random.uniform(-2.5, 2.5)

    def update(self, dt, player):
        dx = player.x - self.x
        dy = player.y - self.y
        dist = max(1, math.hypot(dx, dy))
        self.x += (dx / dist) * self.speed * dt
        self.y += (dy / dist) * self.speed * dt

    def draw(self, screen):
        glow = pygame.Surface((self.radius * 4, self.radius * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*self.color, 40), (self.radius * 2, self.radius * 2), self.radius * 2)
        screen.blit(glow, (self.x - self.radius * 2, self.y - self.radius * 2))

        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, WHITE, (int(self.x - self.radius * 0.25), int(self.y - self.radius * 0.25)), 5)


# -----------------------------
# Projectile
# -----------------------------
class Projectile:
    def __init__(self, x, y, vx, vy, color, radius):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.radius = radius

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), max(2, self.radius // 3))


# -----------------------------
# Starfield background
# -----------------------------
class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.randint(1, 3)
        self.speed = random.uniform(20, 120)
        self.alpha = random.randint(100, 255)

    def update(self, dt):
        self.y += self.speed * dt
        if self.y > HEIGHT:
            self.y = -5
            self.x = random.randint(0, WIDTH)

    def draw(self, screen):
        color = (255, 255, 255, self.alpha)
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size)


# -----------------------------
# Game class
# -----------------------------
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("GAMETIME")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 30, bold=True)
        self.small_font = pygame.font.SysFont("arial", 18)
        self.running = True

        self.player = Player()
        self.enemies = []
        self.bullets = []
        self.particles = []
        self.stars = [Star() for _ in range(180)]
        self.spawn_timer = 0.8
        self.score = 0
        self.best_score = 0

    def create_particles(self, x, y, color, amount=12):
        for _ in range(amount):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(30, 150)
            self.particles.append(
                Particle(
                    x,
                    y,
                    math.cos(angle) * speed,
                    math.sin(angle) * speed,
                    color,
                    random.uniform(0.3, 0.8),
                    random.randint(2, 5),
                )
            )

    def spawn_enemy(self):
        self.enemies.append(Enemy())

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.player.shoot(self.bullets)

    def update(self, dt):
        keys = pygame.key.get_pressed()

        for star in self.stars:
            star.update(dt)

        self.player.update(dt, keys)
        if self.player.invuln > 0:
            self.player.invuln -= dt

        if keys[pygame.K_SPACE]:
            self.player.shoot(self.bullets)

        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            self.spawn_enemy()
            self.spawn_timer = max(0.25, 1.0 - self.score * 0.02)

        for bullet in self.bullets[:]:
            bullet.update(dt)
            if bullet.x < -20 or bullet.x > WIDTH + 20 or bullet.y < -20 or bullet.y > HEIGHT + 20:
                self.bullets.remove(bullet)
                continue

        for enemy in self.enemies[:]:
            enemy.update(dt, self.player)
            if distance((enemy.x, enemy.y), (self.player.x, self.player.y)) < enemy.radius + self.player.radius:
                if self.player.invuln <= 0:
                    self.player.lives -= 1
                    self.player.invuln = 1.5
                    self.create_particles(self.player.x, self.player.y, RED, 24)

                    if self.player.lives <= 0:
                        self.player.alive = False
                        self.best_score = max(self.best_score, self.score)
                        self.running = False
                        return

                    dx = self.player.x - enemy.x
                    dy = self.player.y - enemy.y
                    dist = max(1, math.hypot(dx, dy))
                    self.player.x = clamp(self.player.x + dx / dist * 40, self.player.radius, WIDTH - self.player.radius)
                    self.player.y = clamp(self.player.y + dy / dist * 40, self.player.radius, HEIGHT - self.player.radius)

                self.enemies.remove(enemy)
                continue

        for bullet in self.bullets[:]:
            for enemy in self.enemies[:]:
                if distance((bullet.x, bullet.y), (enemy.x, enemy.y)) < bullet.radius + enemy.radius:
                    self.bullets.remove(bullet)
                    self.enemies.remove(enemy)
                    self.create_particles(enemy.x, enemy.y, CYAN, 18)
                    self.score += 10
                    break

        for particle in self.particles[:]:
            particle.update(dt)
            if particle.life <= 0:
                self.particles.remove(particle)

        self.player.score = self.score

    def draw(self):
        self.screen.fill(BLACK)

        for y in range(0, HEIGHT, 4):
            alpha = int(20 + (y / HEIGHT) * 40)
            pygame.draw.line(self.screen, (10 + (y // 8) % 10, 12 + (y // 8) % 20, 25 + (y // 8) % 25, alpha), (0, y), (WIDTH, y))

        for star in self.stars:
            star.draw(self.screen)

        pulse = 180 + int(math.sin(pygame.time.get_ticks() * 0.004) * 40)
        glow = pygame.Surface((pulse, pulse), pygame.SRCALPHA)
        pygame.draw.circle(glow, (73, 232, 255, 18), (pulse // 2, pulse // 2), pulse // 2)
        self.screen.blit(glow, (WIDTH // 2 - pulse // 2, HEIGHT // 2 - pulse // 2))

        for enemy in self.enemies:
            enemy.draw(self.screen)

        for bullet in self.bullets:
            bullet.draw(self.screen)

        self.player.draw(self.screen)

        for particle in self.particles:
            particle.draw(self.screen)

        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (20, 20))

        lives_text = self.font.render(f"Lives: {self.player.lives}", True, GREEN)
        self.screen.blit(lives_text, (20, 60))

        best_text = self.small_font.render(f"Best: {self.best_score}", True, (200, 200, 255))
        self.screen.blit(best_text, (WIDTH - 150, 20))

        mx, my = pygame.mouse.get_pos()
        pygame.draw.line(self.screen, WHITE, (mx - 8, my), (mx + 8, my), 1)
        pygame.draw.line(self.screen, WHITE, (mx, my - 8), (mx, my + 8), 1)

        pygame.display.flip()

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()

        self.screen.fill(BLACK)
        over_font = pygame.font.SysFont("arial", 70, bold=True)
        small_font = pygame.font.SysFont("arial", 30)

        title = over_font.render("GAME OVER", True, RED)
        score = small_font.render(f"Final Score: {self.score}", True, WHITE)
        best = small_font.render(f"Best Score: {self.best_score}", True, CYAN)
        retry = small_font.render("Press any key to restart", True, WHITE)

        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 120))
        self.screen.blit(score, (WIDTH // 2 - score.get_width() // 2, HEIGHT // 2 - 30))
        self.screen.blit(best, (WIDTH // 2 - best.get_width() // 2, HEIGHT // 2 + 20))
        self.screen.blit(retry, (WIDTH // 2 - retry.get_width() // 2, HEIGHT // 2 + 80))
        pygame.display.flip()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False

        self.__init__()
        self.run()


if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()
