#coding=utf-8
# 进源码啥都别说，先一起喊： 瓦门！
from static import *
from games import bomber, chess, poker, truth, uno, dryEye, countryKill
from money import bank, LoanStatus, oddEven, zhaJinHua, blackjack

# OOP, 但不完全OOP
class Awaya:
    def __init__(self, channel: str, nick: str, passwd: str="", color: str=""):
        self.nick = nick
        self.channel = channel
        self.passwd = passwd
        self.color = color

        self.funclist = [self.selfSelf, self.premade, self.afks, self.mainfunc]
        self.blacktemp = []
        self.peeper = Peeper()
        self.afker = Afker()
        self.users = Users()
        self.looker = Looker()
        self.motded = False
        
        # 从日志加载200条peep
        lines = []
        if os.path.exists(f"logs/{self.channel}_{sysList[3]}.txt"):
            with open(f"logs/{self.channel}_{sysList[3]}.txt", "r", encoding="utf8") as f:
                for line in f:
                    if "：" in line and not line.startswith(self.nick):
                        lines.append(line)
                    if len(lines) > 200:
                        lines.pop(0)
            for line in lines:
                array = line.split("：")
                _nick = array[0]
                if not ignore.check(nick=_nick):
                    self.peeper.push(_nick, "：".join(array[1:]))
        # 干活
        self._reconnect()
        threading.Thread(target=self._clock).start()
        threading.Thread(target=self._heartbeat).start()
        # threading.Thread(target=self._person_control).start() # 人工操作
    def _reconnect(self, pswd="", rand=False):
        try:
            self.ws.close()
        except:
            pass
        passwd = pswd or self.passwd
        if rand:
            nick = info["nick"] + "_" + str(random.randint(1,999))
        else:
            nick = info["nick"]
        while True:
            try:
                self.ws = websocket.create_connection(WSADD)
            except:
                time.sleep(30)
            else:
                self.oled = False # 是否进入频道
                self.nicks = []
                self.nick = nick

                self._sendPacket({"cmd": "join", "channel": self.channel, "nick": f"{nick}#{passwd}"}, True)
                return
    def _sendPacket(self, packet: dict, force: bool=False):
        if (not sysList[2]) or (self.users.getAttr(sysList[4], "trip") in whiteList) or force:
            if "text" in packet:
                text = packet["text"]
                if not text:
                    return
                if len(text) > 2999:
                    packet["text"] = toWeb(text)
            encoded = json.dumps(packet)
            try:
                self.ws.send(encoded)
            except websocket.WebSocketException:
                pass
    def _person_control(self):
        while self.ws.connected:
            inputs = input()
            try:
                if inputs == "-users":
                    print(", ".join(self.nicks))
                elif inputs == "-exit":
                    self.ws.close()
                    sys.exit()
                else:
                    self.sendMsg(inputs, True)
            except:
                pass
    # 心跳，检测是否被踢
    def _heartbeat(self):
        while True:
            time.sleep(sysList[6])
            try:
                self.whisper(self.nick, "w", True)
            except:
                pass
    # 骂谁布谷鸟
    def _clock(self):
        while True:
            bo_od = gmNow()
            hour = (bo_od.tm_hour + 1) % 24

            time.sleep(3600 - bo_od.tm_min*60 - bo_od.tm_sec)

            sysList[3] = nowDay()
            if sysList[1]:
                try:
                    self.sendMsg(CLOCKS[hour])

                    if hour > 12:
                        ampm = f"{hour - 13}-{hour - 12} p.m."
                    else:
                        ampm = f"{(hour - 1) % 12}-{hour} a.m."
                    chumo = MOTD[:]
                    chumo.append(f"Activity past hour / today ({ampm} / {MONTHS[bo_od.tm_mon]} {bo_od.tm_mday}):")
                    today, tohour = hourCount.get()
                    chumo.append(f"Messages: {tohour[0]}/{today[0]}")
                    chumo.append(f"Users: {tohour[1]}/{today[1]}")
                    self._sendPacket({"cmd": "setmotd", "motd": "\n".join(chumo)})
                    # MotdChat(self.channel, MOD, "\n".join(chumo)).rock()
                    # self.motded = True
                except:
                    pass
            if hour == 0:
                msgCount[sysList[3]] = {"count": 0, "users": []}
                hourCount.initDay()
            msgCount["hour"] = {"count": 0, "users": []}
            hourCount.initHour()

            self.sendMsg(bank.checkExpire())
            bank.check_aka_expire()
            bank.update_loans()
            left.check_expire()

    def newContext(self, user: dict, type_: Literal["chat", "whisper"]):
        self.user = user # 发送者的各项数据
        self.type_ = type_ # chat/whisper

        self.returns = False
        self.remake = False
        
        self.chat = []
        self.whispers: dict[str, list] = {}
        self.part = []
        self.history: list[dict] = []
    def addWhisper(self, to, text):
        if to not in self.whispers:
            self.whispers[to] = []
        self.whispers[to].append(text)
    def appText(self, text: str, type_: str="", **kwargs):
        if not text:
            return

        type_ = type_ or self.type_
        if type_ == "chat":
            self.chat.append(text)
        elif type_ == "whisper":
            to = kwargs.get("to") or self.user["nick"]
            kwargs["to"] = to
            self.addWhisper(to, text)
        else:
            self.part.append(dict({"text": text}, **kwargs))
        self.history.append({"text": text, "type": type_, **kwargs})
    def pop(self, num: int=1):
        for _ in range(num):
            operate = self.history.pop()
            if operate["type"] == "chat":
                self.chat.pop()
            elif operate["type"] == "whisper":
                self.whispers[operate["to"]].pop()
            else:
                self.part.pop()
    def runContext(self):
        self.sendMsg("\n".join(self.chat))
        for to, text in self.whispers.items():
            self.whisper(to, "\n".join(text))
        for kws in self.part:
            self.sendMsg(**kws)

    def sendMsg(self, text: str, cid: str="", force: bool=False):
        if cid:
            self._sendPacket({"cmd": "chat", "text": text, "customId": cid}, force)
        else:
            self._sendPacket({"cmd": "chat", "text": text}, force)
    def whisper(self, to: str, text: str, force: bool=False):
        self._sendPacket({"cmd": "whisper", "nick": to, "text": text}, force)
    def updateMsg(self, mode: str, text: str, customId: str):
        self._sendPacket({"cmd": "updateMessage", "mode": mode, "text": text, "customId": customId})
    # 孤独但不摇滚
    def rock(self):
        try:
            while self.ws.connected:
                sayori = json.loads(self.ws.recv())
                cmd = sayori["cmd"]
                sysList[4] = rnick = sayori.get("nick")
                if cmd == "captcha":
                    time.sleep(30)
                    self._reconnect(AUTH)
                elif cmd == "warn":
                    text = sayori["text"]
                    print(text)
                    self.log(text)
                    # 史上最不优雅的判断
                    if text == "Nickname taken":
                        self._reconnect(rand=True)
                    elif re.match(r"^You are (?:be|join|send)ing", text):
                        if not self.oled:
                            time.sleep(60)
                            self._reconnect()
                        else:
                            threading.Thread(target=self.ufts, args=(30,)).start()
                elif sayori.get("channel") and sayori.get("channel") != self.channel:
                    time.sleep(6)
                    self._reconnect()
                elif cmd == "chat":
                    self.onMsg(sayori["text"], rnick, sayori.get("trip"), "chat", customId=sayori.get("customId"), userid=sayori["userid"])
                elif cmd == "onlineAdd":
                    self.onJoin(rnick, sayori)
                elif cmd == "onlineRemove":
                    self.onLeave(rnick)
                elif cmd == "emote":
                    self.onEmote(sayori["nick"], sayori["text"])
                elif cmd == "info":
                    if sayori.get("type") == "whisper":
                        self.onWhisper(sayori["from"], sayori["text"].split(": ", 1)[1], sayori)
                    else:
                        self.onInfo(sayori["text"])
                elif cmd == "updateUser":
                    self.onColorChange(sayori)
                elif cmd == "updateMessage":
                    self.onMsgUpdate(sayori["mode"], sayori["text"], sayori["customId"], sayori["userid"])
                elif cmd == "onlineSet":
                    self.onSet(sayori)
        # 如果是ws连接问题则重连
        except (websocket.WebSocketException, BrokenPipeError, ConnectionResetError) as e:
            time.sleep(30)
            self._reconnect()
        # 我好贴心
        except KeyboardInterrupt:
            self.ws.close()
            sys.exit()
        # 否则报错
        except BaseException as e:
            error = traceback.format_exc(chain=False)
            if sysList[5]:
                self.sendMsg(f"被玩坏了，呜呜呜……\n```\n{error}\n```", True)
            else:
                filename = e.__class__.__name__ + ftime(now(), "%Y_%m_%d_%H_%M_%S")
                with open(f"traceback/{filename}.txt", "w", encoding="utf8") as f:
                    f.write(error)
                self.sendMsg(f"被玩坏了，呜呜呜……\n```\n{e}\n```\n具体请查看文件……", True)
                # time.sleep(6)
                # self._reconnect()
        self.rock()
    ## 玩
    def get_status(self) -> str:
        return "\n".join([
            "### Awaya v2.1.3",
            f"上次重启：{status_list[0]}",
            f"历史记录条数：{len(self.peeper.allMsg)}",
            "",
            "---",
            "#### 最近更新",
            "25.6.29: 历史上的今天",
            "25.6.27: 修复bug，增加小优化",
            "25.6.21: 增加存钱功能",
            "25.6.2: 修复bug，添加了这个",
        ])

    # 小憩一会
    def ufts(self, sec: int):
        sysList[2] = True
        sec = now() + sec
        if sec > sysList[7]:
            sysList[7] = sec
            while sysList[2]:
                if now() > sec:
                    sysList[2] = False
                elif sysList[7] != sec:
                    break
                else:
                    time.sleep(1)
    # 日志
    def log(self, text):
        with open(f"logs/{self.channel}_{sysList[3]}.txt", "a+", encoding="utf8") as f:
            f.write(text + "\n")
    # 当前频道用户
    def listNow(self) -> str:
        broken = []
        for user in self.nicks:
            if user == self.nick:
                continue
            if self.users.getAttr(user, "trip"):
                trip = ", " + self.users.getAttr(user, "trip")
            else:
                trip = ""
            broken.append(f"{user}{trip}, {self.users.getAttr(user, 'hash')}")
        return "\n".join(broken)
    # 发言与封禁词rl
    def rl(self, sender: str, msg: str, score: int=0):
        hash_ = self.users.getAttr(sender, "hash")
        if msgRl.frisk(hash_, 1+len(msg)/512 + score):
            msgRl.records[hash_]["score"] = msgRl.threshold / 2
            self.kick(sender)
        for word in banWords:
            if re.search(word, msg) and wordRl.frisk(hash_, 1):
                wordRl.records[hash_]["score"] = wordRl.threshold / 2
                self.kick(sender)
    # 踢
    def kick(self, *nicks, assert_: bool=False) -> bool:
        kkNicks = []
        for nick in nicks:
            if nick == self.nick or self.users.getAttr(nick, "trip") in whiteList:
                if assert_:
                    return False
                else:
                    continue
            else:
                self.blacktemp.append(nick)
                kkNicks.append(nick)
        if kkNicks:
            self.sendMsg(KICK + " " + " ".join(kkNicks), force=True)
        return True
    ## 多线程updatemsg
    def updateFunc(self, func, cid, *args):
        threading.Thread(target=lambda: self.updateMsg("overwrite", func(*args), cid)).start()

    def selfSelf(self, msg: str, sender: str, trip: str, type_: str, **kwargs):
        # 日志, 添加look与seen
        if type_ != "whisper":
            self.log(f"{sender}：{msg}")
            sawer.add(sender, trip, msg)
            self.looker.add(sender)
        elif sender != self.nick:
            self.log(f"{sender}私信:{msg}")
        # stfu
        if sysList[2] and (self.users.getAttr(sysList[4], "trip") not in whiteList):
            return
        # 处理自己
        if sender == self.nick:
            if sysList[8]:
                sysList[8] = False
            else:
                self.returns = True
    def premade(self, msg: str, sender: str, trip: str, type_: str, **kwargs):
        user = self.users.getUser(sender)
        if type_ != "whisper":
            # rl
            self.rl(sender, msg)
            # 加peep
            if not ignore.check(**user):
                self.peeper.push(sender, msg, kwargs.get("customId"), kwargs.get("userid"))
                hourCount.add(sender)
            # 随机复读
            if 2 < len(msg) and len(msg) < 256:
                sysList[9].append(msg)
        elif trip not in whiteList:
            # 私信rl更严
            # self.rl(sender, msg, len(msg)/256 + 2)
            self.rl(sender, msg)
        try:
            command = msg.split(" ")[0]
        except:
            command = "" # 服了
        if msg[0] == WHTFIX and trip in whiteList:
            command = command[1:]
            if command == "help":
                cmd = msg[6:]
                if not msg[5:]:
                    self.appText(f"{MENUMIN}", "whisper")
                elif cmd in WTCOMMANDS:
                    self.appText("我是占位符awa\n" + WTCOMMANDS[cmd], "whisper")
                elif cmd in COMMANDS:
                    self.appText("我是占位符awa\n" + COMMANDS[cmd], "whisper")
                else:
                    self.appText(random.choice(ERRORMSG))
            elif command == "addb":
                bloods = msg.split()
                if len(bloods) < 2:
                    self.appText("缺少参数")
                elif len(bloods) < 3:
                    hash_ = self.users.getAttr(namePure(msg[6:]), "hash")
                    if hash_ is None:
                        self.appText("参数错误")
                    else:
                        self.appText(black.add("hash", hash_))
                else:
                    self.appText(black.add(bloods[1], namePure(bloods[2])))
            elif command == "delb":
                bloods = msg.split()
                if len(bloods) < 2:
                    self.appText("缺少参数")
                elif len(bloods) < 3:
                    hash_ = self.users.getAttr(namePure(msg[6:]), "hash")
                    if hash_ is None:
                        self.appText("参数错误")
                    else:
                        self.appText(black.delete("hash", hash_))
                elif len(bloods) > 3:
                    for attr in bloods[2:]:
                        black.delete(bloods[1], namePure(attr))
                    self.appText("阿瓦一下")
                else:
                    self.appText(black.delete(bloods[1], namePure(bloods[2])))
            elif command == "igno":
                bloods = msg.split()
                if len(bloods) < 2:
                    self.appText("缺少参数")
                elif len(bloods) < 3:
                    self.appText(ignore.add("nick", namePure(msg[6:])))
                else:
                    self.appText(ignore.add(bloods[1], namePure(bloods[2])))
            elif command == "unig":
                bloods = msg.split()
                if len(bloods) < 2:
                    self.appText("缺少参数")
                elif len(bloods) < 3:
                    self.appText(ignore.delete("nick", namePure(msg[6:])))
                elif len(bloods) > 3:
                    for attr in bloods[2:]:
                        ignore.delete(bloods[1], namePure(attr))
                    self.appText("阿瓦一下")
                else:
                    self.appText(ignore.delete(bloods[1], namePure(bloods[2])))
            elif command == "bans":
                bloods = msg.split()
                if len(bloods) < 2:
                    return self.appText("缺少参数")
                elif len(bloods) < 3:
                    hash_ = self.users.getAttr(namePure(msg[6:]), "hash")
                    if hash_ is None:
                        return self.appText("参数错误")
                    else:
                        bloods[1] = "hash"
                        bloods.append(hash_)
                attr = namePure(bloods[2])
                nicks = self.users.attrsGet(bloods[1], attr)
                if nicks:
                    assert_ = self.kick(*nicks, assert_=True)
                    if assert_:
                        self.appText(banned.add(bloods[1], attr))
                    else:
                        self.appText("6")
                else:
                    self.appText(banned.add(bloods[1], attr))
            elif command == "uban":
                bloods = msg.split()
                if len(bloods) < 2:
                    self.appText("缺少参数")
                elif len(bloods) < 3:
                    self.appText(banned.delete("hash", msg[6:]))
                elif len(bloods) > 3:
                    for attr in bloods[2:]:
                        banned.delete(bloods[1], namePure(attr))
                    self.appText("阿瓦一下")
                else:
                    self.appText(banned.delete(bloods[1], namePure(bloods[2])))
            elif command == "repl":
                _000 = msg.split(" ")
                if len(_000) < 3 or not _000[1]:
                    self.appText(f"命令错误，请使用`{WHTFIX}repl 提问 回答`的格式(‾◡◝)")
                else:
                    ans = " ".join(_000[2:])
                    quest = textPure(_000[1])
                    if quest not in answer:
                        answer[quest] = [ans]
                    else:
                        answer[quest].append(ans)
                    self.appText(f"添加成功(☆▽☆)")
                    writeJson("answer", answer)
            elif command == "kill":
                self.kick(*msg[6:].split())
            elif command == "gnkey":
                key = getStr()
                keys[trip] = key
                writeJson("userData", userData)
                self.appText("\n".join([
                    "占位awa",
                    f"`{key}`是您的新key，可用于在无识别码状态私信使用`{PREFIX}decp <key>`关闭验证码",
                    "请妥善保管，如遗失，可使用此识别码执行此命令重新生成"
                ]), "whisper")
            elif command == "unwe":
                trip = msg[6:12]
                if trip not in welcome:
                    self.appText("还没有设置欢迎语")
                else:
                    del welcome[trip]
                    writeJson("userData", userData)
                    self.appText("删除欢迎语成功")
            elif command == "encap":
                self.appText(".m enablecap", "part")
            elif command == "decap":
                self.appText(".m disablecap", "part")
            elif command == "lock":
                self.appText(".m lockroom", "part")
            elif command == "unlock":
                self.appText(".m unlockroom", "part")
            elif command == "setrl":
                op = msg.split()
                if op[-1] == "word":
                    setRl = wordRl
                elif op[-1] == "join":
                    setRl = joinRl
                elif op[-1] == "setu":
                    setRl = setuRl
                else:
                    setRl = msgRl
                try:
                    setRl.halflife = int(op[1])
                    setRl.threshold = int(op[2])
                except:
                    pass
                self.appText(f"halflife: {setRl.halflife}, threshold: {setRl.threshold}")
            elif command == "addw":
                word = msg[6:]
                if word in banWords:
                    self.appText("已经有这个封禁词了~")
                else:
                    banWords.append(word)
                    writeJson("userData", userData)
                    self.appText("好好好，又进去了一个。")
            elif command == "delw":
                word = msg[6:]
                if word not in banWords:
                    self.appText("没有这个封禁词了~")
                else:
                    banWords.remove(word)
                    writeJson("userData", userData)
                    self.appText("好好好，删除成功。")
            elif command == "list":
                lChannel = msg[6:]
                if not lChannel:
                    self.appText("-_-#")
                elif lChannel == self.channel:
                    self.appText(self.listNow())
                elif type_ == "whisper":
                    self.appText("暂不支持私信, 果咩捏")
                else:
                    # List? kita kita~
                    cid = getStr(6)
                    self.appText("桥豆麻袋", "part", cid=cid)
                    kita = ListChat(lChannel, cid, self.passwd)
                    self.updateFunc(kita.rock, cid)
            elif command == "room":
                lChannel = msg[6:] or self.channel
                cid = getStr(6)
                self.appText("桥豆麻袋", "part", cid=cid)
                kita = RoomChat(lChannel, cid, self.nick)
                self.updateFunc(kita.rock, cid)
            elif command == "bomb":
                sp = msg.split()
                try:
                    mini, maxi = int(sp[1]), int(sp[2])
                except:
                    return self.appText(f"输入格式有误，请在{WHTFIX}bomb 后面用空格隔开，输入最小值和最大值两个整数！")
                if (maxi-mini) < 1:
                    self.appText("两数的差别过小，请重新设置！")
                else:
                    bomber.bombs[3], bomber.bombs[4] = mini, maxi
                    self.appText("设置成功！")        
            elif command == "fun":
                try:
                    sysList[10] = int(msg.split()[1])
                except (IndexError, TypeError):
                    self.appText(f"参数有误，请输入数字")
                else:
                    self.appText("设置随机拟人概率成功！")
            elif command == "regst":
                array = msg.split(" ")
                if len(array) == 1:
                    hlg = []
                    for trip_, name in bank.wait.items():
                        hlg.append(f"{name}({trip_})")
                    self.appText(" ".join(hlg) or "当前没有请求")
                elif array[1] == "all":
                    for trip_ in bank.wait.copy():
                        bank.register(trip_)
                    self.appText("耶！！！")
                elif array[1] == "-all":
                    bank.wait.clear()
                    bank.save()
                    self.appText("欸——")
                elif array[1] == "-":
                    for trip_ in array[2:]:
                        del bank.wait[trip_]
                    bank.save()
                    self.appText("欸……")
                else:
                    for trip_ in array[1:]:
                        if trip_ in bank.wait:
                            bank.register(trip_)
                    self.appText("耶！")
        elif msg[0] == OWNFIX and trip in OWNER:
            command = command[1:]
            if command == "help":
                self.appText(OWNMENU, "whisper")
            elif command == "addw":
                trip_ = msg[6:12]
                if trip_ not in whiteList:
                    whiteList.append(trip_)
                    writeJson("userData", userData)
                    self.appText("添加特殊服务的家伙咯╰(￣▽￣)╮")
                else:
                    self.appText("你要找的人并不在这里面(๑°ㅁ°๑)‼")
            elif command == "delw":
                trip_ = msg[6:12]
                if trip_ not in whiteList:
                    self.appText("你要找的人并不在这里面( ˃᷄˶˶̫˶˂᷅ )")
                else:
                    whiteList.remove(trip_)
                    if trip_ in keys:
                        del keys[trip_]
                    writeJson("userData", userData)
                    self.appText("删除白名单用户成功๑乛◡乛๑")
            elif command == "kkal":
                try:
                    chocol = int(msg[6:])
                    self.kick(*self.nicks[-chocol:])
                except ValueError:
                    self.appText("寄了吧你")
            elif command == "chkr":
                _17 = msg.split()
                if len(_17) < 2:
                    self.appText("\n".join(answer.keys()), "whisper")
                else:
                    ans = answer.get(textPure(_17[1]))
                    if not ans:
                        self.appText(f"当前问题还没有设置回答，请重新确认后查询（用`~`代表空格，`\\~`代表\\~）！", "whisper")
                    else:
                        if len(_17) == 2:
                            _17 = []
                            for i, v in enumerate(ans):
                                _17.append(f"{i}：{v[:55]}")
                            col = "\n".join(_17)
                            self.appText(f"此问题的回答有：\n{col}", "whisper")
                        else:
                            try:
                                self.appText(f"{ans[int(_17[2])]}", "whisper")
                            except:
                                self.appText(f"当前问题还没有此序号，请重新确认后查询！", "whisper")
            elif command == "tstr":
                ans = textPure(msg[6:])
                if ans:
                    for k, v in answer.items():
                        if re.search(k, ans):
                            self.appText(k, "whisper")
                            break
                    else:
                        self.appText(f"当前问题还没有设置回答，请重新确认后查询（用`~`代表空格，`\\~`代表\\~）！", "whisper")
            elif command == "delr":
                kilo = msg.split()
                if len(kilo) < 2 or len(kilo) > 3:
                    self.appText(f"命令错误，请使用`{OWNFIX}delr 问题 序号`的格式（序号可选，用`~`代表空格，`\\~`代表\\~）！", "whisper")
                else:
                    kilo[1] = textPure(kilo[1])
                    if len(kilo) == 2:
                        try: del answer[kilo[1]]
                        except: self.appText(f"此问题还未设置答案，请重新确认后再次再试！", "whisper")
                        else: self.appText(f"已成功删除“{kilo[1]}”的所有回答！", "whisper")
                    else:
                        try: ans = answer[kilo[1]].pop(int(kilo[2]))
                        except: self.appText(f"此问题还未设置答案或序号错误，请重新确认后再次再试！", "whisper")
                        else: self.appText(f"已成功删除回答：“{ans}”！", "whisper")
                    writeJson("answer", answer)
            elif command == "relo":
                ind = msg[6:]
                if ind == "long":
                    self.peeper.longlong = []
                elif ind == "mean":
                    sysList[9] = []
                elif ind == "left":
                    left.msg = {}
                    writeJson("userData", userData)
                elif ind == "peep":
                    self.peeper.allMsg = []
                elif ind == "afks":
                    self.afker.clear()
                elif ind == "bans":
                    banned.clear()
                elif ind == "black":
                    black.clear()
                elif ind == "ignore":
                    ignore.clear()
                else:
                    return
                self.appText("成功")
            elif command == "stfu":
                sysList[2] = not sysList[2]
                self.appText(f"阿瓦了这下: {sysList[2]}")
            elif command == "prtt":
                _4w4 = msg[6:].split()
                if len(_4w4) != 2:
                    self.appText("参数不正确")
                else:
                    protect[_4w4[0]] = _4w4[1]
                    self.appText(f"为昵称{_4w4[0]}绑定识别码{_4w4[1]}成功")
                    writeJson("userData", userData)
            elif command == "delp":
                name = namePure(msg[6:])
                if name not in protect:
                    self.appText("此昵称还没有被保护")
                else:
                    self.appText(f"删除成功，被绑定的识别码有{protect[name]}")
                    del protect[name]
                    writeJson("userData", userData)
            elif command == "remake":
                self.remake = True
            elif command == "atrm":
                sysList[5] = not sysList[5]
                self.appText(f"阿瓦了这下: {sysList[5]}")
            elif command == "beat":
                try:
                    sysList[6] = int(msg[6:])
                except:
                    self.appText("QAQ")
                else:
                    self.appText("设置成功~")
            elif command == "send":
                sysList[8] = True
                self.appText(msg[6:], "part")
            elif command == "eval":
                try:
                    if msg[6:7] == "*":
                        self.appText(str(eval(msg[7:])))
                    else:
                        exec(msg[6:])
                except BaseException as e:
                    self.appText("错误！\n```\n" + traceback.format_exc(chain=False) + "\n```")
            # elif command == "motd":
            #     userData["motd"] = msg[6:]
            #     writeJson("userData", userData)
            #     MotdChat(self.channel, MOD).rock()
        # 检查黑名单
        if black.check(**user) or sender in self.blacktemp:
            self.returns = True
        # 检查留言
        self.appText(left.check(**user), "whisper")
    # 古兰枝掌管afk的神
    def afks(self, msg: str, sender: str, trip: str, type_: str, **kwargs):
        if type_ != "whisper":
            self.appText(self.afker.check(sender))
            if re.match(r"^afk\b", msg):
                self.appText(self.afker.add(sender, msg[4:44] or "AFK"))
            if "@" in msg:
                self.appText(self.afker.alert(msg))
    def mainfunc(self, msg: str, sender: str, trip: str, type_: str, **kwargs):
        msg_list = msg.split(" ")
        command = msg_list[0]
        icb9 = random.randint(1, 1000)

        if msg[0] == PREFIX:
            command = command[1:]            
            if command == "help":
                kc = msg.split()
                if len(kc) < 2:
                    self.appText(f"{MENUMIN}", "whisper")
                elif len(kc) > 6:
                    self.appText("太多了，装不下了~")
                else:
                    result = []
                    for cmd in kc:
                        if cmd in COMMANDS:
                            result.append(COMMANDS[cmd])
                    if result:
                        self.appText("我是占位符awa\n" + "\n".join(result), "whisper")
                    else:
                        self.appText(random.choice(ERRORMSG))
            elif command == "status":
                self.appText(self.get_status())
            elif command == "hash":
                self.appText(hasher.hashByName(namePure(msg[6:])))
            elif command == "hasn":
                nick = namePure(msg[6:])
                if nick in self.nicks:
                    self.appText(hasher.hashByCode(self.users.getAttr(nick, "hash")))
                else:
                   self.appText("此人当前不在线( ⊙ o ⊙ )")
            elif command == "code":
                self.appText(hasher.hashByCode(msg[6:]))
            elif command == "colo":
                name = namePure(msg[6:])
                if name not in self.nicks:
                    self.appText("没有这个用户(╰_╯)#")
                else:
                    color = self.users.getAttr(name, "color")
                    if color:
                        self.appText(color)
                    else:
                        self.appText("RESET")
            elif command == "left":
                mauver = re.sub(r"(```|~~~)", r"\\\1", msg).split(" ")
                text = " ".join(mauver[2:])
                if len(mauver) < 3:
                    self.appText("命令不正确！")
                elif mauver[1].startswith("*"):
                    self.appText(left.add("trip", mauver[1][1:], sender, trip, text))
                else:
                    self.appText(left.add("nick", namePure(mauver[1]), sender, trip, text))
            elif command == "peep":
                if msg[6:7] == "*":
                    if not trip:
                        self.appText("当前还没有识别码")
                    elif not msg[7:]:
                        try:
                            del subscribe[trip]
                        except:
                            pass
                        else:
                            self.appText(f"为#{trip} 取消订阅成功")
                    else:
                        subscribe[trip] = msg[7:]
                        self.appText(f"为#{trip} 订阅成功")
                else:
                    self.appText(self.peeper.getPeep(msg[6:]), "whisper")
            elif command == "welc":
                if not msg[5:]:
                    if trip not in welcome:
                        self.appText("你还没有设置欢迎语！")
                    else:
                        del welcome[trip]
                        writeJson("userData", userData)
                        self.appText(f"为识别码{trip}清除欢迎语成功了！")
                elif not trip:
                    self.appText("您当前还没有识别码，请重进并在昵称输入界面使用==昵称#密码==设置一个！")
                else:
                    welcome[trip] = msg[6:]
                    writeJson("userData", userData)
                    self.appText(f"为识别码{trip}设置欢迎语成功了！")
            elif command == "seen":
                light = msg.split()
                if len(light) < 2:
                    self.appText("参数呢！！！")
                elif light[1][0:1] == "*":
                    self.appText(sawer.get(namePure(light[1][1:]), "trip"))
                else:
                    self.appText(sawer.get(namePure(light[1]), "nick"))
            elif command == "look":
                name = namePure(msg[6:])
                self.appText(self.looker.get(name))
            elif command == "long":
                try:
                    index = int(msg[6:])
                    self.appText(":\n" + self.peeper.getLong(index), "whisper")
                except:
                    self.appText("索引有误！")
            # 什么傻逼功能
            elif command == "Lori":
                lori = msg[6:7]
                if lori in ["l", "I", "1", "|", "丨"]:
                    if lori == "l":
                        self.appText(f"您输入的“{lori}”是字母表的第十二个字母, “L”的小写。")
                    elif lori == "I":
                        self.appText(f"您输入的“{lori}”是字母表的第九个字母, “i”的大写。")
                    elif lori == "1":
                        self.appText(f"您输入的“{lori}”是最小的正整数, 3-2的结果。")
                    elif lori == "|":
                        self.appText(f"您输入的“{lori}”是我喜欢你, 按住Shift+\\\\可以打出。")
                    elif lori == "丨":
                        self.appText(f"您输入的“{lori}”是一个汉字, 一般地, 读作gun3。")
                elif lori in ["0", "O"]:
                    if lori == "0":
                        self.appText(f"您输入的“{lori}”是最小的自然数, 1-1的结果。")
                    elif lori == "O":
                        self.appText(f"您输入的“{lori}”是字母表的第十五个字母, “o”的大写。")
                else:
                    self.appText("不知道您大人想干嘛呢")
            elif command == "decp":
                for tp, ky in keys.items():
                    if msg[6:] == ky:
                        self.appText(tp, "part")
                        self.appText(".m disablecap", "part")
            elif command == "list":
                cmd = msg[6:]
                if cmd in cmdList:
                    self.appText(cmdList[cmd]())
                elif cmd == "afks":
                    self.appText(self.afker.list())
                elif cmd == self.channel:
                    self.appText(self.listNow())
                else:
                    self.appText("早？")
            elif command == "setu":
                if setuRl.frisk("*", 1):
                    self.appText("rl乐，别涩涩了")
                elif type_ == "whisper":
                    self.appText("别私信乐")
                elif not sysList[2]:
                    cid = getStr(6)
                    self.appText("少女祈祷中. . .", "part", cid=cid)
                    self.updateFunc(colorPic, cid, msg[6:])
            elif command == "prime":
                try:
                    digit = msg[7:20]
                    eq = "\\*".join(getPrime(int(digit), []))
                    self.appText(f"{digit}={eq}")
                except ValueError:
                    self.appText("请输入一个***正整数***啊啊啊啊(￢_￢)")
            elif command == "hug":
                to = namePure(msg[5:])
                self.appText(f"/me @{sender} gives @{to} a hug.", "part")
            elif command == "shoot":
                to = namePure(msg[7:])
                if random.random() > 0.15:
                    through = random.choice(BODY_PARTS)
                    self.appText(f"/me @{sender} shoots @{to} through the {through}!", "part")
                else:
                    self.appText(f"/me @{sender} shoots @{to}, but missed!", "part")
            elif command == "uwu":
                self.appText("/uwuify " + sender, "part")
                self.appText("😸！")
            elif command == "kkme":
                nick = msg[6:]
                trip_ = self.users.getAttr(nick, "trip")
                if not trip:
                    self.appText("你没有识别码！")
                elif not nick:
                    for kcin, canyu in self.users:
                        if kcin != sender and canyu["trip"] == trip:
                            self.sendMsg(KICK + " " + kcin)
                            break
                elif trip == trip_:
                    self.sendMsg(KICK + " " + nick)
                else:
                    self.appText("识别码不符！")
            
            # 金钱系统
            elif command == "aka":
                trip_ = msg[5:11]
                if bank.get(trip):
                    related = bank.getRelated(trip)
                    if not trip_:
                        abraca = "，".join(related)
                        self.appText(f"当前关联识别码有：{abraca}")
                    elif not verify("trip", trip_):
                        self.appText("阿瓦阿瓦啊！")
                    elif trip_ in related:
                        if isinstance(bank.bank.get(trip_), dict):
                            self.appText(f"?!")
                        else:
                            bank.deregister(trip_)
                            self.appText(f"已将{trip_}取消关联！")
                    else:
                        self.appText(bank.aka_register(trip, trip_))
                elif trip in bank.akas and verify("trip", trip_):
                    self.appText(bank.aka_register(trip, trip_))
                else:
                    self.appText("你还没有银行！")
            elif not trip:
                self.appText("你还没有识别码，请重进使用==昵称#识别码==设置")
            elif command == "regst":
                valid = msg[7:31].replace("\n", "")
                self.appText(bank.request(trip, valid or sender))
            elif not bank.get(trip):
                self.appText(f"你还没有银行！使用=={PREFIX}regst==注册一个！")

            elif command == "sign":
                self.appText(bank.sign(trip))
            elif command == "bank":
                if not msg[6:]:
                    self.appText(bank.format(trip))
                else:
                    self.appText(bank.format(msg[6:]))
            elif command == "rank":
                self.appText(bank.rank())
            elif command == "v":
                juhee = msg_list[1:]
                if not juhee:
                    self.appText("参数错误！")
                elif len(juhee) == 1:
                    try:
                        num = float(juhee[0])
                    except:
                        self.appText("参数错误！")
                    else:
                        lucky = bank.random()
                        bank.give(trip, lucky, num)
                        self.appText(f"已转给**{bank.getAttr(lucky, 'name')}**({lucky}) {num}豆！")
                else:
                    trip_ = juhee[0]
                    try:
                        num = float(juhee[1])
                        assert bank.get(trip_)
                    except:
                        self.appText("参数错误！")
                    else:
                        bank.give(trip, trip_, num)
                        self.appText(f"已转给**{bank.getAttr(trip_, 'name')}**({trip_}) {num}豆！")
            elif command == "packet":
                headache = msg.split(" ")[1:]
                if not headache:
                    self.appText(bank.checkPackets())
                elif headache[0] in bank.packets:
                    self.appText(bank.robPacket(trip, headache[0]))
                else:
                    try:
                        money = int(headache[0])
                        people = int(headache[1])
                    except:
                        self.appText("参数错误！")
                    else:
                        self.appText(bank.sendPacket(trip, money, people))

            elif command == "loans":
                if not msg[7:]:
                    self.appText(bank.format_loans(trip))
                else:
                    self.appText(bank.format_loans(msg[7:]))
            elif command == "borrow":
                if len(msg_list) < 3:
                    self.appText("参数不够")
                    return
                if len(msg_list) < 4:
                    msg_list.insert(1, bank.offering_box)
                elif not bank.get(msg_list[1]):
                    self.appText("不存在这个账户")
                    return
                try:
                    num = float(msg_list[2])
                    days = int(msg_list[3])
                except:
                    self.appText("参数有误")
                else:
                    self.appText(bank.borrow(trip, num, days, msg_list[1]))
            elif command == "lend":
                try:
                    interest = float(msg_list[2])
                except:
                    self.appText("参数有误")
                else:
                    self.appText(bank.lend(trip, msg_list[1], interest))
            elif command == "reject":
                if len(msg_list) < 2:
                    self.appText("参数不足")
                    return
                if msg_list[1] == "all":
                    for id_, loan in bank.get_loans(trip, 2):
                        if loan["status"] == LoanStatus.WAITING:
                            bank.reject(trip, id_)
                    self.appText("爽了")
                    return
                if msg_list[1] == "all!":
                    for id_, loan in bank.get_loans(trip, 2):
                        if loan["status"] == LoanStatus.OVERDUE:
                            bank.reject(trip, id_)
                    self.appText("爽了")
                    return
                try:
                    num = float(msg_list[2])
                except:
                    self.appText(bank.reject(trip, msg_list[1]))
                else:
                    self.appText(bank.reject(trip, msg_list[1], num))

            elif command == "repay":
                try:
                    if len(msg_list) < 3:
                        loan_id = ""
                        num = float(msg_list[1])
                    else:
                        loan_id = msg_list[1]
                        num = float(msg_list[2])
                except:
                    self.appText("参数有误")
                else:
                    self.appText(bank.repay(trip, loan_id, num))
            elif command == "store":
                try:
                    num = float(msg_list[1])
                except:
                    self.appText("参数有误")
                else:
                    self.appText(bank.store(trip, num))

        elif namePure(msg) == self.nick:
            if icb9 > 990:
                self.appText(random.choice(replys[1]).replace("sender", sender))
            elif icb9 > 666:
                self.appText(f"So, {PREFIX}help might, uh, well, nevermind. . .",)
            else:
                self.appText(random.choice(replys[0]).replace("sender", sender))
        elif msg.startswith(f"@{self.nick} "):
            msg = msg[len(self.nick)+2:]
            if msg == "提问":
                self.appText(random.choice(replys[3]).replace("sender", sender))
            elif type_ != "whisper":
                self.appText(reply(sender, msg))
            else:
                self.appText(reply(sender, msg, False))
        elif msg == "菜单":
            self.appText(f"{MENUMIN}", "whisper")

        elif msg[0] == "r" and type_ != "whisper":
            if msg == "r":
                self.appText(truth.truthDo(sender, self.users.getAttr(sender, "hash")))
            elif msg[:2] == "r ":
                sakura = msg.split()[1:]
                try:
                    beR = int(sakura[0])
                except:
                    akashi = random.randint(1, 1000)
                else:
                    try:
                        r2 = int(sakura[1])
                    except:
                        r2 = 1
                    if beR > r2:
                        akashi = random.randint(r2, beR)
                    else:
                        akashi = random.randint(beR, r2)
                self.appText(loliNum(akashi))
            elif command == "rollen":
                digit = msg[7:25]
                try: self.appText(rollTo1(int(digit)))
                except ValueError as e: self.appText(rollTo1(1000))
            elif command == "rprime":
                digit = msg[7:20]
                try:
                    dig = random.randint(1, int(digit))
                    if dig > 0:
                        eq = "\\*".join(getPrime(dig, []))
                        self.appText(f"{dig}={eq}")
                    else:
                        raise ValueError
                except ValueError as e:
                    digit = str(random.randint(1, 1000))
                    eq = "\\*".join(getPrime(int(digit), []))
                    self.appText(f"{digit}={eq}")
        elif msg.startswith("cc ") and type_ != "whisper":
            self.appText(chess.main(sender, msg[3:].strip()))
        elif msg.startswith("p ") and type_ != "whisper":
            poker.main(self, sender, msg[2:].replace("。", ".").strip())
        elif msg.startswith("t ") and type_ != "whisper":
            self.appText(truth.main(msg[2:]).strip())
        elif msg.startswith("u ") and type_ != "whisper":
            uno.main(self, sender, msg[2:].replace("。", ".").replace("？！", "?!").strip())
        elif msg.startswith("b ") and type_ != "whisper":
            bomber.main(self, sender, msg[2:].strip())
        elif msg.startswith("s ") and type_ != "whisper":
            countryKill.main(self, sender, msg[2:].replace("。", ".").strip())
        elif msg.startswith("g ") and type_ != "whisper":
            dryEye.main(self, sender, msg[2:].replace("。", ".").strip())
        elif msg.startswith("oe "):
            oddEven.main(self, msg[3:].strip(), type_)
        elif msg.startswith("z ") and type_ != "whisper":
            zhaJinHua.main(self, sender, msg[2:].strip())
        elif msg.startswith("bj ") and type_ != "whisper":
            blackjack.main(self, sender, msg[3:].strip())
        
        # 古老的梗
        elif namePure(msg) == sender:
            self.appText("why did you call yourself")
        elif msg.lower() in lineReply and type_ != "whisper":
            call = lineReply[msg.lower()]
            if hasattr(call, "__call__"):
                self.appText(call())
            else:
                self.appText(random.choice(call).replace("sender", sender))
        elif icb9 > sysList[10]:
            fcjz = random.randint(1, 10)
            if fcjz > 8:
                self.appText(random.choice(KAWAII).replace("sender", sender))
            elif fcjz > 5:
                self.appText(chatApi(msg))
            else:
                self.appText(EHHH + random.choice(sysList[9]))

    def onJoin(self, joiner: str, result: dict):
        """{'cmd': 'onlineAdd', 'nick': str, 'trip': str, 
            'uType': 'user', 'hash': str, 'level': int, 
            'userid': int, 'isBot': False, 'color': False or str, 
            'channel': str, 'time': int}"""
        self.log(f"{joiner} 加入")
        trip = result["trip"]

        self.nicks.append(joiner)
        self.users.addUser(**result)
        self.looker.addUser(joiner)
        hasher.addHash(joiner, result["hash"])
        
        # if self.motded:
        #     self.motded = False
        #     return

        if joinRl.frisk("*", 1):
            joinRl.records["*"]["score"] = 0
            threading.Thread(target=self.ufts, args=(180,)).start()
            self.sendMsg("Stfued for 180s", True)

        for i in protect:
            if re.search(i, joiner) and protect[i] != trip:
                self.sendMsg(f"昵称{i}已经被识别码#{protect[i]}绑定，请使用其他名字重进\nNickname {i} has already been bound to trip #{protect[i]}. Please use another name to rejoin")
                self.sendMsg(f"{KICK} {joiner}")
                return

        if banned.check(**result):
            self.kick(joiner)
        elif black.check(**result):
            pass
        else:
            msg = EHHH + welcome[trip] if trip in welcome else random.choice(replys[2]).replace("joiner", joiner)
            self.sendMsg(msg)
            if trip in subscribe:
                self.whisper(joiner, self.peeper.getPeep(subscribe[trip], 0))

        if not ignore.check(**result):
            hourCount.add(joiner)
        sawer.addUser(joiner, self.users.getAttr(joiner, "trip"), True)
        self.whisper(joiner, left.check(**result))
        self.rl(joiner, "", 1)
    def onLeave(self, leaver: str):
        self.log(f"{leaver} 离开")
        self.nicks.remove(leaver)
        self.users.delUser(leaver)
        self.looker.delUser(leaver)
        # self.afker.check(leaver)
        if leaver in self.blacktemp:
            self.blacktemp.remove(leaver)
    def onSet(self, result: dict):
        """{'cmd': 'onlineSet', 'nicks': list, 'users': 
            [{'channel': str, 'isme': bool,  'nick': str,  'trip': str, 
                'uType': 'user', 'hash': str,  'level': int, 'userid': int, 
                'isBot': False, 'color': str or False}],
            'channel': str, 'time': int}"""
        self.nicks = result["nicks"]
        self.log("当前在线: " + ", ".join(result["nicks"]))
        self.users.data = {}
        self.oled = True
        for user in result["users"]:
            nick, hash_ = user["nick"], user["hash"]

            self.users.addUser(**user)
            sawer.addUser(nick, user["trip"], True)
            self.looker.addUser(nick)
            hasher.addHash(nick, hash_)

            if nick == self.nick:
                self.userid = user["userid"]
            if banned.check(**user):
                self.kick(nick)
        writeJson("hash", data)

        if self.color:
            self.sendMsg(f"/color {self.color}")
        for i in info["prologue"]:
            self.sendMsg(i)
    def onColorChange(self, result:dict):
        """{'nick': str, 'trip': str, 'uType': 'user', 
            'hash': str, 'level': 100, 'userid': int, 
            'isBot': False, 'color': str, 'cmd': 'updateUser', 
            'channel': str, 'time': int}"""
        self.users.changeAttr(result["nick"], "color", result["color"])
    def onWhisper(self, sender: str, msg: str, result: dict):
        """{"cmd": "info", "channel": str, "from": str, "to": int,
            "text": str, "type": "whisper", "trip": str,
            "level": int, "uType": str, "time": int}
        私信别人时(几把hc):
           {"cmd": "info", "channel": str, "from": int, "to": int,
            "text": str, "type": "whisper", "time": int}"""
        if isinstance(sender, int):
            return
        else:
            sysList[4] = sender
            self.onMsg(msg, sender, result.get("trip"), "whisper")
    def onEmote(self, sender: str, msg: str):
        """{"cmd": "emote", "nick": str, "userid": int, "text": str,
            "channel": str, ?"trip": str, "time": int}"""
        trip = self.users.getAttr(sender, "trip")
        self.peeper.push("*", msg)
        self.log(f"\\*：{msg[:256]}")
        self.rl(sender, msg, 0.2)
        sawer.add(sender, trip, msg)
        self.looker.addUser(sender)
        self.whisper(sender, left.check(**self.users.getUser(sender)))
    def onInvite(awa):
        """{"cmd": "info", "channel": str, "from": str, "to": int, "inviteChannel": str,
            "type": "invite", "text": str, "time": int}
        邀请别人时from为空字符"""
        pass
    def onInfo(self, text: str):
        self.log(text)
        if text.startswith("You have been denied"):
            time.sleep(30)
            self._reconnect(AUTH)
    def onMsgUpdate(self, mode: str, text: str, customId: str, userid: str):
        """{"cmd": "updateMessage", "userid": int, "channel": str, "level": int,
        "mode": str, text": str, "customId": str, "time": int}"""
        if userid == self.userid:
            return
        data = self.peeper.findCustom(customId, userid, mode, text)
        if data:
            sender = data["nick"]
            sawer.add(sender, self.users.getAttr(sender, "trip"), data["text"])
            self.looker.add(sender)
            self.rl(sender, text, 1)
    def onMsg(self, msg: str, sender: str, trip: str, type_: str, **kwargs):
        self.newContext(self.users.getUser(sender), type_)
        for func in self.funclist:
            func(msg, sender, trip, type_, **kwargs)
            if self.remake:
                self._reconnect()
                return
            elif self.returns:
                break
        self.runContext()

if __name__ == "__main__":
    bocchi = Awaya(info["channel"], info["nick"], info["passwd"], info["color"])
    bocchi.rock() # 波门