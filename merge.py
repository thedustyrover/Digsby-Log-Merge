import sys
import os
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
def isMessageLine(line):

    sanitizedLine = sanitizePotentialMsgToXml(line)
    
    try:
        xml = ElementTree.fromstring(sanitizedLine)
        if 'timestamp' not in xml.attrib:
            return False
        if 'class' in xml.attrib:
            classes = xml.attrib['class'].split(' ')
            if 'message' in classes:
                return True
    except ElementTree.ParseError:
        return False

    return False

#Given a log file at fromFilePath and toFilePath, creates a merged file at outputFilePath
#A merged file is a copy of the toFile, with any messages in the fromFile inserted among
#the messages of the toFile in a time-ordered fashion
def mergeLogs(fromFilePath, toFilePath, outputFilePath):
    fromFile = open(fromFilePath, 'r')
    toFile = open(toFilePath, 'r')
    outputFile = open(outputFilePath, 'w')

    #Loop through the toFile, writing each of its lines to the output file
    #We'll check the fromFile and insert its message lines in between
    insideToMessageSectionFlag = False
    insideFromMessageSectionFlag = False
    currentFromLine = fromFile.readline()

    toCount = 1
    fromCount = 1
    for toLine in toFile:
        #No special processing if we haven't reached the message section,
        #or if it's the newline at the end of the message section
        if insideToMessageSectionFlag or isMessageLine(toLine):
            insideToMessageSectionFlag = True

            #the only non-message in the message section is the trailing newline
            if (toLine == '\n'):
                outputFile.write(toLine)
                toCount+=1
                
            try:
                toMsgXml = ElementTree.fromstring(sanitizePotentialMsgToXml(toLine))
            except ElementTree.ParseError:
                print("XML Parse Error of message in toFile " + toFilePath + " line " + str(toCount))
                print("line:" + toLine)
                input("Press Enter to close")
                sys.exit(1)
                
            toMsgTime = toMsgXml.attrib['timestamp']

            # write any msg from fromFile that comes before this msg
            while (currentFromLine != ''):
                if insideFromMessageSectionFlag or isMessageLine(currentFromLine):
                    insideFromMessageSectionFlag = True
                    
                    try:
                        fromMsgXml = ElementTree.fromstring(sanitizePotentialMsgToXml(currentFromLine))
                        
                    except ElementTree.ParseError:
                        print("XML Parse Error of message in fromFile " + fromFilePath + " line " + str(fromCount))
                        print("line:" + currentFromLine)
                        input("Press Enter to close")
                        sys.exit(1)
                    
                    fromMsgTime = fromMsgXml.attrib['timestamp']
                    
                    #Compare fromMsg time to current toMsg
                    #Write the line if it occurs before
                    if (fromMsgTime < toMsgTime):
                        outputFile.write(currentFromLine)
                    else:
                        break

                #Read the next line from the fromFile
                #We get here if the currentFromLine:
                # A) is not a message, or
                # B) does not occur before the toMsg
                #We leave it unchanged if it is a message and happens after toMsg,
                #so that it can be used to compare against the next toMsg
                currentFromLine = fromFile.readline()
                fromCount+=1

        #All lines from the toFile are written
        outputFile.write(toLine)
        toCount+=1

    #Write any remaining messages from the fromFile
    while (currentFromLine != ''):
        if isMessageLine(currentFromLine):
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