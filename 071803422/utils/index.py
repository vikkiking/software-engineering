from pypinyin import pinyin, Style
from utils.hanzi_chaizi import HanziChaizi


def isChinese(word):
    return '\u4e00' <= word <= '\u9fff'


hc = HanziChaizi()


def div(x):  # 拆分汉字
    return hc.query(x)


def getPY(x):  # 获取汉字拼音
    return pinyin(x, heteronym=True, style=Style.NORMAL)

