from random import choice, randrange, randint
import pygame

# -- constantes globais

# cores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)

BACKGROUND_COLOR = (0, 51, 102)
WALL_COLOR = (204, 68, 0)
FONT_COLOR = WHITE
PLAYER_COLOR = WHITE
TARGET_COLOR = GREEN
MENU_ARROW_COLOR = WHITE
MENU_FONT_COLOR = WHITE

PLAY = True
QUIT = False

# dimensões da janela
SCREEN_WIDTH  = 700
SCREEN_HEIGHT = 500

# tamanho do jogador
PLAYER_SIZE = [9, 9]

# velocidade do jogador
SPEED = 2

# tamanho do deslocamento
OFFSET = 12

INITIAL_TIME = 90

NUMBER_OF_LEVELS = 10

class Player(pygame.sprite.Sprite):
	def __init__(self, x, y, player_color):
		super().__init__()
		
		# define a image e a superfície do jogador
		self.image = pygame.Surface(PLAYER_SIZE)
		self.image.fill(player_color)
		
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		
		# define a velocidade
		self.change_x = 0
		self.change_y = 0
		
		# lista de paredes em que o jogador pode colidir
		self.walls = None

		# alvo do jogador
		self.target = None

		# estado do jogo
		self.win = False
	

	# muda a velocidade do jogador
	def changespeed(self, x, y):
		self.change_x += x
		self.change_y += y

		
	def update(self):

		# checa colisão do eixo x do alvo e das paredes
		self.rect.x += self.change_x

		target_hit = pygame.sprite.spritecollide(self, self.target, False)
		if len(target_hit) > 0:
			self.win = True

		block_hit_list = pygame.sprite.spritecollide(self, self.walls, False)
		for block in block_hit_list:
			if self.change_x > 0:
				self.rect.right = block.rect.left
			else:
				self.rect.left = block.rect.right
		
		# checa colisão do eixo y do alvo e das paredes
		self.rect.y += self.change_y
		
		target_hit = pygame.sprite.spritecollide(self, self.target, False)
		if len(target_hit) > 0:
			self.win = True

		block_hit_list = pygame.sprite.spritecollide(self, self.walls, False)
		for block in block_hit_list:
			if self.change_y > 0:
				self.rect.bottom = block.rect.top
			else:
				self.rect.top = block.rect.bottom
				
	
class Wall(pygame.sprite.Sprite):
	def __init__(self, x, y, width, height, color):
		super().__init__()
		
		self.image = pygame.Surface([width, height])
		self.image.fill(color)
		
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y

		self.mask = pygame.mask.from_surface(self.image)


class Maze():
	def __init__(self, wall_color):
		self.rows = SCREEN_WIDTH // 20 - 8
		self.cols = SCREEN_HEIGHT // 20 - 9
		self.grid = []
		self.unvisited = []
		self.wall_color = wall_color

	
	def get_unvisited_neighbors(self, current, unvisited):
		x = current[0]
		y = current[1]
		move = [(0, 2), (0, -2), (-2, 0), (2, 0)]
		neighbors = [(x + dx, y + dy) for dx, dy in move]
		return [(a, b) for a, b in neighbors if (a, b) in unvisited]


	# preenche o grid que representa o labirinto numericamente
	def fill_grid(self):
 		# pega o total de linhas e colunas no grid, contando com as paredes
		total_rows = self.rows * 2 + 1
		total_cols = self.cols * 2 + 1

		# 0 -> caminho livre
		# 1 -> parede
		for i in range(total_rows):
			row = []
			for j in range(total_cols):
				if i & 1:
					if j & 1:
						row.append(0)
						self.unvisited.append((i, j))
					else:
						row.append(1)
				else:
					row.append(1)
			self.grid.append(row)


	# algoritmo para gerar o labirinto - variação da DFS
	def build_maze(self):
		self.fill_grid()

		# pilha auxiliar
		stack = []

		# escolhe a posição atual aleatoriamente
		current = choice(self.unvisited)

		# remove dos não visitados, ou seja, visita
		self.unvisited.remove(current)

		# enquanto ainda há posições não visitadas
		while len(self.unvisited) > 0:

			# pega os visinhos não visitados da posição atual
			unvisited_neighbors = self.get_unvisited_neighbors(current, self.unvisited)

			if len(unvisited_neighbors) > 0:
				neighbor = choice(unvisited_neighbors)
				stack.append(current)

				# remove a parede entre o vizinho e a posição atual
				wall_x = (current[0] + neighbor[0]) // 2
				wall_y = (current[1] + neighbor[1]) // 2
				self.grid[wall_x][wall_y] = 0

				current = neighbor
				self.unvisited.remove(current)
			elif len(stack) > 0:
				current = stack.pop()
			else:
				current = choice(self.unvisited)
				self.unvisited.remove(current)
			
	def generate_walls(self, maze):
		maze_row_len = len(maze)
		maze_col_len = len(maze[0])
		
		wall_list = []		
		for x in range(maze_row_len):
			for y in range(maze_col_len):
				if maze[x][y] == 1:
					wall = Wall(to_pixel_x(x), to_pixel_y(y), 12, 12, self.wall_color)
					wall_list.append(wall)
					
		return wall_list
		

