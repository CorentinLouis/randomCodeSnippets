import os
import numpy as np
import astropy as ap
from astropy import coordinates
import astropy.units as u
import matplotlib.pyplot as plt


stationPhaseCtr = [3801692.284, -528984.335, 5076957.630]
target = "PSR B0531+21"

station = coordinates.EarthLocation.from_geocentric(stationPhaseCtr[0], stationPhaseCtr[1], stationPhaseCtr[2], u.m)
source = coordinates.SkyCoord.from_name(target)

dmFilter = [49,52]
#sourceFolders = ['./2020_03_17/cands/', './2020_06_26/cands/', './2020_06_30/cands/', './2020_07_01/cands/', './2020_07_07/cands/']
#sourceFolders = ['./2020_06_30/cands/']
cands = []

def treeSearch(folder, requiredString):
	returnList = []
	for base, dirs, files in os.walk(folder):
		for file in files:
			if requiredString in file:
				returnList.append(os.path.join(base, file))

	return returnList

searchLoc = '/mnt/ucc4_data2/data/David/crab/'

def getCands(searchLoc):
	cands = treeSearch(searchLoc, '.cand')

	candfiles = []
	for cand in cands:
		with open(cand, 'r') as readRef:
			canddata = [line.strip('\n').split('\t') for line in readRef.readlines()]
			candfiles += [(cand, canddata)]

	return candfiles

def generateMetaData(cands):
	data = [] # (time, elevation, snr, , DM) #altAzObj)

	for (candfil, canddata) in cands:
		time = candfil.split('/')[-1].split('_')[0]
		time = '-'.join(time.split('-')[:2] + ['T'.join(time.split('-')[2:])])
		obsTime = ap.time.Time(time, format = 'isot')
		altAzObj = source.transform_to(coordinates.AltAz(location = station, obstime = obsTime))
		altDeg = altAzObj.alt.deg.astype(float)
		for cand in canddata:
			#if (float(cand[5]) > dmFilter[1]) or (float(cand[5]) < dmFilter[0]): continue
			#if (float(cand[0]) < 12): continue
			#data.append((obsTime, altDeg, float(cand[0]), float(cand[5]), altAzObj))
			data.append((obsTime, altDeg, float(cand[0]), float(cand[5]), altAzObj))

	#print(data)
	return np.vstack(data)



def filterCands(datastack, snrMin = None, snrMax = None, dmMin = None, dmMax = None, elevationMin = None, elevationMax = None):

	filterIdx = np.ones(datastack.shape[0])

	if snrMin is not None:
		filterIdx = np.logical_and(filterIdx, datastack[:, 2] > snrMin)

	if snrMax is not None:
		filterIdx = np.logical_and(filterIdx, datastack[:, 2] < snrMax)

	if dmMin is not None:
		filterIdx = np.logical_and(filterIdx, datastack[:, 3] > dmMin)

	if dmMax is not None:
		filterIdx = np.logical_and(filterIdx, datastack[:, 3] < dmMax)

	if elevationMin is not None:
		filterIdx = np.logical_and(filterIdx, datastack[:, 1] < elevationMin)

	if elevationMax is not None:
		filterIdx = np.logical_and(filterIdx, datastack[:, 1] < elevationMax)

	return datastack[filterIdx, :]

def defaultFilter(cands):
	crab =filterCands(cands, dmMin = 54, dmMax = 61)
	B0525 = filterCands(cands, dmMin = 48, dmMax = 52.5)

	return crab, B0525

def simpleSNRCorrection(cands):
	return cands[:, 2] / np.square(np.sin(cands[:, 1].astype(float) * np.pi / 180))

def standardMethod(searchLoc):
	raw = generateMetaData(getCands(searchLoc)) 
	filterCrab, filterB0525 = defaultFilter(raw)
	crabSnrCorr, B0525SnrCorr = simpleSNRCorrection(filterCrab), simpleSNRCorrection(filterB0525)

	return raw, filterCrab, filterB0525, crabSnrCorr, B0525SnrCorr

