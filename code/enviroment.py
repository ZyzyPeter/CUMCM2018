import tkinter as tk
import numpy as np
import time
import sys
import pyglet

TOTAL_TIME = 28800  # 8个小时时间
PUT = 25  # RGV清洗放置作业时间
MOVE1 = 18 # RGV移动一个单位的时间
MOVE2 = 32  # RGV移动两个单位的时间
MOVE3 = 46 # RGV移动三个单位的时间
CNC_1 = 545 # CNC加工完成一道工序时间
CNC_2_1 = 455  # CNC加工完成两道工序中第一道工序时间
CNC_2_2 = 182  # CNC加工完成两道工序中第二道工序时间
EXCHANGE1 = 27  # RGV为奇数编号CNC完成一次上下料时间
EXCHANGE2 = 32  # RGV为偶数编号CNC完成一次上下料时间

CNC_STATUS = [0, 0, 0, 0, 0, 0, 0, 0]  # CNC初始工作状态
CNC_LOC = [1, 2, 3, 4, 5, 6, 7, 8]  # CNC位置标识序列
CNC_WORK_TYPE = [0,0,0,0,0,0,0,0]  # CNC工种 0,1,2 对应一道工序，二道工序第一道，二道工序第二道
CNC_WORK_TIME_TYPE=[CNC_1,CNC_2_1,CNC_2_2]

RGV_INITIAL_LOC=1

RGV_HEIGHT=50
RGV_WIDTH=100
CNC_HEIGHT=100
CNC_WIDTH=100

ERROR_RATE=0.01
FIX_TIME=600

class RGVaction(object):
	def __init__(self,time,move,action_type,cnc_num):
		'''
		time rgv完成这个动作所消耗的时间
		move rgv的行动步数 -3 - +3
		action_type 对应0，1，2，3，4，5，6分别表示 等待，移动，上料，下料，上下料，清洗作业,放置下料
		'''
		self.consume_time=time
		self.move=move
		self.action_type=action_type
		self.cnc_num=cnc_num


