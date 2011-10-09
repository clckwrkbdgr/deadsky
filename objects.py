# objects.py
# author antifin 2011
# license WTFPLv2
#
# Basic Object class and all successors: Ships, Bonus, Bullets etc.

from defs import *
import pygame
import random
import sprites

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
		if [other for other in collidees if isinstance(other, PlayerShip)]:
			self.exists = False
		return []

class WeaponBonus(Bonus):
	pass

class HealthBonus(Bonus):
	pass

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
			created_objects.append(Explode(sprites.EXPLODE_SPRITE, self.pos, EXPLODE_SIZE, EXPLODE_DELAY))

		return created_objects

class Bullet(Object):
	""" Base bullet. Just flies, doesn't collide with objects. """

	def __init__(self, sprite, pos, radius, velocity, foe_class = None):
		""" Velocity is a direction vector. """
		Object.__init__(self, sprite, pos, radius)
		self.velocity = velocity
		self.exists = True
		self.foe_class = foe_class
	
	def is_alive(self):
		return self.exists

	def update(self, sec):
		self.move((self.velocity[0] * sec, self.velocity[1] * sec))
		return Object.update(self, sec)

	def collide(self, collidees):
		if [other for other in collidees if isinstance(other, self.foe_class)]:
			self.exists = False
		return []

class PlayerBullet(Bullet):
	def __init__(self, sprite, pos, radius, velocity):
		Bullet.__init__(self, sprite, pos, radius, velocity, EnemyShip)

class EnemyBullet(Bullet):
	def __init__(self, sprite, pos, radius, velocity):
		Bullet.__init__(self, sprite, pos, radius, velocity, PlayerShip)

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
			new_bonus = get_prob_cause({
				"PROB_CREATE_WEAPON_BONUS": lambda: WeaponBonus(sprites.WEAPON_BONUS_SPRITE, self.pos, BONUS_SIZE),
				"PROB_CREATE_HEALTH_BONUS": lambda: HealthBonus(sprites.HEALTH_BONUS_SPRITE, self.pos, BONUS_SIZE)
				}, lambda: None)
			if new_bonus:
				created_objects.append(new_bonus)
		return created_objects

	def shoot(self):
		created_objects = []
		if self.ready_to_shoot():
			created_objects.extend([EnemyBullet(sprites.ENEMY_BULLET_SPRITE, self.pos, BULLET_SIZE, ENEMY_BULLET_VELOCITY)])
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
			return [PlayerBullet(sprites.PLAYER_BULLET_SPRITE, self.pos, BULLET_SIZE, PLAYER_BULLET_VELOCITY)]
		elif direction == 2:
			return [PlayerBullet(sprites.PLAYER_BULLET_SPRITE, (self.pos[0] - self.radius, self.pos[1]), BULLET_SIZE, PLAYER_BULLET_VELOCITY),
					PlayerBullet(sprites.PLAYER_BULLET_SPRITE, (self.pos[0] + self.radius, self.pos[1]), BULLET_SIZE, PLAYER_BULLET_VELOCITY)]
		elif direction == 3:
			return [PlayerBullet(sprites.PLAYER_BULLET_SPRITE, self.pos, BULLET_SIZE, PLAYER_AUX_RIGHT_BULLET_VELOCITY),
					PlayerBullet(sprites.PLAYER_BULLET_SPRITE, self.pos, BULLET_SIZE, PLAYER_AUX_LEFT_BULLET_VELOCITY)]
		elif direction == 4:
			return [PlayerBullet(sprites.PLAYER_BULLET_SPRITE, self.pos, BULLET_SIZE, PLAYER_SIDE_RIGHT_BULLET_VELOCITY),
					PlayerBullet(sprites.PLAYER_BULLET_SPRITE, self.pos, BULLET_SIZE, PLAYER_SIDE_LEFT_BULLET_VELOCITY)]
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


