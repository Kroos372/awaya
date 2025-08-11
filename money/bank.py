from static import readJson, writeJson, now, timeDiff, randomStr, Time, PREFIX, ftime, random_design
import random, math
import numpy as np

# 有机会拆分一下

class LoanStatus:
    WAITING = 0
    UNPAYED = 1
    OVERDUE = 2

class Bank:
    offering_box = "r2SKbu"
    def __init__(self, bank: dict):
        self.bank: dict[str, dict] = bank["bank"]
        self.wait: dict[str, str] = bank["wait"]
        self.packets: dict[str, dict[str, list | int]] = bank["packets"]
        self.akas: dict[str, str] = bank.setdefault("akas", {})
        self.loans: dict[str, dict] = bank.setdefault("loans", {})
    # get
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
    def getAttr(self, trip: str, attr: str, default=None):
        money = self.get(trip)
        if attr not in money:
            money[attr] = default
        return money[attr]
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

    # 注册、账号
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
    def register(self, trip: str, packet: dict=None):
        if not packet:
            self.bank[trip] = {
                "name": self.wait.pop(trip),
                "money": 0,
                "sign": 0,
                "remain": 0,
                "nextSign": 0,
                "credits": 100
            }
        else:
            self.bank[trip] = packet
        self.save()
    def rename(self, trip: str, name: str):
        money = self.get(trip)
        money["name"] = name
        self.save()
    def aka_register(self, trip: str, aka_trip: str) -> str:
        if aka_trip in self.akas:
            return "这个识别码正在请求中！"
        elif trip in self.akas and aka_trip == self.akas[trip]["trip"]:
            del self.akas[trip]
            self.bank[trip] = aka_trip
            self.save()
            return f"已成功关联{trip}至{aka_trip}"
        elif aka_trip in self.bank:
            return "这个识别码已经被关联了！"
        else:
            self.akas[aka_trip] = {
                "trip": trip,
                "expire": now() + Time.DAY
            }
            self.save()
            return f"已发送请求，请在24小时内使用{aka_trip}发送 {PREFIX}aka {trip} 完成关联！"
    def check_aka_expire(self):
        save_needed = False
        for key, packet in self.akas.copy().items():
            if now() > packet["expire"]:
                del self.akas[key]
                save_needed = True
        if save_needed:
            self.save()
    def migrate(self, trip: str, target_trip: str):
        money = self.deregister(trip, True)
        self.register(target_trip, money)
    
    # 操作豆数
    def delete(self, trip: str, num: int, reason: str="", force: bool=False, save: bool=True) -> int:
        if num <= 0:
            return num

        money = self.get(trip)
        if force:
            real_num = num
        else:
            real_num = min(money["money"], num)

        money["money"] -= real_num
        money["money"] = round(money["money"], 2)

        if reason:
            self.add_reason(trip, f"{reason}：-{real_num:,}")
        if save:
            self.save()
        return num
    def add(self, trip: str, num: int, reason: str="", save: bool=True):
        if num <= 0:
            return

        money = self.get(trip)
        money["money"] += num
        money["money"] = round(money["money"], 2)
        
        if reason:
            self.add_reason(trip, f"{reason}：+{num:,}")
        if save:
            self.save()
    def give(self, giver: str, reciever: str, num: int, reason: str="", benefit: bool=False):
        """benefit: 强制加钱"""
        if benefit and not self.loans.get(f"store-{giver}"):
            force = False
        else:
            force = True

        if self.getAttr(giver, "money") >= num or benefit:
            self.delete(giver, num, f"{reason}转给{reciever}", force)
            self.add(reciever, num, f"{reason}来自{giver}的转账")
    def offer(self, num: int, reason: str=""):
        self.add(self.offering_box, num, reason, save=False)

    # 债务系统
    def borrow(self, borrower: str, num: int, days: int, lender: str) -> str:
        if self.getAttr(borrower, "money") <= -10000:
            return "当前资产太少，无法发起借款"
        if days < 1:
            return "期限至少一天"
        if num < 1:
            return "嗯……嗯？"
        
        lender = self.get(lender, True)
        borrower = self.get(borrower, True)
        loan_id = self.random_id()
        self.loans[loan_id] = {
            "borrower": borrower,
            "num": num,
            "days": days,
            "status": LoanStatus.WAITING,
            "expire": now() + Time.DAY,
            "lender": lender
        }
        if lender == self.offering_box:
            if days > 30:
                self.reject(lender, loan_id)
                return "期限太久"
            elif self.loan_num_of(borrower, lender) + num > 9999:
                self.reject(lender, loan_id)
                return "已借额度过大，请归还后再借"
            else:
                interest = self.get_interest(borrower)
                self.lend(lender, loan_id, interest)
                return f"借款成功，利率{interest}，记得及时归还喵"
        else:
            self.save()
            return f"已向{lender}发起借款。\nID为{loan_id}，将在24小时后过期"
    def lend(self, trip: str, loan_id: str, interest: float) -> str:
        loan = self.loans.get(loan_id)
        trip = self.get(trip, True)
        if loan is None:
            return "ID错误，请检查后重试"
        if interest > 0.5:
            return "利率过高"
        if loan["lender"] != trip:
            return "你不是贷款人"
        if loan["status"] != LoanStatus.WAITING:
            return "债务已经成交了"
        if self.getAttr(trip, "money") < loan["num"]:
            return "你没有足够的阿瓦豆"
        
        if trip != self.offering_box:
            self.delete(trip, loan["num"], f"借款给{loan['borrower']}")
        self.add(loan["borrower"], loan["num"], f"来自{trip}的借款")
        loan.update({
            "status": LoanStatus.UNPAYED,
            "interest": interest,
            "overdue_time": now() + loan["days"] * Time.DAY,
            "last_update": now(),
            "need_repay": loan["num"]
        })
        del loan["expire"]
        del loan["days"]
        self.save()
        return "成功借出。\n" + self.format_loan(loan_id)
    def reject(self, trip: str, loan_id: str, num: int=0) -> str:
        loan = self.loans.get(loan_id)
        trip = self.get(trip, True)
        if loan is None:
            return "ID错误，请检查后重试"
        if loan["lender"] != trip:
            return "你不是贷款人"
        if loan["status"] == LoanStatus.UNPAYED and loan["overdue_time"] > now():
            return "债务已成交且尚未逾期"

        if loan["status"] == LoanStatus.WAITING:
            del self.loans[loan_id]
            self.save()
            return f"成功拒绝ID为{loan_id}的借款"
        
        elif loan["need_repay"] < num:
            return "没欠这么多"
        else:
            borrower = loan["borrower"]
            if num > 0:
                loan["need_repay"] -= num
                need_repay = num
            else:
                need_repay = loan["need_repay"]
                del self.loans[loan_id]
            self.delete(borrower, need_repay, f"逾期强制归还向{trip}的借款", True)
            self.add(trip, need_repay, f"来自{borrower}的还款")
            self.save()
            return f"已强制扣除{borrower} **{need_repay}**阿瓦豆归还"
    def repay(self, trip: str, loan_id: str, num: int | float) -> str:
        loan = self.loans.get(loan_id)
        trip = self.get(trip, True)
        if loan is None:
            loans = self.get_loans(trip, 1)
            if not loans:
                return "ID错误，请检查后重试"
            else:
                loan_id = loans[0][0]
                loan = loans[0][1]

        if num <= 0:
            return "不是哥们"
        if self.getAttr(trip, "money") < num:
            return "你没有足够阿瓦豆"
        if loan["borrower"] != trip:
            return "你不是借款人"
        if loan["status"] == LoanStatus.WAITING:
            return "对方尚未同意借款"

        real_repay = min(num, loan["need_repay"])
        loan["need_repay"] -= real_repay
        self.give(trip, loan["lender"], real_repay, f"债务{loan_id}-")
        if loan["need_repay"] <= 0:
            del self.loans[loan_id]
        self.save()
        return f"还款成功，还剩{loan['need_repay']}豆需还"
    def store(self, trip: str, num: int | float) -> str:
        if self.getAttr(trip, "money") < num:
            return "钱数不足"
        elif num < 1:
            return "..."

        trip = self.get(trip, True)
        self.give(trip, self.offering_box, num, "存钱")
        loan_id = f"store-{trip}"
        if loan_id in self.loans:
            self.loans[loan_id]["need_repay"] += num
            # self.loans[loan_id]["num"] += num
        else:
            self.loans[loan_id] = {
                "borrower": self.offering_box,
                "num": num,
                "days": 0,
                "status": LoanStatus.OVERDUE,
                "overdue_time": now(),
                "last_update": now(),
                "interest": 0,
                "need_repay": num,
                "lender": trip
            }
        self.save()
        
        return f"存钱成功，债务ID为{loan_id}"

    def format_loan(self, loan_id: str) -> str:
        if loan_id not in self.loans:
            return "ID错误"
        loan = self.loans[loan_id]
        borrower, lender = loan["borrower"], loan["lender"]
        text = [
            f"#### {loan_id}",
            f"借款者：**{self.getAttr(borrower, 'name')}({borrower})**，" +
            f"贷款者：**{self.getAttr(lender, 'name')}({lender})**，" +
            f"借贷金额：**{loan['num']:,}**",
        ]

        if loan["status"] == LoanStatus.WAITING:
            text.extend([
                "状态：待处理",
                f"归还期限：{loan['days']}日",
                f"将于{timeDiff(loan['expire'] - now())}后过期"
            ])
        elif loan["status"] == LoanStatus.UNPAYED:
            text.extend([
                "状态：待归还",
                f"利率：{loan['interest']}，剩余归还金额：{loan['need_repay']:,}",
                f"将于{timeDiff(loan['overdue_time'] - now())}后逾期"
            ])
        else:
            text.extend([
                "状态：==逾期==",
                f"利率：{loan['interest']}，剩余归还金额：{loan['need_repay']:,}",
            ])
        
        return "\n".join(text)
    def format_loans(self, trip: str) -> str:
        self.update_loans()
        trip = self.get(trip, True)
        borrows = ["## 你的债务\n### 借款"]
        lends = ["### 贷款"]
        for id_, loan in self.loans.items():
            if loan["borrower"] == trip:
                borrows.append(self.format_loan(id_))
            elif loan["lender"] == trip:
                lends.append(self.format_loan(id_))
        return "\n\n---\n".join(borrows + lends)
    def get_loans(self, trip: str, type_: int=0) -> list[tuple[str, dict]]:
        """type: 0: 借贷, 1: 借, 2: 贷"""
        loans = []
        for id_, loan in self.loans.items():
            if not type_ or (type_ == 1 and loan["borrower"] == trip) or (
                type_ == 2 and loan["lender"] == trip):
                loans.append((id_, loan))
        return loans
    def loan_num_of(self, borrower: str, lender: str) -> int:
        sum_ = 0
        for value in self.loans.values():
            if (value["borrower"] == borrower and value["lender"] == lender
                and value["status"] != LoanStatus.WAITING):
                sum_ += value["num"]
        return sum_
    def update_loans(self):
        save_needed = False
        for key, loan in self.loans.copy().items():
            if loan["status"] == LoanStatus.UNPAYED and loan["overdue_time"] < now():
                loan["status"] = LoanStatus.OVERDUE
                save_needed = True
            if loan["status"] == LoanStatus.WAITING:
                if now() > loan["expire"]:
                    del self.loans[key]
                    save_needed = True
            elif loan["last_update"] + Time.DAY < now():
                if loan["status"] == LoanStatus.UNPAYED:
                    loan["need_repay"] += loan["num"] * loan["interest"]
                    loan["last_update"] = now()
                else:
                    loan["need_repay"] += loan["num"] * loan["interest"] * 2
                    loan["last_update"] = now()
                save_needed = True

        if save_needed:
            self.save()

    # 信用（没用）
    def add_credit(self, trip: str, num: int):
        credits = self.getAttr(trip, "credits", 100)
        self.setAttr(trip, "credits", min(credits + num, 100))
    def delete_credit(self, trip: str, num: int):
        credits = self.getAttr(trip, "credits", 100)
        self.setAttr(trip, "credits", max(credits - num, 0))
    def get_interest(self, trip: str) -> float:
        return 0.02

    # 娱乐、红包
    def request(self, trip: str, name: str) -> str:
        if trip in self.bank:
            money = self.get(trip)
            money["name"] = name
            return f"成功变更账户名为{name}"
        else:
            self.wait[trip] = name
            return f"{name}({trip})\n请求成功，请耐心等待。（小号将不作受理）"
    def sign(self, trip: str) -> str:
        money = self.get(trip)
        if not money:
            return f"你还没有银行！使用=={PREFIX}regst==注册一个！"
        if money["nextSign"] > now():
            return f"你在{timeDiff(money['nextSign'] - now())}后才可再次签到！"
        else:
            if money["nextSign"] + Time.DAY < now():
                money["remain"] = 0
            addMoney = random.randint(900, 1100) + (10 * money["sign"]) + (50 * money["remain"])
            money["sign"] += 1
            money["remain"] += 1
            money["nextSign"] = now() + 20 * Time.HOUR
            self.add(trip, addMoney, "每日签到")
            return f"签到成功，获得{addMoney}阿瓦豆。\n" + self.format(trip, 1)
    def rank(self, num: int=20) -> str:
        if num > 50:
            return "太多啦"
        abab = []
        for trip in self.users:
            packet = self.bank[trip]
            abab.append((trip, packet["money"], packet["name"]))
        abab = sorted(abab, key=lambda x: x[1], reverse=True)[:num+1]
        result = ["### 排行"]
        rank = 0
        for trip, num, name in abab:
            result.append(f"{rank}\\. **{name}**({trip})：{num:,}")
            rank += 1
        return "\n".join(result)
    def sendPacket(self, trip: str, money: int, people: int) -> str:
        if self.getAttr(trip, "money") < money:
            return "你还没有那么多钱！"
        elif people and (money / people) < 1:
            return "太小气啦！"
        elif money < 1 or people < 2:
            return "太少了！"
        else:
            key = randomStr()
            self.delete(trip, money, "发红包")
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
            self.add(trip, money, "红包")
            del self.packets[key]
            self.save()
            return f"**{name}**({trip})抢到了**{money}**豆，红包已被抢完！"
        else:
            maxAmount = round(packet["money"] / packet["people"] * 2, 1)
            money = round(random.uniform(0.01, maxAmount), 2)
            self.add(trip, money, "红包")
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
                self.add(trip, money, "红包退还")
                yuri.append(f"ID为{key}的红包已过期，退回给**{self.getAttr(trip, 'name')}({trip})** {money}豆！")
                del self.packets[key]
        if yuri:
            self.save()
            return "\n".join(yuri)
        else:
            return ""

    # reasons
    def add_reason(self, trip: str, reason: str):
        reasons: list = self.getAttr(trip, "reasons", [])
        reasons.insert(0, f"({ftime(now())}) {reason}")
        if len(reasons) > 10:
            reasons.pop()
    def get_reasons(self, trip: str) -> str:
        return "#### 账单明细\n" + "\n".join(self.getAttr(trip, "reasons", []))

    # 其他
    def hasMoney(self, trip: str, num: int) -> int:
        money = self.get(trip)
        return min(money["money"], num)
    def format(self, trip: str, level: int=0) -> str:
        money = self.get(trip)
        if not money:
            return ""
        if level == 3:
            return f"{money['money']:,}"
        elif level == 2:
            return f"余额**{money['money']:,}**阿瓦豆。"
        elif level == 1:
            return f"当前累计签到{money['sign']}天，连续签到{money['remain']}天，余额**{money['money']:,}**阿瓦豆。"
        else:
            msgs = [
                f"### {money['name']}({trip})",
                f"当前累计签到{money['sign']}天，连续签到{money['remain']}天",
                # f"信用分{self.getAttr(trip, 'credits', 100)}",
                f"余额**{money['money']:,}**阿瓦豆。",
                ""
            ]
            if level < 0:
                msgs.extend([
                    "---",
                    self.get_reasons(trip)
                ])
            return "\n".join(msgs)
    def random_id(self, length: int=6) -> str:
        loan_id = randomStr(length)
        while loan_id in self.loans:
            loan_id = randomStr(length)
        return loan_id
    def save(self):
        writeJson("money", money)
    def random(self) -> str:
        return random.choice(self.users)
    def list_users(self) -> str:
        users = []
        for trip, packet in self.bank.items():
            if isinstance(packet, dict):
                users.append(packet["name"] + "：" + trip)
        return "\n".join(users)

