## 导入相关模块
import random
from time import sleep
import numpy as np
import pygame
import sys

from pygame.locals import *


snake_speed = 50 #贪吃蛇的速度
windows_width = 1000
windows_height = 1000 #游戏窗口的大小
cell_size = 50       #贪吃蛇身体方块大小,注意身体大小必须能被窗口长宽整除

''' #初始化区
由于我们的贪吃蛇是有大小尺寸的, 因此地图的实际尺寸是相对于贪吃蛇的大小尺寸而言的
'''
map_width = int(windows_width / cell_size)
map_height = int(windows_height / cell_size)

# 颜色定义
white = (255, 255, 255)
black = (0, 0, 0)
gray = (230, 230, 230)
dark_gray = (40, 40, 40)
DARKGreen = (0, 155, 0)
Green = (0, 255, 0)
Red = (255, 0, 0)
blue = (0, 0, 255)
dark_blue =(0,0, 139)


BG_COLOR = black #游戏背景颜色

# 定义方向
UP = 1
DOWN = 2
LEFT = 3
RIGHT = 4

HEAD = 0 #贪吃蛇头部下标

class Wrong_index_for_action(Exception):
    def __init__(self):
        # 调用父类 Exception 的 __init__ 方法来设置错误消息
        super().__init__()
        # 可选：在自定义错误类中添加其他属性
	
