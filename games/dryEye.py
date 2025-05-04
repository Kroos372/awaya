# code by sora
import random, re

cardsRank = {1: "0",2: "2", 3: "3", 4: "4", 5: "5", 6: "6", 7: "7",
               8: "8", 9: "9", 10: "10", 11: "J", 12: "Q", 13: "K",14: "A",
               15: "Joker"}

DERULE = "\n".join([
    "游戏规则：[点我点我点我](http://aberia.pythonanywhere.com/static/docs/dryeye.html)。",
    "出牌规则：",
    "1. 单张：发送 `g 3` 表示出 3。",
    "2. 对子：发送 `g 3*2` 表示出对 3。",
    "3. 三张：发送 `g 3*3` 表示出 333。",
    "4. 顺子：发送 `g 3-5` 表示出 345。",
    "5. 双顺：发送 `g 3-5*2` 表示出 334455。",
    "6. 炸弹：发送 `g 3*4` 表示出 3333。",
    "7. 癞子：直接发送想要出的牌，系统会自动补齐癞子。",
    "8. 跳过：发送 `g .` 表示跳过回合。",
    "9. 查看牌：发送 `g check` 查看自己当前的牌。",
    "注意：出牌时必须符合规则，系统会自动校验牌型和大小。"
])
DERMENU = "\n".join([
    "干瞪眼，代码改自sora",
    "g 加入: 加入一场干瞪眼。",
    "g 退出: 在开始之前退出对局。",
    "g <牌>: 出牌，具体规则请查看出牌规则。",
    "g 结束: 在对局中结束游戏。",
    "g 规则: 获取干瞪眼的出牌规则。",
])


