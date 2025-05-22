import pygame
import math
import sys
from pygame.locals import *

pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
BLACK   = (0, 0, 0)
WHITE   = (255, 255, 255)
BLUE    = (0, 0, 255)
RED     = (255, 0, 0)
GREEN   = (0, 255, 0)
YELLOW  = (255, 255, 0)
EARTH_RADIUS = 100         # Reduced Earth size
EARTH_CENTER = (WIDTH // 2, HEIGHT // 2)
G = 2500                   # Gravitational constant for player's dynamics
ISS_G = 20000              # Gravitational constant for ISS dynamics

# Standard starting parameters (working ok)
PLAYER_START_RADIUS = 110          # <-- Starting distance from Earth (modify as needed)
PLAYER_START_ANGLE = math.radians(45)  # <-- Starting angle in radians
PLAYER_START_SPEED = 15             # <-- Starting speed for the green spacecraft (modify here)
KEY_SENSITIVITY = 0.8              # <-- Input thrust sensitivity multiplier (modify here)

DOCKING_HOLD_TIME = 15.0            # <-- Time (in seconds) that conditions must be met for docking (modify here)

# NEW DOCKING PROXIMITY RADIUS CONSTANT:
DOCKING_PROXIMITY_RADIUS = 3      # <-- Maximum distance (in pixels) between ISS and spaceship for docking (modify here)

# Base class using mass-dependent update (for the player's spacecraft)
class SpaceObject:
    def __init__(self, x, y, vx, vy, mass, color, radius):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.mass = mass
        self.color = color
        self.radius = radius
        self.trail = []
        self.max_trail_length = 100
        
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        if len(self.trail) > 1:
            pygame.draw.lines(screen, self.color, False, self.trail, 1)
    
    def update(self, dt):
        # Physics update used by ISS; Player will override collision handling.
        dx = self.x - EARTH_CENTER[0]
        dy = self.y - EARTH_CENTER[1]
        distance = math.sqrt(dx*dx + dy*dy)
        angle = math.atan2(dy, dx)
        
        if distance > EARTH_RADIUS:
            force = self.mass * G / (distance*distance)
            self.vx -= math.cos(angle) * force * dt
            self.vy -= math.sin(angle) * force * dt
        
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        self.trail.append((int(self.x), int(self.y)))
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)
        
        # Collision handling for non-player objects:
        if distance < EARTH_RADIUS:
            self.x = EARTH_CENTER[0] + EARTH_RADIUS * 1.5 * math.cos(angle)
            self.y = EARTH_CENTER[1] + EARTH_RADIUS * 1.5 * math.sin(angle)
            self.vx = 0
            self.vy = 0

# Player class overrides update to detect crash rather than resetting to high orbit.
class Player(SpaceObject):
    def __init__(self, x, y):
        super().__init__(x, y, 0, 0, 10, GREEN, 5)
        self.thrust = 1.5  # Base thrust value
        self.fuel = 200
        self.docked = False
        self.docking_timer = 0  # Timer for how long docking conditions are met
       
    def apply_thrust(self, direction, dt):
        if self.fuel > 0:
            heading = self.get_heading()
            effective_thrust = self.thrust * KEY_SENSITIVITY  # <-- Adjust sensitivity here
            if direction == "forward":
                self.vx += math.cos(math.radians(heading)) * effective_thrust * dt
                self.vy += math.sin(math.radians(heading)) * effective_thrust * dt
            elif direction == "reverse":
                self.vx -= math.cos(math.radians(heading)) * effective_thrust * dt
                self.vy -= math.sin(math.radians(heading)) * effective_thrust * dt
            elif direction == "left":
                self.vx += math.cos(math.radians(heading + 90)) * effective_thrust * dt
                self.vy += math.sin(math.radians(heading + 90)) * effective_thrust * dt
            elif direction == "right":
                self.vx += math.cos(math.radians(heading - 90)) * effective_thrust * dt
                self.vy += math.sin(math.radians(heading - 90)) * effective_thrust * dt
            self.fuel -= 0.1
    
    def get_heading(self):
        if self.vx == 0 and self.vy == 0:
            return 0
        return math.degrees(math.atan2(self.vy, self.vx))
    
    def update(self, dt):
        # Override update to use physics without collision "rescue"
        dx = self.x - EARTH_CENTER[0]
        dy = self.y - EARTH_CENTER[1]
        distance = math.sqrt(dx*dx + dy*dy)
        angle = math.atan2(dy, dx)
        
        if distance > EARTH_RADIUS:
            force = self.mass * G / (distance*distance)
            self.vx -= math.cos(angle) * force * dt
            self.vy -= math.sin(angle) * force * dt
        
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        self.trail.append((int(self.x), int(self.y)))
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)
        
        # Instead of resetting, detect crash and signal it.
        if distance < EARTH_RADIUS:
            return "crashed"
        return None
    
    def draw(self, screen):
        super().draw(screen)
        heading = self.get_heading()
        nose_x = self.x + math.cos(math.radians(heading)) * 10
        nose_y = self.y + math.sin(math.radians(heading)) * 10
        pygame.draw.line(screen, WHITE, (self.x, self.y), (nose_x, nose_y), 2)

