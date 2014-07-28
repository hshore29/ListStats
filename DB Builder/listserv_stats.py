from ftp_module import Website
from gmail_api import GmailAPI
from db_connector import Database

# Define list servs & gmail label Ids
listservs = [{'name':'Bros','id':'Label_7','address':'<kdr-brothers-l.cornell.edu>'},
             {'name':'Events','id':'Label_9','address':'<kdr-events-l.cornell.edu>'},
             {'name':'Spams','id':'Label_8','address':'<kdr-spam-l.cornell.edu>'}]

# Create FTP connection object, download db
#ftp = Website('kdrcornell.com','/intraweb/listservstats',
#              '*******','*****')
#ftp.retr('kdr_listserv.db')

# Create SQLite and Gmail connection objects, update db
db = Database('kdr_listserv.db','id_lookup.csv')
#gmail = GmailAPI(db)
#gmail.loadMsgs(listservs)
#db.updateLookup()
#db.joinThreads()
db.addTextMetadata()
db.commit()

# Close SQLite connection, upload updated db file
db.close()
#ftp.stor('kdr_listserv.db')