class Stock:
    heartbeat = Time.MINUTE * 2
    def __init__(self, bank: dict):
        self.stocks: list[dict[str, int | dict]] = bank.setdefault("stocks", [])
        self.next_update = now() + self.heartbeat
    
    def new_stock(self, scale=0):
        num = random.random()
        if not scale:
            scale = round(random.uniform(0.01, 0.5), 2)
        if num > 0.66:
            init = random.randint(10, 30)
        elif num > 0.33:
            init = random.randint(100, 300)
        else:
            init = random.randint(1000, 3000)
        self.stocks.append({
            "name": random_design(),
            "init": init,
            "last": init,
            "now": init,
            "scale": scale,
            "investors": {}
        })

    def up_or_down(self, stock: dict, level: int=0) -> str:
        last = stock["last"]
        now = stock["now"]
        if now > last:
            if level == 1:
                return "↑" + str(round(now - last, 2))
            else:
                return "↑ +" + str(round(now - last, 3))
        elif now < last:
            if level == 1:
                return "↓" + str(round(last - now, 2))
            else:
                return "↓ -" + str(round(last - now, 3))
        else:
            return "→"

    def check_stocks(self, trip: str, level: int=0) -> str:
        msgs = [
            f"距下次更新还有{timeDiff(self.next_update - now())}",
            "",
            "---"
        ]
        for code, stock in enumerate(self.stocks):
            if not bank.get(trip):
                owned = 0
            else:
                owned = stock["investors"].get(bank.get(trip, True), 0)
            if level == 1:
                msgs.append(f"{stock['name']}#{code+1}: **{stock['now']:,}**awb {self.up_or_down(stock, level)}")
                msgs.append(f"? {stock['scale']} ! {round(stock['init'] * 0.1, 2)} ({owned:,})")
                msgs.append("[]()")
            else:
                msgs.extend([
                    f"### {stock['name']}(序号{code+1})",
                    f"当前股价: **{stock['now']:,}**豆/支 " + self.up_or_down(stock),
                    f"浮动：{stock['scale']}",
                    f"强平线：{round(stock['init'] * 0.1, 3)}",
                    f"你持有{owned:,}支",
                    "",
                    "---"
                ])
        return "\n".join(msgs)

    def update_stocks(self) -> str:
        dead = []
        msg = ""
        for i, stock in enumerate(self.stocks):
            price = stock["now"]
            init = stock["init"]
            scale = stock["scale"]
            change = np.random.normal(-scale**2 / 2, scale)

            stock["last"] = price
            stock["now"] = round(price * math.exp(change), 3)

            if stock["now"] < 0.1 * init:
                msg += f"「{stock['name']}」的股价跌破10%，已强制平仓\n"
                for investor, num in stock["investors"].items():
                    self.sell_stock(investor, i, num)
                self.new_stock()
                dead.append(i)
        
        for i in dead[::-1]:
            self.stocks.pop(i)
 
        self.next_update = now() + self.heartbeat
        bank.save()
        return msg

    def buy_stock(self, trip: str, code: int, num: int) -> str:
        stock = self.stocks[code]
        total_price = num * stock["now"]
        trip = bank.get(trip, True)
        owned = stock["investors"].get(trip, 0)

        if num < 1:
            return "你在干什么"
        if bank.getAttr(trip, "money") < total_price:
            return "你的钱数不足以买那么多支"
        
        stock["investors"][trip] = owned + num
        bank.delete(trip, total_price, f"买入股票「{stock['name']}」")
        bank.save()
        return f"买入成功，花费{total_price:,}豆\n" + bank.format(trip, 2)

    def sell_stock(self, trip: str, code: int, num: int) -> str:
        stock = self.stocks[code]
        total_price = num * stock["now"]
        trip = bank.get(trip, True)
        owned = stock["investors"].get(trip, 0)

        if num < 1:
            return "你在干什么"
        if owned < num:
            return "你持有的股数不足"

        stock["investors"][trip] = owned - num
        bank.add(trip, total_price, f"卖出股票「{stock['name']}」")

        if owned == 0:
            del stock["investors"][trip]
        bank.save()
        return f"卖出成功，获得{total_price:,}豆\n" + bank.format(trip, 2)


money = readJson("money")

bank = Bank(money)
stock = Stock(money)