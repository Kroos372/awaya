#coding=utf-8
# 进源码啥都别说，先一起喊： 阿瓦！
import json, time, math, re, websocket, requests, threading, traceback, sys, os, random, datetime

# 独立于类的函数
## 处理BOM字符
def dec(cont: str) -> str:
    if cont.startswith(u"\ufeff"):
        return cont.encode("utf8")[3:].decode("utf8")
    else:
        return cont
## 整数秒
def now()->int:
    return int(time.time())
## 不知道
def gmNow(sec=0):
    if not sec:
        sec = now()
    return time.gmtime(sec + 28800)
## 存入记忆中！
def writeJson(filename, datas):
    with open("files/" + filename, "w", encoding="utf8") as f:
        json.dump(datas, fp=f, ensure_ascii=False, indent=2)
## 开始真心话
def truth()->str:
    if truthList[0]:
        return "已经在玩了哦╮(╯_╰)╭"
    else: 
        truthList[0] = True
        return f"发r, 发结算, 发结束游戏, 别发@{NAME} 提问"
## 结算真心话
def atLast()->str:
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
## 结束真心话
def endTruth()->str:
    if truthList[0]:
        truthList[0] = False
        return "好吧好吧，结束咯(一。一;;）"
    return "真心话还没开始你在结束什么啊(▼皿▼#)"
## 那个啥，反正就是那个
def getTime() -> str:
    tcg = gmNow()
    try:
        response = requests.get(f"https://literature-clock.jenevoldsen.com/times/{tcg.tm_hour:0>2}_{tcg.tm_min:0>2}.json", timeout=10).json()
    except:
        return "出错啦，请稍后再试(◐_◑)"
    panzerlied = random.choice(response)
    text = ">" + panzerlied["quote_first"] + f"**{panzerlied['quote_time_case']}**" + panzerlied["quote_last"] + "\n\n"
    from_ = "\\- " + panzerlied["title"] + f", *{panzerlied['author']}*"
    return text.replace("<br/>", "\n>") + from_
## r来r去
def rollTo1(maxNum: int=1000) -> str:
    road =  []
    while True:
        ran = random.randint(1, maxNum)
        road.append(str(ran))
        if ran != 1:
            maxNum = ran
        else:
            break
    return f"{', '.join(road)}: {len(road)}"
## 离谱青云客
def chatApi(msg) -> str:
    try:
        cont = requests.get(f"http://api.qingyunke.com/api.php?key=free&msg={msg}", timeout=10)
    except:
        return "寄了"
    else:
        cache = cont.json()["content"].replace("菲菲", NAME).replace("{br}", "\n")
        return cache.replace("help", f"==@{NAME} help==，==菜单==或==@{NAME} 帮助==")
## 自定义回复
def reply(sender: str, msg: str, api: bool=True) -> str:
    for ques, ans in answer.items():
        try:
            searched = re.search(ques, msg)
        except:
            del answer[ques]
            writeJson("answer.json", answer)
            return f"*已清除{ques}的回答"
        else:
            if not (searched and ans):
                continue
            else:
                ans = random.choice(ans).replace("sender", sender)
                if searched.groups():
                    for i, v in enumerate(searched.groups()):
                        ans = re.sub(rf"\\{i+1}", v, ans)
                return EHHH + ans
    if api:
        return chatApi(msg)
    else:
        return None # 乖巧
## 长消息上传
def toWeb(text):
    try:
        requests.post(URL, data={"token": TOKEN, "text": text}, timeout=10)
        return URL
    except:
        return text[:512]
## 随机字符串
def getStr(length=16) -> str:
    dinnerbone = ""
    strs = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    for i in range(length):
        dinnerbone += random.choice(strs)
    return dinnerbone
## 名字提纯
def namePure(name: str) -> str:
    return name.strip("@").strip()
## 自定义回复的空格转换
def textPure(text: str) -> str:
    return text.replace("\\~", "~").replace("~", " ")
## 防止md代码块导致的排版错乱
def mdPure(text: str) -> str:
    return re.sub("(~~~|```)", r"\\\1", text)
## 防止md下划线导致的排版错乱
def nameMd(name: str) -> str:
    return name.replace("_", "\\_")
## 时间差
def timeDiff(seconds) -> str:
    if seconds >= 86400:
        diff = f"{seconds // 86400}日"
        return diff + timeDiff(seconds % 86400)
    elif seconds >= 3600:
        diff = f"{seconds // 3600}时"
        return diff + timeDiff(seconds % 3600)
    elif seconds >= 60:
        diff = f"{seconds // 60}分"
        return diff + timeDiff(seconds % 60)
    else:
        return f"{seconds}秒"
## 格式化时间
def ftime(seconds, format="%Y-%m-%d %H:%M:%S") -> str:
    struct = gmNow(seconds)
    magnolia = time.strftime(format, struct)
    return magnolia