class Menu():
	def __init__(self, screen):
		self.screen = screen
		self.menu_loop = True
		self.arrow = PLAY 
	
	def loop(self):
		while self.menu_loop:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.menu_loop = False
					self.arrow = QUIT
				
				# usuário pressionou uma tecla
				elif event.type == pygame.KEYDOWN:
					if event.key == pygame.K_RETURN:
						self.menu_loop = False
					elif event.key == pygame.K_UP or event.key == pygame.K_DOWN:
						self.arrow = not self.arrow
							
				# usuário soltou uma tecla
				elif event.type == pygame.KEYUP:
					if event.key == pygame.K_RETURN:
						self.menu_loop = False
			
			# --- código de limpar a tela vem aqui
			# all_sprite_list.update()
			
			# limpa a tela e pinta ela de preto
			self.screen.fill(BACKGROUND_COLOR)
			
			# --- fim limpar tela
			
			# --- código de desenho vem aqui
			# all_sprite_list.draw(screen)
			
			# seleciona a fonte, o tamanho, se é negrito, se é itálico
			font = pygame.font.SysFont('Calibri', 30, False, False)

			name_font = pygame.font.SysFont('Calibri', 50, False, False)

			name = name_font.render("TIC TAC MAZE", True, MENU_FONT_COLOR)			
			play_opt = font.render("JOGAR", True, MENU_FONT_COLOR)
			quit_opt = font.render("SAIR", True, MENU_FONT_COLOR)
		 
			# coloca a imagem do texto na posição [x, y] da tela
			# nesse caso, os textos "JOGAR" e "SAIR" são centralizados
			play_w = play_opt.get_rect().width
			play_h = play_opt.get_rect().height
			play_x = SCREEN_WIDTH / 2 - play_w / 2
			play_y = SCREEN_HEIGHT / 2 - play_h / 2
			self.screen.blit(play_opt, [play_x, play_y])			
			
			quit_w = quit_opt.get_rect().width
			quit_h = quit_opt.get_rect().height
			quit_x = SCREEN_WIDTH / 2 - quit_w / 2
			quit_y = SCREEN_HEIGHT / 2 - quit_h / 2 + 30
			self.screen.blit(quit_opt, [quit_x, quit_y])

			name_w = name.get_rect().width
			name_h = name.get_rect().height
			name_x = SCREEN_WIDTH / 2 - name_w / 2
			name_y = SCREEN_HEIGHT / 2 - name_h / 2 - 50
			self.screen.blit(name, [name_x, name_y])
			
			# coloca a "setinha" na opção desejada
			if self.arrow == PLAY:
				a_x = play_x - 16
				a_y = play_y + 6
			else:
				a_x = quit_x - 16
				a_y = quit_y + 6
				
			arrow_x = (a_x, a_x + 10, a_x)
			arrow_y = (a_y, a_y + 5, a_y + 10)
			
			pygame.draw.polygon(self.screen, MENU_ARROW_COLOR, ((arrow_x[0], arrow_y[0]), (arrow_x[1], arrow_y[1]), (arrow_x[2], arrow_y[2])))
			
			# --- fim desenho
			
			# --- atualiza a tela com o que foi desenhado
			pygame.display.flip()
			
		return self.arrow
		

