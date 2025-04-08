import json, websocket, ssl, os, random

# [0是否游戏中, 1[玩家列表], 2[各玩家的牌], 3[当前牌堆], 4第一人, 5第一张牌, 6轮到序号]
unoList = [False, [], [], [], None, None, 0]

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
    "游戏规则请自行百度",
    "使用==p 牌 <参数>==出牌，例如==p 绿2==, ==p 变色 蓝==",
    "使用==p .==跳过回合、==p check==查看自己目前的牌",
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
    unoList[0] = 1
    initCards()
    for i in range(len(unoList[1])):
        playerCard = []
        for j in range(7):
            addCard = random.choice(unoList[3])
            playerCard.append(addCard)
            unoList[3].remove(addCard)
        unoList[2].append(playerCard)
    unoList[4] = random.choice(unoList[1])
    unoList[5] = random.choice(unoList[3])
    while unoList[5] == "+4":
        unoList[5] = random.choice(unoList[3])
    unoList[3].remove(unoList[5])

def stop_game():
    unoList[0] = 0
    unoList[1] = []
    unoList[2] = []

def add4(color, id_):
    nextid_ = (id_ + 1) % len(unoList[1])
    next2id_ = (id_ + 2) % len(unoList[1])
    no_card(4)
    unoList[5] = color + "?"
    unoList[4] = unoList[1][next2id_]
    for i in range(4):
        addCard = random.choice(unoList[3])
        unoList[2][nextid_].append(addCard)
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

def turn(id_):
    unoList[6] = 1
    unoList[1].reverse()
    unoList[2].reverse()
    unoList[4] = unoList[1][(-id_) % len(unoList[1])]
            
def unoReply(context, sender, msg):
    if msg == "加入":
        if unoList[0]:
            context.appText("游戏已经开始了，等下一轮吧。")
        if sender in unoList[1]:
            context.appText("你已经加入了！")
        else:
            unoList[1].append(sender)
            context.appText(f"加入成功，现在有{len(unoList[1])}人。")
    elif msg == "退出" and sender in unoList[1]:
        unoList[1].remove(sender)
        context.appText("退出成功...")
    elif msg == "开始" and not unoList[0]:
        if len(unoList[1]) >= 2:
            if len(unoList[1]) == 8:
                context.appText("人数达到上限，游戏自动开始！")
            start_game()
            for i in range(len(unoList[2])):
                context.appText(f"这是你的牌：{unoList[2][i]}", "whisper", to=unoList[1][i])
            context.appText(f"牌发完啦，初始牌是=={unoList[5]}==，请`{unoList[4]}`先出！发送==u 规则==可以查看出牌规则哦")
        else:
            context.appText("人数不够！")
    elif msg == "结束" and unoList[0]:
        stop_game()
        context.appText("结束了...")
    elif msg == "help":
        context.appText(UNOMENU)
    elif msg == "规则":
        context.appText(UNORULE)
    elif sender == unoList[4]:
        msgList = msg.split()
        card = msgList[1]
        id_ = unoList[1].index(sender)
        nextid_ = (id_ + 1) % len(unoList[1])
        next2id_ = (id_ + 2) % len(unoList[1])
        if card == "check":
            context.appText(f"现在牌面上的牌是=={unoList[5]}==，这是你的牌：{unoList[2][id_]}", "whisper", to=sender)
            
        if card == ".":
            nextid_ = (id_ + 1) % len(unoList[1])
            addCard = random.choice(unoList[3])
            unoList[3].remove(addCard)
            if addCard[1:] == "禁":
                ban(id_)
                context.appText(f"`{sender}`补到了=={addCard}==并将其打出，`{unoList[1][nextid_]}`跳过1轮，轮到`{unoList[4]}`！")
            elif addCard[1:] == "+2":
                add2(id_)
                context.appText(f"`{sender}`补到了=={addCard}==并将其打出，`{unoList[1][nextid_]}`加2张，轮到`{unoList[4]}`！")
                context.appText(f"你新增了2张牌，这是你现在的牌：{unoList[2][nextid_]}。", "whisper", to=unoList[1][nextid_])
            elif addCard[1:] == "转向":
                turn(id_)
                context.appText(f"`{sender}`补到了{addCard}并将其打出，==顺序转换==，轮到`{unoList[4]}`！")
            else:
                unoList[4] = unoList[1][nextid_]
                unoList[2][id_].append(addCard)
                context.appText(f"`{sender}`补了一张牌，轮到`{unoList[4]}`！")
                context.appText(f"你新增了1张牌，这是你现在的牌：{unoList[2][id_]}。", "whisper", to=sender)
                    
                if card not in unoList[2][id_]:
                    context.appText("你没有那张牌！")
                    
                if card == "+4":
                    for i in unoList[2][id_]:
                        if i[0] == unoList[5][0]:
                            context.appText("不符合规则！")
                    if len(msgList) < 3:
                        context.appText("缺少参数！")
                    if msgList[2] not in "红黄蓝绿":
                        context.appText("参数错误！")
                    add4(msgList[2], id_)
                    context.appText(f"`{sender}`出了+4（王牌），`{unoList[1][nextid_]}`加四张，颜色变为=={msgList[2]}==，轮到`{unoList[4]}`！")
                    context.appText(f"你新增了4张牌，这是你现在的牌：{ unoList[2][nextid_]}。", "whisper", to=unoList[1][nextid_])
            
        if card == "变色":
            if len(msgList) < 3:
                context.appText("缺少参数！")
            if msgList[2] not in "红黄蓝绿":
                context.appText("参数错误！")
            color(msgList[2], id_)
            context.appText(f"`{sender}`出了变色牌，颜色变为=={msgList[2]}==，轮到`{unoList[4]}`！")
        
        if card[0] == unoList[5][0] or card[1:] == unoList[5][
                1:] or unoList[5] == "变色":
            unoList[5] = card
            if card[1:] == "禁":
                ban(id_)
                context.appText(f"`{sender}`出了=={card}==，`{unoList[1][nextid_]}`跳过1轮，轮到`{unoList[4]}`！")
            elif card[1:] == "+2":
                add2(id_)
                context.appText(f"`{sender}`出了=={card}==，`{unoList[1][nextid_]}`加2张，轮到`{unoList[4]}`！")
                context.appText(f"你新增了2张牌，这是你现在的牌：{unoList[2][nextid_]}。", "whisper", to=unoList[1][nextid_])
            elif card[1:] == "转向":
                turn(id_)
                context.appText(f"`{sender}`出了{card}，==顺序转换==，轮到`{unoList[4]}`！")
            else:
                unoList[4] = unoList[1][nextid_]
                context.appText(f"`{sender}`出了=={card}==，轮到`{unoList[4]}`！")
        elif card not in ["+4", "变色"]:
            context.appText("不符合规则！")
        if unoList[6]:
            id_ = (-id_ - 1) % len(unoList[1])
            unoList[6] = 0
        unoList[2][id_].remove(card)
        if len(unoList[2][id_]) == 1:
            context.appText(f"`{sender}`==UNO==了！！！")
        if len(unoList[2][id_]) == 0:
            context.appText(f"`{sender}`获胜，游戏结束。")
            stop_game()
        no_card(1)