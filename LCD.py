import drivers
from time import sleep
from datetime import datetime
from subprocess import check_output

display = drivers.Lcd()
IP = check_output(['hostname', '-I'], encoding='utf8').split()[0]
HOSTNAME = check_output('hostname', encoding='utf8')
try:
     display.lcd_display_string(str(HOSTNAME), 1)
     display.lcd_display_string(str(IP), 2)
except KeyboardInterrupt:
     print('Cleaning up')
     display.lcd_clear()
