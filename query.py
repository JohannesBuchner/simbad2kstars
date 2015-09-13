import joblib
import sys
import requests
import random
mem = joblib.Memory('.')

@mem.cache
def loadpage(criteria):
	params = {'Criteria':criteria, 'output.format':'ASCII', 'OutputMode':'LIST',
		#'epoch1':'J', 'equi1':2000, 'list.coo1':'on', 'frame1':'ICRS'
		}
	req = requests.get("http://simbad.u-strasbg.fr/simbad/sim-sam", 
		params=params)
	print req.url
	return req.text

kstars_ids = dict(STAR=0, CATALOG_STAR=1, PLANET=2, OPEN_CLUSTER=3, GLOBULAR_CLUSTER=4,
	GASEOUS_NEBULA=5, PLANETARY_NEBULA=6, SUPERNOVA_REMNANT=7, GALAXY=8,
	COMET=9, ASTEROID=10, CONSTELLATION=11, MOON=12, ASTERISM=13,
	GALAXY_CLUSTER=14, DARK_NEBULA=15, QUASAR=16, MULT_STAR=17, RADIO_SOURCE=18,
	SATELLITE=19, SUPERNOVA=20, UNKNOWN=99)
maps = [
	#([], 'STAR'),
	#([''], 'CATALOG_STAR'),
	(['Pl?', 'Pl'], 'PLANET'),
	(['OpC', 'C?*', 'OpC'], 'OPEN_CLUSTER'),
	(['GlC', 'Gl?'], 'GLOBULAR_CLUSTER'),
	('GNe,BNe,RNe,MoC,glb,cor,SFR,HVC,HII'.split(','), 'GASEOUS_NEBULA'), 
	(['PN','PN?'], 'PLANETARY_NEBULA'),
	(['SR?', 'SNR'], 'SUPERNOVA_REMNANT'),
	('IG,PaG,G,PoG,GiC,BiC,GiG,GiP,HzG,ALS,LyA,DLA,mAL,LLS,BAL,rG,H2G,LSB,LeI,LeG,LeQ,EmG,SBG,bCG'.split(','), 'GALAXY'),
	('SCG,ClG,GrG,CGG'.split(','), 'GALAXY_CLUSTER'),
	(['DNe'], 'DARK_NEBULA'),
	('AGN,LIN,SyG,Sy1,Sy2,Bla,BLL,OVV,QSO,AG?,Q?,Bz?,BL?'.split(','), 'QUASAR'),
	(['LXB,HXB, As*,St*,MGr,**,EB*,Al*,bL*,WU*,EP*,SB*,El*,Sy*,CV*,DQ*,AM*,NL*,No*,DN*,XB*,LXB,HXB'], 'MULT_STAR'),
	('Rad,mR,cm,mm,smm'.split(','), 'RADIO_SOURCE'),
	(['SN?', 'SN*'], 'SUPERNOVA'),
	# ([''], 'SATELLITE'), # no satellites in Simbad, they don't have fixed positions
	#([''], 'COMET'),
	#([''], 'ASTEROID'),
	#([''], 'CONSTELLATION'),
	#([''], 'MOON'),
	#([''], 'ASTERISM'),
	
]
simbad2kstar_typemap = dict()
for simbad_types, kstar_type in maps:
	for simbad_type in simbad_types:
		simbad2kstar_typemap[simbad_type] = kstar_type

from observable import Observer

try:
	observer = Observer()
	print
	print 'Objects will be graded by observability:'
	print '    Column 1: Name'
	print '    Column 2: Fraction of time when above minimum elevation'
	print '    Column 3: Maximum elevation'
	print
except IOError as e:
	print 'To enable observability trimming, create obswindow.json and location.json'
	observer = None

def kstars_type(simbad_type):
	kstars_type = simbad2kstar_typemap.get(simbad_type, 'UNKNOWN')
	if kstars_type == 'UNKNOWN' and '*' in simbad_type:
		kstars_type = 'STAR'
	return kstars_ids[kstars_type]

criteria = sys.argv[1]
out = loadpage(criteria)

lines = out.split('\n')
a = [i for i, l in enumerate(lines) if l.startswith('Number of objects')][0]
b = [i for i, l in enumerate(lines) if l.startswith('===============')][0]
table = lines[a+4:b]
outputfile = sys.argv[2]
name = outputfile.rstrip('.kstarcat')
fout = open(outputfile, 'w')
color = ('0123456789ABCDEF'[int(random.random()*16)])*2
fout.write("""# Name: SIMBAD:%s
# Color: #%s0000
# Epoch: 2000
# ID RA Dc Tp Nm
""" % (name, color))
object_ranking = []
trimmed = 0
passed = 0
for i, row in enumerate(table):
	parts = row.strip().split('|')
	name = parts[1].strip()
	simbad_type = parts[2].strip()
	
	radec = parts[3].strip()
	radecparts = radec.split(' ')
	ra = ':'.join(radecparts[:3])
	dec = ':'.join(radecparts[3:])
	if observer:
		obsfraction, quality, alt = observer.observable(radec)
		print '%-20s %.1f %.1f' % (name, round(obsfraction, 1), quality)
		object_ranking.append((round(obsfraction, 1), quality, name))
		if obsfraction == 0:
			trimmed += 1
			continue
	fout.write('%d %s %s %d "%s"\n' % (i+1, ra[:10], dec[:9], kstars_type(simbad_type), name))
	passed += 1

print
print '%d objects in output catalogue' % passed
if observer:
	print '%d unobservable objects trimmed from output catalogue' % trimmed
	object_ranking.sort(reverse=True)
	print 'Top 10: %s' % ', '.join([name for _, _, name in object_ranking][:10])