class Env():
	viewer = None  # viewer默认为空
	score=0
	time=TOTAL_TIME #总共的时间，在回合结束前不断消耗
	material_num=1 #工料编号
	work_list=[] #加工成功的工料列表
	error_list=[] #故障的工料列表
	material_dict={} #工料表
	action_space = [
		RGVaction(1, 0, 0, -1),
		RGVaction(MOVE1, 1, 1, -1),
		RGVaction(MOVE1, -1, 1, -1),
		RGVaction(MOVE2, 2, 1, -1),
		RGVaction(MOVE2, -2, 1, -1),
		RGVaction(MOVE3, 3, 1, -1),
		RGVaction(MOVE3, -3, 1, -1),  # 6
		RGVaction(EXCHANGE1, 0, 2, 0),
		RGVaction(EXCHANGE1, 0, 3, 0),
		RGVaction(EXCHANGE1, 0, 4, 0),
		RGVaction(EXCHANGE2, 0, 2, 1),
		RGVaction(EXCHANGE2, 0, 3, 1),
		RGVaction(EXCHANGE2, 0, 4, 1),
		RGVaction(EXCHANGE1, 0, 2, 2),
		RGVaction(EXCHANGE1, 0, 3, 2),
		RGVaction(EXCHANGE1, 0, 4, 2),
		RGVaction(EXCHANGE2, 0, 2, 3),
		RGVaction(EXCHANGE2, 0, 3, 3),
		RGVaction(EXCHANGE2, 0, 4, 3),
		RGVaction(EXCHANGE1, 0, 2, 4),
		RGVaction(EXCHANGE1, 0, 3, 4),
		RGVaction(EXCHANGE1, 0, 4, 4),
		RGVaction(EXCHANGE2, 0, 2, 5),
		RGVaction(EXCHANGE2, 0, 3, 5),
		RGVaction(EXCHANGE2, 0, 4, 5),
		RGVaction(EXCHANGE1, 0, 2, 6),
		RGVaction(EXCHANGE1, 0, 3, 6),
		RGVaction(EXCHANGE1, 0, 4, 6),
		RGVaction(EXCHANGE2, 0, 2, 7),
		RGVaction(EXCHANGE2, 0, 3, 7),
		RGVaction(EXCHANGE2, 0, 4, 7),
		RGVaction(0, 0, 5, -1),
		RGVaction(PUT, 0, 6, -1)
	]

	def __init__(self):
		self.rgv_info=RGVenv().rgv_info
		self.cnc_info=CNCenv().cnc_info
		self.n_actions=len(self.action_space)

	def update(self,observation):
		self.time=observation[0]
		self.rgv_info=observation[1]
		self.cnc_info=observation[2]
		self.material_num=observation[3]
		self.work_list=observation[4]
		self.error_list=observation[5]
		self.material_dict = observation[6]

	def step(self, rgv_action):
		FIX_TIME=np.random.randint(600,1200)#随机产生一个修理时间

		rgv_action=self.action_space[rgv_action]

		done=False
		r=0

		rgv_info=self.rgv_info.copy()
		time=self.time
		cnc_info=self.cnc_info.copy()
		material_num=self.material_num
		work_list=self.work_list.copy()
		error_list=self.error_list.copy()
		material_dict=self.material_dict.copy()

		consume=rgv_action.consume_time #rgv完成这个动作所消耗的时间
		move=rgv_action.move #rgv的行动步数 -3 - +3
		work=rgv_action.action_type # action_type 对应0，1，2，3，4，5，6分别表示 等待，移动，上料，下料，上下料，清洗作业,放置下料

		rgv_info['loc']=rgv_info['loc']+move
		rgv_info['move']=move

		time=time-consume
		r-=consume*0.01

		for cnc in range(8):
			if cnc_info['status'][cnc]==0:
				r-=1
			if cnc_info['over_time'][cnc]>=time:
				cnc_info['status'][cnc]=0


		if work==6:
			material = material_dict[int(rgv_info['material_num'])]
			if rgv_info['material_type']==2:
				rgv_info['material_type']=0
			elif rgv_info['material_type']==6:
				rgv_info['material_type']=0
			self.score+=1
			print(material_dict)
			work_list.append(material) #将工料添加进完成列表
			material_dict.pop(int(rgv_info['material_num'])) #将工料从工料表中删除
			rgv_info['material_num']=0 #清除RGV上的工料
			r=10
		elif work==2: # 上料
			rgv_info['material_type'] = 0
			cnc=rgv_action.cnc_num
			print('cnc编号:',cnc+1)

			if cnc_info['work_type'][cnc]==0:# 如果是需要一道工序的生料
				cnc_info['status'][cnc]=1
				cnc_info['material_type'][cnc]=1
				# 增加工料
				material=Material(material_num,time+consume,0)
				material.cnc1=cnc+1
				material_dict[material.num]=material
				cnc_info['material_num'][cnc] = material.num
				material_num+=1
			elif cnc_info['work_type'][cnc]==1:# 如果是需要两道工序的生料
				cnc_info['status'][cnc] = 2
				cnc_info['material_type'][cnc] = 3
				# 增加工料
				material = Material(material_num, time + consume,1)
				material.cnc1 = cnc + 1
				material_dict[material.num] = material
				cnc_info['material_num'][cnc] = material.num
				material_num += 1

			elif cnc_info['work_type'][cnc]==2:  # 如果是需要两道工序的熟料
				cnc_info['status'][cnc] = 3
				cnc_info['material_type'][cnc] = 5
				#转移工料
				material_dict[int(rgv_info['material_num'])].up_time2=time+consume
				material_dict[int(rgv_info['material_num'])].cnc2 = cnc + 1
				cnc_info['material_num'][cnc]=int(rgv_info['material_num'])
				rgv_info['material_num']=0

			if np.random.uniform() < ERROR_RATE:  # 如果发生了故障
				cnc_info['material_type'][cnc] = 0
				cnc_info['status'][cnc] = 4
				#记录故障工料
				material=material_dict[int(cnc_info['material_num'][cnc])]
				material.error_cnc=cnc+1

			if cnc_info['status'][cnc]!=4:
				cnc_info['over_time'][cnc]=time-cnc_info['work_time'][cnc] #标识cnc工作完成的时间点
			else:
				cnc_info['over_time'][cnc]=time-FIX_TIME-np.random.randint(0,cnc_info['work_time'][cnc]) #标识故障修理完的时间点
				material = material_dict[int(cnc_info['material_num'][cnc])]
				material.error_end=time-FIX_TIME-np.random.randint(0,cnc_info['work_time'][cnc]) #在工料上记录故障修理完成时间点
				material.error_start=time+consume
				error_list.append(material) #将工料添加至故障工料队列
				material_dict.pop(int(cnc_info['material_num'][cnc]))
			r=1
		elif work==4: #上下料
			cnc = rgv_action.cnc_num

			cache=int(cnc_info['material_num'][cnc]) #缓存工料

			if cnc_info['work_type'][cnc] == 0:  # 如果是需要一道工序的生料
				cnc_info['status'][cnc] = 1
				rgv_info['material_type']=1 #取回完成一道工序的熟料
				cnc_info['material_type'][cnc] = 1
				# 增加工料
				material = Material(material_num, time + consume,0)
				material.cnc1 = cnc + 1
				material_dict[material.num] = material
				cnc_info['material_num'][cnc] = material.num
				material_num += 1
				material_dict[cache].down_time1=time+consume

			elif cnc_info['work_type'][cnc] == 1:  # 如果是需要两道工序的生料
				cnc_info['status'][cnc] = 2
				rgv_info['material_type'] = 3 #取回完成一道工序需要第二道工序的熟料
				cnc_info['material_type'][cnc] = 3
				# 增加工料
				material = Material(material_num, time + consume,1)
				material.cnc1 = cnc + 1
				material_dict[material.num] = material
				cnc_info['material_num'][cnc] = material.num
				material_num += 1
				material_dict[cache].down_time1 = time + consume

			elif rgv_info['material_type'] == 4 and cnc_info['work_type'][cnc] == 2:  # 如果是需要两道工序并且被清洗过后的熟料
				cnc_info['status'][cnc] = 3
				rgv_info['material_type'] = 5 #取回完成两道工序的熟料
				cnc_info['material_type'][cnc] = 5
				# 转移工料
				material_dict[int(rgv_info['material_num'])].up_time2 = time + consume
				material_dict[int(rgv_info['material_num'])].cnc2 = cnc + 1
				cnc_info['material_num'][cnc] = int(rgv_info['material_num'])
				material_dict[cache].down_time2 = time + consume

			# 转移工料
			rgv_info['material_num'] = cache

			if np.random.uniform() < ERROR_RATE:  # 如果发生了故障
				cnc_info['material_type'][cnc] = 0
				cnc_info['status'][cnc] = 4
				# 记录故障工料
				material = material_dict[int(cnc_info['material_num'][cnc])]
				material.error_cnc = cnc + 1

			if cnc_info['status'][cnc] != 4:
				cnc_info['over_time'][cnc] = time - cnc_info['work_time'][cnc]  # 标识cnc工作完成的时间点
			else:
				cnc_info['over_time'][cnc] = time - FIX_TIME-np.random.randint(0,cnc_info['work_time'][cnc])  # 标识故障修理完的时间点
				material = material_dict[int(cnc_info['material_num'][cnc])]
				material.error_end = time - FIX_TIME -np.random.randint(0,cnc_info['work_time'][cnc]) # 在工料上记录故障修理完成时间点
				material.error_start = time + consume
				error_list.append(material)  # 将工料添加至故障工料队列
				material_dict.pop(int(cnc_info['material_num'][cnc]))
			r=3
		elif work==5:
			if rgv_info['material_type']==1:
				rgv_info['material_type']=2
			elif rgv_info['material_type']==3:
				rgv_info['material_type']=4
			elif rgv_info['material_type']==5:
				rgv_info['material_type']=6
			r=5

		if time<=0:
			done=True
			s_='terminal'
		else:
			s_=[time,rgv_info,cnc_info,material_num,work_list,error_list,material_dict]

		return s_,r,done


	def reset(self):
		self.rgv_info['move'] = 0
		self.rgv_info['loc'] = RGV_INITIAL_LOC
		self.rgv_info['material_type'] = 0
		# 携带的物料编号，0表示没有携带
		self.rgv_info['material_num'] = 0
		self.time=TOTAL_TIME
		self.score=0
		self.cnc_info['status'] = 0
		self.cnc_info['over_time'] = 0
		# material_type 取值 0，1，2，3，4，5，6 表示 无工料，熟料，成料，需要第二道加工并已经过一道加工的熟料，需要第二道加工并已经过一道加工并且清洗过后的熟料，二道加工完成的熟料，二道加工并且被清洗过后的成料
		self.cnc_info['material_type'] = 0
		# 携带的物料编号，0表示没有携带
		self.cnc_info['material_num'] = 0
		self.material_num = 1
		self.work_list = []
		self.error_list = []
		self.material_dict={}
		for cnc, work_type in zip(range(8), CNC_WORK_TYPE):
			self.cnc_info['work_time'][cnc] = CNC_WORK_TIME_TYPE[work_type]
			self.cnc_info['work_type'][cnc] = work_type

		return [self.time,self.rgv_info,self.cnc_info,self.material_num,self.work_list,self.error_list]

	def render(self,observation):
		if self.viewer is None:  # 若没有viewer则生成一个
			self.viewer = Viewer(rgv_info=self.rgv_info,cnc_info=self.cnc_info)
		self.viewer.render(observation)  # 使用viewer中的render功能

	def sample_action(self):
		action=RGVaction(10,1,1,-1)
		return action


	def destroy(self,RL,path):
		RL.q_table.to_csv(path)

