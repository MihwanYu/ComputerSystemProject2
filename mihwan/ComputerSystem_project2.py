# -*- coding: utf-8 -*-
"""
Created on Wed Dec  8 15:07:52 2021

@author: mihwan_yu
"""
import re
import time

# lyrics: on the ground + thank you next + rain on me

# %% data load and preprocessing
with open('C:/Users/sally/Desktop/2021-2/학사/Computer System/과제/팀플2/ComputerSystemProject2/lyrics.txt',
          'r') as f:
    lyrics = f.read()
# 전처리: 특수문자 제거, 알파벳 소문자 변환, 어절 분리
new_lyric = lyrics.replace('\n', ' ')
new_lyric = re.sub(r"[^a-zA-Z0-9 ]", "", new_lyric).lower().split()
print(new_lyric)

# i, me 같이 무의미하게 반복되는 친구들(stopwords)
with open('C:/Users/sally/Desktop/2021-2/학사/Computer System/과제/팀플2/ComputerSystemProject2/stopwords_english.txt',
          'r') as f:
    stopwords = f.read().split()

# stopwords 제거
new_lyric = [word for word in new_lyric if word not in stopwords]


# %% cache class

# 캐시블록: 캐시 레벨 안에 여러개 들어갈 수 있음. 1개 블록에는 valid, tag, memory block(offset)을 가짐
class cacheblock:
    num_of_blocks = 0

    def __init__(self, valid=False, sets=1):  # 사실 set이랑 valid는 필요 없을듯
        self.valid = valid
        self.tag = 0
        self.memoryblock = {}  # offsets: 0-7
        cacheblock.num_of_blocks += 1

    # isnotfull(): 8개 메모리 블록이 모두 다 찼으면 true, 아니면 false반환
    def isnotfull(self):
        if len(self.memoryblock) == 8:
            return False
        else:
            return True

    # 메모리 블록에 단어 쌍을 추가함. word(key) : 1(frequency)
    def insert_into_offset(self, word):
        self.memoryblock[word] = 1


