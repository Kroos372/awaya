#coding=utf-8
# 进源码啥都别说，先一起喊： 瓦门！
from static import *
from games import bomber, chess, countryKill, poker, truth, uno

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
            if "text" in packet and not packet["text"]:
                return
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
            if sysList[1]:
                try:
                    self.sendMsg(CLOCKS[hour])
                except:
                    pass
            if hour == 0:
                sysList[3] = nowDay()
                # MotdChat(self.channel, MOD).rock()
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
                result = json.loads(self.ws.recv())
                cmd = result["cmd"]
                sysList[4] = rnick = result.get("nick")
                if cmd == "captcha":
                    time.sleep(30)
                    self._reconnect(AUTH)
                elif cmd == "warn":
                    text = result["text"]
                    print(text)
                    # 史上最不优雅的判断
                    if text == "Nickname taken":
                        self._reconnect(rand=True)
                    elif re.match(r"^You are (?:be|join|send)ing", text):
                        if not self.oled:
                            time.sleep(60)
                            self._reconnect()
                        else:
                            threading.Thread(target=self.ufts, args=(40,)).start()
                elif result.get("channel") and result.get("channel") != self.channel:
                    time.sleep(6)
                    self._reconnect()
                elif cmd == "chat":
                    self.onMsg(result["text"], rnick, result.get("trip"), "chat", customId=result.get("customId"), userid=result["userid"])
                elif cmd == "onlineAdd":
                    self.onJoin(rnick, result)
                elif cmd == "onlineRemove":
                    self.onLeave(rnick)
                elif cmd == "emote":
                    self.onEmote(result["nick"], result["text"])
                elif cmd == "info":
                    if result.get("type") == "whisper":
                        self.onWhisper(result["from"], result["text"].split(": ", 1)[1], result)
                    else:
                        self.onInfo(result["text"])
                elif cmd == "updateUser":
                    self.onColorChange(result)
                elif cmd == "updateMessage":
                    self.onMsgUpdate(result["mode"], result["text"], result["customId"], result["userid"])
                elif cmd == "onlineSet":
                    self.onSet(result)
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
            if not sysList[5]:
                self.sendMsg(f"被玩坏了，呜呜呜……\n```\n{error}\n```", True)
            else:
                filename = e.__class__.__name__ + ftime(now(), "%Y_%m_%d_%H_%M_%S")
                with open(f"traceback/{filename}.txt", "w", encoding="utf8") as f:
                    f.write(error)
                self.sendMsg(f"被玩坏了，呜呜呜……即将重启，请查看报错文件……", True)
                time.sleep(6)
                self._reconnect()
        self.rock()

    # 小憩一会
    def ufts(self, sec):
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
        result = []
        for user in self.nicks:
            if user == self.nick:
                continue
            if self.users.getAttr(user, "trip"):
                trip = ", " + self.users.getAttr(user, "trip")
            else:
                trip = ""
            result.append(f"{user}{trip}, {self.users.getAttr(user, 'hash')}")
        return "\n".join(result)
    # 发言与封禁词rl
    def rl(self, sender: str, msg: str, score: int=0) -> str:
        hash_ = self.users.getAttr(sender, "hash")
        if msgRl.frisk(hash_, 1+len(msg)/512 + score):
            msgRl.records[hash_]["score"] = msgRl.threshold / 2
            return self.kick(sender)
        for word in banWords:
            if re.search(word, msg) and wordRl.frisk(hash_, 1):
                wordRl.records[hash_]["score"] = wordRl.threshold / 2
                return self.kick(sender)
        return ""
    # 踢
    def kick(self, *nicks, assert_: bool=False):
        return
        kkNicks = []
        for nick in nicks:
            if nick == self.nick or self.users.getAttr(nick, "trip") in whiteList:
                if assert_:
                    return None
                else:
                    continue
            else:
                self.blacktemp.append(nick)
                kkNicks.append(nick)
        if kkNicks:
            return KICK + " " + " ".join(kkNicks)
        return ""
    ## 多线程updatemsg
    def updateFunc(self, func, cid, *args):
        threading.Thread(target=lambda: self.updateMsg("overwrite", func(*args), cid)).start()

    def selfSelf(self, context, msg, sender, trip, type_, **kwargs):
        # 日志, 添加look与seen
        if type_ != "whisper":
            self.log(f"{sender}：{msg}")
            sawer.add(sender, trip, msg)
            self.looker.add(sender)
        elif sender != self.nick:
            self.log(f"{sender}私信：{msg}")
        # stfu
        if sysList[2] and (self.users.getAttr(sysList[4], "trip") not in whiteList):
            return
        # 处理自己
        if sender == self.nick:
            if sysList[8]:
                sysList[8] = False
            else:
                context.returns = True
    def premade(self, context, msg, sender, trip, type_, **kwargs):
        user = self.users.getUser(sender)
        if type_ != "whisper":
            # rl
            context.appText(self.rl(sender, msg), "part", force=True)
            # 加peep
            if not ignore.check(**user):
                self.peeper.push(sender, msg, kwargs.get("customId"), kwargs.get("userid"))
            # 随机复读
            if 1 < len(msg) and len(msg) < 256:
                sysList[9].append(msg)
        elif trip not in whiteList:
            # 私信rl更严
            context.appText(self.rl(sender, msg, len(msg)/256 + 2), "part", force=True)
        try:
            command = msg.split()[0]
        except:
            command = "" # 服了
        if msg[0] == WHTFIX and trip in whiteList:
            command = command[1:]
            if command == "help":
                cmd = msg[6:]
                if not msg[5:]:
                    context.appText(f"{MENUMIN}", "whisper")
                elif cmd in WTCOMMANDS:
                    context.appText("我是占位符awa\n" + WTCOMMANDS[cmd], "whisper")
                elif cmd in COMMANDS:
                    context.appText("我是占位符awa\n" + COMMANDS[cmd], "whisper")
                else:
                    context.appText("暂时没有此功能或懒得写了¯\\\\\\_(ツ)_/¯")
            if command == "addb":
                bloods = msg.split()
                if len(bloods) < 2:
                    context.appText("缺少参数")
                elif len(bloods) < 3:
                    hash_ = self.users.getAttr(namePure(msg[6:]), "hash")
                    if hash_ is None:
                        context.appText("参数错误")
                    else:
                        context.appText(black.add("hash", hash_))
                else:
                    context.appText(black.add(bloods[1], namePure(bloods[2])))
            elif command == "delb":
                bloods = msg.split()
                if len(bloods) < 2:
                    context.appText("缺少参数")
                elif len(bloods) < 3:
                    hash_ = self.users.getAttr(namePure(msg[6:]), "hash")
                    if hash_ is None:
                        context.appText("参数错误")
                    else:
                        context.appText(black.delete("hash", hash_))
                elif len(bloods) > 3:
                    for attr in bloods[2:]:
                        black.delete(bloods[1], namePure(attr))
                    context.appText("阿瓦一下")
                else:
                    context.appText(black.delete(bloods[1], namePure(bloods[2])))
            if command == "igno":
                bloods = msg.split()
                if len(bloods) < 2:
                    context.appText("缺少参数")
                elif len(bloods) < 3:
                    context.appText(ignore.add("nick", namePure(msg[6:])))
                else:
                    context.appText(ignore.add(bloods[1], namePure(bloods[2])))
            elif command == "unig":
                bloods = msg.split()
                if len(bloods) < 2:
                    context.appText("缺少参数")
                elif len(bloods) < 3:
                    context.appText(ignore.delete("nick", namePure(msg[6:])))
                elif len(bloods) > 3:
                    for attr in bloods[2:]:
                        ignore.delete(bloods[1], namePure(attr))
                    context.appText("阿瓦一下")
                else:
                    context.appText(ignore.delete(bloods[1], namePure(bloods[2])))
            elif command == "bans":
                bloods = msg.split()
                if len(bloods) < 2:
                    return context.appText("缺少参数")
                elif len(bloods) < 3:
                    hash_ = self.users.getAttr(namePure(msg[6:]), "hash")
                    if hash_ is None:
                        return context.appText("参数错误")
                    else:
                        bloods[1] = "hash"
                        bloods.append(hash_)
                attr = namePure(bloods[2])
                nicks = self.users.attrsGet(bloods[1], attr)
                if nicks:
                    assert_ = self.kick(*nicks, assert_=True)
                    if assert_:
                        context.appText(banned.add(bloods[1], attr))
                        context.appText(assert_, "part")
                    else:
                        context.appText("6")
                else:
                    context.appText(banned.add(bloods[1], attr))
            elif command == "uban":
                bloods = msg.split()
                if len(bloods) < 2:
                    context.appText("缺少参数")
                elif len(bloods) < 3:
                    context.appText(banned.delete("hash", msg[6:]))
                elif len(bloods) > 3:
                    for attr in bloods[2:]:
                        banned.delete(bloods[1], namePure(attr))
                    context.appText("阿瓦一下")
                else:
                    context.appText(banned.delete(bloods[1], namePure(bloods[2])))
            elif command == "repl":
                _000 = msg.split()
                if len(_000) < 3 or not _000[1]:
                    context.appText(f"命令错误，请使用`{WHTFIX}repl 提问 回答`的格式(‾◡◝)")
                else:
                    ans = " ".join(_000[2:])
                    quest = textPure(_000[1])
                    if quest not in answer:
                        answer[quest] = [ans]
                    else:
                        answer[quest].append(ans)
                    context.appText(f"添加成功(☆▽☆)")
                    writeJson("answer.json", answer)
            elif command == "kill":
                context.appText(self.kick(*msg[6:].split()), "part")
            elif command == "gnkey":
                key = getStr()
                keys[trip] = key
                writeJson("userData.json", userData)
                context.appText("\n".join([
                    "占位awa",
                    f"`{key}`是您的新key，可用于在无识别码状态私信使用`{PREFIX}decp <key>`关闭验证码",
                    "请妥善保管，如遗失，可使用此识别码执行此命令重新生成"
                ]), "whisper")
            elif command == "unwe":
                trip = msg[6:12]
                if trip not in welcome:
                    context.appText("还没有设置欢迎语")
                else:
                    del welcome[trip]
                    writeJson("userData.json", userData)
                    context.appText("删除欢迎语成功")
            elif command == "encap":
                context.appText(".m enablecap", "part")
            elif command == "decap":
                context.appText(".m disablecap", "part")
            elif command == "lock":
                context.appText(".m lockroom", "part")
            elif command == "unlock":
                context.appText(".m unlockroom", "part")
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
                context.appText(f"halflife: {setRl.halflife}, threshold: {setRl.threshold}")
            elif command == "addw":
                word = msg[6:]
                if word in banWords:
                    context.appText("已经有这个封禁词了~")
                else:
                    banWords.append(word)
                    writeJson("userData.json", userData)
                    context.appText("好好好，又进去了一个。")
            elif command == "delw":
                word = msg[6:]
                if word not in banWords:
                    context.appText("没有这个封禁词了~")
                else:
                    banWords.remove(word)
                    writeJson("userData.json", userData)
                    context.appText("好好好，删除成功。")
            elif command == "list":
                lChannel = msg[6:]
                if not lChannel:
                    context.appText("-_-#")
                elif lChannel == self.channel:
                    context.appText(self.listNow())
                elif type_ == "whisper":
                    context.appText("暂不支持私信, 果咩捏")
                else:
                    # List? kita kita~
                    cid = getStr(6)
                    context.appText("桥豆麻袋", "part", cid=cid)
                    kita = ListChat(lChannel, cid, self.passwd)
                    self.updateFunc(kita.rock, cid)
            elif command == "room":
                lChannel = msg[6:] or self.channel
                cid = getStr(6)
                context.appText("桥豆麻袋", "part", cid=cid)
                kita = RoomChat(lChannel, cid, self.nick)
                self.updateFunc(kita.rock, cid)
            elif command == "setb":
                sp = msg.split()
                try:
                    mini, maxi = int(sp[1]), int(sp[2])
                except:
                    return context.appText("输入格式有误，请在0setb 后面用空格隔开，输入最小值和最大值两个整数！")
                if (maxi-mini) < 1:
                    context.appText("两数的差别过小，请重新设置！")
                else:
                    bomber.bombs[3], bomber.bombs[4] = mini, maxi
                    context.appText("设置成功！")        
        elif msg[0] == OWNFIX and trip in OWNER:
            command = command[1:]
            if command == "help":
                context.appText(OWNMENU, "whisper")
            elif command == "addw":
                trip_ = msg[6:12]
                if trip_ not in whiteList:
                    whiteList.append(trip_)
                    writeJson("userData.json", userData)
                    context.appText("添加特殊服务的家伙咯╰(￣▽￣)╮")
                else:
                    context.appText("你要找的人并不在这里面(๑°ㅁ°๑)‼")
            elif command == "delw":
                trip_ = msg[6:12]
                if trip_ not in whiteList:
                    context.appText("你要找的人并不在这里面( ˃᷄˶˶̫˶˂᷅ )")
                else:
                    whiteList.remove(trip_)
                    if trip_ in keys:
                        del keys[trip_]
                    writeJson("userData.json", userData)
                    context.appText("删除白名单用户成功๑乛◡乛๑")
            elif command == "kkal":
                try:
                    chocol = int(msg[6:])
                    context.appText(self.kick(*self.nicks[-chocol:]), "part")
                except ValueError:
                    context.appText("寄了吧你")
            elif command == "chkr":
                _17 = msg.split()
                if len(_17) < 2:
                    context.appText("\n".join(answer.keys()), "whisper")
                else:
                    ans = answer.get(textPure(_17[1]))
                    if not ans:
                        context.appText(f"当前问题还没有设置回答，请重新确认后查询（用`~`代表空格，`\\~`代表\\~）！", "whisper")
                    else:
                        if len(_17) == 2:
                            _17 = []
                            for i, v in enumerate(ans):
                                _17.append(f"{i}：{v[:55]}")
                            col = "\n".join(_17)
                            context.appText(f"此问题的回答有：\n{col}", "whisper")
                        else:
                            try:
                                context.appText(f"{ans[int(_17[2])]}", "whisper")
                            except:
                                context.appText(f"当前问题还没有此序号，请重新确认后查询！", "whisper")
            elif command == "tstr":
                ans = textPure(msg[6:])
                if ans:
                    for k, v in answer.items():
                        if re.search(k, ans):
                            context.appText(k, "whisper")
                            break
                    else:
                        context.appText(f"当前问题还没有设置回答，请重新确认后查询（用`~`代表空格，`\\~`代表\\~）！", "whisper")
            elif command == "delr":
                kilo = msg.split()
                if len(kilo) < 2 or len(kilo) > 3:
                    context.appText(f"命令错误，请使用`{OWNFIX}delr 问题 序号`的格式（序号可选，用`~`代表空格，`\\~`代表\\~）！", "whisper")
                else:
                    kilo[1] = textPure(kilo[1])
                    if len(kilo) == 2:
                        try: del answer[kilo[1]]
                        except: context.appText(f"此问题还未设置答案，请重新确认后再次再试！", "whisper")
                        else: context.appText(f"已成功删除“{kilo[1]}”的所有回答！", "whisper")
                    else:
                        try: ans = answer[kilo[1]].pop(int(kilo[2]))
                        except: context.appText(f"此问题还未设置答案或序号错误，请重新确认后再次再试！", "whisper")
                        else: context.appText(f"已成功删除回答：“{ans}”！", "whisper")
                    writeJson("answer.json", answer)
            elif command == "relo":
                ind = msg[6:]
                if ind == "long":
                    self.peeper.longlong = []
                elif ind == "mean":
                    sysList[9] = []
                elif ind == "left":
                    left.msg = {}
                    writeJson("userData.json", userData)
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
                context.appText("成功")
            elif command == "stfu":
                sysList[2] = not sysList[2]
                context.appText(f"阿瓦了这下: {sysList[2]}")
            elif command == "prtt":
                _4w4 = msg[6:].split()
                if len(_4w4) != 2:
                    context.appText("参数不正确")
                else:
                    protect[_4w4[0]] = _4w4[1]
                    context.appText(f"为昵称{_4w4[0]} 绑定识别码{_4w4[1]} 成功")
                    writeJson("userData.json", userData)
            elif command == "delp":
                name = namePure(msg[6:])
                if name not in protect:
                    context.appText("此昵称还没有被保护")
                else:
                    context.appText(f"删除成功，被绑定的识别码有{protect[name]}")
                    del protect[name]
                    writeJson("userData.json", userData)
            elif command == "remake":
                context.remake = True
            elif command == "atrm":
                sysList[5] = not sysList[5]
                context.appText(f"阿瓦了这下: {sysList[5]}")
            elif command == "beat":
                try:
                    sysList[6] = int(msg[6:])
                except:
                    context.appText("QAQ")
                else:
                    context.appText("设置成功~")
            elif command == "send":
                sysList[8] = True
                context.appText(msg[6:], "part")
            elif command == "eval":
                try:
                    if msg[6:7] == "*":
                        context.appText(str(eval(msg[7:])))
                    else:
                        exec(msg[6:])
                except BaseException as e:
                    context.appText("错误！\n```\n" + traceback.format_exc(chain=False) + "\n```")
            # elif command == "motd":
            #     userData["motd"] = msg[6:]
            #     writeJson("userData.json", userData)
            #     MotdChat(self.channel, MOD).rock()
        # 检查黑名单
        if black.check(**user) or sender in self.blacktemp:
            context.returns = True
        # 检查留言
        context.appText(left.check(**user), "whisper")
    # 古兰枝掌管afk的神
    def afks(self, context, msg, sender, trip, type_, **kwargs):
        if type_ != "whisper":
            context.appText(self.afker.check(sender))
            if re.match(r"^afk\b", msg):
                context.appText(self.afker.add(sender, msg[4:44] or "AFK"))
            if "@" in msg:
                context.appText(self.afker.alert(msg))
    def mainfunc(self, context, msg, sender, trip, type_, **kwargs):
        try:
            command = msg.split()[0]
        except:
            command = ""
        icb9 = random.randint(1, 134)

        if msg[0] == PREFIX:
            command = command[1:]
            if command == "hash":
                context.appText(hasher.hashByName(namePure(msg[6:])))
            elif command == "hasn":
                nick = namePure(msg[6:])
                if nick in self.nicks:
                    context.appText(hasher.hashByCode(self.users.getAttr(nick, "hash")))
                else:
                   context.appText("此人当前不在线( ⊙ o ⊙ )")
            elif command == "code":
                context.appText(hasher.hashByCode(msg[6:]))
            elif command == "colo":
                name = namePure(msg[6:])
                if name not in self.nicks:
                    context.appText("没有这个用户(╰_╯)#")
                else:
                    color = self.users.getAttr(name, "color")
                    if color:
                        context.appText(color)
                    else:
                        context.appText("RESET")
            elif command == "left":
                mauver = re.sub(r"(```|~~~)", r"\\\1", msg).split(" ")
                text = " ".join(mauver[2:])
                if len(mauver) < 3:
                    context.appText("命令不正确！")
                elif mauver[1].startswith("*"):
                    context.appText(left.add("trip", mauver[1][1:], sender, trip, text))
                else:
                    context.appText(left.add("nick", namePure(mauver[1]), sender, trip, text))
            elif command == "peep":
                if msg[6:7] == "*":
                    if not trip:
                        context.appText("当前还没有识别码")
                    elif not msg[7:]:
                        try:
                            del subscribe[trip]
                        except:
                            pass
                        else:
                            context.appText(f"为#{trip} 取消订阅成功")
                    else:
                        subscribe[trip] = msg[7:]
                        context.appText(f"为#{trip} 订阅成功")
                else:
                    context.appText(self.peeper.getPeep(msg[6:]), "whisper")
            elif command == "welc":
                if not msg[5:]:
                    if trip not in welcome:
                        context.appText("你还没有设置欢迎语！")
                    else:
                        del welcome[trip]
                        writeJson("userData.json", userData)
                        context.appText(f"为识别码{trip}清除欢迎语成功了！")
                elif not trip:
                    context.appText("您当前还没有识别码，请重进并在昵称输入界面使用==昵称#密码==设置一个！")
                else:
                    welcome[trip] = msg[6:]
                    writeJson("userData.json", userData)
                    context.appText(f"为识别码{trip}设置欢迎语成功了！")
            elif command == "seen":
                light = msg.split()
                if len(light) < 2:
                    context.appText("参数呢！！！")
                elif light[1][0:1] == "*":
                    context.appText(sawer.get(namePure(light[1][1:]), "trip"))
                else:
                    context.appText(sawer.get(namePure(light[1]), "nick"))
            elif command == "look":
                name = namePure(msg[6:])
                context.appText(self.looker.get(name))
            elif command == "help":
                kc = msg.split()
                if len(kc) < 2:
                    context.appText(f"{MENUMIN}", "whisper")
                elif len(kc) > 6:
                    context.appText("太多了，装不下了~")
                else:
                    result = []
                    for cmd in kc:
                        if cmd in COMMANDS:
                            result.append(COMMANDS[cmd])
                    if result:
                        context.appText("我是占位符awa\n" + "\n".join(result), "whisper")
                    else:
                        context.appText("暂时没有此功能或懒得写了¯\\\\\\_(ツ)_/¯")
            elif command == "long":
                try:
                    index = int(msg[6:])
                    context.appText(":\n" + self.peeper.getLong(index), "whisper")
                except:
                    context.appText("索引有误！")
            # 什么傻逼功能
            elif command == "Lori":
                lori = msg[6:7]
                if lori in ["l", "I", "1", "|", "丨"]:
                    if lori == "l":
                        context.appText(f"您输入的“{lori}”是字母表的第十二个字母, “L”的小写。")
                    elif lori == "I":
                        context.appText(f"您输入的“{lori}”是字母表的第九个字母, “i”的大写。")
                    elif lori == "1":
                        context.appText(f"您输入的“{lori}”是最小的正整数, 3-2的结果。")
                    elif lori == "|":
                        context.appText(f"您输入的“{lori}”是我喜欢你, 按住Shift+\\\\可以打出。")
                    elif lori == "丨":
                        context.appText(f"您输入的“{lori}”是一个汉字, 一般地, 读作gun3。")
                elif lori in ["0", "O"]:
                    if lori == "0":
                        context.appText(f"您输入的“{lori}”是最小的自然数, 1-1的结果。")
                    elif lori == "O":
                        context.appText(f"您输入的“{lori}”是字母表的第十五个字母, “o”的大写。")
                else:
                    context.appText("不知道您大人想干嘛呢")
            elif command == "decp":
                for tp, ky in keys.items():
                    if msg[6:] == ky:
                        context.appText(tp, "part")
                        context.appText(".m disablecap", "part")
            elif command == "list":
                cmd = msg[6:]
                if cmd in cmdList:
                    context.appText(cmdList[cmd]())
                elif cmd == "afks":
                    context.appText(self.afker.list())
                elif cmd == self.channel:
                    context.appText(self.listNow())
                else:
                    context.appText("早？")
            elif command == "setu":
                if setuRl.frisk("*", 1):
                    context.appText("rl乐，别涩涩了")
                elif type_ == "whisper":
                    context.appText("别私信乐")
                elif not sysList[2]:
                    cid = getStr(6)
                    context.appText("少女祈祷中. . .", "part", cid=cid)
                    self.updateFunc(colorPic, cid, msg[6:])

        elif namePure(msg) == self.nick:
            if icb9 > 130:
                context.appText(random.choice(replys[1]).replace("sender", sender))
            elif icb9 > 80:
                context.appText("发送菜单了解我的功能~")
            else:
                context.appText(random.choice(replys[0]).replace("sender", sender))
        elif msg.startswith(f"@{self.nick} "):
            msg = msg[len(self.nick)+2:]
            if msg == "提问":
                context.appText(random.choice(replys[3]).replace("sender", sender))
            elif type_ != "whisper":
                context.appText(reply(sender, msg))
            else:
                context.appText(reply(sender, msg, False))
        elif msg == "菜单":
            context.appText(f"{MENUMIN}", "whisper")

        elif msg[0] == "r" and type_ != "whisper":
            if msg == "r":
                context.appText(truth.truthDo(sender, self.users.getAttr(sender, "hash")))
            elif msg[:2] == "r ":
                sakura = msg.split()[1:]
                try:
                    beR = int(sakura[0])
                except:
                    context.appText(str(random.randint(1, 1000)))
                else:
                    try:
                        r2 = int(sakura[1])
                    except:
                        r2 = 1
                    if beR > r2:
                        context.appText(str(random.randint(r2, beR)))
                    else:
                        context.appText(str(random.randint(beR, r2)))
            elif command == "rollen":
                digit = msg[7:25]
                try: context.appText(rollTo1(int(digit)))
                except ValueError as e: context.appText(rollTo1(1000))
        elif msg.startswith("cc ") and type_ != "whisper":
            context.appText(chess.main(sender, msg[3:]))
        elif msg.startswith("p ") and type_ != "whisper":
            poker.main(context, sender, msg[2:].replace("。", "."))
        elif msg.startswith("t ") and type_ != "whisper":
            context.appText(truth.main(msg[2:]))
        elif msg.startswith("u ") and type_ != "whisper":
            uno.main(context, sender, msg[2:].replace("。", ".").replace("？！", "?!"))
        elif msg.startswith("b ") and type_ != "whisper":
            bomber.main(context, sender, msg[2:])
        elif msg.startswith("s ") and type_ != "whisper":
            countryKill.main(context, sender, msg[2:].replace("。", "."))

        # 古老的梗
        elif namePure(msg) == sender:
            context.appText("why did you call yourself")
        elif msg.lower() in lineReply and type_ != "whisper":
            call = lineReply[msg.lower()]
            if hasattr(call, "__call__"):
                context.appText(call())
            else:
                context.appText(random.choice(call).replace("sender", sender))
        elif icb9 > 128:
            if icb9 == 129:
                context.appText(random.choice(KAWAII).replace("sender", sender))
            elif icb9 < 132:
                context.appText(chatApi(msg))
            else:
                context.appText(EHHH + random.choice(sysList[9]))

    def onJoin(self, joiner: str, result: dict):
        """{'cmd': 'onlineAdd', 'nick': str, 'trip': str, 
            'uType': 'user', 'hash': str, 'level': int, 
            'userid': int, 'isBot': False, 'color': False or str, 
            'channel': str, 'time': int}"""
        self.log(f"{joiner} 加入")
        trip = result["trip"]

        self.nicks.append(joiner)
        self.users.addUser(**result)
        hasher.addHash(joiner, result["hash"])

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
            self.sendMsg(self.kick(joiner))
        elif black.check(**result):
            pass
        else:
            msg = EHHH + welcome[trip] if trip in welcome else random.choice(replys[2]).replace("joiner", joiner)
            self.sendMsg(msg)
            if trip in subscribe:
                self.whisper(joiner, self.peeper.getPeep(subscribe[trip], 0))

        sawer.addUser(joiner, self.users.getAttr(joiner, "trip"), True)
        self.looker.addUser(joiner)
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
                self.sendMsg(self.kick(nick))
        writeJson("hash.json", data)

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
        self.sendMsg(self.rl(sender, msg, 0.2), force=True)
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
            self.sendMsg(self.rl(sender, text, 1), force=True)
    def onMsg(self, msg: str, sender: str, trip: str, type_: str, **kwargs):
        context = Context(sender, type_)
        context.nick = self.nick
        for func in self.funclist:
            func(context, msg, sender, trip, type_, **kwargs)
            if context.remake:
                self._reconnect()
                return
            elif context.returns:
                break
        self.sendMsg("\n".join(context.chat))
        for to, text in context.whisper.items():
            self.whisper(to, "\n".join(text))
        for kws in context.part:
            self.sendMsg(**kws)

if __name__ == "__main__":
    for owner in OWNER:
        if not owner in whiteList:
            whiteList.append(owner)
            writeJson("userData.json", userData)

    bocchi = Awaya(info["channel"], info["nick"], info["passwd"], info["color"])
    bocchi.rock() # 波门