import pandas as pd
import matplotlib.pyplot as plt

def draw_p1c1_r():
	record=pd.read_csv('result/record/param1case1_record.csv')
	plt.xlabel('Episode')
	plt.ylabel('score')
	plt.plot(record)
	plt.show()

def draw_p1c1_pr_r():
	record = pd.read_csv('result/record/param1case1_predict_record.csv')
	plt.xlabel('Episode')
	plt.ylabel('score')
	plt.plot(record)
	plt.show()

def draw_p1c2_r():
	record = pd.read_csv('result/record/param1case2_record.csv')
	plt.xlabel('Episode')
	plt.ylabel('score')
	plt.plot(record)
	plt.show()

def draw_p1c3_1_r():
	record = pd.read_csv('result/record/param1case3_1_record.csv')
	plt.xlabel('Episode')
	plt.ylabel('score')
	plt.plot(record)
	plt.show()

def draw_p1c3_2_r():
	record = pd.read_csv('result/record/param1case3_2_record.csv')
	plt.xlabel('Episode')
	plt.ylabel('score')
	plt.plot(record)
	plt.show()
if __name__=="__main__":
	draw_p1c3_2_r()