march17, march17Crab, march17B0525, march17CrabSnrCorr, march17B0525SnrCorr = standardMethod(searchLoc + "2020_03_17")
june26, june26Crab, june26B0525, june26CrabSnrCorr, june26B0525SnrCorr = standardMethod(searchLoc + "2020_06_26")
june30, june30Crab, june30B0525, june30CrabSnrCorr, june30B0525SnrCorr = standardMethod(searchLoc + "2020_06_30")
july1, july1Crab, july1B0525, july1CrabSnrCorr, july1B0525SnrCorr = standardMethod(searchLoc + "2020_07_01")
july7, july7Crab, july7B0525, july7CrabSnrCorr, july7B0525SnrCorr = standardMethod(searchLoc + "2020_07_07")
june26 = generateMetaData(getCands(searchLoc + "2020_06_26"))
june30 = generateMetaData(getCands(searchLoc + "2020_06_30"))
july1 = generateMetaData(getCands(searchLoc + "2020_07_01"))
july7 = generateMetaData(getCands(searchLoc + "2020_07_07")) 

 = defaultFilter(march17)
june26Crab, june26B0525 = defaultFilter(june26)
june30Crab, june30B0525 = defaultFilter(june30)
july1Crab, july1B0525 = defaultFilter(july1)
july7Crab, july7B0525 = defaultFilter(july7)




march17CrabSnrCorr = simpleSNRCorrection(march17Crab)
march17B0525SnrCorr = simpleSNRCorrection(march17B0525)

june26CrabSnrCorr = simpleSNRCorrection(june26Crab)
june26B0525SnrCorr = simpleSNRCorrection(june26B0525)

june30CrabSnrCorr = simpleSNRCorrection(june30Crab)
june30B0525SnrCorr = simpleSNRCorrection(june30B0525)

july1CrabSnrCorr = simpleSNRCorrection(july1Crab)
july1B0525SnrCorr = simpleSNRCorrection(july1B0525)

july7CrabSnrCorr = simpleSNRCorrection(july7Crab)
july7B0525SnrCorr = simpleSNRCorrection(july7B0525)




import powerlaw

march17CrabSnrCorrFit = powerlaw.Fit(march17CrabSnrCorr)
march17B0525SnrCorrFit = powerlaw.Fit(march17B0525SnrCorr)
june26CrabSnrCorrFit = powerlaw.Fit(june26CrabSnrCorr)
june26B0525SnrCorrFit = powerlaw.Fit(june26B0525SnrCorr)
june30CrabSnrCorrFit = powerlaw.Fit(june30CrabSnrCorr)
june30B0525SnrCorrFit = powerlaw.Fit(june30B0525SnrCorr)
july1CrabSnrCorrFit = powerlaw.Fit(july1CrabSnrCorr)
july1B0525SnrCorrFit = powerlaw.Fit(july1B0525SnrCorr)
july7CrabSnrCorrFit = powerlaw.Fit(july7CrabSnrCorr)
july7B0525SnrCorrFit = powerlaw.Fit(july7B0525SnrCorr)


fits = [march17CrabSnrCorrFit, march17B0525SnrCorrFit, june26CrabSnrCorrFit, june26B0525SnrCorrFit, june30CrabSnrCorrFit, june30B0525SnrCorrFit, july1CrabSnrCorrFit, july1B0525SnrCorrFit, july7CrabSnrCorrFit, july7B0525SnrCorrFit]
labels = ["March 17th", "June 26th", "June 30th", "July 1st", "July 7th"]

plt.close('all')
for label, fit in zip(labels, fits[::2]):
	print(fit.power_law.alpha, fit.power_law.sigma)
	plt.figure(figsize = (12,12))
	fit.power_law.plot_pdf( color= 'b',linestyle='--',label=f'{label} Fit: {fit.power_law.alpha}+-{fit.power_law.sigma}')
	fit.plot_pdf( color= 'b', label = f"{label} Data")
	plt.savefig(f"./{label}_crab.png")

print("\n\n\n")

for label, fit in zip(labels, fits[1::2]):
	print(fit.power_law.alpha, fit.power_law.sigma)
	plt.figure(figsize = (12,12))
	fit.power_law.plot_pdf( color= 'b',linestyle='--',label=f'{label} Fit: {fit.power_law.alpha}+-{fit.power_law.sigma}')
	fit.plot_pdf( color= 'b', label = f"{label} Data")
	plt.savefig(f"./{label}_b0525.png")

plt.close('all')


