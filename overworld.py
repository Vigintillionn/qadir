import pygame
from support import import_folder
from decoration import Sky
from game_data import levels

class Node(pygame.sprite.Sprite):
  def __init__(self, pos, state, icon_speed, path):
    super().__init__();
    self.frames = import_folder(path);
    self.frame_index = 0;
    self.image = self.frames[self.frame_index];
    if state == "available":
      self.state = "available";
    else:
      self.state = "locked";
    self.rect = self.image.get_rect(center = pos);

    self.detection_zone = pygame.Rect(self.rect.centerx - (icon_speed / 2), self.rect.centery - (icon_speed / 2), icon_speed, icon_speed);

  def animate(self):
    self.frame_index += 0.15;
    if self.frame_index >= len(self.frames):
      self.frame_index = 0;
    self.image = self.frames[int(self.frame_index)];

  def update(self):
    if self.state == "available":
      self.animate();
    else:
      tint_surf = self.image.copy();
      tint_surf.fill((255, 255, 255, 100), None, pygame.BLEND_RGBA_MULT);
      self.image.blit(tint_surf, (0, 0));
  
class Icon(pygame.sprite.Sprite):
  def __init__(self, pos):
    super().__init__();
    self.pos = pos;
    self.image = pygame.image.load("./graphics/marbles/gold/0.png");
    self.rect = self.image.get_rect(center = pos);

  def update(self):
    self.rect.center = self.pos;

class Overworld:
  def __init__(self, start_level, max_level, surface, create_level):
    self.display_surface = surface;
    self.max_level = max_level;
    self.curr_level = int(start_level);
    self.create_level = create_level;

    self.font = pygame.font.Font("./graphics/ui/ARCADEPI.ttf", 30);

    self.moving = False;
    self.move_direction = pygame.math.Vector2(0, 0);
    self.speed = 8;

    self.setup_nodes();
    self.setup_icon();
    self.sky = Sky(8, "overworld");

    self.start_time = pygame.time.get_ticks();
    self.allow_input = False;
    self.timer_length = 300;

  def setup_nodes(self):
    self.nodes = pygame.sprite.Group();

    for i, node_data in enumerate(levels.values()):
      if i <= self.max_level:
        node_sprite = Node(node_data["node_pos"], "available", self.speed, node_data["node_graphics"]);
      else:
        node_sprite = Node(node_data["node_pos"], "locked", self.speed, node_data["node_graphics"]);
      self.nodes.add(node_sprite);

  def draw_paths(self):
    if self.max_level > 0:
      points = [node["node_pos"] for i, node in enumerate(levels.values()) if i <= self.max_level];
      pygame.draw.lines(self.display_surface, '#a04f45', False, points, 6);

  def setup_icon(self):
    self.icon = pygame.sprite.GroupSingle();
    self.icon.add(Icon(self.nodes.sprites()[self.curr_level].rect.center));

  def input(self):
    keys = pygame.key.get_pressed();

    if not self.moving and self.allow_input:
      if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.curr_level < self.max_level:
        self.move_direction = self.get_movement_data("next");
        self.curr_level += 1.
        self.moving = True;
      elif (keys[pygame.K_LEFT] or keys[pygame.K_a] or keys[pygame.K_q]) and self.curr_level > 0:
        self.move_direction = self.get_movement_data("prev");
        self.curr_level -= 1.
        self.moving = True;
      elif keys[pygame.K_SPACE]:
        self.create_level(self.curr_level);

  def create_country_name(self):
    country_names = ["Afghanistan", "Iran", "Turkije", "Griekenland", "Belgie"];
    level_data = list(levels.values());
    node_pos = level_data[int(self.curr_level)]["node_pos"];
    #Display the country name
    country_name = self.font.render(country_names[int(self.curr_level)], True, "#181425");
    country_rect = country_name.get_rect(center = (node_pos[0], node_pos[1] - 40));
    self.display_surface.blit(country_name, country_rect);



  def get_movement_data(self, direction):
    start = pygame.math.Vector2(self.nodes.sprites()[int(self.curr_level)].rect.center);

    if direction == "next":
      end = pygame.math.Vector2(self.nodes.sprites()[int(self.curr_level + 1)].rect.center);
    else:
      end = pygame.math.Vector2(self.nodes.sprites()[int(self.curr_level - 1)].rect.center);
    
    return (end - start).normalize();

  def update_icon_pos(self):
    if self.moving and self.move_direction:
      self.icon.sprite.pos += self.move_direction * self.speed;
      target_node = self.nodes.sprites()[int(self.curr_level)];
      if target_node.detection_zone.collidepoint(self.icon.sprite.pos):
        self.moving = False;
        self.move_direction = pygame.math.Vector2(0, 0);
  
  def input_timer(self):
    if not self.allow_input:
      current_time = pygame.time.get_ticks();
      if current_time - self.start_time >= self.timer_length:
        self.allow_input = True;

  def run(self):
    if self.curr_level > self.max_level:
      self.curr_level = self.max_level;
      self.update_icon_pos();
    else:
      self.input_timer();
      self.input();
      
    self.update_icon_pos();
    self.icon.update();
    self.nodes.update();

    self.sky.draw(self.display_surface);
    self.draw_paths();
    self.nodes.draw(self.display_surface);
    self.icon.draw(self.display_surface);
    self.create_country_name();
      