## 检验字符串规范
def verify(type_, text):
    if type_ == "nick":
        return re.search(r"^@?[\w]{1,24}$", text)
    elif type_ == "trip":
        return re.search(r"^[A-Za-z0-9+/]{6}$", text)
    elif type_ == "hash":
        return re.search(r"^[A-Za-z0-9+/]{15}$", text)
    elif type_ == "color":
        return re.search(r"^#?([0-9a-fA-F]{3}){1,2}$", text)
    else:
        return None # 乖巧
## 又加回来了
def colorPic(args: str=""):
    if not args:
        loli = "https://api.lolicon.app/setu/v2"
    else:
        loli = "https://api.lolicon.app/setu/v2?" + args
    try:
        jankie = requests.get(loli, timeout=10).json()
        if jankie["error"]:
            return "API出问题啦"
        elif not jankie["data"]:
            return "没有找到符合要求的涩图啦"
        else:
            jankie = jankie["data"][0]
    except:
        return "出问题啦"
    else:
        # 过滤离谱关键词
        tags = [i for i in jankie["tags"] if not re.search("[乳魅内尻屁胸]", i)]
        url = jankie["urls"]["original"]
        pixiv = "https://www.pixiv.net/artworks/" + str(jankie["pid"])
        title = jankie["title"]
        author = jankie["author"]
        return f"![qaq]({url})\n原url：{pixiv}\n标题：{title}\n标签：{', '.join(tags)}\n作者：{author}"
## 返回日期
def nowDay() -> str:
    now = time.gmtime(time.time() + 28800)
    return f"{now.tm_year}{now.tm_mon:0>2}{now.tm_mday:0>2}"

# 玩类玩的
## 仿rate-limiter
class RateLimiter:
    def __init__(self, halflife, threshold):
        self.halflife = halflife
        self.threshold = threshold
        self.records = {}
    # 获取信息
    def search(self, name: str)->dict:
        record = self.records.get(name)
        if not record:
            record = self.records[name] = {"time": now(), "score": 0}
        return record
    def fscore(self, score, time, delta=1):
        # 使分数随时间衰减，半衰期为halflife秒
        score *= 2**((time-now())/self.halflife)
        return score + delta
    # 监测与加分
    def frisk(self, name: str, delta):
        record = self.search(name)
        # 加分
        record["score"] = self.fscore(record["score"], record["time"], delta)
        record["time"] = now()
        # 分数达到阈值(threshold)时被rl
        if record["score"] >= self.threshold:
            return 1
        return 0
    # 返回需要等多少秒才能使threshold降到to
    def waits(self, name: str, to) -> int:
        return int(math.log2(self.records[name]["score"] / to) * self.halflife)
## 消息载体
class Context:
    def __init__(self, sender, type_):
        self.sender = sender
        self.type_ = type_

        self.returns = False
        self.remake = False

        self.chat = []
        self.whisper = {}
        self.part = []
    def addWhisper(self, to, text):
        if to not in self.whisper:
            self.whisper[to] = []
        self.whisper[to].append(text)
    def appText(self, text: str, type_: str="", **kwargs):
        """chat: 公屏, whisper: 私信, part: 强制独立(命令、custom等)"""
        if not text:
            return
        type_ = type_ or self.type_
        if type_ == "chat":
            self.chat.append(text)
        elif type_ == "whisper":
            to = kwargs.get("to") or self.sender
            self.addWhisper(to, text)
        else:
            self.part.append(dict({"text": text}, **kwargs))
## 消息记录器
class Peeper:
    def __init__(self):
        self.allMsg = []
        self.longlong = []
    def push(self, nick, text, customId="", userid=""):
        if len(text) > 256:
            self.longlong.append(f"{nick}:\n{text}")
            nick = "*"
            text = f"`{text[:30]}...`全文见 {PREFIX}long {len(self.longlong)-1}".replace("\n", "")
        self.allMsg.append({
            "nick": nick,
            "text": text,
            "customId": customId,
            "userid": userid
        })
        if len(self.allMsg) > 520:
            del self.allMsg[0]
    def findCustom(self, customId, userid, mode, text):
        if not customId:
            return None
        for i in self.allMsg:
            if i["customId"] == customId and i["userid"] == userid:
                self.push("*"+i["nick"], self.addCustom(i["text"], mode, text))
                return {"nick": i["nick"], "text": self.addCustom(i["text"], mode, text)}
        return None
    def getMsg(self, i1, i2=0):
        flower = []
        if not i2:
            if i1 > 0:
                array = self.allMsg[:i1]
            else:
                array = self.allMsg[i1:]
        else:
            array = self.allMsg[i1:i2]
        for i in array:
            nick = nameMd(i["nick"])
            text = mdPure(i["text"])
            flower.append(f"{nick}: {text}")
        return "\n\n".join(flower)
    def getLong(self, index):
        return self.longlong[index]
    def getPeep(self, msg, pard=1):
        try:
            while_ = msg.split()
            want_peep = int(while_[0])
            if want_peep == 0:
                raise ValueError
            if len(while_) == 1: 
                if want_peep < 0:
                    res = self.getMsg(-want_peep)
                elif pard:
                    res = self.getMsg(-want_peep-pard, -pard)
                else:
                    res = self.getMsg(-want_peep)
            elif len(while_) > 1:
                res = self.getMsg(int(while_[0]), int(while_[1]))
            else:
                raise ValueError
            if len(res) >= 3000:
                return toWeb(res)
            else:
                return f"：\n{res}"
        except (ValueError, IndexError):
            return "然而peep后面需要一个非零整数"
    @staticmethod
    def addCustom(origin, mode, text) -> str:
        if mode == "overwrite":
            return text
        elif mode == "append":
            return origin + text
        else:
            return text + origin
