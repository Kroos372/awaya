import random, re
from static import bank, Context

CARDS = ["3", "4", "5", "6", "7", "8", "9", "H", "J", "Q", "K", "A", "2"]
JOKERS = ["小", "大"]
SORT = CARDS + JOKERS
PINIT = CARDS*4 + JOKERS

POKERMENU = "\n".join([
    "斗地主...",
    "p 加入: 开始或加入一场斗地主，满三人后自动开始。",
    "p bot: 增加机器人(很傻)",
    "p 退出: 在开始之前退出对局。",
    "p <牌>: 出牌，具体规则请查看出牌规则。",
    "p 结束: 在对局中结束游戏。",
    "p 规则: 获取扑克的出牌规则。",
])
POKERRULE = "\n".join([
    "游戏规则请自行参考[此处](https://baike.baidu.com/item/%E4%B8%89%E4%BA%BA%E6%96%97%E5%9C%B0%E4%B8%BB/9429860)(<-是个链接)，要注意的是这里用==H==代表==10==，==小==代表小王，==大==代表大王。以下是出牌规则：",
    "使用==p 牌==出牌，例如==p 1==, ==p J==，大小写均可；",
    "使用==p .==跳过回合、==p check==查看自己目前的牌、==p all==查看所有玩家的牌",
    "多张相同面值的牌间使用==牌*张数==，例如==p 3*2==，==p 4*3==；",
    "顺子使用==最小牌-最大牌==，例如==p 4-8==，==p 6-A==；",
    "双顺或三顺使用==最小-最大*张数==，例如==p 3-5*2==，==p 4-5*3==；",
    "三带二、飞机等带的对子中不使用==*==，例如==p K*3 77==，==p 8-9*3 33 44==",
    "王炸直接发送==p 王炸==即可；",
    "剩余的就将这两种组合，不同组别用空格隔开即可，例如==p 4-5*3 7 9== ==p 7*4 99 HH==……",
    "玩得开心~"
])

# 带多的带的是否为同长度(对或单)
def sameLen(seq) -> bool:
    try:
        length = len(seq[0])
        for i in seq[1:]:
            if len(i) != length or len(set(i))!=1 or not seq[0][0] in SORT:
                return False
        return True
    except:
        return False

class Player:
    def __init__(self, name: str, trip: str):
        self.trip = trip
        self.name = name
        self.cards = []
        self.nakedCards = False
        self.isbot = False
        self.landlord = False
    def formatCards(self) -> str:
        return " ".join(self.cards)

