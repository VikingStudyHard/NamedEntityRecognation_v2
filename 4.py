from pyltp import Postagger
from pyltp import Segmentor
from pyltp import Parser
from pyltp import SementicRoleLabeller
from pyltp import NamedEntityRecognizer
import os
import jieba

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


sentence = '在零部件名称中填写MBRASSY-FRSIDERH'
parser_list = []
arcs_list = []
print(str(sentence))
cut = jieba.cut(sentence)
print("jieba分词:")

print("\t\t".join(cut))
cut1 = jieba.cut_for_search(sentence)
print("jieba搜索分词:")

print("\t\t".join(cut1))
word = segmentor.segment(sentence)  # 分词
word_list = list(word)
print("LTP分词:")
print(len(word_list))
print("\t\t".join(word))
postags = postager.postag(word)  # 词性标注
pos_list = list(postags)

print("\t\t".join(postags))