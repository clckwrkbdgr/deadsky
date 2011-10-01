# Into the dead sky - shoot'em up scroller.
# version 0.9.1.1
# author antifin 2011
# license WTFPLv2
#
# Simple top-down scroller shoot'em up game.
# An objective is to survive and not to let enemies go past bottom border.
# A couple of bonus types, lots of enemies, keyboard controls.
# Arrows - move. Space - shoot. Escape or Q - exit.

import pygame
import math
import random
import copy

HEALTHBAR_COLOR = (255, 255, 255)
SCREEN_SIZE = (800, 600)
STAR_COUNT = 500
STAR_COLOR = (255, 255, 255)
BACK_COLOR = (0, 0, 0)
TEXT_COLOR = (255, 255, 255)
START_TEXT = "Get ready!"
WIN_TEXT = "You have passed!"
LOSE_TEXT = "Fail."
TEXT_DELAY = 3 # seconds
PLAYER_SIZE = 32
BULLET_SIZE = 16
BONUS_SIZE = 32
ENEMY_SIZE = 32
EXPLODE_SIZE = 48

LEVEL_SPEED = 50 # pixels per sec
PLAYER_SPEED = 400.0 # pixels per sec
PLAYER_RELOAD_TIME = 0.5 # seconds to reload
PLAYER_HEALTH = 100 # hit points
PLAYER_BULLET_VELOCITY = (0.0, -300.0) # pixels per sec
PLAYER_AUX_LEFT_BULLET_VELOCITY = (-212.0, -212.0) # pixels per sec
PLAYER_AUX_RIGHT_BULLET_VELOCITY = (212.0, -212.0) # pixels per sec
PLAYER_SIDE_LEFT_BULLET_VELOCITY = (-300.0, 0.0) # pixels per sec
PLAYER_SIDE_RIGHT_BULLET_VELOCITY = (300.0, 0.0) # pixels per sec
HEALTH_IMPROVEMENT = 25 # hit points
ENEMY_RELOAD_TIME = 0.5 # seconds to reload
ENEMY_SPEED = 50
ENEMY_BULLET_VELOCITY = (0.0, 300.0) # pixels per sec
COLLISION_DAMAGE = 10 # hit points per collision
EXPLODE_DELAY = 1.5 # seconds
LEVEL_LENGTH = 4000 # pixels
ENEMY_GROUP_COUNT = 40
ENEMY_GROUP_SIZE = 10
ENEMY_DISTANCE = 48

PROB_CREATE_WEAPON_BONUS = 0.25
PROB_CREATE_HEALTH_BONUS = 0.25

PROB_SCOUT = 0.25
PROB_PENDULUM = 0.25
PROB_HUNTER = 0.25
PROB_PAWN = 0.25

PROB_NO_SHOOT = 0.33
PROB_SNIPER = 0.33
PROB_GUNNER = 0.33

PROB_H_LINE = 0.25
PROB_V_LINE = 0.25
PROB_SLASH = 0.25
PROB_BACKSLASH = 0.25


