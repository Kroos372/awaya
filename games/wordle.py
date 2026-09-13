from static import Awaish, now, timeDiff, word_trans
import random

with open("files/valid_words.txt") as f:
    WORD_LIST = [line.strip() for line in f]

WORDLEMENU = "\n".join([
    "Wordle!",
    "w start: 开始游戏",
    "   - w start !: 严格模式",
    "   - w start !!: 困难模式，只返回A(🟩)与B(🟨)的个数，不显示具体字母",
    "w <word>: 猜词",
    "w .: 查看局势",
    "w hint: 提示",
    "w end: 放弃",
    "w rule: 规则",
    "w ? <word>: 查词典"
])
WORDLERULE = "\n".join([
    "6次机会，猜一指定五字单词",
    "==高亮==(🟩)表示该字母位置正确",
    "***斜体***(🟨)表示该字母位置不正确",
    "否则(⬛)表示答案中没有该字母"
])

class Word:
    WRONG = 0
    HALF_CORRECT = 1
    CORRECT = 2
    def __init__(self, word: str):
        self.word = word
        self.mask: list = [self.WRONG] * 5
        self.solved: bool = False
    def __str__(self):
        texts = []
        colors = []
        for (i, letter) in enumerate(self.word):
            letter = letter.upper()
            if self.mask[i] == self.CORRECT:
                texts.append(f"=={letter}==")
                # colors.append("🟩")
            elif self.mask[i] == self.HALF_CORRECT:
                texts.append(f"***{letter}***")
                # colors.append("🟨")
            else:
                texts.append(f"{letter}")
                # colors.append("⬛")

        # return to_fullwidth(" ".join(texts)) + "\n" + "".join(colors)
        return to_fullwidth(" ".join(texts))

    def compare(self, answer: str):
        letter_count: dict[str, int] = {}
        for letter in set(answer):
            letter_count[letter] = answer.count(letter)

        # 先判断是否完全正确
        for (i, letter) in enumerate(self.word):
            if answer[i] == letter:
                self.mask[i] = self.CORRECT
                letter_count[letter] -= 1
        # 再判断是否位置错误
        for (i, letter) in enumerate(self.word):
            if letter_count.get(letter) and self.mask[i] == self.WRONG:
                self.mask[i] = self.HALF_CORRECT
                letter_count[letter] -= 1
                
        if answer == self.word:
            self.solved = True

class WordHard(Word):
    def __init__(self, word: str):
        super().__init__(word)
        self.As = 0
        self.Bs = 0

    def __str__(self):
        return f"{self.word} -> {self.As}A{self.Bs}B"
    
    def compare(self, answer: str):
        letter_count: dict[str, int] = {}
        for letter in set(answer):
            letter_count[letter] = answer.count(letter)

        # 先判断是否完全正确
        for (i, letter) in enumerate(self.word):
            if answer[i] == letter:
                self.mask[i] = self.CORRECT
                self.As += 1
                letter_count[letter] -= 1
        # 再判断是否位置错误
        for (i, letter) in enumerate(self.word):
            if letter_count.get(letter) and self.mask[i] == self.WRONG:
                self.Bs += 1
                letter_count[letter] -= 1

        if answer == self.word:
            self.solved = True


