import time
import datetime


def update_txt_log(timestamp, humidity, temperature, light_on, moisterizer_on, ventil_on):
	line = f"\n| {timestamp} |        {humidity}%         |    {temperature}°C     |  {'an' if light_on else 'aus'}   |     {'an' if moisterizer_on else 'aus'}     |  {'an' if ventil_on else 'aus'}   |"
	with open("log.txt",'a') as file :
		file.write(line)

for counter in range(10):
	update_txt_log(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), counter, counter, True, True, False)
	time.sleep(2)