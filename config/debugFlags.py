# Fanoos: Multi-Resolution, Multi-Strength, Interactive Explanations for Learned Systems ; David Bayani and Stefan Mitsch ; paper at https://arxiv.org/abs/2006.12453
# Copyright (C) 2021  David Bayani
# 
# This file is part of Fanoos.
# 
# Fanoos is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License only.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# 
# Contact Information:
# 
# Electronic Mail:
#   dcbayani@alumni.cmu.edu
# 
# Paper Mail:
#   David Bayani
#   Computer Science Department
#   Carnegie Mellon University
#   5000 Forbes Ave.
#   Pittsburgh, PA 15213
#   USA
# 
# 


v_print=0; # stands for verbrosity of printing.
    # v_print=0 - print nothing.
    # v_print > 0  - print various debug information.

assert(isinstance(v_print, int));
assert(v_print >= 0);

# If <fileName> is not listed below, then get_v_print_ForThisFile(<fileName>)
# returns the default verbrosity level, v_print . If <fileName> is in the
# below dictionary, then get_v_print_ForThisFile(<fileName>) returns 
# dictMappingFileToDebugLevel[<fileName>] as the verbrosity level.
# Note that this framework could easily be extended to have matches use
# regular expressions as oppossed to strict matches in a dictionary.
# For now, however, this first our purposes.
#
# Currently, we list some examples in the below dictionary for illustration
# purposes.
dictMappingFileToDebugLevel = {\
    "fanoos.py" : 2, \
    "domainsAndConditions/classesDefiningQuestions.py" : 1, \
    "CEGARLikeAnalysis/CEGARLikeAnalysisMain.py" : 1, \
    "utils/distributionStatics.py" : 2 \
};



def get_v_print_ForThisFile(filePath):
    pathToThisConfigFile = __file__;
    relativePathToThisConfigFile = "config/debugFlags.py";
    assert(pathToThisConfigFile.endswith(relativePathToThisConfigFile));
    directoryStartPath = pathToThisConfigFile[:-len(relativePathToThisConfigFile)];
    relativeFilePath = filePath;
    if(filePath.startswith(directoryStartPath)):
        relativeFilePath = filePath[len(directoryStartPath):];
    return dictMappingFileToDebugLevel.get(relativeFilePath, v_print);


