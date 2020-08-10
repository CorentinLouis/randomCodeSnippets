import argparse
import os
import numpy as np
import matplotlib.pyplot as plt
import datetime

nchans = 488
sampleRate = 5.12 * 10** -6
# Top of sb499
absftop = 197.4609375

def dm_delays(ftop, foff, nchan, dm):
	# Implements the standard DM delay
	freqs = ftop + 0.5 * foff + foff * np.arange(nchan)
	delays = np.hstack([[0.], 4150 * dm * ((1. / np.square(freqs[1:])) - (1. / np.square(freqs[0])))])

	return delays

def test_dm_delays(ftop, foff, nchan, dm):
	# Something I was testing, safe to ignore
	freqs = ftop + foff * np.arange(nchan)
	freqoffs = (-1 * np.square(foff) * freqs - 2 * foff * np.square(freqs) - 2 * np.power(freqs, 3) \
		+ 1.41421 * np.sqrt(np.square(freqs) * np.square(foff  + freqs) * (np.square(foff) + 2 * foff * freqs + 2 * np.square(freqs))))\
		/(np.square(foff) + 2 * foff * freqs + 2 * np.square(freqs))

	freqs += freqoffs

	delays = np.hstack([[0.], 4150 * dm * (1. / np.square(freqs[1:]) - 1. / np.square(freqs[0]))])


	return delays

def dm_delays(ftop, foff, nchan, dm):
	# Implements the standard DM delay
	freqs = ftop + 0.5 * foff + foff * np.arange(nchan)
	delays = np.hstack([[0.], 4150 * dm * ((1. / np.square(freqs[1:])) - (1. / np.square(freqs[0])))])

	return delays

def test_dm_delays(ftop, foff, nchan, dm):
	# Something I was testing, safe to ignore
	freqs = ftop + foff * np.arange(nchan)
	freqoffs = (-1 * np.square(foff) * freqs - 2 * foff * np.square(freqs) - 2 * np.power(freqs, 3) \
		+ 1.41421 * np.sqrt(np.square(freqs) * np.square(foff  + freqs) * (np.square(foff) + 2 * foff * freqs + 2 * np.square(freqs))))\
		/(np.square(foff) + 2 * foff * freqs + 2 * np.square(freqs))

	freqsnew = freqs + freqoffs

	delays = np.hstack([[0.], 4150 * dm * (1. / np.square(freqsnew[1:]) - 1. / np.square(freqsnew[0]))])
	freqs = ftop + 0.5 * foff + foff * np.arange(nchan)
	delays2 = np.hstack([[0.], 4150 * dm * ((1. / np.square(freqs[1:])) - (1. / np.square(freqs[0])))])

	return (delays - delays2), freqs, freqsnew