def player_sprite():
	sprite = pygame.Surface((16, 16), pygame.HWSURFACE)
	sprite.fill((255, 0, 255))
	sprite.set_colorkey((255, 0, 255))
	pixels = pygame.PixelArray(sprite)

	for p in [(0, 9), (1, 7), (3, 6), (5, 4), (6, 2), (6, 13), (5, 14)]:
		pixels[p[0]][p[1]] = 0x303030

	l = [(0, 8), (2, 7), (4, 6), (5, 5), (6, 3)]
	l.extend([(1 + x, 10 + x) for x in range(4)])
	for p in l: pixels[p[0]][p[1]] = 0x5c5c5c

	l = [(1+x, 9+x) for x in range(5)]
	l.extend([(6, 5), (6, 4), (7, 2), (7, 1)])
	l.extend([(2+x*2, 8-x) for x in range(3)])
	l.extend([(1+x*2, 8-x) for x in range(3)])
	for p in l: pixels[p[0]][p[1]] = 0x808080

	for p in [(3, 8), (5, 7), (6, 6), (7, 10), (7, 12)]: pixels[p[0]][p[1]] = 0xa0a0a0

	l = [(3+x,9+x) for x in range(3)]
	l.extend([(4+x,9+x) for x in range(3)])
	l.extend([(7, 6), (7, 7), (6, 8), (7, 9)])
	for p in l: pixels[p[0]][p[1]] = 0xc0c0c0

	for p in [(6, 7), (7, 8)]: pixels[p[0]][p[1]] = 0x0000ff

	l = [(7,3+x) for x in range(3)]
	l.extend([(4+x,8+x) for x in range(4)])
	l.extend([(2+x,9+x) for x in range(4)])
	l.extend([(5,8), (6,9), (2,10), (3,11), (6,12)])
	for p in l: pixels[p[0]][p[1]] = 0x0000ff

	for x in range(8):
		pixels[15 - x] = pixels[x]

	return sprite


def player_bullet_sprite():
	sprite = pygame.Surface((8, 8), pygame.HWSURFACE)
	sprite.fill((255, 0, 255))
	sprite.set_colorkey((255, 0, 255))
	pixels = pygame.PixelArray(sprite)

	l = [(x,0) for x in range(3)]
	l.extend([(0,x) for x in range(3)])
	for p in l:
		pixels[p[0]][p[1]] = 0xff00ff

	for p in [(1+x, 2-x) for x in range(2)]:
		pixels[p[0]][p[1]] = 0x0055ff

	for p in [(x+1, 3-x) for x in range(3)]:
		pixels[p[0]][p[1]] = 0x00aaff

	for p in [(x+2, 3-x) for x in range(2)]:
		pixels[p[0]][p[1]] = 0x00ffff

	pixels[3][3] = 0xaaffff

	pixels[0][0] = 0xff00ff

	for x in range(4):
		for y in range(4):
			pixels[7 - x][y] = pixels[x][y]
			pixels[7 - x][7 - y] = pixels[x][y]
			pixels[x][7 - y] = pixels[x][y]

	return sprite


def enemy_bullet_sprite():
	sprite = pygame.Surface((8, 8), pygame.HWSURFACE)
	sprite.fill((255, 0, 255))
	sprite.set_colorkey((255, 0, 255))
	pixels = pygame.PixelArray(sprite)

	l = [(x,0) for x in range(3)]
	l.extend([(0,x) for x in range(3)])
	for p in l:
		pixels[p[0]][p[1]] = 0x550000

	for p in [(1, 1), (3, 0), (0, 3)]:
		pixels[p[0]][p[1]] = 0x810000

	for p in [(x+1, 2-x) for x in range(2)]:
		pixels[p[0]][p[1]] = 0xaa0000

	for p in [(x+1, 3) for x in range(3)]:
		pixels[p[0]][p[1]] = 0xf06666

	for p in [(x+2, 3-x*2) for x in range(2)]:
		pixels[p[0]][p[1]] = 0xff0000

	for p in [(x+2, 2) for x in range(2)]:
		pixels[p[0]][p[1]] = 0xff8585

	pixels[0][0] = 0xff00ff

	for x in range(4):
		for y in range(4):
			pixels[7 - x][y] = pixels[y][x]
			pixels[7 - x][7 - y] = pixels[x][y]
			pixels[x][7 - y] = pixels[y][x]

	return sprite


