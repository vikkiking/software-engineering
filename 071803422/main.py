import json
import sys

from utils.tries import Tree
from utils.index import *


def main(argv):
    if len(argv) != 3:
        print('参数多于或少于三个！')
        return
    org_path, words_path, ans_path = argv
    res_path = 'res.txt'
    sw_tree = Tree()
    sw_tree.parse(words_path)
    f = open('utils/tree.json', 'w')
    f.write(json.dumps(sw_tree.trees, ensure_ascii=False))
    f.close()
    st_ptr_org = 0
    flag = True  # 是否还未找到新敏感词的第一个字
    res = []
    line = 1

    with open(org_path, 'r') as org_txt:
        org_txt = org_txt.read()
        i = 0
        root = sw_tree.trees
        while i < len(org_txt):
            if org_txt[i] == '\n':
                line += 1
                flag = True
                root = sw_tree.trees
            elif org_txt[i].lower() in root or org_txt[i].lower() in sw_tree.trees:
                if org_txt[i].lower() in sw_tree.trees:
                    root = sw_tree.trees
                    st_ptr_org = i
                    flag = False
                if flag:
                    st_ptr_org = i
                    flag = False
                root = root[org_txt[i].lower()]
                if not flag and 'word' in root:  # 找到完整的一个敏感词，做记录
                    temp = root
                    if len(root) > 1:
                        for j in range(i + 1, len(org_txt)):
                            if org_txt[j] in root:
                                root = root[org_txt[j]]
                            else:
                                break
                        if 'word' not in root:
                            root = temp
                        else:
                            i = j - 1
                    res.append(
                        f'\nLine{line}: <{root["word"]}> {org_txt[st_ptr_org:i + 1]}')
                    flag = True
                    root = sw_tree.trees
            elif isChinese(org_txt[i]):
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
                    if yy == len(pys[k]) - 1 and (haveChinese(root) or 'word' in root):  # 谐音字
                        if flag:
                            st_ptr_org = i
                            flag = False
                        if not flag and 'word' in root:
                            res.append(f'\nLine{line}: <{root["word"]}> {org_txt[st_ptr_org:i + 1]}')
                            flag = True
                            root = sw_tree.trees
                        break
                    else:
                        flag = True
                        root = sw_tree.trees
            i += 1
    with open(res_path, 'w') as res_txt:
        res_txt.write(f'Total: {len(res)}')
        for x in res:
            res_txt.write(x)
        res_txt.close()


if __name__ == '__main__':
    main(sys.argv[1:])