## 用户容器
class Users:
    def __init__(self):
        self.data = {}
    def addUser(self, nick, **kwargs):
        self.data[nick] = dict(kwargs, nick=nick)
    def getUser(self, nick):
        try:
            return self.data[nick]
        except KeyError:
            return None # 乖巧
    def delUser(self, nick):
        del self.data[nick]
    def getAttr(self, nick, attr):
        try:
            return self.data[nick][attr]
        except KeyError:
            return None # 乖巧
    def attrGet(self, attr, value):
        for nick, maggie in self.data.items():
            if maggie[attr] == value:
                return nick
        return None # 乖巧
    def attrsGet(self, attr, value) -> list:
        zhuyue = []
        for nick, maggie in self.data.items():
            if maggie[attr] == value:
                zhuyue.append(nick) 
        return zhuyue
    def changeAttr(self, nick, attr, value):
        self.data[nick][attr] = value
## 挂机器
class Afker:
    def __init__(self):
        # 别问为什么不写一块
        self.tfk = {} # Trip aFK
        self.nfk = {} # Nick aFK
    def check(self, nick, trip) -> str:
        try:
            if trip:
                doing = self.tfk.pop(trip)
                return f"{nick}#{trip} {doing[0]} 了 {timeDiff(now() - doing[1])}, 欢迎回来(\\*￣ω￣)"
            else:
                doing = self.nfk.pop(nick)
                return f"{nick} {doing[0]} 了 {timeDiff(now() - doing[1])}, 欢迎回来(\\*￣ω￣)"
        except KeyError:
            return ""
    def add(self, nick, trip, doing) -> str:
        if trip:
            self.tfk[trip] = [doing, now(), nick]
            return f"{nick}#{trip} 正在{doing}, 加油ヾ(◍°∇°◍)ﾉﾞ"
        else:
            self.nfk[nick] = [doing, now()]
            return f"{nick} 正在{doing}, 加油ヾ(◍°∇°◍)ﾉﾞ"
    def alert(self, msg) -> str:
        huwu = []
        for trip, dpg in self.tfk.items():
            if re.search(rf"@{dpg[2]}\b", msg):
                huwu.append(f"{dpg[2]}#{trip} {timeDiff(now() - dpg[1])}前开始 正在{dpg[0]}, 请不要打扰ta――")
        for nick, dpg in self.nfk.items():
            if re.search(rf"@{nick}\b", msg):
                huwu.append(f"{nick} {timeDiff(now() - dpg[1])}前开始 正在{dpg[0]}, 请不要打扰ta――")
        return "\n".join(huwu)
    def list(self) -> str:
        xuan2wei1 = []
        for trip, dpg in self.tfk.items():
            xuan2wei1.append(f"{dpg[2]}#{trip} 正在 {dpg[0]} (从{timeDiff(now() - dpg[1])}前开始)")
        for nick, dpg in self.nfk.items():
            xuan2wei1.append(f"{nick} 正在 {dpg[0]} (从{timeDiff(now() - dpg[1])}前开始)")
        xuan2wei1 = "\n".join(xuan2wei1)
        return "### 正在挂机的……\n" + xuan2wei1 if xuan2wei1 else "大家都在哦~"
    def clear(self):
        self.tfk.clear()
        self.nfk.clear()
## 留言器
class Lefter:
    def __init__(self, msg: dict):
        self.msg = msg
    def add(self, type_, to, sender, senderTrip, text):
        if not verify(type_, to):
            return "昵称或识别码不合法！"
        elif not text:
            return "信息不能为空哦uwu"
        else:
            if type_ not in self.msg:
                self.msg[type_] = {}
            if to not in self.msg[type_]:
                self.msg[type_][to] = []
            self.msg[type_][to].append([sender, senderTrip, ftime(now()), text])
            self._writeJson()
            return "留言成功~"
    def check(self, **kwargs) -> str:
        k24 = []
        for type_, to in kwargs.items():
            try:
                tusk = self.msg[type_].pop(to)
            except KeyError:
                pass
            else:
                for yaya in tusk:
                    if yaya[1]:
                        k24.append(f"{nameMd(yaya[0])}#{yaya[1]} 曾在" + 
                            f"（{yaya[2]}）通过{type_}给您留言：\n{mdPure(yaya[3])}")
                    else:
                        k24.append(f"{nameMd(yaya[0])} 曾在" + 
                            f"（{yaya[2]}）通过{type_}给您留言：\n{mdPure(yaya[3])}")
                self._writeJson()
        return "\n\n".join(k24)
    def _writeJson(self):
        userData["leftMsg"] = self.msg
        writeJson("userData.json", userData)