def enemy_sprite():
	sprite = pygame.Surface((16, 16), pygame.HWSURFACE)
	sprite.fill((255, 0, 255))
	sprite.set_colorkey((255, 0, 255))
	pixels = pygame.PixelArray(sprite)

	l = [(3,7), (5,5), (6,7), (5,8), (6,9), (4,15)]
	for x in range(3):
		l.extend([(x,6+x*3), (x,7+x*3), (x+1,6+x*3)])
	l.extend([(x, 5-x) for x in range(6)])
	for p in l: pixels[p[0]][p[1]] = 0xd80000

	for p in [(5,0), (3,1), (2, 2), (1,3), (0,5), (0,8), (1,11), (2,14), (3,15), (4,14), (3,11), (3,8), (4,6), (6,5)]:
		pixels[p[0]][p[1]] = 0xaa0000

	l = [(2,11), (3,14), (7,3)]
	l.extend([(2+x, 6-x) for x in range(5)])
	for p in l: pixels[p[0]][p[1]] = 0xff6565

	for p in [(3,4), (4,3), (6,3), (7,2)]:
		pixels[p[0]][p[1]] = 0xffa0a0

	for p in [(5,0), (3,1), (2, 2), (1,3), (0,5), (0,8), (1,11), (2,14), (3,15), (4,14), (3,11), (3,8), (4,6), (6,5)]:
		pixels[p[0]][p[1]] = 0xaa0000

	for x in range(8):
		pixels[15 - x] = pixels[x]

	return sprite


def explode_sprite():
	sprite = pygame.Surface((24, 24), pygame.HWSURFACE)
	sprite.fill((255, 0, 255))
	sprite.set_colorkey((255, 0, 255))
	pixels = pygame.PixelArray(sprite)

	for i in range(300):
		x = random.randrange(24)
		y = random.randrange(24)
		if math.hypot(x-12, y-12) > 12:
			continue
		r = random.randrange(128)
		pixels[x][y] = (r, r, r)

	return sprite


def health_bonus_sprite():
	sprite = pygame.Surface((16, 16), pygame.HWSURFACE)
	sprite.fill((255, 0, 255))
	sprite.set_colorkey((255, 0, 255))
	pixels = pygame.PixelArray(sprite)

	colors = [0x00aa00, 0x00ff00, 0x00c800]

	for i in reversed(range(3)):
		l = [(i+x,8-x*2) for x in range(4)]
		l.extend([(i+x,7-x*2) for x in range(4)])
		l.extend([(4+i+x,0+i) for x in range(5-i)])
		for p in l:
			pixels[p[0]][p[1]] = colors[i]

		for p in [(5+i, 7), (7, 5+i)]:
			pixels[p[0]][p[1]] = colors[i]
		
	for x in range(8):
		for y in range(8):
			pixels[15 - x][y] = pixels[x][y]
			pixels[15 - x][15 - y] = pixels[x][y]
			pixels[x][15 - y] = pixels[x][y]

	return sprite


def weapon_bonus_sprite():
	sprite = pygame.Surface((16, 16), pygame.HWSURFACE)
	sprite.fill((255, 0, 255))
	sprite.set_colorkey((255, 0, 255))
	pixels = pygame.PixelArray(sprite)

	colors = [0xffaa00, 0xffff00, 0xffc800]

	for i in reversed(range(3)):
		l = [(i+x,8-x*2) for x in range(4)]
		l.extend([(i+x,7-x*2) for x in range(4)])
		l.extend([(4+i+x,0+i) for x in range(5-i)])
		for p in l:
			pixels[p[0]][p[1]] = colors[i]

	for x in range(8):
		for y in range(8):
			pixels[15 - x][y] = pixels[x][y]
			pixels[15 - x][15 - y] = pixels[x][y]
			pixels[x][15 - y] = pixels[x][y]

	for j in range(3):
		for i in range(3-j):
			pixels[5+i+j][9-j*2] = colors[i]
			pixels[10-i-j][9-j*2] = colors[i]
			pixels[5+i+j][9-j*2-1] = colors[i]
			pixels[10-i-j][9-j*2-1] = colors[i]
	
	pixels[5+0+2][9-2*2-1] = (255, 0, 255)
	pixels[10-0-2][9-2*2-1] = (255, 0, 255)

	return sprite


