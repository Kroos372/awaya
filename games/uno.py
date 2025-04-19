import random

# [0是否游戏中, 1[玩家列表], 2[各玩家的牌], 3[当前牌堆], 4下一人, 5上一张牌, 6是否等待+4质疑, 7等待质疑者， 8+4要变的色]
unoList = [False, [], [], [], None, None, False, None, None]

UNOMENU = "\n".join([
    "UNO，代码改写自[Blaze](https://github.com/geGDVS/UNO/)",
    "u 加入: 开始或加入一场uno",
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

def initCards():
    unoList[3] = []
    for j in "红黄蓝绿":
        for i in range(1, 10):
            unoList[3].append(j + str(i))
            unoList[3].append(j + str(i))
        for i in ["+2", "禁", "转向"]:
            unoList[3].append(j + i)
            unoList[3].append(j + i)
        unoList[3].append(j + "0")
    for i in range(4):
        unoList[3].append("+4")
        unoList[3].append("变色")

def no_card(num):
    if len(unoList[3]) < num:
        unoList[3] = initCards()
        for i in unoList[2]:
            for j in i:
                unoList[3].remove(j)

def start_game():
    unoList[0] = True
    initCards()
    random.shuffle(unoList[1])
    for _ in range(len(unoList[1])):
        playerCard = []
        for _ in range(7):
            addCard = random.choice(unoList[3])
            playerCard.append(addCard)
            unoList[3].remove(addCard)
        unoList[2].append(playerCard)
    unoList[4] = unoList[1][0]
    unoList[5] = random.choice(unoList[3])
    while unoList[5][0] not in "红黄蓝绿":
        unoList[5] = random.choice(unoList[3])
    unoList[3].remove(unoList[5])

def stop_game():
    unoList[0] = False
    unoList[1] = []
    unoList[2] = []
    unoList[4] = ""
    unoList[5] = False
    unoList[6] = False

def add4(id_, question=False, num=4):
    if question:
        nextid_ = (id_ + 2) % len(unoList[1])
    else:
        nextid_ = (id_ + 1) % len(unoList[1])
    unoList[4] = unoList[1][nextid_]
    no_card(4)
    for i in range(num):
        addCard = random.choice(unoList[3])
        unoList[2][id_].append(addCard)
        unoList[3].remove(addCard)

def color(color, id_):
    nextid_ = (id_ + 1) % len(unoList[1])
    unoList[4] = unoList[1][nextid_]
    unoList[5] = color + "?"

def ban(id_):
    next2id_ = (id_ + 2) % len(unoList[1])
    unoList[4] = unoList[1][next2id_]

def add2(id_):
    nextid_ = (id_ + 1) % len(unoList[1])
    next2id_ = (id_ + 2) % len(unoList[1])
    unoList[4] = unoList[1][next2id_]
    no_card(2)
    for i in range(2):
        addCard = random.choice(unoList[3])
        unoList[2][nextid_].append(addCard)
        unoList[3].remove(addCard)

def turn(id_) -> int:
    unoList[1].reverse()
    unoList[2].reverse()
    newNextId = len(unoList[1]) - id_
    unoList[4] = unoList[1][newNextId % len(unoList[1])]
    return newNextId - 1

def formatCards(id_) -> str:
    cards = unoList[2][id_]
    cards.sort()
    return "\n" + ", ".join(cards)
def formatOrder() -> str:
    text = []
    for player in unoList[1]:
        if player == unoList[4]:
            player = f"=={player}=="
        text.append(player)
    return " -> ".join(text)
def formatAll() -> str:
    text = []
    for i, player in enumerate(unoList[1]):
        if player == unoList[4]:
            player = f"=={player}=="
        text.append(f"{player}: {len(unoList[2][i])}")
    return "当前玩家各自手牌数: \n" + ", ".join(text)

def main(context, sender, msg):
    if msg == "加入":
        if unoList[0]:
            context.appText("游戏已经开始了，等下一轮吧。")
        elif sender in unoList[1]:
            context.appText("你已经加入了！")
        else:
            unoList[1].append(sender)
            context.appText(f"加入成功，现在有{len(unoList[1])}人。")
    elif msg == "退出" and sender in unoList[1]:
        unoList[1].remove(sender)
        context.appText("退出成功...")
    elif msg == "开始" and not unoList[0]:
        if len(unoList[1]) >= 2:
            start_game()
            for i in range(len(unoList[2])):
                context.appText(f"这是你的牌：\n{formatCards(i)}", "whisper", to=unoList[1][i])
            context.appText(f"牌发完啦，初始牌是=={unoList[5]}==，顺序是 {formatOrder()}\n请@{unoList[4]} 先出！发送==u 规则==可以查看出牌规则哦")
        else:
            context.appText("人数不够！")
    elif msg == "结束" and unoList[0]:
        stop_game()
        context.appText("结束了...")
    elif msg == "help":
        context.appText(UNOMENU)
    elif msg == "规则":
        context.appText(UNORULE)
    elif sender in unoList[1]:
        msgList = msg.split()
        if not msgList:
            return
        card, id_ = msgList[0], unoList[1].index(sender)
        nextid_ = (id_ + 1) % len(unoList[1])
        if card == "check":
            context.appText(f"现在牌面上的牌是=={unoList[5]}==，顺序是 {formatOrder()}\n这是你的牌：{formatCards(id_)}", "whisper", to=sender)
        elif card == "all":
            context.appText(formatAll())
        elif not unoList[6] and sender == unoList[4]:
            if card == ".":
                nextid_ = (id_ + 1) % len(unoList[1])
                addCard = random.choice(unoList[3])
                unoList[3].remove(addCard)
                if addCard[0] == unoList[5][0] or addCard[1:] == unoList[5][1:]:
                    unoList[5] = addCard
                    if addCard[1:] == "禁":
                        ban(id_)
                        context.appText(f"{sender}补到了=={addCard}==并将其打出，{unoList[1][nextid_]}跳过1轮，轮到@{unoList[4]} ！")
                    elif addCard[1:] == "+2":
                        add2(id_)
                        context.appText(f"{sender}补到了=={addCard}==并将其打出，{unoList[1][nextid_]}加2张，轮到@{unoList[4]} ！")
                        context.appText(f"你新增了2张牌，这是你现在的牌：\n{formatCards(nextid_)}。", "whisper", to=unoList[1][nextid_])
                    elif addCard[1:] == "转向":
                        id_ = turn(id_)
                        context.appText(f"{sender}补到了=={addCard}==并将其打出，==顺序转换==，轮到@{unoList[4]} ！")
                    else:
                        unoList[4] = unoList[1][nextid_]
                        context.appText(f"{sender}补到了=={addCard}==并将其打出，轮到@{unoList[4]} ！")
                else:
                    unoList[4] = unoList[1][nextid_]
                    unoList[2][id_].append(addCard)
                    context.appText(f"{sender}补了一张牌，轮到@{unoList[4]} ！")
                    context.appText(f"你新增了1张牌，这是你现在的牌：\n{formatCards(id_)}。", "whisper", to=sender)
            elif card not in unoList[2][id_]:
                context.appText("你没有那张牌！")
                
            elif card == "+4":
                if len(msgList) < 2:
                    context.appText("缺少参数！")
                elif msgList[1] not in "红黄蓝绿":
                    context.appText("参数错误！")
                else:
                    unoList[8] = msgList[1]
                    unoList[7] = unoList[1][nextid_]
                    unoList[6] = True
                    unoList[5] = unoList[5][0]
                    unoList[2][id_].remove(card)
                    context.appText(f"{sender}出了+4！@{unoList[1][nextid_]} 可以发送==u ?!==质疑或==u .==跳过。")
            elif card == "变色":
                if len(msgList) < 2:
                    context.appText("缺少参数！")
                elif msgList[1] not in "红黄蓝绿":
                    context.appText("参数错误！")
                else:
                    color(msgList[1], id_)
                    unoList[2][id_].remove(card)
                    context.appText(f"{sender}出了变色牌，颜色变为=={msgList[1]}==，轮到@{unoList[4]} ！")
            elif card[0] == unoList[5][0] or card[1:] == unoList[5][1:]:
                unoList[5] = card
                if card[1:] == "禁":
                    ban(id_)
                    context.appText(f"{sender}出了=={card}==，{unoList[1][nextid_]}跳过1轮，轮到@{unoList[4]} ！")
                elif card[1:] == "+2":
                    add2(id_)
                    context.appText(f"{sender}出了=={card}==，{unoList[1][nextid_]}加2张，轮到@{unoList[4]} ！")
                    context.appText(f"你新增了2张牌，这是你现在的牌：\n{formatCards(nextid_)}。", "whisper", to=unoList[1][nextid_])
                elif card[1:] == "转向":
                    id_ = turn(id_)
                    context.appText(f"{sender}出了{card}，==顺序转换==，轮到@{unoList[4]} ！")
                else:
                    unoList[4] = unoList[1][nextid_]
                    context.appText(f"{sender}出了=={card}==，轮到@{unoList[4]} ！")
                    no_card(1)
                unoList[2][id_].remove(card)
            elif card not in ["+4", "变色"]:
                return context.appText("不符合规则！")
            if len(unoList[2][id_]) == 1:
                context.appText(f"{sender}==UNO==了！！！")
            elif not unoList[2][id_]:
                context.appText(f"{sender}获胜，游戏结束。")
                stop_game()
        elif sender == unoList[7]:
            lastid_ = (id_ - 1) % len(unoList[1])
            if card == ".":
                add4(id_)
                context.appText(f"{sender}不质疑，加4张，颜色变为=={unoList[8]}==。轮到@{unoList[4]} ！")
                context.appText(f"你新增了4张牌，这是你现在的牌：\n{formatCards(id_)}。", "whisper", to=unoList[1][id_])
                unoList[5] = unoList[8] + "?"
                unoList[6] = False
            elif card == "?!":
                if any(unoList[5] == i[0] for i in unoList[2][lastid_]):
                    add4(lastid_, True)
                    lastPlayer = unoList[1][lastid_]
                    context.appText(f"{lastPlayer}==有=={unoList[5]}色牌！")
                    context.appText(f"{sender}质疑成功！=={lastPlayer}==加4张，颜色变为=={unoList[8]}==。轮到@{unoList[4]}！")
                    context.appText(f"你新增了4张牌，这是你现在的牌：\n{formatCards(id_)}。", "whisper", to=lastPlayer)
                    unoList[5] = unoList[8] + "?"
                else:
                    add4(id_, num=6)
                    context.appText(f"{unoList[1][lastid_]}==没有=={unoList[5]}色牌！")
                    context.appText(f"{sender}质疑失败，加==6==张，颜色变为=={unoList[8]}==。轮到@{unoList[4]} ！")
                    context.appText(f"你新增了6张牌，这是你现在的牌：\n{formatCards(id_)}。", "whisper", to=unoList[1][id_])
                    unoList[5] = unoList[8] + "?"
                unoList[6] = False