def SetTimeFunction(fSetTime, TIME_UNIT):
    seconds = float(fSetTime)
    if TIME_UNIT == '分钟':
        seconds = seconds * 60.0
    elif TIME_UNIT == '秒':
        seconds = seconds
    elif TIME_UNIT == '毫秒':
        seconds = seconds / 1000.0
    return int(round(seconds * 10))
