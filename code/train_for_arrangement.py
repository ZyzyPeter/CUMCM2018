from enviroment import Env
from smart_generate import smart_work_type_genarate
from rl import QLearning
import enviroment
import pandas as pd
import numpy as np
# 设置全局变量
MAX_EPISODES = 30

def update():
	score_record=[]
	for episode in range(MAX_EPISODES):
		# 初始化 state 的观测值
		observation = env.reset()

		while True:
			# 更新可视化环境
			# env.render(observation)

			# RL 大脑根据 state 的观测值挑选 action
			action = RL.choose_action_QL(observation)

			# 探索者在环境中实施这个 action, 并得到环境返回的下一个 state 观测值, reward 和 done (是否是掉下地狱或者升上天堂)
			observation_, reward, done = env.step(action)

			# RL 从这个序列 (state, action, reward, state_) 中学习
			RL.learn(observation, action, reward, observation_)

			# 将下一个 state 的值传到下一次循环，并更新环境参数
			if observation_!='terminal':
				observation = observation_
			env.update(observation)

			print("获得reward:",str(reward),"采用动作:",action,"RGV位置",observation[1]['loc'],"剩余时间:",env.time)
			print("RGV携带工料:",observation[1]['material_type'])
			print("RGV状态",str(observation[1]),"CNC状态",str(observation[2]))

			print("加工物料:",str(env.score))

			# 回合结束
			if done:
				print("本回合加工物料:",str(env.score))
				score_record.append(env.score)
				pd.DataFrame({'score':score_record}).to_csv('result/record/param3case4_record.csv',index=False)
				mean_score = np.mean(score_record[-3:])
				if np.abs(mean_score-env.score) < 5 and len(score_record) >9:
					return score_record
				break
	return score_record
	# 结束并关闭窗口
	print('over')
	env.destroy(RL,path='result/q_result_p1c1.csv')

if __name__ == "__main__":
	# 定义环境 env 和 RL 方式
	Best_Score = []
	Type = []
	CNC_2_1 = enviroment.CNC_2_1
	CNC_2_2 = enviroment.CNC_2_2
	smart_genarate = smart_work_type_genarate(CNC_2_1,CNC_2_2,2)
	for group in smart_genarate:
		print('刀具策略为',group)
		Type.append(group)
		enviroment.CNC_WORK_TYPE = group
		env = Env()
		RL = QLearning(actions=list(range(env.n_actions)))
		# 开始可视化环境 env
		score_record = update()
		Best_Score.append(np.max(score_record))
	result = pd.DataFrame({'Best_Score':Best_Score,'Type':Type})
	result.to_csv('result_param3_case4.csv',index = False)
