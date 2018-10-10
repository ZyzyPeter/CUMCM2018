import pandas as pd
import numpy as np

class QLearning(object):
	def __init__(self,actions,learning_rate=0.01,reward_decay=0.9,e_greedy=0.9,path=None):
		self.actions = actions  # a list
		self.lr = learning_rate  # 学习率
		self.gamma = reward_decay  # 奖励衰减
		self.epsilon = e_greedy  # 贪婪度
		if path==None:
			self.q_table = pd.DataFrame(columns=self.actions, dtype=np.float64)  # 初始 q_table
		else:
			self.q_table=pd.read_csv(path,index_col=0)
			self.q_table.columns=self.actions

	def action_limit(self,s,actions):
		# 根据环境设置动作限制条件
		actions_=[_ for _ in actions]
		time=s[0]
		rgv_info=s[1]
		cnc_info=s[2]
		cnc_num=list(range(2*int(rgv_info['loc'])-2,2*int(rgv_info['loc']))) # rgv附近两台cnc的序号
		cnc_1_action=[_ for _ in range(6+(cnc_num[0]+1)*3-2,6+(cnc_num[0]+1)*3+1)] #cnc序号对应的上下料动作
		cnc_2_action = [_ for _ in range(6 + (cnc_num[1]+1) * 3 - 2, 6 + (cnc_num[1]+1) * 3 + 1)]
		cnc_action=[cnc_1_action,cnc_2_action]

		for i in range(7,31):#将rgv触碰不到的cnc动作都排除
			if i not in cnc_1_action+cnc_2_action:
				actions_.remove(i)

		actions_.remove(31) #先将清洗动作去除
		actions_.remove(32) #先将放料动作去除

		if rgv_info['loc']==1: #移动限制规则
			actions_.remove(2)
			actions_.remove(4)
			actions_.remove(6)
		elif rgv_info['loc']==2:
			actions_.remove(5)
			actions_.remove(4)
			actions_.remove(6)
		elif rgv_info['loc']==3:
			actions_.remove(5)
			actions_.remove(3)
			actions_.remove(6)
		elif rgv_info['loc']==4:
			actions_.remove(5)
			actions_.remove(3)
			actions_.remove(1)
		if rgv_info['material_type']==1 or rgv_info['material_type']==5 or rgv_info['material_type']==3: #身上有携带工料即刻清洗
			actions_=[31]
		if rgv_info['material_type']==2 or rgv_info['material_type']==6: # 身上有可放置工料即刻放置
			actions_=[32]

		if rgv_info['material_type']!=0: # rgv携带工料不为空时
			for num in cnc_num:
				if cnc_info['work_type'][num]==0 or cnc_info['work_type'][num]==1: # 此时cnc若为0或者1工种则不允许上料，下料，上下料
					try:
						actions_.remove(cnc_action[num % 2][0])
						actions_.remove(cnc_action[num % 2][1])
						actions_.remove(cnc_action[num % 2][2])
					except ValueError:
						pass
		if rgv_info['material_type']!=4:
			for num in cnc_num:
				if cnc_info['work_type'][num] == 2 :  # 此时cnc若为2工种则不允许上下料
					for action_num in cnc_action[num%2]:
						try:
							actions_.remove(action_num)
						except ValueError:
							pass
		for num in cnc_num:
			# 先将下料动作去除
			try:
				actions_.remove(cnc_action[num%2][1])
			except ValueError:
				pass
			if cnc_info['status'][num]!=0:#如果cnc不空闲，不允许上下料
				for action_num in cnc_action[num%2]:
					try:
						actions_.remove(action_num)
					except ValueError:
						pass
			if cnc_info['material_type'][num]==0: #如果cnc上没有工料，不允许下料和上下料
				try:
					actions_.remove(cnc_action[num%2][2])
				except ValueError:
					pass
			elif cnc_info['material_type'][num]!=0: #如果cnc上有工料，不允许上料
				try:
					actions_.remove(cnc_action[num%2][0])
				except ValueError:
					pass
		print(actions_)

		return actions_

	def choose_action_QL(self,s):
		o=self.state_extract(s) # 从环境中提取观察状态
		self.check_state_exist(o)  # 检测本 state 是否在 q_table 中存在
		actions=self.action_limit(s,self.actions)
		# 选择action
		if np.random.uniform()<self.epsilon: #选择Q value最高的action
			state_action=self.q_table.loc[str(o),actions]

			# 同一个 state, 可能会有多个相同的 Q action value, 所以我们打乱顺序
			action = np.random.choice(state_action[state_action == np.max(state_action)].index)

		else:
			action=np.random.choice(actions)
		return action

	def choose_action_static(self,s):
		o = self.state_extract(s)  # 从环境中提取观察状态
		self.check_state_exist(o)  # 检测本 state 是否在 q_table 中存在
		actions = self.action_limit(s, self.actions)
		# 选择action
		# 选择Q value最高的action
		state_action = self.q_table.loc[str(o), actions]
		# 同一个 state, 可能会有多个相同的 Q action value, 所以我们打乱顺序
		action = np.random.choice(state_action[state_action == np.max(state_action)].index)

		return action

	def learn(self,s,a,r,s_):
		o = self.state_extract(s) # 从环境中提取观察状态
		o_ = self.state_extract(s_)  # 从环境中提取观察状态
		self.check_state_exist(o_) #检测q_table中是否存在s_
		q_predict = self.q_table.loc[str(o), a]
		if o_ != 'terminal':
			q_target = r + self.gamma * self.q_table.loc[str(o_), :].max()  # 下个 state 不是 终止符
		else:
			q_target = r  # 下个 state 是终止符
		self.q_table.loc[str(o), a] += self.lr * (q_target - q_predict)  # 更新对应的 state-action 值

	def check_state_exist(self, state):
		if str(state) not in self.q_table.index:
			# append new state to q table
			self.q_table = self.q_table.append(
				pd.Series(
					[0] * len(self.actions),
					index=self.q_table.columns,
					name=str(state),
				)
			)

	def state_extract(self,s):# 从环境因素中提取观察状态
		if s=='terminal':
			return s
		state=[]
		rgv_info=s[1]
		cnc_info=s[2]
		state.append(int(rgv_info['loc']))
		state.append(int(rgv_info['material_type']))
		for i in range(8):
			state.append(int(cnc_info['status'][i]))
			state.append(int(cnc_info['work_type'][i]))
			state.append(int(cnc_info['material_type'][i]))
		state=np.array(state)
		return state