# Into the dead sky - shoot'em up scroller.
# author antifin 2011
# license WTFPLv2
#
# Simple top-down scroller shoot'em up game.
# An objective is to survive and not to let enemies go past bottom border.
# A couple of bonus types, lots of enemies, keyboard controls.
# Arrows - move. Space - shoot. Escape or Q - exit.

import pygame
import random
import math
import copy

from defs import *
import sprites
import controller
import objects

class Background:
	""" Represent a background with all its stars as self.stars. """

	def __init__(self, size, count):
		""" Creates a background for screen with _size_ and fills it with _count_ of stars. """
		self.width, self.height = size
		self.stars = [(random.randrange(self.width), random.randrange(self.height), (random.randrange(2) == 0)) for i in xrange(count)]

	def move_down(self, amount):
		""" Moves every star down with _amount_ of pixels. """
		new_stars = []
		for x, y, pattern in self.stars:
			if y + amount + sprites.DIGIT_PATTERN_SIZE[1] <= self.height:
				new_stars.append((x, y + amount, pattern))
			else:
				new_stars.append((random.randrange(self.width), 0, pattern))
		self.stars = new_stars

	def update(self, sec):
		""" Updates background for _sec_ seconds after the last call. """
		self.move_down(LEVEL_SPEED * sec)

class Label:
	""" Represents an on-screen label for any important game moments.
	Can also close the game after it is gone if there is need to. """

	def __init__(self, text, lifetime, close_after=False):
		self.close_after = close_after
		self.time_left = lifetime
		self.text = text
	
	def	is_alive(self):
		return self.time_left > 0

	def update(self, sec):
		if self.is_alive():
			self.time_left -= sec

class Painter:
	""" Do all the painting jobs whatsoever. """

	def draw_background(self, screen, background):
		""" Clears screen before rendering of background so it should be first in a queue. """
		screen.fill(BACK_COLOR)
		for x, y, pattern in background.stars:
			screen.blit(sprites.DIGIT_SPRITE[pattern], (x, y))
	
	def draw_label(self, screen, label):
		""" Draws a big label on the screen centered. """
		font = pygame.font.Font(None, FONT_SIZE)
		sprite = font.render(label.text, True, TEXT_COLOR)
		textpos = sprite.get_rect(centerx=screen.get_rect().centerx, centery=screen.get_rect().centery)
		screen.blit(sprite, textpos)

	def draw_healthbar(self, screen, player):
			rect = pygame.Rect(player.get_rect().left, player.get_rect().bottom, player.get_rect().width, player.get_rect().height / 4)
			rect.move_ip(0, rect.height)
			ind_rect = rect.inflate(-4, -4)
			ind_rect.width = ind_rect.width * player.health / player.max_health

			if player.health < player.max_health / 2:
				i = 255 * 2 * player.health / player.max_health
				color = (255, i, 0)
			else:
				i = 255 * 2 * (player.health - player.max_health / 2) / player.max_health
				color = (255 - i, 255, 0)
			pygame.draw.rect(screen, HEALTHBAR_COLOR, rect, 1)
			pygame.draw.rect(screen, color, ind_rect)
	
	def draw_object(self, screen, obj):
		if isinstance(obj.sprite, pygame.Surface):
			dest_rect = obj.sprite.get_rect()
			dest_rect.center = obj.pos
			screen.blit(obj.sprite, dest_rect)
		else:
			pygame.draw.circle(screen, obj.sprite, (int(obj.pos[0]), int(obj.pos[1])), int(obj.radius))

		if isinstance(obj, objects.PlayerShip) and obj.health < obj.max_health:
			self.draw_healthbar(screen, obj)