# ISS class using mass-independent update with ISS_G
class ISS(SpaceObject):
    def __init__(self, x, y, vx, vy):
        super().__init__(x, y, vx, vy, 1000, BLUE, 15)
        
    def update(self, dt):
        dx = self.x - EARTH_CENTER[0]
        dy = self.y - EARTH_CENTER[1]
        distance = math.sqrt(dx*dx + dy*dy)
        angle = math.atan2(dy, dx)
        
        if distance > EARTH_RADIUS:
            acceleration = ISS_G / (distance*distance)
            self.vx -= math.cos(angle) * acceleration * dt
            self.vy -= math.sin(angle) * acceleration * dt
        
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        self.trail.append((int(self.x), int(self.y)))
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)
        
        if distance < EARTH_RADIUS:
            self.x = EARTH_CENTER[0] + EARTH_RADIUS * 1.5 * math.cos(angle)
            self.y = EARTH_CENTER[1] + EARTH_RADIUS * 1.5 * math.sin(angle)
            self.vx = 0
            self.vy = 0
            
    def draw(self, screen):
        super().draw(screen)
        pygame.draw.rect(screen, WHITE, (self.x - 20, self.y - 5, 40, 10))
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), 8)

# Modified docking check function using DOCKING_PROXIMITY_RADIUS
def check_docking(player, station):
    dx = player.x - station.x
    dy = player.y - station.y
    distance = math.sqrt(dx*dx + dy*dy)
    
    dvx = player.vx - station.vx
    dvy = player.vy - station.vy
    rel_velocity = math.sqrt(dvx*dvx + dvy*dvy)
    
    # Use DOCKING_PROXIMITY_RADIUS for improved accuracy (highlighted)
    if distance < DOCKING_PROXIMITY_RADIUS and rel_velocity < 1.5:
        return True
    return False

def initialize_iss_orbit(center_x, center_y, radius, clockwise=True):
    angle = math.radians(45)
    x = center_x + radius * math.cos(angle)
    y = center_y + radius * math.sin(angle)
    v = math.sqrt(ISS_G / radius)
    if clockwise:
        vx = v * math.sin(angle)
        vy = -v * math.cos(angle)
    else:
        vx = -v * math.sin(angle)
        vy = v * math.cos(angle)
    return x, y, vx, vy

def initialize_player_position():
    x = EARTH_CENTER[0] + PLAYER_START_RADIUS * math.cos(PLAYER_START_ANGLE)
    y = EARTH_CENTER[1] + PLAYER_START_RADIUS * math.sin(PLAYER_START_ANGLE)
    vx = PLAYER_START_SPEED * math.sin(PLAYER_START_ANGLE)  # <-- PLAYER_START_SPEED is highlighted above.
    vy = -PLAYER_START_SPEED * math.cos(PLAYER_START_ANGLE)
    return x, y, vx, vy

