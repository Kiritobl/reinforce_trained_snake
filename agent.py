from time import sleep
import torch
import random
import numpy as np
from snake import Snake,UP,DOWN,LEFT,RIGHT
from collections import deque
from model import QTrainer,Linear_QNet
from helper import plot
import threading
MAX_MEMORY= 100_000
BATCH_SIEZ = 500
LR =0.00001

class Agent:
    def __init__(self) -> None:
        self.n_games=0
        self.epsilion=0
        self.gamma=0
        self.memory =deque(maxlen=MAX_MEMORY)  
        self.model=Linear_QNet(11,512,3)
        self.model.load_state_dict(torch.load('./model/61.pth'))
        self.trainer=QTrainer(self.model,lr=LR,gamma=self.gamma)
    def get_state(self,game:Snake):
        head=game.snake_coords[0]
        x_coords = [dictionary['x'] for dictionary in game.snake_coords]
        y_coords = [dictionary['y'] for dictionary in game.snake_coords]

        # 使用矢量化操作将对应位置的元素修改为1
        

        point_u={'x':head['x'],"y":head['y']-1}
        point_r={'x':head['x']+1,"y":head['y']}
        point_l={'x':head['x']-1,"y":head['y']}
        point_d={'x':head['x'],"y":head['y']+1}
        # dir_up
        # dir_right
        # dir_left
        # dir_down   
        dir_u= game.direction ==UP
        dir_r= game.direction ==RIGHT
        dir_l= game.direction ==LEFT
        dir_d= game.direction ==DOWN
        food=game.food

        state=[

        dir_u,
        dir_r,
        dir_l,
        dir_d,

        # danger straight
        (dir_r and not game.snake_is_alive(point_r))or
        (dir_d and not game.snake_is_alive(point_d))or
        (dir_l and not game.snake_is_alive(point_l))or
        (dir_u and not game.snake_is_alive(point_u)),
        # danger RIGHT
        (dir_u and not game.snake_is_alive(point_r))or
        (dir_r and not game.snake_is_alive(point_d))or
        (dir_d and not game.snake_is_alive(point_l))or
        (dir_l and not game.snake_is_alive(point_u)),
         # danger LEFT       
        (dir_u and not game.snake_is_alive(point_l))or
        (dir_l and not game.snake_is_alive(point_d))or
        (dir_d and not game.snake_is_alive(point_r))or
        (dir_r and not game.snake_is_alive(point_u)),


        #up
        food['y']>head['y'],
        #right
        food['x']>head['x'],
        #left
        food['x']<head['x'],
        #down
        food['y']<head['y'],
      






        ] 
        
        return np.array(state,dtype=int)
    

    def remember(self,state,action,reward,next_state,done):
        self.memory.append((state,action,reward,next_state,done))
    def train_long_memory(self):
        if len(self.memory) >BATCH_SIEZ:
            mini_sample = random.sample(self.memory,BATCH_SIEZ)
        else:
            mini_sample = self.memory


        states,actions,rewards,next_states,dones = zip (*mini_sample)

        self.trainer.train_step(states,actions,rewards,next_states,dones)


    def train_short_memory(self,state,action,reward,next_state,done):
        self.trainer.train_step(state,action,reward,next_state,done)

    def get_action(self,state):
        self.epsilion = 0 - self.n_games
        final_move = [0,0,0]
        if random.randint(0,500)<self.epsilion:
            move = random.randint(0,2)
            final_move[move]=1
        else:
            state0 = torch.tensor(state, dtype=torch.float32)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move]=1
        return final_move
def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record=0
    agent = Agent()
    games = [Snake() for _ in range(4)]  # 创建四个游戏实例
    lock = threading.Lock()  # 创建锁，用于确保多线程访问网络的安全

    def play_game(game, agent, game_id):
        nonlocal total_score
        nonlocal record
        while True:
            sleep(0.2)
            state_old = agent.get_state(game)

            final_move = agent.get_action(state_old)

            reward, done, score = game.do_step(final_move, agent.n_games)

            state_new = agent.get_state(game)

            with lock:
                agent.train_short_memory(state=state_old, action=final_move, reward=reward, next_state=state_new, done=done)
                agent.remember(state=state_old, action=final_move, reward=reward, next_state=state_new, done=done)

            if done:
                # train long memory
                with lock:
                    game.reset()
                    agent.n_games += 1
                    agent.train_long_memory()
                    if score > record:
                        record = score
                        agent.model.save(str(record) + '.pth')
                    print("游戏", game_id, "第", agent.n_games, "局得分", score, '最高得分', record)

                    plot_scores.append(score)
                    total_score += score
                    mean_score = total_score / agent.n_games
                    plot_mean_scores.append(mean_score)
                    plot(plot_scores, plot_mean_scores)

    threads = [threading.Thread(target=play_game, args=(game, agent, game_id)) for game_id, game in enumerate(games)]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()





def train_one():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record=0
    agent = Agent()
    game = Snake()  # 创建四个游戏实例


    while True:
        state_old = agent.get_state(game)

        final_move = agent.get_action(state_old)

        reward, done, score = game.do_step(final_move, agent.n_games)

        state_new = agent.get_state(game)


        agent.train_short_memory(state=state_old, action=final_move, reward=reward, next_state=state_new, done=done)
        agent.remember(state=state_old, action=final_move, reward=reward, next_state=state_new, done=done)

        if done:
            # train long memory

                game.reset()
                agent.n_games += 1
                agent.train_long_memory()
                if score > record or agent.n_games%100==0:
                    record = score
                    agent.model.save(str(record)+str(random.randint(0,100)) + '.pth')
                print("游戏", "第", agent.n_games, "局得分", score, '最高得分', record)

                plot_scores.append(score)
                total_score += score
                mean_score = total_score / agent.n_games
                plot_mean_scores.append(mean_score)
                plot(plot_scores, plot_mean_scores)

if __name__=="__main__":
    train_one()




