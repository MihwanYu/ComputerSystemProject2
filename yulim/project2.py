# -*- coding: utf-8 -*-
"""
Created on Wed Dec  8 15:07:52 2021

@author: sally
"""
import re
import time

L1_SIZE = 1
L2_SIZE = 16
L3_SIZE = 256
L4_SIZE = 4096

l1 = [{}]
l2 = [{}]
l3 = [{}, {}]
l4 = [{}]

file = open("Mariah Carey_2010.txt", "r")
lyrics = file.read()

# 전처리: 특수문자 제거, 알파벳 소문자 변환, 어절 분리
new_lyric = lyrics.replace('\n', ' ')
new_lyric = re.sub(r"[^a-zA-Z0-9 ]", "", new_lyric).lower().split()
print(new_lyric)
print()

# normal iteration
word_count_iteration = {}
s_time = time.time()
for word in new_lyric:
    if word_count_iteration.get(word) == None:
        word_count_iteration[word] = 1
    else:
        word_count_iteration[word] += 1

print(word_count_iteration)
print('end time: ', time.time() - s_time)

# cache
stopwords = ['me', 'i', 'and', 'yeah', 'oh', 'im', 'are']
# words_l1 = {0: dict(zip(stopwords, [0] * len(stopwords))), 1: {}}  # len: 2
# words_l2 = {0: {}, 1: {}, 2: {}, 3: {}}  # len: 4
# words_l3 = {0: {}, 1: {}, 2: {}, 3: {}, 4: {}, 5: {}, 6: {}, 7: {}}  # len: 8

# for word in new_lyric:
#     # l1에 있는지 없는지 확인
#     if words_l1[0].get(word):
#         words_l1[0][word] += 1
#     elif words_l1[1].get(word):  # 있을 때
#         # check l1 cache empty
#         words_l1[1][word] += 1
#     else:
#         word_count_iteration[word] += 1

tag = 0
for word in new_lyric:
    if len(l4[0]) != L4_SIZE and word not in l4[0].values():
        l4[0][tag] = word

        # if len(l3[0]) != L3_SIZE:
        #     l3[0][tag] = l4[0].get(tag)
        # elif len(l3[1]) != L3_SIZE:
        #     l3[1][tag] = l4[0].get(tag)
        # if len(l2[0]) != L2_SIZE:
        #     l2[0][tag] = l3[0].get(tag)
        # if len(l1[0]) != L1_SIZE:
        #     l1[0][tag] = l2[0].get(tag)

        tag += 1
