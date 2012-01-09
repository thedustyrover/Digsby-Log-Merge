import sys
import os
import time
import codecs
import xml.etree.ElementTree as ElementTree
import shutil

#Sanitizes a potential message string into xml
#This cleans up a few message problems that may prevent
def sanitizePotentialMsgToXml(string):
    #sanitizedStr = string
    sanitizedStr = string.replace('<br>','<br/>')
    return sanitizedStr
    

#Check if the line contains a Digsby format message
#Currently the criteria is:
# 1. It's xml-ish (see filtering below), and
# 2. the top-level xml element has a "timestamp" attribute, and
# 3. the top-level xml element has a "class" attribute, and
# 4. the class attribute is space-separated elements, and contains "message" as one of the elements
#
# If things break, it's a good idea to look here to see if Digsby changed their log format
def getMessageElementFromCompleteLine(line):

    sanitizedLine = sanitizePotentialMsgToXml(line)
    
    try:
        xml = ElementTree.fromstring(sanitizedLine)
        if 'timestamp' not in xml.attrib:
            return None
        if 'class' in xml.attrib:
            classes = xml.attrib['class'].split(' ')
            if 'message' in classes:
                return xml
    except ElementTree.ParseError:
        return None

    return None

def getMessageElementFromAtLeastPartialLine(line):
    firstParenIndex = line.find('<')
    if (firstParenIndex < 0):
        return None
    secondParenIndex = line.find('>',firstParenIndex+1)
    if (secondParenIndex < 0):
        return None

    firstElementStr = line[firstParenIndex:secondParenIndex+1]  + '</div>'
    try:
        firstElementXml = ElementTree.fromstring(firstElementStr)
        if 'timestamp' not in firstElementXml.attrib:
            return None
        if 'class' in firstElementXml.attrib:
            classes = firstElementXml.attrib['class'].split(' ')
            if 'message' in classes:
                return firstElementXml
    except ElementTree.ParseError:
        return None

    return None

def isCompleteMessageLine(line):
    msg = getMessageElementFromCompleteLine(line)
    if (msg == None):
        return False
    else:
        return True

def isAtLeastBeginningOfMessageLine(line):
    msg = getMessageElementFromAtLeastPartialLine(line)
    if (msg == None):
        return False
    else:
        return True

def getMessageLine(line):
    msg = None;
    msg = getMessageElementFromCompleteLine(line)
    if (msg == None):
        msg = getMessageElementFromAtLeastPartialLine(line)

    return msg


#Given a log file at fromFilePath and toFilePath, creates a merged file at outputFilePath
#A merged file is a copy of the toFile, with any messages in the fromFile inserted among
#the messages of the toFile in a time-ordered fashion
def mergeLogs(fromFilePath, toFilePath, outputFilePath):
    fromFile = codecs.open(fromFilePath, 'r','utf-8')
    toFile = codecs.open(toFilePath, 'r','utf-8')
    outputFile = codecs.open(outputFilePath, 'w','utf-8')

    #Loop through the toFile, writing each of its lines to the output file
    #We'll check the fromFile and insert its message lines in between
    insideToMessageSectionFlag = False
    insideFromMessageSectionFlag = False
    currentFromLine = fromFile.readline()

    toCount = 1
    fromCount = 1
    for toLine in toFile:

        #Do a check to see if we've reached the message section
        if not insideToMessageSectionFlag:
            if isAtLeastBeginningOfMessageLine(toLine):
                insideToMessageSectionFlag = True
                
        if insideToMessageSectionFlag:
            toMsgXml = getMessageLine(toLine)
            if (toMsgXml != None): #This is at least the beginning of a message,
                #write any messages from fromFile that comes before this message
                toMsgTime = time.strptime(toMsgXml.attrib['timestamp'],'%Y-%m-%d %H:%M:%S')
                
                while (currentFromLine != ''):                    
                    if not insideFromMessageSectionFlag:
                        if isAtLeastBeginningOfMessageLine(currentFromLine):
                            insideFromMessageSectionFlag = True

                    if insideFromMessageSectionFlag:
                        fromMsgXml = getMessageLine(currentFromLine)
                        if (fromMsgXml != None): #This is at least the beginning of a fromMessage,
                            fromMsgTime = time.strptime(fromMsgXml.attrib['timestamp'],'%Y-%m-%d %H:%M:%S')
                    
                            #Compare fromMsg time to current toMsg
                            #Stop writing if the fromLine occurs after
                            if (fromMsgTime >= toMsgTime):
                                break

                        outputFile.write(currentFromLine)
                    
                    #Read the next line from the fromFile. We get here if the currentFromLine:
                    # A) is not a message, or
                    # B) does not occur before the toMsg
                    #We leave it unchanged if it is a message and happens after toMsg,
                    #so that it can be used to compare against the next toMsg
                    currentFromLine = fromFile.readline()
                    fromCount+=1
            else: #This is a line that is inside the message section, but not the start of a message. Just write it.
                pass

        #All lines from the toFile are written
        outputFile.write(toLine)
        toCount+=1

    #Write any remaining messages from the fromFile
    while (currentFromLine != ''):
        outputFile.write(currentFromLine)
        currentFromLine = fromFile.readline()

    fromFile.close()
    toFile.close()
    outputFile.close()

#Defaults for test purposes    
fromLogsDir = 'testFrom'
toLogsDir = 'testTo'
outputLogsDir = 'merged'

#Check command line args. First arg is the script name
if (len(sys.argv) >= 2): #first arg is from dir
    fromLogsDir = sys.argv[1]
if (len(sys.argv) >= 3): #second arg is from dir
    toLogsDir = sys.argv[2]
if (len(sys.argv) >= 4): #first arg is from dir
    outputLogsDir = sys.argv[3]

#Dive through fromLogsDir to find all log files
if not os.path.exists(fromLogsDir):
    print("fromLogsDir "+fromLogsDir+" does not exist!")
    input("Press Enter to close")
    sys.exit(1)
else:
    fileCount = 0
    
    for root, dirs, files in os.walk(fromLogsDir):
        for file in files:
            fromFilePath = os.path.join(root, file)

            # Find the matching toFile, and merge them if it exists
            commonPath = os.path.relpath(fromFilePath,fromLogsDir)
            matchingToFilePath = os.path.join(toLogsDir,commonPath)
            matchingOutputFilePath = os.path.join(outputLogsDir,commonPath)
            if not os.path.exists(os.path.dirname(matchingOutputFilePath)): #Make the output directory if needed
                    os.makedirs(os.path.dirname(matchingOutputFilePath))
			
            if os.path.exists(matchingToFilePath):                
                mergeLogs(fromFilePath,matchingToFilePath,matchingOutputFilePath)
                print("Merged " + commonPath)
                fileCount+=1
            else: #fromFile exists but no toFile, so we can do a direct copy of fromFile
                shutil.copyfile(fromFilePath,matchingOutputFilePath)
                print("Copied " + commonPath)
                fileCount+=1
    
    print("")
    print("Merged " + str(fileCount) + " files to " + os.path.abspath(outputLogsDir))
    input("Press Enter to close")
