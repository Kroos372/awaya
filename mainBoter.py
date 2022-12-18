#coding=utf-8
from const import *
import websocket, ssl, requests, re, threading, traceback, sys, os

# 存入记忆中！
def writeJson(filename, datas):
    with open(filename, "w", encoding="utf8") as f:
        json.dump(datas, fp=f, ensure_ascii=False, indent=2)
# 名字提纯
def namePure(name: str) -> str: return name.replace("@", "").replace(" ", "")
# 内容转换
def textPure(text: str) -> str: return text.replace("\\~", "~").replace("~", " ")
# 获取沙雕小设计
def randomDesign(num: int=1) -> str:
    full = []
    if num > 10:
        return "最多一次性获取10个(〃｀ 3′〃)"
    elif num < 1:
        return "最少获取一个(〃｀ 3′〃)"
    for i in range(num):
        item = random.choice(designs["items"])
        const = random.choice(designs["constraints"])
        prepend = random.choice(designs["prepend"])
        if const[-1] == "的":
            full.append(f"{prepend}{const}{item}")
            continue
        full.append( f"{const}{prepend}{item}")
    return "，\n".join(full)
# 分解质因数！这是我的数学极限了，呜呜……
def getPrime(i, factors) -> list:
    if i == 1: return ["没法分解啊啊啊啊(+﹏+)"]
    for x in range(2, int(i**0.5 + 1)):
        if i % x == 0:
            factors.append(str(x))
            getPrime(int(i / x), factors)
            return factors
    factors.append(str(i))
    return factors
# r来r去
def rollTo1(maxNum: int=1000) -> str:
    road =  []
    while True:
        road.append(str(ran:=random.randint(1, maxNum)))
        if ran != 1: maxNum = ran
        else: break
    return f"{'，'.join(road)}：{len(road)}"
def hashByCode(code: str) -> str:
    try: return "，".join(data[code])
    except: return "不存在这个hash码(◐_◑)"
def hashByName(name: str, now: bool=False) -> str:
    if now:
        try: return hashByCode(userHash[name])
        except: return "此人当前不在线( ⊙ o ⊙ )"
    else:
        l, count = [], 0
        for i in data.values():
            if name in i:
                count += 1
                text = f"{count}\\. "+"，".join(i)
                l.append(text.replace("_", "\\_"))
        return "\n".join(l) or "没有这个名字！"
# 一天不涩涩，癫痫发作作
def colorPic() -> str:
    setu = requests.get("https://api.lolicon.app/setu/v2").json()["data"][0]
    # 过滤离谱关键词
    tags = [i for i in setu["tags"] if not "乳" in i and not "魅" in i and\
    not "内" in i and not "尻" in i and not "屁" in i and not "胸" in i]
    url = setu["urls"]["original"]
    title = setu["title"]
    author = setu["author"]
    return f"{url}\n标题：{title}\n标签：{','.join(tags)}\n作者：{author}"
# 结束
def endBomb():
    bombs[5], bombs[2], bombs[1] = False, 0, []
    bombs[6], bombs[7] = bombs[3], bombs[4]
# 判断数字与更新
def bombRule(chat, num=None):
    old = bombs[1][bombs[2]]
    if old == nick:
        num = random.randint(bombs[6], bombs[7])
    if bombs[6] > num or bombs[7] < num:
        return chat.sendMsg(f"不符合规则，数字必须在{bombs[6]}到{bombs[7]}之间！（含两边）")
    elif bombs[0] > num:
        bombs[6] = num + 1
    elif bombs[0] < num:
        bombs[7] = num - 1
    else:
        endBomb()
        return chat.sendMsg(f"炸弹炸到{old}了！")
    bombs[2] = (bombs[2] + 1) % len(bombs[1])
    player = bombs[1][bombs[2]]
    chat.sendMsg(f"{old}没有踩中！\n现在炸弹范围为{bombs[6]}到{bombs[7]}，轮到@{player} 了！")
    if player == nick:
        bombRule(chat)
# 我该如何回复大家呢？
def reply(sender: str, msg: str) -> str:
    rans = random.randint(1, 10)
    if rans > 6:
        for k, v in answer.items():
            if re.search(k, msg):
                if v: return random.choice(v).replace("sender", sender).replace("called", called)
                else: break
    cont = requests.get(f"https://api.qingyunke.com/api.php?key=free&msg={msg}")
    return cont.json()["content"].replace("菲菲", called).replace("{br}", "\n")\
    .replace("help", "==@bot名 help==，==菜单==或==@bot名 帮助==")
# 日志日志
def logs(text: str):
    with open(f"log/{thingsList[9]}.txt", "a+", encoding="utf8") as f:
        f.write(text+"\n")
