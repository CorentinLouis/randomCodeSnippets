import datetime

obsBlock = "pointing='{},{},{}'\nbeamctl --antennaset=HBA_JOINED --rcus=$rcus --band=110_190  --beamlets=0:487 --subbands=12:499 --anadir=$pointing --digdir=$pointing &\nbash sleepuntil.sh {}\nkillall -9 beamctl\n\n\n\n"

recBlock = "obs_start='{}.0'\nobs_end='{}.0'\ntarget='{}' # No Spaces\nbash sleepuntil.sh {}\necho $target $obs_start $obs_end\nlogdate=`date +'%Y%m%d%H%M%S'`\nbash generic_ucc1_timestamps.sh $obs_start $obs_end 'dump_udp_ow_12' $target 2>&1 | tee -a $logdate'_$target.log'\n\n\n\n"

obsPreamble = "bash ./sleepuntil.sh {}\necho 'Initialising: SWLEVEL 2' \neval swlevel 2 \nrspctl --wg=0 \nsleep 1 \nrspctl --rcuprsg=0 \nsleep 1 \nrspctl --bitmode=8 \nrspctl --bitmode \nsleep 1 \nkillall beamctl \nsleep 3 \necho 'Initialising: SWLEVEL 3' \neval swlevel 3 \nsleep 2 \nrspctl --splitter=0 \nsleep 3 \nrcus='0:83,86:191' \n\n\n\n"


with open('./basicSched.txt', 'r') as sRef:
	startupTime = sRef.readline().strip("\n")
	data = sRef.readlines()
	data = [line.strip('\n') for line in data]

startDay = startupTime.split(' ')[0]
with open(f'./lcu_script_{startDay}.sh', 'w+') as lcuRef, open(f'./ucc_script_{startDay}.sh', 'w+') as uccRef:
	preamble = False
	for line in data:
		if line == '': continue
		lcuRef.writelines("# " + line + "\n\n")
		uccRef.writelines("# " + line + "\n\n")
		if '[' in line and line[line.index('[') -1] != '\\':
			splitLine = line.split("[")[1].split(',')
			pointingRa = splitLine[0].strip(' ')
			pointingDec = splitLine[1].strip(' ')
			pointingCoords = splitLine[2].strip(' ').replace("'", "")[:-1]

			splitLine = line.split(' ')
			startTime = datetime.datetime.strptime(splitLine[0], "%Y-%m-%dT%H:%M")
			endTime = datetime.datetime.strptime(splitLine[2], "%Y-%m-%dT%H:%M")

			preStart = (startTime - datetime.timedelta(seconds = 30)).strftime("%Y%m%d %H%M%S") # YYYYMMDD HHMMSS
			postEnd = (endTime + datetime.timedelta(seconds = 10)).strftime("%Y%m%d %H%M%S")
			strStartTime = startTime.strftime("%Y-%m-%dT%H:%M:%S")# ISOT
			strEndTime = endTime.strftime("%Y-%m-%dT%H:%M:%S")
			targName = line.split(':')[-1].split('\t')[1].split(' ')[0]
			if not preamble:
				preamble = True
				lcuRef.writelines(obsPreamble.format(startupTime))


			lcuRef.writelines(obsBlock.format(pointingRa, pointingDec, pointingCoords, postEnd))
			uccRef.writelines(recBlock.format(strStartTime, strEndTime, targName, preStart))