class AutoBot:
    def __init__(self, name: str):
        self.name = name
        self.cards = []
        self.landlord = False # 原来是这个词
        self.isbot = True

    def getCardType(self) -> dict:
        setCards = set(self.cards)
        allType = {
            1: [],
            2: [],
            3: [],
            4: [],
            "st": self.getStraights(setCards, 5)
        }
        
        for card in setCards:
            allType[self.cards.count(card)].append(card)
        for i in range(1, 5):
            allType[i].sort(key=lambda x: SORT.index(x))

        allType["2st"] = self.getStraights(allType[2], 3)
        allType["3st"] = self.getStraights(allType[3], 2)
        if "大" in self.cards and "小" in self.cards:
            allType["王炸"] = True
        else:
            allType["王炸"] = False

        return allType
    
    def getStraights(self, cards, min_len: int) -> dict:
        result = []
        valids = [SORT.index(i) for i in cards if i not in "2小大"]
        valids.sort()
        
        if len(valids) < min_len:
            return result
        
        start = 0
        for i in range(1, len(valids)):
            if valids[i] != valids[i-1] + 1:
                length = len(valids[start:i])
                if length >= min_len:
                    result.append([valids[start], length])
                start = i
        if len(valids) - start >= min_len:
            result.append([valids[start], len(valids) - start])

        return result
    
    def goStraight(self, start: int, length: int) -> bool:
        for _ in range(length):
            card = SORT[start]
            if self.cards.count(card) >= 3:
                return False
            start += 1
        return True

    def play(self) -> str:
        if poker.status == 1:
            text = "."
        else:
            types = self.getCardType()
            last = poker.lastCard
            # 本轮第一发
            if last is None:
                if types["3st"]:
                    start, length = types["3st"].pop(0)
                    end = SORT[start + length - 1]
                    start = SORT[start]
                    if len(types[1]) >= length:
                        withs = " ".join(str(types[1].pop(0)) for _ in range(length))
                        text = f"{start}-{end}*3 {withs}"
                    elif len(types[2]) >= length:
                        withs = " ".join(str(types[2].pop(0))*2 for _ in range(length))
                        text = f"{start}-{end}*3 {withs}"
                    else:
                        text = f"{start}-{end}*3"
                elif types[3]:
                    three = types[3].pop(0)
                    if types[1]:
                        text = f"{three}*3 {types[1].pop(0)}"
                    elif types[2]:
                        text = f"{three}*3 {str(types[2].pop(0))*2}"
                
                elif types["2st"]:
                    start, length = types["2st"].pop(0)
                    end = SORT[start + length - 1]
                    start = SORT[start]
                    text = f"{start}-{end}*2"
                elif types["st"]:
                    start, length = types["st"].pop(0)
                    text = f"{SORT[start]}-{SORT[start + length - 1]}"

                elif types[1]:
                    text = f"{types[1].pop(0)}"
                elif types[2]:
                    text = f"{types[2].pop(0)}*2"
                else:
                    if len(types[1]) >= 2:
                        withs = " ".join(str(types[1].pop(0)) for _ in range(2))
                        text = f"{types[4].pop(0)}*4 {withs}"
                    elif len(types[2]) >= 2:
                        withs = " ".join(str(types[2].pop(0))*2 for _ in range(2))
                        text = f"{types[4].pop(0)}*4 {withs}"
                    else:
                        text = f"{types[4].pop(0)}*4"
            # 接别人的牌
            elif last == "王炸":
                text = "."
            else:
                text = ""
                lindex = SORT.index(last[0])
                isFriend = not (self.landlord or poker.lastPlayer == poker.landlord)
                
                # 别太坑队友
                if isFriend and lindex > 10:
                    text = "."
                # 单张两张三张四张
                elif last in SORT or re.match(r"^.\*.$", last):
                    try:
                        times = int(last[2])
                    except:
                        times = 1
                    if times != 4 or not isFriend:
                        for card in types[times]:
                            if SORT.index(card) > lindex:
                                if times == 1:
                                    text = card
                                else:
                                    text = f"{card}*{times}"
                                break
                # 顺子双顺三顺
                elif re.match(r"^.-.$", last) or re.match(r"^.-.\*.$", last):
                    try:
                        times = int(last[4])
                    except:
                        times = 1
                    if times == 1:
                        sts = types["st"]
                    elif times == 2:
                        sts = types["2st"]
                    else:
                        sts = types["3st"]
                    lend = SORT.index(last[2])
                    llength = lend - lindex + 1
                    for start, length in sts:
                        if length >= llength:
                            rend = start + length - 1
                            rstart = rend - llength + 1
                            if rstart > lindex:
                                if times == 1:
                                    text = f"{SORT[rstart]}-{SORT[rend]}"
                                else:
                                    text = f"{SORT[rstart]}-{SORT[rend]}*{times}"
                                break
                # 三带一、三带对
                elif re.match(r"^.\*3 .{1,2}$", last):
                    length = len(last.split(" ")[1])
                    for card in types[3]:
                        if SORT.index(card) > lindex and types[length]:
                            text = f"{card}*3 {types[length].pop(0)*length}"
                # 四带二
                elif re.match(r".\*4 .*", last) and not isFriend:
                    length = len(last.split(" ")[1])
                    for card in types[4]:
                        if SORT.index(card) > lindex and len(types[length]) >= 2:
                            text = f"{card}*4 {types[length].pop(0)*length} {types[length].pop(0)*length}"
                # 飞机
                elif re.match(r"^.-.\*3 $", last[:6]) and not isFriend:
                    lend = SORT.index(last[2])
                    llength = lend - lindex + 1
                    withlength = len(last.split(" ")[1])
                    for start, length in types["3st"]:
                        if length >= llength:
                            rend = start + length - 1
                            if SORT[rend - llength + 1] > lindex and len(types[withlength]) >= llength:
                                withs = types[withlength].pop(0)*withlength
                                for _ in range(llength-1):
                                    withs += f" {types[withlength].pop(0)*withlength}"
                                text = f"{SORT[start]}-{SORT[rend]}*{times} {withs}"
                
                
                if not text:
                    kodan = random.random()
                    if types[4] and kodan < 0.2 and not re.match(r"^.\*4$", last):
                        text = f"{types[4].pop(0)}*4"
                    elif types["王炸"] and kodan < 0.2:
                        text = "王炸"
        return text or "."

