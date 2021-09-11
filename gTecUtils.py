# %%
import mne
import h5py
import numpy as np
import pandas as pd
from lxml import etree
import xml.etree.ElementTree as ET


class gTecDataset:
    def __init__(self, filename):
        self.filename = filename
        self.hdf5 = h5py.File(filename, 'r')
        self.info = self.parser()
        self.data = self.info['RawData/Samples'].T * 1e-6  # to uV

        if 'RawData/AcquisitionTaskDescription/ChannelProperties' in self.info:
            self.ch_names = list(
                self.info['RawData/AcquisitionTaskDescription/ChannelProperties']['ChannelName'])
            self.ch_types = list(
                self.info['RawData/AcquisitionTaskDescription/ChannelProperties']['ChannelType'])
            if type(self.ch_types[0]) is not str:
                self.loadChanInfo_standard()
        else:
            self.loadChanInfo_standard()

        # self.ch_types = ['eeg' for x in range(32)]
        if 'RawData/AcquisitionTaskDescription/SamplingFrequency' in self.info:
            self.sfreq = int(
                self.info['RawData/AcquisitionTaskDescription/SamplingFrequency'])
        else:
            v = getValueFromXML(
                self.hdf5['RawData']['AcquisitionTaskDescription'][0], 'SamplingFrequency')
            self.sfreq = int(v)

    def parser(self):
        """ Parse g.tec hdr5 format using h5py and lxml """
        dataDict = {}

        def inner(name, obj):
            if type(obj) is h5py.Dataset:
                if 'S' in str(obj.dtype):
                    if 'xml' in str(obj[0][:20]):
                        try:
                            # raise Exception('xml error')
                            xmlObj = etree.fromstring(obj[0])
                            for key, value in xmlParser(xmlObj).items():
                                dataDict[name + '/' + key] = value
                        except Exception as ex:
                            print(
                                'warning: can not parse xml. Replace xml field to None.')
                            print(ex)
                            dataDict[name] = None
                    else:
                        dataDict[name] = str(obj[0], "utf-8")
                else:
                    dataDict[name] = np.array(obj)

        self.hdf5.visititems(inner)
        return dataDict

    def loadChanInfo(self, fn=None):
        if fn is None:
            fn = './settings/montage_EEGonly_32ch.xml'
            chanInfo = montageParser(fn)

    def loadChanInfo_standard(self, ch_names=True, ch_types=True):
        if ch_names:
            self.ch_names = ['FP1', 'FP2', 'AF3', 'AF4', 'F7', 'F3', 'Fz', 'F4',
                             'F8', 'FC5', 'FC1', 'FC2', 'FC6', 'T7', 'C3', 'Cz',
                             'C4', 'T8', 'CP5', 'CP1', 'CP2', 'CP6', 'P7', 'P3',
                             'Pz', 'P4', 'P8', 'PO7', 'PO3', 'PO4', 'PO8', 'Oz']
        if ch_types:
            self.ch_types = ['eeg' for x in range(32)]

    def toMNE(self):
        ''' Convert data into MNE RawArray format'''
        info = mne.create_info(self.ch_names[:32], self.sfreq, self.ch_types[:32])
        return mne.io.RawArray(self.data[:32, :], info)

    # def __del__(self):
    #     self.hdf5.close()


def xmlParser(xmlObj):
    """Parse xml string using lxml. Convert content into string or pandas DataFrame"""
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
            # if no child
            xmlDict[xmlObj.tag] = xmlObj.text

        return xmlDict

    xmlParser_inner(xmlObj)
    return xmlDict


def getValueFromXML(xmlStr, tag):
    root = ET.fromstring(xmlStr)
    return root.find(tag).text


def montageParser(filename):
    """Parse montage xml file created from g.tec MontageCreator"""
    tree = etree.parse(filename)
    root = tree.getroot()

    d = dict()
    for c in root:
        v = c.text
        if type(v) is str:
            v = v.split(',')
            if len(v) > 1:
                if np.char.isnumeric(v[0]):
                    v = np.fromiter(v, dtype=np.float64)
            else:
                v = v[0]
        elif type(v) is type(None):
            v = 'None'
        else:
            raise ValueError("can't recognize type")

        print(v)
        d[c.tag] = v

    return d