def msgGot(chat, msg: str, sender: str, senderTrip: str):
    rans = random.randint(1, 134)
    this_turn = f"{sender}：{msg}"
    # print(this_turn)
    command = msg[:6]
    logs(this_turn)
    if not sender in ignored:
        allMsg.append(this_turn)
        if len(allMsg) > 377: del allMsg[0]
    if userTrip.get(sender) in blackList or sender in blackName: return

    if (mes := afk.get(sender)) is not None:
        chat.sendMsg(f"@{sender} 不再{mes}了，欢迎回来~~摸鱼~~(\\*￣ω￣)")
        del afk[sender]
    elif msg.lower() == "afk":
        mes = "AFK"
        chat.sendMsg(f"@{sender} {mes}了")
        afk[sender] = mes
    elif msg[:4].lower() == "afk ":
        mes = msg[4:]
        chat.sendMsg(f"@{sender} 正在{mes}~~，加油~~ヾ(◍°∇°◍)ﾉﾞ")
        afk[sender] = mes
    else:
        for user in afk:
            if f"@{user.lower()}" in msg.lower():
                chat.sendMsg(f"{user} 正在{afk[user]}，请不要打扰ta……(\\* \"･∀･)ﾉ――◎")
    if msg[0] == PREFIX:
        command = msg[1:6]
        if command == "hash ": chat.sendMsg(hashByName(namePure(msg[6:])))
        elif command == "hasn ": chat.sendMsg(hashByName(namePure(msg[6:]), True))
        elif command == "code ": chat.sendMsg(hashByCode(msg[6:]))
        elif command == "colo ":
            if (color := userColor.get(namePure(msg[6:]))) is not None:
                if color: chat.sendMsg(color)
                else: chat.sendMsg("该用户还没有设置颜色(￢_￢)")
            else: chat.sendMsg("没有这个用户(╰_╯)#")
        elif command == "left ":
            if len(lis := msg.split()) < 3:
                chat.sendMsg("命令不正确！")
            elif lis[1] in chat.onlineUsers:
                chat.sendMsg(f"{lis[1]}在线着呢，为什么还要留言啊喂~")
            elif not re.search(r"^@{0,1}[a-zA-Z0-9_]{1,24}$", lis[1]):
                chat.sendMsg("昵称不合法！")
            else:
                leftMsg[time.time()] = [sender, namePure(lis[1]), "".join(lis[2:])]
                chat.sendMsg(f"@{sender}, {lis[1]}将会在加入时收到你的留言！~~如果那时我还在的话~~")
        elif command == "peep ":
            try:
                if msg[6:] == "0": raise ValueError
                array = msg.split(" ")
                if len(array)==2: 
                    want_peep = int(array[1])
                    if want_peep < 0: chat.sendMsg(f"/w {sender} 以下是从最前面到第{-want_peep}条的消息：\n"+ "\n".join(allMsg[:-want_peep]))
                    else: chat.sendMsg(f"/w {sender} 以下是从最近的{want_peep}条的消息：\n"+ "\n".join(allMsg[-want_peep:]))
                elif len(array)>2: chat.sendMsg(f"/w {sender} 懒得写提示语了：\n"+ "\n".join(allMsg[int(array[1]):int(array[2])]))
                else: raise ValueError
            except ValueError: chat.sendMsg(f"/w {sender} 然而peep后面需要一个非零整数")
        elif command == "welc ":
            if (text := msg[6:])[:1] == "/":
                chat.sendMsg("诶！你想干什么？真是坏心眼~")
            elif senderTrip:
                userData["welText"][senderTrip] = text
                writeJson("userData.json", userData)
                chat.sendMsg(f"为识别码{senderTrip}设置欢迎语成功了！")
            else: chat.sendMsg("您当前还没有识别码，请重进并在昵称输入界面使用==昵称#密码==设置一个！")
        elif msg == "welc":
            if senderTrip in userData["welText"]:
                del userData["welText"][senderTrip]
                writeJson("userData.json", userData)
                chat.sendMsg(f"为识别码{senderTrip}清除欢迎语成功了！")
            else: chat.sendMsg("你还没有设置欢迎语！")
        elif command == "last ":
            if sender in userData["lastText"] and userData["lastText"][sender][0] != senderTrip:
                chat.sendMsg(f"已经有人为{sender}设置过留言了，请换一个名字！")
            elif senderTrip:
                userData["lastText"][sender] = [senderTrip, msg[6:]]
                writeJson("userData.json", userData)
                chat.sendMsg(f"为{sender}({senderTrip})设置留言成功了！记得及时清除哦！")
            else: chat.sendMsg("您当前还没有识别码，请重启并在昵称输入界面使用==昵称#密码==设置一个！")
        elif command == "lost ":
            if (name:=namePure(msg[6:])) in (dic:=userData["lastText"]):
                chat.sendMsg(f"以下是{name}({dic[name][0]})的留言：\n{dic[name][1]}")
            else: chat.sendMsg("该用户还没有设置留言~")
        elif command == "unlo ":
            if (name:=namePure(msg[6:])) in (dic:=userData["lastText"]):
                if senderTrip == dic[name][0] or senderTrip in whiteList:
                    del dic[name]
                    writeJson("userData.json", userData)
                    chat.sendMsg("留言已删除，感谢您的使用！")
                else: chat.sendMsg(f"您的识别码与被清除者不同！正确识别码应为{dic[name][0]}！")
            else: chat.sendMsg("此用户还没有设置留言~")
        elif command == "prim ":
            try:
                digit = msg[6:19]
                eq = "\\*".join(getPrime(int(digit), []))
                chat.sendMsg(f"{digit}={eq}")
            except ValueError: chat.sendMsg("请输入一个***正整数***啊啊啊啊(￢_￢)")
        elif command == "rand ":
            try:
                digit = int(msg[6:])
                chat.sendMsg(randomDesign(digit))
            except ValueError: chat.sendMsg("参数必须是1到10之间的正整数(￣_,￣ )")
        elif command == "repl ":
            array = msg.split(" ")
            if len(array) < 3: chat.sendMsg(f"命令错误，请使用`{PREFIX}repl 提问 回答`的格式(‾◡◝)")
            else:
                ans = " ".join(array[2:])
                quest = textPure(array[1])
                if array[2:][0] == "/":
                    chat.sendMsg("？你想干什么(⊙﹏⊙)")
                    return
                elif not quest in answer: answer[quest] = ans
                else: answer[quest].append(ans)
                chat.sendMsg(f"添加成功(☆▽☆)")
                writeJson("answer.json", answer)

    elif msg.strip() == f"@{nick}":
        if rans > 129: chat.sendMsg(random.choice(RANDLIS[1]).replace("sender", sender))
        else: chat.sendMsg(random.choice(RANDLIS[0]).replace("sender", sender))
    elif msg.startswith(f"@{nick} "):
        chat.CCreply(sender, msg[len(nick)+2:])
    elif msg[0] == "r":
        if msg == "r":
            ranNum = random.randint(1, 1000)
            if thingsList[4]:
                if sender in thingsList[6]:
                    chat.sendMsg(f"{sender}已经摇出{thingsList[6][sender]}了(ﾉ\"◑ڡ◑)ﾉ")
                elif (hashCode := userHash[sender] ) in thingsList[7]:
                    chat.sendMsg(f"{sender}，不要想开小号哦(￢з￢)σ ")
                else:
                    thingsList[6][sender] = ranNum
                    chat.sendMsg(str(ranNum))
                    thingsList[7].append(hashCode)
            else: chat.sendMsg(str(ranNum))
        elif msg[:2] == "r ":
            try: beR = int(msg[2:])
            except: chat.sendMsg(str(random.randint(1, 1000)))
            else:
                if beR > 1: chat.sendMsg(str(random.randint(1, beR)))
                else: chat.sendMsg(str(random.randint(beR, 1)))
        elif command == "rollen":
            digit = msg[7:]
            try: chat.sendMsg(rollTo1(int(digit)))
            except ValueError as e: chat.sendMsg(rollTo1(1000))
        elif command == "rprime":
            digit = msg[7:20]
            try:
                if (dig:=random.randint(1, int(digit))) > 0:
                    eq = "\\*".join(getPrime(dig, []))
                    chat.sendMsg(f"{dig}={eq}")
                else: raise ValueError
            except ValueError as e:
                digit = str(random.randint(1, 1000))
                eq = "\\*".join(getPrime(int(digit), []))
                chat.sendMsg(f"{digit}={eq}")
    elif msg == "结算":
        if thingsList[4]:
            if len(thingsList[7]) < 2: chat.sendMsg("有句话叫什么，一个巴掌拍不响(°o°；)")
            else:
                sort = sorted(thingsList[6].items(), key=lambda x: x[1])
                loser, winner = sort[0], sort[-1]
                fin = "\n".join([f"本轮参与人数：{len(thingsList[6])}。",f"最大：{winner[1]}（{winner[0]}），",
                    f"最小：{loser[1]}（{loser[0]}）。", f"@{winner[0]} 向@{loser[0]} 提问，@{loser[0]} 回答。"])
                chat.sendMsg(fin)
                thingsList[6] = {}
                thingsList[7] = []
        else: chat.sendMsg(f"真心话就没开始你在结算什么呢，{sender}(▼皿▼#)")
    elif msg == "真心话":
        if not thingsList[4]:
            chat.sendMsg(GAMEMENU)
            thingsList[4] = True
        else: chat.sendMsg("已经在玩了哦╮(╯_╰)╭")
    elif msg == "结束游戏" and thingsList[4]:
        chat.sendMsg("好吧好吧，结束咯(一。一;;）")
        thingsList[4] = False
    elif msg[:2] == "b " and bombs[5] and sender == bombs[1][bombs[2]]:
        try: num = int(msg[2:])
        except: chat.sendMsg("请输入一个整数ヾ|≧_≦|〃")
        else: bombRule(chat, num)
    elif msg == "bomber":
        if not bombs[5]:
            if not sender in bombs[1]:
                bombs[1].append(sender)
                chat.sendMsg("您已成功加入游戏・▽・)ノ ")
            else: chat.sendMsg("您已经加入过了(￣▽￣)")
        else: chat.sendMsg("这局已经开始了，等下局吧(￣▽￣)")
    elif msg == "开始b" and not bombs[5]:
        if len(bombs[1]) > 1:
            bombs[5], bombs[6], bombs[7] = True, bombs[3], bombs[4]
            bombs[0] = random.randint(bombs[3], bombs[4])
            chat.sendMsg(f"炸弹已经设置好了，范围在{bombs[3]}到{bombs[4]}（包含两数）之间！\n由@{bombs[1][0]} 开始，发送==b 数字==游玩！")
            if bombs[1][0] == nick: bombRule(chat)
        else: chat.sendMsg("至少需要两个人才能开始(⊙﹏⊙)")
    elif msg == "结束b" and bombs[5]:
        endBomb()
        chat.sendMsg("好吧好吧，结束咯_(:зゝ∠)\\_")
    elif msg[:2] == "菜单" or msg[:4] == "menu":
        if msg == "菜单":
            if senderTrip == OWNER: men = "\n".join(MENU+MENUSSP)
            elif senderTrip in whiteList: men = "\n".join(MENU+MENUSP)
            else: men = "\n".join(MENU+MENUFT)
            chat.sendMsg(f"/w {sender} {men}")
        elif msg == "菜单w" and senderTrip in whiteList:
            men = "\n".join(ADMMENU)
            chat.sendMsg(f"/w {sender} {men}")
        elif msg == "菜单~" and senderTrip == OWNER:
            chat.sendMsg(f"/w {sender} {OWNMENU}")
        elif msg == "menu":
            if senderTrip == OWNER: men = "\n".join(ENGMENU+ENGMENUSSP)
            elif senderTrip in whiteList: men = "\n".join(ENGMENU+ENGMENUSP)
            else: men = "\n".join(ENGMENU+ENGMENUFT)
        elif msg == "menuw" and senderTrip in whiteList:
            men = "\n".join(ENGADMMENU)
            chat.sendMsg(f"/w {sender} {men}")
        elif msg == "menu~" and senderTrip == OWNER:
            chat.sendMsg(f"/w {sender} {ENGOWNMENU}")
    # 古老的梗
    elif namePure(msg) == sender: chat.sendMsg("why did you call yourself")
    elif msg.lower() in LINE:
        call = LINE[msg.lower()]
        if hasattr(call, "__call__"): chat.sendMsg(call(sender))
        else: chat.sendMsg(random.choice(call).replace("sender", sender))
    # 白名单功能，阿瓦娅的VIP用户捏~
    elif msg[0] == "0" and senderTrip in whiteList:
        # 涩涩，没有涩涩我要死了！！！
        if command == "0setu ":
            try:
                thingsList[3] = int(msg[6:])
                chat.sendMsg("涩涩涩涩涩——")
            except ValueError: chat.sendMsg("你是1还是0？")
        # 小黑屋是不值得学习的！
        elif command == "0addb ":
            try:
                if not (hash_:=userHash[namePure(msg[6:])]) in blackList:
                    blackList.append(hash_)
                    writeJson("userData.json", userData)
                    chat.sendMsg("好好好，又进去了一个。")
                else: chat.sendMsg("可惜他/她已经在咯~")
            except KeyError: chat.sendMsg("可惜这人现在不在呢…(⊙＿⊙；)…")
        elif command == "0delb ":
            try:
                if (hash_:=userHash[namePure(msg[6:])]) in blackList:
                    blackList.remove(hash_)
                    writeJson("userData.json", userData)
                    chat.sendMsg("删除黑名单用户成功！")
                else: chat.sendMsg("这人不在小黑屋里哦？")
            except KeyError: chat.sendMsg("可惜这人现在不在呢…(⊙＿⊙；)…")
        elif command == "0addn ":
            try:
                if not (name:=namePure(msg[6:])) in blackName:
                    blackName.append(name)
                    writeJson("userData.json", userData)
                    chat.sendMsg("好好好，又进去了一个。")
                else: chat.sendMsg("可惜他/她已经在咯~")
            except KeyError: chat.sendMsg("可惜这人现在不在呢…(⊙＿⊙；)…")
        elif command == "0deln ":
            try:
                if (name:=namePure(msg[6:])) in blackName:
                    blackName.remove(name)
                    writeJson("userData.json", userData)
                    chat.sendMsg("删除黑名单用户成功！")
                else: chat.sendMsg("这人不在小黑屋里哦？")
            except KeyError: chat.sendMsg("可惜这人现在不在呢…(⊙＿⊙；)…")
        elif command == "0time ":
            try:
                thingsList[5] = int(msg[6:])
                chat.sendMsg("好好好，如你所愿~")
            except ValueError:
                chat.sendMsg("1或者0，明白了吗~")
        elif command == "0bcol ":
            chat.sendMsg(f"/color {msg[6:]}")
            chat.sendMsg("自动变色ヽ(*。>Д<)o゜")
        elif msg == "rcolor":
            chat.sendMsg(f"/color {hex(random.randint(0, 0xffffff))[2:]:0>6}")
            chat.sendMsg("自动变色ヽ(*。>Д<)o゜")
        elif command == "0kill ":
            chat.sendMsg(f"/w {msg[6:]} "+"$\\begin{pmatrix}qaq\\\\[999999999em]\\end{pmatrix}$")
            chat.sendMsg(f"~kick {msg[6:]}")
        elif command == "0bans ":
            if not (hash_:=userHash[namePure(msg[6:])]) in banned:
                banned.append(hash_)
                chat.sendMsg(f"/w {msg[6:]} "+"$\\begin{pmatrix}qaq\\\\[999999999em]\\end{pmatrix}$")
                chat.sendMsg(f"~kick {msg[6:]}")
            else:
                chat.sendMsg("他/她已经被封了！")
        elif command == "0uban ":
            try: banned.pop(int(msg[6:]))
            except: chat.sendMsg("命令错了。。。")
            else: chat.sendMsg("删除成功！")
        elif senderTrip == OWNER:
            if command == "0addw ":
                if not (name:=msg[6:12]) in whiteList:
                    whiteList.append(name)
                    writeJson("userData.json", userData)
                    chat.sendMsg("添加特殊服务的家伙咯╰(￣▽￣)╮")
                else: chat.sendMsg("你要找的人并不在这里面(๑°ㅁ°๑)‼")
            elif command == "0delw ":
                if (name:=msg[6:12]) in whiteList:
                    whiteList.remove(msg[6:12])
                    writeJson("userData.json", userData)
                    chat.sendMsg("删除白名单用户成功๑乛◡乛๑")
                else: chat.sendMsg("你要找的人并不在这里面( ˃᷄˶˶̫˶˂᷅ )")
            elif command == "0igno ":
                if not (name:=namePure(msg[6:])) in ignored:
                    ignored.append(name)
                    writeJson("userData.json", userData)
                    chat.sendMsg(f"忽略{name}的消息咯~")
                else: chat.sendMsg("已经在了~")
            elif command == "0unig ":
                if (name:=namePure(msg[6:])) in ignored:
                    ignored.remove(name)
                    writeJson("userData.json", userData)
                    chat.sendMsg(f"恢复记录{name}的消息成功了~")
                else: chat.sendMsg("好消息是他/她的信息本来就被记录着~")
            elif command == "0chkr ":
                array = msg.split()
                if len(array) >= 2:
                    if ans:=answer.get(textPure(array[1])):
                        if len(array) == 2:
                            arr = []
                            for i, v in enumerate(ans): arr.append(f"{i}：{v}")
                            col = "\n".join(arr)
                            chat.sendMsg(f"/w {sender} 此问题的回答有：\n{col}")
                        else:
                            try: chat.sendMsg(f"/w {sender} {ans[int(array[2])]}")
                            except: chat.sendMsg(f"/w {sender} 当前问题还没有此序号，请重新确认后查询！")
                    else: chat.sendMsg(f"/w {sender} 当前问题还没有设置回答，请重新确认后查询（用`~`代表空格，`\\~`代表\\~）！")
                else: chat.sendMsg(f"/w {sender} 命令错误，请使用`chkr 问题 序号`的格式（序号可选，用`~`代表空格，`\\~`代表\\~）！")
            elif command == "0delr ":
                array = msg.split()
                if len(array) > 3: chat.sendMsg(f"/w {sender} 命令错误，请使用`0delr 问题 序号`的格式（序号可选，用`~`代表空格，`\\~`代表\\~）！")
                else: 
                    array[1] = textPure(array[1])
                    if len(array) == 2:
                        try:
                            del answer[array[1]]
                            chat.sendMsg(f"/w {sender} 已成功删除“{array[1]}”的所有回答！")
                        except: chat.sendMsg(f"/w {sender} 此问题还未设置答案，请重新确认后再次再试！")
                    else:
                        try: 
                            ans = answer[array[1]].pop(int(array[2]))
                            chat.sendMsg(f"/w {sender} 已成功删除回答：“{ans}”！")
                        except: chat.sendMsg(f"/w {sender} 此问题还未设置答案或序号错误，请重新确认后再次再试！")
            elif command == "0remb ":
                try: blackList.pop(int(msg[6:]))
                except: chat.sendMsg("命令错了。。。")
                else:
                    writeJson("userData.json", userData)
                    chat.sendMsg("好好好。")
            elif command == "0rems ":
                try: banned.pop(int(msg[6:]))
                except: chat.sendMsg("命令错了。。。")
                else:
                    writeJson("userData.json", userData)
                    chat.sendMsg("好好好。")
            elif command == "0setb ":
                sp = msg.split()
                try: mini, maxi = int(sp[1]), int(sp[2])
                except: chat.sendMsg("输入格式有误，请在0setb 后面用空格隔开，输入最小值和最大值两个整数！")
                else:
                    if (maxi-mini)<10: chat.sendMsg("两数的差别过小，请重新设置！")
                    else:
                        bombs[3], bombs[4] = mini, maxi
                        chat.sendMsg("设置成功！")
            elif command == "0relo ":
                if (ind:=msg[6:]) == "0":
                    with open(FILENAME, encoding="utf8") as f:
                        global data
                        data = json.load(f)
                        chat.sendMsg("开盒数据重读成功咯~")
                elif ind == "1":
                    with open("design.json", encoding="utf8") as f:
                        global designs
                        designs = json.load(f)
                        chat.sendMsg("脑瘫设计数据重读成功咯~")
                else:
                    with open("reply.json", encoding="utf8") as f:
                        rpy = json.load(f)
                        RANDLIS[6] = rpy[0]
                        RANDLIS[19] = rpy[1]
                        chat.sendMsg(f"{called}回复信息重读成功咯~")
            elif command == "0stfu ":
                try: thingsList[8] = int(msg[6:])
                except: pass
            elif msg == "0remake":
                p = sys.executable
                chat.ws.close()
                os.execl(p, p, *sys.argv)
    elif rans > 130 and allMsg:
        if rans == 133:
            chat.sendMsg(" "+random.choice(allMsg).split("：")[1])
        else:
            chat.sendMsg(random.choice(RANDLIS[2]).replace("sender", sender))
    else:
        for k, v in INLINE.items(): 
            if re.search(k, msg):
                chat.sendMsg(random.choice(v).replace("sender", sender))