class DryEye:
    def __init__(self):
        self.context = None
        self.initInit()
    
    def initInit(self):
        self.gameEnded = False
        self.players = []
        self.gamePhase = 0

    def initGame(self):
        self.num_decks = 0 # 牌堆数量
        self.upCards = "" # 上家出的牌
        self.upCardsInfo = "" # 上家出的牌的信息
        self.upCardsKind = "空" # 上家出的牌的类型
        self.upBomb = (0,0,0) #上家出的炸弹的信息 card,bomb_size,joker_count
        self.upPlayer = "" # 上家的昵称
        self.latestPlayer = 0 # 最新出牌的玩家编号
        self.next_player = 1  # 下一个出牌的玩家
        self.playerMoney = {}  # 玩家金钱
        self.poker = {} # 扑克牌结构
        self.checkPass = 0 #检查这轮是否需要结束

        self.multipleTurn = {
            "players": [],  # 倍数轮的两个玩家
            "multiple": 1,  # 当前倍数
            "base": 5      # 基数
        }

        self.roundCount = 0  # 当前大轮次数
        self.playedCards = {1: False, 2: False, 3: False}  # 记录每个玩家是否出过牌
        self.deck = []  # 用于存储剩余牌堆   

    def dealCards(self):
        # 初始化扑克牌（2-14为2-A，15为joker）
        self.deck = [i for i in range(2, 15)] * 4 * self.num_decks + [15] * 2 * self.num_decks
        random.shuffle(self.deck)

        # 初始化桶结构 self.poker[player][suit][rank]
        self.poker = [[[0 for _ in range(16)] for _ in range(1,5)] for _ in range(self.playerNumero+1)] #应该是这个吧（*＾-＾*）
        # self.poker = [[[0] * 16] * 4] * (self.playerNumero + 1) # ?
        for player in range (1, self.playerNumero+1):
            self.poker[player][0] = ""  # 玩家昵称
        self.poker[0][0] = "...新的一轮刚开始，没有上家哦~"
        # 分发牌给3位玩家，每人5张
        for player in range(1, self.playerNumero+1):
            for _ in range(5):
                card = self.deck.pop()
                self.poker[player][1][card] += 1

        # 初始化玩家金钱
        for player in range(1, self.playerNumero + 1):
            self.playerMoney[player] = 100  # 每个玩家初始100块

        self.gamePhase = 1
        return self.poker

    def checkCard(self, player):
        # 检查玩家牌
        cards_info = "\n泥当前剩的牌是"
        playerName = self.poker[player][0]
        player_cards = self.poker[player][1]
        
        for rank in range(3, 16):
            for i in range (1,player_cards[rank]+1):
                cards_info += cardsRank[rank] + " "
        for rank in range(2, 3):
            for i in range (1,player_cards[rank]+1):
                cards_info += cardsRank[rank] + " "

        money_info = f"\n你现在还剩{self.playerMoney[player]}块钱，"
        if self.multipleTurn["players"] and player in self.multipleTurn["players"]:
            other_player = self.multipleTurn["players"][0] if self.multipleTurn["players"][1] == player else self.multipleTurn["players"][1]
            money_info += f"正在和{self.poker[other_player][0]}的{self.multipleTurn['multiple']}倍数对决中！"
        else:
            money_info += "暂时没有进入倍数轮。"
        self.context.appText(f"{playerName}真是杂鱼，要好好记牌哦！你的编号是{player}，上一家出牌的是{self.poker[self.upPlayer][0]}，出的牌是{self.upCardsInfo}。{cards_info}。{money_info}\n加油捏，看好你", "whisper", to=playerName)

    #mM->multiplicative Multiplication
    def updateMultipleTurn(self, player1, player2, mM):
        """更新倍数轮状态"""
        if not self.multipleTurn["players"]:
            self.multipleTurn["players"] = [player1, player2]
        self.multipleTurn["multiple"] *= mM
        self.context.appText(f"\\*(੭*ˊᵕˋ)੭\\*ଘ，{self.poker[player1][0]}与{self.poker[player2][0]}间的倍数已累至{self.multipleTurn['multiple']}倍！")

    def endMultipleTurn(self, winner):
        #结束倍数轮，进行结算
        if not self.multipleTurn["players"]:
            return

        if self.multipleTurn["players"][0] == winner:
            loser = self.multipleTurn["players"][1]
        else:
            loser = self.multipleTurn["players"][0]
        amount = self.multipleTurn["multiple"] * self.multipleTurn["base"]
        
        self.playerMoney[winner] += amount
        self.playerMoney[loser] -= amount
        
        self.context.appText(f"该倍数轮结束！{self.poker[winner][0]}赢得了{amount}块钱，{self.poker[loser][0]}失去了{amount}块钱！")
        # 重置倍数轮
        self.multipleTurn["players"] = []
        self.multipleTurn["multiple"] = 1

    def calculateTribute(self, player_cards):
        #计算上供金额
        normal_cards = sum(player_cards[1:14]) - player_cards[2]  # 除去2的普通牌
        special_cards = player_cards[2] + player_cards[14]  # 2和王的数量
        return normal_cards * 2 + special_cards * 10

    def endRound(self):
        #处理大轮结束
        self.gamePhase += self.gamePhase == 1
        # 结束第一阶段
        self.roundCount += 1
        self.checkPass = 0
        # 结算倍数轮
        if self.multipleTurn["players"]:
            self.endMultipleTurn(self.upPlayer)
        # 重置出牌记录
        self.upCards = ""
        self.upCardsInfo = ""
        self.upPlayer = 0
        self.upBomb = (0,0,0)
        self.upCardsKind = "空"
        self.context.appText(f"第{self.roundCount}轮结束！现在继续补牌，下一轮将由{self.poker[self.latestPlayer][0]}开始出牌")
        # 处理补牌
        i = self.latestPlayer
        for _ in range(self.playerNumero):  # 给三个玩家各补一张牌
            if not self.dealExtraCard(i):  # 如果牌堆空了
                self.context.appText("牌堆已空，不能继续补牌了！进入第三阶段，到底谁会赚的最多呢")
                self.gamePhase = 3
                break
            i = (i % self.playerNumero) + 1

    def checkFirstPhaseForce(self, player):
        # 检查第一阶段是否有必须出的炸弹
        player_cards = self.poker[player][1]
        for card in range(2, 15):
            if player_cards[card] >= 3 - player_cards[15]:  # 有炸弹
                return f"{card}*{player_cards[card]}"
        return None

    def findBestJokerCombo(self, player_cards, target_combo):
        # 找出最佳的癞子组合方式
        # 返回: (是否可行, 需要的癞子数量, 癞子替代的牌值列表)
        joker_count = player_cards[15]
        needed_jokers = 0
        
        if re.match(r"^\d+\*\d+$", target_combo):  # 连张
            card = int(target_combo.split("*")[0])
            if player_cards[card] + joker_count >= int(target_combo.split("*")[1]):
                needed_jokers = max(0, int(target_combo.split("*")[1]) - player_cards[card])
                return (True, needed_jokers, [card] * needed_jokers)
        elif re.match(r"^\d+-\d+$", target_combo):  # 顺子
            start, end = map(int, target_combo.split("-"))
            needed_jokers = 0
            joker_positions = []
            for card in range(start, end + 1):
                if player_cards[card] == 0:
                    needed_jokers += 1
                    joker_positions.append(card)
                    if needed_jokers > joker_count:
                        return (False, 0, [])
            if needed_jokers >= 0:
                return (True, needed_jokers, joker_positions)
                
        elif re.match(r"^\d+-\d+\*2$", target_combo):  # 双顺
            start, end = map(int, target_combo.split("*")[0].split("-"))
            needed_jokers = 0
            joker_positions = []
            for card in range(start, end + 1):
                need = max(0, 2 - player_cards[card])
                needed_jokers += need
                joker_positions.extend([card] * need)
                if needed_jokers > joker_count:
                    return (False, 0, [])
            if needed_jokers >= 0:
                return (True, needed_jokers, joker_positions)
        
        return (False, 0, [])

    def formatJokerUsage(self, joker_positions):
        """格式化癞子使用信息"""
        if not joker_positions:
            return ""
        usage = {}
        for pos in joker_positions:
            usage[pos] = usage.get(pos, 0) + 1
        
        result = "使用癞子替代了："
        for card, count in usage.items():
            result += f"{count}张{cardsRank[card]}，"
        return result.rstrip("，")

    def compareBombLevel(self, bomb1, bomb2):
        """比较两个炸弹的大小
        Args:
            bomb1: (card, bomb_size, joker_count) 第一个炸弹的信息
            bomb2: (card, bomb_size, joker_count) 第二个炸弹的信息
        Returns:
            1: bomb1 更大
            -1: bomb2 更大
            0: 相等
        """
        card1, bomb_size1, joker_count1 = bomb1
        card2, bomb_size2, joker_count2 = bomb2
        
        if bomb_size1 > bomb_size2:
            return 1
        elif bomb_size1 < bomb_size2:
            return -1
        else:  # bomb_size相同时比较joker_count
            if joker_count1 < joker_count2:
                return 1
            elif joker_count1 > joker_count2:
                return -1
            else:
                if card1 > card2:
                    return 1
                elif card1 < card2:
                    return -1
                elif card1 == card2:
                    return 0

    def dealExtraCard(self, player):
        #处理补牌
        if not self.deck:
            return False
        
        card = self.deck.pop()
        self.poker[player][1][card] += 1
        
        # 生成当前所有手牌信息
        cards_info = ""
        player_cards = self.poker[player][1]
        for rank in range(2, 16):
            for i in range(1, player_cards[rank]+1):
                cards_info += cardsRank[rank] + " "
        
        # 私发补牌和手牌信息
        # print(self.poker[player][0])
        self.context.appText(f"你抽到了{cardsRank[card]}，\n现在你的所有牌是：{cards_info}", "whisper", to=self.poker[player][0])
        return True

    def cardLegalityCheck(self, player, command):
        """检查玩家出牌的合法性并处理出牌"""
        command = command.upper().replace("J", "11").replace("Q", "12").replace("K", "13").replace("A", "14")
        player_name = self.poker[player][0]
        joker_text = ""
        # 检查游戏状态和进行状态转换
        def checkGameState():
            # 检查是否出完所有牌
            if sum(self.poker[player][1][1:15]) == 0:
                self.context.appText(f"玩家{player_name}出完了所有的牌！")
                if self.multipleTurn["players"]:
                    self.endMultipleTurn(player)  # 结束倍数轮
                self.handleGameEnd(player)
                return True
            return False

        # 第一阶段强制出炸处理
        if self.gamePhase == 1 and player != 1:  # 非1号玩家在第一阶段
            force_bomb = self.checkFirstPhaseForce(player)
            if force_bomb:
                if not (command.endswith("*3") or command.endswith("*4") or command.endswith("*5") or command.endswith("*6") or command.endswith("*7")):
                    return self.context.appText("第一阶段有炸弹则必须出炸弹！再不出瓦达西就生气了")
                # 处理开门炸

        # 解析牌型
        # 单张
        if re.match(r"^\d+$", command):
            if not self.upCardsKind in ["空","单张"]:
                return self.context.appText("泥的牌打不了上家的牌！")
            
            card = int(command)
            if not (1 <= card <= 14):  # A-K
                return self.context.appText("无效的牌面值！")
            
            if self.poker[player][1][card] < 1:
                return self.context.appText("泥没有这张牌，讨厌欸")
            
            # 检查是否能打过上家
            if self.upCards and self.upCards.isdigit():
                if self.upCards == "2":
                    return self.context.appText("泥的牌打不过上家的2！")
                if card != int(self.upCards) + 1 and card != 2:
                    return self.context.appText(f"您的牌打不过上家的{self.upCardsInfo}！")
            
            # 出牌
            self.upCards = str(card)
            self.upCardsInfo = cardsRank[card]
            self.upPlayer = player
            self.next_player = (player % self.playerNumero) + 1
            self.upCardsKind = "单张"
            self.checkPass = 0
            self.latestPlayer = player
            self.poker[player][1][card] -= 1
            self.context.appText(f"{player_name}出了{cardsRank[card]}，@轮到{self.poker[self.next_player][0]} 出牌")
            self.playedCards[player] = True
            return not checkGameState()

        # 对子
        elif re.match(r"^\d+\*2$", command):
            if not self.upCardsKind in ["空","对子"]:
                return self.context.appText("泥的牌打不了上家的牌！") 
            
            card = int(command.split("*")[0])
            if not (1 <= card <= 14):
                return self.context.appText("无效的牌面值！")
            
            # 检查是否需要使用癞子
            can_play, jokers_needed, joker_positions = self.findBestJokerCombo(self.poker[player][1], command)
            if not can_play and self.poker[player][1][card] < 2:
                return self.context.appText("您没有足够的牌且癞子不足！")
            
            # 检查是否能打过上家
            if self.upCards and "*2" in self.upCards:
                up_card = int(self.upCards.split("*")[0])
                if up_card == 2:
                    return self.context.appText("泥的对子打不过上家的对2！")
                if card != up_card + 1 and card != 2:
                    return self.context.appText(f"泥的对子打不过上家的对{cardsRank[up_card]}！")

            # 出牌逻辑
            if jokers_needed > 0:
                self.poker[player][1][14] -= jokers_needed
                joker_text = self.formatJokerUsage(joker_positions)
                self.poker[player][1][card] -= 2 - jokers_needed
            else:
                self.poker[player][1][card] -= 2
            
            # 出牌
            self.upCards = f"{card}*2"
            self.upCardsInfo = f"{cardsRank[card]}\\*2" + joker_text
            self.upPlayer = player
            self.next_player = (player % self.playerNumero) + 1
            self.upCardsKind = "对子"
            self.checkPass = 0
            self.latestPlayer = player
            self.context.appText(f"{player_name}出了对{cardsRank[card]}，轮到@{self.poker[self.next_player][0]} 出牌")#wawa这里已经改过了 owob self.poker[player][0]是昵称 self.poker[player][1]是牌桶
            self.playedCards[player] = True
            return not checkGameState()

        # 顺子
        elif re.match(r"^\d+-\d+$", command):
            if not self.upCardsKind in ["空","顺子"]:
                return self.context.appText("泥的牌打不了上家的牌！") 
            start, end = map(int, command.split("-"))
            if not (1 <= start <= 14 and 1 <= end <= 14):
                return self.context.appText("无效的牌面值！")
            if end <= start:
                return self.context.appText("顺子的结束值必须大于起始值！拜托🙏")
            if 2 in range(start, end + 1):
                return self.context.appText("2不能加入顺子♿♿♿")
            
            # 检查是否需要使用癞子
            can_play, jokers_needed, joker_positions = self.findBestJokerCombo(self.poker[player][1], command)
            if not can_play:
                return self.context.appText("泥没有足够的牌组成顺子且癞子不足，哭哭")
            
            # 检查是否能打过上家
            if self.upCards and "-" in self.upCards and "*" not in self.upCards:
                up_start, up_end = map(int, self.upCards.split("-"))
                if up_end - up_start != end - start:
                    return self.context.appText("顺子长度必须相同！")
                if start != up_start + 1:
                    return self.context.appText(f"您的顺子打不过上家的顺子！")
                
            # 出牌逻辑
            if jokers_needed > 0:
                self.poker[player][1][15] -= jokers_needed
                joker_text = self.formatJokerUsage(joker_positions)
                for card in range(start, end + 1):
                    self.poker[player][1][card] -= 1 * (self.poker[player][1][card] >= 1)
            else:
                for card in range(start, end + 1):
                    self.poker[player][1][card] -= 1

            # 出牌
            self.upCards = f"{start}-{end}"
            self.upCardsInfo = f"{cardsRank[start]}-{cardsRank[end]}" + joker_text
            self.upPlayer = player
            self.next_player = (player % self.playerNumero) + 1
            self.upCardsKind = "顺子"
            self.checkPass = 0
            self.latestPlayer = player
            self.context.appText(f"{player_name}出了顺子{self.upCardsInfo}，轮到@{self.poker[self.next_player][0]} 出牌")
            self.playedCards[player] = True
            return not checkGameState()

        # 双顺
        elif re.match(r"^\d+-\d+\*2$", command):
            if not self.upCardsKind in ["空","双顺"]:
                return self.context.appText("泥的牌打不了上家的牌！")
            start, end = map(int, command.split("*")[0].split("-"))
            if not (1 <= start <= 14 and 1 <= end <= 14):
                return self.context.appText("无效的牌面值！😡😡😡")
            if end <= start:
                return self.context.appText("顺子的结束值必须大于起始值！就离谱")
            if 2 in range(start, end + 1):
                return self.context.appText("2不能加入顺子！(￣y▽,￣)╭ ")

            # 检查是否需要使用癞子
            can_play, jokers_needed, joker_positions = self.findBestJokerCombo(self.poker[player][1], command)
            if not can_play:
                return self.context.appText("泥没有足够的牌组成双顺且癞子不足嘤嘤嘤")
            
            # 出牌逻辑
            if jokers_needed > 0:
                self.poker[player][1][15] -= jokers_needed
                joker_text = self.formatJokerUsage(joker_positions)
                for card in range(start, end + 1):
                    self.poker[player][1][card] -= 2 * (self.poker[player][1][card] >= 2)
            else:
                for card in range(start, end + 1):
                    self.poker[player][1][card] -= 2
            
            # 检查是否能打过上家
            if self.upCards and "*2" in self.upCards:
                up_start, up_end = map(int, self.upCards.split("*")[0].split("-"))
                if up_end - up_start != end - start:
                    return self.context.appText("双顺长度必须相同！")
                if start != up_start+1:
                    return self.context.appText(f"泥的双顺打不过上家的双顺！😠😿")

            # 出牌
            self.upCards = f"{start}-{end}*2"
            self.upCardsInfo = f"{cardsRank[start]}-{cardsRank[end]}\\*2" + joker_text
            self.upPlayer = player
            self.next_player = (player % self.playerNumero) + 1
            self.upCardsKind = "双顺"
            self.checkPass = 0
            self.latestPlayer = player
            self.context.appText(f"{player_name}出了双顺{self.upCardsInfo}，轮到@{self.poker[self.next_player][0]} 出牌力")
            self.playedCards[player] = True
            return not checkGameState()

        # 炸弹
        elif re.match(r"^\d+\*\d+$", command):  # 炸弹
            card = int(command.split("*")[0])
            bomb_size = int(command.split("*")[1])
            # 检查是否需要使用癞子
            can_play, jokers_needed, joker_positions = self.findBestJokerCombo(self.poker[player][1], command)
            if not can_play and self.poker[player][1][card] < bomb_size:
                return self.context.appText("你没有足够的牌组成炸弹且癞子不足！主播主播还有没有比炸弹更强势的牌呀(p≧w≦q)")
            bomb = (card, bomb_size, jokers_needed)  # 炸弹信息
            # 检查炸弹大小
            if self.upCards:
                tmp = self.compareBombLevel (bomb, self.upBomb)
                if tmp == 0 or tmp == -1:
                    return self.context.appText("你的炸弹打不过上家的炸弹！哼〒▽〒")
                
            # 出牌逻辑
            if jokers_needed > 0:
                self.poker[player][1][15] -= jokers_needed
                joker_text = self.formatJokerUsage(joker_positions)
                self.poker[player][1][card] -= bomb_size - jokers_needed
            else:
                self.poker[player][1][card] -= bomb_size

            # 出牌
            self.upCards = f"{card}*{bomb_size}"
            self.upCardsInfo = f"{cardsRank[card]}\\*{bomb_size}" + joker_text
            self.upBomb = bomb
            self.upCardsKind = "炸弹"
            self.next_player = (player % self.playerNumero) + 1
            self.checkPass = 0
            self.latestPlayer = player
            self.context.appText(f"{player_name}出了炸弹{self.upCardsInfo}，轮到@{self.poker[self.next_player][0]} 出牌")
            self.playedCards[player] = True

            # 处理倍数轮
            initial_multiple = 2
            if self.gamePhase == 1 and player != 1:  # 非1号玩家在第一阶段
                initial_multiple *= 2  # 第一阶段倍数为1
                self.gamePhase = 2  # 进入第二阶段
            if self.upCardsKind == "炸弹":
                initial_multiple *= 2 # 反炸初始倍数翻倍
            if self.upCardsKind in ["单张","对子"]:
                if self.upCards[0] == card or self.upCards[0] + 1 == card:
                    initial_multiple *= 2 # 冒头炸初始倍数翻倍

            if not self.upCardsKind == "空" and self.upPlayer != 0 and self.upPlayer != player:
                if self.multipleTurn["players"] and player not in self.multipleTurn["players"]:
                    self.endMultipleTurn(self.upPlayer)  # 结束倍数轮
                self.updateMultipleTurn(player, self.upPlayer, initial_multiple)  # 更新倍数轮
            self.upPlayer = player
            return not checkGameState()

        else:
            return self.context.appText("无效的出牌格式！")

    def handleGameEnd(self, winner):
        """处理游戏结束"""
        # 计算上供
        for player in range(1, self.playerNumero+1):
            if player != winner:
                tribute = self.calculateTribute(self.poker[player][1])
                # 检查春天
                if not self.playedCards[player]:
                    tribute *= 2
                    self.context.appText(f"{self.poker[player][0]}被春天了！上供翻倍！")
                self.playerMoney[winner] += tribute
                self.playerMoney[player] -= tribute
                self.context.appText(f"=={self.poker[player][0]}==上供{tribute}块钱给=={self.poker[winner][0]}==！")
        
        # 显示最终结果
        self.context.appText("游戏结束！最终金钱情况：")
        for player in range(1, self.playerNumero+1):
            self.context.appText(f"{self.poker[player][0]}: {self.playerMoney[player]}块钱")
        
        # 找出赢家
        final_winner = max(self.playerMoney.items(), key=lambda x: x[1])[0]
        self.context.appText(f"恭喜=={self.poker[final_winner][0]}==最后赚钱钱了！")
        self.initInit()

    def playCard(self, player: int, command: str):
        # 处理cards命令
        if self.gamePhase == 0:
            if command.startswith("cards"):
                if self.gamePhase == 0:
                    try:
                        self.num_decks = int(command.split()[1])  # 获取牌组数量
                    except (IndexError, ValueError):
                        self.context.appText("请输入正确的牌组数量，例如：g cards 2")
                    else:
                        if self.num_decks < 1 or game.num_decks > 10:
                            self.context.appText("牌组数量必须在1-10之间哦！")
                            return
                        self.start()
                else:
                    self.context.appText("游戏已经开始了，不能更改牌组数量！")
                return
            else:
                return
        elif " " in command:
            return self.context.appText("无效的牌面值！不要有空格啦")
        #出牌

        if command == "check":
            self.checkCard(player)
            return

        if self.next_player and player != self.next_player:
            return self.context.appText(f"现在是{self.poker[self.next_player][0]}的回合哦！请等ta出牌")

        if command == ".":
            if self.upCardsKind == "空":
                return self.context.appText("这是你的回合，必须出牌哦~")
            self.checkPass += 1 # 记录过牌次数
            self.next_player = (self.next_player % self.playerNumero) + 1
            # 检查是否需要结束大轮
            if self.checkPass >= self.playerNumero - 1:
                if self.gamePhase == 3:
                    self.context.appText(f"无人能打，{self.poker[self.latestPlayer][0]}继续出牌")
                else:
                    self.endRound()
            else:
                self.context.appText(f"{self.poker[player][0]} 不想出（哼哼，那就轮到@{self.poker[self.next_player][0]} 出牌了")
            return
        elif command == "":
            self.context.appText("雅达雅达（波奇摇头）\n![](https://img.duotegame.com/article/contents/2022/10/31/small_2022103134200180.gif)")
            return
        else:
            self.cardLegalityCheck(player, command)
            return

    def start(self):
        """游戏开始函数"""
        self.dealCards()
        self.gamePhase = 1
        # 随机打乱玩家顺序并分配编号
        random.shuffle(self.players)

        # 初始化self.playedCards
        self.playedCards = {i+1: False for i in range(self.playerNumero)}

        # 将玩家昵称保存到self.poker
        for i in range(self.playerNumero):
            self.poker[i+1][0] = self.players[i]
            self.context.appText(f"{self.players[i]}被随机分配到了{i+1}号位置")
        
        # 抽取一张牌作为1号玩家的初始出牌
        first_card = self.deck.pop()
        while first_card in (2, 15):  # 如果抽到2或大小王
            self.playerMoney[1] -= 10
            self.playerMoney[2] += 10
            self.context.appText(f"{self.poker[1][0]}好点背hh，抽到了{cardsRank[first_card]}，扣10块钱,2号玩家得10块钱！ww")
            first_card = self.deck.pop()  # 重新抽牌

        self.upCards = str(first_card)
        self.upPlayer = 1 # 1号玩家出牌
        self.upCardsKind = "单张" # 初始出牌类型
        self.upCardsInfo = cardsRank[first_card] # 初始出牌信息
        self.upBomb = (0,0,0) # 炸弹信息
        self.next_player = 2 # 下一个出牌的玩家
        self.latestPlayer = 1 # 最近出牌的玩家
        for i in range(self.playerNumero):
            self.checkCard(i+1)
        # 发送初始牌信息
        self.context.appText(f"游戏开始！{self.poker[1][0]}的初始牌是{cardsRank[first_card]},接下来由=={self.poker[2][0]}==出牌")
        # 游戏阶段提示
        self.context.appText("第一阶段开始！如果有炸弹必须出炸！！！（悄悄提示，开门炸会有特殊奖赏哦")