class Poker:
    def __init__(self):
        self.context: Context = None
        self.initPoker()
    def initPoker(self):
        self.status = 0
        self.playerObjs: dict[str, Player | AutoBot] = {}
        self.players: list[str] = []
        self.cards = PINIT[:]
        self.landlord = ""
        self.basePoint = random.randint(20, 60)
        self.mults = 0
        self.moneyless = []
        
        self.spring = True
        self.gnirps = True # 反春
        self.playerIndex = 0
        self.firstPlayer = 0
        self.lastPlayer = ""
        self.lastCard = None
    def allCards(self) -> str:
        result = ["玩家手牌:"]
        for player in self.playerObjs.values():
            if player.nakedCards:
                result.append(f"{player.name}(明牌)：{player.formatCards()}")
            else:
                result.append(f"{player.name}：{len(player.cards)}张")
        return "\n".join(result)
    def landonwer(self, owner: str): 
        senderObj: Player | AutoBot = self.playerObjs[owner]
        self.landlord = owner
        self.status = 2
        self.firstPlayer = self.playerIndex
        self.playerIndex = self.players.index(self.landlord)
        senderObj.cards += self.cards
        senderObj.cards.sort(key=lambda x: SORT.index(x))
        senderObj.landlord = True
        self.context.appText(f"{' '.join(self.cards)}是底牌，{owner}是地主。底分{self.basePoint}豆，基础倍数{self.mults}倍。")
        self.context.appText(f"游戏开始，地主@{owner} 可发送==p 明==明牌或直接出牌\n发送==p 规则==可以查看出牌规则哦；")
        if not senderObj.isbot:
            self.context.appText(f"以下是您的牌：{senderObj.formatCards()}", "whisper", to=owner)
    def passLand(self):
        self.playerIndex = (self.playerIndex+1) % 3
        if self.playerIndex == self.firstPlayer:
            self.mults = 1
            self.landonwer(self.players[self.playerIndex])
    def start(self):
        # 开始
        self.status = 1
        self.players = list(self.playerObjs.keys())
        # 洗牌
        random.shuffle(self.cards)
        # 发牌
        for i in range(len(self.cards)):
            self.playerObjs[self.players[i%3]].cards.append(self.cards.pop())
            if i == 50:
                break
        # 整理牌、告诉牌
        for player in self.playerObjs.values():
            player.cards.sort(key=lambda x: SORT.index(x))
            if not player.isbot:
                self.context.appText(f"以下是您的牌：{player.formatCards()}", "whisper", to=player.name)
        own = random.choice(self.players)
        self.playerIndex = self.players.index(own)
        self.firstPlayer = self.playerIndex
        self.context.appText(f"好的，发牌完成，随机到@{own} 拥有地主牌{random.choice(self.playerObjs[own].cards)}，请发送`p <分数>`叫地主或`p .`选择不叫。")
        if self.playerObjs[own].isbot:
            self.play(own, "0")
    def play(self, sender: str, msg: str):
        msg = msg.upper()
        senderObj: Player | AutoBot = self.playerObjs[sender]
        # 叫牌阶段
        if self.status == 1:
            if msg[0] == ".":
                self.passLand()
                if self.status == 1:
                    self.context.appText(f"{sender}不叫，轮到@{self.players[self.playerIndex]} ")
            elif msg[0] in ["1", "2", "3"]:
                point = int(msg[0])
                if point == 3:
                    self.mults = point
                    self.landonwer(sender)
                else:
                    if self.mults >= point:
                        self.context.appText("叫的数字必须比前面的大！")
                    else:
                        self.mults = point
                        self.firstPlayer = self.playerIndex
                        self.passLand()
                        if not self.landlord:
                            self.context.appText(f"{sender}叫出了{point}点，轮到@{self.players[self.playerIndex]} ")
            else: 
                self.context.appText("命令错误，请先叫分")
        # 出牌阶段
        else:
            # 跳过
            if msg == ".":
                if self.lastCard is None:
                    self.context.appText("由你开始的啦，随便出一张吧。")
                else:
                    self.playerIndex = (self.playerIndex+1)%3
                    if self.playerIndex == self.firstPlayer:
                        self.lastCard = None
                        self.context.appText(f"所有玩家都要不起，@{self.players[self.playerIndex]} 继续出牌。")
                    else:
                        self.context.appText(f"{sender}跳过，轮到@{self.players[self.playerIndex]} 。")
            elif msg == "明" and self.status == 2:
                if senderObj.nakedCards:
                    self.context.appText("你已经明牌了！")
                else:
                    senderObj.nakedCards = True
                    self.mults *= 2
                    self.context.appText(f"{sender}明牌！倍数翻倍，当前{self.mults}倍。以下是{sender}的牌:\n{senderObj.formatCards()}")
            else:
                senderCards = senderObj.cards
                mults = 0
                # 本轮第一发
                if self.lastCard is None:
                    # 单张
                    if msg in SORT and msg in senderCards:
                        senderCards.remove(msg)
                    # 对子或三张或四张
                    elif re.match(r"^[2-9AHJQK]\*[234]$", msg):
                        if senderCards.count(msg[0])>=int(msg[-1]):
                            for _ in range(int(msg[-1])): senderCards.remove(msg[0])
                        else: return self.context.appText("牌数不足！")
                    # 顺子
                    elif re.match(r"^[3-9AHJQK]-[3-9AHJQK]$", msg):
                        start, end = CARDS.index(msg[0]), CARDS.index(msg[-1])
                        if (end-start) >= 4:
                            for i in CARDS[start:end+1]:
                                if not i in senderCards:
                                    return self.context.appText("拥有的牌不够！")
                            for i in CARDS[start:end+1]:
                                senderCards.remove(i)
                        else: return self.context.appText("顺子最少五个！")
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
                        else: return self.context.appText("牌数不足！")
                    # 双顺、三顺
                    elif re.match(r"^[3-9AHJQK]-[3-9AHJQK]\*[23]$", msg):
                        start, end, mult = CARDS.index(msg[0]), CARDS.index(msg[2]), int(msg[-1])
                        if (end-start) >= (4-mult):
                            for i in CARDS[start:end+1]:
                                if senderCards.count(i) < mult:
                                    return self.context.appText("拥有的牌不够！")
                            for i in CARDS[start:end+1]:
                                for _ in range(mult): senderCards.remove(i)
                        else: return self.context.appText("牌数不够，三顺最少两个，双顺最少三个;")
                    # 四带二
                    elif re.match(r"([2-9AHJQK])\*4 (?!.*?\1)(?:([2-9AHJQK])\2 ([2-9AHJQK])\3|[2-9AHJQK大小] [2-9AHJQK大小])$", msg):
                        array = msg.split()[1:]
                        if senderCards.count(msg[0])==4 and sameLen(array) and senderCards.count(array[0][0])>=len(array[0][0]) and senderCards.count(array[1][0])>=len(array[1][0]):
                            for _ in range(4):
                                senderCards.remove(msg[0])
                            for i in "".join(array):
                                senderCards.remove(i)
                        else: return self.context.appText("牌不够，;;;")
                    # 飞机
                    elif re.match(r"^[3-9AHJQK]-[3-9AHJQK]\*3 $", msg[:6]):
                        start, end = CARDS.index(msg[0]), CARDS.index(msg[2])
                        if (end-start) < 1: return self.context.appText("牌数不够;")
                        else:
                            array = msg[6:].split(" ")
                            if sameLen(array) and len(array) == (end-start+1):
                                for i in CARDS[start:end+1]:
                                    if senderCards.count(i) < 3: return self.context.appText("牌数不足;;;;")
                                    if i in array or i+i in array: return self.context.appText("别搞")
                                for i in array:
                                    if senderCards.count(i[0]) < len(i):
                                        return self.context.appText("牌数不足;;;;")
                                for i in CARDS[start:end+1]:
                                    for _ in range(3): senderCards.remove(i)
                                for i in "".join(array):
                                    senderCards.remove(i)
                            else: return self.context.appText("不符合规则！")
                    # 炸弹
                    elif re.match(r"^[2-9AHJQK]\*4$", msg):
                        if senderCards.count(msg[0])<4:
                            return self.context.appText("牌数不足！")
                        for _ in range(4):
                            senderCards.remove(msg[0])
                        mults = 2
                    # 6
                    elif msg == "王炸":
                        if not ("大" in senderCards and "小" in senderCards): return self.context.appText("牌数不足！")
                        else:
                            senderCards.remove("大")
                            senderCards.remove("小")
                            mults = 2
                    else: return self.context.appText("命令不正确或牌数不足，请查看规则后重试;")
                else:
                    last = self.lastCard
                    # 单张
                    if last in SORT and msg in SORT and msg in senderCards:
                        if SORT.index(msg) <= SORT.index(last):
                            return self.context.appText(f"你的牌没有{last}大！")
                        senderCards.remove(msg)
                    # 对子或三张或四张
                    elif re.match(r"^.\*.$", last) and re.match(rf"^[2-9AHJQK]\*{last[-1]}$", msg):
                        if senderCards.count(msg[0])>=int(msg[-1]):
                            if SORT.index(msg[0]) <= SORT.index(last[0]): return self.context.appText(f"你的牌没有{last}大！")
                            for _ in range(int(msg[-1])): senderCards.remove(msg[0])
                        else: return self.context.appText("牌数不足！")
                    # 顺子
                    elif re.match(r"^.-.$", last) and re.match(r"^[3-9AHJQK]-[3-9AHJQK]$", msg):
                        start, end = CARDS.index(msg[0]), CARDS.index(msg[-1])
                        lstart, lend = CARDS.index(last[0]), CARDS.index(last[-1])
                        if (end-start) != (lend-lstart): return self.context.appText("牌数不符！")
                        elif lstart >= start: return self.context.appText(f"你的牌没有{last}大！")
                        for i in CARDS[start:end+1]:
                            if not i in senderCards:
                                return self.context.appText("拥有的牌不够！")
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
                        if not condition: return self.context.appText("牌数不足！")
                        elif SORT.index(last[0]) >= SORT.index(msg[0]): return self.context.appText(f"你的牌没有{last}大！")
                        elif len(msg.split()[1]) != len(last.split()[1]) or SORT.index(msg[0]) <= SORT.index(last[0]): return self.context.appText("牌型不符合！")
                        for i in range(int(msg[2])): senderCards.remove(msg[0])
                        for i in range(mult): senderCards.remove(msg[-1])
                    # 双顺、三顺
                    elif re.match(r".-.\*.$", last) and re.match(rf"^[3-9AHJQK]-[3-9AHJQK]\*{last[-1]}$", msg):
                        start, end, mult = CARDS.index(msg[0]), CARDS.index(msg[2]), int(msg[-1])
                        lstart, lend = CARDS.index(last[0]), CARDS.index(last[2])
                        if (end-start) != (lend-lstart): return self.context.appText("牌数不符！")
                        elif lstart >= start: return self.context.appText(f"你的牌没有{last}大！")
                        for i in CARDS[start:end+1]:
                            if senderCards.count(i) < mult:
                                return self.context.appText("拥有的牌不够！")
                        for i in CARDS[start:end+1]:
                            for _ in range(mult): senderCards.remove(i)
                    # 四带二
                    elif re.match(r".\*4 .*", last) and re.match(r"([2-9AHJQK])\*4 (?!.*?\1)(?:([2-9AHJQK])\2 ([2-9AHJQK])\3|[2-9AHJQK大小] [2-9AHJQK大小])$", msg):
                        array = msg.split()[1:]
                        larray = last.split()[1:]
                        if senderCards.count(msg[0])==4 and sameLen(array) and senderCards.count(array[0][0])>=len(array[0][0]) and senderCards.count(array[1][0])>=len(array[1][0]):
                            if len(larray[-1]) != len(array[-1]): return self.context.appText("牌型不符！")
                            elif SORT.index(last[0]) >= SORT.index(msg[0]): return self.context.appText(f"你的牌没有{last}大！")
                            for _ in range(4): senderCards.remove(msg[0])
                            for i in "".join(array): senderCards.remove(i)
                        else: return self.context.appText("牌不够，;;;")
                    # 飞机
                    elif re.match(r"^.-.\*3 $", last[:6]) and re.match(r"^[3-9AHJQK]-[3-9AHJQK]\*3 $", msg[:6]):
                        start, end = CARDS.index(msg[0]), CARDS.index(msg[2])
                        lstart, lend = CARDS.index(last[0]), CARDS.index(last[2])
                        if (end-start) != (lend-lstart): return self.context.appText("牌数不符！")
                        elif SORT.index(last[0]) >= SORT.index(msg[0]): return self.context.appText(f"你的牌没有{last}大！")
                        else:
                            array = msg[6:].split(" ")
                            if sameLen(array) and len(array) == (end-start+1):
                                for i in CARDS[start:end+1]:
                                    if senderCards.count(i) < 3: return self.context.appText("牌数不足;;;;")
                                    if i in array: return self.context.appText("别搞")
                                for i in array:
                                    if senderCards.count(i[0]) < len(i): return self.context.appText("牌数不足;;;;")
                                for i in CARDS[start:end+1]:
                                    for _ in range(3): senderCards.remove(i)
                                for i in "".join(array):
                                    senderCards.remove(i)
                            else: return self.context.appText("不符合规则！")
                    # 炸弹
                    elif re.match(r"^[2-9AHJQK]\*4$", msg) and last != "王炸":
                        if senderCards.count(msg[0])<4: return self.context.appText("牌数不足！")
                        else:
                            if re.match(r"^.*4$", last) and SORT.index(int(last[0])) >= SORT.index(int(msg[0])):
                                return self.context.appText(f"你的牌没有{last}大!")
                            for _ in range(4): senderCards.remove(msg[0])
                            mults = 2
                    # 6
                    elif msg == "王炸":
                        if not ("大" in senderCards and "小" in senderCards): return self.context.appText("牌数不足！")
                        else:
                            senderCards.remove("大")
                            senderCards.remove("小")
                            mults = 2
                    else: return self.context.appText(f"牌型不符或牌数不足，上家的牌是{self.lastCard}。请查看规则后重试;")

                self.lastCard = msg
                self.lastPlayer = sender
                self.firstPlayer = self.playerIndex
                self.playerIndex = (self.playerIndex+1) % 3
                
                if self.status == 2:
                    self.status = 3
                elif senderObj.landlord:
                    self.gnirps = False
                else:
                    self.spring = False
                    
                if mults:
                    self.mults *= mults
                    self.context.appText(f"{sender}出了炸，倍数翻倍！当前{self.mults}倍。")
                if not senderCards:
                    self.players.remove(self.landlord)
                    if senderObj.landlord:
                        winner = sender
                    else:
                        winner = " @".join(self.players)
                    self.context.appText(f"@{winner} 获胜！")

                    if self.spring:
                        self.mults *= 2
                        self.context.appText("春天！倍数翻倍！")
                    elif self.gnirps:
                        self.mults *= 2
                        self.context.appText("反春天！倍数翻倍！")
                    
                    baseMoney = self.basePoint * self.mults
                    if not self.moneyless:
                        if senderObj.landlord:
                            for nick in self.players:
                                thisMoney = bank.delete(self.playerObjs[nick].trip, baseMoney)
                                bank.add(senderObj.trip, thisMoney)
                                self.context.appText(f"{nick}输给了{sender} **{thisMoney}**阿瓦豆。")
                        else:
                            thisMoney = bank.delete(self.playerObjs[self.landlord].trip, baseMoney * 2)
                            for nick in self.players:
                                bank.add(self.playerObjs[nick].trip, thisMoney / 2)
                                self.context.appText(f"{self.landlord}输给了{nick} **{thisMoney}**阿瓦豆。")
                    else:
                        self.context.appText(f"共计{self.mults}倍。")
                    
                    return self.initPoker()
                else:
                    msg = msg.replace("*", "\\*")
                    self.context.appText(f"{sender}出了{msg}，轮到@{self.players[self.playerIndex]} 。")
                    if len(senderCards) < 4:
                        self.context.appText(f"{sender}只剩{len(senderCards)}张牌了！")

        nextObj: Player | AutoBot = self.playerObjs[self.players[self.playerIndex]]
        if nextObj.isbot:
            botCard = nextObj.play()
            # self.context.appText(f"{nextObj.name} 出了 {botCard}".replace("*", "\\*"))
            self.play(nextObj.name, botCard)