## saw器
class Sawer:
    def __init__(self, last: dict):
        self.last = last or {"nick": {}, "trip": {}}
    def addUser(self, nick, trip, onSet=False):
        time = now()
        # 不是我说，就这个and和or，我自己都觉得天才
        if trip:
            self.last["nick"][nick] = trip
            self.last["trip"][trip] = onSet and self.last["trip"].get(trip) or {"time": time, "msg": None}
        else:
            self.last["nick"][nick] = onSet and self.last["nick"].get(nick) or {"time": time, "msg": None}
        self._writeJson()
    def add(self, nick, trip, msg):
        time = now()
        if trip:
            self.last["trip"][trip] = {"time": time, "msg": msg}
        else:
            self.last["nick"][nick] = {"time": time, "msg": msg}
        self._writeJson()
    def get(self, text: str, type_: str) -> str:
        user = self.last[type_].get(text)
        if not user:
            return "此人还没有光顾此处的样子(◐_◑)"
        if isinstance(user, str):
            type_ = "trip"
            text = user
            user = self.last["trip"][user]
        ltime = user["time"]
        observer = f"最后一次见到{type_}为{text}的用户是在{ftime(ltime)}（距现在{timeDiff(now() - ltime)}）\n"
        if user["msg"] is not None:
            observer += f"他说了：{user['msg'][:50]}"
        else:
            observer += "他加入了。"
        return observer
    def _writeJson(self):
        userData["lastSaw"] = self.last
        writeJson("userData.json", userData)
## look器
class Looker:
    def __init__(self):
        self.now = {}
    def addUser(self, nick):
        self.now[nick] = {"joined": now(), "words": 0}
    def delUser(self, nick):
        if nick in self.now:
            del self.now[nick]
    def add(self, nick):
        if nick in self.now:
            self.now[nick]["words"] += 1
    def get(self, nick) -> str:
        if nick not in self.now:
            return "查无此人ლ(´ڡ`ლ)"
        else:
            saw = self.now[nick]
            joined = now() - saw["joined"]
            if saw["words"]:
                times = joined / 60 / saw["words"]
                freq = f"每{times:.1f}分钟一次"
            else:
                freq = "无发言记录"
            return f"\n他于{timeDiff(joined)}前加入。\n发言频率：{freq}"
## 在线用户列表器
class ListChat:
    def __init__(self, chat, channel: str, customId: str, passwd: str=""):
        self.nick = f"_list{random.randint(1, 9999)}"
        self.customId = customId
        self.channel = channel
        self.passwd = passwd
        self.chat = chat

        self.oled = False
    def _sendPacket(self, packet):
        encoded = json.dumps(packet)
        try:
            self.ws.send(encoded)
        except websocket.WebSocketException:
            pass
    def rock(self) -> str:
        self.ws = websocket.create_connection(
            "wss://hack.chat/chat-ws"
        )
        self._sendPacket({"cmd": "join", "channel": self.channel, "nick": f"{self.nick}#{self.passwd}"})
        while True:
            result = json.loads(self.ws.recv())
            cmd = result["cmd"]

            if cmd == "captcha":
                self.remake(AUTH)
            elif cmd == "warn":
                text = result["text"]
                if text == "Nickname taken": # 这概率
                    self.remake()
                elif re.match(r"^You are (?:be|join)ing", text):
                    break # 开摆
            elif cmd == "info" and text.startswith("You have been denied"):
                self.remake(AUTH)
            elif result.get("channel") and result.get("channel") != self.channel:
                self.remake()
            elif cmd == "onlineSet":
                starry = ""
                for user in result["users"]:
                    if user["isme"]:
                        continue
                    if user["trip"]:
                        trip = ", " + user["trip"]
                    else:
                        trip = ""
                    starry += f"{user['nick']}{trip}, {user['hash']}\n"
                self.ws.close()
                return starry or "空空如也~"
    # 重启
    def remake(self, pswd=""):
        self.ws.close()
        passwd = pswd or self.passwd
        try:
            ryo = ListChat(self.chat, self.channel, self.customId, passwd)
        except:
            pass
        else:
            ryo.rock()
