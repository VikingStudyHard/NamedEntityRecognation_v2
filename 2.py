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
# srl_model_path = os.path.join(LTP_DATA_DIR, 'pisrl.model')  # 语义角色标注模型目录路径

segmentor = Segmentor()  # 初始化实例
segmentor.load(cws_model_path)  # 加载模型

postagger = Postagger()  # 初始化实例
postagger.load(pos_model_path)  # 加载模型

parser = Parser()  # 初始化实例
parser.load(par_model_path)  # 加载模型

# labeller = SementicRoleLabeller() # 初始化实例
# labeller.load(srl_model_path)  # 加载模型

def cht_to_chs(line):   # 转换繁体到简体
    line = Converter('zh-hans').convert(line)
    line.encode('utf-8')
    return line


def data_prepare(sentences, labA, labT, labD):   # 获取人工标注
    wordList = []
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

        sentence = sentences[i]
        words = segmentor.segment(sentence)  # 分词
        word_list = list(words)
        # 补充LTP分词去掉的空格
        k = 0
        for ii in range(0, len(word_list)):
            for j in range(0, len(word_list[ii])):
                if word_list[ii][j] == sentence[k]:
                    k = k + 1
                else:
                    word_list[ii] = sentence[k].join((word_list[ii][:j], word_list[ii][j:]))
                    k = k + 1

        wordList.append(word_list)
        postag = postagger.postag(words)  # 词性标注
        postag_list = list(postag)
        postagList.append(postag_list)

        arcs = parser.parse(words, postag)  # 句法分析
        for arc in arcs:
            parser_list.append(arc.relation)
        parserList.append(parser_list)

        # roles = labeller.label(words, postag, arcs)  # 语义角色标注

        # label 标签
        labAstring = labA[i]
        labTstring = labT[i]
        labDstring = labD[i]

# 后面没改

        if len(labA[i]) == 0 and len(labT[i]) == 0 and len(labD[i]) == 0:
            label = (len(word_list)) * "O"
        else:
            for j in range(len(labAstring)):
                if len(labAstring[j]) == 1:
                    pattern = "I"
                    words[i] = re.sub(labAstring[j], pattern, str(words[i]))
                if len(labAstring[j]) > 1:
                    pattern = "L" + (len(labAstring[j]) - 2) * "M" + "X"
                    words[i] = re.sub(labAstring[j], pattern, str(words[i]))
            for k in range(len(labTstring)):
                if len(labTstring[k]) == 1:
                    pattern = "r"
                    words[i] = re.sub(labTstring[k], pattern, str(words[i]))
                if len(labTstring[k]) > 1:
                    pattern = "l" + (len(labTstring[k]) - 2) * "m" + "x"
                    words[i] = re.sub(labTstring[k], pattern, str(words[i]))
            for p in range(len(labDstring)):
                if len(labDstring[p]) > 1:
                    pattern = "J" + (len(labDstring[p]) - 2) * "Q" + "K"
                    words[i] = re.sub(labDstring[p], pattern, str(words[i]))
                if len(labDstring[p]) == 1:
                    pattern = "q"
                    words[i] = re.sub(labDstring[p], pattern, str(words[i]))
            label = re.sub(u'[^LXMlmxJQKqIr]', "0", words[i])
        labelList.append(list(label))

    return wordList, labelList, parserList, postagList



def load_data():  # 从手动标注集加载数据
    words = []
    labA = []
    labT = []
    labD = []
    path = 'data/in'
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
wordList, labelList, parserList, postagList = data_prepare(words, labA, labT, labD)
# 写入txt
write(wordList, labelList, parserList, postagList)
# 构造embedding
embedding_sentences(words)

postagger.release()   # 释放模型
parser.release()   # 释放模型
segmentor.release()   # 释放模型
