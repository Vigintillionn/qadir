import pygame;
from math import sin

from support import import_folder;


class Player(pygame.sprite.Sprite):
  def __init__(self, pos, surface, create_jump_particles, change_health):
    super().__init__();
    self.import_character_assets();
    self.frame_index = 0;
    self.animation_speed = 0.15;
    self.image = self.animations["idle"][self.frame_index];
    self.rect = self.image.get_rect(topleft = pos);

    self.import_dust_run_particles();
    self.dust_frame_index = 0;
    self.dust_animation_speed = 0.15;
    self.display_surface = surface;
    self.create_jump_particles = create_jump_particles;

    self.direction = pygame.math.Vector2(0, 0);
    self.speed = 8;
    self.gravity = 0.8;
    self.jump_speed = -16;
    self.collision_rect = pygame.Rect(self.rect.topleft, (50, self.rect.height));

    self.state = "idle";
    self.facing_right = True;
    self.on_ground = False;
    self.on_ceiling = False;
    self.on_left = False;
    self.on_right = False;

    self.change_health = change_health;
    self.invincible = False;
    self.invincible_dur = 500;
    self.hurt_time = 0;

  def import_character_assets(self):
    character_path = "./graphics/character/";
    self.animations = { "idle": [], "run": [], "jump": [], "fall": [] };
    
    for animation in self.animations.keys():
      full_path = character_path + animation;
      self.animations[animation] = import_folder(full_path);
    
  def import_dust_run_particles(self):
    self.dust_run_particles = import_folder("./graphics/character/dust_particles/run");

  def animate(self):
    animation = self.animations[self.state];

    self.frame_index += self.animation_speed;
    if self.frame_index >= len(animation):
      self.frame_index = 0;
    
    img = animation[int(self.frame_index)];
    if self.facing_right:
      self.image = img;
      self.rect.bottomleft = self.collision_rect.bottomleft;
    else:
      flipped_img = pygame.transform.flip(img, True, False);
      self.image = flipped_img;
      self.rect.bottomright = self.collision_rect.bottomright;

    if self.invincible:
      alpha = self.wave_value();
      self.image.set_alpha(alpha);
    else:
      self.image.set_alpha(255);

  def run_dust_animation(self):
    if self.state == "run" and self.on_ground:
      self.dust_frame_index += self.dust_animation_speed;
      if self.dust_frame_index >= len(self.dust_run_particles):
        self.dust_frame_index = 0;
      
      dust_particle = self.dust_run_particles[int(self.dust_frame_index)];

      if self.facing_right:
        pos = self.rect.bottomleft - pygame.math.Vector2(6, 10);
        self.display_surface.blit(dust_particle, pos);
      else:
        pos = self.rect.bottomright - pygame.math.Vector2(6, 10);
        self.display_surface.blit(pygame.transform.flip(dust_particle, True, False), pos);

  def get_input(self):
    keys = pygame.key.get_pressed();

    if keys[pygame.K_LEFT] or keys[pygame.K_a] or keys[pygame.K_q]:
      self.direction.x = -1;
      self.facing_right = False;
    elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
      self.direction.x = 1;
      self.facing_right = True;
    else:
      self.direction.x = 0;

    if keys[pygame.K_SPACE] and self.on_ground:
      self.jump();
    

  def get_state(self):
    if self.direction.y < 0:
      self.state = "jump";
    elif self.direction.y > 1:
      self.state = "fall";
    else:
      if self.direction.x != 0:
        self.state = "run";
      else:
        self.state = "idle";

  def apply_gravity(self):
    self.direction.y += self.gravity;
    self.collision_rect.y += self.direction.y;

  def jump(self):
    self.direction.y = self.jump_speed;

  def take_damage(self):
    if not self.invincible:
      self.change_health(-1);
      self.invincible = True;
      self.hurt_time = pygame.time.get_ticks();

  def invincible_timer(self):
    if self.invincible:
      if pygame.time.get_ticks() - self.hurt_time > self.invincible_dur:
        self.invincible = False;

  def wave_value(self):
    value = sin(pygame.time.get_ticks());
    if value >= 0: return 255;
    else: return 0;

  def update(self):
    self.get_input();
    self.get_state();
    self.animate();
    self.run_dust_animation();
    self.invincible_timer();
    self.wave_value();