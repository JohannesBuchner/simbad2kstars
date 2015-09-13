Simbad to KStars import
-------------------------

Grepping through Simbad to look for interesting objects you could observe.

* Queries Simbad for objects. Supports arbitrary user-defined criteria.
* The names, positions and types are stored in a KStars catalogue
* Can trim out objects that can not be observed from your location (see below)
* The catalogue can then be loaded in KStars, and viewed.
* Caches Simbad queries, so a request is not repeated to the servers. To clear cache, remove joblib directory.

Example Use Cases
------------------

General questions:

* Where are exoplanets? (Simbad query: otype='Pl')
  The list is updated all the time, so it makes sense to just load from simbad.

* What are the brightest Globular Clusters? (Vmag<8.5&otype='GlC')
  A magnitude-cut.

Lets say you have a telecope available, for example for a student, but are not
sure what object to point to.

If you have a spectrograph:

* Where are bright spectroscopic binaries? (Vmag<5&otype = 'SB*')
* What is a good, bright peculiar star to look at? (Vmag<7&otype = 'Pe*')

Hint: Search exoplanet.eu for planets with 
short-period (<5 days) and high-amplitude (K>50). You might be able to detect
those with a few nights of observations!

Usage
------

1. Create a KStars catalogue from an arbitrary `Simbad query <http://simbad.u-strasbg.fr/simbad/sim-fsam>`_::

	$ python query.py "Vmag<8.5&otype='GlC'" outputfile.kstarscat

2. Open KStars, go to KStars Settings -> Advanced -> Load catalogue
   Loading catalogues is slow, but finally you will have all objects in KStars.


Observable objects
-------------------

To trim the catalogue to objects you can actually observe in your part of the world
in a given time window, I have included some simple ephemeris calculations.

1. Define your location in location.json::

	{
		"lat": -33.459229, 
		"lon": -70.645348,
		"height": 0
	}
	
	Latitude and longitude in degrees, height in meters.

2. Define when you want to do your observations (time window, minimum elevation)::

	{
		"start": "2015-09-12 18:00:00",
		"stop":  "2015-09-20 02:00:00",
		"steps": 1200,
		"minalt": 15,
		"hourranges": [[20, 24], [0,2]],
		"timezone": "America/Santiago"
	}

	When you run query.py, the RA/Dec will be sampled in the time window.
	Between *start* and *stop* one point every *steps* seconds (in the 
	example above, every 20 minutes) is created.
	Points outside the hour ranges are discarded (in the example the night
	is between 8pm and 2am).
	The timezone is in the common `tz format <https://en.wikipedia.org/wiki/List_of_tz_database_time_zones>`_.
	
	At every remaining point the altitude of each object is computed.
	
	Objects get scores for the maximum altitude reached,
	and if the altitude is never above *minalt* (in degrees),
	they are removed from the catalogue.
	
	
3. Run query.py as above. This is of course a very crude tool. KStars has a 
   observability tool which you can use to compare the objects in more detail.

Example
-------------

Looking for brighter than magnitude 7 stars, which are peculiar (Pe*)::

	$ python query.py "Vmag<7&otype='Pe*'" peculiar.kstarcat

	Objects will be graded by observability:
	    Column 1: Name
	    Column 2: Fraction of time when above minimum elevation
	    Column 3: Maximum elevation

	* zet Cyg            0.8 26.2
	HD 175674            1.0 75.0
	* omi Vir            0.0 -0.2
	* 56 Peg             0.7 31.0
	* eps Peg            1.0 46.6
	HD 199394            0.0 10.1
	* ksi Cap            1.0 69.1
	HR 4862              1.0 36.8
	* tet Aur            0.0 -11.3
	* 53 Cam             0.0 -37.6
	HR 3612              0.0 -45.6
	V* alf02 CVn         0.0 -7.8
	* 58 Leo             0.0 -10.8
	HD 198590            1.0 84.4
	* 55 Cam             0.0 -38.7
	HR 3166              0.0 10.3
	HD 223617            0.8 54.2
	HR 5058              0.3 39.2
	HR 774               0.0 -26.0
	* 16 Ser             0.3 37.2
	V* TZ Lyn            0.0 -39.3
	HD 41701             0.2 30.2
	V* HR CMa            0.0 9.3
	* o Vir              0.1 20.7
	* zet Cap            1.0 78.9
	* ups02 Cas          0.0 -2.7
	V* GO And            0.0 11.5
	HD 77247             0.0 -46.1
	HR 4474              0.0 -26.0
	HD 205011            0.9 32.6
	* 12 Pup             0.0 -0.9
	* 49 Cam             0.0 -36.0
	HD 100012            0.0 11.5
	* y Vel              0.0 3.6
	* ksi Cyg            0.0 12.5
	
	14 objects in output catalogue
	21 unobservable objects trimmed from output catalogue
	Top 10: HD 198590, * zet Cap, HD 175674, * ksi Cap, * eps Peg, HR 4862, HD 205011, HD 223617, * zet Cyg, * 56 Peg


HD 198590 is easy to observe -- it goes up to 84 degrees and never sets.