def join(chat, joiner: str, color: str, result: dict):
    '''{'cmd': 'onlineAdd', 'nick': str, 'trip': str, 
        'uType': 'user', 'hash': str, 'level': 100, 
        'userid': iny, 'isBot': False, 'color': False or str, 
        'channel': str, 'time': int}'''
    chat.onlineUsers.append(joiner)
    trip, hash_ = result.get("trip"), result["hash"]
    msg = dic[trip] if trip in (dic:=userData["welText"]) else random.choice(RANDLIS[3]).replace("joiner", joiner)
    userColor[joiner], userHash[joiner], userTrip[joiner] = color, hash_, trip
    logs(f"{joiner}加入")
    if names := data.get(hash_):
        if not joiner in names:
            print(f"此hash曾用名：{'，'.join(names)}")
            data[hash_].append(joiner)
            writeJson(FILENAME, data)
    else:
        data[hash_] = [joiner]
        writeJson(FILENAME, data)
    for k, v in leftMsg.copy().items():
        if joiner == v[1]:
            chat.sendMsg(f"/w {joiner} {v[0]}曾在（{time.ctime(k)}）给您留言：{v[2]}")
            del leftMsg[k]
    if hash_ in banned:
        chat.sendMsg(f"/w {joiner} "+"$\\begin{pmatrix}qaq\\\\[999999999em]\\end{pmatrix}$")
        chat.sendMsg(f"~kick {joiner}")
    else: chat.sendMsg(msg)

