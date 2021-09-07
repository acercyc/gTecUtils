# %%
import mne
import h5py
import numpy as np
import xml.etree.ElementTree as ET
import pandas as pd
from lxml import etree

# %%
fn = "Z:\RecordSession_2021.08.27_17.36.03.hdf5"
f = h5py.File(fn, 'r')

#%%
dd = f.get('RawData/Samples')
np.array(dd).shape


#%%
f.get('RawData/AcquisitionTaskDescription')

# %%
class gTecDataset:
    def __init__(self, filename):
        self.filename = filename
        self.hdf5 = h5py.File(filename, 'r')
        self.info = self.parser()
        self.data = self.info['RawData/Samples']

    def printDataStructure(self):
        def ps(name, obj):
            print('{}\n    {}'.format(name, obj))
        self.hdf5.visititems(ps)

    def printDataStructure2(self):
        def ps(name, obj):
            print('{}\n    {}'.format(name, type(obj)))
        self.hdf5.visititems(ps)
    
    def parser(self):
        dataDict = {}
        def inner(name, obj):
            if type(obj) is h5py.Dataset:
                print('{}\n    {}'.format(name, obj))
                            
                if 'S' in str(obj.dtype):
                    if 'xml' in str(obj[0][:20]):
                        xmlObj = etree.fromstring(obj[0])
                        dataDict[name] = xmlParser(xmlObj)
                    else:
                        dataDict[name] = obj
                else:
                    dataDict[name] = np.array(obj)

                
        self.hdf5.visititems(inner)
        return dataDict
            
            

# g = gTecDataset(fn)
# g.printDataStructure()
# g.printDataStructure2()
# g.parser()
# g.info['RawData/AcquisitionTaskDescription']
#%% 

def xmlParser(xmlObj):
    xmlDict = {}

    def xmlParser_inner(xmlObj):
        # list children
        if len(xmlObj) > 0:
            childrenTag = [c.tag for c in xmlObj]

            print(childrenTag)

            if len(set(childrenTag)) > 1:
                # if different children
                for child in xmlObj:
                    xmlParser_inner(child)
            else:
                # if same children
                df = pd.read_xml(etree.tostring(xmlObj))
                xmlDict[xmlObj.tag] = df
                # print(df)

        else:
            # if no children
            # xmlDict.update({xmlObj.tag: xmlObj.text})
            xmlDict[xmlObj.tag] = xmlObj.text
            print(xmlObj.tag)
            print(xmlObj.text)

        return xmlDict

    xmlParser_inner(xmlObj)
    return xmlDict