PLAYER_SPRITE = pygame.transform.scale(player_sprite(), (PLAYER_SIZE * 2, PLAYER_SIZE * 2))
PLAYER_BULLET_SPRITE = pygame.transform.scale(player_bullet_sprite(), (BULLET_SIZE * 2, BULLET_SIZE * 2))
ENEMY_BULLET_SPRITE = pygame.transform.scale(enemy_bullet_sprite(), (BULLET_SIZE * 2, BULLET_SIZE * 2))
ENEMY_SPRITE = pygame.transform.scale(enemy_sprite(), (ENEMY_SIZE * 2, ENEMY_SIZE * 2))
EXPLODE_SPRITE = pygame.transform.scale(explode_sprite(), (EXPLODE_SIZE * 2, EXPLODE_SIZE * 2))
HEALTH_BONUS_SPRITE = pygame.transform.scale(health_bonus_sprite(), (BONUS_SIZE * 2, BONUS_SIZE * 2))
WEAPON_BONUS_SPRITE = pygame.transform.scale(weapon_bonus_sprite(), (BONUS_SIZE * 2, BONUS_SIZE * 2))


class Background:
	""" Represent a background with all its stars as self.stars. """

	def __init__(self, size, count):
		""" Creates a background for screen with _size_ and fills it with _count_ of stars. """
		self.width, self.height = size
		self.stars = [(random.randrange(self.width), random.randrange(self.height)) for i in xrange(count)]

	def move_down(self, amount):
		""" Moves every star down with _amount_ of pixels. """
		new_stars = []
		for star in self.stars:
			if star[1] + amount <= self.height:
				new_stars.append((star[0], star[1] + amount))
			else:
				new_stars.append([random.randrange(self.width), 0])
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


class Object:
	""" A base class for all game objects. """

	def __init__(self, sprite, pos, radius):
		self.sprite = sprite
		self.pos = pos
		self.radius = radius

	def get_rect(self):
		return pygame.Rect(int(self.pos[0] - self.radius), int(self.pos[1] - self.radius),
				int(self.radius * 2), int(self.radius * 2))

	def is_alive(self):
		""" Default behavior is always return True: base object simply don't die. """
		return True

	def move(self, shift):
		self.pos = (self.pos[0] + shift[0], self.pos[1] + shift[1])

	def collide(self, other):
		""" Process colliding with other objects.
		Base implementation does nothing. """
		return []

	def update(self, sec):
		""" Must return all object it creates (like explode or bullet etc.).
		Any successor class should invoke this implementation as super(). """
		return []


class Explode(Object):
	""" Appears after death of any ship. """

	def __init__(self, sprite, pos, radius, delay):
		Object.__init__(self, sprite, pos, radius)
		self.delay = delay

	def is_alive(self):
		""" Stays still until vanished. """
		return (self.delay > 0)

	def update(self, sec):
		if self.is_alive():
			self.delay -= sec
		return []


class Bonus(Object):
	""" Base bonus class. Just moves and collides with player. """

	def __init__(self, sprite, pos, radius):
		Object.__init__(self, sprite, pos, radius)
		self.exists = True
	
	def is_alive(self):
		return self.exists

	def update(self, sec):
		self.move((0, LEVEL_SPEED * sec))
		return Object.update(self, sec)

	def collide(self, collidees):
		for other in collidees:
			if isinstance(other, PlayerShip):
				self.exists = False
		return []


class WeaponBonus(Bonus): pass
class HealthBonus(Bonus): pass


class Controller:
	""" A base controller for ships. """

	def __init__(self):
		self.reset()

	def shoot(self):
		""" Tells controller that a shot have been done. """
		self.shooting = False
	
	def reset(self):
		self.shift = (0, 0)
		self.shooting = False

	def update(self, sec):
		pass


