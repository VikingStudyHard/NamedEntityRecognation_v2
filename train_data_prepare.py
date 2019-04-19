from gensim.corpora.dictionary import Dictionary
from gensim.models import Word2Vec
from ChineseTranslation.langconv import Converter
from pyltp import Postagger
from pyltp import Segmentor
from pyltp import Parser
from pyltp import SementicRoleLabeller

import pandas as pd

import re
import codecs
import os

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

labeller = SementicRoleLabeller() # 初始化实例
labeller.load(srl_model_path)  # 加载模型

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


def data_prepare(sentences, labA, labT, labD):   # 获取人工标注
    dataList = []
    labelList = []
    postagList = []
    parserList = []
    srlList = []

    for i in range(len(sentences)):
        # if i % 100 == 0:
        #     print(i, end=',')

        word_list = []  # 单句话的 分词 list
        postag_list = []  # 单句话分词后的 词性 list
        parser_list = []  # 单句话分词后的 句法 list
        srl_list = []


        words = segmentor.segment(sentences[i])  # 分词
        word_list = list(words)
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

        roles = labeller.label(words, postag, arcs) # 语义角色标注


        for s in range(len(postag_list)):  # 词性标注到每个字上
            for t in range(len(word_list[s])):
                sequence_postag.append(postag_list[s])
        postagList.append(sequence_postag)

        for s in range(len(parser_list)):  # 句法分析标注到每个字上
            for t in range(len(word_list[s])):
                sequence_parser.append(parser_list[s])
        parserList.append(sequence_parser)

        # label 标签
        labWstring = labA[i]
        labCstring = labT[i]
        labEstring = labD[i]

        if len(labA[i]) == 0 and len(labT[i]) == 0 and len(labD[i]) == 0:
            label = (len(words[i])) * "O"
        else:
            for j in range(len(labWstring)):
                if len(labWstring[j]) == 1:
                    pattern = "I"
                    words[i] = re.sub(labWstring[j], pattern, str(words[i]))
                if len(labWstring[j]) > 1:
                    pattern = "L" + (len(labWstring[j]) - 2) * "M" + "X"
                    words[i] = re.sub(labWstring[j], pattern, str(words[i]))
            for k in range(len(labCstring)):
                if len(labCstring[k]) == 1:
                    pattern = "r"
                    words[i] = re.sub(labCstring[k], pattern, str(words[i]))
                if len(labCstring[k]) > 1:
                    pattern = "l" + (len(labCstring[k]) - 2) * "m" + "x"
                    words[i] = re.sub(labCstring[k], pattern, str(words[i]))
            for p in range(len(labEstring)):
                if len(labEstring[p]) > 1:
                    pattern = "J" + (len(labEstring[p]) - 2) * "Q" + "K"
                    words[i] = re.sub(labEstring[p], pattern, str(words[i]))
                if len(labEstring[p]) == 1:
                    pattern = "q"
                    words[i] = re.sub(labEstring[p], pattern, str(words[i]))
            label = re.sub(u'[^LXMlmxJQKqIr]', "0", words[i])
        labelList.append(list(label))


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

postagger.release()  # 释放模型
parser.release()  # 释放模型
segmentor.release()  # 释放模型
labeller.release()  # 释放模型