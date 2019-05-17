import xml.dom.minidom
import xlwt


def parseXML():
    xml_path = "data/auto_ELV_Test_Cases.xml"
    dom = xml.dom.minidom.parse(xml_path)
    db = dom.documentElement
    row_element = db.getElementsByTagName('row')
    row_num = row_element.length

    for i in range(0, row_num):
        xls = xlwt.Workbook()
        sheet = xls.add_sheet('sheet1', cell_overwrite_ok=True)
        row = 0

        module = row_element[i].getElementsByTagName('module')[0].firstChild.data
        if "347" in str(module):
            id = row_element[i].getElementsByTagName('id')[0].firstChild.data
            stepDesc = row_element[i].getElementsByTagName('stepDesc')[0].firstChild.data
            expectDesc = row_element[i].getElementsByTagName('stepExpect')[0].firstChild.data

            stepList = stepDesc.replace('\n', '').replace('。', '').replace(' ', '').split('<br/>')
            expectList = expectDesc.replace('\n', '').replace('。', '').replace(' ', '').split('<br/>')
            leng = len(stepList)
            for j in range(0, leng - 1):
                step = stepList[j].split('.')[1]
                stepArray = step.split('，')
                for stepUnit in stepArray:
                    sheet.write(row, 0, str(stepUnit))
                    row = row + 1
                row = row - 1
                sheet.write(row, 1, str(expectList[j]))
                row = row + 1
            xls.save('TestCase/caseDirectory/caseDirectory347/testCase_' + id + '.xls')




