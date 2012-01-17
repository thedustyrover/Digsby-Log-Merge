import sys
import os
import time
from xml.etree.ElementTree import SubElement as SE, Element as E, fromstring, ElementTree
import shutil

#Given a log file at fromFilePath and toFilePath, creates a merged file at outputFilePath
#A merged file is a copy of the toFile, with any messages in the fromFile inserted among
#the messages of the toFile in a time-ordered fashion
def mergeLogs(fromFilePath, toFilePath, outputFilePath):
    utf8open = lambda s: open(s, 'r', 'utf8')

    outputDoc = E('html')

    with utf8open(fromFilePath) as fromFile, utf8open(toFilePath) as toFile:

        # the body and HTML tags are left open so the app can just append
        # when a new message comes in. we have to close them.
        # note: this could also be taken care of by BeautifulSoup or
        # perhaps lxml.html

        fromDoc = fromstring(fromFile.read() + '</BODY></HTML>')
        toDoc = fromstring(toFile.read() + '</BODY></HTML>')

        # copy the head tag so formatting and stuff is preserved in our new doc
        outputDoc.append(fromDoc.find('HEAD').copy())

        fromMessages = fromDoc.findall('./BODY/div')
        toMessages = toDoc.findall('./BODY/div')

        allMessages = list(fromMessages) + list(toMessages)
        allMessages.sort(key = lambda e: time.strptime(e.attrib['timestamp'], '%Y-%m-%d %H:%M:%S'))

        body = SE(outputDoc, 'BODY', attrib = fromDoc.find('BODY').attrib)
        body.extend(x.copy() for x in allMessages)

    ElementTree(outputDoc).write(outputFilePath, 'utf8')

def main(fromLogsDir, toLogsDir, outputLogsDir = './merged'):
    #Dive through fromLogsDir to find all log files
    if not os.path.exists(fromLogsDir):
        print("fromLogsDir %r does not exist!" % fromLogsDir, file = sys.stderr)
        return 1

    fileCount = 0

    for root, dirs, files in os.walk(fromLogsDir):
        for file in files:
            fromFilePath = os.path.join(root, file)

            # Find the matching toFile, and merge them if it exists
            commonPath = os.path.relpath(fromFilePath, fromLogsDir)
            matchingToFilePath = os.path.join(toLogsDir, commonPath)
            matchingOutputFilePath = os.path.join(outputLogsDir, commonPath)
            if not os.path.exists(os.path.dirname(matchingOutputFilePath)): #Make the output directory if needed
                os.makedirs(os.path.dirname(matchingOutputFilePath))

            if os.path.exists(matchingToFilePath):
                mergeLogs(fromFilePath, matchingToFilePath, matchingOutputFilePath)
                print("Merged " + commonPath)
                fileCount+=1
            else: #fromFile exists but no toFile, so we can do a direct copy of fromFile
                shutil.copyfile(fromFilePath, matchingOutputFilePath)
                print("Copied " + commonPath)
                fileCount+=1

    print("")
    print("Merged %d files to %r" % (fileCount, os.path.abspath(outputLogsDir)))
    fileCount = 0

    return 0

def test():
    return main('testFrom', 'testTo', 'merged')

if __name__ == '__main__':
    if len(sys.argv == 2) and sys.argv[1] == 'test':
        sys.exit(test())

    result = main(*sys.argv[1:])
    input("Press Enter to close")
    sys.exit(result)

