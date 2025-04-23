from static import random, Context

UNOMENU = "\n".join([
    "UNO，代码改写自[Blaze](https://github.com/geGDVS/UNO/)",
    "u 加入: 开始或加入一场uno",
    "u bot: 添加傻傻bot( ﾟ∀。)",
    "u 退出: 在开始之前退出对局。",
    "u 开始: 开始一场uno。",
    "u <牌>: 出牌，具体规则请查看出牌规则。",
    "u 结束: 在对局中结束游戏。",
    "u 规则: 获取出牌规则。",
])
UNORULE = "\n".join([
    "牌先出完者获胜。游戏规则:",
    "一般地，uno牌分为<颜色><名称(多是数字)>两部分(如==绿2==, ==红禁==)，打出的牌需 与上家<颜色>或/和<名称>相同。",
    "对于<名称>部分，存在以下几种具有特殊效果的情况:",
    "1. ==转向==: 出牌顺序逆转(顺时针变逆时针，反之亦然)",
    "2. ==禁==: 使下家跳过一回合",
    "3. ==+2==: 使下家增加2张牌，并跳过一回合。",
    "另外有==变色==, ==+4==两种需要参数的特殊牌:",
    "1. 变色 <颜色>: 指定下家需要出的颜色(无<名称>)",
    "2. +4 <颜色>: 在==变色==的基础上，使下家增加4张牌，并跳过一回合。",
    "#### +4的质疑规则: ",
    "一般地，+4只能在无与当前牌<颜色>相同的牌时出(如当前牌是==蓝1==，手中拥有蓝色牌则不能出+4)。",
    "玩家A出+4时，下家B可以选择质疑A。质疑后该玩家须展示手牌。此时有两种情况:",
    "1. A出牌合规(无与当前牌<颜色>相同的牌): 变色生效，B摸6张，并跳过一回合",
    "2. A出牌不合规(有与当前牌<颜色>相同的牌): 变色生效，A摸4张，B跳过一回合",
    "---",
    "出牌规则:",
    "==u 牌 <参数>==出牌，例如==u 绿2==, ==u 变色 蓝==",
    "==u .==跳过回合, ==u ?!==质疑",
    "==u check==查看自己目前的牌, ==u all==查看所有人牌数",
])

class AutoBot:
    def __init__(self, cards: list):
        self.cards = cards
    def getCardType(self) -> dict:
        types: dict[str, int | list] = {
            "红": [],
            "黄": [],
            "蓝": [],
            "绿": [],

            "+2": [],
            "禁": [],
            "转向": [],

            "+4": 0,
            "变色": 0,
            "?": 0 # ?
        }
        types.update({str(x): [] for x in range(10)})
        for card in self.cards:
            if card in types: # +4 变色
                types[card] += 1
            else:
                types[card[0]].append(card)
                types[card[1:]].append(card)
        
        return types
    def getMaxColor(self, types: dict=None) -> str:
        types = types or self.getCardType()
        color = "红"
        maxinum = len(types["红"])
        for i in "黄蓝绿":
            if len(types[i]) > maxinum:
                maxinum = len(types[i])
                color = i
        return color
    def play(self) -> str:
        if uno.status == 2:
            return "."
        else:
            text = ""
            types = self.getCardType()
            color, number = uno.lastCard[0], uno.lastCard[1:]
            if types[color]:
                text = random.choice(types[color])
            elif types[number]:
                text = random.choice(types[number])
            else:
                if types["+4"]:
                    text = f"+4 {self.getMaxColor(types)}"
                elif types["变色"]:
                    text = f"变色 {self.getMaxColor(types)}"
        return text or "."