class Level():
	def __init__(self, num):
		self.num = num
		self.time = []
		self.colors = {
			'font': [],
			'player': [],
			'target': [],
			'wall': [],
			'background': [
				(50, 18, 131),
				(26, 15, 62),
				(87, 28, 94),
				(61, 51, 12),
				(96, 6, 159),
				(63, 10, 11),
				(13, 66, 14),
				(19, 76, 71),
				(71, 41, 59),
				(45, 29, 3)
			]
		}
		
		for i in range(num):
			self.time.append(INITIAL_TIME - i * 6)
			self.colors['font'].append(WHITE)
			self.colors['player'].append(WHITE)
			self.colors['target'].append(RED)
			self.colors['wall'].append((183, 179, 137))

	def is_last_level(self, curr_level):
		return curr_level == self.num - 1
		

def generate_positions(maze, min_distance):
	maze_row_len = len(maze)
	maze_col_len = len(maze[0])
	
	player_pos = 0, 0
	while(maze[player_pos[0]][player_pos[1]] == 1):
		player_pos = randrange(maze_row_len), randrange(maze_col_len)
		
	target_pos = 0, 0
	while(maze[target_pos[0]][target_pos[1]] == 1 or manhattan_distance(player_pos, target_pos) < min_distance):
		target_pos = randrange(maze_row_len), randrange(maze_col_len)
		
	return player_pos, target_pos


def random_rgb():
	r = lambda: randint(0, 255)
	return r(), r(), r()
			
# transforma a representação numérica da posição X para pixel
def to_pixel_x(x):
	return x * OFFSET + 10


# transforma a representação numérica da posição Y para pixel
def to_pixel_y(y):
	return y * OFFSET + 80


# pega a distância de manhattan entre dois pontos
def manhattan_distance(x, y):
	return abs(x[0] - y[0]) + abs(x[1] - y[1])