class PlayerController(Controller):
	""" A controller for the player ship. It uses keyboard. """

	def press_up(self):
		self.shift = (self.shift[0], self.shift[1] - PLAYER_SPEED)

	def press_down(self):
		self.shift = (self.shift[0], self.shift[1] + PLAYER_SPEED)

	def press_left(self):
		self.shift = (self.shift[0] - PLAYER_SPEED, self.shift[1])

	def press_right(self):
		self.shift = (self.shift[0] + PLAYER_SPEED, self.shift[1])
	
	def press_shoot(self):
		self.shooting = True


class MoveTemper:
	""" Move temper for an AI such as enemy. """
	
	def __init__(self):
		self.movement = (0, 0)

	def update(self, sec):
		self.movement = (0, ENEMY_SPEED)


def ensure_range(x, x_range): 
	left, right = x_range
	if x < left:
		return left
	if x > right:
		return right
	return x


class HunterMoveTemper(MoveTemper):
	""" Hunts down its target. """

	def __init__(self, target):
		MoveTemper.__init__(self)
		self.target = target
	
	def update(self, sec):
		""" Shifts itself to position so it and its target will be in the same line. """
		if not self.target.is_alive():
			return

		parent_ship = self.parent_controller.parent_ship
		shift = ensure_range(self.target.pos[0] - parent_ship.pos[0], (-ENEMY_SPEED, ENEMY_SPEED))
		self.movement = (shift, ENEMY_SPEED)


class PendulumMoveTemper(MoveTemper):
	""" Moves like pendulum inside some range. """

	def __init__(self, movement_range):
		MoveTemper.__init__(self)
		self.movement_range = movement_range
		if self.movement_range[0] > self.movement_range[1]:
			self.movement_range = (self.movement_range[1], self.movement_range[0])
		self.side_shift = ENEMY_SPEED
	
	def update(self, sec):
		parent_ship = self.parent_controller.parent_ship
		x, y = parent_ship.pos
		new_x = ensure_range(x, self.movement_range)
		if x != new_x:
			parent_ship.pos = (new_x, y)
			self.side_shift = -self.side_shift

		self.movement = (self.side_shift, ENEMY_SPEED)


class ScoutMoveTemper(MoveTemper):
	""" Moves twice as faster as Pawn. """

	def update(self, sec):
		self.movement = (0, ENEMY_SPEED * 2)


class PawnMoveTemper(MoveTemper):
	pass


class ShootTemper:
	""" Basic shoot temper for ships. """

	def __init__(self, group_delay, group_count):
		self.group_delay = group_delay
		self.current_group_delay = 0
		self.group_count = group_count
		self.current_group_count = self.group_count

	def shoot(self):
		""" Shoots and decreases group count. """
		if self.want_to_shoot():
			self.current_group_count -= 1
			if self.current_group_count <= 0:
				self.current_group_count = self.group_count
				self.current_group_delay = self.group_delay

	def want_to_shoot(self):
		return (self.group_count <= 0) and (self.current_group_delay <= 0)

	def update(self, sec):
		""" Wait until wanted to shoot. """
		if not self.want_to_shoot():
			self.current_group_delay -= sec


class EnemyController(Controller):
	""" Basic enemy AI controller. """

	def __init__(self, shoot_temper, move_temper):
		Controller.__init__(self)
		self.shoot_temper = shoot_temper
		self.move_temper = move_temper
		self.move_temper.parent_controller = self
	
	def shoot(self):
		if self.parent_ship.ready_to_shoot():
			self.shoot_temper.shoot()
		Controller.shoot(self)

	def update(self, sec):
		self.shoot_temper.update(sec)
		self.move_temper.update(sec)
		if self.shoot_temper.want_to_shoot():
			self.shooting = True
		self.shift = self.move_temper.movement
	