## 黑名单
class Black:
    def __init__(self, name: str):
        self.name = name
        self.data = userData[name]
    def add(self, type_, to) -> str:
        if not verify(type_, to):
            return "参数不合法！"
        if type_ not in self.data:
            self.data[type_] = []
        if to in self.data[type_]:
            return "已经在了"
        else:
            self.data[type_].append(to)
            self._writeJson()
            return "好好好，又进去了一个"
    def delete(self, type_, to) -> str:
        if not (verify(type_, to) and type_ in self.data):
            return "参数不合法！"
        else:
            try:
                self.data[type_].remove(to)
            except:
                return "没有"
            else:
                self._writeJson()
        return "好好好，又出去了一个"
    def check(self, **kwargs) -> bool:
        for type_, to in kwargs.items():
            if type_ not in self.data:
                continue
            elif to in self.data[type_]:
                return True
        return False
    def clear(self):
        self.data = {}
        self._writeJson()
    def list(self) -> str:
        awaya = []
        for k, v in self.data.items():
            uwuya = ", ".join(v)
            if uwuya:
                awaya.append(f"{k}: {uwuya}")
        return "\n".join(awaya)
    def _writeJson(self):
        userData[self.name] = self.data
        writeJson("userData.json", userData)

## hash器
class Hasher:
    def __init__(self, data):
        self.data = data
    def addHash(self, nick, hash_):
        if hash_ not in self.data:
            self.data[hash_] = []
        if nick not in self.data[hash_]:
            self.data[hash_].append(nick)
            writeJson("hash.json", self.data)
    def hashByCode(self, code: str) -> str:
        try:
            return ", ".join(self.data[code]).replace("_", "\\_")
        except:
            return "不存在这个hash码(◐_◑)"
    def hashByName(self, nick: str) -> str:
        l = []
        for i in self.data.values():
            if nick in i:
                text = "，".join(i)
                l.append(text.replace("_", "\\_"))
        l = list(set(l))
        for i, v in enumerate(l):
            l[i] = f"{i+1}\\. "+l[i]
        result = "\n".join(l) or "没有这个名字！"
        return result if len(result) < 666 else toWeb(result)

# 读取文件们
with open("files/info.json", encoding="utf8") as f:
    info = json.loads(dec(f.read()))
with open("files/hash.json", encoding="utf8") as f:
    data = json.loads(dec(f.read()))
with open("files/userData.json", encoding="utf8") as f:
    userData = json.loads(dec(f.read()))
with open("files/reply.json", encoding="utf8") as f:
    replys = json.loads(dec(f.read()))
with open("files/answer.json", encoding="utf8") as f:
    answer = json.loads(dec(f.read()))
# 常量
PREFIX, WHTFIX, OWNFIX = ";", "0", "."
KICK, AUTH, EHHH = "/w mbot kick", info["auth"], "&zwj;"
URL, TOKEN = "http://play.simpfun.cn:17254/awaya/", info["token"]
LATEXOOM = r"$\begin{pmatrix}qaq\\[20231128em]\end{pmatrix}$"
NAME, OWNER = info["name"], info["owner"]