class Uno:
    def __init__(self):
        self.context: Context = None
        self.initUno()
    def initUno(self):
        self.status = 0
        self.players = []
        self.playerCards = []
        self.cards = []
        self.nextPlayer = ""
        self.lastCard = ""
        self.waitPlayer = ""
        self.add4Color = ""
        self.botDict: dict[str, AutoBot] = {}
    def initCards(self):
        self.cards = []
        for j in "红黄蓝绿":
            for i in range(1, 10):
                self.cards.append(j + str(i))
                self.cards.append(j + str(i))
            for i in ["+2", "禁", "转向"]:
                self.cards.append(j + i)
                self.cards.append(j + i)
            self.cards.append(j + "0")
        for i in range(4):
            self.cards.append("+4")
            self.cards.append("变色")

    def no_card(self, num):
        if len(self.cards) < num:
            self.cards = self.initCards()
            for i in self.playerCards:
                for j in i:
                    self.cards.remove(j)

    def start_game(self):
        self.status = 1
        self.initCards()
        random.shuffle(self.players)
        for _ in range(len(self.players)):
            playerCard = []
            for _ in range(7):
                addCard = random.choice(self.cards)
                playerCard.append(addCard)
                self.cards.remove(addCard)
            self.playerCards.append(playerCard)
        self.nextPlayer = self.players[0]
        self.lastCard = random.choice(self.cards)
        while self.lastCard[0] not in "红黄蓝绿":
            self.lastCard = random.choice(self.cards)
        self.cards.remove(self.lastCard)
        for i in range(len(self.playerCards)):
            player = self.players[i]
            if player in self.botDict:
                self.botDict[player] = AutoBot(sorted(self.playerCards[i]))
            else:
                self.context.appText(f"这是你的牌：\n{self.formatCards(i)}", "whisper", to=player)
        self.context.appText(f"牌发完啦，初始牌是=={self.lastCard}==，顺序是 {self.formatOrder()}\n请@{self.nextPlayer} 先出！发送==u 规则==可以查看出牌规则哦")
        if self.nextPlayer in self.botDict:
            self.play(self.nextPlayer, self.botDict[self.nextPlayer].play())

    def stop_game(self):
        self.status = 0
        self.players = []
        self.playerCards = []
        self.nextPlayer = ""
        self.lastCard = False

    def add4(self, id_, question=False, num=4):
        if question:
            nextid_ = (id_ + 2) % len(self.players)
        else:
            nextid_ = (id_ + 1) % len(self.players)
        self.nextPlayer = self.players[nextid_]
        self.no_card(4)
        for i in range(num):
            addCard = random.choice(self.cards)
            self.playerCards[id_].append(addCard)
            self.cards.remove(addCard)
        self.status = 1
        self.waitPlayer = ""

    def color(self, color, id_):
        nextid_ = (id_ + 1) % len(self.players)
        self.nextPlayer = self.players[nextid_]
        self.lastCard = color + "?"

    def ban(self, id_):
        next2id_ = (id_ + 2) % len(self.players)
        self.nextPlayer = self.players[next2id_]

    def add2(self, id_):
        nextid_ = (id_ + 1) % len(self.players)
        next2id_ = (id_ + 2) % len(self.players)
        self.nextPlayer = self.players[next2id_]
        self.no_card(2)
        for i in range(2):
            addCard = random.choice(self.cards)
            self.playerCards[nextid_].append(addCard)
            self.cards.remove(addCard)

    def turn(self, id_) -> int:
        self.players.reverse()
        self.playerCards.reverse()
        newNextId = len(self.players) - id_
        self.nextPlayer = self.players[newNextId % len(self.players)]
        return newNextId - 1

    def formatCards(self, id_) -> str:
        cards = self.playerCards[id_]
        cards.sort()
        return "\n" + ", ".join(cards)
    def formatOrder(self) -> str:
        text = []
        for player in self.players:
            if player == self.nextPlayer:
                player = f"=={player}=="
            text.append(player)
        return " -> ".join(text)
    def formatAll(self) -> str:
        text = []
        for i, player in enumerate(self.players):
            if player == self.nextPlayer:
                player = f"=={player}=="
            text.append(f"{player}: {len(self.playerCards[i])}")
        return "当前玩家各自手牌数: \n" + ", ".join(text)
    def play(self, sender: str, msg: str):
        msgList = msg.split()
        if not msgList:
            return
        card, id_ = msgList[0], self.players.index(sender)
        nextid_ = (id_ + 1) % len(self.players)
        if card == "check":
            self.context.appText(f"现在牌面上的牌是=={self.lastCard}==，顺序是 {self.formatOrder()}\n这是你的牌：{self.formatCards(id_)}", "whisper", to=sender)
        elif card == "all":
            self.context.appText(self.formatAll())
        elif uno.status == 1 and sender == self.nextPlayer:
            if card == ".":
                nextid_ = (id_ + 1) % len(self.players)
                addCard = random.choice(self.cards)
                self.cards.remove(addCard)
                if addCard[0] == self.lastCard[0] or addCard[1:] == self.lastCard[1:]:
                    self.lastCard = addCard
                    if addCard[1:] == "禁":
                        self.ban(id_)
                        self.context.appText(f"{sender}补到了=={addCard}==并将其打出，{self.players[nextid_]}跳过1轮，轮到@{self.nextPlayer} ！")
                    elif addCard[1:] == "+2":
                        self.add2(id_)
                        self.context.appText(f"{sender}补到了=={addCard}==并将其打出，{self.players[nextid_]}加2张，轮到@{self.nextPlayer} ！")
                        self.context.appText(f"你新增了2张牌，这是你现在的牌：\n{self.formatCards(nextid_)}。", "whisper", to=self.players[nextid_])
                    elif addCard[1:] == "转向":
                        id_ = self.turn(id_)
                        self.context.appText(f"{sender}补到了=={addCard}==并将其打出，==顺序转换==，轮到@{self.nextPlayer} ！")
                    else:
                        self.nextPlayer = self.players[nextid_]
                        self.context.appText(f"{sender}补到了=={addCard}==并将其打出，轮到@{self.nextPlayer} ！")
                else:
                    self.nextPlayer = self.players[nextid_]
                    self.playerCards[id_].append(addCard)
                    self.context.appText(f"{sender}补了一张牌，轮到@{self.nextPlayer} ！")
                    self.context.appText(f"你新增了1张牌，这是你现在的牌：\n{self.formatCards(id_)}。", "whisper", to=sender)
            elif card not in self.playerCards[id_]:
                self.context.appText("你没有那张牌！")
                
            elif card == "+4":
                if len(msgList) < 2:
                    self.context.appText("缺少参数！")
                elif msgList[1] not in "红黄蓝绿":
                    self.context.appText("参数错误！")
                else:
                    self.add4Color = msgList[1]
                    self.status = 2
                    self.waitPlayer = self.players[nextid_]
                    self.lastCard = self.lastCard[0]
                    self.playerCards[id_].remove(card)
                    self.context.appText(f"{sender}出了+4！@{self.players[nextid_]} 可以发送==u ?!==质疑或==u .==跳过。")
            elif card == "变色":
                if len(msgList) < 2:
                    self.context.appText("缺少参数！")
                elif msgList[1] not in "红黄蓝绿":
                    self.context.appText("参数错误！")
                else:
                    self.color(msgList[1], id_)
                    self.playerCards[id_].remove(card)
                    self.context.appText(f"{sender}出了变色牌，颜色变为=={msgList[1]}==，轮到@{self.nextPlayer} ！")
            elif card[0] == self.lastCard[0] or card[1:] == self.lastCard[1:]:
                self.lastCard = card
                if card[1:] == "禁":
                    self.ban(id_)
                    self.context.appText(f"{sender}出了=={card}==，{self.players[nextid_]}跳过1轮，轮到@{self.nextPlayer} ！")
                elif card[1:] == "+2":
                    self.add2(id_)
                    self.context.appText(f"{sender}出了=={card}==，{self.players[nextid_]}加2张，轮到@{self.nextPlayer} ！")
                    self.context.appText(f"你新增了2张牌，这是你现在的牌：\n{self.formatCards(nextid_)}。", "whisper", to=self.players[nextid_])
                elif card[1:] == "转向":
                    id_ = self.turn(id_)
                    self.context.appText(f"{sender}出了{card}，==顺序转换==，轮到@{self.nextPlayer} ！")
                else:
                    self.nextPlayer = self.players[nextid_]
                    self.context.appText(f"{sender}出了=={card}==，轮到@{self.nextPlayer} ！")
                    self.no_card(1)
                self.playerCards[id_].remove(card)
            elif card not in ["+4", "变色"]:
                return self.context.appText("不符合规则！")
            if len(self.playerCards[id_]) == 1:
                self.context.appText(f"{sender}==UNO==了！！！")
            elif not self.playerCards[id_]:
                self.context.appText(f"{sender}获胜，游戏结束。")
                self.initUno()
        elif sender == self.waitPlayer:
            lastid_ = (id_ - 1) % len(self.players)
            if card == ".":
                self.add4(id_)
                self.context.appText(f"{sender}不质疑，加4张，颜色变为=={self.add4Color}==。轮到@{self.nextPlayer} ！")
                self.context.appText(f"你新增了4张牌，这是你现在的牌：\n{self.formatCards(id_)}。", "whisper", to=self.players[id_])
                self.lastCard = self.add4Color + "?"
            elif card == "?!":
                if any(self.lastCard == i[0] for i in self.playerCards[lastid_]):
                    self.add4(lastid_, True)
                    lastPlayer = self.players[lastid_]
                    self.context.appText(f"{lastPlayer}==有=={self.lastCard}色牌！")
                    self.context.appText(f"{sender}质疑成功！=={lastPlayer}==加4张，颜色变为=={self.add4Color}==。轮到@{self.nextPlayer}！")
                    self.context.appText(f"你新增了4张牌，这是你现在的牌：\n{self.formatCards(id_)}。", "whisper", to=lastPlayer)
                    self.lastCard = self.add4Color + "?"
                else:
                    self.add4(id_, num=6)
                    self.context.appText(f"{self.players[lastid_]}==没有=={self.lastCard}色牌！")
                    self.context.appText(f"{sender}质疑失败，加==6==张，颜色变为=={self.add4Color}==。轮到@{self.nextPlayer} ！")
                    self.context.appText(f"你新增了6张牌，这是你现在的牌：\n{self.formatCards(id_)}。", "whisper", to=self.players[id_])
                    self.lastCard = self.add4Color + "?"
        botNick = self.waitPlayer or self.nextPlayer
        if botNick in self.botDict:
            self.botDict[botNick].cards = self.playerCards[self.players.index(botNick)]
            botCard = self.botDict[botNick].play()
            with open("log.txt", "a+", encoding="utf8") as f:
                f.write(str(self.playerCards))
                f.write(f"{botNick}出了:{botCard}\n")
            # self.context.appText(f"{botNick}出了:{botCard}")
            self.play(botNick, botCard)

