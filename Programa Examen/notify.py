import rrdtool , smtplib , tempfile
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from os.path import basename

mailsender = 'asr4cm3@gmail.com'
password = 'redes34cm3'
mailreceip = 'olbrlvalbt@gmail.com'
mailserver = 'smtp.gmail.com: 587'


def sendAlertEmail(subject, img, rrd):
    	""" Will send e-mail, attaching png
    	files in the flist.
    	"""
	msg = MIMEMultipart()
	msg['Subject'] = subject
	msg['From'] = mailsender
	msg['To'] = mailreceip

    	with open(img, 'rb') as f:
        	part = MIMEApplication(f.read(), Name = basename(img))
        	part['Content-Disposition'] = 'attachment; filename="%s"' % basename(img)
        	msg.attach(part)
	with open(rrd, 'rb') as f:
		part = MIMEApplication(f.read(), Name = basename(rrd))
		part['Content-Disposition'] = 'attachment; filename="%s"' % basename(rrd)
		msg.attach(part)
    
	mserver = smtplib.SMTP(mailserver)
	mserver.starttls()
	mserver.login(mailsender, password)

	mserver.sendmail(mailsender, mailreceip, msg.as_string())
	mserver.quit()


def check_aberration(rrdpath, fname):
	""" This will check for begin and end of aberration
	in file. Will return:
	0 if aberration not found.
	1 if aberration begins
	2 if aberration ends
	"""
	ab_status = 0
	rrdfilename = rrdpath + fname

	info = rrdtool.info(rrdfilename)
	rrdstep = int(info['step'])
	lastupdate = info['last_update']
	previosupdate = str(lastupdate - rrdstep - 1)
	graphtmpfile = tempfile.NamedTemporaryFile()
	# Ready to get FAILURES  from rrdfile
	# will process failures array values for time of 2 last updates
	values = rrdtool.graph(graphtmpfile.name+'F',
		           'DEF:f0=' + rrdfilename + ':inoctets:FAILURES:start=' + previosupdate + ':end=' + str(lastupdate),
		           'PRINT:f0:MIN:%1.0lf',
		           'PRINT:f0:MAX:%1.0lf',
		           'PRINT:f0:LAST:%1.0lf')

	f = open(str(rrdpath)+"Informe.txt","a")
	f.write(str("New aberration\n"))
	f.write(str(values)+"\n")
	fmin = float(values[2][0])
	fmax = float(values[2][1])
	flast = float(values[2][2])
	f.write(str("fmin="+str(fmin)+", fmax="+str(fmax)+",flast="+str(flast))+"\n\n")
	#print ("fmin="+str(fmin)+", fmax="+str(fmax)+",flast="+str(flast))
	# check if failure value had changed.
	f.close()
	if (fmin != fmax):
		if (flast == 1):
	   		ab_status = 1
		else:
	    		ab_status = 2
	return ab_status


