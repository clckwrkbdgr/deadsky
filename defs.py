# defs.py
# author antifin 2011
# license WTFPLv2
#
# Global definitions for the game.

import math
import random

HEALTHBAR_COLOR = (255, 255, 255)
SCREEN_SIZE = (800, 600)
STAR_COUNT = 500
STAR_COLOR = (0, 127, 0)
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
FONT_SIZE = 32


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

probs = {
		"PROB_CREATE_WEAPON_BONUS": 0.25,
		"PROB_CREATE_HEALTH_BONUS": 0.25,

		"PROB_SCOUT": 0.25,
		"PROB_PENDULUM": 0.25,
		"PROB_HUNTER": 0.25,
		"PROB_PAWN": 0.25,

		"PROB_SNIPER": 0.33,
		"PROB_GUNNER": 0.33,
		"PROB_NO_SHOOT": 0.33,

		"PROB_H_LINE": 0.25,
		"PROB_V_LINE": 0.25,
		"PROB_SLASH": 0.25,
		"PROB_BACKSLASH": 0.25
		}

def objects_colliding(first, second):
	result = math.hypot(first.pos[0] - second.pos[0], first.pos[1] - second.pos[1]) < (first.radius + second.radius)
	return result

def ensure_range(x, x_range): 
	left, right = x_range
	if x < left:
		return left
	if x > right:
		return right
	return x

def get_prob_cause(prob_map, default_builder):
	dice = random.random()
	cur_prob = 0.0
	for prob in prob_map:
		cur_prob += probs[prob]
		if cur_prob > dice:
			return prob_map[prob]()
	return default_builder()

