import sys
import astropy
from astropy import coordinates as coord
from astropy import time
from astropy import units as u
from datetime import datetime, timedelta
from dateutil import tz
import json

class Observer(object):
	def __init__(self):
		posinfo = json.load(open('location.json'))
		loc = coord.EarthLocation(**posinfo)
		timeinfo = json.load(open('obswindow.json'))
		#start = time.Time(timeinfo['start'], format='iso')
		#stop  = time.Time(timeinfo['end'], format='iso')
		#step  = time.TimeDelta(timeinfo['steps'], format='sec')
		#times = [start]
		hourranges = timeinfo['hourranges']
		from_zone = tz.gettz(timeinfo['timezone'])
		to_zone = tz.tzutc()
		start = datetime.strptime(timeinfo['start'], '%Y-%m-%d %H:%M:%S').replace(tzinfo=from_zone)
		stop = datetime.strptime(timeinfo['stop'], '%Y-%m-%d %H:%M:%S').replace(tzinfo=from_zone)
		step = timedelta(seconds=timeinfo['steps'])

		times = []
		tcur = start
		while tcur < stop:
			#if any([time.datetime.hour >= lo and time.datetime.hour <= hi  for lo, hi in hourranges]):
			if any([tcur.hour >= lo and tcur.hour <= hi for lo, hi in hourranges]):
				times.append(time.Time(tcur.astimezone(to_zone), format='datetime'))
			tcur += step
		self.times = times
		self.loc = loc
		self.timeinfo = timeinfo
		self.posinfo = posinfo
		self.minalt = self.timeinfo['minalt']
		self.altaz = coord.AltAz(obstime=self.times, location=self.loc)

	def observable(self, radec):
		coords = coord.SkyCoord(radec, frame='icrs', unit=(u.hourangle, u.deg))

		altaz = coords.transform_to(self.altaz)
		alt = altaz.alt.degree

		obsfraction = (alt > self.minalt).mean()
		quality = alt.max()
		return obsfraction, quality, alt

if __name__ == '__main__':
	radec = sys.argv[1]
	print Observer().observable(radec)
	#import matplotlib.pyplot as plt
	#plt.plot(alt)
	#plt.show()
	#print altaz.alt.degree

