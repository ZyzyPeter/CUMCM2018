import numpy as np
import pandas as pd

def cal_best_m(n = 8,process = 560,move_1 = 20,move_2 = 33, move_3 = 46,exchange_1 = 28,exchange_2 = 31,wash = 25):
    move = [0,0,move_1,move_1,move_2,move_2,move_3,move_3]
    Init = np.ceil(n/2)*exchange_1+np.floor(n/2)*exchange_2+(np.ceil(n/2)-1)*move_1 +move[n-1]
    wait1 = max(process - Init,0)
    Loop = Init + n*wash
    wait2 = max(process-Loop,0)
    time = 0
    max_loop = (8*3600- Init-wait1)*n/(Loop+wait2)
    print(max_loop)
    step = [i for i in range(1,n+1)]
    exchange = [exchange_1,exchange_2]
    num = [] # 记录CNC编号
    start = [] # 记录CNC上料开始时间
    end = [] # 记录CNC下料开始时间
    for i in step:
        num.append(i)
        start.append(time)
        if i % 2 == 1:
            time +=exchange[0]
        else:
            time += exchange[1]
        if i == n:
            time += move[n-1]
            break
        if i in [2,4,6]:
            time += move_1
    time += wait1
    while time < 8*3600:
        for i in step:
            num.append (i)
            start.append (time)
            end.append(time)
            time+=wash
            if i % 2 == 1:
                time += exchange[0]
            else:
                time += exchange[1]
            if i ==  n:
                time += move[n - 1]
                break
            if i in [2, 4, 6]:
                time += move_1
        time += wait2
    for i in range(len(start)-len(end)):
        end.append(np.nan)
    df  = pd.DataFrame({'加工CNC编号':num,'上料开始时间':start,'下料开始时间':end},columns = ['加工CNC编号','上料开始时间','下料开始时间'])
    print(df)
    df.to_csv('1.3.csv')# 输出结果
if __name__ == '__main__':
    cal_best_m(n = 8,process = 545,move_1 = 18,move_2 = 32, move_3 = 46,exchange_1 = 27,exchange_2 = 32,wash = 25)


