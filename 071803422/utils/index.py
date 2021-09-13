from pypinyin import pinyin, Style
from utils.hanzi_chaizi import HanziChaizi


def isChinese(word):
    return '\u4e00' <= word <= '\u9fff'


def haveChinese(root):
    for x in root:
        if isChinese(x):
            return True
    return False


hc = HanziChaizi()


def div(x):  # 拆分汉字
    v = hc.query(x)
    if isinstance(v, list):
        return v[0] if len(v) == 1 else v[1]
    return v


def getPY(x):  # 获取汉字拼音
    return pinyin(x, heteronym=True, style=Style.NORMAL)
