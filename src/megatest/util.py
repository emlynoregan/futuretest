import time

def DateTimeToUnixTimestampMicrosec(aDateTime):
    return long(time.mktime(aDateTime.timetuple()) * 1000000 + aDateTime.microsecond) if aDateTime else 0
