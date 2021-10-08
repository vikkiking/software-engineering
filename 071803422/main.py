import sys
from utils.filter import Filter

# from memory_profiler import profile


# @profile
def main(argv):
    if len(argv) != 3:
        print('参数多于或少于三个！')
        exit(0)
    words_path, org_path, ans_path = argv
    sw_tree = Filter()
    sw_tree.filter(words_path, org_path, ans_path)


if __name__ == '__main__':
    main(sys.argv[1:])
