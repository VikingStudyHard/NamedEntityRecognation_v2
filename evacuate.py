import numpy as np
import pandas as pd


ExcelFile = pd.read_excel('./testResult_v5.xls', header=None, index=None).fillna(0)
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

# 4：
# Action 平均分：0.9510740740740733
# Target 平均分：0.991525901194748
# Data 平均分： 0.9505469860483153

# 5
# result:0.8969798657718121
# Action 平均分：0.9590223219852843
# Target 平均分：0.9892203871462706
# Data 平均分： 0.952364617282101
#


# 6
# 宾 BIESO标注
# result:0.8916107382550336
# Action 平均分：0.9584368335215148
# Target 平均分：0.9900911169469266
# Data 平均分： 0.9533233265730978

# result:0.757847533632287
# Action 平均分：0.9861932938856024
# Target 平均分：0.9932885528027224
# Data 平均分： 0.9686766225227765

# result:0.8571428571428571
# Action 平均分：1.0
# Target 平均分：0.9938533869906416
# Data 平均分： 0.9830700798838053