class RGVenv(object):
	state_dim=4
	action_dim=4

	def __init__(self):
		self.rgv_info=np.zeros(
			1,dtype=[('move',np.int32),
					 ('loc',np.int32),
					 ('material_type',np.int32),
					 ('material_num',np.int32)]
		)
		# move取值-3,-2,-1,0,1,2,3
		self.rgv_info['move']=0
		# loc取值1,2,3,4
		self.rgv_info['loc']=RGV_INITIAL_LOC
		# material_type 取值 0，1，2，3，4，5，6 表示 无工料，熟料，成料，需要第二道加工并已经过一道加工的熟料，需要第二道加工并已经过一道加工并且清洗过后的熟料，二道加工完成的熟料，二道加工并且被清洗过后的成料
		self.rgv_info['material_type'] = 0
		#携带的物料编号，0表示没有携带
		self.rgv_info['material_num']=0

class CNCenv(object):

	def __init__(self):
		self.cnc_info=np.zeros(
			8,dtype=[('status',np.int32),
					 ('over_time',np.int32),
					 ('work_time',np.int32),
					 ('work_type',np.int32),
					 ('material_type',np.int32),
					 ('material_num',np.int32)]
		)
		# 0,1,2,3,4 空闲，加工，加工1，加工2，故障
		self.cnc_info['status']=0 #所有cnc起初都处于空闲状态
		self.cnc_info['over_time']=0
		# material_type 取值 0，1，2，3，4，5，6 表示 无工料，熟料，成料，需要第二道加工并已经过一道加工的熟料，需要第二道加工并已经过一道加工并且清洗过后的熟料，二道加工完成的熟料，二道加工并且被清洗过后的成料
		self.cnc_info['material_type']=0
		# 携带的物料编号，0表示没有携带
		self.cnc_info['material_num'] = 0
		for cnc,work_type in zip(range(8),CNC_WORK_TYPE): #初始化所有cnc的工种
			self.cnc_info['work_time'][cnc]=CNC_WORK_TIME_TYPE[work_type]
			self.cnc_info['work_type'][cnc] = work_type


