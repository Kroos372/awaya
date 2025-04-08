import random

## [0真心话开关, 1{昵称：摇出的数字}, 2[玩游戏中的hash]]
truthList = [False, {}, []]

MENU = "\n".join([
    "t 开始: 开始",
    "t 结束: 结束",
    "t 结算: 结算",
])

def truthDo(sender, hashCode)->str:
    ranNum = random.randint(1, 1000), 
    if not truthList[0]:
        return str(ranNum)
    elif sender in truthList[1]:
        return f"{sender}已经摇出{truthList[1][sender]}了(ﾉ\"◑ڡ◑)ﾉ"
    elif hashCode in truthList[2]:
        return f"{sender}，不要想开小号哦(￢з￢)σ "
    else:
        truthList[1][sender] = ranNum
        truthList[2].append(hashCode)
        return str(ranNum)

def truthReply(msg)->str:
    if msg == "开始":
        if truthList[0]:
            return "已经在玩了哦╮(╯_╰)╭"
        else: 
            truthList[0] = True
            return f"发r, 发结算, 发@awa_ya 提问"
    elif msg == "结束":
        if truthList[0]:
            truthList[0] = False
            return "好吧好吧，结束咯(一。一;;）"
        else:
            return "真心话还没开始你在结束什么啊(▼皿▼#)"
    elif msg == "结算":
        if not truthList[0]:
            return "真心话还没开始你在结算什么啊(▼皿▼#)"
        elif len(truthList[2]) < 2:
            return "人数不够"
        else:
            sort = sorted(truthList[1].items(), key=lambda x: x[1])
            loser, winner = sort[0], sort[-1]
            fin = f"人数：{len(truthList[1])}。\n最大：{winner[1]}（{winner[0]}），最小：{loser[1]}（{loser[0]}）。"
            truthList[1] = {}
            truthList[2] = []
            return fin
    elif msg == "help":
        return MENU