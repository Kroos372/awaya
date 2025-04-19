import random, re

# [0扑克开关, 1{在玩的人:[拥有的牌]}, 2轮到序号, 3当前牌堆, 4底牌, 5地主, 6是否在叫牌阶段, 7[玩家名称], 8叫了几分, 9本轮第一出牌的序号, 10上家的牌]
pokers = [False, {}, 0, [], [], None, False, [], 0, None, None]
CARDS = ["3", "4", "5", "6", "7", "8", "9", "H", "J", "Q", "K", "A", "2"]
JOKERS = ["小", "大"]
SORT = CARDS + JOKERS
PINIT = CARDS*4 + JOKERS

POKERMENU = "\n".join([
    "斗地主...",
    "p 加入: 开始或加入一场斗地主，满三人后自动开始。",
    "p 退出: 在开始之前退出对局。",
    "p <牌>: 出牌，具体规则请查看出牌规则。",
    "p 结束: 在对局中结束游戏。",
    "p 规则: 获取扑克的出牌规则。",
])
POKERRULE = "\n".join([
    "游戏规则请自行参考[此处](https://baike.baidu.com/item/%E4%B8%89%E4%BA%BA%E6%96%97%E5%9C%B0%E4%B8%BB/9429860)(<-是个链接)，要注意的是这里用==H==代表==10==，==小==代表小王，==大==代表大王。以下是出牌规则：",
    "使用==p 牌==出牌，例如==p 1==, ==p J==，大小写均可；",
    "使用==p .==跳过回合、==p check==查看自己目前的牌；",
    "多张相同面值的牌间使用==牌*张数==，例如==p 3*2==，==p 4*3==；",
    "顺子使用==最小牌-最大牌==，例如==p 4-8==，==p 6-A==；",
    "双顺或三顺使用==最小-最大*张数==，例如==p 3-5*2==，==p 4-5*3==；",
    "三带二、飞机等带的对子中不使用==*==，例如==p K*3 77==，==p 8-9*3 33 44==",
    "王炸直接发送==p 王炸==即可；",
    "剩余的就将这两种组合，不同组别用空格隔开即可，例如==p 4-5*3 7 9== ==p 7*4 99 HH==……",
    "玩得开心~"
])

def allCards() -> str:
    return "玩家牌数: " + ", ".join([f"{i}: {len(pokers[1][i])}" for i in pokers[7]])
def landonwer(context, sender: str): 
    pokers[5] = sender
    pokers[6] = False
    pokers[9] = pokers[2]
    pokers[2] = pokers[7].index(pokers[5])
    pokers[1][sender] += pokers[4]
    pokers[1][sender].sort(key=lambda x: SORT.index(x))
    cards = " ".join(pokers[1][sender])
    context.appText(f"{' '.join(pokers[4])}是底牌，{sender}是地主。\n游戏开始，地主@{sender} 先出，发送==p 规则==可以查看出牌规则哦；")
    context.appText(f"以下是您的牌：{cards}", "whisper")
def passLand(context):
    pokers[2] = (pokers[2]+1) % 3
    if pokers[2] == pokers[9]:
        landonwer(context, pokers[7][pokers[2]])
# 飞机带的是否为同类
def sameLen(seq) -> bool:
    try:
        length = len(seq[0])
        for i in seq[1:]:
            if len(i) != length or len(set(i))!=1 or not seq[0][0] in SORT: return False
        return True
    except:
        return False
def endPoker():
    pokers[0], pokers[1], pokers[2] = False, {}, 0
    pokers[4], pokers[8], pokers[10] = [], 0, None
    pokers[5] = None

