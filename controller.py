# controller.py
# author antifin 2011
# license WTFPLv2
#
# Controllers for player and enemy ships. Also, all the shoot and move tempers enemy could have.

from defs import *

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


