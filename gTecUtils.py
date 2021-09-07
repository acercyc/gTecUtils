# %%
import mne
import h5py
import numpy as np
import xml.etree.ElementTree as ET
import pandas as pd
from lxml import etree


# %%
class gTecDataset:
    def __init__(self, filename):
        self.filename = filename
        self.hdf5 = h5py.File(filename, 'r')
        self.info = self.parser()
        self.data = self.info['RawData/Samples'].T
        self.ch_names = list(
            self.info['RawData/AcquisitionTaskDescription']['ChannelProperties']['ChannelName'])
        # self.ch_types = list(self.info['RawData/AcquisitionTaskDescription']['ChannelProperties']['ChannelType'])
        self.ch_types = ['eeg' for x in range(32)]
        self.sfreq = self.info['RawData/AcquisitionTaskDescription']['SamplingFrequency']

    def parser(self):
        dataDict = {}

        def inner(name, obj):
            if type(obj) is h5py.Dataset:

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

    def toMNE(self):
        info = mne.create_info(self.ch_names, self.sfreq, self.ch_types)
        return mne.io.RawArray(self.data, info)


def xmlParser(xmlObj):
    xmlDict = {}

    def xmlParser_inner(xmlObj):
        # list children
        if len(xmlObj) > 0:
            childrenTag = [c.tag for c in xmlObj]

            if len(set(childrenTag)) > 1:
                # if different children
                for child in xmlObj:
                    xmlParser_inner(child)
            else:
                # if same children
                df = pd.read_xml(etree.tostring(xmlObj))
                xmlDict[xmlObj.tag] = df

        else:
            # if no children
            # xmlDict.update({xmlObj.tag: xmlObj.text})
            xmlDict[xmlObj.tag] = xmlObj.text

        return xmlDict

    xmlParser_inner(xmlObj)
    return xmlDict


if __name__ == "__main__":
    pass

# %%
