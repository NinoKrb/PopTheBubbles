import pygame
import pygame.mixer
import os
import random
import glob
import time
import json


class Settings():
    window_height = 645
    window_width = 1080

    base_file = os.path.dirname(os.path.abspath(__file__))
    assets_folder = os.path.join(base_file, "assets")
    path_image = os.path.join(assets_folder, "images")
    path_font = os.path.join(assets_folder, "fonts")
    path_sounds = os.path.join(assets_folder, "sounds")
    score_file = os.path.join(base_file, "score.json")
    title = "PopTheBubbles - The Game"
    fps = 60
    scoreboard_count = 5

    plop_sound = 'plop_sound.wav'
    spawn_sound = 'spawn_sound.wav'
    crash_sound = 'crash_sound.wav'

    # Fade & Text delay
    points_label_margin = (100, 535)
    keybinds_label_margin = 535
    click_to_start_alpha_speed = 0.7
    gray_overlay_alpha = 75
    gray_overlay_color = (77, 77, 77)

    # Fonts
    font_type = "Pixellari.ttf"  # ChubbyChoo-Regular
    font_info_size = 22
    font_overlay_size = 30
    font_title_size = 50
    font_color_white = (255, 255, 255)
    font_color_blue = (70, 108, 255)
    font_color_overlay = (255, 229, 150)

    # Text
    text_game_over = "Game Over"
    text_pause = "Game Paused"
    text_welcome_to = "Welcome to"
    text_keybinds = "[m] Mute/Unmute Music | [+] Volume up | [-] Volume down"
    text_your_score = "Your Score: {}"
    text_your_play_time = "Your Playtime: {}"
    text_points = "{} Points"
    text_play_time = "{}s"
    text_scoreboard = "Scoreboard"
    text_scoreboard_item = "Playtime: {}s, Score: {}, Popped Bubbles: {}"
    text_scoreboard_empty = "There are no score entries available"

    # Bubble Settings
    bubble_size = (5, 5)
    bubble_grow_speed = (1, 4)
    bubble_grow_delay = 12.5
    max_grow_speed = 10
    bubble_spawn_delay = 60
    min_bubble_spawn_delay = 40
    bubble_border_distance = 10
    bubble_border_x = 118
    bubble_border_y = 150
    bubble_max_count = (window_height + window_width) / 100
    bubble_path = "bubbles/*.png"
    bubble_animation_frames = glob.glob(os.path.join(path_image, bubble_path))

    bubble_collide_ratio = 4
    # I have deliberately set the collide ratio higher here, because otherwise it could lead to almost impossible situations in the course of the game.

    # Images - Overlay Sprites
    logo_image = "PopTheBubbleLogo.png"
    click_to_start_image = "ClickToStart.png"

    # Images - Game Sprites
    background_image = "Background.png"
    bubble_image = "Bubble.png"

    # Cursor Settings
    cursor_size = (30, 30)
    cursor_image_click = "Cursor_click.png"
    cursor_image_hand = "Cursor_hand.png"


class Background(pygame.sprite.Sprite):
    def __init__(self, filename):
        super().__init__()
        self.image = pygame.image.load(os.path.join(
            Settings.path_image, filename)).convert()
        self.image = pygame.transform.scale(
            self.image, (Settings.window_width, Settings.window_height))

    def draw(self, screen):
        screen.blit(self.image, (0, 0))


