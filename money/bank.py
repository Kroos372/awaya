from static import readJson, writeJson, random, now, timeDiff, randomStr, Time, PREFIX

class Bank:
    def __init__(self, bank):
        self.bank: dict[str, dict] = bank["bank"]
        self.wait: dict[str, str] = bank["wait"]
        self.packets: dict[str, dict[str, list | int]] = bank["packets"]
    @property
    def users(self) -> list[str]:
        users = []
        for trip, packet in self.bank.items():
            if isinstance(packet, dict):
                users.append(trip)
        return users
    def get(self, trip: str, onlyTrip: bool=False) -> (dict | str | None):
        """onlyTrip: 返回注册用的识别码"""
        while True:
            trip_ = self.bank.get(trip)
            if isinstance(trip_, dict):
                if onlyTrip:
                    return trip
                else:
                    return trip_
            elif trip_ is None:
                return None
            trip = trip_
    def getAttr(self, trip: str, attr: str):
        money = self.get(trip)
        return money.get(attr)
    def setAttr(self, trip: str, attr: str, value):
        money = self.get(trip)
        money[attr] = value
    def getRelated(self, trip: str) -> list[str]:
        result = []
        final = self.get(trip, True)
        for trip_ in self.bank:
            if self.get(trip_, True) == final:
                result.append(trip_)
        return result

    def deregister(self, trip: str, deep: bool=False):
        if deep:
            trips = self.getRelated(trip)
        else:
            trips = [trip]
        money = self.get(trip)
        for trip in trips:
            del self.bank[trip]
        self.save()
        return money
    def register(self, trip: str, packet: dict | str=None):
        if not packet:
            self.bank[trip] = {
                "name": self.wait.pop(trip),
                "money": 0,
                "sign": 0,
                "remain": 0,
                "nextSign": 0
            }
        else:
            self.bank[trip] = packet
        self.save()
    def migrate(self, trip: str, target_trip: str):
        money = self.deregister(trip, True)
        self.register(target_trip, money)
    
    def request(self, trip: str, name: str) -> str:
        if trip in self.bank:
            money = self.get(trip)
            money["name"] = name
            return f"成功变更账户名为{name}"
        else:
            self.wait[trip] = name
            return f"请求成功。{name}({trip})"
    def sign(self, trip: str) -> str:
        money = self.get(trip)
        if not money:
            return f"你还没有银行！使用=={PREFIX}regst==注册一个！"
        if money["nextSign"] > now():
            return f"你在{timeDiff(money['nextSign'] - now())}后才可再次签到！"
        else:
            if money["nextSign"] + Time.DAY < now():
                money["remain"] = 0
            addMoney = random.randint(900, 1100) + (2 * money["sign"]) + (50 * money["remain"])
            money["money"] += addMoney
            money["sign"] += 1
            money["remain"] += 1
            money["nextSign"] = now() + 20 * Time.HOUR
            self.save()
            return f"签到成功，获得{addMoney}阿瓦豆。\n" + self.format(trip, 1)
    def sendPacket(self, trip: str, money: int, people: int) -> str:
        if self.hasMoney(trip, money) != money:
            return "你还没有那么多钱！"
        elif (money / people) < 1:
            return "太小气啦！"
        elif money < 1 or people < 2:
            return "太少了！"
        else:
            key = randomStr()
            self.delete(trip, money)
            self.packets[key] = {
                "sender": trip,
                "money": money,
                "people": people,
                "robbed": [],
                "expire": now() + Time.DAY
            }
            self.save()
            return f"红包发出去了，期限24(-25)小时，id是{key}！"
    def robPacket(self, trip: str, key: str) -> str:
        packet = self.packets.get(key)
        name = self.getAttr(trip, "name")
        if packet is None:
            return "id不正确！"
        elif trip in packet["robbed"]:
            return "你已经抢过了！"
        elif packet["people"] == 1:
            money = packet["money"]
            self.add(trip, money)
            del self.packets[key]
            self.save()
            return f"**{name}**({trip})抢到了**{money}**豆，红包已被抢完！"
        else:
            maxAmount = round(packet["money"] / packet["people"] * 2, 1)
            money = round(random.uniform(0.01, maxAmount), 2)
            self.add(trip, money)
            packet["money"] -= money
            packet["people"] -= 1
            packet["robbed"].append(trip)
            self.save()
            return f"**{name}**({trip})抢到了**{money}**豆\n还剩{packet['money']}豆、{packet['people']}人！"
    def checkPackets(self) -> str:
        natsuki = ["### 当前红包"]
        for key, packet in self.packets.items():
            natsuki.append(f"ID: {key}，剩余金额{packet['money']}，剩余人数{packet['people']}，" + 
                           f"将在{timeDiff(packet['expire'] - now())}后过期")
        return "\n".join(natsuki)
    def checkExpire(self) -> str:
        yuri = []
        for key, packet in self.packets.copy().items():
            if now() > packet["expire"]:
                trip = packet["sender"]
                money = packet["money"]
                self.add(trip, money)
                yuri.append(f"ID为{key}的红包已过期，退回给**{self.getAttr(trip, 'name')}({trip})** {money}豆！")
                del self.packets[key]
        if yuri:
            self.save()
            return "\n".join(yuri)
        else:
            return ""

    def delete(self, trip: str, num: int) -> int:
        money = self.get(trip)
        money["money"] -= self.hasMoney(trip, num)
        money["money"] = round(money["money"], 2)
        self.save()
        return num
    def add(self, trip: str, num: int):
        money = self.get(trip)
        money["money"] += num
        money["money"] = round(money["money"], 2)
        self.save()
    def give(self, giver: str, reciever: str, num: int, force: bool=False):
        """force: 强制加钱"""
        if (num > 0 and self.hasMoney(giver, num) == num) or force:
            money = self.delete(giver, num)
            self.add(reciever, money)

    def rename(self, trip: str, name: str):
        money = self.get(trip)
        money["name"] = name
        self.save()
    def hasMoney(self, trip: str, num: int) -> int:
        money = self.get(trip)
        if money["money"] >= num:
            return num
        else:
            return money["money"]

    def rank(self) -> str:
        abab = []
        for trip in self.users:
            packet = self.bank[trip]
            abab.append((trip, packet["money"], packet["name"]))
        abab = sorted(abab, key=lambda x: x[1], reverse=True)[:25]
        result = ["### 排行"]
        rank = 1
        for trip, num, name in abab:
            result.append(f"{rank}\\. **{name}**({trip})：{num}")
            rank += 1
        return "\n".join(result)
    def format(self, trip: str, level: int=0) -> str:
        money = self.get(trip)
        if not money:
            return "你还没有银行！"
        elif level == 2:
            return f"余额**{money['money']}**阿瓦豆。"
        elif level == 1:
            return f"当前累计签到{money['sign']}天，连续签到{money['remain']}天，余额**{money['money']}**阿瓦豆。"
        else:
            return f"### {money['name']}({trip})\n当前累计签到{money['sign']}天，连续签到{money['remain']}天，余额**{money['money']}**阿瓦豆。"
    def save(self):
        writeJson("money", money)
    def random(self) -> str:
        return random.choice(self.users)

class Shop:
    pass

money = readJson("money")

bank = Bank(money)
shop = Shop()