MENUMIN = "\n".join([
    "早",
    "普通用户: ",
    f">前缀=={PREFIX}==:",
    "hasn, hash, code, colo, left, peep, welc, seen, look, Lori, decp, list, setu",
    "无前缀:",
    "r, rollen, time, 真心话",
    "",
    "白名单用户：",
    f">前缀=={WHTFIX}==:",
    "addb, delb, igno, unig, bans, uban, kill, unwe, encap, decap, lock, unlock, gnkey, " + 
    "setrl, addw, delw, list",
    "",
    f"发送=={PREFIX}help 命令==可获得该指令详细用法，如=={PREFIX}help help==",
    f"白名单用{WHTFIX}help",
    "开源地址: https://github.com/Kroos372/awaya , 欢迎star～(∠・ω< )⌒★"
])
OWNMENU = "\n".join([
    "好好反思下身为主人为什么还要菜单",
    "addw, delw: 增减白名单trip; igon, unig: 增减peep忽略名称(正则);",
    "chkr: 检查回答; tstr: 测试问题对应的回答; delr: 删除回答;",
    "relo: 清空一些变量; stfu: 休眠开关; atrm: 报错重启开关;",
    "prtt, delp: 增删保护的trip; send: 发送消息; beat: 心跳(检测被踢)频率(默认120秒)",
    "kkal: 踢出最后到倒数x个用户; eval: 执行代码; remake: 重启",
    "看源码去吧你"
])
COMMANDS = {
    "help": "\n".join([
        "# Help Of Commands:",
        "||",
        "|:-:|",
        "|参数: <命令>|",
        "|描述: 查询<命令>的使用方法。|",
        f"|例: {PREFIX}help help|",
        "|注: <>包起来的是参数类型，如<昵称>代表填写昵称，不要带<>，认真看使用示例。|",
        "|前面加==?==表示可选参数，<参数1>/<参数2>表示两参数任选一。|"
    ]),
    "hasn": "\n".join([
        "# Hash Now Online User:",
        "||",
        "|:-:|",
        "|参数: <昵称>|",
        "|描述: 查询==当前在线==名为<昵称>用户的Hash的历史昵称|",
        f"|例: {PREFIX}hasn @{NAME}|",
    ]),
    "hash": "\n".join([
        "# History Nickname For Hash Of Nick:",
        "||",
        "|:-:|",
        "|参数: <昵称>|",
        "|描述: 查询使用过所有<昵称>的用户的Hash的历史昵称|",
        f"|例: {PREFIX}hash @{NAME}|",
        "|注: 谨慎使用，当心后果。|"
    ]),
    "code": "\n".join([
        "# History Nickname For Hash Code:",
        "||",
        "|:-:|",
        "|参数: <Hash码>|",
        "|描述: 查询使用过所有<昵称>的用户的Hash的历史昵称|",
        f"|例: {PREFIX}hash abcdefg|",
        "|注: `/myhash`可快捷查看自己的Hash。谨慎使用，当心后果。|"
    ]),
    "colo": "\n".join([
        "# Color Of Nickname:",
        "||",
        "|:-:|",
        "|参数: <昵称>|",
        "|描述: 查询当前名为<昵称>的用户的颜色|",
        f"|例: {PREFIX}hash abcdefg|",
    ]),
    "left": "\n".join([
        "# Leave Message For Someone:",
        "||",
        "|:-:|",
        "|参数: <昵称>/*<识别码> <消息>|",
        "|描述: 为<昵称>或<识别码>留言，会在用户上线或发言时私信。|",
        f"|例: {PREFIX}left *coBad2 我喜欢你|",
        f"|例2: {PREFIX}left {NAME} 你喜欢我|",
        "|注: 用户上线时通知格式：<昵称>曾在（<时间>）通过<方式>给您留言：<消息>|",
    ]),
    "peep": "\n".join([
        "# View History Messages:",
        "||",
        "|:-:|",
        "|参数: <整数> ?<整数>|",
        "|描述: 浏览最近的<整数>条消息，参数长度为二时则会选择最近520条消息中第<整数>至第<整数>条。|",
        f"|例: {PREFIX}peep 23|",
        "|注: 最多存储520条消息，查看消息过长时无法显示。|",
        f"|注2: 使用{PREFIX}peep *<参数> 可订阅peep, 在当前识别码每次加入时自动发送peep|",
        "|注3: 返回消息中名字前带有*的表示该消息是更改后的（别老updateMessage了）。|"
    ]),
    "welc": "\n".join([
        "# Set Welcome Message:",
        "||",
        "|:-:|",
        "|参数: ?<欢迎语>|",
        "|描述: 为当前识别码设置欢迎语，参数为空时清除欢迎语。|",
        f"|例: {PREFIX}welc 早|",
        "|注: 别太长。|"
    ]),
    "seen": "\n".join([
        "# Last Saw Someone At:",
        "||",
        "|:-:|",
        "|参数: <昵称>/*<识别码>|",
        f"|描述: 最后一次看到某昵称或识别码的时间，与他最后一句话的内容。|",
        f"|例: {PREFIX}seen *coBad2|",
    ]),
    "look": "\n".join([
        "# I Don't Know:",
        "||",
        "|:-:|",
        "|参数: <昵称>|",
        f"|描述: 当前在线昵称的加入时间，发言频率，以及与{PREFIX}seen相同。|",
        f"|例: {PREFIX}look Krs_|",
    ]),
    "Lori": "\n".join([
        "# L Or i ?",
        "||",
        "|:-:|",
        "|参数: <字符>|",
        "|描述: 帮你区分I和l，什么的。 |",
        f"|例: {PREFIX}Lori I |",
        "|注: 首个大写命令 |",
    ]),
    "decp": "\n".join([
        "# ???",
        "||",
        "|:-:|",
        "|???: ???|",
        "|???: ???|",
        "|???: ???|",
        "|???: 前面的区域，以后再来探索吧~|",
    ]),
    "list": "\n".join([
        "# LIST Sth.:",
        "||",
        "|:-:|",
        "|参数: wht/blk/ign/ban/afk/word|",
        "|描述: 列出一些名单|",
        f"|例: {PREFIX}list wht|",
        "|注: 你感到神秘的力量在涌动|"
    ]),
    "setu": "\n".join([
        "# Colorful Picture:",
        "||",
        "|:-:|",
        "|参数: ?<参数>|",
        "|描述: 涩图怎么又回来了，你们谁有头绪|",
        f"|例: {PREFIX}setu tag=阿瓦|",
        "|注: 来自[点我](https://api.lolicon.app/#/setu), 参数详情自己看。有rl(我加的)。|"
    ]),

    "r": "\n".join([
        "# Random Integer:",
        "||",
        "|:-:|",
        "|参数: ?<整数> ?<整数>|",
        "|描述: 1\\~1000、1\\~<整数>、<整数>\\~1、或<整数>\\~<整数>之间的随机整数。|",
        "|例: r 6 666|",
    ]),
    "rollen": "\n".join([
        "# ROLL to ENd(?):",
        "||",
        "|:-:|",
        "|参数: ?<整数>|",
        "|描述: 不断在1与整数间r，直到归1|",
        "|例: rollen 12345|",
        "|注: 自动截断，いたずら断念 殺人鬼|"
    ]),
    "time": "\n".join([
        "# Literature Clock:",
        "||",
        "|:-:|",
        "|参数: 无|",
        "|描述: 文学作品里的时间。|",
        "|例: time|",
        "|注: [来自点我](https://literature-clock.jenevoldsen.com/)|",
    ]),
    "真心话": "\n".join([
        "# Truth or Dare:",
        "||",
        "|:-:|",
        "|锟斤拷: 烫烫烫烫烫烫烫烫|"
    ]),
}
WTCOMMANDS = {
    "addb": "\n".join([
        "# ADD Blacklist:",
        "||",
        "|:-:|",
        "|参数: <hash/trip/nick> <值>|",
        "|描述: 将<值>加入对应类型的黑名单|",
        f"|例: {WHTFIX}addb nick _|"
    ]),
    "delb": "\n".join([
        "# DELete Blacklist:",
        "||",
        "|:-:|",
        "|参数: <hash/trip/nick> <值>|",
        "|描述: 将<值>移出对应类型的黑名单|",
        f"|例: {WHTFIX}delb hash akstnhmyrw|"
    ]),
    "igno": "\n".join([
        "# IGNOre:",
        "||",
        "|:-:|",
        "|参数: <hash/trip/nick> <值>|",
        "|描述: 将<值>加入对应类型的peep屏蔽列表|",
        f"|例: {WHTFIX}igno nick _|"
    ]),
    "delb": "\n".join([
        "# UN IGnore:",
        "||",
        "|:-:|",
        "|参数: <hash/trip/nick> <值>|",
        "|描述: 将<值>移出对应类型的peep屏蔽列表|",
        f"|例: {WHTFIX}unig hash akstnhmyrw|"
    ]),
    "kill": "\n".join([
        "# KILL:",
        "||",
        "|:-:|",
        "|参数: <昵称>|",
        "|描述: 踢出昵称。|",
        f"|例: {WHTFIX}kill awa_ya|",
        "|注: 可用空格分隔多个|"
    ]),
    "bans": "\n".join([
        "# BANS:",
        "||",
        "|:-:|",
        "|参数: <hash/trip/nick> <值>|",
        "|描述: 将<值>加入对应类型的封禁列表，加入时踢出|",
        f"|例: {WHTFIX}ban nick uwu_ya|"
    ]),
    "uban": "\n".join([
        "# UnBAN:",
        "||",
        "|:-:|",
        "|参数: <hash/trip/nick> <值>|",
        "|描述: 将<值>移出对应类型的封禁列表|",
        f"|例: {WHTFIX}uban hash abcdefghijkl|"
    ]),
    "addn": "\n".join([
        "# ADD Blacklist Nick:",
        "||",
        "|:-:|",
        "|参数: <昵称>|",
        "|描述: 将昵称加入黑名单|",
        f"|例: {WHTFIX}addn _|"
    ]),
    "deln": "\n".join([
        "# DELete Blacklist Nick:",
        "||",
        "|:-:|",
        "|参数: <昵称>|",
        "|描述: 将昵称移出黑名单|",
        f"|例: {WHTFIX}deln _|"
    ]),
    "unwe": "\n".join([
        "# UN WElcome:",
        "||",
        "|:-:|",
        "|参数: <识别码>|",
        "|描述: 清除识别码的欢迎语，防刷屏用。|",
        f"|例: {WHTFIX}unwe coBad2|"
    ]),
    "encap": "\n".join([
        "# ENable CAPtcha:",
        "||",
        "|:-:|",
        "|参数: 无|",
        "|描述: 开启验证码。|",
        "|例: 懒得写|"
    ]),
    "decap": "\n".join([
        "# D?able CAPtcha:",
        "||",
        "|:-:|",
        "|参数: 无|",
        "|描述: 关闭验证码。|",
        "|例: 懒得写|"
    ]),
    "lock": "\n".join([
        "# LOCKroom:",
        "||",
        "|:-:|",
        "|参数: 无|",
        "|描述: 锁房。|",
        "|例: 懒得写|"
    ]),
    "unlock": "\n".join([
        "# UNLOCKroom:",
        "||",
        "|:-:|",
        "|参数: 无|",
        "|描述: 解锁。|",
        "|例: 懒得写|"
    ]),
    "gnkey": "\n".join([
        "# GeNerate KEY:",
        "||",
        "|:-:|",
        "|参数: 无|",
        "|描述: 生成key，用于无识别码时关闭验证码。|",
        "|例: 懒得写|"
    ]),
    "setrl": "\n".join([
        "# SET Rate Limiter:",
        "||",
        "|:-:|",
        "|参数: <整数> ?<整数> ?word|",
        "|描述: 设置rl器的半衰期与阈值，如果最后一项为word则设置封禁词的rl器|",
        f"|例: {WHTFIX}setrl 30 3 word|",
        "|注: 具体计算方式见源码|"
    ]),
    "addw": "\n".join([
        "# ADD Ban Word:",
        "||",
        "|:-:|",
        "|参数: <词>|",
        "|描述: 添加封禁词，当rl值到则踢出。支持正则。|",
        f"|例: {WHTFIX}addw .|",
        "|注: 笑点解析: 添加白名单也是addw|"
    ]),
    "delw": "\n".join([
        "# DELete Ban Word:",
        "||",
        "|:-:|",
        "|参数: <词>|",
        "|描述: 删除封禁词|",
        f"|例: {WHTFIX}delw 几把|",
    ]),
    "list": "\n".join([
        "# LIST Channel Users:",
        "||",
        "|:-:|",
        "|参数: <频道>|",
        "|描述: 列出某频道的用户。|",
        f"|例: {WHTFIX}list your-channel|",
        "|注: 别用太多，容易rl|"
    ]),
    "rcolor": "\n".join([
        "# Random COLOR:",
        "||",
        "|:-:|",
        "|参数: 无|",
        "|描述: 随机颜色|",
        "|例: rcolor|",
        "|注: 最好别用|"
    ]),

    "decp": "\n".join([
        "# D?able CaPtcha:",
        "||",
        "|:-:|",
        "|参数: <key>|",
        "|描述: 在没有识别码的情况下关闭验证码。|",
        f"|例: {PREFIX}decp awawaw|",
        "|注: 详见gnkey|"
    ])
}
CLOCKS = [
    "0点了，夜深快准备睡觉吧~",
    "都已经1点，还不睡觉吗？",
    "2点了，惬意而祥和的时光啊。",
    "3点了，月光依然安静地笼罩着大地。",
    "4点，似乎有什么事情要做？",
    "清晨5点，早起的鸟儿有虫吃~",
    "6点，新的一天又开始了呢！",
    "7点啦，什么时候吃早饭呢？",
    "8点了，今天有什么计划呢？",
    "9点了，感觉怎么样呢？",
    "10点了，喝杯水放松一下吧。",
    "11点，上午过去得好快啊。",
    "12点了，准备吃午饭吧。",
    "13点了，漫长的下午要开始咯~",
    "14点到了，要做些什么事吗？",
    "15点了，是不是该喝杯下午茶？",
    "16点了，摸一摸信赖的人吧~",
    "17点了，下午的时间过去了一多半了吧。",
    "18点了，有谁准备快乐地下班了吗？",
    "19点了，今天有收获到什么吗？",
    "20点了，晚上应该怎么度过呢？",
    "21点了，夜宵还是散步，都不错呢~",
    "22点了，早睡早起身体好哦~",
    "23点啦，原来都还在聊天吗。"
]
KAWAII = [
    "sender棒棒",
    "sender是小天使",
    "sender最可爱了"
]

