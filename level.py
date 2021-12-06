import pygame
from support import import_csv_layout, import_cut_graphics
from settings import *;
from tiles import Tile, StaticTile, Marble, Palm
from enemy import Enemy
from player import Player
from decoration import Sky, Water, Clouds
from particles import ParticleEffect
from game_data import levels

class Level:
  def __init__(self, curr_level, surface, create_overworld, change_marbles, change_health, on_death):
    self.display_surface = surface;
    self.world_shift = 0;
    self.current_x = None;

    self.create_overworld = create_overworld;
    self.curr_level = curr_level;
    level_data = levels[curr_level];
    self.new_max_level = level_data['unlock'];

    player_layout = import_csv_layout(level_data['player']);
    self.player = pygame.sprite.GroupSingle();
    self.goal = pygame.sprite.GroupSingle();
    self.player_setup(player_layout, change_health);

    self.change_marbles = change_marbles;

    self.dust_sprite = pygame.sprite.GroupSingle();
    self.player_on_ground = False;

    self.explosion_sprites = pygame.sprite.Group()

    self.on_death = on_death;

    # terrain
    terrain_layout = import_csv_layout(level_data['terrain']);
    self.terrain_sprites = self.create_tile_group(terrain_layout, 'terrain');

    # grass
    grass_layout = import_csv_layout(level_data['grass']);
    self.grass_sprites = self.create_tile_group(grass_layout, 'grass');

    # marbles
    marbles_layout = import_csv_layout(level_data['marbles']);
    self.marble_sprites = self.create_tile_group(marbles_layout, 'marbles');

    # fg palms
    fg_palms_layout = import_csv_layout(level_data['fg palms']);
    self.fg_palms_sprites = self.create_tile_group(fg_palms_layout, 'fg palms');

    # bg palms
    bg_palms_layout = import_csv_layout(level_data['bg palms']);
    self.bg_palms_sprites = self.create_tile_group(bg_palms_layout, 'bg palms');

    # enemies
    enemy_layout = import_csv_layout(level_data['enemies']);
    self.enemy_sprites = self.create_tile_group(enemy_layout, 'enemies');

    # constraints
    constraint_layout = import_csv_layout(level_data['constraints']);
    self.constraint_sprites = self.create_tile_group(constraint_layout, 'constraint');

    self.sky = Sky(8);
    level_width = len(terrain_layout[0]) * TILE_SIZE;
    self.water = Water(SCREEN_HEIGHT - 20, level_width);
    self.clouds = Clouds(400, level_width, 30);

  def create_tile_group(self, layout, type):
    sprites = pygame.sprite.Group();

    for row_ind, row in enumerate(layout):
      for col_ind, col in enumerate(row):
        if col != '-1':
          x = col_ind * TILE_SIZE;
          y = row_ind * TILE_SIZE;

          if type == 'terrain':
            terrain_tile_list = import_cut_graphics("./graphics/terrain/terrain_tiles.png");
            tile_surface = terrain_tile_list[int(col)];
            sprite = StaticTile(TILE_SIZE, x, y, tile_surface);
          
          if type == 'grass':
            grass_tile_list = import_cut_graphics("./graphics/decoration/grass/grass.png");
            tile_surface = grass_tile_list[int(col)];
            sprite = StaticTile(TILE_SIZE, x, y, tile_surface);

          if type == 'marbles':
            if col == '0': sprite = Marble(TILE_SIZE, x, y, "./graphics/marbles/gold", 5);
            if col == '1': sprite = Marble(TILE_SIZE, x, y, "./graphics/marbles/silver", 1);

          if type == 'fg palms':
            if col == '0': sprite = Palm(TILE_SIZE, x, y, "./graphics/terrain/palm_small", 38);
            if col == '1': sprite = Palm(TILE_SIZE, x, y, "./graphics/terrain/palm_large", 64);

          if type == 'bg palms':
            sprite = Palm(TILE_SIZE, x, y, "./graphics/terrain/palm_large", 64);
          
          if type == 'enemies':
            sprite = Enemy(TILE_SIZE, x, y);

          if type == 'constraint':
            sprite = Tile(TILE_SIZE, x, y);

          sprites.add(sprite);
    return sprites;

  def player_setup(self, layout, change_health):
    for row_ind, row in enumerate(layout):
      for col_ind, col in enumerate(row):
        x = col_ind * TILE_SIZE;
        y = row_ind * TILE_SIZE;
        if col == '0':
          sprite = Player((x, y), self.display_surface, self.create_jump_particles, change_health);
          self.player.add(sprite);
        if col == '1':
          goal_surface = pygame.image.load("./graphics/character/flag.png").convert_alpha();
          sprite = StaticTile(TILE_SIZE, x, y, goal_surface);
          self.goal.add(sprite);

  def enemy_collision_reverse(self):
    for enemy in self.enemy_sprites.sprites():
      if pygame.sprite.spritecollide(enemy,self.constraint_sprites, False):
        enemy.reverse();

  def create_jump_particles(self, pos):
    if self.player.sprite.facing_right:
      pos -= pygame.math.Vector2(10, 5);
    else:
      pos += pygame.math.Vector2(10, -5);
    jump_particle_sprite = ParticleEffect(pos, "jump");
    self.dust_sprite.add(jump_particle_sprite);

  def horizontal_movement_collision(self):
    player = self.player.sprite;
    player.collision_rect.x += player.direction.x * player.speed;
    collidable_sprites = self.terrain_sprites.sprites() + self.fg_palms_sprites.sprites();
    for sprite in collidable_sprites:
      if sprite.rect.colliderect(player.collision_rect):
        if player.direction.x < 0: 
          player.collision_rect.left = sprite.rect.right;
          player.on_left = True;
          self.current_x = player.rect.left;
        elif player.direction.x > 0:
          player.collision_rect.right = sprite.rect.left;
          player.on_right = True;
          self.current_x = player.rect.right;

  def vertical_movement_collision(self):
    player = self.player.sprite;
    player.apply_gravity();
    collidable_sprites = self.terrain_sprites.sprites() + self.fg_palms_sprites.sprites();

    for sprite in collidable_sprites:
      if sprite.rect.colliderect(player.collision_rect):
        if player.direction.y > 0: 
          player.collision_rect.bottom = sprite.rect.top;
          player.direction.y = 0;
          player.on_ground = True;
        elif player.direction.y < 0:
          player.collision_rect.top = sprite.rect.bottom;
          player.direction.y = 0;
          player.on_ceiling = True;
    if player.on_ground and player.direction.y < 0 or player.direction.y > 1:
      player.on_ground = False;

  def scroll_x(self):
    player = self.player.sprite;
    player_x = player.rect.centerx;
    direction_x = player.direction.x;
    
    if player_x < SCREEN_WIDTH / 4 and direction_x < 0:
      self.world_shift = 8;
      player.speed = 0;
    elif player_x > SCREEN_WIDTH - (SCREEN_WIDTH / 4) and direction_x > 0:
      self.world_shift = -8;
      player.speed = 0;
    else:
      self.world_shift = 0;
      player.speed = 8;
      
  def get_player_on_ground(self):
    if self.player.sprite.on_ground:
      self.player_on_ground = True;
    else:
      self.player_on_ground = False;

  def create_landing_dust(self):
    if not self.player_on_ground and self.player.sprite.on_ground and not self.dust_sprite.sprites():
      if self.player.sprite.facing_right:
        offset = pygame.math.Vector2(10, 15);
      else:
        offset = pygame.math.Vector2(-10, 15);
      fall_dust_particle = ParticleEffect(self.player.sprite.rect.midbottom - offset, 'land');
      self.dust_sprite.add(fall_dust_particle);

  def check_death(self):
    if self.player.sprite.rect.top > SCREEN_HEIGHT:
      # self.create_overworld(0, 0);
      self.on_death(self.curr_level);

  def check_win(self):
    if pygame.sprite.spritecollide(self.player.sprite, self.goal,False):
      self.create_overworld(self.curr_level, self.new_max_level);
			
  def check_marble_collisions(self):
    collided_marbles = pygame.sprite.spritecollide(self.player.sprite, self.marble_sprites,True);
    if collided_marbles:
      for marble in collided_marbles:
        self.change_marbles(marble.value);

  def check_enemy_collision(self):
    enemy_collisions = pygame.sprite.spritecollide(self.player.sprite, self.enemy_sprites, False);

    if enemy_collisions:
      for enemy in enemy_collisions:
        enemy_center = enemy.rect.centery;
        enemy_top = enemy.rect.top;
        player_bottom = self.player.sprite.rect.bottom;

        if enemy_top < player_bottom < enemy_center and self.player.sprite.direction.y >= 0:
          self.player.sprite.direction.y = -15;
          explosion_sprite = ParticleEffect(enemy.rect.center, 'explosion');
          self.explosion_sprites.add(explosion_sprite);
          enemy.kill();
        else:
          self.player.sprite.take_damage();

  def run(self):
    self.sky.draw(self.display_surface);
    self.clouds.draw(self.display_surface, self.world_shift);

    self.bg_palms_sprites.update(self.world_shift);
    self.bg_palms_sprites.draw(self.display_surface);

    self.dust_sprite.update(self.world_shift);
    self.dust_sprite.draw(self.display_surface);

    self.terrain_sprites.update(self.world_shift);
    self.terrain_sprites.draw(self.display_surface);

    self.enemy_sprites.update(self.world_shift);
    self.constraint_sprites.update(self.world_shift);
    self.enemy_collision_reverse();
    self.enemy_sprites.draw(self.display_surface);
    self.explosion_sprites.update(self.world_shift);
    self.explosion_sprites.draw(self.display_surface);

    self.grass_sprites.update(self.world_shift);
    self.grass_sprites.draw(self.display_surface);

    self.marble_sprites.update(self.world_shift);
    self.marble_sprites.draw(self.display_surface);

    self.fg_palms_sprites.update(self.world_shift);
    self.fg_palms_sprites.draw(self.display_surface);

    self.player.update();
    self.horizontal_movement_collision();
    
    self.get_player_on_ground();
    self.vertical_movement_collision();
    self.create_landing_dust();

    self.scroll_x();
    self.player.draw(self.display_surface);
    self.goal.update(self.world_shift);
    self.goal.draw(self.display_surface);

    self.check_death();
    self.check_win();

    self.check_marble_collisions();
    self.check_enemy_collision();

    self.water.draw(self.display_surface, self.world_shift);






