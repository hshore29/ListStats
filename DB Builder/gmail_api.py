import httplib2, datetime, time, base64, sys, re

from apiclient.discovery import build
from apiclient.http import BatchHttpRequest, HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run

from dateutil import parser

class GmailAPI:
    def __init__(self,db):
        # Path to the client_secret.json file downloaded from the Developer Console
        CLIENT_SECRET_FILE = 'client_secret.json'

        # Check https://developers.google.com/gmail/api/auth/scopes for all available scopes
        OAUTH_SCOPE = 'https://www.googleapis.com/auth/gmail.readonly'

        # Location of the credentials storage file
        STORAGE = Storage('gmail.storage')

        # Start the OAuth flow to retrieve credentials
        self.flow = flow_from_clientsecrets(CLIENT_SECRET_FILE, scope=OAUTH_SCOPE)
        self.http = httplib2.Http()

        # Try to retrieve credentials from storage or run the flow to generate them
        self.credentials = STORAGE.get()
        if self.credentials is None or self.credentials.invalid:
            self.credentials = run(self.flow, STORAGE, http=self.http)

        # Authorize the httplib2.Http object with our credentials
        self.http = self.credentials.authorize(self.http)

        # Build the Gmail service from discovery
        self.mailbox = build('gmail', 'v1', http=self.http)
        self.messages = self.mailbox.users().messages()

        # Store connection to the database
        self.db = db

    # Function to find, get, and insert messages
    def loadMsgs(self,labels):
        # For each label, return a list of message Ids
        self.labels = labels
        ts = (parser.parse(self.db.getTimestamp()) + datetime.timedelta(days=-1))
        for item in self.labels:
            print "Loading " + item['name'] + "..."
            idList = self.getMsgIds(item['id'], 'after: ' + ts.strftime('%Y/%m/%d'))

            # For each id, add 'get' to batch
            n = 0
            self.curLab = item['name']
            self.batch = BatchHttpRequest(callback=self.insertMsg)
            for num in idList:
                self.batch.add(self.messages.get(userId='me',id=num),request_id=num)
                n = n + 1
                               
                # After 1000 or at the end of the list, execute batch and commit
                if ((n % 1000) == 0) | (n == len(idList)):
                    print str(n) + " / " + str(len(idList))
                    try:
                        self.batch.execute(http=self.http)
                    except:
                        print "Unexpected error:", sys.exc_info()[0]
                        raise
                    self.db.commit()
                    self.batch = BatchHttpRequest(callback=self.insertMsg)
                    
            print "Finished " + item['name'] + "!"

    # Return a list of message ids with the given label & matching the given query
    def getMsgIds(self,label,query):
        # Get list of messages given label, query
        msgs = self.messages.list(userId='me', labelIds=label,
                                  q=query, maxResults=500).execute()
        # Add each id to a list, return list
        idList = list()
        while True:
            if 'messages' not in msgs.keys():
                break
            for item in msgs['messages']:
                idList.append(item['id'])
            if 'nextPageToken' in msgs.keys():
                msgs = self.cooldown(self.messages.list(userId='me', labelIds=label,
                                                  q=query, maxResults=500,
                                                  pageToken=msgs['nextPageToken']))
            else:
                break 
        return idList
    
    # Callback function for batch request - handles db insertion
    def insertMsg(self, request_id, response, exception):
        # Handle exceptions
        if exception is not None:
            if (type(exception) == HttpError) & (exception.resp.status in [429,403]):
                response = self.cooldown(self.messages.get(userId='me',id=request_id))
            else:
                raise exception

        # Save relevant header values
        listserv = self.curLab
        for tag in response['payload']['headers']:
            if tag['name'] == 'Date':
                date = parser.parse(tag['value']).strftime("%Y-%m-%d %H:%M:%S")
            if tag['name'] == 'From':
                alias = tag['value'].split('<')[0].strip().replace('"','')
                try:
                    sender = tag['value'].split('<')[1].replace('>','').lower()
                except IndexError:
                    sender = alias.lower()
            if tag['name'] == 'Subject':
                subject = tag['value']
            if tag['name'] == 'List-Id':
                listserv = self.labelLookup(tag['value'])

        # Recursively find all body text
        container = ['multipart/alternative','multipart/related','multipart/mixed']
        textData = ['text/plain','text/html']
        def getBody(payload,output):
            #print payload['mimeType']
            if payload['mimeType'] in container:
                for part in payload['parts']:
                    output = getBody(part,output)
            elif payload['mimeType'] in textData:
                try:
                    body = base64.urlsafe_b64decode(payload['body']['data'].encode('UTF-8'))
                except KeyError:
                    print payload['mimeType'] + ": No Data"
                    body = ''
                output[payload['mimeType']] = body

            return output

        msg = {}
        msg = getBody(response['payload'],msg)
        
        # If there is a text/plain component, parse and insert it
        if 'text/plain' in msg.keys():
            text = self.removeQuotes(msg['text/plain'],True)
            self.db.insertText((response['id'],text))
        
        # Insert header data into messages tabel
        self.db.insertMsg((response['id'],response['threadId'],response['threadId'],
                           date,sender,alias,subject,response['snippet'],
                           response['sizeEstimate'],listserv))

    # Process request while making sure API doesn't exceed rate limit
    def cooldown(self,request):
        while True:
            try:
                response = request.execute()
                return response
            except HttpError:
                time.sleep(1)

    # Given an email address, return the matching name from self.labels
    def labelLookup(self,address):
        for lab in self.labels:
            if lab['address'] == address:
                return lab['name']
        return 'Other'

    # Remove quoted text from text/plain body using regex
    def removeQuotes(self,text,flatten=False):
        # Clean up line breaks, remove quoted text
        text = text.replace("\r\n","\n")
        text = re.split('^>',text,flags=re.M)[0]
        
        # Define header patterns
        patterns = ['^(On\s(.+)wrote:)$',
                    '^(Le\s(.+)crit :)$',
                    '^(20[0-9]{2}\-(0?[1-9]|1[012])\-(0?[1-2][0-9]|3[01]|[1-9])\s(.+):)$']
        
        # Find each header pattern, remove multi lines
        for pattern in patterns:
            m = re.search(pattern,text,flags=(re.M|re.DOTALL))
            if m:
                sub = m.string[m.start():m.end()]
                text = text.replace(sub,sub[::-1].replace('\n','',2)[::-1])
                text = re.split(pattern,text,flags=re.M)[0]

        # Optional: remove all new line characters
        if flatten:
            text = text.replace('\n',' ').strip()

        # Return clean text
        return text.decode('utf-8')
