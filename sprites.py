# sprites.py
# author antifin 2011
# license WTFPLv2
#
# Contains sprites and procedures for their generation.

import pygame
import random
import math

from defs import *

def player_sprite():
	sprite = pygame.Surface((16, 16), pygame.HWSURFACE)
	sprite.fill((255, 0, 255))
	sprite.set_colorkey((255, 0, 255))
	pixels = pygame.PixelArray(sprite)

	colors = [0xaaffff, 0x00ffff, 0x008fff, 0x0000ff]
	size = 4
	size2 = size * 2
	start_x, start_y = size / 2, 0

	quad = lambda points: reduce(lambda a, b: a + b, [[(x, y), (x, size2 - y), (size2 - x, y), (size2 - x, size2 - y)] for x, y in points])
	shift_points = lambda p, shift_x, shift_y: (p[0] + shift_x, p[1] + shift_y)
	def generate_number(number, l):
		for i in l: yield number
	element = lambda shift_x, shift_y, points: map(shift_points, points, generate_number(shift_x, points), generate_number(shift_y, points))
	emblem = lambda points: element(start_x, start_y, points) + \
			element(start_x +      size - 1,  start_y +      size - 1,  points) + \
			element(start_x + 2 * (size - 1), start_y + 2 * (size - 1), points) + \
			element(start_x -     (size - 1), start_y +      size - 1,  points) + \
			element(start_x -     (size - 1), start_y + 3 * (size - 1), points)

	colored_points = {}
	for m in range(1, 1 + size):
		points = [((size - m) + x + 1, (size - m) + m - x) for x in range(m)]
		if points:
			print m - 1, len(colors)
			colored_points[colors[m - 1]] = points
	print colored_points

	for color in colored_points:
		for x, y in emblem(quad(colored_points[color])):
			pixels[x][y] = color

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

PLAYER_SPRITE        = pygame.transform.scale(player_sprite(),        (PLAYER_SIZE * 2,  PLAYER_SIZE * 2))
PLAYER_BULLET_SPRITE = pygame.transform.scale(player_bullet_sprite(), (BULLET_SIZE * 2,  BULLET_SIZE * 2))
ENEMY_BULLET_SPRITE  = pygame.transform.scale(enemy_bullet_sprite(),  (BULLET_SIZE * 2,  BULLET_SIZE * 2))
ENEMY_SPRITE         = pygame.transform.scale(enemy_sprite(),         (ENEMY_SIZE * 2,   ENEMY_SIZE * 2))
EXPLODE_SPRITE       = pygame.transform.scale(explode_sprite(),       (EXPLODE_SIZE * 2, EXPLODE_SIZE * 2))
HEALTH_BONUS_SPRITE  = pygame.transform.scale(health_bonus_sprite(),  (BONUS_SIZE * 2,   BONUS_SIZE * 2))
WEAPON_BONUS_SPRITE  = pygame.transform.scale(weapon_bonus_sprite(),  (BONUS_SIZE * 2,   BONUS_SIZE * 2))
