import utime
import ntptime
from machine import RTC

# winter offset and summer offset set for Britain. use 1 and 2 for CET
def sync_localtime(woff=-4,soff=-5):
    trials = 10
    while trials > 0:
        try:
            ntptime.host = "ca.pool.ntp.org"
            ntptime.settime()
            break
        except Exception as e:
            print(".", end="")
        utime.sleep(1)
        trials -= 1

        if trials == 0:
            print(str(e))
        return

    t = utime.time()
    tm = list(utime.localtime(t))
    tm = tm[0:3] + [0,] + tm[3:6] + [0,]
    year = tm[0]

    #Time of March change for the current year
    t1 = utime.mktime((year,3,(31-(int(5*year/4+4))%7),1,0,0,0,0))
    #Time of October change for the current year
    t2 = utime.mktime((year,10,(31-(int(5*year/4+1))%7),1,0,0,0,0))

    if t >= t1 and t < t2:
        tm[4] += soff #UTC + 1H for BST
    else:
        tm[4] += woff #UTC + 0H otherwise

    RTC().datetime(tm)
    print('Synced datetime with NTP...')
    print(utime.localtime())