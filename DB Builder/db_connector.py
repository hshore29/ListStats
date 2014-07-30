import sqlite3, csv, datetime
from readability import FleschKincaid

# Define common SQL statements
messages_create = ("""
CREATE TABLE IF NOT EXISTS `messages` (
  `id` TEXT NOT NULL,
  `threadId` TEXT NOT NULL,
  `metaThread` TEXT NOT NULL,
  `date` TEXT NOT NULL,
  `sender` TEXT NOT NULL,
  `alias` TEXT NOT NULL,
  `subject` TEXT NOT NULL,
  `snippet` TEXT NOT NULL,
  `sizeEst` INTEGER NOT NULL,
  `listserv` TEXT NOT NULL,
  PRIMARY KEY (`id`,`listserv`)
);""")

text_create = ("""
CREATE TABLE IF NOT EXISTS `text` (
  `id` TEXT NOT NULL,
  `text` TEXT NOT NULL,
  PRIMARY KEY (`id`)
);""")

textmeta_create = ("""
CREATE TABLE IF NOT EXISTS `textmeta` (
  `id` TEXT NOT NULL,
  `sent_count` INTEGER NOT NULL,
  `word_count` INTEGER NOT NULL,
  `syll_count` INTEGER NOT NULL,
  `us_grade` FLOAT NOT NULL,
  `min_age` FLOAT NOT NULL,
  PRIMARY KEY (`id`)
);""")

id_lookup_create = ("""
CREATE TABLE IF NOT EXISTS `id_lookup` (
  `sender` TEXT NOT NULL,
  `netid` TEXT NOT NULL,
  PRIMARY KEY (`sender`,`netid`)
);""")

id_lookup_insert = ("""
INSERT INTO `id_lookup`
(sender,netid)
VALUES (?,?)
;""")

id_lookup_replace = ("""
REPLACE INTO `id_lookup`
(sender,netid)
VALUES (?,?)
;""")

messages_insert=("""
INSERT INTO messages
(id,threadId,metaThread,date,sender,alias,subject,snippet,sizeEst,listserv)
VALUES (?,?,?,?,?,?,?,?,?,?);
""")

messages_replace=("""
REPLACE INTO messages
(id,threadId,metaThread,date,sender,alias,subject,snippet,sizeEst,listserv)
VALUES (?,?,?,?,?,?,?,?,?,?);
""")

text_insert = ("""
INSERT INTO `text`
(id,text)
VALUES (?,?)
;""")

text_replace = ("""
REPLACE INTO `text`
(id,text)
VALUES (?,?)
;""")

textmeta_insert = ("""
INSERT INTO `textmeta`
(id,sent_count,word_count,syll_count,us_grade,min_age)
VALUES (?,?,?,?,?,?)
;""")

textmeta_replace = ("""
REPLACE INTO `textmeta`
(id,sent_count,word_count,syll_count,us_grade,min_age)
VALUES (?,?,?,?,?,?)
;""")

class Database:
    def __init__(self,name,file):
        # Open db connection
        self.db_con = sqlite3.connect(name)
        self.db_cur = self.db_con.cursor()

        # Build tables if they don't exist
        self.db_cur.execute(id_lookup_create)
        self.db_cur.execute(messages_create)
        self.db_cur.execute(text_create)
        self.db_cur.execute(textmeta_create)

        # Load netID lookup file
        self.lookup = file
        self.loadLookup(self.lookup)

    def close(self):
        # Close connection
        self.db_con.close()

    def commit(self):
        # Commit changes
        self.db_con.commit()

    def insertReplace(self,insert,replace,record):
        # Attempt to insert record - if error, replace instead
        try:
            self.db_cur.execute(insert,record)
        except:
            self.db_cur.execute(replace,record)

    def loadLookup(self,lookup):
        # Load id_lookup file into id_lookup table
        with open(lookup) as file:
            netids = csv.DictReader(file)
            id_lookup_data = [(i['sender'].lower(),i['netid'].lower()) for i in netids]

        # Insert records
        for id_lookup in id_lookup_data:
            self.insertReplace(id_lookup_insert,id_lookup_replace,id_lookup)

        # Commit changes
        self.commit()

    def updateLookup(self):
        # Load list of senders from both db tables
        self.db_cur.execute("SELECT distinct(sender) FROM messages")
        senders = self.db_cur.fetchall()
        self.db_cur.execute("SELECT distinct(sender) FROM id_lookup")
        lookups = self.db_cur.fetchall()

        # If there is a new email not in the lookup table
        with open(self.lookup,'a') as file:
            csvWriter = csv.writer(file)
            for email in senders:
                if email not in lookups:
                    if '@cornell.edu' in email:
                        netid = email.replace('@cornell.edu','')
                    else:
                        netid = raw_input('ID for ' + email[0] + ':')
                    lookups.append(email)
                    csvWriter.writerow([email[0],netid])
                    self.db_cur.execute(id_lookup_insert,[email[0],netid])

        # Commit changes
        self.commit()

    def joinThreads(self):
        # Get list of threads that start with a reply
        self.db_cur.execute("SELECT threadId,subject,date FROM messages WHERE id = threadId AND subject LIKE 'Re:%'")
        splitThreads = self.db_cur.fetchall()
        
        # For each split thread, check to see if there are any matches
        for email in splitThreads:
            subject = email[1].replace('Re: ','').replace('RE: ','')
            fwdSubject = 'Fwd: ' + subject
            self.db_cur.execute("SELECT date,id FROM messages WHERE subject IN (?,?) AND id = threadId",[subject,fwdSubject])
            matches = self.db_cur.fetchall()
            
            # If there is a single match, group the threads
            if matches:
                if len(matches) == 1:
                    self.db_cur.execute("UPDATE messages SET metaThread = ? WHERE threadId = ?",[matches[0][1],email[0]])
                    
        # Commit changes
        self.commit()
                    
    def insertMsg(self,record):
        # Insert record into messages table
        self.insertReplace(messages_insert,messages_replace,record)

    def insertText(self,record):
        # Insert record into text table
        self.insertReplace(text_insert,text_replace,record)

        # Calculate readability metrics
        fk = FleschKincaid(record[1])
        metarecord = (record[0],fk.sent_count,fk.word_count,
                      fk.syll_count,fk.gradeLevel(),fk.minAge())

        # Insert text metadata
        self.insertReplace(textmeta_insert,textmeta_replace,metarecord)

    def getTimestamp(self):
        # Get last version, return
        self.db_cur.execute("SELECT date FROM messages ORDER BY date DESC LIMIT 1")
        ts = self.db_cur.fetchall()
        if len(ts) == 0:
            ts = '2000/01/01'
        else:
            ts = ts[0][0]
        return ts

    def addTextMetadata(self):
        # Method used to calculate metadata for all records in text
        # without having to reload the entire database
        self.db_cur.execute("SELECT * FROM text")
        data = self.db_cur.fetchall()
        
        for line in data:
            fk = FleschKincaid(line[1])
            metarecord = (line[0],fk.sent_count,fk.word_count,
                      fk.syll_count,fk.gradeLevel(),fk.minAge())
            self.insertReplace(textmeta_insert,textmeta_replace,metarecord)

        self.commit()