def onSet(chat, result: dict):
    '''{'cmd': 'onlineSet', 'nicks': list, 'users': 
        [{'channel': str, 'isme': bool,  'nick': str,  'trip': str, 
            'uType': 'user', 'hash': str,  'level': 100, 'userid': int, 
            'isBot': False, 'color': str or False}*x],
        'channel': str, 'time': int}'''
    chat.onlineUsers = result["nicks"]
    for i in result["users"]:
        nick_ = i["nick"]
        userHash[nick_] = i["hash"]
        userColor[nick_] = i["color"]
        userTrip[nick_] = i["trip"]
        if names := data.get(i["hash"]):
            if not nick_ in names:
                data[i["hash"]].append(nick_)
        else:
            data[i["hash"]] = [nick_]
    writeJson(FILENAME, data)
    for i in PROLOGUE: chat.sendMsg(i)

def changeColor(chat, result:dict):
    '''{'nick': str, 'trip': str, 'uType': 'user', 
        'hash': str, 'level': 100, 'userid': int, 
        'isBot': False, 'color': str, 'cmd': 'updateUser', 
        'channel': str, 'time': int}'''
    userColor[result["nick"]] = result["color"]

def leave(chat, leaver: str):
    chat.onlineUsers.remove(leaver)
    logs(f"{leaver}离开")
    del userColor[leaver]
    del userHash[leaver]
    del userTrip[leaver]