class Snake():
	#主函数
	def __init__(self,windows_width=windows_width,windows_height=windows_width) -> None:
		self.w=windows_width
		self.h=windows_height
		self.iteration=0
		self.Reward=0
		pygame.init() # 模块初始化
		self.snake_speed_clock = pygame.time.Clock() # 创建Pygame时钟对象
		self.screen = pygame.display.set_mode((self.w, self.h)) #
		self.screen.fill(white)
		self.startx = random.randint(3, map_width - 2) #开始位置
		self.starty = random.randint(3, map_height - 2)
		self.snake_coords = [{'x': self.startx, 'y': self.starty},  #初始贪吃蛇
					{'x': self.startx - 1, 'y': self.starty},
					{'x': self.startx - 2, 'y': self.starty}]

		self.direction = RIGHT       #  开始时向右移动
		self.Reward=0
		self.food = self.get_random_location(self.snake_coords)     #实物随机位置
		self.flag=True
		self.frame_iteration=0
		pygame.display.set_caption("Python 贪吃蛇小游戏") #设置标题
		# self.show_start_info(self.screen)               #欢迎信息




	#游戏运行主体
	def running_game(self):
		while self.flag:
			action=[0,1,0]
			self.flag,_,_=self.do_step(action=action)
			self.flag = not self.flag
			

	def do_step(self,action,num=1):
		self.frame_iteration+=1
		clock_wise=[RIGHT,DOWN,LEFT,UP]
		idx=clock_wise.index(self.direction)
		if np.array_equal(action,[1,0,0]): #straight
			new_dir=clock_wise[idx]
		elif np.array_equal(action,[0,1,0]): #right
			new_dir=clock_wise[(idx+1)%4]
		elif np.array_equal(action,[0,0,1]): #left
			new_dir=clock_wise[(idx-1)%4]
		else:
			raise Wrong_index_for_action
		for event in pygame.event.get():
				if event.type == QUIT:
					self.terminate()
				
					# if (event.key == K_LEFT or event.key == K_a) and self.direction != RIGHT:
					# 	self.direction = LEFT
					# elif (event.key == K_RIGHT or event.key == K_d) and self.direction != LEFT:
					# 	self.direction = RIGHT
					# elif (event.key == K_UP or event.key == K_w) and self.direction != DOWN:
					# 	self.direction = UP
					# elif (event.key == K_DOWN or event.key == K_s) and self.direction != UP:
					# 	self.direction = DOWN
		self.direction=new_dir

		
		self.distan=abs(self.snake_coords[0]['x']-self.food['x'])+abs(self.snake_coords[0]['y']-self.food['y'])
		self.move_snake(self.direction, self.snake_coords) #移动蛇
		self.Reward= -(abs(self.snake_coords[0]['x']-self.food['x'])+abs(self.snake_coords[0]['y']-self.food['y']))*5
		if self.Reward+10*self.distan>0:
			self.Reward+=5
		else:self.Reward-=5
		ret = self.snake_is_alive()
		if not ret:
			self.Reward=-100

			return self.Reward,True,len(self.snake_coords) - 3
		if self.frame_iteration>50:
			self.Reward-= self.frame_iteration
		if(self.snake_is_eat_food(self.snake_coords, self.food)): #判断蛇是否吃到食物
			self.Reward=2*len(self.snake_coords)
			self.frame_iteration=0
		
		self.screen.fill(BG_COLOR)
		self.draw_grid(self.screen)
		self.draw_snake(self.screen, self.snake_coords)
		self.draw_food(self.screen, self.food)
		self.draw_score(self.screen, len(self.snake_coords) - 3)
		pygame.display.update()
		self.snake_speed_clock.tick(snake_speed) #控制fps
		return self.Reward,False,len(self.snake_coords) - 3
	#将食物画出来
	def draw_food(self,screen, food):
		x = food['x'] * cell_size
		y = food['y'] * cell_size
		appleRect = pygame.Rect(x, y, cell_size, cell_size)
		pygame.draw.rect(screen, Red, appleRect)
	#将贪吃蛇画出来
	def draw_snake(self,screen, snake_coords):
		for coord in snake_coords:
			x = coord['x'] * cell_size
			y = coord['y'] * cell_size
			wormSegmentRect = pygame.Rect(x, y, cell_size, cell_size)
			pygame.draw.rect(screen, dark_blue, wormSegmentRect)
			wormInnerSegmentRect = pygame.Rect(                #蛇身子里面的第二层亮绿色
				x + 4, y + 4, cell_size - 8, cell_size - 8)
			pygame.draw.rect(screen, blue, wormInnerSegmentRect)
	#画网格(可选)
	def draw_grid(self,screen):
		for x in range(0, windows_width, cell_size):  # draw 水平 lines
			pygame.draw.line(screen, dark_gray, (x, 0), (x, windows_height))
		for y in range(0, windows_height, cell_size):  # draw 垂直 lines
			pygame.draw.line(screen, dark_gray, (0, y), (windows_width, y))
	#移动贪吃蛇
	def move_snake(self,direction, snake_coords):
		if direction == UP:
			newHead = {'x': snake_coords[HEAD]['x'], 'y': snake_coords[HEAD]['y'] - 1}
		elif direction == DOWN:
			newHead = {'x': snake_coords[HEAD]['x'], 'y': snake_coords[HEAD]['y'] + 1}
		elif direction == LEFT:
			newHead = {'x': snake_coords[HEAD]['x'] - 1, 'y': snake_coords[HEAD]['y']}
		elif direction == RIGHT:
			newHead = {'x': snake_coords[HEAD]['x'] + 1, 'y': snake_coords[HEAD]['y']}

		snake_coords.insert(0, newHead)
	#判断蛇死了没
	def snake_is_alive(self,pt=None):
		if pt==None:
			pt=self.snake_coords[HEAD]
		if pt['x'] == -1 or pt['x'] == map_width or pt['y'] == -1 or pt['y'] == map_height:
			return False # 蛇碰壁啦
		for snake_body in self.snake_coords[1:]:
			if snake_body['x'] == pt['x'] and snake_body['y'] == pt['y']:
				return False # 蛇碰到自己身体啦
		return True
	def play_sound(self,sound_file):
		pygame.mixer.init()
		pygame.mixer.music.load(sound_file)
		pygame.mixer.music.play()
	#判断贪吃蛇是否吃到食物
	def snake_is_eat_food(self,snake_coords, food):  #如果是列表或字典，那么函数内修改参数内容，就会影响到函数体外的对象。
		if snake_coords[HEAD]['x'] == food['x'] and snake_coords[HEAD]['y'] == food['y']:
			# self.play_sound('./hit.mp3')
			food_tmp=self.get_random_location(snake_coords)
			food['x']=food_tmp['x']
			food['y']=food_tmp['y']
			return True
			
		else:
			del snake_coords[-1]  # 如果没有吃到实物, 就向前移动, 那么尾部一格删掉
			return False
	#食物随机生成
	def get_random_location(self,snake_coords):
		food= {'x': random.randint(0, map_width - 1), 'y': random.randint(0, map_height - 1)}
		while food in snake_coords:
			food= {'x': random.randint(0, map_width - 1), 'y': random.randint(0, map_height - 1)}
		return food
	#开始信息显示
	def show_start_info(self,screen):
		font = pygame.font.Font('myfont.ttf', 40)
		tip = font.render('按任意键开始游戏~~~', True, (65, 105, 225))
		gamestart = pygame.image.load('gamestart.png')
		screen.blit(gamestart, (140, 30))
		screen.blit(tip, (240, 550))
		pygame.display.update()

		while True:  #键盘监听事件
			for event in pygame.event.get():  # event handling loop
				if event.type == QUIT:
					self.terminate()     #终止程序
				elif event.type == KEYDOWN:
					if (event.key == K_ESCAPE):  #终止程序
						self.terminate() #终止程序
					else:
						return #结束此函数, 开始游戏
	#游戏结束信息显示
	def show_gameover_info(self,screen):
		font = pygame.font.Font('myfont.ttf', 40)
		tip = font.render('按Q或者ESC退出游戏, 按任意键重新开始游戏~', True, (65, 105, 225))
		gamestart = pygame.image.load('gameover.png')
		screen.blit(gamestart, (60, 0))
		screen.blit(tip, (80, 300))
		pygame.display.update()

		while True:  #键盘监听事件
			for event in pygame.event.get():  # event handling loop
				if event.type == QUIT:
					self.terminate()     #终止程序
				elif event.type == KEYDOWN:
					if event.key == K_ESCAPE or event.key == K_q:  #终止程序
						self.terminate() #终止程序
					else:
						return #结束此函数, 重新开始游戏
	#画成绩
	def draw_score(self,screen,score):
		font = pygame.font.Font('myfont.ttf', 30)
		scoreSurf = font.render('得分: %s' % score, True, Green)
		scoreRect = scoreSurf.get_rect()
		scoreRect.topleft = (windows_width - 120, 10)
		screen.blit(scoreSurf, scoreRect)
	#程序终止
	def terminate(self):
		pygame.quit()
		sys.exit()
	def reset(self):
		self.startx = random.randint(3, map_width - 2) #开始位置
		self.starty = random.randint(3, map_height - 2)
		self.snake_coords = [{'x': self.startx, 'y': self.starty},  #初始贪吃蛇
					{'x': self.startx - 1, 'y': self.starty},
					{'x': self.startx - 2, 'y': self.starty}]

		self.direction = RIGHT       #  开始时向右移动
		self.Reward=0
		self.frame_iteration=0
		self.food = self.get_random_location(self.snake_coords)     #实物随机位置
		self.flag=True
if __name__=="__main__":
	my_snake=Snake(windows_width,windows_height)
	sleep(2)
	my_snake.do_step([0,1,0])
	print(my_snake.snake_coords)
	sleep(2)
	my_snake.do_step([1,0,0])
	sleep(2)
	my_snake.do_step([1,0,0])
	sleep(2)
	my_snake.do_step([1,0,0])
	sleep(2)
	my_snake.do_step([0,1,0])
	sleep(2)
	my_snake.do_step([0,1,0])