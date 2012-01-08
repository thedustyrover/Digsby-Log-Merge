Digsby Log Merge
Nathan Yan
http://thedailynathan.com/digsbymerge/

Digsby Log Merge is a little utility I wrote for merging log files from the multi-protocol instant message client Digsby. It reads log files from two different locations and outputs a set of merged logs with the same directory structure, so you can simply copy it into your Digsby logs directory. The original log files are not modified.

Usage

merge.py fromLogsDirectory toLogsDirectory mergedLogsDirectory

There are three parameters, only the first two of which are really needed:
 * fromLogsDirectory: the directory containing the logs you want to merge from
 * toLogsDirectory: the directory containing the logs you want to merge the fromLogs to (nothing is actually written here - see below for from/to explanation)
 * mergedLogsDirectory: the directory where the merged logs will be created. If not defined, this will default to "merged" in the directory where the script is run from

Notes:

 * The fromLogsDirectory is used as the master list of files to be merged (so if a file exists in toLogsDirectory but not in fromLogsDirectory, no merged file will be created.
 * If a file exists in fromLogsDirectory but not toLogsDirectory, a merged file will be created (a copy of the fromFile)
 * To finish the merge, simply copy the merged files in mergedLogsDirectory to your Digsby log directory (e.g. C:\Users\yourName\Documents\Digsby Logs). Be sure to make a backup of the existing logs if something goes wrong
 * The python script was developed under Python v3.2.2. I haven't tried with Python v2.x, but since even the print statements have changed I'm guessing it will need at least some adjustment.