from gensim.corpora.dictionary import Dictionary
from gensim.models import Word2Vec
from ChineseTranslation.langconv import Converter
from pyltp import Postagger
from pyltp import Segmentor
from pyltp import Parser

import pandas as pd
import re
import codecs
import os

LTP_DATA_DIR = './ltp_data_v3.4.0'  # ltp模型目录的路径
par_model_path = os.path.join(LTP_DATA_DIR, 'parser.model')  # 依存句法分析模型路径，模型名称为`parser.model`
cws_model_path = os.path.join(LTP_DATA_DIR, 'cws.model')  # 分词
pos_model_path = os.path.join(LTP_DATA_DIR, 'pos.model')  # 词性标注模型路径，模型名称为`pos.model`
# srl_model_path = os.path.join(LTP_DATA_DIR, 'pisrl.model')  # 语义角色标注模型目录路径

segmentor = Segmentor()     # 初始化实例
segmentor.load(cws_model_path)  # 加载模型


postagger = Postagger()     # 初始化实例
postagger.load(pos_model_path)  # 加载模型

parser = Parser()    # 初始化实例
parser.load(par_model_path)  # 加载模型


def cht_to_chs(line):   # 转换繁体到简体
    line = Converter('zh-hans').convert(line)
    line.encode('utf-8')
    return line


def load_data():  # 从手动标注集加载数据
    words = []
    labA = []
    labT = []
    labD = []
    path = 'data/input'
    for file in os.walk(path):
        for filename in file[2]:
            child = os.path.join(path, str(filename))
            lib = pd.read_excel(child, header=None, index=None).fillna(0)
            for word in lib[0]:
                word = str(word).replace('\t', '')
                word = cht_to_chs(word)
                word = word.replace(' ', '')
                words.append(word)
            for line in lib[1]:
                line = str(line)
                line = line.replace(' ', '')
                line = cht_to_chs(line)
                lin = line.split('，')
                labA.append(lin)
            for line in lib[2]:
                line = str(line)
                line = line.replace(' ', '')
                line = cht_to_chs(line)
                lin = line.split('，')
                labT.append(lin)
            for line in lib[3]:
                line = str(line)
                line = line.replace(' ', '')
                line = cht_to_chs(line)
                lin = line.split('，')
                # xlrd.xldate_as_datetime(line[0].value, 0)
                labD.append(lin)
    return words, labA, labT, labD

# 找HED
def getHED(words):
    root = None
    for word in words:
        if word['gov'] == -1:
            root = word['dep']
    return root


def data_prepare(words, labAs, labTs, labDs): # 获取人工标注
    dataList = []
    labelList = []
    postagList = []
    parserList = []
    words1 = words

    for i in range(len(words)):
        if i % 100 == 0:
            print(i, end=',')

        word_list = []  # 单句话的 分词 list
        postag_list = []  # 单句话分词后的 词性 list
        parser_list = []  # 单句话分词后的 句法 list


        sequence = list(words[i])  # 单个字
        sequence_postag = []  # 单个字的词性
        sequence_parser = []  # 单个字的句法
        sequnce_label = [] # 单个字的标注

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



        # label 标签
        labAstring = labAs[i] # 可有多个str
        labTstring = labTs[i]
        labDstring = labDs[i]

        for a in range(len(words[i])):
            sequnce_label.append('O')
        # 若是先改BIE 再改S 如果 BIE 中包含了S 会被覆盖掉标签。
        # 所以先S后BIE
        for j in range(len(labAstring)):
            if len(labAstring[j]) == 1:
                A_list_S = [t.start() for t in re.finditer(labAstring[j], words[i])]
                for s in range(len(A_list_S)):
                    sequnce_label[A_list_S[s]] = 'S_ACT'

        for j in range(len(labTstring)):
            if len(labTstring[j]) == 1:
                T_list_S = [t.start() for t in re.finditer(labTstring[j], words[i])]
                for s in range(len(T_list_S)):
                    sequnce_label[T_list_S[s]] = 'S_TAR'

        for j in range(len(labDstring)):
            if len(labDstring[j]) == 1:
                D_list_S = [t.start() for t in re.finditer(labDstring[j], words[i])]
                for s in range(len(D_list_S)):
                    sequnce_label[D_list_S[s]] = 'S_DAT'

        for j in range(len(labAstring)):
            if len(labAstring[j]) > 1:
                A_list_L = [t.start() for t in re.finditer(labAstring[j], words[i])]
                for s in range(len(A_list_L)):
                    sequnce_label[A_list_L[s]] = 'B_ACT'
                    for m in range(A_list_L[s] + 1, A_list_L[s] + len(labAstring[j]) - 1):
                        sequnce_label[m] = 'I_ACT'
                    sequnce_label[A_list_L[s] + len(labAstring[j]) - 1] = 'E_ACT'

        for j in range(len(labTstring)):
            if len(labTstring[j]) > 1:
                T_list_L = [t.start() for t in re.finditer(labTstring[j], words[i])]
                for s in range(len(T_list_L)):
                    sequnce_label[T_list_L[s]] = 'B_TAR'
                    for m in range(T_list_L[s] + 1, T_list_L[s] + len(labTstring[j]) - 1):
                        sequnce_label[m] = 'I_TAR'
                    sequnce_label[T_list_L[s] + len(labTstring[j]) - 1] = 'E_TAR'

        for j in range(len(labDstring)):
            if len(labDstring[j]) > 1:
                D_list_L = [t.start() for t in re.finditer(labDstring[j], words[i])]
                for s in range(len(D_list_L)):
                    sequnce_label[D_list_L[s]] = 'B_DAT'
                    for m in range(D_list_L[s] + 1, D_list_L[s] + len(labDstring[j]) - 1):
                        sequnce_label[m] = 'I_DAT'
                    sequnce_label[D_list_L[s] + len(labDstring[j]) - 1] = 'E_DAT'



        labelList.append(sequnce_label)

    postagger.release()  # 释放模型
    parser.release()  # 释放模型
    segmentor.release()  # 释放模型
    return dataList, labelList, parserList, postagList


def write(words, lab, parser, postag):
    fw = codecs.open('data/sample_train.txt', 'w', 'utf-8')
    for i in range(len(words)):
        for j in range(len(words[i])):
            line = ''.join([words[i][j] + '\t' + postag[i][j] + '\t' + parser[i][j] + '\t' + lab[i][j]]) + '\n'
            fw.writelines(line)
        fw.writelines('\n')
    fw.close()



def embedding_sentences(sentences):
    w2vModel = Word2Vec(sentences, size=64, window=5, min_count=1)
    w2vModel.save('Model/Word2vec_model.pkl')
    gensim_dict = Dictionary()
    gensim_dict.doc2bow(w2vModel.wv.vocab.keys(), allow_update=True)  # gensim 的doc2bow实现词袋模型
    w2indx = {v: k for k, v in gensim_dict.items()}
    w2vec = {word: w2vModel[word] for word in w2indx.keys()}
    return w2vec


words, labA, labT, labD = load_data()
# 得到基于字的词性标注、句法分析、标签
dataList, labelList, parserList, postagList = data_prepare(words, labA, labT, labD)
# 写入txt
write(dataList, labelList, parserList, postagList)
# 构造embedding
embedding_sentences(words)

