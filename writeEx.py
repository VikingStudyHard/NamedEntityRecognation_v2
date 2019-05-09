import xlwt
import numpy as np
import pandas as pd
from predict import predict
import Levenshtein  # pip install python-Levenshtein
from test_data_prepare import release


def compare():
    ExcelFile = pd.read_excel('./RESULT_V4.xls', header=None, index=None).fillna(0)
    # ExcelFile = pd.read_excel('./ResultTest.xlsx', header=None, index=None).fillna(0)
    y = np.array(ExcelFile.values)
    row = y.shape[0]
    num = 0
    xls = xlwt.Workbook()
    sheet = xls.add_sheet('sheet1', cell_overwrite_ok=True)
    j = 0
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
            j += 1
            sheet.write(j, 1, initTarget)
            sheet.write(j, 2, str(resultTarget))
            sheet.write(j, 3, str(Tratio))
            j += 1
            sheet.write(j, 1, initData)
            sheet.write(j, 2, str(resultData))
            sheet.write(j, 3, str(Dratio))
            j += 1
        else:
            print(str(y[i, 0])+"-----------")
    release()
    xls.save('testResult_v6.xls')
    result = num / row
    print('result:' + str(result))

compare()

# result:0.8936241610738255
# result:0.8946308724832215
# result:0.8946308724832215
# result:0.9060402684563759
