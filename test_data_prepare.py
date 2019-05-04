import codecs
import os
from ChineseTranslation.langconv import Converter
from pyltp import Postagger
from pyltp import Segmentor
from pyltp import Parser
from pyltp import SementicRoleLabeller


LTP_DATA_DIR = './ltp_data_v3.4.0'  # ltp模型目录的路径
par_model_path = os.path.join(LTP_DATA_DIR, 'parser.model')  # 依存句法分析模型路径，模型名称为`parser.model`
cws_model_path = os.path.join(LTP_DATA_DIR, 'cws.model')  # 分词
pos_model_path = os.path.join(LTP_DATA_DIR, 'pos.model')  # 词性标注模型路径，模型名称为`pos.model`
srl_model_path = os.path.join(LTP_DATA_DIR, 'pisrl.model')  # 语义角色标注模型目录路径
segmentor = Segmentor()  # 初始化实例
segmentor.load(cws_model_path)  # 加载模型
postagger = Postagger()  # 初始化实例
postagger.load(pos_model_path)  # 加载模型
parser = Parser()  # 初始化实例
parser.load(par_model_path)  # 加载模型
# labeller = SementicRoleLabeller()  # 初始化实例
# labeller.load(srl_model_path)  # 加载模型



def cht_to_chs(line):
    line = Converter('zh-hans').convert(line)
    line.encode('utf-8')
    return line


def load_data(word):
    word = cht_to_chs(word)
    word = word.replace(' ', '')
    words = word.split('，')
    string = [x for x in words if len(x) > 0]
    return string

# 找HED
def getHED(words):
    root = None
    for word in words:
        if word['gov'] == -1:
            root = word['dep']
    return root

def data_prepare(words):


    dataList = []
    postagList = []
    parserList = []
    srlList = []


    for i in range(len(words)):
        if i % 100 == 0:
            print(i, end=',')

        word_list = []  # 单句话的 分词 list
        postag_list = []  # 单句话分词后的 词性 list
        parser_list = []  # 单句话分词后的 句法 list
        srl_list = []  # 单句话分词后的 主谓宾 list
        arcs_list = []  # 句法三元组

        sequence = list(words[i])  # 单个字
        sequence_postag = []  # 单个字的词性
        sequence_parser = []  # 单个字的句法
        sequence_srl = []  # 单个字的主谓宾

        dataList.append(sequence)  # datalist 将每一句话的每一个字作为一个元素加进去

        word = segmentor.segment(words[i])  # 分词
        word_list = list(word)
        # 分词后处理 添加去掉的空格
        for d in range(len(sequence)):
            if sequence[d] == '\u3000':
                sumletter = 0
                indexWord = 0
                for indexWord in range(len(word_list)):
                    if sumletter < d:
                        sumletter += len(word_list[indexWord])
                    else:
                        break
                indexWord = indexWord - 1
                sumletter -= len(word_list[indexWord])
                insertIndex = d - sumletter
                word_list[indexWord] = " ".join(
                    (word_list[indexWord][:insertIndex], word_list[indexWord][insertIndex:]))

        postag = postagger.postag(word)  # 词性标注
        postag_list = list(postag)

        arcs = parser.parse(word, postag)  # 句法分析
        for arc in arcs:
            parser_list.append(arc.relation)

        for s in range(len(postag_list)):  # 词性标注到每个字上
            for t in range(len(word_list[s])):
                sequence_postag.append(postag_list[s])
        postagList.append(sequence_postag)

        for s in range(len(parser_list)):  # 句法分析标注到每个字上
            for t in range(len(word_list[s])):
                sequence_parser.append(parser_list[s])
        parserList.append(sequence_parser)
        #
        # # LTP 提取主干
        # x = 0
        # for arc in arcs:
        #     parser_list.append(arc.relation)
        #     dict = {'dep': x, 'gov': arc.head-1, 'pos': arc.relation}
        #     arcs_list.append(dict)
        #     x = x + 1
        #
        # # predicate_index = -1
        # object_index_start = len(word_list)+1
        # object_index_end = -1
        #
        # # hed = getHED(arcs_list)
        # # if hed is not None:
        # #     predicate_index = hed  # 谓语
        # #     #print(predicate_index)
        #
        # roles = labeller.label(word, postag, arcs)  # 语义角色标注
        # for role in roles:
        #     for arg in role.arguments:
        #         if (len(arg.name) == 2) and (arg.name[0] == 'A') and (arg.name[1] != '0'):
        #             object_index_start = arg.range.start  # 宾语开始
        #             object_index_end = arg.range.end    # 宾语结束
        #             # 去掉宾语 data 两端引号
        #             if word_list[object_index_start] == "“" and word_list[object_index_end] == "”":
        #                 object_index_start = object_index_start + 1
        #                 object_index_end = object_index_end - 1
        #             #print(object_index_start, object_index_end)

        # for y in range(len(postag_list)):
        #     if y == predicate_index:
        #         srl_list.append("P")
        #     elif y >= object_index_start and y <= object_index_end :
        #         srl_list.append("O")
        #     else:
        #         srl_list.append("X")
        #
        # for s in range(len(postag_list)):  # 主谓宾 标注到每个字上
        #     for t in range(len(word_list[s])):
        #         sequence_srl.append(srl_list[s])
        # srlList.append(sequence_srl)
        # for y in range(len(word_list)):
        #         z = len(word_list[y])
        #         if y >= object_index_start and y <= object_index_end:
        #             if object_index_start == object_index_end:
        #                 if z == 1:
        #                     sequence_srl.append("S_O")
        #                 else:
        #                     for d in range(0, z):
        #                         if d == 0:
        #                             sequence_srl.append("B_O")
        #                         elif d == z-1:
        #                             sequence_srl.append("E_O")
        #                         else:
        #                             sequence_srl.append("I_O")
        #             else:
        #                 if y == object_index_start:
        #                     for d in range(0, z):
        #                         if d == 0:
        #                             sequence_srl.append("B_O")
        #                         else:
        #                             sequence_srl.append("I_O")
        #                 elif y == object_index_end:
        #                     for d in range(0, z):
        #                         if d == z-1:
        #                             sequence_srl.append("E_O")
        #                         else:
        #                             sequence_srl.append("I_O")
        #                 else:
        #                     for d in range(0, z):
        #                         sequence_srl.append("I_O")
        #         else:
        #             for d in range(0, z):
        #                 sequence_srl.append("O")
        #
        # srlList.append(sequence_srl)
    return dataList, postagList, parserList


def write(word, postag, parser):
    fw = codecs.open('./data/sample_test.txt', 'w', 'utf-8')
    for i in range(len(word)):
        for j in range(len(word[i])):
            line = ''.join([word[i][j] + '\t' + postag[i][j] + '\t' + parser[i][j]]) + '\n'
            fw.writelines(line)
        fw.writelines('\n')
    fw.close()


def release():
    postagger.release()  # 释放模型
    parser.release()  # 释放模型
    segmentor.release()  # 释放模型
    # labeller.release()  # 释放模型


def writetxt(string):
    lab = load_data(string)
    word, postag, parser = data_prepare(lab)
    write(word, postag, parser)
    return lab




# writetxt('在变更后MDS名称中填写MBRASSY-FRSIDERH')