# 全局变量
## [0涩图开关, 1报时开关, 2休眠开关, 3当前日期, 4sender nick, 5报错是否重启, 6心跳频率(秒), 7stfu时间, 8玩的, 9复读库]
sysList = [False, True, False, nowDay(), "", True, 120, 0, False, []]
## [0真心话开关, 1{昵称：摇出的数字}, 2[玩游戏中的hash]]
truthList = [False, {}, []]

banWords = userData["banWords"]
whiteList = userData["whiteList"]
subscribe = userData["subscribe"]
protect =  userData["protect"]
keys = userData["keys"]
welcome = userData["welText"]

msgRl = RateLimiter(40, 10)
joinRl = RateLimiter(5, 7)
wordRl = RateLimiter(30, 3)
setuRl = RateLimiter(25, 5)
left = Lefter(userData["leftMsg"])
sawer = Sawer(userData["lastSaw"])
black = Black("black")
ignore = Black("ignore")
banned = Black("banned")
hasher = Hasher(data)

lineReply = {
    # 纪念零姬……
    "0.0": ["0.0.0", ".0.", ";0;"],
    "menu": ["菜单", "别发菜单"],

    "time": getTime,
    "真心话": truth,
    "结算": atLast,
    "结束游戏": endTruth,
}
cmdList = {
    "wht": lambda: f"当前白名单识别码：{', '.join(whiteList)}\n当前粉名单识别码：" + ", ".join(OWNER),
    "word": lambda: f"当前封禁词：{', '.join(banWords)}",
    "blk": lambda: f"当前黑名单：\n{black.list()}",
    "ign": lambda: f"当前被忽略：\n{ignore.list()}",
    "ban": lambda: f"当前被封禁：\n{banned.list()}"
}