def whispered(chat, from_: str, msg: str, result: dict):
    msg = msg[1:]
    command = msg[1:6]
    pre = f"/w {from_} "
    print(f"{from_}对你悄悄说：{msg}")
    if msg[0] == PREFIX:
        if command == "left ":
            if len(lis := msg.split()) < 3:
                chat.sendMsg(pre + "命令不正确！")
            elif lis[1] in chat.onlineUsers:
                chat.sendMsg(pre + f"{lis[1]}在线着呢，为什么还要留言啊喂~")
            elif not re.search(r"^@{0,1}[a-zA-Z0-9_]{1,24}$", lis[1]):
                chat.sendMsg(pre + "昵称不合法！")
            else:
                leftMsg[time.time()] = [from_, namePure(lis[1]), "".join(lis[2:])]
                chat.sendMsg(pre + f"{lis[1]}将会在加入时收到你的留言！~~如果那时我还在的话~~")
        elif result.get("trip") in whiteList:
            if command == "hash ": chat.sendMsg(pre + hashByName(namePure(msg[6:])))
            elif command == "hasn ": chat.sendMsg(pre + hashByName(namePure(msg[6:]), True))
    else: chat.sendMsg(pre + reply(from_, msg))

class HackChat:
    def __init__(self, channel: str, nick: str, passwd: str, color: str):
        self.nick = nick
        self.channel = channel
        self.ws = websocket.create_connection("wss://hack.chat/chat-ws", 
            sslopt={"cert_reqs": ssl.CERT_NONE})
        threading.Thread(target=self._clock).start()
        # 人工操作功能，可以让阿瓦娅和主人结合，@w@
        # threading.Thread(target=self._person_control).start()
        self._sendPacket({"cmd": "join", "channel": channel, 
            "nick": f"{nick}#{passwd}"})
        self.sendMsg(f"/color {color}")
    def sendMsg(self, msg:str):
        self._sendPacket({"cmd": "chat", "text": msg,})
    def _sendPacket(self, packet:dict):
        encoded = json.dumps(packet)
        self.ws.send(encoded)
    def move(self, old, new, chess):
        if CBL[0][new[0], new[1]] in [RED[4], BLACK[4]]:
            self.sendMsg(f"@{thingsList[1]} 获胜！恭喜！")
            self._endGame()
            return
        now = thingsList[1]
        thingsList[1] = redBlack[0] if thingsList[1] == redBlack[1] else redBlack[1]
        for i in CBL[0][:,3:6]:
            if (BLACK[4] in i) and (RED[4] in i) and set(i[list(i).index(RED[4])+1:list(i).index(BLACK[4])]) == {"&ensp;"}:
                self.sendMsg(f"@{thingsList[1]} 获胜！恭喜！")
                self._endGame()
                return
        CBL[0][old[0], old[1]] = "&ensp;"
        CBL[0][new[0], new[1]] = chess
        self._sendBoard()
        self.sendMsg(f"{now}挪动了{chr(old[0]+65)}{old[1]+1}的{chess}，轮到@{thingsList[1]}")
    def _endGame(self):
        thingsList[1] = None
        redBlack = [None, None]
        thingsList[0] = False
        CBL[0] = INIT.copy()
    def _sendBoard(self):
        mae = CLOLUMN+[f"|{n}|"+ "|".join(i) +"|" for i, n in zip(CBL[0], LETTERS)]
        self.sendMsg("\n".join(mae))
    def CCreply(self, sender: str, msg: str):
        if redBlack[1] and sender == thingsList[1] and (res := re.search(r"^([ABCDEFGHIJ])([123456789]) ([ABCDEFGHIJ])([123456789])$", msg.upper())):
            res = res.groups()
            old, new = [ord(res[0])-65, int(res[1])-1], [ord(res[2])-65, int(res[3])-1]
            goingChess, moveChess = CBL[0][new[0], new[1]], CBL[0][old[0], old[1]]
            if moveChess != "&ensp;":
                use = CBL[0][min(old[0], new[0])+1:max(old[0], new[0]), old[1]]
                use2 = CBL[0][old[0], min(old[1], new[1])+1:max(old[1], new[1])]
                if (not redBlack.index(sender) and not goingChess in RED and moveChess in RED) or (redBlack.index(sender) and not goingChess in BLACK and moveChess in BLACK):                    
                    if moveChess == RED[5] and (old[0] > 4 and abs(old[1] - new[1]) == 1 and old[0] == new[0] or new == [old[0]+1, old[1]]):
                            self.move(old, new, RED[5])
                    elif moveChess == BLACK[5] and (old[0] < 5 and abs(old[1] - new[1]) == 1 and old[0] == new[0] or new == [old[0]-1, old[1]]):
                            self.move(old, new, BLACK[5])
                    elif moveChess in [RED[6], BLACK[6]]:
                        if goingChess != "&ensp;":
                            if (new[0] == old[0] and len(use2[use2!="&ensp;"]) == 1) or (new[1] == old[1] and len(use[use!="&ensp;"]) == 1):
                                self.move(old, new, moveChess)
                            else: self.sendMsg("不符合行棋规则")
                        elif (new[0] == old[0] and not len(use2[use2!="&ensp;"])) or (new[1] == old[1] and not len(use[use!="&ensp;"])):
                            self.move(old, new, moveChess)
                        else: self.sendMsg("不符合行棋规则")
                    elif (moveChess in [RED[0], BLACK[0]]) and ((new[0] == old[0] and not len(use2[use2!="&ensp;"])) or ((new[1] == old[1]) and not len(use[use!="&ensp;"]))):
                            self.move(old, new, moveChess)
                    elif (moveChess in [RED[1], BLACK[1]]) and ((abs(old[0]-new[0]) == 2 and abs(old[1]-new[1]) == 1 and CBL[0][int(old[0]-(old[0]-new[0])/2), old[1]] == "&ensp;") or (abs(old[1]-new[1]) == 2 and abs(old[0]-new[0]) == 1 and CBL[0][old[0], int(old[1]-(old[1]-new[1])/2)] == "&ensp;")):
                            self.move(old, new, moveChess)
                    elif moveChess == RED[2] and (abs(old[0]-new[0]) == 2 and abs(old[1]-new[1]) == 2 and CBL[0][int(old[0]-(old[0]-new[0])/2), int(old[1]+(old[1]-new[1])/2)] == "&ensp;" and new[0] < 5) :
                            self.move(old, new, RED[2])
                    elif moveChess == BLACK[2] and (abs(old[0]-new[0]) == 2 and abs(old[1]-new[1]) == 2 and CBL[0][int(old[0]-(old[0]-new[0])/2), int(old[1]+(old[1]-new[1])/2)] == "&ensp;" and new[0] > 4) :
                            self.move(old, new, BLACK[2])
                    elif moveChess == RED[4] and (new[0] in [0, 1, 2]) and (new[1] in [3, 4, 5]) and ((old[0]==new[0] and abs(old[1]-new[1])==1) or (old[1]==new[1] and abs(old[0]-new[0])==1)):
                            self.move(old, new, RED[4])
                    elif moveChess == BLACK[4] and (new[0] in [7, 8, 9]) and (new[1] in [3, 4, 5]) and ((old[0]==new[0] and abs(old[1]-new[1])==1) or (old[1]==new[1] and abs(old[0]-new[0])==1)):
                            self.move(old, new, BLACK[4])
                    elif moveChess == RED[3] and (new[0] in [0, 1, 2]) and (new[1] in [3, 4, 5]) and abs(old[0]-new[0])==1 and abs(old[1]-new[1])==1:
                            self.move(old, new, RED[3])
                    elif moveChess == BLACK[3] and (new[0] in [7, 8, 9]) and (new[1] in [3, 4, 5]) and abs(old[0]-new[0])==1 and abs(old[1]-new[1])==1:
                            self.move(old, new, BLACK[3])
                    else: self.sendMsg(f"不符合{moveChess}的行棋规则")
                else: self.sendMsg("不能吃自己也不能用别人的棋子！")
            else: self.sendMsg("不能挪动空气！")
        elif msg == "开始游戏":
            if not thingsList[0]:
                if redBlack[1]:
                    self.sendMsg("游戏已经开始了，等到下局吧~")
                else:
                    thingsList[0] = True
                    redBlack[0] = sender
                    CBL[0] = INIT.copy()
                    self.sendMsg("游戏创建好了，快找人来加入吧！")
            else: self.sendMsg("已经开始了，快找对手来玩吧！")
        elif msg == "加入游戏":
            if not redBlack[0]:
                self.sendMsg("现在，还没有游戏哦~快使用 开始游戏 创建一个吧~")
            elif sender == redBlack[0]:
                self.sendMsg("你已经，加入过了哦~")
            elif redBlack[1]:
                self.sendMsg("游戏已经开始了，等到下局吧~")
            else:
                redBlack[1] = sender
                self._sendBoard()
                self.sendMsg(RULE)
                thingsList[1] = redBlack[0]
                self.sendMsg(f"@{redBlack[0]} 先手执红（绿？）（上方，简体），@{redBlack[1]} 后手执黑（下方，繁体）。开始了哦~")
        elif msg == "结束游戏" and sender in redBlack:
            if not thingsList[2]:
                thingsList[2] = sender
                self.sendMsg("结束游戏需要双方都发送。")
            elif thingsList[2] != sender:
                self._endGame()
                self.sendMsg(f"啊，虽然有点儿遗憾不过，既然{sender}说结束了的话就结束吧……发送开始游戏可以再次开始哦~")
                thingsList[2] = None
            else: self.sendMsg("结束游戏需要双方都发送。")
        elif msg == "帮助":
            self.sendMsg(CCMENU.replace("sender", sender))
        elif msg == "提问":
            self.sendMsg(random.choice(RANDLIS[5]).replace("sender", sender))
        elif msg == "数字炸弹":
            self.sendMsg(BOMBMENU.replace("sender", sender))
        else: self.sendMsg(reply(sender, msg))
    def _person_control(self):
        """和主人结合的过程好难啊，嗯~啊~还有一点~啊啊啊……"""
        while True:
            inputs = input()
            # 更新记忆，就算对我洗脑也没关系的……
            if inputs == "-reread":
                with open(FILENAME, encoding="utf8") as f:
                    global data
                    data = json.load(f)
                print("已重新读取数据")
            # 让我康康都有那些小可爱在线~
            elif inputs == "-users":
                print(",".join(self.onlineUsers))
            elif inputs[:4] == "-st ":
                thingsList[3] = eval(inputs[3:])
            else: self.sendMsg(inputs)
    def _clock(self):
        """既然整点了肯定就要刷一刷存在咯~"""
        while True:
            count = time.localtime(time.time())
            time.sleep(3600 - count.tm_min*60 - count.tm_sec + 28.5)
            hour = (count.tm_hour + 1) % 24
            if thingsList[3]: self.sendMsg(colorPic())
            if thingsList[5]: chat.sendMsg(f"已经{hour}点了啊。")
            if hour == 0: thingsList[9] = nowDay()
    def run(self):
        """开始营业咯，好兴奋好兴奋"""
        try:
            while True:
                result = json.loads(self.ws.recv())
                cmd = result["cmd"]
                rnick = result.get("nick")

                if (not thingsList[8]) or (thingsList[8] and result.get("trip") in whiteList): 
                    # print(result)
                    # 接收到消息！
                    if cmd == "chat":
                            msgGot(self, result["text"], rnick, result.get("trip"))
                    # 有新人来！
                    elif cmd == "onlineAdd": join(self, rnick, result.get("color", ""), result)
                    # 有人离开……
                    elif cmd == "onlineRemove": leave(self, rnick)
                    # 收到私信！
                    elif result.get("type") == "whisper" and result["text"][:3] != "You":
                        whispered(self, result["from"], "".join(result["text"].split(":")[1:]), result)
                    # 更换颜色（色色达咩）
                    elif cmd == "updateUser": changeColor(self, result)
                    # 话痨过头被服务器娘教训啦——
                    elif cmd == "warn":
                        if not "blocked" in result["text"]: print(result["text"])
                        else: time.sleep(2)
                    # 当然要用最好的状态迎接开始啦！
                    elif cmd == "onlineSet": onSet(self, result)
                else:
                    # 有新人来！
                    if cmd == "onlineAdd":
                        self.onlineUsers.append(rnick)
                        userColor[rnick], userHash[rnick], userTrip[rnick] = \
                            result.get("color"), result["hash"], result.get("trip")
                    # 有人离开……
                    elif cmd == "onlineRemove": leave(self, rnick)
                    elif cmd == "updateUser": changeColor(self, result)

        # 坏心眼……
        except BaseException as e:
            with open(f"traceback/{time.time()}.txt", "w", encoding="utf8") as f:
                f.write(traceback.format_exc())
            self.sendMsg(f"被玩坏了，呜呜呜……\n```\n{e}")
            self.run()

if __name__ == '__main__':
    chat = HackChat(channel, nick, passwd, color)
    chat.run()