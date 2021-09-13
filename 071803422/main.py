import sys
from utils.filter import Filter
import time


# from memory_profiler import profile


# @profile
def main(argv):
    if len(argv) != 3:
        print('参数多于或少于三个！')
        return
    org_path, words_path, ans_path = argv
    # t1 = time.time()
    sw_tree = Filter()
    # t2 = time.time()
    # print(f'生成敏感词树花费 {t2 - t1} s')
    sw_tree.filter(words_path, org_path, ans_path)
    # print(f'查询花费 {time.time() - t2} s')


if __name__ == '__main__':
    # tt1 = time.time()
    main(sys.argv[1:])
    # print(f'cost {time.time() - tt1} s')
