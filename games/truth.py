import random

## [0真心话开关, 1{昵称：摇出的数字}, 2[玩游戏中的hash]]
truthList = [False, {}, []]

MENU = "\n".join([
    "t 开始: 开始",
    "t 结束: 结束",
    "t 结算: 结算",
])
TRUTHMENU = "\n".join([
    "真心话现在开始啦，发送*r*来获取随机数，*t 结算*来结算，*t 结束*来结束游戏~",
    "以下是注意事项：",
    "1\\.愿赌服输",
    "2\\.提的问题请在能够接受的范围内，",
    "3\\.尺度请自行把握，不用过于勉强自己也不要勉强他人，感到不适可以要求对方更换问题，",
    "4\\.玩得愉快。",
    f"PS: ***实在***没活整了可以发送==@awa_ya 提问==获取些离谱小问题",
    f"PSS: 获取随机数只能用*r*，而不是*r 数字*，后者在真心话中会被忽略。"
])

def truthDo(sender, hashCode)->str:
    ranNum = random.randint(1, 1000)
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

def main(msg)->str:
    if msg == "开始":
        if truthList[0]:
            return "已经在玩了哦╮(╯_╰)╭"
        else: 
            truthList[0] = True
            return TRUTHMENU
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
            fin = f"人数：{len(truthList[1])}。\n最大：{winner[1]}（{winner[0]}），最小：{loser[1]}（{loser[0]}）。\n请提问。"
            truthList[1] = {}
            truthList[2] = []
            return fin
    elif msg == "help":
        return MENU