class Ship(Object):
	""" Base class for ships. """

	def __init__(self, sprite, pos, radius, controller, reload_time):
		Object.__init__(self, sprite, pos, radius)
		self.reload_time = 0
		self.reload_delay = reload_time

		self.controller = controller
		self.controller.parent_ship = self
	
	def ready_to_shoot(self):
		return self.reload_time <= 0

	def shoot(self):
		""" Tries to shoot.
		Returns any created objects such as bullets. """
		if not self.ready_to_shoot():
			return []
		self.controller.shoot()
		self.reload_time = self.reload_delay
		return []

	def update(self, sec):
		created_objects = []

		self.controller.update(sec)
		shift = self.controller.shift
		shooting = self.controller.shooting

		self.move((shift[0] * sec, shift[1] * sec))
		self.controller.reset()
		if shooting:
			created_objects.extend(self.shoot())

		if not self.ready_to_shoot():
			self.reload_time -= sec

		created_objects.extend(Object.update(self, sec))

		if not self.is_alive():
			created_objects.append(Explode(EXPLODE_SPRITE, self.pos, EXPLODE_SIZE, EXPLODE_DELAY))

		return created_objects


class Bullet(Object):
	""" Base bullet. Just flies, doesn't collide with objects. """

	def __init__(self, sprite, pos, radius, velocity):
		""" Velocity is a direction vector. """
		Object.__init__(self, sprite, pos, radius)
		self.velocity = velocity
		self.exists = True
	
	def is_alive(self):
		return self.exists

	def update(self, sec):
		self.move((self.velocity[0] * sec, self.velocity[1] * sec))
		return Object.update(self, sec)


class PlayerBullet(Bullet):
	def collide(self, collidees):
		for other in collidees:
			if isinstance(other, EnemyShip):
				self.exists = False
		return []


class EnemyBullet(Bullet):
	def collide(self, collidees):
		for other in collidees:
			if isinstance(other, PlayerShip):
				self.exists = False
		return []


class EnemyShip(Ship):
	""" Defines common enemy ship. """

	def __init__(self, sprite, pos, radius, controller, reload_time):
		Ship.__init__(self, sprite, pos, radius, controller, reload_time)
		self.exists = True

	def is_alive(self):
		return self.exists

	def update(self, sec):
		created_objects = Ship.update(self, sec)
		if not self.is_alive():
			if PROB_CREATE_WEAPON_BONUS > random.random():
				created_objects.append(WeaponBonus(WEAPON_BONUS_SPRITE, self.pos, BONUS_SIZE))
			elif PROB_CREATE_WEAPON_BONUS + PROB_CREATE_HEALTH_BONUS > random.random():
				created_objects.append(HealthBonus(HEALTH_BONUS_SPRITE, self.pos, BONUS_SIZE))
		return created_objects

	def shoot(self):
		created_objects = []
		if self.ready_to_shoot():
			created_objects.extend([EnemyBullet(ENEMY_BULLET_SPRITE, self.pos, BULLET_SIZE, ENEMY_BULLET_VELOCITY)])
		created_objects.extend(Ship.shoot(self))
		return created_objects

	def collide(self, collidees):
		""" Collides only with player or its bullets. """
		for other in collidees:
			if isinstance(other, PlayerShip):
				self.exists = False
			if isinstance(other, PlayerBullet):
				self.exists = False
		return []


