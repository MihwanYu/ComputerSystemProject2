# -*- coding: utf-8 -*-
"""
Created on Wed Dec  8 15:07:52 2021

@author: sally
"""
import re
import time
from os import chdir, getcwd
wd=getcwd()
chdir(wd)
#lyrics: on the ground + thank you next + rain on me

#%% data load and preprocessing
with open('./../Mariah Carey_1990s.txt', 'r') as f:
    lyrics= f.read()
#전처리: 특수문자 제거, 알파벳 소문자 변환, 어절 분리
new_lyric = lyrics.replace('\n',' ')
new_lyric = re.sub(r"[^a-zA-Z0-9 ]","",new_lyric).lower().split()
print(new_lyric)

#i, me 같이 무의미하게 반복되는 친구들(stopwords)
with open('./../stopwords_english.txt', 'r') as f:
    stopwords= f.read().split()

#stopwords 제거
new_lyric = [word for word in new_lyric if word not in stopwords]


#%% cache test
#normal iteration
word_count_iteration={}
s_time = time.time()
for word in new_lyric:
    if word_count_iteration.get(word)==None:
        word_count_iteration[word]=1
    else:
        word_count_iteration[word] +=1
        
print(word_count_iteration)
print('end time: ',time.time()-s_time)

#캐시블록: 캐시 레벨 안에 여러개 들어갈 수 있음. 1개 블록에는 valid, tag, memory block(offset)을 가짐
class cacheblock:
    def __init__(self):
        self.valid = False
        self.tag = 0
        self.memoryblock={} #offsets: 0-7
    
    #isfull(): 8개 메모리 블록이 모두 다 찼으면 true, 아니면 false반환
    def isfull(self):
        if len(self.memoryblock)==8: return True
        else: return False
    
    #메모리 블록에 단어 쌍을 추가함. word(key) : 1(frequency)
    def insert_into_offset(self, word):
        self.memoryblock[word] = 1
        

#캐시레벨: cache hierarchy를 위해 만듦.
#캐시 레벨 객체를 만들 때는 안에 몇 개 set있는지, block있는지, 하위 레벨 cache는 누군지 설정해줘야함
class cachelevel:
    def __init__(self, sets, low_level=None, E=1):
        self.sets = sets
        # self.blocks = self.make_blocks()
        self.blocks = []
        self.E = E
        self.low_level = low_level
    
    #캐시블록 배열 생성(레벨 객체 __init__에서 생성할 때 사용)
    def make_blocks(self):#일단 E=1일때로
        temp_blocks=[]
        for i in range(self.sets):
            temp_blocks.append(cacheblock())
        return temp_blocks
    
    #해당 레벨에 단어가 있는지 찾고, 찾으면 단어가 존재하는 블록 객체를 리턴함
    #단어가 없으면 하위 레벨에서 단어를 찾고, 단어가 존재하는 블록 객체를 리턴함
    def find_word(self, word):
        for b in self.blocks:
            if word in b.memoryblock:
                print('find word: located in block ',b)
                return self.blocks.index(b)
            
        return self.find_word_low_level(word)#근데 사실 찾았으면 빈도수 +1해줘야함
    
    #find_word()에서 사용하기 위한 함수. 하위 level 에서 단어 찾아오고, 상위 레벨에 단어가 존재하는 블록을 로드해줌
    def find_word_low_level(self, word):
        if self.low_level is not None:
            return self.low_level.find_word(word)
        else:
            self.insert_data(word)
            return self.find_word(word)
        
    #단어가 블록에 존재하지 않을 때 블록에 넣어줌
    def insert_data(self, word):
        for b in self.blocks:
            if b.isfull() is False:
                b.insert_into_offset(word)
                break
        #모든 blocks에 data 꽉 차있을 경우?
                


level3 = cachelevel(8)
level2 = cachelevel(4, low_level=level3)
level1 = cachelevel(2, low_level=level2)   #[캐시블록1, 캐시블록2]   캐시블록1 => valid, tag, memoryblock={'cant':1, 'live': 2 ....}


level3.find_word('word')

#cache
words_l1 = [   ] #len: 2  {0: [ 'cant':1, 'live':2 ... ]}, {1: ['give': 1, ...]}
words_l2 = [             ] #len: 4
words_l3 = [{0:[]} , {1:[]}, {2:[]}, {3:[]} , {4:[]} , {5:[]} , {6:[]} , {7:[]} ] #len: 8


for word in new_lyric:
    #l1에 있는지 없는지 확인
    if words_l1[0].get(word):
        words_l1[0][word] +=1
    elif words_l1[1].get(word):#있을 때
        #check l1 cache empty
        words_l1[1][word] +=1
    else:
        word_count_iteration[word] +=1



