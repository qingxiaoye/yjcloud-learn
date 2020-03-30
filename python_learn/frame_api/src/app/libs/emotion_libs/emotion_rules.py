'''
Temporarily design: predict each emotion class for a dialogue
Input: (sentence, ori_label)
        ---> ori_label: default: 0
Output: [label string] ---> list
'''

import torch
from torch.autograd import Variable
# from app.libs.emotion_libs.Preprocess import Dictionary
from app.libs.emotion_libs.Preprocess import Dictionary
import pickle
import os
# from app.libs.emotion_libs.Utils import ToTensor
from app.libs.emotion_libs.Utils import ToTensor

PAD = 0
UNK = 1
PAD_WORD = '<pad>'
UNK_WORD = '<unk>'
MAX_SEQ_LEN = 60
GPU = False
Weight = 0.7
Thread = 0.5

def load_vocab(vocabPath, vocabEmo):
    with open(vocabPath, 'rb') as f:
        vocab = pickle.load(f)

    with open(vocabEmo, 'rb') as f:
        vocab_emo = pickle.load(f)

    return vocab, vocab_emo


def get_feat(convers, vocab):
    '''
    :params: convers: List conversation
    Notes: each line been split up and no punctuation exist
    '''
    if not isinstance(convers, list):
        raise ValueError('No support type except of list')

    dia_idxs = []
    emo_list = []

    for sentence, emo in convers:
        d_idxs = [vocab.word2index[w] if w in vocab.word2index else UNK for w in sentence.split(' ')]
        emo_list.append(emo)

        if len(d_idxs) > MAX_SEQ_LEN:
            dia_idxs.append(d_idxs[:MAX_SEQ_LEN])

        else:
            dia_idxs.append(d_idxs + [PAD] * (MAX_SEQ_LEN - len(d_idxs)))

    return dia_idxs, emo_list

def smooth_score(pre_score, ori_socre, weigth, thread):
    total_score = pre_score * (1 - weigth) + ori_socre * weigth
    return ori_socre if total_score > thread else pre_score



def get_prediction(feats, model, vocab_emo, emo_list,
                   weight, thread):
    model.eval()

    feat, lens = ToTensor(feats, is_len = True)
    feat = Variable(feat)

    if GPU:
        os.environ['CUDA_VISIBLE_DEVICES'] = GPU
        device = torch.device('cuda: 0')
        model.cuda(device)
        feat = feat.cuda(device)

    log_prob = model(feat, lens)
    emo_predidx = torch.argmax(log_prob, dim=1).tolist()
    # {'0':'normal', '1': negative}

    emo_predidx = [smooth_score(x, y, weight, thread) for x,y in zip(emo_predidx, emo_list)]

    # print('Prediction Label:')
    # print([vocab_emo.index2word[x] for x in emo_predidx])

    return ([vocab_emo.index2word[x] for x in emo_predidx])


# if __name__ == '__main__':
#     model = torch.load('./snapshot/higru-sf_DownloadedYyh.pt', map_location='cp')
#
#     sentence = [('您好，请给我们的服务进行点评',0),
#                 ('我觉得这次的外卖太难吃了差评',0),
#                 ('哈哈哈哈说的对',0),
#                 ('所以今天你让我很生气',0)]
#     vocab, vocab_emo = load_vocab('DownloadedYyh_vocab.pt', 'DownloadedYyh_emodict.pt')
#     feats, emo_list = get_feat(sentence, vocab)
#     get_prediction(feats, model, vocab_emo, emo_list, Weight, Thread)
#