class Material(object):
	def __init__(self,num,up_time,type):
		self.num=num
		self.up_time1=up_time
		self.down_time1=0
		self.up_time2=0
		self.down_time2=0
		self.cnc1=0
		self.cnc2=0
		self.type=type
		self.error_cnc=0
		self.error_start=0
		self.error_end=0

class RGV(object):
	width = RGV_WIDTH
	height = RGV_HEIGHT

	def __init__(self, location, status):
		# location 包括 1，2，3，4 标识RGV在通道上的第几个格子
		self.location = location
		# status 包括 0(等待),1(清洗)
		self.status = status
		# 携带的物料
		self.material_status=None

class CNC(object):
	width = CNC_WIDTH
	height = CNC_HEIGHT

	def __init__(self, location, status, work_type):
		# 1-8对应8个cnc的位置
		self.location = location
		# status 包括 0（空闲），1（工作），2（故障）
		self.status = status
		# work_type 表示工种，0（一道工序类型），1（两道工序第一种刀片），2（两道工序第二种刀片）
		self.work_type = work_type


class Viewer(pyglet.window.Window):
	def __init__(self,rgv_info,cnc_info):
		# 画出RGV，CNC，轨道

		# 创建窗口的继承
		# vsync 如果是 True, 按屏幕频率刷新, 反之不按那个频率
		super(Viewer, self).__init__(width=400, height=250, resizable=False, caption='RGV', vsync=False)

		# 窗口背景颜色
		pyglet.gl.glClearColor(1, 1, 1, 1)

		# 将作图信息放入batch
		self.batch = pyglet.graphics.Batch()  # display whole batch as once

		# 生成RGV参数表
		cnc = CNC(1, 0, 0)
		rgv = RGV(RGV_INITIAL_LOC, 0)

		# 添加RGV
		self.rgv = self.batch.add(
			4, pyglet.gl.GL_QUADS, None,  # 4 corners
			('v2f', [(rgv.location - 1) * rgv.width, cnc.height,  # x1, y1
					 (rgv.location - 1) * rgv.width, cnc.height + rgv.height,  # x2, y2
					 rgv.location * rgv.width, cnc.height + rgv.height,  # x3, y3
					 rgv.location * rgv.width, cnc.height,  # x4, y4
					 ]),
			('c3B', (86, 109, 249) * 4)  # color
		)

		# 添加CNC
		self.cncs = []
		for i, j, k in zip(CNC_LOC, CNC_STATUS, CNC_WORK_TYPE):
			cnc = CNC(i, j, k)
			if cnc.location == 1 or cnc.location == 2:
				x = 0
			elif cnc.location == 3 or cnc.location == 4:
				x = 1
			elif cnc.location == 5 or cnc.location == 6:
				x = 2
			else:
				x = 3
			y = cnc.location % 2
			self.cncs.append(
				self.batch.add(
					4, pyglet.gl.GL_QUADS, None,  # 4 corners
					('v2f', [x * cnc.width, y * (rgv.height + cnc.height),
							 x * cnc.width, y * (rgv.height + cnc.height) + cnc.height,
							 x * cnc.width + cnc.width, y * (rgv.height + cnc.height) + cnc.height,
							 x * cnc.width + cnc.width, y * (rgv.height + cnc.height)]),
					('c3B', [249, 86 + 2 * cnc.work_type, 86 + 2 * cnc.work_type,
							 249, 86 + 2 * cnc.work_type, 86 + 2 * cnc.work_type,
							 150, 86 + 2 * cnc.work_type, 86 + 2 * cnc.work_type,
							 150, 86 + 2 * cnc.work_type, 86 + 2 * cnc.work_type])  # color
				)
			)
		# 添加RGV信息
		self.rgv_info=rgv_info
		self.cnc_info=cnc_info

	def render(self,observation):
		# 刷新并呈现在屏幕上
		self._update_RGV(observation[1])  # 更新RGV内容
		self._update_CNC(observation[2])  # 更新CNC内容 （暂时没有变化）
		self.switch_to()
		self.dispatch_events()
		self.dispatch_event('on_draw')
		self.flip()

	def on_draw(self):
		# 刷新RGV的位置，状态，CNC的状态
		self.clear()  # 清屏
		self.batch.draw()  # 画上 batch 里面的内容

	def _update_RGV(self,rgv_info):
		# 更新RGV的位置，状态信息
		loc=rgv_info['loc']

		#RGV当前坐标信息
		x1,y1=(loc-1)*RGV_WIDTH,CNC_HEIGHT
		x2,y2=(loc-1)*RGV_WIDTH,CNC_HEIGHT+RGV_HEIGHT
		x3,y3=loc*RGV_WIDTH,CNC_HEIGHT+RGV_HEIGHT
		x4,y4=loc*RGV_WIDTH,CNC_HEIGHT

		# RGV移动
		self.rgv.vertices=([x1,y1,
							x2,y2,
							x3,y3,
							x4,y4])

	def _update_CNC(self,cnc_info):
		# 更新CNC的状态信息
		status=cnc_info['status']
		work_type=cnc_info['work_type']
		color_map={
			0:0,
			1:100,
			2:150,
			3:200,
			4:255
		}
		# CNC状态改变
		for i in range(8):
			self.cncs[i].colors[0]=color_map[int(status[i])]


