

from utils.contracts import requires, ensures;
import requests;
import gzip;
import re;

from utils.handleError import handleError;
from databaseIOManager import objDatabaseInterface;
import config ; 
import typing;
from typing import List, Dict, Tuple ;

def _parseProposedAddressAndReturnTargetAddresses(proposedAddress : str) -> Dict[str,str]:
    requires(isinstance(proposedAddress,str));
  
    # Note: we're careful to include the $ at the end, otherwise addresses like 
    #     "https://docs.google.com/document/d/1OJvwsoBlDZJfuUFgQv-XQcaNv6EE2S0i0apuCjKZWLYfghfhdfgexport?format=pdf"
    # would pass through, it would just stop before the last "?" in the text (not the "?" in the regex pattern, mind you).
    pattern="^(https://docs.google.com/document/d/[0-9a-zA-z]+[_-][0-9a-zA-Z]+)(/.*)?$"
    matchInfo = re.match(pattern, proposedAddress);
    if(matchInfo is None):
        raise Exception("The provided URL for the Google Sheet does not match the expected format. We " +\
                        f"expected a URL that would match with the regular expression pattern \"{pattern}\", " + \
                        f"for instance \"{pattern}\"");
    assert(len(matchInfo.groups()) == 2);
    assert("".join([x for x in matchInfo.groups() if (x is not None)]) == proposedAddress);
    assert(isinstance(matchInfo.group(1),str));

    # NOTE: one of the reasons we don't just go html is because the images in the 
    # html might not be part of the same file/document which risks them being lost, especially
    # if they're just links to content online as oppossed to files locally. In contrast, the PDFs
    # Google returns seems to have them embedded locally. There were a couple other considerations
    # made after establishing that which lead to the current selection of exports also; the 
    # factor just mentioned, however, moved the considerations a good bit. 
    resultToReturn={};
    for thisKey, thisURLEnd in [ ("pdf", "/export?format=pdf"), \
                                  ("md", "/export?format=md") ]:
        resultToReturn[thisKey] = matchInfo.group(1) + thisURLEnd;

    ensures(isinstance(resultToReturn,dict));
    ensures(all([isinstance(x, str) for x in resultToReturn.keys()]));
    ensures( len(set([x.rpartition("/")[0] for x in resultToReturn])) == 1);
    ensures(all([(re.match("^(https://docs.google.com/document/d/[0-9a-zA-z]+[_-][0-9a-zA-Z]+)/export?format=[a-zA-Z0-9_-]*$", x) is not None) for x in resultToReturn.keys()]));
    return resultToReturn;


def _getData(proposedAddress : str) -> bytes:
    requires(isinstance(proposedAddress,str));

    responceToHTTPRequest=requests.get(proposedAddress);
    responceToHTTPRequest.raise_for_status();
    if(not responceToHTTPRequest.ok):
        # Below should be repetative with the call to raise_for_status above, but
        # we do it just in case, etc
        raise Exception(f"Website indicated error when we attemted to visit {proposedAddress}:" + \
            str({x : eval(x) for x in ["retrievedContent.ok", "retrievedContent.reason", "retrievedContent.status_code"]}) );
    contentOfResponce = responceToHTTPRequest.content;
    assert(isinstance(contentOfResponce,bytes));
    if(len(contentOfResponce) == 0):
        raise Exception(f"The content returned by the website after visiting \"{proposedAddress}\" was empty");
    # TODO: actually limit how much data is read in up-front, possibly taking approaches such as those shown at
    #     https://stackoverflow.com/a/66986706 . As-is, it might hypotetically be possible for someone to specify
    #     an address that loads so much data into memory that the program crashes - I'm not sure if actually
    #     the call to requests would just fail and throw an error that the program would recover gracefully from or
    #     not. For now those, and for most foreseeable practical use in the intended environment, just an issue
    #     seems doubtful.
    if(len(contentOfResponce) > config.defaultValues.maxSizeGoogleSheetFile):
        raise Exception(\
            f"The content returned by the website after visiting \"{proposedAddress}\" was " + \
            f"larger than the maximum allowed content size of {config.defaultValues.maxSizeGoogleSheetFile} bytes. What was " + \
            f"retrieved was {len(contentOfResponce)} bytes (note that we do not rule out the possibility that only some of the content was" + \
            f"retrieved, so this may be an underestimate of the total size of the content that was attempted to be grabbed ). Please " + \
            "get in touch with a system administor for next-steps to handle this case." \
        );
    ensures(isinstance(contentOfResponce, bytes));
    ensures(len(contentOfResponce) > 0);
    ensures(len(contentOfResponce) <= config.defaultValues.maxSizeCommunicationWillReadInBytes);
    return contentOfResponce;


def _sanityCheckMarkdownReceived(markdownTextAsBytes : bytes) -> None:
    requires(isinstance(markdownTextAsBytes,bytes));

    markdownText : str = bytes.decode(markdownTextAsBytes,"UTF8");
    markdownReceivedInLowerCase : str =markdownText.lower();

    # We check that the acrpnyms of the expected flourescenes show up at least once,
    # not being too stringent on the nature of a match (e.g, we have not ruled out substring
    # matches here). TODO: consider (though I sense it probably is a "no" with likely low 
    # likelihood to pay off) storing the values in the database (to an extent they're there
    # for the fileContent types already ) and retieve them for comparison here.
    for thisKey in ["ofp", "bfp", "tagrfp", "gcamp", "mneptune"]:
        if(thisKey not in markdownReceivedInLowerCase):
            raise Exception(\
                f"The content downloaded from the Google Doc link provided did not pass " + \
                f"a sanity check. Specifically, text extracted from the material retrieved " + \
                f"fails to contain any mention of the acronymn of one of our main flourophores, " + \
                f"\"{thisKey}\" (note: this match is not case sensative)." \
            )
    return ;


