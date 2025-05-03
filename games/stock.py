from static import bank, random, Context, now, timeDiff, writeJson, nowDay, readJson
import math, time
from typing import List, Dict, Tuple

STOCKMENU = "\n".join([
    "Lounge 股票(Code:LGST)模拟炒股系统",
    "st 买入 <股数>: 以当前价格买入指定数量的股票",
    "st 卖出 <股数>: 以当前价格卖出指定数量的股票", 
    "st 持有: 查看自己持有的股票数量和当前价值",
    "st 行情: 查看当前股价、技术指标和趋势图",
    "st 排行: 查看持股排行榜",
    "st 分析: 查看详细技术分析"
])

class Stock:
    def __init__(self):
        self.load_data()
    
    def load_data(self):
        try:
            data = readJson("userData.json")
            if "stock" in data:
                stock_data = data["stock"]
                self.base_price = stock_data.get("base_price", 100)
                self.current_price = stock_data.get("current_price", self.base_price)
                self.price_history = stock_data.get("price_history", [self.current_price])
                self.volume_history = stock_data.get("volume_history", [0] * len(self.price_history))
                self.holdings = stock_data.get("holdings", {})
                self.last_update = stock_data.get("last_update", now())
                self.last_trend = stock_data.get("last_trend", 0)
                self.trend_streak = stock_data.get("trend_streak", 0)
                self.high_price = stock_data.get("high_price", self.current_price)
                self.low_price = stock_data.get("low_price", self.current_price)
                self.open_price = stock_data.get("open_price", self.current_price)
                self.market_sentiment = stock_data.get("market_sentiment", 0)  # 市场情绪(-1到1)
            else:
                self.initStock()
        except:
            self.initStock()
    
    def save_data(self):
        data = readJson("userData.json")
        data["stock"] = {
            "base_price": self.base_price,
            "current_price": self.current_price,
            "price_history": self.price_history,
            "volume_history": self.volume_history,
            "holdings": self.holdings,
            "last_update": self.last_update,
            "last_trend": self.last_trend,
            "trend_streak": self.trend_streak,
            "high_price": self.high_price,
            "low_price": self.low_price,
            "open_price": self.open_price,
            "market_sentiment": self.market_sentiment
        }
        writeJson("userData.json", data)
    
    def initStock(self):
        self.base_price = 100
        self.current_price = self.base_price
        self.price_history = [self.current_price]
        self.volume_history = [0]
        self.holdings = {}
        self.last_update = now()
        self.update_interval = 1
        self.last_trend = 0
        self.trend_streak = 0
        self.high_price = self.current_price
        self.low_price = self.current_price
        self.open_price = self.current_price
        self.market_sentiment = 0
    
    def calculate_ma(self, period: int) -> float:
        if len(self.price_history) < period:
            return self.current_price
        return sum(self.price_history[-period:]) / period
    
    def calculate_volume_ma(self, period: int) -> float:
        if len(self.volume_history) < period:
            return sum(self.volume_history) / len(self.volume_history) if self.volume_history else 0
        return sum(self.volume_history[-period:]) / period
    
    def calculate_rsi(self) -> float:
        if len(self.price_history) < 14:
            return 50.0
        
        gains = []
        losses = []
        for i in range(1, 14):
            change = self.price_history[-i] - self.price_history[-i-1]
            if change >= 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(-change)
        
        avg_gain = sum(gains) / 14
        avg_loss = sum(losses) / 14
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def calculate_macd(self) -> Tuple[float, float, float]:
        if len(self.price_history) < 26:
            return 0.0, 0.0, 0.0
            
        ema12 = self.calculate_ema(12)
        ema26 = self.calculate_ema(26)
        macd_line = ema12 - ema26
        signal_line = self.calculate_ema(9, [macd_line])
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram

    def calculate_ema(self, period: int, data: List[float] = None) -> float:
        if data is None:
            data = self.price_history
        
        if len(data) < period:
            return data[-1] if data else 0
            
        alpha = 2 / (period + 1)
        ema = data[-period]
        for price in data[-period+1:]:
            ema = price * alpha + ema * (1 - alpha)
        return ema

    def calculate_bollinger_bands(self) -> Tuple[float, float, float]:
        if len(self.price_history) < 20:
            return self.current_price, self.current_price, self.current_price
            
        ma20 = self.calculate_ma(20)
        std = math.sqrt(sum((x - ma20) ** 2 for x in self.price_history[-20:]) / 20)
        
        upper_band = ma20 + (2 * std)
        lower_band = ma20 - (2 * std)
        
        return upper_band, ma20, lower_band

    def update_price(self):
        current_time = now()
        if current_time - self.last_update < self.update_interval:
            return False
            
        # 计算技术指标
        ma5 = self.calculate_ma(5)
        ma20 = self.calculate_ma(20)
        rsi = self.calculate_rsi()
        macd_line, signal_line, histogram = self.calculate_macd()
        upper_band, _, lower_band = self.calculate_bollinger_bands()
        
        # 根据技术指标和市场情绪调整趋势概率
        trend_prob = 0.5 + (self.market_sentiment * 0.2)  # 市场情绪影响
        
        # 均线系统影响
        if ma5 > ma20:  # 金叉
            trend_prob += 0.15
        elif ma5 < ma20:  # 死叉
            trend_prob -= 0.15
            
        # RSI影响
        if rsi > 70:  # 超买
            trend_prob -= 0.1
        elif rsi < 30:  # 超卖
            trend_prob += 0.1
            
        # MACD影响
        if histogram > 0 and histogram > self.calculate_macd()[2]:  # MACD柱状图上升
            trend_prob += 0.1
        elif histogram < 0 and histogram < self.calculate_macd()[2]:  # MACD柱状图下降
            trend_prob -= 0.1
            
        # 布林带影响
        if self.current_price > upper_band:
            trend_prob -= 0.15
        elif self.current_price < lower_band:
            trend_prob += 0.15
            
        # 确保概率在合理范围内
        trend_prob = max(0.1, min(0.9, trend_prob))
            
        # 决定价格变动方向
        if self.last_trend != 0 and random.random() < 0.7:
            trend = self.last_trend
            self.trend_streak += 1
        else:
            trend = 1 if random.random() < trend_prob else -1
            if trend != self.last_trend:
                self.trend_streak = 1
            else:
                self.trend_streak += 1
        
        self.last_trend = trend
        
        # 计算波动率
        base_volatility = random.uniform(0.05, 0.15)
        if self.trend_streak > 1:
            volatility = min(base_volatility * (1 + 0.1 * self.trend_streak), 0.25)
        
        # 考虑成交量影响
        avg_volume = self.calculate_volume_ma(5)
        if avg_volume > 0:
            volume_factor = sum(self.volume_history[-1:]) / avg_volume
            volatility *= (1 + (volume_factor - 1) * 0.1)
            
        # 大单交易影响
        if len(self.volume_history) > 0 and self.volume_history[-1] > avg_volume * 2:
            volatility *= 1.5  # 大单交易增加波动率
            self.market_sentiment = max(-1, min(1, self.market_sentiment + (0.1 * trend)))  # 大单影响市场情绪
        
        # 计算新价格
        change = self.current_price * volatility * trend
        self.current_price = max(10, self.current_price + change)
        
        # 更新最高最低价
        self.high_price = max(self.high_price, self.current_price)
        self.low_price = min(self.low_price, self.current_price)
        
        # 更新历史数据
        self.price_history.append(self.current_price)
        if len(self.price_history) > 48:
            self.price_history.pop(0)
            self.volume_history.pop(0)
        
        # 市场情绪自然衰减
        self.market_sentiment *= 0.95
        
        self.last_update = current_time
        self.save_data()
        return True
    
    def buy(self, trip: str, amount: int) -> str:
        if amount <= 0:
            return "购买数量必须为正数"
        
        self.update_price()
        total_cost = math.ceil(self.current_price * amount)
        
        if bank.hasMoney(trip, total_cost) != total_cost:
            return f"您的余额不足，需要{total_cost}阿瓦豆，但您只有{bank.get(trip)['money']}阿瓦豆"
        
        bank.delete(trip, total_cost)
        
        if trip not in self.holdings:
            self.holdings[trip] = 0
        self.holdings[trip] += amount
        
        # 记录成交量
        self.volume_history.append(amount)
        self.save_data()
        
        return f"成功以单价{self.current_price:.2f}阿瓦豆买入{amount}股Lounge 股票(Code:LGST)，共花费{total_cost}阿瓦豆"
    
    def sell(self, trip: str, amount: int) -> str:
        if amount <= 0:
            return "卖出数量必须为正数"
        
        if trip not in self.holdings or self.holdings[trip] < amount:
            current_amount = self.holdings.get(trip, 0)
            return f"您只持有{current_amount}股，无法卖出{amount}股"
        
        self.update_price()
        total_gain = math.floor(self.current_price * amount)
        
        self.holdings[trip] -= amount
        if self.holdings[trip] == 0:
            del self.holdings[trip]
        
        bank.add(trip, total_gain)
        
        # 记录成交量
        self.volume_history.append(amount)
        self.save_data()
        
        return f"成功以单价{self.current_price:.2f}阿瓦豆卖出{amount}股Lounge 股票(Code:LGST)，共获得{total_gain}阿瓦豆"
    
    def check_holdings(self, trip: str) -> str:
        self.update_price()
        
        if trip not in self.holdings or self.holdings[trip] == 0:
            return "您当前未持有Lounge"
        
        amount = self.holdings[trip]
        total_value = math.floor(self.current_price * amount)
        
        return f"您当前持有{amount}股Lounge 股票(Code:LGST)，当前单价{self.current_price:.2f}阿瓦豆，总价值约{total_value}阿瓦豆"
    
    def get_market_info(self) -> str:
        self.update_price()
        
        # 计算技术指标
        ma5 = self.calculate_ma(5)
        ma20 = self.calculate_ma(20)
        avg_volume = self.calculate_volume_ma(5)
        
        # 计算24小时变化趋势
        if len(self.price_history) > 1:
            change = self.price_history[-1] - self.price_history[0]
            change_percent = (change / self.price_history[0]) * 100
            trend_str = f"{'上涨' if change >= 0 else '下跌'}{abs(change_percent):.2f}%"
        else:
            trend_str = "持平 0.00%"
        
        # 生成趋势图
        chart = self._generate_chart()
        
        result = [
            "### Lounge 股票(Code:LGST)行情",
            f"当前价格: **{self.current_price:.2f}**阿瓦豆",
            f"MA5: {ma5:.2f}",
            f"MA20: {ma20:.2f}",
            f"5日均量: {avg_volume:.2f}",
            f"24小时趋势: {trend_str}",
            "",
            "### 价格走势图:",
            chart,
            "",
            f"下次更新时间: {timeDiff(self.update_interval - (now() - self.last_update))}后"
        ]
        
        return "\n".join(result)
    
    def _generate_chart(self) -> str:
        if not self.price_history:
            return "暂无数据"
        
        # 计算图表大小
        chart_height = 10
        chart_width = len(self.price_history)
        
        # 找出最高和最低价格
        min_price = min(self.price_history)
        max_price = max(self.price_history)
        price_range = max(max_price - min_price, 1)  # 防止除零错误
        
        # 生成图表
        chart = []
        for y in range(chart_height, 0, -1):
            line = []
            threshold = min_price + (price_range * (y - 1) / chart_height)
            for price in self.price_history:
                if price >= threshold:
                    line.append("▓")
                else:
                    line.append(" ")
            chart.append("".join(line))
        
        # 添加价格标签
        chart.append("─" * chart_width)
        max_label = f"{max_price:.1f}"
        min_label = f"{min_price:.1f}"
        chart.insert(0, max_label)
        chart.append(min_label)
        
        return "```\n" + "\n".join(chart) + "\n```"
    
    def get_ranking(self) -> str:
        self.update_price()
        
        if not self.holdings:
            return "当前没有用户持有"
        
        # 计算每个用户持股的总价值
        rankings = []
        for trip, amount in self.holdings.items():
            total_value = math.floor(self.current_price * amount)
            rankings.append((trip, amount, total_value))
        
        # 按总价值排序
        rankings.sort(key=lambda x: x[2], reverse=True)
        
        result = ["### Lounge 股票(Code:LGST)持股排行"]
        for i, (trip, amount, value) in enumerate(rankings[:10], 1):
            result.append(f"{i}. {trip}: {amount}股，价值约{value}阿瓦豆")
        
        return "\n".join(result)

    def get_technical_analysis(self) -> str:
        self.update_price()
        
        rsi = self.calculate_rsi()
        macd_line, signal_line, histogram = self.calculate_macd()
        upper_band, ma20, lower_band = self.calculate_bollinger_bands()
        
        # 生成技术分析结论
        analysis = []
        analysis.append("### 技术指标分析")
        
        # RSI分析
        analysis.append("\n📊 RSI指标:")
        analysis.append(f"当前RSI: {rsi:.2f}")
        if rsi > 70:
            analysis.append("⚠️ RSI超买，可能面临回调风险")
        elif rsi < 30:
            analysis.append("💡 RSI超卖，可能存在反弹机会")
        
        # MACD分析
        analysis.append("\n📈 MACD指标:")
        analysis.append(f"MACD线: {macd_line:.3f}")
        analysis.append(f"信号线: {signal_line:.3f}")
        analysis.append(f"MACD柱: {histogram:.3f}")
        if histogram > 0 and histogram > self.calculate_macd()[2]:
            analysis.append("💹 MACD柱状图上升，上升趋势增强")
        elif histogram < 0 and histogram < self.calculate_macd()[2]:
            analysis.append("📉 MACD柱状图下降，下降趋势增强")
        
        # 布林带分析
        analysis.append("\n📊 布林带:")
        analysis.append(f"上轨: {upper_band:.2f}")
        analysis.append(f"中轨: {ma20:.2f}")
        analysis.append(f"下轨: {lower_band:.2f}")
        if self.current_price > upper_band:
            analysis.append("⚠️ 价格突破上轨，可能存在回调风险")
        elif self.current_price < lower_band:
            analysis.append("💡 价格突破下轨，可能存在反弹机会")
        
        # K线形态
        analysis.append("\n📊 K线分析:")
        analysis.append(f"开盘价: {self.open_price:.2f}")
        analysis.append(f"最高价: {self.high_price:.2f}")
        analysis.append(f"最低价: {self.low_price:.2f}")
        analysis.append(f"当前价: {self.current_price:.2f}")
        
        # 市场情绪
        analysis.append("\n🌡️ 市场情绪:")
        sentiment = self.market_sentiment
        if sentiment > 0.5:
            analysis.append("市场情绪非常乐观")
        elif sentiment > 0:
            analysis.append("市场情绪偏向乐观")
        elif sentiment < -0.5:
            analysis.append("市场情绪非常悲观")
        elif sentiment < 0:
            analysis.append("市场情绪偏向悲观")
        else:
            analysis.append("市场情绪中性")
        
        return "\n".join(analysis)

# 创建全局实例
stock = Stock()

def main(context: Context, sender: str, msg: str, trip: str=""):
    if not msg:
        return context.appText(STOCKMENU)
    
    if not trip:
        return context.appText("你还没有识别码，无法使用股票功能!")
    
    if msg == "帮助" or msg == "help":
        context.appText(STOCKMENU)
    elif msg == "行情":
        context.appText(stock.get_market_info())
    elif msg == "持有":
        context.appText(stock.check_holdings(trip))
    elif msg == "排行":
        context.appText(stock.get_ranking())
    elif msg == "分析":
        context.appText(stock.get_technical_analysis())
    elif msg.startswith("买入 "):
        try:
            amount = int(msg[3:])
            context.appText(stock.buy(trip, amount))
        except ValueError:
            context.appText("请输入正确的数量")
    elif msg.startswith("卖出 "):
        try:
            amount = int(msg[3:])
            context.appText(stock.sell(trip, amount))
        except ValueError:
            context.appText("请输入正确的数量")
    else:
        context.appText(f"未知命令，请查看{STOCKMENU}") 