# 캐시레벨: cache hierarchy를 위해 만듦.
# 캐시 레벨 객체를 만들 때는 안에 몇 개 set있는지, block있는지, 하위 레벨 cache는 누군지 설정해줘야함
class cachelevel:
    def __init__(self, low_level=None, E=1, size=0, cachename=''):
        # self.blocks = self.make_blocks()
        self.blocks = []
        self.E = E
        self.low_level = low_level
        self.size = size  # 메인 메모리는 음.... 기본값 0으로 들어가긴 하지만 size가 사용되지 않음
        self.cachename = cachename
        self.hit = 0
        self.miss = 0

    # 해당 레벨에 단어가 있는지 찾고, 찾으면 단어가 존재하는 블록 객체를 리턴함
    # 단어가 없으면 하위 레벨에서 단어를 찾고, 단어가 존재하는 블록 객체를 리턴함
    def find_word(self, word):
        for b in self.blocks:  # b는 블록 객체
            if word in b.memoryblock:
                # print(self.cachename, '에서 word를 찾았습니다. ',b,'블록에 존재합니다.')
                self.blocks.remove(b)  # 블록 b를 blocks 리스트 맨 앞에 갖다 주기 위해 뺐다가 다시 삽입함
                self.blocks.insert(0, b)
                b.memoryblock[word] += 1  # 빈도수1 증가시켜줌
                print('찾은 word의 빈도수는 ', b.memoryblock[word], '입니다.')
                self.hit += 1
                return b.tag  # word가 존재하는 block의 tag를 리턴
                # 근데 사실 찾았으면 빈도수 +1해줘야함 <<아직 구현x
        # print('현재 level ', self.cachename,'에 word가 없습니다. 다음 level에서 재검색합니다.')
        # 하위 레벨에서 단어 검색 후, 단어가 존재하는 block의 tag값 받아옴-> 그 블록을 내 레벨에 로드함
        self.miss += 1
        b_tag = self.find_word_at_low_level(word)
        if self.low_level is not None:  # 하위 메모리가 아닐 경우에는
            new_b = self.get_block_from_lower(b_tag)  # b_tag 값 통해서 하위 캐시 계층으로부터 블록 객체를 가져옴
            self.load_block(new_b)  # 하위 계층에서 받아온 block을 현재 레벨에 로드함(맨 앞)
        return b_tag

    # 목적: 하위 레벨에 word가 있는지 확인, 있으면-> 그 word가 있는 block을 현재 메모리에 로드, block의 태그 값 리턴
    # 최하위 메모리일 경우-> 그 word를 block에 추가하고, word가 추가된 block을 현재 메모리에 로드, block의 태그 값 리턴
    def find_word_at_low_level(self, word):
        # 현재 메모리가 가장 하위 메모리인 경우:
        #   insert_word 함수 호출해서 {word:1} key-value 쌍을 offset에 추가
        if self.low_level is None:
            tag = self.insert_word(word)
            print('최하위 메모리의 [block ', tag, ']에 word', word, '값이 추가되었습니다.')
            return tag

        # 하위에 다른 메모리 계층이 존재하는 경우:
        #   하위 메모리에서 단어 찾음 -> 단어가 존재하는 블록을 내 계층에 넣음
        else:
            tag = self.low_level.find_word(word)  # 얘가 그 블록의 인덱스 값을 알아와야 함
            # self.load_block(tag) #tag값 이용해서 블록을 내 레벨에 로드<<이거 필요없음
            print('하위 메모리', self.low_level.cachename, '에서 block ', tag, '및 word', word, '값을 찾아왔습니다.')
            return tag
            # 단어가 존재하는 블록을 내 계층에 넣으려면 어떻게 할까- 하위에서 그 블록의 태그 값을 알아내서 가져와야겠지,
            # 내 계층이 이미 꽉 찼다면 다른 애랑 바꿔치기 해야겠지-> 맨 뒤에 있는 블록을 pop 할거임

    # 호출 배경: word가 현재 최하위 메모리에 존재하지 않음. 목적: word:1 쌍을 추가하고, 추가된 block의 태그를 리턴
    def insert_word(self, word):
        # 아주 처음, 블록이 없을 경우, 최하위 메모리에 블록 생성과 동시에 word를 블록에 추가하고 함수 종료
        if len(self.blocks) == 0:
            tag = self.makeblock_withword(word)
            return tag  # 첫번째 cache blcok의 태그 값은 1

        # 기존에 존재하던 블록 중 가장 마지막 블록 b에 공간이 남아있다면 그 블록에 단어 쌍을 추가함
        b = self.blocks[-1]
        if b.isnotfull() is True:
            b.insert_into_offset(word)
            # print('기존 블록에 단어 ',word,'를 추가했습니다. block의 태그 값은: ', b.tag)
            return b.tag
        # 모든 blocks에 data 꽉 차있을 경우-> 블록 생성과 동시에 word를 블록에 추가
        else:
            tag = self.makeblock_withword(word)
            return tag

    # 호출 배경 및 목적: 최하위 메모리에 block을 {word:1} 쌍과 함께 추가
    def makeblock_withword(self, word):
        new_b = cacheblock()
        new_b.insert_into_offset(word)
        self.blocks.append(new_b)
        new_b.tag = cacheblock.num_of_blocks
        print('블록 생성 및 ', word, '값이 추가되었습니다. block의 태그 값은 : ', new_b.tag)
        return new_b.tag  # 방금 생성된 block의 태그 값 리턴

    # 호출 배경 및 목적: find_word 함수에서 하위 레벨의 block 객체를 현재 level에 로드하고자
    def get_block_from_lower(self, b_tag):
        if self.low_level == None:
            # print('현재 위치가 최하위 메모리입니다. 블록 객체를 리턴하지 않습니다.')#<<애초에 실행 안될걸?
            return None
        for block in self.low_level.blocks:
            # print('하위 메모리는 ',self.low_level.cachename, '입니다. 하위 메모리에 존재하는 블록 객체를 리턴합니다. b_tag: ',b_tag)
            if block.tag == b_tag:
                return block

    # 호출 배경 및 목적: 새로운 블록 객체를 현재 캐시 레벨에 로드
    def load_block(self, new_b):
        if new_b in self.blocks:  # 이미 그 블록 객체가 존재할 경우에는 추가 안하고 함수 종료
            return
        # print('새로운 블록 객체를 현재 캐시 레벨에 로드합니다. 현재 캐시 레벨: ',self.cachename)
        if len(self.blocks) < self.size:
            self.blocks.insert(0, new_b)
            # 블록 로드 쌉가능
        elif len(self.blocks) == self.size:
            # 블록 하나 지워야함
            self.blocks.pop()
            self.blocks.insert(0, new_b)
        elif self.cachename == 'main_memory':
            print('최하위 메모리입니다. load_block 실행 하지 않습니다.')
        else:
            print('잘못된 상황. 캐시 안에 블록 수가 지정 사이즈보다 크다--> 개쌉오바')

    def hit_miss_ratio(self):
        return self.hit / (self.hit + self.miss)


# %% class 객체 생성
main_memory = cachelevel(cachename='main_memory')  # 메인 메모리
level4 = cachelevel(cachename='level4', size=4096, low_level=main_memory)
level3 = cachelevel(cachename='level3', size=256, low_level=level4)
level2 = cachelevel(cachename='level2', size=16, low_level=level3)
level1 = cachelevel(cachename='level1', size=1, low_level=level2)

# cache = cachelevel(size=16, low_level = main_memory, cachename='cache') #캐시
# register = cachelevel(size=1, low_level = cache, cachename='register') #레지스터


# tens = ['love', 'someone', 'deeply', 'become', 'life', 'easy', 'succumb', 'whelming', 'fears', 'inside']
tens = new_lyric
# sample_str = ['happy', 'ever', 'after', 'does', 'exist', 'on', 'the', 'ground', 'been', 'so', 'long', 'please', 'come', 'home', 'miss', 'you', 'been', 'so', 'long', 'distance', 'vicious', 'miss', 'you', 'send', 'wishes', 'on', 'whishes', 'pretty', 'perfect', 'you', 'but', 'seem', 'uncertain', 'wanna', 'love', 'you', 'listen', 'my', 'words', 'please', 'come', 'home']
# tens = sample_str
for word in tens:
    print('검색 word: ', word)
    level1.find_word(word)
    # print('검색 완료 및 빈도수 추가 완료')

print('\n\n____________________________________')
for level in [level1, level2, level3, level4]:
    print(level.cachename, '의 hit ratio는 ', level.hit_miss_ratio())