class PlayerShip(Ship):
	""" Player ship. Extends base ship with health status and upgradable weapon. """

	def __init__(self, sprite, pos, radius, controller, reload_time, max_health):
		Ship.__init__(self, sprite, pos, radius, controller, reload_time)
		self.max_health = max_health
		self.health = self.max_health
		self.weapon_level = 1
	
	def is_alive(self):
		return (self.health > 0)

	def bullets_for_direction(self, direction):
		""" Returns set of bullets for given direction:
		1 - straight ahead;
		2 - couple of them;
		3 - auxiliary;
		4 - side bullets. """
		if direction == 1:
			return [PlayerBullet(PLAYER_BULLET_SPRITE, self.pos, BULLET_SIZE, PLAYER_BULLET_VELOCITY)]
		elif direction == 2:
			return [PlayerBullet(PLAYER_BULLET_SPRITE, (self.pos[0] - self.radius, self.pos[1]), BULLET_SIZE, PLAYER_BULLET_VELOCITY),
					PlayerBullet(PLAYER_BULLET_SPRITE, (self.pos[0] + self.radius, self.pos[1]), BULLET_SIZE, PLAYER_BULLET_VELOCITY)]
		elif direction == 3:
			return [PlayerBullet(PLAYER_BULLET_SPRITE, self.pos, BULLET_SIZE, PLAYER_AUX_RIGHT_BULLET_VELOCITY),
					PlayerBullet(PLAYER_BULLET_SPRITE, self.pos, BULLET_SIZE, PLAYER_AUX_LEFT_BULLET_VELOCITY)]
		elif direction == 4:
			return [PlayerBullet(PLAYER_BULLET_SPRITE, self.pos, BULLET_SIZE, PLAYER_SIDE_RIGHT_BULLET_VELOCITY),
					PlayerBullet(PLAYER_BULLET_SPRITE, self.pos, BULLET_SIZE, PLAYER_SIDE_LEFT_BULLET_VELOCITY)]
		else:
			return []

	def shoot(self):
		""" Extended shooting: can create a number of bullets depending on current weapon level. """
		created_objects = []
		if self.ready_to_shoot():
			bullets = self.bullets_for_direction(2 - self.weapon_level % 2)
			if self.weapon_level >= 3:
				bullets.extend(self.bullets_for_direction(3))
			if self.weapon_level >= 5:
				bullets.extend(self.bullets_for_direction(4))
			created_objects.extend(bullets)
		created_objects.extend(Ship.shoot(self))
		return created_objects

	def collide(self, collidees):
		for other in collidees:
			if isinstance(other, EnemyShip) or isinstance(other, EnemyBullet):
				self.health = ensure_range(self.health - COLLISION_DAMAGE, (0, self.max_health))
			if isinstance(other, HealthBonus):
				self.health = ensure_range(self.health + HEALTH_IMPROVEMENT, (0, self.max_health))
			if isinstance(other, WeaponBonus):
				self.weapon_level = ensure_range(self.weapon_level + 1, (1, 6))
		return []


class Painter:
	""" Do all the painting jobs whatsoever. """

	def draw_background(self, screen, background):
		""" Clears screen before rendering of background so it should be first in a queue. """
		screen.fill(BACK_COLOR)
		for star in background.stars:
			screen.set_at((int(star[0]), int(star[1])), STAR_COLOR)
	
	def draw_label(self, screen, label):
		""" Draws a big label on the screen centered. """
		font = pygame.font.Font(None, 32)
		sprite = font.render(label.text, True, TEXT_COLOR)
		textpos = sprite.get_rect(centerx=screen.get_rect().centerx, centery=screen.get_rect().centery)
		screen.blit(sprite, textpos)

	def draw_healthbar(self, screen, player):
			rect = pygame.Rect(player.get_rect().left, player.get_rect().bottom, player.get_rect().width, player.get_rect().height / 4)
			rect.move_ip(0, rect.height)
			ind_rect = rect.inflate(-4, -4)
			ind_rect.width = ind_rect.width * player.health / player.max_health

			if player.health * 2 < player.max_health:
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

		if isinstance(obj, PlayerShip) and obj.health < obj.max_health:
			self.draw_healthbar(screen, obj)


