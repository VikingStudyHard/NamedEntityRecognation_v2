import xlwt
import numpy as np
import pandas as pd
from predict import predict
import Levenshtein  # pip install python-Levenshtein
from test_data_prepare import release


def compare():
    ExcelFile = pd.read_excel('./RESULT_V5.xls', header=None, index=None).fillna(0)
    # ExcelFile = pd.read_excel('./ResultTest.xlsx', header=None, index=None).fillna(0)
    y = np.array(ExcelFile.values)
    row = y.shape[0]
    num = 0
    xls = xlwt.Workbook()
    sheet = xls.add_sheet('sheet1', cell_overwrite_ok=True)
    j = 0
    A_0 = 0
    A_1 = 0
    A_x = 0
    T_0 = 0
    T_1 = 0
    T_x = 0
    D_0 = 0
    D_1 = 0
    D_x = 0
    for i in range(0, row):
        print("row:" + str(i))
        print(str(y[i, 0]))
        resultAction, resultTarget, resultData = predict(
            str(y[i, 0]).replace('\t', '').replace('\n', '').replace('\r', ''))
        initAction = str(y[i, 1]).replace("，", "").replace(",", "").replace('\t', '').strip()
        initTarget = str(y[i, 2]).replace("，", "").replace(",", "").replace('\t', '').strip()
        if len(str(y[i, 3])) > 0:
            initData = str(y[i, 3]).replace("，", "").replace('\t', '').strip()
        else:
            initData = str(y[i, 3])
        resultAction = str(resultAction).replace('***', '')
        resultTarget = str(resultTarget).replace('***', '').replace("和", "").replace("、", "")
        resultData = "".join(resultData).replace('***', '')

        Aratio = Levenshtein.ratio(initAction, str(resultAction))
        Tratio = Levenshtein.ratio(initTarget, str(resultTarget))
        Dratio = Levenshtein.ratio(initData, str(resultData))
        # print(Aratio, Tratio)
        if ((resultAction in initAction) or (initAction in resultAction)) and (resultTarget in initTarget):
            num = num + 1

        line = ''.join(
            str(y[i, 0]) + '\n' + 'action:' + initAction + '\t' + 'pAction:' + str(resultAction) + '\t' + str(
                Aratio) + '\n' + 'target:' + initTarget + '\t' + 'pTarget:' + str(resultTarget) + '\t' + str(
                Tratio) + '\n' + 'data:' + initData + '\t' + 'pData:' + str(resultData) + '\t' + str(Dratio)) + '\n'

        sheet.write(j, 0, str(y[i, 0]))
        sheet.write(j, 1, initAction)
        sheet.write(j, 2, str(resultAction))
        sheet.write(j, 3, str(Aratio))
        if Aratio == 1:
            A_1 = A_1 + 1
        elif Aratio == 0:
            A_0 = A_0 + 1
        else:
            A_x = A_x + 1
        j += 1
        sheet.write(j, 1, initTarget)
        sheet.write(j, 2, str(resultTarget))
        sheet.write(j, 3, str(Tratio))
        if Tratio == 1:
            T_1 = T_1 + 1
        elif Tratio == 0:
            T_0 = T_0 + 1
        else:
            T_x = T_x + 1
        j += 1
        sheet.write(j, 1, initData)
        sheet.write(j, 2, str(resultData))
        sheet.write(j, 3, str(Dratio))
        if Dratio == 1:
            D_1 = D_1 + 1
        elif Dratio == 0:
            D_0 = D_0 + 1
        else:
            D_x = D_x + 1
        j += 1
    release()
    xls.save('testResult_lstmcrf+pos+parser.xls')
    result = num / row

    print(str(num))

    print(str(A_0) + ' ' + str(A_x) + " " + str(A_1))
    A_P = A_1 / (A_1 + A_x)
    A_R = A_1 / row
    A_F = (2 * A_P * A_R) / (A_P + A_R)
    print('Action P' + str(A_P))
    print('Action R' + str(A_R))
    print('Action F' + str(A_F))

    print(str(T_0) + ' ' + str(T_x) + " " + str(T_1))
    T_P = T_1 / (T_1 + T_x)
    T_R = T_1 / row
    T_F = (2 * T_P * T_R) / (T_P + T_R)
    print('Target P' + str(T_P))
    print('Target R' + str(T_R))
    print('Target F' + str(T_F))

    print(str(D_0) + ' ' + str(D_x) + " " + str(D_1))
    D_P = D_1 / (D_1 + D_x)
    D_R = D_1 / row
    D_F = (2 * D_P * D_R) / (D_P + D_R)
    print('Data P' + str(D_P))
    print('Data R' + str(D_R))
    print('Data F' + str(D_F))
    print('result:' + str(result))

compare()
ExcelFile = pd.read_excel('./testResult_lstmcrf+pos+parser.xls', header=None, index=None).fillna(0)
y = np.array(ExcelFile.values)
row = y.shape[0]
A_avg_ratio = 0
T_avg_ratio = 0
D_avg_ratio = 0
for i in range(0, row):
    # print(str(i))
    if i % 3 == 2:
        D_avg_ratio = D_avg_ratio + y[i, 3]
    elif i % 3 == 1:
        T_avg_ratio = T_avg_ratio + y[i, 3]
    else:
        A_avg_ratio = A_avg_ratio + y[i, 3]
    # print('Action 平均分：' + str(A_avg_ratio) + '\nTarget 平均分：' + str(T_avg_ratio) + '\nData 平均分： ' + str(D_avg_ratio))

print('Action 平均分：' + str(A_avg_ratio / row * 3) + '\nTarget 平均分：' + str(
    T_avg_ratio / row * 3) + '\nData 平均分： ' + str(D_avg_ratio / row * 3))

# 658
# 4 7 692
# Action P0.9899856938483548
# Action R0.984352773826458
# Action F0.9871611982881597
# 35 42 626
# Target P0.937125748502994
# Target R0.8904694167852063
# Target F0.9132020423048869
# 21 5 677
# Data P0.9926686217008798
# Data R0.9630156472261735
# Data F0.9776173285198556
# result:0.9359886201991465
# Action 平均分：0.990990990990991
# Target 平均分：0.9369805067866004
# Data 平均分： 0.9677290072026914