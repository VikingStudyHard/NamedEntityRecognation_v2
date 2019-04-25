from pyltp import Postagger
from pyltp import Segmentor
from pyltp import Parser
from pyltp import SementicRoleLabeller
from pyltp import NamedEntityRecognizer
import os
import jieba

# 找HED
def getHED(words):
    root = None
    for word in words:
        if word['gov'] == -1:
            root = word['dep']
    return root


def getWord(words, HED, wType):
    sbv = None
    for word in words:
        if word['pos'] == wType and word['gov'] == HED:
            sbv = word['dep']
    return sbv


def getFirstNotNone(array):
    for word in array:
        if word is not None:
            return word
    return None


LTP_DATA_DIR = './ltp_data_v3.4.0'  # ltp模型目录的路径
par_model_path = os.path.join(LTP_DATA_DIR, 'parser.model')  # 依存句法分析模型路径，模型名称为`parser.model`
cws_model_path = os.path.join(LTP_DATA_DIR, 'cws.model')  # 分词
pos_model_path = os.path.join(LTP_DATA_DIR, 'pos.model')  # 词性标注模型路径，模型名称为`pos.model`
srl_model_path = os.path.join(LTP_DATA_DIR, 'pisrl.model')  # 语义角色标注模型目录路径
# ner_model_path = os.path.join(LTP_DATA_DIR, 'ner.model')  # 命名实体识别模型路径


segmentor = Segmentor()  # 初始化实例
segmentor.load(cws_model_path)  # 加载模型
postager = Postagger()  # 初始化实例
postager.load(pos_model_path)  # 加载模型
parser = Parser()  # 初始化实例
parser.load(par_model_path)  # 加载模型
labeller = SementicRoleLabeller() # 初始化实例
labeller.load(srl_model_path)  # 加载模型
# recognizer = NamedEntityRecognizer() # 初始化实例
# recognizer.load(ner_model_path)  # 加载模型


sentence = '邮政编码一栏输入“５１０４１０”'
parser_list=[]
arcs_list = []

# cut = jieba.cut(sentence)
# print("jieba分词")
# print("\t\t".join(cut))
# cut1 = jieba.cut_for_search(sentence)
# print("jieba搜索分词")
# print("\t\t".join(cut1))
word = segmentor.segment(sentence)  # 分词
word_list = list(word)
# print("LTP分词")
print("\t".join(word))
postags = postager.postag(word)  # 词性标注

print("\t".join(postags))
# netags = recognizer.recognize(word, postags)  # 命名实体识别
# print('\t'.join(netags))
arcs = parser.parse(word, postags)  # 句法分析
print("\t".join("%d:%s" % (arc.head, arc.relation) for arc in arcs))
x = 0
for arc in arcs:
    parser_list.append(arc.relation)
    dict = {'dep': x, 'gov': arc.head-1, 'pos': arc.relation}
    arcs_list.append(dict)
    x = x + 1

hed = getHED(arcs_list)
if hed is not None:
    sbv = getWord(arcs_list, hed, 'SBV')  # 主语
    vob = getWord(arcs_list, hed, 'VOB')  # 宾语
    fob = getWord(arcs_list, hed, 'FOB')  # 后置宾语

    adv = getWord(arcs_list, hed, 'ADV')  # 定中
    pob = getWord(arcs_list, adv, 'POB')  # 介宾如果没有主语可做主语

    # zhuWord = getFirstNotNone([sbv, pob])  # 最终主语
    weiWord = hed  # 最终谓语
    binWord = getFirstNotNone([vob, fob, pob])  # 最终宾语

# print("主语：%s" % word_list[zhuWord])
print("提取主干 谓语：%s" % word_list[weiWord])
#print("提取主干 宾语：%s" % word_list[binWord])

roles = labeller.label(word, postags, arcs)  # 语义角色标注
for role in roles:
    print(role.index, "".join(
        ["%s:(%d,%d)" % (arg.name, arg.range.start, arg.range.end) for arg in role.arguments]))

for role in roles:
    print("语义角色标注 谓语：%s" % word_list[role.index])
    for arg in role.arguments:
        if arg.name[0] == 'A':
            print("语义角色标注 宾语：%s:" % (arg.name),"".join(["%s" % word_list[m] for m in range(arg.range.start, arg.range.end+1)]))




postager.release()  # 释放模型
parser.release()  # 释放模型
segmentor.release()  # 释放模型
labeller.release()  # 释放模型
# recognizer.release()  # 释放模型

