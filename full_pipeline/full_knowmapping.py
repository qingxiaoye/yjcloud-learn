'''
调各类辅助函数
实现:
    Data ---> Regex_mapping ---> Answer

输入:
dataStruct ---> Dict(question: index)
answerDict ---> Dict(index: answer)

1. Union(dataStruct.keys() + answerDict.values()) ---> tokenizer
2. tokenizer ---> tfidf
3. dataStruct.keys() <--- tfidf
4. arrange
'''

from fileReader import readFromExcel
from tokenizer import Tokenizer
from tfidf import tfidfProcessor
from regexMap import regexProcessor
import pickle
import os
import random

def konwMappingGenerator():
    print('file reader processor...')
    file_reader_op = readFromExcel(filepath = 'questionBase.xls')

    # ------------------
    file_reader_op.load_excel()
    train_data = list(file_reader_op.DataStrut.keys()) + \
                 list(file_reader_op.answerDict.values())


    # ------------------
    print('tokenizer processor...')
    tokenizer_op = Tokenizer(train_data)
    tokenizer_op.tokenizer()

    # ------------------
    print('tfidf processor...')
    tfidf_op = tfidfProcessor(lineList = tokenizer_op.unionSentence)

    print(len(tfidf_op.tfidfModel.vocabulary_))

    # ------------------
    print('regex processor...')

    regex_train_data_length = len(file_reader_op.DataStrut)
    regex_train_data = tokenizer_op.unionSentence[:regex_train_data_length]
    random_index = list(range(regex_train_data_length))
    #random_index = list(range(1000))
    #new_regex_train_data = []
    #for i in random_index:
    #   new_regex_train_data.append(regex_train_data[i])


    regex_mapping_op = regexProcessor(questionList = regex_train_data,
                                      tfidfModel = tfidf_op.tfidfModel,
                                      initK = 8,
                                      initIndex = random_index)

    regex_mapping_op.pipeline()

    print(regex_mapping_op.NoneRef)


    # ------------------
    print('arange...')
    regex2ans = arange_func(file_reader_op.answerDict,
                            regex_mapping_op.regexMapping, file_reader_op.query2row)


    save_regex_model(regex2ans)

    originQuery = tokenizer_op.index2text
    save_chooseData(regex2ans, regex_mapping_op.regexMapping, originQuery)
    # =====================

    print('Save Done...')


def arange_func(answer_dict, regex_mapping, query2row):
    '''
    :param answer_dict: dict ---> row2answer
    :param regex_mapping: dict ---> row2regex
    :param query2row: dict --->id2row
    :return: regex2answer
    '''
    # return {reg:ans for reg,ans in zip(regex_mapping.values(),
    #                                    answer_dict.values())}

    res_dict = {}
    for id, regex in regex_mapping.items():
        res_dict[regex] = answer_dict[query2row[id]]

    return res_dict



def save_regex_model(model):
    with open('regex2ans.model', 'wb') as f:
        f.write(pickle.dumps(model))


def save_chooseData(regex2ans, regexMapping, questionList):
    res = {}
    for index,val in regexMapping.items(): # index, regex
        query = questionList[index]
        answer = regex2ans[val]
        res[query] = answer

    with open('query2answer.model', 'wb') as f:
        f.write(pickle.dumps(res))
        

#if __name__ == '__main__':
konwMappingGenerator()