def _retrieveGoogleSheetMaterialAndSanityCheckIt(proposedAddress : str) -> List[Tuple[str,str,bytes]]:
    requires(isinstance(proposedAddress, str));
    addressesToExamine : typing.Dict[str,str]= _parseProposedAddressAndReturnTargetAddresses(proposedAddress);
    assert(isinstance(addressesToExamine, dict));
    assert("md" in addressesToExamine.keys());

    retrievedMarkdownInBytes : bytes = _getData(addressesToExamine["md"]);
    _sanityCheckMarkdownReceived(retrievedMarkdownInBytes);
    compressedMarkdownRetrieved : bytes = gzip.compress(retrievedMarkdownInBytes);
    assert(isinstance(compressedMarkdownRetrieved, bytes));
    # Really, if the markdown passes the sanity checks above (i.e., that control flow even reaches here),
    #  then the second term in the disjunct should never evaulate to true, but for now we... leave that bit there...
    assert( (len(compressedMarkdownRetrieved) > 0) or (len(retrievedMarkdownInBytes) == 0) );

    retrievedPDFMaterialAsBytes : bytes = _getData(addressesToExamine["pdf"])
    # We could attempt to sanity-check the PDF, but that is a venture further afield than 
    # called for at present, given what is already in place and what is yet to be (ex: automated
    # emails ).
    if( (len(retrievedPDFMaterialAsBytes) == 0 ) and (len(retrievedMarkdownInBytes) > 0)):
        # TODO: consider committing to the database a copy of the markdown content despite this 
        # error - liekly before even retrieving the PDF content. Not yet sure if want both to 
        # fail-out from generating any stored content if only one does, or collect, store and
        # commit what you can and report the other errors for user correction.
        raise Exception("An issue occurred why attempting to retrieve a copy of "+ \
            "a Google Sheet document provided: somehow the PDF fetched is empty, despite the " +\
            "markdown export being non-empty. Check the link - both on the account where you made it" + \
            "and outside your typical webbrowser (maybe a friend's computer without logging in?), and if "+ \
            "that does not expose a correctable issue, please contact the system admins for help.");
    compressedPDFRetrieved : bytes= gzip.compress(retrievedPDFMaterialAsBytes);    
    assert(isinstance(compressedPDFRetrieved,bytes));

    # TODO: ensures
    return [ ("pdf", addressesToExamine["pdf"], compressedPDFRetrieved), \
             ("md" , addressesToExamine["md"] , compressedMarkdownRetrieved) ];

# TODO: 
#     make the database tables (seperate sql script)
#     make the primary function that is called here
#         store the values generated above in the table
#         -----
#         work back in the below error catching:
"""
    try:

    except Exception as e: 
        errorMessage=f"An issue came to light while trying to access the content at \"{proposedAddress}\". " + \
            "While you should see the following error message, be aware that this may be the result of failing to " + \
            "share the content at the address widely enough; if other error, such as a typo in the address, is not the cause " + \
            "we suggest you revisit the permission associated with the Googe Document under the \"share\" menu.\n\nError details:" ;
        handleError(errorMessage);
"""

## file type table
##     ID 
##     name
##     description
##     isCompress
##     compressed format (for now text limited to being either NUll or in the set ('gzip'))
##     ----------
##     .txt
##     .html
##     .md (markdown)
##     .tar
##     .pdf
##     .txt.gzip
##     .pdf.gzip
# Tables to store in:
#    session ID
#    ID of dataset part of 
#    time and data added 
#    name (http address typically)
#    additional notes text
#    > see https://stackoverflow.com/questions/1884787/how-do-i-drop-a-constraint-from-a-sqlite-3-6-21-table/1884893#1884893 for the below, 
#    > which complicates the idea since Sqlite3 is being used here (other databases allow updates to what constraints apply to a table....)
#    fileType text (tempted to make another table for this but thats overkill for now... for now, check for 
#        membership of a set..... eh... might want to make this a named constraint so it can be dropped and replaced later if needed) ####filetype ID
#    ### just have compressed format be null... ### is compressed
#    compressed format if applicable (for now text limited to being either NUll or in the set ('gzip'); ass above 
#        might want to make this a named constraint so it can be dropped and replaced later if needed)
#             In light of Sqlite3's limited ability to adjust constraints (sort of mild abuse of the system like triggering a copy of data that goes to a table with that constraint
#             for the sole purpose of being able to drop that table conveniantly), it is likely best to make another small table  with compression formats listed....
#    content blob



# TODO : make feature / enhancement request on the FLV-Utils to use the database....
#     during loads or updates, or routine scanning, read-in trace file, populate rows of (datasetID, row revision number, neuron ID, trace as a blob),
#     with row revision id being a foreign key to a table with the id and date modified, then neuron ID being  a foreign key to a table of ID number to name etc....


