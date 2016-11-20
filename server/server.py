#Database columns: ID, username, password, wins, losses, draws, elo, AI, available -> integer where 0 is false and 1 is true
#On page load: JS script checks for login details cookie, if they're there fills them in if not does something else?
from http.server import BaseHTTPRequestHandler,HTTPServer
from urllib.parse import parse_qs
import os.path, sqlite3, os, json, random
import xml.etree.ElementTree as ET

#Any new folder must be a key in accessDict with True if access is allowed and False if not
accessDict = {"server":False,"misc":False,"css":True,"pages":True,"img":True,"scripts":True,"fonts":True}

address = ("0.0.0.0",8080)

sessions = {}

def elo(r1,r2,s):
    replacementDict = {1:0,0.5:0.5,0:1}
    k = 32
    R1 = float(10 ** (r1 / 400))
    R2 = float(10 ** (r2 / 400))
    E1 = R1 / (R1 + R2)
    E2 = R2 / (R1 + R2)
    S1 = s
    S2 = replacementDict[s]
    newP1Rating = r1 + k * (S1 - E1)
    newP2Rating = r2 + k * (S2 - E2)
    return (newP1Rating,newP2Rating)

class myHandler(BaseHTTPRequestHandler):
    
    def contentType(self):

        if len(self.currentPath) == 1:
            self.headerEnding = "text/html"
            self.readMethod = "r"
            return
        
        if self.path[-4:] == ".css":
            self.headerEnding ="text/css"
            self.readMethod = "r"
            
        elif self.path[-5:] == ".html":
            self.headerEnding = "text/html"
            self.readMethod = "r"
        
        #As this is an image rb must be used to read files
        elif self.path[-4:] == ".jpg":
            self.headerEnding = "image/jpeg"
            self.readMethod = "rb"
        
        elif self.path[-4:] == ".png":
            self.headerEnding = "image/png"
            self.readMethod = "rb"
            
        elif self.path[-3:] == ".js":
            self.headerEnding = "application/javascript"
            self.readMethod = "r"
        
    def send_400(self):
        
        print("Sending 400")
        self.send_response(400)
        self.send_header("Content-type","text/html")
        self.end_headers()
        thePath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"pages","invalidrequest.html")
        file = open(thePath,"r").read()
        self.wfile.write(bytes(file,"utf-8"))
        return
    
    #Sends a set of user data in xml format. Used by account creation and log in requests.
    def sendUserInfo(self,cursor,user):
        '''
        cursor.execute("select username,wins,losses,draws,elo,AI,available from accounts where username=?",(user,))
        row = cursor.fetchall()[0]
        rawXML = ET.Element("data")
        usernameXML = ET.SubElement(rawXML,"username")
        usernameXML.text = row[0]
        winsXML = ET.SubElement(rawXML,"wins")
        winsXML.text = str(row[1])
        lossesXML = ET.SubElement(rawXML,"losses")
        lossesXML.text = str(row[2])
        drawsXML = ET.SubElement(rawXML,"draws")
        drawsXML.text = str(row[3])
        eloXML = ET.SubElement(rawXML,"elo")
        eloXML.text = str(row[4])
        aiXML = ET.SubElement(rawXML,"AI")
        aiXML.text = str(row[5])
        availXML = ET.SubElement(rawXML,"available")
        availXML.text = str(row[6])
        data = ET.tostring(rawXML)
        self.send_response(200)
        self.send_header("Content-type","text/xml")
        self.end_headers()
        self.wfile.write(data)
        '''
        
        
    def send_403(self): 
        
        self.send_response(403)
        self.send_header("Content-type","text/html")
        self.end_headers()
        self.wfile.write(bytes("Access denied (incorrect or improper credentials).","utf-8"))
    
    def getData(self,cursor,columnToFind,columnToIdentify,identifier):
        
        cursor.execute("select " + columnToFind + " from accounts where " + columnToIdentify + "=?",(identifier,))
        return cursor.fetchone()[0]
    
    def setData(self,cursor,columnToChange,columnToIdentify,newValue,identifier):
        
        cursor.execute("update accounts set " + columnToChange + "=? where " + columnToIdentify + "=?",(newValue,identifier))
    
    def generateSessionID(self,length):
        
        characters = "ABCDEFGHIJKLOMNOQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890"
        myString = ""
        
        for x in range(0,length):
            myString += characters[random.randint(0,len(characters)-1)]
            
        return myString
         
    def send_myaccount(self,cursor,username):
        
        global sessions
        accountFile = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"pages","myaccount.html")
        accountFile = str(open(accountFile,"r").read())
        cursor.execute("select username,wins,losses,draws,elo,available from accounts where username=?",(username,))
        row = cursor.fetchall()[0]
        if row[5] == 1:
            availability = "Available"
        else:
            availability = "Unavailable"
        accountFile = accountFile.replace("$username",row[0])
        accountFile = accountFile.replace("$wins",str(row[1]))
        accountFile = accountFile.replace("$losses",str(row[2]))
        accountFile = accountFile.replace("$draws",str(row[3]))
        accountFile = accountFile.replace("$elo",str(row[4]))
        accountFile = str(accountFile.replace("$available",availability))
        self.send_response(200)
        self.send_header("Content-type","text/html")
        userSessionID = str(self.generateSessionID(10))
        sessions[userSessionID] = username
        print(userSessionID)
        self.send_header("Set-Cookie","<session-id>=" + userSessionID)
        self.end_headers()
        print(sessions)
        self.wfile.write(bytes(accountFile,"utf-8"))
         
    def do_GET(self):
        
        self.currentPath = self.path.split("/")
        self.currentPath = self.currentPath[1:]
        #Pages
        print(self.currentPath)
        if len(self.currentPath) == 1:
        #This needs rewriting to take into account user ID            
            if self.currentPath[-1] == "":
                pathEnding = "index.html"
                
            else:
                pathEnding = self.currentPath[-1] + ".html"
            thePath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"pages",pathEnding)
            
        #Any other resources
        
        elif accessDict[self.currentPath[0]] == False:
            self.send_403()
            return
            
        else:
            thePath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            for x in self.currentPath:
                thePath = os.path.join(thePath,x)

        #Select the correct content-type ending for header from HTTP request, as well as reading method
        self.contentType()
        
        #Attempt to open requested resource
        try:
            file = open(thePath,self.readMethod).read()
            self.send_response(200)
            
        #If attempt fails send 404 code
        except:
            thePath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"pages","notfound.html")
            file = open(thePath,"r").read()
            self.send_response(404)
            self.headerEnding = "html"
        
        
        self.send_header("Content-type",self.headerEnding)
        self.end_headers()
        
        if self.readMethod == "r":
            self.wfile.write(bytes(file, 'UTF-8'))
            
        else:
            self.wfile.write(file)
    
    def send_index(self,code):
        self.send_response(code)
        self.send_header("Content-type","text/html")
        self.end_headers()
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"pages","index.html")
        fileToSend = open(path,"r").read()
        self.wfile.write(bytes(fileToSend,"utf-8"))
        
    
    def do_POST(self):
        
        dbConn = sqlite3.Connection("users.db")
        dbConn.text_factory = str
        dbConnCurs = dbConn.cursor()
        #Find post parameters
        length = int(self.headers['content-length'])
        postvars = parse_qs(self.rfile.read(length).decode(), keep_blank_values=1)
        #Checks that request has a request code attached
        print(postvars)
        try:
            requestCode = postvars["requestcode"][0]
            if requestCode == "create account":
                
                try:
                    username = postvars["username"][0]
                    password = postvars["password"][0]
                    dbConnCurs.execute("select max(id) from accounts")
                    
                    try:
                        currentID = 1 + dbConnCurs.fetchone()[0]
                        
                    except:
                        currentID = 1
                        
                    dbConnCurs.execute("select ID from accounts where username=?",(username,))
                    
                    try:
                        if len(dbConnCurs.fetchall()) > 0:
                            raise Exception
                            
                    except:
                        self.send_index(403)
                        return
                    
                    try:
                        dbConnCurs.execute("insert into accounts values (?,?,?,?,?,?,?,?,?)",(currentID,username,password,0,0,0,1200,username,0))
                        dbConn.commit()
                        userAI = open(os.path.join("User computers",username + ".py"),"w")
                        self.send_myaccount(dbConnCurs,username)
                        
                    except:
                        self.send_index(400)
                        return
                    
                except:
                    self.send_index(400)
                    return
                    
            elif requestCode == "log in":
                username = postvars["username"][0]
                password = postvars["password"][0]
                print(username)
                print(password)
                try:
                    dbConnCurs.execute("select password from accounts where username=?",(username,))
                    dbPassword = dbConnCurs.fetchone()[0]
                    
                except:
                    print("username error")
                    self.send_index(400)
                    dbConn.close()
                    return
                
                if dbPassword != password:
                    print("Incorrect password error.")
                    self.send_index(403)
                    dbConn.close()
                    return    
                
                self.send_myaccount(dbConnCurs,username)
    
                #Logged in requests below here
            
            sessionID = postvars["sessionID"]
            username = sessions[sessionID]
                            
            if requestCode == "upload AI":
                code = postvars["code"][0]
                code = code.split("\\n")
                fileName = self.getData(dbConnCurs,"AI","username",username) + ".py"
                aiFile = open(os.path.join("User computers",fileName),"w")
                aiFile.write("")
                aiFile.close()
                aiFile = open(os.path.join("User computers",fileName),"a")
                
                for x in code:
                    aiFile.write(x)
                    aiFile.write("\n")
                    
                aiFile.close()
                self.send_response(200)
                self.send_header("Content-type","text/html")
                self.end_headers()
                self.wfile.write(bytes("AI successfully saved.","utf-8"))
                
            elif requestCode == "change AI name":
                newName = postvars["newname"][0]
                oldName = self.getData(dbConnCurs,"AI","username",username)
                
                try:
                    self.getData(dbConnCurs,"username","AI",newName)
                    self.send_400()
                    dbConn.close()
                    return
                
                except:
                    pass
                
                for x in os.listdir("User computers"):
                    print(x)
                    if x == oldName + ".py":
                        print("Found old AI")
                        os.rename(os.path.join("User computers",oldName + ".py"),os.path.join("User computers",newName + ".py"))
                    
                dbConnCurs.execute("update accounts set AI=? where username=?",(newName,username))
                dbConn.commit()
                self.sendUserInfo(dbConnCurs,username)
                
            elif requestCode == "get available opponents":
                print("user list req received")
                dbConnCurs.execute("select username from accounts where available=?",(1,))
                userList = dbConnCurs.fetchall()
                listString = ""
                for x in userList:
                    if x != username:
                        listString += x[0] + "#"
                rawXML = ET.Element("data")
                userString = ET.SubElement(rawXML,"users")
                userString.text = listString
                self.send_response(200)
                self.send_header("Content-type","text/xml")
                self.end_headers()
                self.wfile.write(ET.tostring(rawXML))
            
            elif requestCode == "change AI availability":
                newState = int(postvars["state"][0])
                self.setData(dbConnCurs,"available","username",newState,username)
                dbConn.commit()
                self.sendUserInfo(dbConnCurs,username)
        
            elif requestCode == "challenge":
                opponent = postvars["opponent"][0]
                if self.getData(dbConnCurs,"available","username",opponent) == 0:
                    raise Exception
                #Make match here
                
                
        #If not, sends code 400 response
                
        except TypeError:
            self.send_400()
            
        dbConn.close()
    
    
myServer = HTTPServer(address, myHandler)
print("Listening on port",address[1])
myServer.serve_forever()
  