class Level:
	""" A main class that represents the whole level with all the objects. """

	def __init__(self, view_rect, length):
		""" Creates a new level with given length in seconds. """
		self.length = length
		self.player = PlayerShip(PLAYER_SPRITE, view_rect.center, PLAYER_SIZE, PlayerController(), PLAYER_RELOAD_TIME, PLAYER_HEALTH)
		self.objects = [self.player]

		self.queue = []
		for i in xrange(ENEMY_GROUP_COUNT):
			# pawn, scout, pendulum, hunter
			move_temper = PawnMoveTemper()
			dice = random.random()
			if PROB_SCOUT > dice:
				move_temper = ScoutMoveTemper()
			elif PROB_PENDULUM > dice - PROB_SCOUT:
				movement_range = (random.randrange(ENEMY_SIZE, view_rect.width - ENEMY_SIZE), random.randrange(ENEMY_SIZE, view_rect.width - ENEMY_SIZE))
				move_temper = PendulumMoveTemper(movement_range)
			elif PROB_HUNTER > dice - PROB_SCOUT - PROB_PENDULUM:
				move_temper = HunterMoveTemper(self.player)
			elif PROB_PAWN > dice - PROB_SCOUT - PROB_PENDULUM - PROB_HUNTER:
				move_temper = PawnMoveTemper()

			# (0, 0), (3, 1), (3, 3)
			shoot_temper = ShootTemper(0, 0)
			dice = random.random()
			if PROB_SNIPER > dice:
				shoot_temper = ShootTemper(3, 1)
			elif PROB_GUNNER > dice - PROB_SNIPER:
				shoot_temper = ShootTemper(3, 3)
			elif PROB_NO_SHOOT > dice - PROB_SNIPER - PROB_GUNNER:
				shoot_temper = ShootTemper(0, 0)

			# row, column, /, \ and random count from [1, 5]
			shift = (0, ENEMY_DISTANCE)
			dice = random.random()
			if PROB_H_LINE > dice:
				shift = (ENEMY_DISTANCE, 0)
			elif PROB_BACKSLASH > dice - PROB_H_LINE:
				shift = (ENEMY_DISTANCE, ENEMY_DISTANCE)
			elif PROB_SLASH > dice - PROB_H_LINE - PROB_BACKSLASH:
				shift = (-ENEMY_DISTANCE, ENEMY_DISTANCE)
			elif PROB_V_LINE > dice - PROB_H_LINE - PROB_BACKSLASH - PROB_SLASH:
				shift = (0, ENEMY_DISTANCE)
			group_size = random.randrange(1, ENEMY_GROUP_SIZE)
			group_width = shift[0] * (group_size - 1) + ENEMY_SIZE * 2
			group_height = shift[1] * (group_size - 1) + ENEMY_SIZE * 2

			# min(start_pos, start_pos + group_width) > 0
			# max(start_pos, start_pos + group_width) < view_rect.width
			start_pos_x = view_rect.centerx
			if 0 > group_width:
				start_pos_x = random.randrange(group_width, view_rect.width)
			if 0 < group_width:
				start_pos_x = random.randrange(0, view_rect.width - group_width)
			start_pos_y = self.length / 2
			if 0 < group_height:
				start_pos_y = random.randrange(view_rect.height / 2 + group_height, self.length)
			if 0 > group_height:
				start_pos_y = random.randrange(view_rect.height / 2, self.length - group_height)

			positions = [(start_pos_x + shift[0] * i, start_pos_y + shift[1] * i) for i in xrange(group_size)]

			for pos in positions:
				controller = EnemyController(copy.copy(shoot_temper), copy.copy(move_temper))
				enemy = EnemyShip(ENEMY_SPRITE, pos, ENEMY_SIZE, controller, ENEMY_RELOAD_TIME)
				self.queue.append(enemy)

		self.length = length + view_rect.height

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


def objects_colliding(first, second):
	result = math.hypot(first.pos[0] - second.pos[0], first.pos[1] - second.pos[1]) < (first.radius + second.radius)
	return result


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

		created_objects = []
		for o in level.objects:
			colliding_objects = [other for other in level.objects if other != o and objects_colliding(o, other)]
			created_objects.extend(o.collide(colliding_objects))
		for o in level.objects:
			created_objects.extend(o.update(sec))
		level.objects[0:0] = created_objects

		if not level.player.is_alive() and label == None:
			label = Label(LOSE_TEXT, TEXT_DELAY, close_after=True)

		level.objects = [o for o in level.objects if o.is_alive()]
		if len([o for o in level.objects if isinstance(o, EnemyShip) and o.get_rect().bottom > screen.get_rect().bottom]) > 0:
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