def main(context, sender: str, msg: str):
    msg = msg.upper()
    if msg == "规则":
        context.appText(POKERRULE)
    elif msg == "HELP":
        context.appText(POKERMENU)
    elif msg == "结束" and sender in pokers[7]:
        endPoker()
        context.appText("唔，结束了;;;;")
    elif msg == "CHECK" and sender in pokers[7] and not pokers[6]:
        context.appText(f"地主是{pokers[5]}, 上家出的牌是：{pokers[10]}\n{allCards()}\n以下是您的牌：{' '.join(pokers[1][sender])}", "whisper")
    elif pokers[0] and sender == pokers[7][pokers[2]]:
        # 叫牌阶段
        if pokers[6]:
            if msg[0] == "0":
                passLand(context)
                if pokers[6]:
                    context.appText(f"{sender}不叫，轮到@{pokers[7][pokers[2]]} ")
            elif msg[0] in ["1", "2", "3"]:
                point = int(msg[0])
                if point == 3:
                    landonwer(context, sender)
                else:
                    if pokers[8] >= point:
                        context.appText("叫的数字必须比前面的大！")
                    else:
                        pokers[8] = point
                        pokers[9] = pokers[2]
                        passLand(context)
                        if not pokers[5]:
                            context.appText(f"{sender}叫出了{point}点，轮到@{pokers[7][pokers[2]]} ")
            else: 
                context.appText("命令错误，请先叫分")
        # 出牌阶段
        else:
            # 跳过
            if msg == ".":
                if pokers[10] is None:
                    context.appText("由你开始的啦，随便出一张吧。")
                else:
                    pokers[2] = (pokers[2]+1)%3
                    if pokers[2] == pokers[9]:
                        pokers[10] = None
                        context.appText(f"所有玩家都要不起，@{pokers[7][pokers[2]]} 继续出牌。")
                    else:
                        context.appText(f"{sender}跳过，轮到@{pokers[7][pokers[2]]} 。")
            else:
                senderCards = pokers[1][sender]
                # 本轮第一发
                if pokers[10] is None:
                    # 单张
                    if msg in SORT and msg in senderCards:
                        senderCards.remove(msg)
                    # 对子或三张或四张
                    elif re.match(r"^[2-9AHJQK]\*[234]$", msg):
                        if senderCards.count(msg[0])>=int(msg[-1]):
                            for _ in range(int(msg[-1])): senderCards.remove(msg[0])
                        else: return context.appText("牌数不足！")
                    # 顺子
                    elif re.match(r"^[3-9AHJQK]-[3-9AHJQK]$", msg):
                        start, end = CARDS.index(msg[0]), CARDS.index(msg[-1])
                        if (end-start) >= 4:
                            for i in CARDS[start:end+1]:
                                if not i in senderCards:
                                    return context.appText("拥有的牌不够！")
                            for i in CARDS[start:end+1]:
                                senderCards.remove(i)
                        else: return context.appText("顺子最少五个！")
                    # 三带一、三带二
                    elif re.match(r"^[2-9AHJQK]\*3 [2-9AHJQK大小]{1,2}$", msg):
                        mult = len(msg.split()[1])
                        if msg[-1] != msg[0]:
                            condition = senderCards.count(msg[0])>=int(msg[2]) and senderCards.count(msg[-1])>=mult
                        # 不会真有人出6*3 6这种的吧
                        else:
                            condition = senderCards.count(msg[0])>=(int(msg[2])+mult)
                        if condition:
                            for i in range(int(msg[2])): senderCards.remove(msg[0])
                            for i in range(mult): senderCards.remove(msg[-1])
                        else: return context.appText("牌数不足！")
                    # 双顺、三顺
                    elif re.match(r"^[3-9AHJQK]-[3-9AHJQK]\*[23]$", msg):
                        start, end, mult = CARDS.index(msg[0]), CARDS.index(msg[2]), int(msg[-1])
                        if (end-start) >= (4-mult):
                            for i in CARDS[start:end+1]:
                                if senderCards.count(i) < mult:
                                    return context.appText("拥有的牌不够！")
                            for i in CARDS[start:end+1]:
                                for _ in range(mult): senderCards.remove(i)
                        else: return context.appText("牌数不够，三顺最少两个，双顺最少三个;")
                    # 四带二
                    elif re.match(r"([2-9AHJQK])\*4 (?!.*?\1)(?:([2-9AHJQK])\2 ([2-9AHJQK])\3|[2-9AHJQK大小] [2-9AHJQK大小])$", msg):
                        array = msg.split()[1:]
                        if senderCards.count(msg[0])==4 and senderCards.count(array[0])>=len(array[0]) and senderCards.count(array[1])>=len(array[1]):
                            for _ in range(4): senderCards.remove(msg[0])
                            for i in "".join(array): senderCards.remove(i)
                        else: return context.appText("牌不够，;;;")
                    # 飞机
                    elif re.match(r"^[3-9AHJQK]-[3-9AHJQK]\*3 $", msg[:6]):
                        start, end = CARDS.index(msg[0]), CARDS.index(msg[2])
                        if (end-start) < 1: return context.appText("牌数不够;")
                        else:
                            array = msg[6:].split(" ")
                            if sameLen(array) and len(array) == (end-start+1):
                                for i in CARDS[start:end+1]:
                                    if senderCards.count(i) < 3: return context.appText("牌数不足;;;;")
                                    if i in array or i+i in array: return context.appText("别搞")
                                for i in array:
                                    if senderCards.count(i[0]) < len(i):
                                        return context.appText("牌数不足;;;;")
                                for i in CARDS[start:end+1]:
                                    for _ in range(3): senderCards.remove(i)
                                for i in "".join(array):
                                    senderCards.remove(i)
                            else: return context.appText("不符合规则！")
                    # 炸弹
                    elif re.match(r"^[2-9AHJQK]\*4$", msg):
                        if senderCards.count(msg[0])<4: return context.appText("牌数不足！")
                        for _ in range(4): senderCards.remove(msg[0])
                    # 6
                    elif msg == "王炸":
                        if not ("大" in senderCards and "小" in senderCards): return context.appText("牌数不足！")
                        else:
                            senderCards.remove("大")
                            senderCards.remove("小")
                    else: return context.appText("命令不正确或牌数不足，请查看规则后重试;")
                else:
                    last = pokers[10]
                    # 单张
                    if last in SORT and msg in SORT and msg in senderCards:
                        if SORT.index(msg) <= SORT.index(last):
                            return context.appText(f"你的牌没有{last}大！")
                        senderCards.remove(msg)
                    # 对子或三张或四张
                    elif re.match(r"^.\*.$", last) and re.match(rf"^[2-9AHJQK]\*{last[-1]}$", msg):
                        if senderCards.count(msg[0])>=int(msg[-1]):
                            if SORT.index(msg[0]) <= SORT.index(last[0]): return context.appText(f"你的牌没有{last}大！")
                            for _ in range(int(msg[-1])): senderCards.remove(msg[0])
                        else: return context.appText("牌数不足！")
                    # 顺子
                    elif re.match(r"^.-.$", last) and re.match(r"^[3-9AHJQK]-[3-9AHJQK]$", msg):
                        start, end = CARDS.index(msg[0]), CARDS.index(msg[-1])
                        lstart, lend = CARDS.index(last[0]), CARDS.index(last[-1])
                        if (end-start) != (lend-lstart): return context.appText("牌数不符！")
                        elif lstart >= start: return context.appText(f"你的牌没有{last}大！")
                        for i in CARDS[start:end+1]:
                            if not i in senderCards:
                                return context.appText("拥有的牌不够！")
                        for i in CARDS[start:end+1]:
                            senderCards.remove(i)
                    # 三带一、三带二
                    elif re.match(r"^.\*3 .{1,2}$", last) and re.match(r"^[2-9AHJQK]\*3 [2-9AHJQK大小]{1,2}$", msg):
                        mult = len(msg.split()[1])
                        if msg[-1] != msg[0]:
                            condition = senderCards.count(msg[0])>=int(msg[2]) and senderCards.count(msg[-1])>=mult
                        # 不会真有人出6*3 6这种的吧
                        else:
                            condition = senderCards.count(msg[0])>=(int(msg[2])+mult)
                        if not condition: return context.appText("牌数不足！")
                        elif SORT.index(last[0]) >= SORT.index(msg[0]): return context.appText(f"你的牌没有{last}大！")
                        elif len(msg.split()[1]) != len(last.split()[1]) or SORT.index(msg[0]) <= SORT.index(last[0]): return context.appText("牌型不符合！")
                        for i in range(int(msg[2])): senderCards.remove(msg[0])
                        for i in range(mult): senderCards.remove(msg[-1])
                    # 双顺、三顺
                    elif re.match(r".-.\*.$", last) and re.match(rf"^[3-9AHJQK]-[3-9AHJQK]\*{last[-1]}$", msg):
                        start, end, mult = CARDS.index(msg[0]), CARDS.index(msg[2]), int(msg[-1])
                        lstart, lend = CARDS.index(last[0]), CARDS.index(last[2])
                        if (end-start) != (lend-lstart): return context.appText("牌数不符！")
                        elif lstart >= start: return context.appText(f"你的牌没有{last}大！")
                        for i in CARDS[start:end+1]:
                            if senderCards.count(i) < mult:
                                return context.appText("拥有的牌不够！")
                        for i in CARDS[start:end+1]:
                            for _ in range(mult): senderCards.remove(i)
                    # 四带二
                    elif re.match(r".\*4 .*", last) and re.match(r"([2-9AHJQK])\*4 (?!.*?\1)(?:([2-9AHJQK])\2 ([2-9AHJQK])\3|[2-9AHJQK大小] [2-9AHJQK大小])$", msg):
                        array = msg.split()[1:]
                        larray = last.split()[1:]
                        if senderCards.count(msg[0])==4 and senderCards.count(array[0])>=len(array[0]) and senderCards.count(array[1])>=len(array[1]):
                            if len(larray[-1]) != len(array[-1]): return context.appText("牌型不符！")
                            elif SORT.index(last[0]) >= SORT.index(msg[0]): return context.appText(f"你的牌没有{last}大！")
                            for _ in range(4): senderCards.remove(msg[0])
                            for i in "".join(array): senderCards.remove(i)
                        else: return context.appText("牌不够，;;;")
                    # 飞机
                    elif re.match(r"^.-.\*3 $", last[:6]) and re.match(r"^[3-9AHJQK]-[3-9AHJQK]\*3 $", msg[:6]):
                        start, end = CARDS.index(msg[0]), CARDS.index(msg[2])
                        lstart, lend = CARDS.index(last[0]), CARDS.index(last[2])
                        if (end-start) != (lend-lstart): return context.appText("牌数不符！")
                        elif SORT.index(last[0]) >= SORT.index(msg[0]): return context.appText(f"你的牌没有{last}大！")
                        else:
                            array = msg[6:].split(" ")
                            if sameLen(array) and len(array) == (end-start+1):
                                for i in CARDS[start:end+1]:
                                    if senderCards.count(i) < 3: return context.appText("牌数不足;;;;")
                                    if i in array: return context.appText("别搞")
                                for i in array:
                                    if senderCards.count(i[0]) < len(i): return context.appText("牌数不足;;;;")
                                for i in CARDS[start:end+1]:
                                    for _ in range(3): senderCards.remove(i)
                                for i in "".join(array):
                                    senderCards.remove(i)
                            else: return context.appText("不符合规则！")
                    # 炸弹
                    elif re.match(r"^[2-9AHJQK]\*4$", msg) and last != "王炸":
                        if senderCards.count(msg[0])<4: return context.appText("牌数不足！")
                        else:
                            if re.match(r"^.*4$", last) and SORT.index(int(last[0])) >= SORT.index(int(msg[0])):
                                return context.appText(f"你的牌没有{last}大!")
                            for _ in range(4): senderCards.remove(msg[0])
                    # 6
                    elif msg == "王炸":
                        if not ("大" in senderCards and "小" in senderCards): return context.appText("牌数不足！")
                        else:
                            senderCards.remove("大")
                            senderCards.remove("小")
                    else: return context.appText(f"牌型不符或牌数不足，上家的牌是{pokers[10]}。请查看规则后重试;")

                pokers[10] = msg
                pokers[9] = pokers[2]
                pokers[2] = (pokers[2]+1)%3
                if not senderCards:
                    if sender == pokers[5]:
                        winner = sender
                    else:
                        pokers[7].remove(pokers[5])
                        winner = " @".join(pokers[7])
                    context.appText(f"@{winner} 获胜！")
                    return endPoker()
                else:
                    context.appText(f"{sender}出了{msg}，轮到@{pokers[7][pokers[2]]} 。")
                    if len(senderCards) < 4:
                        context.appText(f"{sender}只剩{len(senderCards)}张牌了！")
    elif msg == "加入":
        if pokers[0]:
            context.appText("这局已经开始了，等下局吧(￣▽￣)")
        elif sender in pokers[1]:
            context.appText("你已经加入过了，再找些人吧ヾ|≧_≦|〃")
        else:
            pokers[1][sender] = []
            if len(pokers[1]) == 3:
                # 开始
                pokers[0] = True
                pokers[7] = list(pokers[1].keys())
                pokers[3] = PINIT[:]
                # 选底牌
                for i in range(3):
                    index = random.randrange(0, len(pokers[3]))
                    pokers[4].append(pokers[3].pop(index))
                # 洗牌
                random.shuffle(pokers[3])
                # 发牌
                for i, v in enumerate(pokers[3]):
                    pokers[1][pokers[7][i%3]].append(v)
                # 整理牌、告诉牌
                for k, v in pokers[1].items():
                    v.sort(key=lambda x: SORT.index(x))
                    cards = " ".join(v)
                    context.appText(f"以下是您的牌：{cards}", "whisper", to=k)
                own = random.choice(pokers[7])
                pokers[2] = pokers[7].index(own)
                pokers[9] = pokers[2]
                context.appText(f"好的，发牌完成，随机到@{own} 拥有地主牌{random.choice(pokers[1][own])}，请发送`p <分数>`叫地主或`p 0`选择不叫。")
                pokers[6] = True
            else:
                context.appText("加入成功！")
    elif msg == "退出" and sender in pokers[1]:
        if msg[-1] == "t":
            del pokers[1][sender]
            context.appText("已成功退出(‾◡◝)")

