import numpy as np
import pandas as pd


ExcelFile = pd.read_excel('./testResult3.xls', header=None, index=None).fillna(0)
y = np.array(ExcelFile.values)
row = y.shape[0]
A_avg_ratio = 0
T_avg_ratio = 0
D_avg_ratio = 0
for i in range(0, row):
    #print(str(i))
    if i % 3 == 2:
        D_avg_ratio = D_avg_ratio + y[i, 3]
    elif i % 3 == 1:
        T_avg_ratio = T_avg_ratio + y[i, 3]
    else:
        A_avg_ratio = A_avg_ratio + y[i, 3]
    #print('Action 平均分：' + str(A_avg_ratio) + '\nTarget 平均分：' + str(T_avg_ratio) + '\nData 平均分： ' + str(D_avg_ratio))

print('Action 平均分：'+str(A_avg_ratio/row*3)+'\nTarget 平均分：'+str(T_avg_ratio/row*3)+'\nData 平均分： '+str(D_avg_ratio/row*3))
# 2：
# Action 平均分：0.9558389597399344
# Target 平均分：0.9454459847547629
# Data 平均分： 0.9532556383657615

# 3：
# Action 平均分：0.9558389597399344
# Target 平均分：0.9914810136622958
# Data 平均分： 0.9532556383657615
