from enum import IntEnum

class Settings:
    start_cash = 1500
    mortgage = False
    vacation_cash = False
    poor_prison = False # 在监狱不能收租
    auction = False

class Status(IntEnum):
    CLOSED = 0
    BEFORE_ROLL = 1
    BEFORE_DOUBLE = 2
    AFTER_ROLL = 3
    AUCTION = 4
    ENDING = 5

DICES = ["", "⚀", "⚁", "⚂", "⚃", "⚄", "⚅"]