# class AutoBot:
#     def __init__(self, nick: str, cards: list):
#         self.nick = nick
#         self.cards = cards
#         self.landlord = False # 原来是这个词
        
#         self.cards.sort(key=lambda x: SORT.index(x))

#     def getCardType(self) -> dict:
#         setCards = set(self.cards)
#         allType = {
#             1: [],
#             2: [],
#             3: [],
#             4: [],
#             "st": self.getStraights(setCards, 5)
#         }
        
#         for card in setCards:
#             allType[self.cards.count(card)].append(card)

#         allType["2st"] = self.getStraights(allType[2], 3)
#         allType["3st"] = self.getStraights(allType[3], 2)
#         if "大" == self.cards[-1] and "小" == self.cards[-2]:
#             allType["王炸"] = True
#         else:
#             allType["王炸"] = False

#         return allType
    
#     def getStraights(self, cards, min_len: int) -> dict:
#         result = {}
#         valids = [SORT.index(i) for i in cards if i not in "2小大"]
        
#         if len(valids) < min_len:
#             return result
        
#         start = 0
#         for i in range(1, len(valids)):
#             if valids[i] != valids[i-1] + 1:
#                 length = len(valids[start:i])
#                 if length >= min_len:
#                     result[start] = length
#                 start = i
#         if len(valids) - start >= min_len:
#             result[start] = len(valids) - start

#         return result

#     def play(self) -> str:
#         if pokers[6]:
#             text = "0"
#         else:
#             types = self.getCardType()
#             if pokers[10] is None:
#                 pass
#             else:
#                 pass
        
#         return "p " + text