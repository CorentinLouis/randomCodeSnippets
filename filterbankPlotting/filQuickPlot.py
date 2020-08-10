import sigpyproc as spp
import argparse
from astropy.time import Time
import numpy as np
from tqdm import trange

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from  matplotlib.colors import Normalize as colourNorm

def initFigure(sampleDatablock, figSize =(26, 14)):
	fig = plt.figure(figsize=figSize, constrained_layout=True) 
	plt.tight_layout()
	gs = fig.add_gridspec(26, 14)

	axtop = fig.add_subplot(gs[0:2, :-2])
	axright = fig.add_subplot(gs[2:, -2:])
	axmain = fig.add_subplot(gs[3:, :-2])

	title = axtop.set_title("")
	axtop.set_title("Time series")
	axright.set_title("Bandpass")

	axmain.set_xlabel("Time (seconds since start of block")
	axmain.set_ylabel("Frequency (MHz)")

	axmainArtist = axmain.imshow(np.zeros(sampleDatablock.shape), vmin=-1, vmax=1, aspect = 'auto', interpolation = 'nearest', extent = (0, sampleDatablock.shape[1] * sampleDatablock.header.tsamp, sampleDatablock.header.fch1 + sampleDatablock.header.nchans * sampleDatablock.header.foff, sampleDatablock.header.fch1))
	axtopArtist, = axtop.plot(sampleDatablock.shape[1])
	axrightArtist, = axright.plot(sampleDatablock.shape[0], sampleDatablock.shape[0])

	axtop.set_xlim([0, sampleDatablock.shape[1]])
	axright.set_xlim(-0.1, 1.1)
	axtop.set_ylim(-0.1, 1.1)
	axright.set_ylim([0, sampleDatablock.shape[0]])

	axright.invert_yaxis()

	axmainbackground = fig.canvas.copy_from_bbox(axmain.bbox)
	axtopbackground = fig.canvas.copy_from_bbox(axtop.bbox)
	axrightbackground = fig.canvas.copy_from_bbox(axright.bbox)

	fig.canvas.draw() 
	plt.show(block = False)

	return fig, axtop, axright, axmain, axtopArtist, axrightArtist, axmainArtist, title, axmainbackground, axtopbackground, axrightbackground

def plot_data(datablock, figureInputs, plotPrefix, filePrefix, startingSample, deci = 0, suffix = 0):
	fig, axtop, axright, axmain, axtopArtist, axrightArtist, axmainArtist, title, axmainbackground, axtopbackground, axrightbackground = figureInputs
	time = Time(datablock.header.tstart, format = "mjd")

	timeseries = np.log2(datablock.get_tim())
	timeseries -= np.min(timeseries)
	timeseries /= np.max(timeseries)
	axtopArtist.set_data(np.arange(timeseries.size), timeseries)

	bandpass = np.log2(datablock.get_bandpass())
	bandpass -= np.min(bandpass)
	bandpass /= np.max(bandpass)
	axrightArtist.set_data(bandpass, np.arange(bandpass.size))

	dbn = datablock
	vmx, vmn = np.percentile(dbn, (83, 33))
	axmainArtist.set(norm = colourNorm(np.log2(vmn), np.log2(vmx)))
	axmainArtist.set_data(np.log2(dbn))
	title.set_text(f"{plotPrefix} {time.isot} ({datablock.shape[1] * datablock.header.tsamp:.03f} seconds @ samples {startingSample})")

	fig.canvas.restore_region(axmainbackground)
	fig.canvas.restore_region(axtopbackground)
	fig.canvas.restore_region(axrightbackground)

	axmain.draw_artist(axmainArtist)
	axtop.draw_artist(axtopArtist)
	axright.draw_artist(axrightArtist)

	fig.canvas.blit(axmain.bbox)
	fig.canvas.blit(axtop.bbox)
	fig.canvas.blit(axright.bbox)

	fig.canvas.flush_events()            


	plt.savefig(f"{filePrefix}_{suffix}.png")


def rollingAverage(data, step = 8):
	rollingSum = np.cumsum(data)
	return rollingSum[step:] - rollingSum[:-step]

def decimate(data, step = 64):
	rollingSum = np.cumsum(data)
	return rollingSum[step::step] - rollingSum[:-step:step]


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description = "Plot data contained within a sigproc filterbank.")

	parser.add_argument('-i', dest = 'input', required = True, help = "Input File Location")
	parser.add_argument('--deci', dest = 'deci', default = 64, type = int, help = "Default decimation factor")

	parser.add_argument('--init_ts', dest = 'init', default = 0, type = int, help = "Time sample to start plotting from")
	parser.add_argument('--overlap_frac', dest = 'overlap', default = 0.1, type = float, help = "Fraction of data to keep between time blocks; 0 for none, 0.9 for 90%% data reuse")
	parser.add_argument('--samples', dest = 'samples', default = int(10. / 5.12e-6), type = int, help = "Samples per plot")
	
	parser.add_argument('--plot_raw', dest = 'plot_raw', default = False, action = 'store_true', help = "Plot the raw data")
	parser.add_argument('--plot_deci', dest = 'plot_deci', default = False, action = 'store_true', help = "Plot the base decimated data")

	parser.add_argument("--title", dest = 'title', default = 'plot', help = "Plot title prefix")
	parser.add_argument("-o", dest = 'prefix', default = 'plot', help = "Plot file prefix")

	args = parser.parse_args()

	if args.overlap > 1:
		raise RuntimeError(f"Invalid overlap time {args.overlap} > 1")
	elif args.overlap < 0:
		raise RuntimeError(f"Invalid overlap time {args.overlap} < 0")

	if args.plot_raw == args.plot_deci == args.plot_deci_sec == False:
		raise RuntimeError("Failed to provide any task to perform. Exiting.")

	filReader = spp.FilReader(args.input)

	startingSamples = args.init
	baseTime = args.init

	samplesPerBlock = int(args.samples * (1. + args.overlap))
	samplesPerBlock += samplesPerBlock % args.deci
	print(f"We will be reading {samplesPerBlock} samples per block.")


	dataBlock = filReader.readBlock(readTimestamp, samplesPerBlock)

	if args.plot_deci:
		deciBlock = baseBlock.downsample(tfactor = args.deci)


	if args.plot_raw:
		normalInit = initFigure(dataBlock)
	if args.plot_deci:
		deciInit = initFigure(deciBlock)


	for i in trange(int(filReader.header.nsamples / args.samples)):
		if i != 0: 
			dataBlock = filReader.readBlock(readTimestamp, samplesPerBlock)
			if args.plot_deci:
				deciBlock = dataBlock.downsample(tfactor = args.deci)

		if args.plot_raw:
			plot_data(dataBlock, normalInit, args.title, args.prefix, readTimestamp, args.deci, suffix = i)	
		if args.plot_deci:
			plot_data(deciBlock, deciInit, f"{args.title} (Decimated x {args.deci})", f"{args.prefix}_deci_{args.deci}", readTimestamp, args.deci, suffix = i)	

		readTimestamp += args.samples

