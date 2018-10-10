import numpy as np
import itertools

def  __work_type_genarate_all__():
	j = 1
	CNC_WORK_TYPE = []
	while j < 8:
		list1 = [1 for count in range(j)]
		extend_list = [2 for count in range(8-len(list1))]
		list1.extend(extend_list)
		list2 = []
		for i in range (1, len (list1) + 1):
			iter = itertools.permutations (list1, i)
			list2.append (list (iter))
		CNC_WORK_TYPE.extend(list(set(list2[7])))
		j = j+ 1
	return CNC_WORK_TYPE
def __smart_work_type_genarate__(CNC_2_1 , CNC_2_2,Type = 1):
	ALL = np.array(__work_type_genarate_all__())
	if Type == 1:
		return ALL
	if CNC_2_1 < CNC_2_2:		# 需求更多的刀片2
		mask = np.where(np.sum(ALL-1,axis=1)<4,False,True)
	else:		# 需求更多的刀片1
		mask = np.where(np.sum(ALL-1,axis=1)<=4,True,False)
	return ALL[mask]
def  smart_work_type_genarate(CNC_2_1 , CNC_2_2,Type = 1):
	ALL = __smart_work_type_genarate__(CNC_2_1 , CNC_2_2,Type)
	for group in ALL:
		yield group

