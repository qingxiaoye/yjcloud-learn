'''
对每个问题进行唯一、相斥的正则模式搜索

returns: Dict(int: regex expression)

Notes: There may be problems for keys of returns object,
       since here I acquiesce a decision that, these keys are ascending sequence
       that take the answerDict keys
'''

import os
import re
from typing import List, Text
import numpy as np


class regexProcessor():
    def __init__(self,
                 questionList, # type: List
                 tfidfModel,
                 initK = 2, # type: int
                 initIndex = None, #type: List
                 ):
        '''
        :param questionList: ['a b c', 'd e f']
        '''

        self.questionList = self.check_inputFormat(questionList)
        self.initK = initK
        self.initIndex = initIndex

        self.tfidfModel = tfidfModel
        self.vocabulary = self.tfidfModel.vocabulary_ # word2index
        self.vocabulary_ = {val:key for key, val in self.vocabulary.items()}

        self.wordMatrix = np.zeros(shape = (len(self.questionList),
                                            len(self.vocabulary)))

        self.matrixWord = {}
        self.matrixWordIndex = {}

        self.tfidfVec = self.predictProcess(self.questionList,
                                            self.tfidfModel)


        # -----------
        self.NoneRef = [] # find bug, those line have no regex expression
        self.regexMapping = {}



    # def init_matrix(self):
    #     arg_index_col = np.argsort(-self.tfidfVec, 1)[:, :self.initK].reshape(-1)
    #     arg_index_row = np.repeat(np.arange(self.tfidfVec.shape[0]), self.initK)
    #
    #
    #     考虑重复词
        # for row, col in zip(arg_index_row, arg_index_col):
        #     word_count = self.questionList[row].count(self.vocabulary_[col])
        #     self.wordMatrix[row, col] += word_count

    def init_matrix(self):
        arg_index_col = np.argsort(-self.tfidfVec, 1)[:, :self.initK]

        # 考虑重复词
        for row, col in enumerate(arg_index_col):
            self.matrixWord[row] = []
            self.matrixWordIndex[row] = []
            for ind, ori_word in enumerate(self.questionList[row].split(' ')):
                if ori_word in self.vocabulary:
                    if self.vocabulary[ori_word] in col:
                        self.matrixWord[row].append(self.vocabulary[ori_word])
                        self.matrixWordIndex[row].append(ind)



    def search_main(self, thread_repeat = 3):
        '''
        1. 检查冲突项，记录位置
        2. 对冲突项的wordMatrix填充 k-th word
        3. return 1
        '''

        search_step = 1
        _repeat_count = 0

        # import time
        while True:
            contradictFlag, contradictRef = self.check_contradict(self.matrixWord, self.NoneRef)

            if not contradictFlag.any():
                break

            else:
                # add word for returned line
                _ifadd = False
                for axis in contradictFlag:
                    _ifadd = self.add_word(axis) or _ifadd

                if _ifadd:
                    _repeat_count = 0
                else:
                    _repeat_count += 1

                print(_ifadd)

                print(f'Search Processing:\t{search_step}')


            # ----------------------------------
            if _repeat_count >= thread_repeat:
                self.NoneRef.append(contradictRef)
                _repeat_count = 0


            search_step += 1

            if search_step % 5 == 0:
                print('*' * 40)
                # print(self.wordMatrix)
                print(contradictRef)
                print(contradictFlag)
            #     print(time.sleep(10))
            # ----------------------------------


    def add_word(self, axis):
        # length = np.where(self.wordMatrix[axis] != 0)[0].size

        length = len(self.matrixWord[axis])

        # ----------------
        # find bug
        # if all word has been filled, then return False
        # if length == len(self.wordMatrix[axis]):

        if length == len(self.questionList[axis]):
            return False
        # next word index: length
        col = np.argsort(-self.tfidfVec[axis])[length]

        # -----------------
        # check whether this word in sentence
        if self.tfidfVec[axis, col] == 0:
            return False
        # -----------------

        # word_count = (self.questionList[axis].split(' ')).count(self.vocabulary_[col])

        for idx, word in enumerate(self.questionList[axis].split(' ')):
            if word == self.vocabulary_[col]:
                self.matrixWordIndex[axis].append(idx)
                self.matrixWord[axis].append(col)

            sorted_struct = sorted([(x,y) for x,y in zip(self.matrixWord[axis], self.matrixWordIndex[axis])],
                                   key = lambda x: x[1])
            self.matrixWord[axis] = [x[0] for x in sorted_struct]
            self.matrixWordIndex[axis] = [x[1] for x in sorted_struct]

        # self.wordMatrix[axis, col] += word_count
        return True



    def regexGenerator(self):
        '''
        从 wordMatrix 映射 到原句顺序的正则表达式
        '''
        if self.initIndex:
            for id, (index, line) in enumerate(zip(self.initIndex, self.questionList)):
                if id in self.NoneRef:
                    continue
                else:
                    regex_line = self.regex_for_line(id, line)

                    self.regexMapping[index] = regex_line

        else:
            for index, line in enumerate(self.questionList):
                if index in self.NoneRef:
                    continue
                else:
                    regex_line = self.regex_for_line(index, line)


                    self.regexMapping[index] = regex_line



    def regex_for_line(self, index, line):
        '''
        :param line: 'a b c': Text
        '''

        TEMPLATEMID = '.*'
        regex_line = ''
        # MAPPING_WORD = [self.vocabulary_[x] for x in np.where(self.wordMatrix[index] != 0)[0]]

        MAPPING_WORD = [self.vocabulary_[x] for x in self.matrixWord[index]]
        # line = re.sub('[ ]+', '', line.strip())
        line = line.strip().split(' ')

        _last_regex = None
        for word in line:
            if word in MAPPING_WORD:
                regex_line += '(%s)' % word.replace('爞', '')

                _last_regex = False
            else:
                if _last_regex:
                    continue
                else:
                    regex_line += TEMPLATEMID
                    _last_regex = True

        return re.compile(regex_line)


    def pipeline(self):
        self.init_matrix()
        self.search_main()
        self.regexGenerator()


    @staticmethod
    def predictProcess(corpus,  # type: List
                       tfidfModel,
                       ):

        if isinstance(corpus[0], List):
            corpus = [' '.joi(x) for x in corpus]
        elif isinstance(corpus[0], Text):
            pass
        else:
            raise ValueError('Not supported corpus type temporarily')

        return tfidfModel.transform(corpus).toarray()


    @staticmethod
    def check_contradict(word_matrix, NoneRef):
        '''
        :param word_matrix: dict, {row: wordId}
        :param word_matrix_index: dict, {row: sort id}
        :param NoneRef:
        :return:
        '''
        for index, line in enumerate(word_matrix):
            print('searching from %d...' % index)
            # -------------------
            if index in NoneRef:
                continue

            # if index == word_matrix.shape[0] - 1:
            #     return np.array([]), index

            if index == len(word_matrix) - 1:
                return np.array([]), index

            #axis_line = np.repeat(line, word_matrix.shape[0] - index - 1).reshape(word_matrix.shape[0] - index - 1, -1)

            #axis = np.logical_and.reduce(word_matrix[(index+1):] == axis_line, axis = 1)
            #axis = np.where(axis)[0]
            axis = []
            for remain_index in range(index + 1, len(word_matrix)):
                if word_matrix[remain_index] == word_matrix[line]:
                    axis.append(remain_index)

            axis = np.asarray(axis)

            if axis.size:
                # axis += index + 1
                # axis = np.concatenate((np.array([index]), axis), 0)
                return axis, index # these line should add one more word
            else:
                continue

        # np.logical_and.reduce(a == b, axis=1)
        return np.array([]), index



    @staticmethod
    def check_inputFormat(question_list):
        if isinstance(question_list[0], List):
            if len(question_list[0]) > 1:
                # [['a', 'bc', 'de'],['a', 'bc', 'de']]
                question_list = [' '.join([y if len(y) > 1 else y+'爞' for y in x]) for x in question_list]
            else:
                # [['a bc de'], ['a bc de']]
                question_list = [' '.join([y if len(y) > 1 else y+'爞' for y in x]) for x in [z[0].split() for z in question_list]]
        elif isinstance(question_list[0], Text):
            question_list = [' '.join([y if len(y) > 1 else y + '爞' for y in x]) for x in
                             [z.split() for z in question_list]]


        else:
            raise ValueError('Not supported corpus type temporarily')

        return question_list


# if __name__ == '__main__':
#     import pickle
#     test_sentence = [['是 由 古 中国 已经 时期 食肉类 进化 起源 比较'],
#                      ['发现 数个 分支 其中 古 猎豹 没能 幸存 猫 世纪'],
#                      ['由 古 时期 进化 起源 比较'],
#                      ['数个 分支 其中 猎豹 幸存 猫']]
#
#     with open('tfidf.model', 'rb') as f:
#         model = pickle.loads(f.read())
#
#     a = regexProcessor(test_sentence, model)
#
#     a.init_matrix()
#     a.search_main()
#     a.regexGenerator()
#     print(a.regexMapping)
