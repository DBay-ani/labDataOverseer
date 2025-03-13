import sqlite3
import config;
from utils.contracts import requires, ensures;

import subprocess;

import sys ;

from databaseIOManager import objDatabaseInterface;

import time;


import os ;
import traceback;

from utils.handleError import handleError;



def getMessagesCurrentlyPendingSend():
    return 

#TODO: dailly, email maintainers, let know how many messages queued have error state, and list the last 5 by date added...
"""


SELECT B.ID, B.message, A.name, A.contactInfo 
FROM 
    Contactors AS A, 
    OutgoingMessageTable AS B  
WHERE 
    B.status = 'pending'  AND
    ( 
        ( (A.notifyAboutGeneralMaintenceAndInfo = 1) AND (B.isGeneralMaintenceAndInfo = 1) ) OR
        ( (A.notifyWhenAdditions = 1) AND (B.isDataAddition = 1)) OR
        ( (A.notifyWhenProblem = 1) AND (B.isProblem = 1)) 
);

SELECT ID, message, status FROM OutgoingMessageTable WHERE isGeneralMaintenceAndInfo = 0 AND isDataAddition = 0 AND isProblem = 0 ;
    change status to error
select the ones labeled "error", summarize them and send...    

handle errors as also something written in the message queue....

"""