def main():
	# inicia o pygame
	pygame.init()

	# título da janela
	pygame.display.set_caption('Tic Tac Maze')

	# tamanho da janela
	size = (SCREEN_WIDTH, SCREEN_HEIGHT)
	screen = pygame.display.set_mode(size)

	pygame.mixer.init()
	pygame.mixer.music.load('background.mp3')
	pygame.mixer.music.play(-1)
	
	# menu
	menu = Menu(screen)
	option = menu.loop()
	
	if option == PLAY:

		font = pygame.font.SysFont('Calibri', 25, False, False)

		before_game = True
		while before_game:
			for event in pygame.event.get():
				if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
					before_game = False
			
			screen.fill(BACKGROUND_COLOR)
			
			font = pygame.font.SysFont('Calibri', 30, False, False)
			
			message = font.render("Alcance o quadrado vermelho dentro do tempo!", True, MENU_FONT_COLOR)
		 
			# coloca a imagem do texto na posição [x, y] da tela
			# nesse caso, os textos "JOGAR" e "SAIR" são centralizados
			msg_w = message.get_rect().width
			msg_h = message.get_rect().height
			msg_x = SCREEN_WIDTH / 2 - msg_w / 2
			msg_y = SCREEN_HEIGHT / 2 - msg_h / 2
			screen.blit(message, [msg_x, msg_y])
			
			# --- fim desenho
			
			# --- atualiza a tela com o que foi desenhado
			pygame.display.flip()

		
		levels = Level(NUMBER_OF_LEVELS)

		# loop principal
		for curr_level in range(levels.num):
		
			# lista com todos os sprites
			all_sprite_list = pygame.sprite.Group()
			
			maze_obj = Maze(levels.colors['wall'][curr_level])
			maze_obj.build_maze()
			maze = maze_obj.grid

			# desenha as paredes do labirinto
			wall_list = maze_obj.generate_walls(maze)
			for wall in wall_list:
				all_sprite_list.add(wall)

			# gera posições aleatórias para o jogador [0] e para o alvo [1]
			player_pos, target_pos = generate_positions(maze, 20)

			# cria o alvo
			target = Wall(to_pixel_x(target_pos[0]), to_pixel_y(target_pos[1]), PLAYER_SIZE[0], PLAYER_SIZE[1], levels.colors['target'][curr_level])
			wall_list.append(target)
			all_sprite_list.add(target)

			# cria o jogador
			player = Player(to_pixel_x(player_pos[0]), to_pixel_y(player_pos[1]), levels.colors['player'][curr_level])
			player.walls = wall_list
			player.target = [target]
			all_sprite_list.add(player)

			# quão rápida a tela é atualizada
			clock = pygame.time.Clock()
			
			# variáveis para o temporizador
			frame_count = 0
			frame_rate = 60
			play_time = levels.time[curr_level]

			running = True
			game_over = False
			can_frame_count = True
			next_lvl = False
			go_to_next_level = False
			while running:
				for event in pygame.event.get():
					if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
						running = False
						return
					
					# usuário pressionou uma tecla
					elif event.type == pygame.KEYDOWN:
						if not game_over:
							if event.key == pygame.K_LEFT:
								player.changespeed(-SPEED, 0)
							elif event.key == pygame.K_RIGHT:
								player.changespeed(SPEED, 0)
							elif event.key == pygame.K_UP:
								player.changespeed(0, -SPEED)
							elif event.key == pygame.K_DOWN:
								player.changespeed(0, SPEED)
						
						if next_lvl == True and event.key == pygame.K_RETURN:
							go_to_next_level = True
							break
							
							
					# usuário soltou uma tecla
					elif event.type == pygame.KEYUP:
						if not game_over:
							if event.key == pygame.K_LEFT:
								player.changespeed(SPEED, 0)
							elif event.key == pygame.K_RIGHT:
								player.changespeed(-SPEED, 0)
							elif event.key == pygame.K_UP:
								player.changespeed(0, SPEED)
							elif event.key == pygame.K_DOWN:
								player.changespeed(0, -SPEED)

				if go_to_next_level:
					break

				# --- código de limpar a tela vem aqui
				all_sprite_list.update()
				
				# limpa a tela e pinta ela de preto
				screen.fill(levels.colors['background'][curr_level])
				
				# --- fim limpar tela
				
				# --- código de desenho vem aqui
				all_sprite_list.draw(screen)
				
				# --- Temporizador ---
				# calcula o total de segundos = tempo inicial - (contagem de quadros / taxa de quadros)
				total_seconds = play_time - (frame_count // frame_rate)
				if total_seconds < 0:
					total_seconds = 0
			 
				# divide por 60 para pegar os minutos
				minutes = total_seconds // 60
			 
				# usa o resto da divisão para pegar os segundos
				seconds = total_seconds % 60

				next_lvl_string = ""

				#debug - enter pra sempre ir pra proxima fase
				next_lvl = True

				if player.win == True:
					output_string = "Seu tempo: {0:02}:{1:02}".format(minutes, seconds)
					if not levels.is_last_level(curr_level):
						next_lvl_string = "Aperte ENTER para ir para a próxima fase"
						next_lvl = True
					game_over = True
					can_frame_count = False
				elif minutes == 0 and seconds == 0:
					output_string = "Tempo acabou. Game Over!"
					game_over = True
				else:
					output_string = "Tempo restante: {0:02}:{1:02}".format(minutes, seconds)
					
				# seleciona a fonte, o tamanho, se é negrito, se é itálico
				font = pygame.font.SysFont('Calibri', 25, False, False)
				font_esc = pygame.font.SysFont('Calibri', 20, False, False)
				
				# renderiza o texto. "True" significa texto anti-aliased
				# último parâmetro: cor do texto 
				# este comando, porém, ainda não coloca a imagem do texto na tela
				text = font.render(output_string, True, levels.colors['font'][curr_level])
				esc = font_esc.render("Aperte ESC para sair do jogo", True, levels.colors['font'][curr_level])

				level = 'Fase ' + str(curr_level + 1)

				level_font = font.render(level, True, levels.colors['font'][curr_level])

				if player.win == True and levels.is_last_level(curr_level):
					win = font.render("PARABENS, VOCE VENCEU!", True, levels.colors['font'][curr_level])
					screen.blit(win, [SCREEN_WIDTH / 2 + 70, 15])

				# debug
				# next_lvl_string = "Aperte ENTER para ir para a próxima fase"
				
				if next_lvl_string != "":
					next_lvl_font = font.render(next_lvl_string, True, levels.colors['font'][curr_level])
					screen.blit(next_lvl_font, [SCREEN_WIDTH / 2 - 100, 15])
			 
				# coloca a imagem do texto na posição [x, y] da tela
				screen.blit(esc, [10, 15])
				screen.blit(text, [10, 45])

				screen.blit(level_font, [SCREEN_WIDTH - 100, 45])
				
				# --- fim desenho
				
				if can_frame_count:
					frame_count += 1
				
				# --- limita para o que está definido em frame_rate
				clock.tick(frame_rate)
				
				# --- atualiza a tela com o que foi desenhado
				pygame.display.flip()	
		
	pygame.mixer.quit()

	# encerra o pygame
	pygame.quit()


if __name__ == "__main__":
	main()
