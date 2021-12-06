import pygame;

class UI:
  def __init__(self, surface):
    self.display_surface = surface;

    self.health_bar = pygame.image.load("./graphics/ui/health_bar.png").convert_alpha();
    self.health_bar_topleft = (54, 39);
    self.bar_max_width = 152;
    self.bar_height = 4;

    self.marble = pygame.image.load("./graphics/ui/marble.png").convert_alpha();
    self.marble_rect = self.marble.get_rect(topleft = (50, 61));
    self.font = pygame.font.Font("./graphics/ui/ARCADEPI.ttf", 30);

  def draw_health_bar(self, current, full):
    self.display_surface.blit(self.health_bar, (20, 10));
    current_health_ratio = current / full;
    current_bar_width = self.bar_max_width * current_health_ratio;
    health_bar_rect = pygame.Rect(self.health_bar_topleft, (current_bar_width, self.bar_height));
    pygame.draw.rect(self.display_surface, (255, 0, 0), health_bar_rect);

  def show_marbles(self, amount):
    self.display_surface.blit(self.marble, self.marble_rect);
    marlbe_amount_surf = self.font.render(str(amount), True, "#33323d");
    marble_amount_rect = marlbe_amount_surf.get_rect(midleft = (self.marble_rect.right + 4, self.marble_rect.centery));
    self.display_surface.blit(marlbe_amount_surf, marble_amount_rect);
