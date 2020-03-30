# -*- coding: utf-8 -*-
import codecs
import glob
import os
from pathlib import Path

# =======================

class node(object):

    def __init__(self):
        self.next = {}
        self.fail = None
        self.isWord = False
        self.word = ""

class ac_automation(object):

    def __init__(self):
        self.root = node()

    def addword(self, word):
        temp_root = self.root
        for char in word:
            if char not in temp_root.next:
                temp_root.next[char] = node()
            temp_root = temp_root.next[char]
        temp_root.isWord = True
        temp_root.word = word

    def make_fail(self):
        temp_que = []
        temp_que.append(self.root)
        while len(temp_que) != 0:
            temp = temp_que.pop(0)
            p = None
            for key,value in temp.next.item():
                if temp == self.root:
                    temp.next[key].fail = self.root
                else:
                    p = temp.fail
                    while p is not None:
                        if key in p.next:
                            temp.next[key].fail = p.fail
                            break
                        p = p.fail
                    if p is None:
                        temp.next[key].fail = self.root
                temp_que.append(temp.next[key])

    def search(self, content):

        p = self.root
        result = []
        position = []
        currentposition = 0
        while currentposition < len(content):
            word = content[currentposition]
            while word in p.next == False and p != self.root:
                p = p.fail
            if word in p.next:
                p = p.next[word]
            else:
                p = self.root
            if p.isWord:
                result.append(p.word)
                position.append(currentposition)
                p = self.root
            currentposition += 1
        return result, position


    def parse(self, folder = os.path.abspath(__file__) + '/' + 'corpus'):
        # folder = Path(os.path.abspath(__file__)).parent / 'corpus'
        # folder = 'D:/pycharm_project/AI_Speech_QIA/database/corpus/'
        # for _folder in os.listdir(folder):
        for _folder in glob.glob('D:/pycharm_project/AI_Speech_QIA/database/corpus/*.txt'):
            '''
            TODO: API and function for adding defraud word by self
            '''
            with open(_folder, encoding='utf-8') as f:
                for keyword in f:
                    self.addword(str(keyword).strip())

    def words_replace(self, text):

        # result = list(set(self.search(text)))
        # for x in result:
        #     m = text.replace(x, '*' * len(x))
        #     text = m
        result, position = self.search(text)
        # res = {'sentence': text, 'defraud': [{'word': None, 'start': None, 'end': None}]}
        res = {'sentence': text, 'defraud': []}

        for _res, _pos in zip(result, position):
            res['defraud'].append({'word': _res, 'start': _pos, 'end': _pos + len(_res) - 1})

        return res


# def load_dict(op, folder = os.path.abspath(__file__) + '/' + 'corpus') :
#     for file in os.listdir(folder):
#         with codecs.open(file, encoding = 'utf-8') as f:
#             for line in f:
#                 op.addword(line.strip())




def main_func():
    ah = ac_automation()
    ah.parse()
    # load_dict(ah)
    return ah

if __name__ == '__main__':
    sample = '出售雷管炸药各种炸药配方大全'
    ParseOp = main_func()
    parse_res = ParseOp.words_replace(sample)
