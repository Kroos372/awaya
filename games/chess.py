import re
import numpy as np

# [0象棋开关, 1轮到谁, 2[红方, 黑方], 3当前棋盘]
CCList = [False, None, [None, None], []]
CLOLUMN, LETTERS = ["| \\ |1|2|3|4|5|6|7|8|9|", "|-|-|-|-|-|-|-|-|-|-|"], list("ABCDEFGHIJ")
RED, BLACK = ["==车==", "==马==", "==相==", "==士==", "==帥==", "==兵==", "==炮=="], ["車", "馬", "象", "仕", "將", "卒", "砲"]

RULE = "\n".join([
    "好、的，听清楚规则了哦~",
    "如你所见，棋盘一共有10行，从上到下依次为ABCDEFGHIJ；又有9列，从左到右依次为123456789。",
    "用这个方法可以表示出棋盘上的任何位置，例如左上角的马，其坐标应为A2。",
    "发送`cc 旧位置 新位置`移动棋子，例如`cc C2 C3`可以将左上角的炮向右挪动一格。",
    "明白了吗？开始吧~",
    "温馨提示：使用暗色主题棋盘显示效果更佳~"
])
MENU = "\n".join([
    "使·用·说·明\\~\n哟，这不是sender吗，我是来自阿瓦国的狂热象棋Bot阿瓦娅哦，很高兴认识你\\~",
    "以下是我能做的事情，如果能帮上你的忙的话我会很高兴的！~~请随意使用我吧~~",
    "`cc 加入`：加入游戏或者创建一个游戏\\~",
    "`cc 结束`：结束游戏，如果你执意要这么做的话……",
    "`cc help`：显示这一段话~~，也就是套娃啦！~~",
    "`cc check`:当前棋盘",
    "芜湖，就这么多了，虽然我也知道我很棒不过毕竟人的能力是有限的嘛~但放心，我每天都在努力学习，也许明天，下个小时或者下一分钟，\
    在你不注意的时候，我就有新功能啦，ᕕ( ᐛ )ᕗ\\~"
])
CINIT = np.array([
    [RED[0], RED[1], RED[2], RED[3], RED[4], RED[3],RED[2], RED[1], RED[0]],
    [" "]*9,
    [" ", RED[6], " ", " ", " ", " ", " ", RED[6], " "],
    [RED[5], " ", RED[5], " ", RED[5], " ", RED[5], " ", RED[5]],
    [" "]*9,

    [" "]*9,
    [BLACK[5], " ", BLACK[5], " ", BLACK[5], " ", BLACK[5], " ", BLACK[5]],
    [" ", BLACK[6], " ", " ", " ", " ", " ", BLACK[6], " "],
    [" "]*9,
    [BLACK[0], BLACK[1], BLACK[2], BLACK[3], BLACK[4], BLACK[3], BLACK[2], BLACK[1], BLACK[0]],
])

def move(old, new, chess) -> str:
    if CCList[3][new[0], new[1]] in [RED[4], BLACK[4]]:
        text = f"@{CCList[1]} 获胜！恭喜！"
        endGame()
        return text
    now = CCList[1]
    CCList[1] = CCList[2][0] if CCList[1] == CCList[2][1] else CCList[2][1]
    for i in CCList[3][:,3:6]:
        if (BLACK[4] in i) and (RED[4] in i) and set(i[list(i).index(RED[4])+1:list(i).index(BLACK[4])]) == {" "}:
            text = f"@{CCList[1]} 获胜！恭喜！"
            endGame()
            return text
    CCList[3][old[0], old[1]] = " "
    CCList[3][new[0], new[1]] = chess
    return f"{sendBoard()}\n{now}挪动了{chr(old[0]+65)}{old[1]+1}的{chess}，轮到@{CCList[1]}"
def endGame():
    CCList[0] = False
    CCList[1] = None
    CCList[2] = [None, None]
    CCList[3] = CINIT.copy()
def sendBoard() -> str:
    mae = CLOLUMN+[f"|{n}|"+ "|".join(i) +"|" for i, n in zip(CCList[3], LETTERS)]
    return "\n".join(mae)
