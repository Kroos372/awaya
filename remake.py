#coding=utf-8
# 用于清除数据。按说应该提醒你一下谨慎的，不过无所谓啦
import json
def dec(cont: str) -> str:
    if cont.startswith(u"\ufeff"):
        return cont.encode("utf8")[3:].decode("utf8")
    else:
        return cont
with open("files/hash.json", "w", encoding="utf8") as f:
    f.write("{}")
with open("files/userData.json", "r", encoding="utf8") as f:
    userData = json.loads(dec(f.read()))
userData["lastSaw"] = {}
with open("files/userData.json", "w", encoding="utf8") as f:
    json.dump(userData, fp=f, ensure_ascii=False, indent=2)