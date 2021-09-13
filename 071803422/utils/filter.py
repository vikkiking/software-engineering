"""
生成敏感词（含变形）树
"""

from utils.index import *


class Tree(object):
    def __init__(self) -> None:
        super().__init__()
        self.trees = {}

    def add(self, word, index, root):
        if word[index:]:
            temp = root
            if word[index] not in root:
                root[word[index]] = {}
            root = root[word[index]]
            self.add(word, index + 1, root)
            if isChinese(word[index]):
                py = getPY(word)[index][0]
                divs = div(word[index])
                if py:
                    root = temp
                    for x in py:
                        root[x] = root[x] if x in root else {}
                        root = root[x]
                    self.add(word, index + 1, temp[py[0]])
                    self.add(word, index + 1, root)
                if divs:
                    root = temp
                    for x in range(len(divs)):
                        root[divs[x]] = root[divs[x]] if divs[x] in root else {}
                        xx = getPY(divs[x])[0]
                        for xxx in xx:
                            if xxx == py:
                                root[divs[x]]['word'] = word
                        root = root[divs[x]]
                    self.add(word, index + 1, root)
        else:
            root['word'] = word

    def parse(self, path):
        with open(path, 'r') as words:
            words = words.read().split('\n')
            for word in words:
                word = word.lower()
                self.add(word, 0, self.trees)
