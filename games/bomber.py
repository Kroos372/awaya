import random

# [0炸弹数字, 1[在玩的人], 2轮到序号, 3初始最小值, 4初始最大值, 5是否在玩, 6本轮最小值, 7本轮最大值]
bombs = [0, [], 0, 1, 1000, False, 1, 1000]

BOMBMENU = "\n".join([
    "数字炸弹——",
    "规则很简单，在一个给定的范围中设某个数字为「炸弹」，玩家轮流猜数缩小范围，直到某人猜到炸弹。以下是关于数字炸弹的命令：",
    "b 加入 : 加入数字炸弹游戏！",
    "b 退出 : 退出数字炸弹游戏",
    "b bot : 让机器人加入！",
    "b 开始 : 开始数字炸弹，至少需要两个人。",
    "b <数字> : 猜数。",
    "b 结束 : 结束数字炸弹……",
    "就是这么多了，祝你好运，ᕕ( ᐛ )ᕗ\\~"
])

def endBomb():
    bombs[5], bombs[2], bombs[1] = False, 0, []
    bombs[6], bombs[7] = bombs[3], bombs[4]

# 判断数字与更新
def bombRule(context, num=None):
    old = bombs[1][bombs[2]]
    if old == context.nick:
        num = random.randint(bombs[6], bombs[7])
        context.appText(f"{context.nick}猜了{num}！")
    if bombs[6] > num or bombs[7] < num:
        return context.appText(f"不符合规则，数字必须在{bombs[6]}到{bombs[7]}之间！（含两边）")
    elif bombs[0] > num:
        bombs[6] = num + 1
    elif bombs[0] < num:
        bombs[7] = num - 1
    else:
        endBomb()
        return context.appText(f"炸弹炸到{old}了！")
    bombs[2] = (bombs[2] + 1) % len(bombs[1])
    player = bombs[1][bombs[2]]
    context.appText(f"{old}没有踩中！\n现在炸弹范围为{bombs[6]}到{bombs[7]}，轮到@{player} 了！")
    if player == context.nick:
        bombRule(context) # 递归赛高~

def main(context, sender, msg):
    if msg == "help":
        context.appText(BOMBMENU)
    elif msg == "加入":
        if bombs[5]:
            context.appText("这局已经开始了，等下局吧(￣▽￣)")
        elif sender in bombs[1]:
            context.appText("您已经加入过了(￣▽￣)")
        else:
            bombs[1].append(sender)
            context.appText("您已成功加入游戏・▽・)ノ ")
    elif msg == "退出":
        if sender in bombs[1]:
            bombs[1].remove(sender)
            context.appText("退出成功_(:зゝ∠)\\_")
    elif msg == "bot":
        if bombs[5]:
            context.appText("这局已经开始了，等下局吧~")
        elif context.nick in bombs[1]:
            context.appText("机器人已经加入过了！")
        else:
            bombs[1].append(context.nick)
            context.appText("已成功添加机器人进入游戏！")
    elif msg == "开始" and not bombs[5]:
        if len(bombs[1]) < 2:
            context.appText("至少需要两个人才能开始(⊙﹏⊙)")
        else:
            bombs[5], bombs[6], bombs[7] = True, bombs[3], bombs[4]
            bombs[0] = random.randint(bombs[3], bombs[4])
            context.appText(f"炸弹已经设置好了，范围在{bombs[3]}到{bombs[4]}（包含两数）之间！\n由@{bombs[1][0]} 开始，发送==b 数字==游玩！")
            if bombs[1][0] == context.nick:
                bombRule(context)
    elif msg == "结束" and bombs[5]:
        endBomb()
        context.appText("好吧好吧，结束咯~")
    elif bombs[5] and sender == bombs[1][bombs[2]]:
        try:
            num = int(msg)
        except:
            context.appText("请输入一个整数ヾ|≧_≦|〃")
        else:
            bombRule(context, num)