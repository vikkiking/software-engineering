"""
生成敏感词（含变形）树
"""
import json
from utils.index import *


def tryIO(path):
    try:
        f = open(path, 'r')
    except IOError:
        print(f'没有找到 {path}')
        exit(0)
    else:
        f.close()


class Filter(object):
    def __init__(self) -> None:
        super().__init__()
        self.trees = {}  # 敏感词树
        self.words = []  # 敏感词列表
        self.maxChars = 20

    def add(self, i_words, i_word, root):
        """
        i_words: 当前敏感词在self.words中的索引
        i_word:  当前单字在敏感词中的位置
        root:    前一个单字所在分支
        """
        if self.words[i_words][i_word:]:
            temp = root
            if self.words[i_words][i_word] not in root:
                root[self.words[i_words][i_word]] = {}
            root = root[self.words[i_words][i_word]]
            self.add(i_words, i_word + 1, root)
            if isChinese(self.words[i_words][i_word]):
                py = getPY(self.words[i_words])[i_word][0]  # words[i][index]的拼音
                divs = div(self.words[i_words][i_word])  # words[i][index]的拆解（可能有多组）
                # if py:
                root = temp
                for x in py:
                    root[x] = root[x] if x in root else {}
                    root = root[x]
                self.add(i_words, i_word + 1, temp[py[0]])
                self.add(i_words, i_word + 1, root)
                root['end'] = True
                if divs:
                    for y in divs:
                        root = temp
                        for x in y:
                            root[x] = root[x] if x in root else {}
                            '''eg：睦=目+坴，“睦”和“目”谐音，因此根据“睦邻”这个词更新敏感词，新添[睦，m，目]三个分支后，
                               "目"应该新添和"睦"一样的分支
                            '''
                            xx = getPY(x)[0]
                            for xxx in xx:
                                if xxx == py:
                                    # self.ml.append({0: temp[self.words[i_words][i_word]], 1: root[x]})
                                    for sth in temp[self.words[i_words][i_word]]:
                                        root[x][sth] = temp[self.words[i_words][i_word]][sth]
                                    break
                            root = root[x]
                        self.add(i_words, i_word + 1, root)
        else:
            root['word'] = i_words

    def parse(self, path):
        with open(path, 'r', encoding='UTF-8') as words:
            self.words = words.read().split('\n')
            for i in range(len(self.words)):
                self.add(i, 0, self.trees)

    def filter(self, words_path, org_path, ans_path):
        tryIO(words_path)
        tryIO(org_path)
        self.parse(words_path)
        st_ptr_org, prev, res, line, i = 0, 0, [], 1, 0
        flag = True  # 是否还未找到新敏感词的第一个字
        with open(org_path, 'r', encoding='UTF-8') as org_txt:
            org_txt = org_txt.read()
            root = self.trees

            def func():
                nonlocal root, i, temp, org_txt, prev
                nonlocal st_ptr_org, flag, res, line
                if (i - prev - 1 > self.maxChars and not flag) or \
                        (prev != i - 1 and '0' <= org_txt[i] <= '9'):
                    flag = True
                    root = self.trees
                else:
                    root = root[org_txt[i].lower()]
                    if not flag and 'word' in root:  # 找到完整的一个敏感词，做记录
                        temp = root
                        if len(root) > 1:
                            for index in range(i + 1, len(org_txt)):
                                if org_txt[index] in root:
                                    root = root[org_txt[index]]
                                else:
                                    if 'word' not in root:
                                        root = temp
                                    else:
                                        i = index - 1
                                    break
                                if index == len(org_txt) - 1:
                                    if 'word' not in root:
                                        root = temp
                                    else:
                                        i = index
                        res.append(
                            f'\nLine{line}: <{self.words[root["word"]]}> {org_txt[st_ptr_org:i + 1]}')
                        flag = True
                        root = self.trees
                    prev = i

            while i < len(org_txt):
                if org_txt[i] == '\n':
                    line += 1
                    flag = True
                    root = self.trees
                elif org_txt[i].lower() in root:
                    if flag:
                        st_ptr_org = i
                        prev = i
                        flag = False
                    func()
                elif isChinese(org_txt[i]):
                    temp = root
                    pys = getPY(org_txt[i])[0]
                    for k in range(len(pys)):
                        for j in range(len(pys[k])):
                            if pys[k][j] in root:
                                root = root[pys[k][j]]
                                yy = j
                            else:
                                yy = j - 1
                                break
                        if yy == len(pys[k]) - 1 and 'end' in root and not ('0' <= org_txt[i - 1] <= '9'):  # 谐音字
                            if i - prev - 1 > self.maxChars and not flag:
                                flag = True
                                root = self.trees
                            else:
                                if flag:
                                    st_ptr_org = i
                                    flag = False
                                if not flag and 'word' in root:  # 找到完整的一个敏感词，做记录
                                    res.append(
                                        f'\nLine{line}: <{self.words[root["word"]]}> {org_txt[st_ptr_org:i + 1]}')
                                    flag = True
                                    root = self.trees
                                prev = i
                                break
                        else:
                            root = temp
                        if k == len(pys) - 1:
                            if not flag:
                                i -= 1
                            flag = True
                            root = self.trees
                elif org_txt[i].lower() in self.trees:
                    root = self.trees
                    flag = False
                    st_ptr_org = i
                    prev = i
                    func()
                elif isChinese(org_txt[st_ptr_org]) and (
                        'a' <= org_txt[i].lower() <= 'z' or '0' <= org_txt[i] <= '9'):
                    flag = True
                    root = self.trees
                i += 1
        with open(ans_path, 'w', encoding='UTF-8') as res_txt:
            res_txt.write(f'Total: {len(res)}')
            for x in res:
                res_txt.write(x)
