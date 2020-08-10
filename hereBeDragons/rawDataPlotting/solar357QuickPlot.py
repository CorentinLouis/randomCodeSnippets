import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime

plt.viridis()

inFn = './sun_stokesI_0_2020-06-02T10:40:00_19422538979118.raw'
inFnSplit = inFn.split('_')
ts = inFnSplit[3]
print("Data load")
# Load in the last 75 seconds of data
rawData = np.fromfile(inFn, dtype = np.float32, offset = int(488 * 195312.5 * 220 * 4)).reshape(488, -1)

print("Subplots")
fig, (axHBAHi, axHBALo, axLBA) = plt.subplots(3, 1, figsize = (160, 40), gridspec_kw={'height_ratios': [1, 2.27, 2.27]})



print("p1")
# 288:488 210:244
lbaVmin, lbaVmax = np.percentile(rawData[288:, :], (16, 86))

print("p2")
# 88:288, 110:188
hbaLoVmin, hbaLoVmax = np.percentile(rawData[88:288, :], (16, 86))

print("p2")
# 0:88 10:88
hbaHiVmin, hbaHiVmax = np.percentile(rawData[:88, :], (16, 86))


initTs = datetime.datetime.fromisoformat(ts)
endTs = datetime.timedelta(seconds = 300) + initTs
x_lims = [initTs, endTs]
x_lims = mdates.date2num(x_lims)
date_format = mdates.DateFormatter('%Y-%M%DT%H:%M:%S')


print("plot1")
axLBA.imshow(rawData[288::-1, :], vmax = lbaVmax, vmin = lbaVmin, extent = [x_lims[0], x_lims[1],  10, 80], aspect = 'auto')

print("plot2")
axHBALo.imshow(rawData[88:288:-1, :], vmax = hbaLoVmax, vmin = hbaLoVmin, extent = [x_lims[0], x_lims[1],  110, 180], aspect = 'auto')

print("plot3")
axHBAHi.imshow(rawData[:88:-1, :], vmax = hbaHiVmax, vmin = hbaHiVmin, extent = [x_lims[0], x_lims[1],  210, 244], aspect = 'auto')
axHBAHi.xaxis_date()
axHBAHi.xaxis.set_major_formatter(date_format)


fig.autofmt_xdate()
axLBA.tick_params(labelbottom=False) 
axHBALo.tick_params(labelbottom=False) 

plt.xlabel("Time (UTC)")
plt.ylabel("Frequency (MHz)")
plt.title(f"{inFnSplit[0]}-{inFnSplit[1]}, Event {inFnSplit[2]} @ {inFnSplit[3]}UTC")

print("Save")
plt.savefig('./testplotsun.png')
plt.savefig('./testplotsun.svg')
plt.clf()

print("Exit")