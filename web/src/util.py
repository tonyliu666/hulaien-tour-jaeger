import time
def GetCurrentTime():
    nowTime = int(time.time()) # 取得現在時間
    struct_time = time.localtime(nowTime) # 轉換成時間元組
    timeString = time.strftime('%Y-%m-%d %H:%M:%S', struct_time)
    return timeString