class Bubble(pygame.sprite.Sprite):
    def __init__(self, filename):
        super().__init__()
        self.update_sprite(filename)
        self.rect = self.image.get_rect()
        self.grow_speed = random.randint(
            Settings.bubble_grow_speed[0], Settings.bubble_grow_speed[1])

        self.grow_speed = game.playtime // 2 * self.grow_speed * 0.1
        if self.grow_speed >= Settings.max_grow_speed:
            self.grow_speed = Settings.max_grow_speed
        elif self.grow_speed < 0.5:
            self.grow_speed = 0.5

        self.find_position()
        self.check_spawn_position()
        self.play_sound(Settings.spawn_sound, 1)

        self.grow_delay = 0
        self.death = False
        self.death_animation_count = 0
        self.scale = {'width': self.rect.width, 'height': self.rect.height}

    def play_sound(self, file, channel):
        self.sound = pygame.mixer.Sound(
            os.path.join(Settings.path_sounds, file))
        pygame.mixer.Channel(channel).play(self.sound)

    def stop_sound(self):
        if self.sound != None:
            pygame.mixer.Sound.stop(self.sound)

    # Find spawn position
    def find_position(self):
        self.rect.top = random.randrange(Settings.bubble_border_y + Settings.bubble_border_distance,
                                         Settings.window_height - Settings.bubble_border_y - self.rect.height - Settings.bubble_border_distance)
        self.rect.left = random.randrange(Settings.bubble_border_x + Settings.bubble_border_distance,
                                          Settings.window_width - Settings.bubble_border_x - self.rect.width - Settings.bubble_border_distance)

    # Check if spawn position is valid
    def check_spawn_position(self):
        for i in range(10):
            hits = pygame.sprite.spritecollide(
                self, game.bubbles, False, pygame.sprite.collide_circle_ratio(Settings.bubble_collide_ratio))
            if len(hits) > 0:
                self.find_position()
                continue
            else:
                game.new_bubbles.remove(self)
                game.bubbles.add(self)
                break

    def update(self):
        self.grow_delay += 1

        if self.grow_delay >= Settings.bubble_grow_delay:
            self.grow_delay = 0
            self.scale_up()

        self.set_center()

        self.check_collision()

    def update_sprite(self, filename):
        self.image = pygame.image.load(os.path.join(
            Settings.path_image, filename)).convert_alpha()
        self.image = self.original_image = pygame.transform.scale(
            self.image, (Settings.bubble_size[0], Settings.bubble_size[1]))

    # Scaling
    def scale_up(self):
        if self.rect.width < Settings.window_width:
            self.scale['width'] += self.grow_speed
            self.scale['height'] += self.grow_speed

    def get_scale(self):
        return (self.scale['width'], self.scale['height'])

    # Centering the Sprite
    def set_center(self):
        c = self.rect.center
        self.image = pygame.transform.scale(
            self.original_image, (self.get_scale()))
        self.rect = self.image.get_rect()
        self.rect.center = c

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    # Check for cursor interactions
    def check_interaction(self, event):
        if self.rect.collidepoint(event.pos):
            self.death = True
            game.popped_bubbles += 1

    def check_collision(self):
        if self.rect.top <= Settings.bubble_border_y or self.rect.left <= Settings.bubble_border_x or self.rect.right >= Settings.window_width - Settings.bubble_border_x or self.rect.bottom >= Settings.window_height - Settings.bubble_border_y:
            game.game_over = True
            game.end_timer()
            self.play_sound(Settings.crash_sound, 3)
            game.save_score()

        collisions = pygame.sprite.spritecollide(
            self, game.bubbles, False, pygame.sprite.collide_mask)
        for sprite in collisions:
            if sprite != self:
                game.game_over = True
                game.end_timer()
                self.play_sound(Settings.crash_sound, 3)
                game.save_score()

    # Check if Bubble is hitten, then play animation frame
    def check_plop_animation(self):
        if self.death == True:
            if self.death_animation_count >= len(Settings.bubble_animation_frames):
                self.play_sound(Settings.plop_sound, 2)
                game.stats_points += round(self.scale['width'] /
                                           Settings.bubble_size[0] * 1)
                self.kill()
                return

            self.update_sprite(Settings.bubble_animation_frames[self.death_animation_count].split(
                "/")[-2] + "/" + Settings.bubble_animation_frames[self.death_animation_count].split("/")[-1])
            self.set_center()
            self.death_animation_count += 1