game = DryEye()

def main(context, sender: str, command: str):
    game.context = context
    if command == "规则":
        context.appText(DERULE)
    elif command == "help":
        context.appText(DERMENU)
    # 处理加入命令
    elif command == "加入":
        if game.gamePhase > 0:
            context.appText(f"抱歉呢{sender}，已经开始了，等下一局吧~")
        elif sender in game.players:
            context.appText(f"啊咧咧，{sender}已经在游戏中了呢，不能重复加入哦╮(╯▽╰)╭")
        else:
            game.players.append(sender)
            context.appText(f"{sender}加入了游戏！(已加入{len(game.players)}人)")
    # 处理开始命令
    elif command == "开始":
        if game.gamePhase > 0:
            context.appText(f"抱歉呢{sender}，已经开始了，等下一局吧~")
        elif sender not in game.players:
            context.appText(f"{sender}都还没加入游戏呢，开始啥(｡ŏ_ŏ)")
        elif len(game.players) >= 2:
            game.initGame()
            game.playerNumero = len(game.players) # 玩家数量
            context.appText(f"共有{len(game.players)}名玩家参与，游戏即将开始！请发送g cards [number]告诉我想打几副牌哦！")
        else:
            context.appText("至少需要两个人才能开始游戏，加入更多玩家吧(～￣▽￣)～")
    elif command == "退出":
        if game.gamePhase > 0:
            context.appText(f"抱歉呢{sender}，已经开始了，等下一局吧~")
        elif sender not in game.players:
            context.appText(f"啊咧咧，{sender}已经不在游戏中了呢，不能重复退出哦╮(╯▽╰)╭")
        else:
            game.players.remove(sender)
            context.appText(f"{sender}退出了游戏！(已加入{len(game.players)}人)")
    # 处理结束命令
    elif command == "结束":
        if sender not in game.players:
            context.appText(f"{sender}都还没加入游戏呢，结束啥(｡ŏ_ŏ)")
        else:
            context.appText("游戏被迫终止了...下次再来玩吧QAQ")
            game.initInit()
    # 处理游戏中的命令
    elif sender in game.players and not game.gameEnded:
        player_index = game.players.index(sender) + 1  # 获取玩家编号(1-game.playerNumero)
        game.playCard(player_index, command)