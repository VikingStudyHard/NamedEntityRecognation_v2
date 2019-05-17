import os
import xlwt
import numpy as np
import pandas as pd
from parseXML import parseXML
from predict import predict
from test_data_prepare import release


def writeTestCase():
    parseXML()
    path = "./TestCase/caseDirectory/caseDirectory347"
    for file in os.walk(path):
        fileNameList = file[2]
        for fileName in fileNameList:
            id = str(fileName).split("_")[1]
            id = id.split(".")[0]
            ExcelFile = pd.read_excel(path + "/" + str(fileName), header=None, index=None).fillna(0)
            y = np.array(ExcelFile.values)
            row = y.shape[0]
            xls = xlwt.Workbook()
            sheet = xls.add_sheet('sheet1', cell_overwrite_ok=True)
            j = 0

            for i in range(0, row):
                print(y[i, 0])

                resultAction, resultTarget, resultData = predict(str(y[i, 0]).replace('\t', '').replace('\n', '').replace('\r', '').strip())
                resultAction = str(resultAction).split('***')[0].strip()
                resultTarget = str(resultTarget).strip().replace('***', '').replace("和", "").replace("、", "")
                resultData = "".join(resultData).strip().replace('***', '')


                sheet.write(j, 0, resultAction)
                sheet.write(j, 1, resultTarget)
                sheet.write(j, 2, resultData)
                sheet.write(j, 3, y[i, 1])
                j += 1

            # xls.save('testCasePredict.xls')

            xls.save('./TestCase/xlsToTuples/xlsToTuples347/testCasePredict_' + id + '.xls')


writeTestCase()
release()
