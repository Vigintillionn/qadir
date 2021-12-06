import pygame, sys

from pygame.constants import K_KP_ENTER, K_SPACE
from overworld import Overworld
from settings import *;
from ui import UI;
from level import Level
from decoration import Sky

class Game:
  def __init__(self):
    self.max_level = 0;

    self.max_health = 3;
    self.curr_health = 3;
    self.marbles = 0;

    self.overworld = Overworld(0, self.max_level, WINDOW, self.create_level);
    self.state = "overworld";

    self.ui = UI(WINDOW);

  def create_level(self, curr_level):
    self.level = Level(curr_level, WINDOW, self.create_overworld, self.change_marbles, self.change_health, self.on_death);
    self.state = 'level';

  def create_overworld(self, curr_level, new_max_level):
    if new_max_level > self.max_level:
      self.max_level = new_max_level;
    self.curr_health = 3;
    self.overworld = Overworld(curr_level, self.max_level, WINDOW, self.create_level);
    self.state = "overworld";

  def change_marbles(self, amm):
    self.marbles += amm;

  def change_health(self, amm):
    self.curr_health += amm;
  
  def check_game_over(self):
    if self.curr_health <= 0:
      self.on_death(self.max_level);

  def on_death(self, curr_level):
    self.marbles = 0;
    self.max_level = curr_level;
    self.create_overworld(curr_level, curr_level);

  def run(self):
    if self.state == "overworld":
      self.overworld.run();
    else:
      self.level.run();
      self.ui.show_marbles(self.marbles);
      self.ui.draw_health_bar(self.curr_health, self.max_health);
      self.check_game_over();

class TitleScreen:
  def __init__(self):
    self.image = pygame.image.load("./graphics/title_screen.png");
    self.font = pygame.font.Font("./graphics/ui/ARCADEPI.ttf", 30);
    self.font_small = pygame.font.Font("./graphics/ui/ARCADEPI.ttf", 18);

  def show_title_screen(self):
    WINDOW.blit(self.image, (0, 0));

  def show_text(self):
    start_text = self.font.render("Druk ENTER om te starten!", True, "#967A72");
    start_rect = start_text.get_rect(midleft = (300, 500));
    WINDOW.blit(start_text, start_rect);

    start_text = self.font_small.render("Door Vigintillion", True, "#967A72");
    start_rect = start_text.get_rect(midleft = (450, 680));
    WINDOW.blit(start_text, start_rect);

  def run(self):
    self.show_title_screen();
    self.show_text();

pygame.init();

WINDOW = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT));
clock = pygame.time.Clock();
icon = pygame.image.load("./graphics/marbles/gold/0.png");
pygame.display.set_icon(icon);
pygame.display.set_caption("De vlucht van Qadir");

game = Game();
title_screen = TitleScreen();

def main():
  started = False;
  while True:
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pygame.quit();
        quit();
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_RETURN:
          if not started:
            started = True;

    WINDOW.fill((209, 170, 157));
    if not started:
      title_screen.run();
    else:
      game.run();

    pygame.display.update();


if __name__ == "__main__":
  main();