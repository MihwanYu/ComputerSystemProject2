import re


class Memory:
    def __init__(self, name, level):
        self.name = name
        self.level = level

        if self.level == 1:
            self.size = 1
        elif self.level == 2:
            self.size = 16
        elif self.level == 3:
            self.size = 256
        elif self.level == 4:
            self.size = 4096

        if self.level == 2:
            self.array = [{}, {}]
        else :
            self.array = [{}]



class StoreData:
    def __init__(self):
        self.tag = 0
        self.l1 = Memory(name = "l1", level = 1)
        self.l2 = Memory(name = "l2", level = 2)
        self.l3 = Memory(name = "l3", level = 3)
        self.l4 = Memory(name = "l4", level = 4)

    def load_data(self):
        file = open("Mariah Carey_2010.txt", "r")
        lyrics = file.read()

        # 전처리: 특수문자 제거, 알파벳 소문자 변환, 어절 분리
        self.new_lyric = lyrics.replace('\n', ' ')
        self.new_lyric = re.sub(r"[^a-zA-Z0-9 ]", "", self.new_lyric).lower().split()

        return self.new_lyric

    def read(self):
        words = self.load_data()

        for word in words:
            if len(self.l4.array[0]) != self.l4.size and word not in self.l4.array[0].values():
                self.l4.array[0][self.tag] = word
                self.tag += 1

        print(self.l4.array)

    def low_level_check(self):