def main(context: Context, sender: str, msg: str, trip: str="", bot: bool=False):
    poker.context = context
    if msg == "规则":
        context.appText(POKERRULE)
    elif msg == "help":
        context.appText(POKERMENU)
    elif msg == "结束" and sender in poker.players:
        poker.initPoker()
        context.appText("唔，结束了;;;;")
    elif msg == "check" and (sender in poker.players) and (poker.status == 3):
        context.appText(f"地主是{poker.landlord}, 上家出的牌是：{poker.lastCard}\n以下是您的牌：{poker.playerObjs[sender].formatCards()}", "whisper")
    elif msg == "all" and (sender in poker.players) and (poker.status == 3):
        context.appText(poker.allCards())
    elif poker.status and sender == poker.players[poker.playerIndex]:
        poker.play(sender, msg)
    elif msg == "加入":
        if poker.status:
            context.appText("这局已经开始了，等下局吧(￣▽￣)")
        elif sender in poker.playerObjs:
            context.appText("你已经加入过了，再找些人吧ヾ|≧_≦|〃")
        else:
            if bot or not trip:
                poker.moneyless.append(sender)
                context.appText("(有bot或无识别码玩家加入，本局将不算钱)")
            if bot:
                poker.playerObjs[sender] = AutoBot(sender)
            else:
                poker.playerObjs[sender] = Player(sender, trip)

            if len(poker.playerObjs) == 3:
                poker.start()
            else:
                context.appText("加入成功！")
    elif msg[:3] == "bot":
        addNick = msg[4:] or context.nick
        if poker.status:
            context.appText("这局已经开始了，等下局吧(￣▽￣)")
        elif addNick in poker.playerObjs and poker.playerObjs[addNick].isbot:
            context.appText("BOT!!!!!!!😭")
            main(context, addNick, "退出", bot=True)
        else:
            context.appText("BOT!!!!!!!ヾ|≧_≦|〃")
            main(context, addNick, "加入", bot=True)
    elif msg == "退出" and not poker.status and sender in poker.playerObjs:
            poker.playerObjs.pop(sender)
            context.appText("已成功退出(‾◡◝)")
            if sender in poker.moneyless:
                poker.moneyless.remove(sender)

poker = Poker()