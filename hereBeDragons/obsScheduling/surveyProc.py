import os, psrqpy

folders = [folder for folder in os.listdir('./') if os.path.isdir(f"./{folder}")]

psrNames = []
psrData = []
for folder in folders:
	if folder == "surveyOutput": continue
	psrName = "J" + folder.split('J')[1]
	psrNames.append(psrName)

	psrPath = f"./{folder}"

	for fil in os.listdir(folder):
		if "udp_16130" in fil:
			arbName = fil.replace("16130", "1613%d")
			psrUdp = f"{psrPath}/{arbName}"
	psrData.append((psrName, psrPath, psrUdp))

universe = psrqpy.QueryATNF()

pulsarData = {}

for psr in psrNames:
	pulsar = universe.get_pulsar(psr)

	dm, period, raj, decj = float(pulsar['DM']), float(pulsar['P0']), pulsar['RAJ'][0], pulsar['DECJ'][0]

	print(psr, dm, period, raj, decj)

	pulsarData[psr] = [dm, period, raj, decj]


with open("./batchProccess.sh", 'w+') as ref:
	for name, folder, data in psrData:
		psrDm, psrP, psrRa, psrDec = pulsarData[name]

		print(f"{name}: DM {psrDm}, Period {psrP}, RAJ {psrRa}, DECJ {psrDec}")

		mockHdrLoc = f"{folder}/{name}_mode5.sigprochdr"
		mockHeader = "mockHeader"
		ref.writelines(f"{mockHeader} -nchans 488 -fch1 197.55859375 -fo -0.1953125 -tel 1916 -tsamp 0.00000512 -nbits 8 -nifs 1 -source {name} -ra {psrRa} -dec {psrDec} {mockHdrLoc}\n")
		ref.writelines(f"cdmt_udp -d {psrDm},0,1 -f 8 -c -t 1916 -m {mockHdrLoc} -o ./surveyOutput/{name}_DM{psrDm}_P{psrP}_cdmt {data}\n")

		ref.writelines("\n")
		ref.writelines("\n")

		#psrDm, psrP, psrRa, psrDec = pulsarData[name]
		inName = f"./surveyOutput/{name}_DM{psrDm}_P{psrP}_cdmt_cDM{int(psrDm):03d}.{int((psrDm % 1) * 100)}_P000.fil"
		outName = f"./surveyOutput/{name}_DM{psrDm}_P{psrP}_8bit_cdmt_cDM{int(psrDm):03d}.{int((psrDm % 1) * 100)}_P000.fil"
		ref.writelines(f"digifil -b 8 -o {outName} {inName}\n")
		ref.writelines(f"rm {inName}\n")

		ref.writelines("\n")
		ref.writelines("\n")