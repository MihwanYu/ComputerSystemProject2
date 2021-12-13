import re

# %% data load and preprocessing
with open('lyrics.txt', 'r', encoding="utf-8") as f:
    lyrics = f.read()
# 전처리: 특수문자 제거, 알파벳 소문자 변환, 어절 분리
new_lyric = lyrics.replace('\n', ' ')
new_lyric = re.sub(r"[^a-zA-Z ]", "", new_lyric).lower().split()

# i, me 같이 무의미하게 반복되는 친구들(stopwords)
with open('stopwords_english.txt', 'r', encoding="utf-8") as f:
    stopwords = f.read().split()

# stopwords 제거
new_lyric = [word for word in new_lyric if word not in stopwords]
print(new_lyric)


# %% cache class
class cacheblock:
    num_of_blocks = 0

    def __init__(self, valid=False, sets=1):
        self.valid = valid
        self.tag = 0
        self.memoryblock = {}  # offsets: 0-7
        cacheblock.num_of_blocks += 1

    def isnotfull(self):
        if len(self.memoryblock) == 8:
            return False
        else:
            return True

    def insert_into_offset(self, word):
        self.memoryblock[word] = 1



class cachelevel:
    def __init__(self, low_level=None, E=1, size=0, cachename=''):
        self.blocks = []
        self.E = E
        self.low_level = low_level
        self.size = size
        self.cachename = cachename
        self.hit = 0
        self.miss = 0


    def find_word(self, word):
        for b in self.blocks:
            if word in b.memoryblock:
                self.blocks.remove(b)
                self.blocks.insert(0, b)
                b.memoryblock[word] += 1
                self.hit += 1
                return b.tag
        self.miss += 1
        b_tag = self.find_word_at_low_level(word)
        if self.low_level is not None:
            new_b = self.get_block_from_lower(b_tag)
            self.load_block(new_b)
        return b_tag


    def find_word_at_low_level(self, word):
        if self.low_level is None:
            tag = self.insert_word(word)
            return tag

        else:
            tag = self.low_level.find_word(word)
            return tag


    def insert_word(self, word):
        if len(self.blocks) == 0:
            tag = self.makeblock_withword(word)
            return tag

        b = self.blocks[-1]
        if b.isnotfull() is True:
            b.insert_into_offset(word)
            print('기존 블록에 단어 ', word, '를 추가했습니다. block의 태그 값은: ', b.tag)
            return b.tag

        else:
            tag = self.makeblock_withword(word)
            return tag


    def makeblock_withword(self, word):
        new_b = cacheblock()
        new_b.insert_into_offset(word)
        self.blocks.append(new_b)
        new_b.tag = cacheblock.num_of_blocks
        print('블록 생성 및 ', word, '값이 추가되었습니다. block의 태그 값은 : ', new_b.tag)
        return new_b.tag  # 방금 생성된 block의 태그 값 리턴


    def get_block_from_lower(self, b_tag):
        if self.low_level == None:
            return None
        for block in self.low_level.blocks:
            if block.tag == b_tag:
                return block


    def load_block(self, new_b):
        if new_b in self.blocks:
            return
        if len(self.blocks) < self.size:
            self.blocks.insert(0, new_b)

        elif len(self.blocks) == self.size:
            self.blocks.pop()
            self.blocks.insert(0, new_b)
        elif self.cachename == 'main_memory':
            print('최하위 메모리입니다. load_block 실행 하지 않습니다.')
        else:
            print('잘못된 상황. 캐시 안에 블록 수가 지정 사이즈보다 크다')


    def hit_miss_ratio(self):
        return self.hit / (self.hit + self.miss)


with open('cmp_lyrics.txt', 'r', encoding="utf-8") as f:
    lyrics2 = f.read()

# %% class 객체 생성
main_memory = cachelevel(cachename='main_memory')
level4 = cachelevel(cachename='level4', size=4096, low_level=main_memory)
level3 = cachelevel(cachename='level3', size=256, low_level=level4)
level2 = cachelevel(cachename='level2', size=16, low_level=level3)
level1 = cachelevel(cachename='level1', size=1, low_level=level2)

tens = new_lyric

for word in tens:
    print('검색 word: ', word)
    level1.find_word(word)

for level in [level1, level2, level3, level4]:
    level.hit = 0
    level.miss = 0

new_lyric2 = lyrics2.replace('\n', ' ')
new_lyric2 = re.sub(r"[^a-zA-Z ]", "", new_lyric2).lower().split()

new_lyric2 = [word for word in new_lyric2 if word not in stopwords]

tens2 = new_lyric2

for word in tens2:
    print('검색 word: ', word)
    level1.find_word(word)

print('\n\n____________________________________')

for level in [level1, level2, level3, level4]:
    hitRatio = level.hit_miss_ratio() * 100
    print('%s의 hit ratio는 %.2f%%' % (level.cachename, hitRatio))