class Level:
	""" A main class that represents the whole level with all the objects. """

	def __init__(self, view_rect, length):
		""" Creates a new level with given length in seconds. """
		self.length = length
		self.player = objects.PlayerShip(sprites.PLAYER_SPRITE, view_rect.center, PLAYER_SIZE, controller.PlayerController(), PLAYER_RELOAD_TIME, PLAYER_HEALTH)
		self.objects = [self.player]

		random_x = lambda: random.randrange(ENEMY_SIZE, view_rect.width - ENEMY_SIZE)
		self.queue = []
		for i in xrange(ENEMY_GROUP_COUNT):
			move_temper = get_prob_cause({
				"PROB_SCOUT":    lambda: controller.ScoutMoveTemper(),
				"PROB_PENDULUM": lambda: controller.PendulumMoveTemper((random_x(), random_x())),
				"PROB_HUNTER":   lambda: controller.HunterMoveTemper(self.player),
				"PROB_PAWN":     lambda: controller.PawnMoveTemper()
				}, lambda: controller.PawnMoveTemper())

			shoot_temper = get_prob_cause({
				"PROB_SNIPER"  : lambda: controller.ShootTemper(3.0, 1),
				"PROB_GUNNER"  : lambda: controller.ShootTemper(3.0, 3),
				"PROB_NO_SHOOT": lambda: controller.ShootTemper(0.0, 0),
				}, lambda: controller.ShootTemper(0.0, 0))

			shift = get_prob_cause({
				"PROB_H_LINE":    lambda: (ENEMY_DISTANCE, 0),
				"PROB_BACKSLASH": lambda: (ENEMY_DISTANCE, ENEMY_DISTANCE),
				"PROB_SLASH":     lambda: (-ENEMY_DISTANCE, ENEMY_DISTANCE),
				"PROB_V_LINE":    lambda: (0, ENEMY_DISTANCE)
				}, lambda: (0, ENEMY_DISTANCE))
			group_size = random.randrange(0, ENEMY_GROUP_SIZE) + 1
			group_width  = shift[0] * (group_size - 1) + math.copysign(ENEMY_SIZE * 2, shift[0])
			group_height = shift[1] * (group_size - 1) + math.copysign(ENEMY_SIZE * 2, shift[1])

			# min(start_pos, start_pos + group_width) > 0
			# max(start_pos, start_pos + group_width) < view_rect.width
			start_pos_x = view_rect.centerx
			if 0 > group_width:
				start_pos_x = random.randrange(ENEMY_SIZE - group_width, view_rect.width - ENEMY_SIZE)
			if 0 < group_width:
				start_pos_x = random.randrange(ENEMY_SIZE, view_rect.width - group_width - ENEMY_SIZE)
			start_pos_y = self.length / 2
			if 0 < group_height:
				start_pos_y = random.randrange(view_rect.height / 2 - group_height, self.length - view_rect.height)
			if 0 > group_height:
				start_pos_y = random.randrange(view_rect.height / 2, self.length - view_rect.height - group_height)

			positions = [(start_pos_x + shift[0] * i, start_pos_y + shift[1] * i) for i in xrange(group_size)]

			for pos in positions:
				ai = controller.EnemyController(copy.copy(shoot_temper), copy.copy(move_temper))
				enemy = objects.EnemyShip(sprites.ENEMY_SPRITE, pos, ENEMY_SIZE, ai, ENEMY_RELOAD_TIME)
				self.queue.append(enemy)

		self.length += view_rect.height / 2

	def is_ended_up(self):
		return self.length <= 0

	def update(self, sec):
		if not self.is_ended_up():
			self.length -= LEVEL_SPEED * sec

			ready_objects = [o for o in self.queue if o.pos[1] > self.length]
			for o in ready_objects:
				o.pos = (o.pos[0], 0)
				self.queue.remove(o)
			self.objects.extend(ready_objects)

def main():
	pygame.init()
	pygame.mouse.set_visible(False)
	screen = pygame.display.set_mode(SCREEN_SIZE)
	painter = Painter()
	clock = pygame.time.Clock()

	background = Background(screen.get_size(), STAR_COUNT)
	label = Label(START_TEXT, TEXT_DELAY)
	level = Level(screen.get_rect(), LEVEL_LENGTH)

	pressed_keys = set()
	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return
			elif event.type == pygame.KEYDOWN:
				if event.key in [pygame.K_q, pygame.K_ESCAPE]:
					return
				elif event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_RIGHT, pygame.K_LEFT, pygame.K_SPACE]:
					pressed_keys |= set([event.key])
			elif event.type == pygame.KEYUP:
				if event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_RIGHT, pygame.K_LEFT, pygame.K_SPACE]:
					pressed_keys -= set([event.key])

		if pygame.K_UP in pressed_keys:
			if level.player.get_rect().top > screen.get_rect().top:
				level.player.controller.press_up()
		if pygame.K_DOWN in pressed_keys:
			if level.player.get_rect().bottom < screen.get_rect().bottom:
				level.player.controller.press_down()
		if pygame.K_RIGHT in pressed_keys:
			if level.player.get_rect().right < screen.get_rect().right:
				level.player.controller.press_right()
		if pygame.K_LEFT in pressed_keys:
			if level.player.get_rect().left > screen.get_rect().left:
				level.player.controller.press_left()
		if pygame.K_SPACE in pressed_keys:
			level.player.controller.press_shoot()

		sec = clock.tick() / 1000.0
		level.update(sec)
		background.update(sec)
		if label: label.update(sec)

		created_objects = reduce(lambda a, b: a + b,
				map(lambda o: o.collide([other for other in level.objects if other != o and objects_colliding(o, other)]), level.objects) +
				map(lambda o: o.update(sec), level.objects)
				)
		level.objects[0:0] = created_objects

		if not level.player.is_alive() and label == None:
			label = Label(LOSE_TEXT, TEXT_DELAY, close_after=True)

		level.objects = [o for o in level.objects if o.is_alive()]
		if [o for o in level.objects if isinstance(o, objects.EnemyShip) and o.get_rect().bottom > screen.get_rect().bottom]:
			level.player.health = 0
		level.objects = [o for o in level.objects if screen.get_rect().colliderect(o.get_rect())]

		if label and not label.is_alive():
			if label.close_after:
				return
			label = None
		if level.is_ended_up() and label == None:
			label = Label(WIN_TEXT, TEXT_DELAY, close_after=True)

		painter.draw_background(screen, background)
		for o in level.objects:
			painter.draw_object(screen, o)
		if label: painter.draw_label(screen, label)
		pygame.display.flip()


if __name__ == "__main__":
	main()
