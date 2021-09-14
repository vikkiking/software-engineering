"""
生成敏感词（含变形）树
"""
import json
from utils.index import *


class Filter(object):
    def __init__(self) -> None:
        super().__init__()
        self.trees = {}  # 敏感词树
        self.words = []  # 敏感词列表

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
                    root = temp
                    for y in divs:
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
            '''for st in self.ml:
                for ppp in st[0]:
                    st[1][ppp] = st[0][ppp]
            self.ml.clear()'''

    def parse(self, path):
        with open(path, 'r',encoding='UTF-8') as words:
            self.words = words.read().split('\n')
            for i in range(len(self.words)):
                self.add(i, 0, self.trees)

    def filter(self, words_path, org_path, ans_path):
        self.parse(words_path)
        # with open('tree.json', 'w',encoding='UTF-8')as f:
        #     f.write(json.dumps(self.trees, ensure_ascii=False))
        st_ptr_org = 0
        flag = True  # 是否还未找到新敏感词的第一个字
        res = []
        wait = -1
        line = 1
        i = 0
        with open(org_path, 'r',encoding='UTF-8') as org_txt:
            org_txt = org_txt.read()
            root = self.trees

            def func():
                nonlocal root, i, temp, org_txt, wait
                nonlocal st_ptr_org, flag, res, line
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
                                i = index
                    res.append(
                        f'\nLine{line}: <{self.words[root["word"]]}> {org_txt[st_ptr_org:i + 1]}')
                    flag = True
                    root = self.trees

            while i < len(org_txt):
                if org_txt[i] == '\n':
                    line += 1
                    flag = True
                    root = self.trees
                elif org_txt[i].lower() in root:
                    if flag:
                        st_ptr_org = i
                        flag = False
                    func()
                elif isChinese(org_txt[i]):
                    if wait >= 0:
                        flag = False
                        root = self.trees[org_txt[wait]]
                        st_ptr_org = wait
                        wait = -1
                    temp = root
                    xy = False
                    pys = getPY(org_txt[i])[0]
                    for k in range(len(pys)):
                        yy = 0
                        for j in range(len(pys[k])):
                            if pys[k][j] in root:
                                root = root[pys[k][j]]
                                yy = j
                            else:
                                yy = j - 1
                                break
                        if yy == len(pys[k]) - 1 and 'end' in root:  # 谐音字
                            xy = True
                            if flag:
                                st_ptr_org = i
                                flag = False
                            if not flag and 'word' in root:  # 找到完整的一个敏感词，做记录
                                res.append(
                                    f'\nLine{line}: <{self.words[root["word"]]}> {org_txt[st_ptr_org:i + 1]}')
                                flag = True
                                root = self.trees
                            break
                        else:
                            root = temp
                        if k == len(pys) - 1:
                            '''
                             保存该单字
                             例如有【邪教、法轮功】
                             待检测句子“邪法!@#$%^&*()_+轮!@#$%^&*()_+功教”
                             应检测出“法!@#$%^&*()_+轮!@#$%^&*()_+功”
                             为此要把“法”的索引赋值给wait
                            '''
                            wait = i if (not xy and org_txt[i] in self.trees) else -1
                            flag = True
                            root = self.trees
                elif org_txt[i].lower() in self.trees:
                    root = self.trees
                    flag = False
                    st_ptr_org = i
                    func()
                i += 1
        with open(ans_path, 'w',encoding='UTF-8') as res_txt:
            res_txt.write(f'Total: {len(res)}')
            for x in res:
                res_txt.write(x)