def main(context: Context, sender: str, msg: str):
    uno.context = context
    if msg == "加入":
        if uno.status:
            context.appText("游戏已经开始了，等下一轮吧。")
        elif sender in uno.players:
            context.appText("你已经加入了！")
        else:
            uno.players.append(sender)
            context.appText(f"加入成功，现在有{len(uno.players)}人。")
    elif msg == "退出" and sender in uno.players:
        uno.players.remove(sender)
        context.appText("退出成功...")
    elif msg == "开始" and not uno.status:
        if len(uno.players) >= 2:
            uno.start_game()
        else:
            context.appText("人数不够！")
    elif msg == "结束" and uno.status:
        uno.initUno()
        context.appText("结束了...")
    elif msg == "help":
        context.appText(UNOMENU)
    elif msg == "规则":
        context.appText(UNORULE)
    elif msg[:3] == "bot":
        addNick = msg[4:] or context.nick
        if uno.status:
            context.appText("这局已经开始了，等下局吧(￣▽￣)")
        elif addNick in uno.botDict:
            del uno.botDict[addNick]
            context.appText("BOT!!!!!!!😭")
            main(context, addNick, "退出")
        else:
            uno.botDict[addNick] = None
            context.appText("BOT!!!!!!!ヾ|≧_≦|〃")
            main(context, addNick, "加入")
    elif sender in uno.players:
        uno.play(sender, msg)

uno = Uno()