class Wordle:
    def __init__(self):
        self.context: Awaish
        self.status: int = 0

        self.strict: bool = False
        self.hardmode: bool = False

        self.answer: str
        self.life: int
        self.history: list[Word]
        self.start_time: int
    
    def start(self, mode: int=0):
        self.status = 1
        self.life = 6
        self.start_time = now()
        self.history = []
        if mode == 0:
            self.strict = False
        elif mode == 1:
            self.strict = True
        elif mode == 2:
            self.hardmode = True
            self.life = 15

        with open("files/word_bank.txt") as f:
            WORD_BANK = f.readlines()
            self.answer = random.choice(WORD_BANK).strip()
        
        self.context.appText("游戏开始！发送==w <word>==猜测吧！")
    
    def guess(self, sender: str, msg: str):
        msg = msg.lower()
        if msg not in WORD_LIST:
            self.context.appText(f"{msg} 不是合法的单词")
            return
        for word in self.history:
            if word.word == msg:
                self.context.appText(f"{msg} 已经猜过了")
                return

        if self.hardmode:
            word = WordHard(msg)
        else:
            word = Word(msg)
        
        if self.strict and self.history:
            last_word = self.history[-1]
            half_letters = []
            # 先检查之前对的有没有用上&位置错的有没有没变
            for i, letter in enumerate(last_word.word):
                if last_word.mask[i] == Word.CORRECT and msg[i] != letter:
                    self.context.appText(f"你没有用上{letter}!")
                    return
                if last_word.mask[i] == Word.HALF_CORRECT:
                    half_letters.append(letter)
                    if msg[i] == letter:
                        self.context.appText(f"都说啦{letter}不在第{i+1}位")
                        return
            # 有没有用上位置错误的
            for letter in half_letters:
                if letter not in msg:
                    self.context.appText(f"你没有用上{letter}!")
                    return
        
        word.compare(self.answer)
        self.history.append(word)
        
        self.context.appText(f"{sender} 猜测了 {msg}")
        self.context.appText("\n---")
        self.context.appText(self.format())
        self.context.appText("\n---")
        
        self.life -= 1
        if word.solved:
            self.context.appText("获胜！🍾🍾🍾")
            self.context.appText(f"用时{timeDiff(now() - self.start_time)}, {6 - self.life}次！")
            self.status = 0
        elif self.life < 1:
            self.end()
        else:
            self.context.appText(f"还剩{self.life}次机会！")
    
    def end(self):
        self.context.appText("失败了……")
        self.context.appText(f"答案是 **{self.answer}**")
        self.context.appText(word_trans(self.answer))
        
        self.status = 0
        self.hardmode = self.strict = False

    def format(self) -> str:
        lines = [str(word) for word in self.history]
        return "\n".join(lines)
    
    def hint(self) -> str:
        if random.random() > 0.5:
            index = random.randint(1, 5)
            self.context.appText(f"这个单词的第{index}位是{self.answer[index-1]}!")
        
        else:
            letter_count: dict[str, int] = {}
            for letter in set(self.answer):
                letter_count[letter] = self.answer.count(letter)

            letter = random.choice(self.answer)
            self.context.appText(f"这个单词里有{letter_count[letter]}个{letter.upper()}!")
    
    def get_types(self) -> dict[str, set]:
        unused = set("abcdefghijklmnopqrstuvwxyz")
        wrong = set()
        half = set()
        correct = set()
        
        for word in self.history[::-1]:
            for (i, letter) in enumerate(word.word):
                if letter not in unused:
                    continue
                if word.mask[i] == Word.CORRECT:
                    correct.add(letter)
                elif word.mask[i] == Word.HALF_CORRECT:
                    half.add(letter)
                else:
                    wrong.add(letter)
                unused.remove(letter)
        return {
            "unused": unused,
            "correct": correct,
            "half": half,
            "wrong": wrong
        }

    def check(self) -> str:
        data = self.get_types()
        if self.hardmode:
            unused = "现在是困难模式"
        else:
            unused = " ".join(sorted(data['unused']))
        return "\n".join([
            self.format(),
            "",
            "---",
            "未使用字母: " + unused
        ])

def to_fullwidth(s: str):
    return s.translate(str.maketrans(
        "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "０１２３４５６７８９ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ"
    ))

def main(context: Awaish, sender: str, msg: str):
    msg_list = msg.split(" ")
    if msg == "help":
        context.appText(WORDLEMENU)
    elif msg == "rule":
        context.appText(WORDLERULE)
    elif msg_list[0] == "start" and not wordle.status:
        wordle.context = context
        if len(msg_list) < 2:
            wordle.start()
        elif msg_list[1] == "!":
            wordle.start(1)
        elif msg_list[1] == "!!":
            wordle.start(2)
    elif msg_list[0] == "?":
        if len(msg_list) < 2:
            return
        context.appText(word_trans(msg_list[1]))
    elif wordle.status:
        if msg == ".":
            context.appText(f"还剩{wordle.life}次机会\n\n---")
            context.appText(wordle.check())
        elif msg == "end":
            wordle.end()
        elif msg == "hint":
            wordle.hint()
        else:
            wordle.guess(sender, msg)

wordle = Wordle()