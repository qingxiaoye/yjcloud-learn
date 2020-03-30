import pandas as pd
import pickle

query = []
regex = []
answer = []

with open('regex2ans.model', 'rb') as f:
    regex_model = pickle.loads(f.read())

with open('query2answer.model', 'rb') as f:
    query_model = pickle.loads(f.read())

print(len(regex_model))
print(len(query_model))


for reg, qu in zip(regex_model, query_model):
    query.append(qu)
    regex.append(reg)
    answer.append(regex_model[reg])

frame_data = pd.DataFrame({'query':query, 'regex':regex, 'answer':answer})
frame_data.to_csv('model_full.csv')

frame = pd.read_csv('model_full.csv')
regexlist = frame['regex'].to_list()
regexlist = [x[12:] for x in regexlist]


def readline(line):
    word_list = []
    inFlag = False
    sub_word = ''


    for word in line:
        if word == '(':
            inFlag = True
            continue

        if word == ')':
            if sub_word != '':
                word_list.append(sub_word)
            sub_word = ''
            inFlag = False
            continue

        if inFlag:
            sub_word += word
        else:
            sub_word = ''

    return word_list

wordList = []
for regex in regexlist:
    wordList.extend(readline(regex))

import codecs
with codecs.open('model_full_keyword.txt', 'wb', encoding = 'utf-8') as f:
    for word in wordList:
        f.write(word + '\n')