def CCreply(sender: str, msg: str) -> str:
        res = re.search(r"^([ABCDEFGHIJ])([123456789]) ([ABCDEFGHIJ])([123456789])$", msg.upper())
        if CCList[0]:
            if sender in CCList[2]:
                if msg == "结束":
                    return f"啊，虽然有点儿遗憾不过，既然{sender}说结束了的话就结束吧……发送开始游戏可以再次开始哦~"
                elif msg == "check":
                    return sendBoard()
            if not (CCList[2][1] and sender == CCList[1] and res):
                return "不能挪动空气！"
            res = res.groups()
            old, new = [ord(res[0])-65, int(res[1])-1], [ord(res[2])-65, int(res[3])-1]
            goingChess, moveChess = CCList[3][new[0], new[1]], CCList[3][old[0], old[1]]
            if moveChess == " ":
                return "不能吃自己也不能用别人的棋子！"
            use = CCList[3][min(old[0], new[0])+1:max(old[0], new[0]), old[1]]
            use2 = CCList[3][old[0], min(old[1], new[1])+1:max(old[1], new[1])]
            if (not CCList[2].index(sender) and not goingChess in RED and moveChess in RED) or (CCList[2].index(sender) and not goingChess in BLACK and moveChess in BLACK):          
                if moveChess == RED[5] and (old[0] > 4 and abs(old[1] - new[1]) == 1 and old[0] == new[0] or new == [old[0]+1, old[1]]):
                    return move(old, new, moveChess)
                elif moveChess == BLACK[5] and (old[0] < 5 and abs(old[1] - new[1]) == 1 and old[0] == new[0] or new == [old[0]-1, old[1]]):
                    return move(old, new, moveChess)
                elif moveChess in [RED[6], BLACK[6]]:
                    if goingChess != " ":
                        if (new[0] == old[0] and len(use2[use2!=" "]) == 1) or (new[1] == old[1] and len(use[use!=" "]) == 1):
                            return move(old, new, moveChess)
                        else: return "不符合行棋规则"
                    elif (new[0] == old[0] and not len(use2[use2!=" "])) or (new[1] == old[1] and not len(use[use!=" "])):
                        return move(old, new, moveChess)
                    else: return "不符合行棋规则"
                elif (moveChess in [RED[0], BLACK[0]]) and ((new[0] == old[0] and not len(use2[use2!=" "])) or ((new[1] == old[1]) and not len(use[use!=" "]))):
                    return move(old, new, moveChess)
                elif (moveChess in [RED[1], BLACK[1]]) and ((abs(old[0]-new[0]) == 2 and abs(old[1]-new[1]) == 1 and CCList[3][int(old[0]-(old[0]-new[0])/2), old[1]] == " ") or (abs(old[1]-new[1]) == 2 and abs(old[0]-new[0]) == 1 and CCList[3][old[0], int(old[1]-(old[1]-new[1])/2)] == " ")):
                    return move(old, new, moveChess)
                elif moveChess == RED[2] and (abs(old[0]-new[0]) == 2 and abs(old[1]-new[1]) == 2 and CCList[3][int(old[0]-(old[0]-new[0])/2), int(old[1]+(old[1]-new[1])/2)] == " " and new[0] < 5) :
                    return move(old, new, moveChess)
                elif moveChess == BLACK[2] and (abs(old[0]-new[0]) == 2 and abs(old[1]-new[1]) == 2 and CCList[3][int(old[0]-(old[0]-new[0])/2), int(old[1]+(old[1]-new[1])/2)] == " " and new[0] > 4) :
                    return move(old, new, moveChess)
                elif moveChess == RED[4] and (new[0] in [0, 1, 2]) and (new[1] in [3, 4, 5]) and ((old[0]==new[0] and abs(old[1]-new[1])==1) or (old[1]==new[1] and abs(old[0]-new[0])==1)):
                    return move(old, new, moveChess)
                elif moveChess == BLACK[4] and (new[0] in [7, 8, 9]) and (new[1] in [3, 4, 5]) and ((old[0]==new[0] and abs(old[1]-new[1])==1) or (old[1]==new[1] and abs(old[0]-new[0])==1)):
                    return move(old, new, moveChess)
                elif moveChess == RED[3] and (new[0] in [0, 1, 2]) and (new[1] in [3, 4, 5]) and abs(old[0]-new[0])==1 and abs(old[1]-new[1])==1:
                    return move(old, new, moveChess)
                elif moveChess == BLACK[3] and (new[0] in [7, 8, 9]) and (new[1] in [3, 4, 5]) and abs(old[0]-new[0])==1 and abs(old[1]-new[1])==1:
                    return move(old, new, moveChess)
                else:
                    return f"不符合{moveChess}的行棋规则"
        elif msg == "加入":
            if not CCList[2][0]:
                CCList[2][0] = sender
                CCList[3] = CINIT.copy()
                return "游戏创建好了，快找人来加入吧！"
            elif sender == CCList[2][0]:
                return "你已经，加入过了哦~"
            elif CCList[2][1]:
                return "游戏已经开始了，等到下局吧~"
            else:
                CCList[0] = True
                CCList[2][1] = sender
                CCList[1] = CCList[2][0]
                return sendBoard() + "\n" + RULE + f"\n@{CCList[2][0]} 先手执红（绿？）（上方，简体），@{CCList[2][1]} 后手执黑（下方，繁体）。开始了哦~"
        elif msg == "help":
            return MENU.replace("sender", sender)