def main(s0, s1, s2, s3, delayFunc, dm, decimate = 0):

	# Ignore, testing
	"""
	delta = dm_delays(absftop, -100. / 512, nchans, dm) - test_dm_delays(absftop, -100. / 512, nchans, dm)
	print(delta)
	delta /= sampleRate
	print(delta)
	"""


	# Get the delays (in seconds)
	print("Finding time delays...")
	delays = delayFunc(absftop, -100. / 512, nchans, dm)
	print("Delays (s):")
	print(delays)
	delays /= sampleRate
	delays = delays.astype(int)

	# Build up a 
	outputLen = int(s0.shape[0] - np.max(delays))
	dataOut = np.ones((outputLen, nchans), dtype = np.int32)
	print(delays)

	# Terribl approach to RFI
	zapchans = list(range(150,200)) + list(range(280, 290)) + list(range(305, 320)) + list(range(450, nchans))

	# SImple implementation that works, but isn't cache efficient
	print("Forming Stokes I + Dedispersing... processing channel:")
	for i in range(nchans):
		if i in zapchans:
			continue
		print(f"{i} ({100 * i / min(430,nchans)} %)", end = '\r')
		dataOut[..., i] += np.square(s0[delays[i]: delays[i] + outputLen, i].astype(np.int32))
		dataOut[..., i] += np.square(s1[delays[i]: delays[i] + outputLen, i].astype(np.int32))
		dataOut[..., i] += np.square(s2[delays[i]: delays[i] + outputLen, i].astype(np.int32))
		dataOut[..., i] += np.square(s3[delays[i]: delays[i] + outputLen, i].astype(np.int32))

	# Cache efficient but untested
	"""
	print("Forming Stokes I + Dedispersing... processing sample:")
	blockCount = 128
	blockSize = int(dataOut.shape[0] / blockCount)
	for i in range(blockCount):
		if i in zapchans:
			continue
		print(f"{i* blockSize} -> {(i + 1) * blockSize} ({100 * i / blockCount:07.3f} %)", end = '\r')
		dataOut[i * blockSize: (i+1) * blockSize, :] += np.square(s0[i * blockLength + delays[i]: (i + 1) * blockLength + delays[i] + outputLen, i].astype(np.int32))
		dataOut[i * blockSize: (i+1) * blockSize, :] += np.square(s1[i * blockLength + delays[i]: (i + 1) * blockLength + delays[i] + outputLen, i].astype(np.int32))
		dataOut[i * blockSize: (i+1) * blockSize, :] += np.square(s2[i * blockLength + delays[i]: (i + 1) * blockLength + delays[i] + outputLen, i].astype(np.int32))
		dataOut[i * blockSize: (i+1) * blockSize, :] += np.square(s3[i * blockLength + delays[i]: (i + 1) * blockLength + delays[i] + outputLen, i].astype(np.int32))
	"""

	if decimate:
		print("Decimating...")
		rollingSum = np.cumsum(dataOut, axis = 0)
		dataOut = rollingSum[decimate::decimate, :] - rollingSum[:-decimate:decimate, :]


	print("Plotting...")
	plt.figure(figsize = (24,12))
	plt.imshow(dataOut.T, aspect = 'auto', vmax = np.percentile(dataOut, 95), vmin = np.percentile(dataOut, 33))
	plt.savefig(f'./debugfull_{datetime.datetime.now().isoformat()}.png')

	plt.figure(figsize = (24,12))
	plt.imshow(np.log10(dataOut.T), aspect = 'auto', vmax = np.log10(np.percentile(dataOut, 95)), vmin = np.log10(np.percentile(dataOut, 33)))
	plt.savefig(f'./debugfull2_{datetime.datetime.now().isoformat()}.png')
	
	plt.figure(figsize = (24,12))
	d1 = dataOut[:, :100].sum(axis = 1)
	d1 -= np.mean(d1, dtype = np.int64)
	d2 = dataOut[:, 100:200].sum(axis = 1)
	d2 -= np.mean(d2, dtype = np.int64)
	d3 = dataOut[:, 200:300].sum(axis = 1)
	d3 -= np.mean(d3, dtype = np.int64)
	d4 = dataOut[:, 300:].sum(axis = 1)
	d4 -= np.mean(d4, dtype = np.int64)
	plt.plot(d1, alpha = 0.3, label = '1')
	plt.plot(d2, alpha = 0.3, label = '2')
	plt.plot(d3, alpha = 0.3, label = '3')
	plt.plot(d4, alpha = 0.3, label = '4')
	plt.legend()
	plt.savefig(f'./debug_{datetime.datetime.now().isoformat()}.png')

	print("Done!")

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description = "Incoherent Dedispersion test")

	parser.add_argument('-i', dest = 'infile', required = True, help = "Input file Location")
	parser.add_argument('-d', dest = 'dm', type = float, required= True, help = "DM to dedisperse at")
	parser.add_argument('-t', dest = 'delayFunc', default = dm_delays, action = 'store_const', const = test_dm_delays, help = "Enable the new delay function")
	parser.add_argument('-x', dest = 'decimate', default = 0, type = int, help = "Time decimation factor")

	args = parser.parse_args()

	print(f"Prearing to work on files at {args.infile}, with DM {args.dm}, Time decimation x{args.decimate} and delay function {args.delayFunc.__name__}.")

	# Load in our data
	s0 = np.fromfile(args.infile.format("0"), dtype = np.int8).reshape(-1, nchans)
	s1 = np.fromfile(args.infile.format("1"), dtype = np.int8).reshape(-1, nchans)
	s2 = np.fromfile(args.infile.format("2"), dtype = np.int8).reshape(-1, nchans)
	s3 = np.fromfile(args.infile.format("3"), dtype = np.int8).reshape(-1, nchans)

	print("Starting dedispersion...")
	main(s0, s1, s2, s3, args.delayFunc, args.dm, args.decimate)