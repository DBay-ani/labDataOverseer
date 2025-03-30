

from interfaceBaseClasses import InterfaceBaseClass;
import typing;

class interface_dfe6__dc39__sweet_orchestra(InterfaceBaseClass):

    @staticmethod
    def get_human_readable_name():
        return "sweet_orchestra_polite_turbot";

    def process(self, inputVal):
        keyToFunctionMap={"add": self._add, "ls" : self._ls, "get": self._get}
        # see TODO(19e8f005-450a-4790-9ee9-0eead5001b4c).
        # if("request" not in inputVal):
        #     raise Exception("The message does not specify a request type "+\
        #         "(note: comparisons are case sensative and the key to use in order to " + 
        #         "specify your request is, well, \"request\").")
        if(inputVal["request"] not in keyToFunctionMap):
            raise Exception(f"Unrecognized user request type: \"{inputVal["request"]}\"");  
        contentToReturn = keyToFunctionMap[inputVal["request"]](inputVal["request"]);
        return contentToReturn;  

    def checkAndRaiseErrorIfUnknownAdditionalKeys(self, \
        addedDescription: str, valToCheck : typing.Dict[str,typing.Any], allowedKeys : typing.FrozenSet[str]) -> None:
        # see TODO(19e8f005-450a-4790-9ee9-0eead5001b4c).
        keysInTopLevelOfInputVal :typing.FrozenSet[str]=frozenset(valToCheck.keys());
        if(keysInTopLevelOfInputVal != allowedKeys):
            raise Exception("Expected keys not found in the message received. Location in the received message where problem arose: "+addedDescription +\
                "\nExtra keys (fine if empty):"+ str(keysInTopLevelOfInputVal.difference(allowedKeys)) +\
                "\nKeys missing (fine if empty):"+str(allowedKeys.difference(keysInTopLevelOfInputVal)) +\
                "\nNOTE: comparisons ARE case-sensative.");
        return;

    def _add(self, inputVal):
        self.checkAndRaiseErrorIfUnknownAdditionalKeys(\
            "at top-level of the received message's JSON.", inputVal, frozenset(["interface_id","request","content"]));
        contentToRecord=inputVal["content"];
        keysForContentToRead=\
            frozenset(["base_path", "freely_moving", "all_red", "mNeptune", "OFP", "BFP", "google_sheet", "worm_sex", "worm_strain"]);
        self.checkAndRaiseErrorIfUnknownAdditionalKeys(\
            "in the \"content\" dictionary", contentToRecord, keysForContentToRead);        
        for thisKey in keysForContentToRead:
            if(not isinstance(contentToRecord[thisKey],str)):
                raise Exception(f"In the \"content\" dictionary, the value of the key \"{thisKey}\" is not a string."+\
                                " Type found for the value:"+str(type(contentToRecord[thisKey])));
            if(len(contentToRecord[thisKey]) ==0):
                raise Exception(f"In the \"content\" dictionary, the value of the key \"{thisKey}\" is an empty string.");
        if(contentToRecord[thisKey]["worm_sex"] not in {"h","m"}):
            raise Exception("Unknown value specified for \"worm_sex\". "+\
                            "We expect either \"h\" for hermaphrodite or \"m\" for male." + \
                            "Value found:\""+contentToRecord[thisKey]["worm_sex"]+"\"");
    
        raise NotImplementedError();
        #TODO: 
        #     assemble the full file paths
        #     check that the files paths exist and (ideally, but maybe for later) are sufficiently readable
        #         ideally, later, we could do sanity checks to ensure the format is correct as welll...
        #     load the content into the database....
        contentOfReply={"message": "Data added successfully to database. Issue request for `ls` to it listed."}
        return contentOfReply;

    def _ls(self, inputVal):
        # TODO: allow the "content" key to be there so long as the corresponding value is an empty
        # dictionary.
        self.checkAndRaiseErrorIfUnknownAdditionalKeys(\
            "at top-level of the received message's JSON.", inputVal, frozenset(["interface_id","request"]));
        raise NotImplementedError();

    def _get(self, inputVal):
        # TODO: allow the "content" key to be there so long as the corresponding value is an empty
        # dictionary.
        self.checkAndRaiseErrorIfUnknownAdditionalKeys(\
            "at top-level of the received message's JSON.", inputVal, frozenset(["interface_id","request"]));
        raise NotImplementedError();
