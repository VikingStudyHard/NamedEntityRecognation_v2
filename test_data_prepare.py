import codecs
import os
from ChineseTranslation.langconv import Converter
from pyltp import Postagger
from pyltp import Segmentor
from pyltp import Parser


LTP_DATA_DIR = './ltp_data_v3.4.0'  # ltp模型目录的路径
par_model_path = os.path.join(LTP_DATA_DIR, 'parser.model')  # 依存句法分析模型路径，模型名称为`parser.model`
cws_model_path = os.path.join(LTP_DATA_DIR, 'cws.model')  # 分词
pos_model_path = os.path.join(LTP_DATA_DIR, 'pos.model')  # 词性标注模型路径，模型名称为`pos.model`



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


def data_prepare(words):
    segmentor = Segmentor()  # 初始化实例
    segmentor.load(cws_model_path)  # 加载模型
    postagger = Postagger()  # 初始化实例
    postagger.load(pos_model_path)  # 加载模型
    parser = Parser()  # 初始化实例
    parser.load(par_model_path)  # 加载模型

    dataList = []
    postagList = []
    parserList = []

    for i in range(len(words)):
        if i % 100 == 0:
            print(i, end=',')

        word_list = []  # 单句话的 分词 list
        postag_list = []  # 单句话分词后的 词性 list
        parser_list = []  # 单句话分词后的 句法 list

        sequence = list(words[i])  # 单个字
        sequence_postag = []  # 单个字的词性
        sequence_parser = []  # 单个字的句法

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
        postagger.release()  # 释放模型
        parser.release()  # 释放模型
        segmentor.release()  # 释放模型
    return dataList, postagList, parserList


def write(word, postag, parser):
    fw = codecs.open('./data/sample_test.txt', 'w', 'utf-8')
    for i in range(len(word)):
        for j in range(len(word[i])):
            line = ''.join([word[i][j] + '\t' + postag[i][j] + '\t'+parser[i][j] + '\t']) + '\n'
            fw.writelines(line)
        fw.writelines('\n')
    fw.close()


def writetxt(string):
    lab = load_data(string)
    word, postag, parser = data_prepare(lab)
    write(word, postag, parser)
    return lab




# writetxt('在变更后MDS名称中填写MBRASSY-FRSIDERH')