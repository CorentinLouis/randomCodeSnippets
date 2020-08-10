import argparse
import numpy as np

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt



# Ensure we aren't mixing up bit modes
def checkBands(bit, bands, lim):
	if bands > lim:
		raise RunetimeError(f"Bitmode {bitmode} only support up to {lim} subbands ({bands} provided).")

def main(fileLocation, nSubbands = 488, bitmode = 8, outputLoc = None):
	if bitmode not in [4, 8, 16]:
		raise RuntimeError(f"Unknown bitmode {bitmode}")
	elif bitmode == 4:
		workingDtype = np.float16
		checkBands(4, nSubbands, 976)
	elif bitmode == 8:
		workingDtype = np.float32
		checkBands(8, nSubbands, 488)
	else:
		workingDtype = np.float64
		checkBands(16, nSubbands, 244)

	obsStart = '_'.join(fileLocation.split('/')[-1].split('_')[:2])

	data = np.fromfile(fileLocation, dtype = workingDtype).reshape(-1, nSubbands)
	minVal = np.min(data)
	data = np.log10(data - minVal + 1).T
	vmx = np.percentile(data, 90)
	vmn = np.percentile(data, 10)

	plt.figure(figsize=(24,12))
	plt.imshow(data, vmax = vmx, vmin = vmn, aspect = 'auto')
	plt.colorbar()
	
	plt.title(f"{obsStart} Bitmode: {bitmode}, Subbands: {nSubbands}")
	plt.xlabel(f"Time (seconds since {obsStart})")
	plt.ylabel("Frequency Channel")
	
	if outputLoc == None:
		outputLoc = fileLocation.replace('.dat', '.png')

	plt.savefig(outputLoc)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description = "Plot a BST file")

	parser.add_argument('-i', dest = 'infile', required = True, help = "Input BST Location")
	parser.add_argument('-b', dest = 'bitmode', default = 8, type = int, help = "Observation bit mode")
	parser.add_argument('-n', dest = 'subbands', default = 488, type = int, help = "Number of subbands in the observation")
	parser.add_argument('-o', dest = 'outfile', default = None, help = "Output figure loocations / name")

	args = parser.parse_args()

	main(args.infile, args.subbands, args.bitmode, args.outfile)
