Digsby Log Merge
Nathan Yan
http://thedailynathan.com/digsbymerge/

Digsby Log Merge is a little utility I wrote for merging log files from the multi-protocol instant message client Digsby. It reads log files from two different locations and outputs a set of merged logs with the same directory structure, so you can simply copy it into your Digsby logs directory. The original log files are not modified, though you'll eventually want to copy the merged files over them so Digsby can use them.

Note that this script is NOT officially associated with Digsby in any way. I'm just a Digsby user and thought this would be a convenient tool to have. Use at your own risk!

Usage

The general use case of this script is merging logs from one location, such as a backup or secondary computer, to a master location, such as your primary computer or maybe a shared directory under a service like dropbox. To use, run the script from a command line like so:

merge.py fromLogsDirectory toLogsDirectory mergedLogsDirectory

There are three parameters, but only the first two are really needed:

fromLogsDirectory: the directory containing the logs you want to merge from
toLogsDirectory: the directory containing the logs you want to merge the fromLogs to (nothing is actually written here - see below for from/to explanation)
mergedLogsDirectory: the directory where the merged logs will be created. If not defined, this will default to "merged" in the directory where the script is run from

Notes:

* The fromLogsDirectory is used as the master list of files to be merged (so if a file exists in toLogsDirectory but not in fromLogsDirectory, no merged file will be created.
* If a file exists in fromLogsDirectory but not toLogsDirectory, a merged file will be created (a copy of the fromFile)
* To finish the merge, simply copy the merged files in mergedLogsDirectory to your Digsby log directory (e.g. C:\Users\yourName\Documents\Digsby Logs). Be sure to make a backup of the existing logs in case something goes wrong.
* The python script was developed under Python v3.2.2. I haven't tried with Python v2.x, but since even the print statements have changed I'm guessing it will need at least some adjustment.

Download

Both the source python script and a Windows executable (run the included .bat) are available on GitHub!. https://github.com/thedailynathan/Digsby-Log-Merge

Contact

My test set when writing this was just my own logs, which admittedly isn't a large data set. Feel free to contact me at thedailynathan (gmail domain)