def draw_orbit_prediction(screen, x, y, vx, vy, steps=100, dt=0.1):
    points = []
    temp_x, temp_y = x, y
    temp_vx, temp_vy = vx, vy
    
    for _ in range(steps):
        dx = temp_x - EARTH_CENTER[0]
        dy = temp_y - EARTH_CENTER[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > EARTH_RADIUS:
            angle = math.atan2(dy, dx)
            acceleration = ISS_G / (distance*distance)
            temp_vx -= math.cos(angle) * acceleration * dt
            temp_vy -= math.sin(angle) * acceleration * dt
            temp_x += temp_vx * dt
            temp_y += temp_vy * dt
            points.append((int(temp_x), int(temp_y)))
    
    if len(points) > 1:
        for i in range(0, len(points)-1, 2):
            if i+1 < len(points):
                pygame.draw.line(screen, (100,100,100), points[i], points[i+1], 1)

# Global variables for player, ISS, and launch flag
launched = False
player = None
iss = None

def reset_game(launch):
    global player, iss, launched
    # Reinitialize the player's starting position and state.
    start_x, start_y, start_vx, start_vy = initialize_player_position()
    player.x = start_x
    player.y = start_y
    player.vx = start_vx
    player.vy = start_vy
    player.fuel = 200
    player.docked = False
    player.docking_timer = 0
    player.trail = []
    # Optionally, reinitialize ISS if needed.
    # For now, we keep ISS running as is.
    launched = launch

def main():
    global player, iss, launched
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Orbital Mechanics Docking Simulator")
    font = pygame.font.SysFont(None, 24)
    
    # Initialize ISS using ISS_G dynamics
    station_radius = 200
    iss_x, iss_y, iss_vx, iss_vy = initialize_iss_orbit(EARTH_CENTER[0], EARTH_CENTER[1], station_radius, clockwise=True)
    iss = ISS(iss_x, iss_y, iss_vx, iss_vy)
    
    # Compute the player's starting position marker
    start_x, start_y, start_vx, start_vy = initialize_player_position()
    
    # Initially, the player is not launched
    launched = False
    player = Player(start_x, start_y)
    player.vx = start_vx
    player.vy = start_vy
    
    tutorial_tips = [
        "Welcome to Orbital Mechanics Simulator!",
        "Your spacecraft (green) needs to dock with the ISS (blue)",
        "Press W to thrust forward, S to thrust backward",
        "Press A and D to thrust sideways (perpendicular to motion)",
        "Thrust BACKWARDS (S key) to lower orbit and go faster",
        "Thrust FORWARDS (W key) to raise orbit and go slower",
        "The white line shows your direction of motion",
        "Press P to toggle orbit prediction, L to Launch, R to Restart",
        "Dock by matching the ISS orbit and approaching slowly"
    ]
    tip_index = 0
    tip_timer = 0
    mission_complete = False
    show_prediction = False
    clock = pygame.time.Clock()
    
    running = True
    while running:
        dt = 0.1
        
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                # Bind L for launch and R for restart (different behavior)
                if event.key == pygame.K_l:
                    reset_game(True)  # Launch the rocket
                elif event.key == pygame.K_r:
                    reset_game(False)  # Restart: keep the rocket unlaunched
                elif event.key == pygame.K_n:
                    tip_index = (tip_index + 1) % len(tutorial_tips)
                elif event.key == pygame.K_p:
                    show_prediction = not show_prediction
        
        keys = pygame.key.get_pressed()
        # Only update player controls if launched
        if launched and not player.docked:
            if keys[pygame.K_w]:
                player.apply_thrust("forward", dt)
            if keys[pygame.K_s]:
                player.apply_thrust("reverse", dt)
            if keys[pygame.K_a]:
                player.apply_thrust("left", dt)
            if keys[pygame.K_d]:
                player.apply_thrust("right", dt)
        
        # Always update ISS
        iss.update(dt)
        
        # Update player only if launched
        if launched and not player.docked:
            status = player.update(dt)
            if status == "crashed":
                reset_game(False)  # On crash, reset game (rocket unlaunched)
            if check_docking(player, iss):
                player.docking_timer += dt
            else:
                player.docking_timer = 0
            if player.docking_timer >= DOCKING_HOLD_TIME:
                player.docked = True
                mission_complete = True
                player.x = iss.x
                player.y = iss.y
                player.vx = iss.vx
                player.vy = iss.vy
        elif player.docked:
            player.x = iss.x
            player.y = iss.y
            player.vx = iss.vx
            player.vy = iss.vy
            iss.update(dt)
            player.update(0)
        
        screen.fill(BLACK)
        if show_prediction and launched and not player.docked:
            draw_orbit_prediction(screen, player.x, player.y, player.vx, player.vy)
        
        pygame.draw.circle(screen, BLUE, EARTH_CENTER, EARTH_RADIUS)
        iss.draw(screen)
        
        # If not launched, draw the launch marker at the start point
        if not launched:
            pygame.draw.circle(screen, RED, (int(start_x), int(start_y)), 5, 2)  # <-- Launch marker
        
        # Draw player only if launched
        if launched:
            player.draw(screen)
        
        speed_text = font.render(f"Speed: {math.sqrt(player.vx**2 + player.vy**2):.1f}", True, WHITE)
        fuel_text = font.render(f"Fuel: {max(0, int(player.fuel))}", True, WHITE)
        dx = player.x - EARTH_CENTER[0]
        dy = player.y - EARTH_CENTER[1]
        altitude = math.sqrt(dx*dx + dy*dy) - EARTH_RADIUS
        alt_text = font.render(f"Altitude: {int(altitude)}", True, WHITE)
        rel_vel = math.sqrt((player.vx - iss.vx)**2 + (player.vy - iss.vy)**2)
        rel_vel_text = font.render(f"Relative Velocity: {rel_vel:.1f}", True, WHITE)
        dist = math.sqrt((player.x - iss.x)**2 + (player.y - iss.y)**2)
        dist_text = font.render(f"Distance to ISS: {int(dist)}", True, WHITE)
        
        screen.blit(speed_text, (10, 10))
        screen.blit(fuel_text, (10, 40))
        screen.blit(alt_text, (10, 70))
        screen.blit(rel_vel_text, (10, 100))
        screen.blit(dist_text, (10, 130))
        
        controls_text = font.render("W/S: Forward/Back  A/D: Left/Right  P: Prediction  L: Launch  R: Restart", True, WHITE)
        screen.blit(controls_text, (WIDTH//2 - controls_text.get_width()//2, HEIGHT - 30))
        
        tip_timer += 1
        if tip_timer > 300:
            tip_index = (tip_index + 1) % len(tutorial_tips)
            tip_timer = 0
        tip_text = font.render(tutorial_tips[tip_index], True, YELLOW)
        screen.blit(tip_text, (WIDTH//2 - tip_text.get_width()//2, 20))
        
        if mission_complete:
            complete_text = font.render("Mission Complete! Docked with ISS", True, GREEN)
            screen.blit(complete_text, (WIDTH//2 - complete_text.get_width()//2, 50))
            launch_text = font.render("Press R to restart", True, WHITE)
            screen.blit(launch_text, (WIDTH//2 - launch_text.get_width()//2, 80))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
