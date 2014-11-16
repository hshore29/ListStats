import os
from ftplib import FTP

class Website:
    def __init__(self,domain,path,user,passw):
        self.ftp = FTP(domain,user,passw)
        self.ftp.cwd(path)
        
    def retr(self,file):
        with open(file,'wb') as f:
            print "Downloading " + file + "..."
            self.ftp.retrbinary('RETR %s' % file, lambda data: f.write(data))

    def stor(self,file):
        with open(file,'rb') as f:
            print "Uploading " + file + "..."
            self.ftp.storbinary('STOR %s' % file, f)