class Cursor(pygame.sprite.Sprite):
    def __init__(self, filename):
        super().__init__()
        self.update_cursor(filename)
        self.rect = self.image.get_rect()

    # Set the custom cursor to the real cursor position
    def update(self):
        pygame.mouse.set_visible(False)
        pos = pygame.mouse.get_pos()
        self.rect.left = pos[0]
        self.rect.top = pos[1]

        # Check if cursor is in playground or outside => Change cursors appearance
        if self.rect.top <= Settings.bubble_border_y or self.rect.left <= Settings.bubble_border_x or self.rect.right >= Settings.window_width - Settings.bubble_border_x or self.rect.bottom >= Settings.window_height - Settings.bubble_border_y:
            self.update_cursor(Settings.cursor_image_click)
        elif len(pygame.sprite.spritecollide(self, game.bubbles, False, pygame.sprite.collide_mask)):
            self.update_cursor(Settings.cursor_image_click)
        else:
            self.update_cursor(Settings.cursor_image_hand)

    # Helper function to change the cursors image
    def update_cursor(self, filename):
        self.image = pygame.image.load(os.path.join(
            Settings.path_image, filename)).convert_alpha()
        self.image = pygame.transform.scale(self.image, Settings.cursor_size)

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Game():
    def __init__(self):
        super().__init__()
        # Game essential settings
        os.environ['SDL_VIDEO_WINDOW_POS'] = '1'
        pygame.init()
        pygame.display.set_caption(Settings.title)

        self.screen = pygame.display.set_mode(
            (Settings.window_width, Settings.window_height))
        self.fps = pygame.time.Clock()

        # Define Sprites & Spritegroups
        self.background = Background(Settings.background_image)
        self.bubbles = pygame.sprite.Group()
        self.new_bubbles = pygame.sprite.Group()

        self.cursor = Cursor(Settings.cursor_image_hand)

        # Set default game/menu values
        self.running = True
        self.pause_menu = False
        self.game_over = False
        self.game_started = True
        self.scoreboard = False

        # Set fonts for the game overlay
        self.font = pygame.font.Font(os.path.join(
            Settings.path_font, Settings.font_type), Settings.font_overlay_size)
        self.overlay_font = pygame.font.Font(os.path.join(
            Settings.path_font, Settings.font_type), Settings.font_title_size)
        self.info_font = pygame.font.Font(os.path.join(
            Settings.path_font, Settings.font_type), Settings.font_info_size)

        # Reset the game for a new session
        self.reset_game()

    # Main game loop
    def run(self):
        while self.running:
            self.fps.tick(Settings.fps)
            if self.game_over == False and self.pause_menu == False and self.game_started == False:
                self.update()
                self.spawn_bubbles()

            self.cursor.update()
            self.watch_for_events()
            self.draw()

    # Draw all sprites
    def draw(self):
        self.background.draw(self.screen)
        self.bubbles.draw(self.screen)
        self.new_bubbles.draw(self.screen)
        self.cursor.draw(self.screen)
        self.update_overlay()
        pygame.display.flip()

    def spawn_bubbles(self):
        self.bubble_counter += 1

        # Calculate spawnrate of bubbles
        new_bubble_spawn_delay = Settings.bubble_spawn_delay - self.playtime // 10
        if new_bubble_spawn_delay >= Settings.min_bubble_spawn_delay:
            self.bubble_spawn_delay = new_bubble_spawn_delay
        else:
            self.bubble_spawn_delay = Settings.min_bubble_spawn_delay

        if self.bubble_counter >= self.bubble_spawn_delay:
            self.bubble_counter = 0
            # Check if too many bubbles are already in => Spawn new bubble
            if len(self.bubbles) < Settings.bubble_max_count:
                self.new_bubbles.add(Bubble(Settings.bubble_image))

    def update_overlay(self):
        if self.game_over or self.pause_menu or self.game_started:
            # Gray Overlay
            pause_gray_overlay = pygame.Surface(
                (Settings.window_width, Settings.window_height))
            pause_gray_overlay.fill(Settings.gray_overlay_color)
            pause_gray_overlay.set_alpha(Settings.gray_overlay_alpha)
            self.screen.blit(pause_gray_overlay, (0, 0))

            # Set/Render Overlay title
            if self.scoreboard:
                header_text = Settings.text_scoreboard
            elif self.game_over:
                header_text = Settings.text_game_over
            elif self.pause_menu:
                header_text = Settings.text_pause
            elif self.game_started:
                header_text = Settings.text_welcome_to

            header_text = self.overlay_font.render(
                header_text, True, Settings.font_color_blue)
            self.screen.blit(header_text, (Settings.window_width //
                             2 - header_text.get_rect().centerx, 25))

            # Load Logo
            logo = pygame.image.load(os.path.join(
                Settings.path_image, Settings.logo_image)).convert_alpha()
            logo = pygame.transform.scale(logo, (604, 118))
            self.screen.blit(
                logo, ((Settings.window_width // 2 - logo.get_rect().centerx), 75))

            # Render scoreboard
            if self.scoreboard:
                item_count = 0
                scoreboard = self.load_scoreboard()
                if len(scoreboard) > 0:
                    for item in scoreboard[0:Settings.scoreboard_count]:
                        item_count += 1
                        scoreboard_item = self.font.render(Settings.text_scoreboard_item.format(
                            item['playtime'], item['score'], item['popped_bubbles']), True, Settings.font_color_white)
                        self.screen.blit(scoreboard_item, ((Settings.window_width // 2 - scoreboard_item.get_rect(
                        ).centerx), ((item_count + 1) * (scoreboard_item.get_rect().height + 10)) + logo.get_rect().bottom))
                else:
                    scoreboard_item = self.font.render(
                        Settings.text_scoreboard_empty, True, Settings.font_color_white)
                    self.screen.blit(scoreboard_item, ((Settings.window_width // 2 - scoreboard_item.get_rect(
                    ).centerx), ((2) * (scoreboard_item.get_rect().height + 10)) + logo.get_rect().bottom))

            else:
                # Gameover Stats
                if self.game_over or self.pause_menu:
                    # Score
                    score_text = self.font.render(Settings.text_your_score.format(
                        self.stats_points), True, Settings.font_color_white)
                    self.screen.blit(score_text, ((
                        Settings.window_width // 2 - score_text.get_rect().centerx), 75 + logo.get_rect().bottom))

                    # Playtime
                    play_time_text = self.font.render(Settings.text_play_time.format(
                        self.playtime), True, Settings.font_color_white)
                    self.screen.blit(play_time_text, ((
                        Settings.window_width // 2 - play_time_text.get_rect().centerx), 110 + logo.get_rect().bottom))

                if self.game_started or self.game_over:
                    # Loading "click to start" text
                    click_to_start = pygame.image.load(os.path.join(
                        Settings.path_image, Settings.click_to_start_image)).convert_alpha()
                    click_to_start = pygame.transform.scale(
                        click_to_start, (351, 85))

                    # Fade Animation for the "click to start" text
                    if self.alpha_counter >= 100:
                        self.alpha_direction = 0
                    elif self.alpha_counter <= 1:
                        self.alpha_direction = 1

                    if self.alpha_direction == 1:
                        self.alpha_counter += Settings.click_to_start_alpha_speed
                    else:
                        self.alpha_counter -= Settings.click_to_start_alpha_speed

                    click_to_start.set_alpha(self.alpha_counter)
                    self.screen.blit(click_to_start, (Settings.window_width // 2 -
                                     click_to_start.get_rect().centerx, Settings.window_height // 2))

            # Render Keybinds info
            keybinds_text = self.info_font.render(
                Settings.text_keybinds, True, Settings.font_color_overlay)
            self.screen.blit(keybinds_text, (Settings.window_width // 2 -
                             keybinds_text.get_rect().centerx, Settings.keybinds_label_margin))

        else:
            # Hud/Stats Rendering
            # Render Points
            points = self.font.render(Settings.text_points.format(
                self.stats_points), True, Settings.font_color_overlay)
            self.screen.blit(points, Settings.points_label_margin)

            # Render Playtime
            play_time = self.font.render(Settings.text_play_time.format(
                self.playtime), True, Settings.font_color_overlay)
            play_time_rect = play_time.get_rect()
            play_time_rect.right = Settings.window_width - \
                Settings.points_label_margin[0]
            play_time_rect.top = Settings.points_label_margin[1]
            self.screen.blit(play_time, play_time_rect)

    def update(self):
        self.bubbles.update()

        # Check for bubble death => Play animation frame
        for bubble in self.bubbles:
            bubble.check_plop_animation()

        # Calculate the current playtime
        self.playtime = int(
            round(time.time() - self.time - self.time_difference, 0))

    # Playtimer mechanic
    def start_timer(self):
        self.time = time.time()

    def pause_timer(self):
        self.pause_time = time.time()

    def play_timer(self):
        self.time_difference += time.time() - self.pause_time

    def end_timer(self):
        self.time_total = time.time() - self.time - self.time_difference

    # Reset the player stats
    def reset_stats(self):
        self.stats_points = 0
        self.alpha_counter = 0
        self.alpha_direction = 0
        self.bubble_counter = 0
        self.time = 0
        self.time_difference = 0
        self.time_total = 0
        self.playtime = 0
        self.popped_bubbles = 0
        self.pause_time = 0
        self.bubble_spawn_delay = Settings.bubble_spawn_delay

    def reset_game(self):
        self.reset_stats()
        self.bubbles.empty()
        self.new_bubbles.empty()
        self.game_over = False
        self.start_timer()

    # Load all stats from score file
    def load_scoreboard(self):
        file = open(Settings.score_file)
        data = json.load(file)['scores']
        return sorted(data, key=lambda x: x['score'], reverse=True)

    # Save players latest play score
    def save_score(self):
        file = open(Settings.score_file)
        data = json.load(file)

        data['scores'].append({
            "playtime": self.playtime,
            "score": self.stats_points,
            "popped_bubbles": self.popped_bubbles
        })

        with open(Settings.score_file, 'w') as outfile:
            json.dump(data, outfile)

    def stop_sounds(self):
        for bubble in self.bubbles:
            bubble.stop_sound()

    # Check all essential press events
    def watch_for_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # Check cursor collision
                    for bubble in self.bubbles:
                        bubble.check_interaction(event)

                    # Check for menus
                    if self.game_over == True:
                        self.reset_game()

                    elif self.pause_menu == True:
                        self.pause_menu = False
                        self.play_timer()

                    elif self.game_started == True:
                        self.game_started = False
                        self.start_timer()

                elif event.button == 3:
                    # Check for pause menu
                    if self.pause_menu == False and self.game_started == False and self.game_over == False:
                        self.pause_menu = True
                        self.pause_timer()
                        self.stop_sounds()

            if event.type == pygame.KEYDOWN:
                # Toggle pause menu
                if event.key == pygame.K_p:
                    if self.game_started == False and self.game_over == False:
                        self.pause_menu = not self.pause_menu
                        if self.pause_menu == True:
                            self.pause_timer()
                        else:
                            self.play_timer()
                            self.stop_sounds()

                # Toggle scoreboard
                if event.key == pygame.K_TAB:
                    if self.game_started == True or self.game_over == True or self.pause_menu == True:
                        self.scoreboard = not self.scoreboard

                # Close game
                if event.key == pygame.K_ESCAPE:
                    self.running = False


if __name__ == '__main__':
    game = Game()
    game.run()
