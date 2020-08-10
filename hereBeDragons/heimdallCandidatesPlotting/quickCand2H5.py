import sigpyproc as spp 
#import matplotlib.pyplot as plt
#import matplotlib.gridspec as gridspec
import os
import h5py
import numpy as np

#plt.viridis()



### Easy optimisation: batch the writes by first saving data to a numpy array
def saveData(headGroup, idx, filObj, lengthVal, snrVal, fitDM, startSample, endSample):

	print(f"Getting data from {startSample}-{endSample}")
	data = filObj.readBlock(startSample, endSample - startSample)
	print(f"Dedispersing to DM {fitDM}...")
	data2 = data.dedisperse(fitDM)
	h5GroupName = f'{lengthVal}_sample_pulse'
	print(f"Saving data to h5 group {h5GroupName} at index {idx}")


	headGroup[h5GroupName][:, :, idx] = data2[:, : 2 * lengthVal].astype(np.uint8)
	headGroup[h5GroupName + '_snr'][idx] = np.array([snrVal], dtype = np.float16)


def handleHeimdall(folderName, filLoc, h5Name = 'output_pulses.h5', dump = True, dm0 = 55, dm1 = 62, snr0 = 6, maxlen = 512, fitDM = 57.61):
	filObj = spp.FilReader(filLoc)
	f0 = filObj.header.fch1
	df = filObj.header.foff
	tsamp = filObj.header.tsamp
	maxSamples = filObj.header.nsamples

	filName = filLoc.split('/')[-1]

	count = 0
	dm = []
	snr = []
	boxcar = []
	length = []


	for file in os.listdir(folderName):
		if file.split('.')[-1] == 'cand':
			with open(f'{folderName}/{file}', 'r') as currentFile:
				fileData = currentFile.readlines()
				print(file, fileData)
				for currLine in fileData:
					if len(currLine) < 10: continue
					lineData = list(filter(None, currLine.split('\t')))
					print(lineData)

					#if float(lineData[0]) < 9 and int(lineData[3]) > 8: continue
					if float(lineData[5]) < dm0 or float(lineData[5]) > dm1: continue
					if float(lineData[0]) < snr0: continue
					if int(lineData[8]) - int(lineData[7]) > maxlen: continue

					count += 1
					snr.append(float(lineData[0]))
					dm.append(float(lineData[5]))
					boxcar.append(2 ** float(lineData[3]))
					length.append(int(lineData[8]) - int(lineData[7]))

	if not dump:
		return count, snr, dm, boxcar, length

	count = 0

	lengths, counts = np.unique(length, return_counts = True)
	combinedData = np.vstack([lengths, counts]).T

	with h5py.File(h5Name, 'w') as h5ref:
		headGroup = h5ref.create_group(f"{filObj.header.source_name}_pulses")
		#headGroup.attrs.create('sigproc_hdr', filObj.header.SPPHeader(True))
		headGroup.attrs.create('source_fil', filLoc)
		headGroup.attrs.create('source_cands', folderName)
		headGroup.attrs.create('dm0', dm0)
		headGroup.attrs.create('dm1', dm1)
		headGroup.attrs.create('snr-', snr0)
		headGroup.attrs.create('maxlen', maxlen)
		headGroup.attrs.create('fitDM', fitDM)


		for key, val in filObj.header.items():
			headGroup.attrs.create(key, val)

		for lengthVal, counts in combinedData:
			print(f"{lengthVal} samples: {counts}x")
			headGroup.create_dataset(f'{lengthVal}_sample_pulse', (filObj.header.nchans, lengthVal * 2, counts), compression = 'lzf', dtype = np.uint8)
			headGroup.create_dataset(f'{lengthVal}_sample_pulse_snr', (counts,), compression = 'lzf', dtype = np.float16)



		lengthCounts = {length: 0 for length in lengths}
		for file in os.listdir(folderName):
			if file.split('.')[-1] == 'cand':
				with open(f'{folderName}/{file}', 'r') as currentFile:
					fileData = currentFile.readlines()
					print(file, fileData)
					for currLine in fileData:
						if len(currLine) < 10: continue
						lineData = list(filter(None, currLine.split('\t')))
						print(lineData)

						#if float(lineData[0]) < 9 and int(lineData[3]) > 8: continue
						if float(lineData[5]) < dm0 or float(lineData[5]) > dm1: continue
						if float(lineData[0]) < snr0: continue
						if int(lineData[8]) - int(lineData[7]) > maxlen: continue

						
						snrVal = snr[count]
						dmVal = dm[count]						
						lengthVal = length[count]
						count += 1
					
						endSample = int(lineData[8])
						startSample = int(lineData[7])

						dmDelays = filObj.header.getDMdelays(fitDM)
						endSample += dmDelays[-1] + lengthVal # double the observed length for tail investigations
						if endSample > maxSamples:
							endSample = maxSamples

						
						idx = lengthCounts[lengthVal]
						lengthCounts[lengthVal] += 1
						saveData(headGroup, idx, filObj, lengthVal, snrVal, fitDM, startSample, endSample)


	return count, snr, dm, boxcar, length
