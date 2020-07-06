from nptdms import TdmsFile as tdms
import numpy as np

try:
    from tkinter import Tk
    from tkFileDialog import askopenfilenames
except:
    from tkinter import Tk
    from tkinter import filedialog

class Data:

    def __init__(self):
        self.prop = {}





    def load_sdata(self, del_data = True, skip_cal = False):
        if (del_data == True):
            self.delete_data()

        self.prop['fns'] = filedialog.askopenfilenames(filetypes=[("TDMS","*.tdms")], title = 'open s-polarized excitation data')
        self.prop['Nf'] = len(self.prop['fns'])

        self.prop['PxCols'] = list(tdms(self.prop['fns'][0]).properties.items())[11][1]
        self.prop['PxRows'] = list(tdms(self.prop['fns'][0]).properties.items())[12][1]

        self.sIs = np.zeros((self.prop['PxCols'], self.prop['PxRows'], self.prop['Nf']))
        self.sIp = np.zeros((self.prop['PxCols'], self.prop['PxRows'], self.prop['Nf']))

        for i in range(self.prop['Nf']):
            sDat = tdms.read(self.prop['fns'][i]).groups()[0].channels()[1].data #channel 2 is PBS reflection path -> s-polarized light
            pDat = tdms.read(self.prop['fns'][i]).groups()[0].channels()[2].data #channel 3 is PBS transmission path -> p-polarized light

            for j in range(self.prop['PxCols']):
                self.sIs[j,:,i] = sDat[(j*self.prop['PxRows']):((j+1)*self.prop['PxRows'])]
                self.sIp[j,:,i] = pDat[(j*self.prop['PxRows']):((j+1)*self.prop['PxRows'])]

        print(np.mean(self.sIp))
        print(np.mean(self.sIs))

        # beware of doulbe processing when using calibrate function
        if (skip_cal == False):
            self.axelrod()
            self.s_sensitivity(missing = False)

    def load_pdata(self, del_data = True, skip_cal = False):
        if (del_data == True):
            self.delete_data()

        self.prop['fns'] = filedialog.askopenfilenames(filetypes=[("TDMS","*.tdms")], title = 'open p-polarized excitation data')
        self.prop['Nf'] = len(self.prop['fns'])

        self.prop['PxCols'] = list(tdms(self.prop['fns'][0]).properties.items())[11][1]
        self.prop['PxRows'] = list(tdms(self.prop['fns'][0]).properties.items())[12][1]

        self.pIs = np.zeros((self.prop['PxCols'], self.prop['PxRows'], self.prop['Nf']))
        self.pIp = np.zeros((self.prop['PxCols'], self.prop['PxRows'], self.prop['Nf']))

        for i in range(self.prop['Nf']):
            sDat = tdms.read(self.prop['fns'][i]).groups()[0].channels()[1].data #channel 2 is PBS reflection path -> s-polarized light
            pDat = tdms.read(self.prop['fns'][i]).groups()[0].channels()[2].data #channel 3 is PBS transmission path -> p-polarized light

            for j in range(self.prop['PxCols']):
                self.pIs[j,:,i] = sDat[(j*self.prop['PxRows']):((j+1)*self.prop['PxRows'])]
                self.pIp[j,:,i] = pDat[(j*self.prop['PxRows']):((j+1)*self.prop['PxRows'])]
        print(np.mean(self.pIp))
        print(np.mean(self.pIs))


        # beware of doulbe processing when using calibrate function
        if (skip_cal == False):
            self.axelrod()
            self.s_sensitivity(missing = False)

    def calibrate(self):
        self.delete_data()
        self.load_sdata(del_data = True, skip_cal = True)
        self.load_pdata(del_data = False, skip_cal = True)

        self.axelrod()
        self.s_sensitivity(missing = True)


        #look into axelrod sper and pper: matlab code sper and sper2 are similar, pper and pper2 not (pper2 similar with pIs)
        #self.s_sensitivity()

        #AXELROD CORRECTION FOR HIGH-NA DEPOLARIZATION,



    def test(self):
        sigma = np.arcsin(1.27/1.33)
        c1 = (2-3*np.cos(sigma)+np.cos(sigma)**3)/(6*(1-np.cos(sigma)))
        c2 = (1-3*np.cos(sigma)+3*np.cos(sigma)**2-np.cos(sigma)**3)/(24*(1-np.cos(sigma)))
        c3 = (5-3*np.cos(sigma)-np.cos(sigma)**2-np.cos(sigma)**3)/(8*(1-np.cos(sigma)))

        temp_par = ((c1+c3)*self.pIp-(c1+c2)*self.pIs)/(c3*(c1+c3)-c2*(c1+c2))
        temp_per = (c2*self.pIp-c3*self.pIs)/(c2*(c1+c3)-c3*(c1+c3))
        self.pIp = temp_par
        self.pIs = temp_per

        temp_par = ((c1+c3)*self.sIs-(c1+c2)*self.sIp)/(c3*(c1+c3)-c2*(c1+c2))
        temp_per = (c2*self.sIs-c3*self.sIp)/(c2*(c1+c3)-c3*(c1+c3))
        self.sIs = temp_par
        self.sIp = temp_per

        #SENSITIVITY CORRECTION FOR S-DETECTION PATH
        self.f_s = np.sqrt((np.mean(self.sIp)*np.mean(self.pIp))/(np.mean(self.sIs)*np.mean(self.pIs)))
        self.sIs = self.sIs*self.f_s
        self.pIs = self.pIs*self.f_s

    def delete_data(self):
        if hasattr(self, 'sIs'):
            del self.sIs
        if hasattr(self, 'sIp'):
            del self.sIp

        if hasattr(self, 'pIs'):
            del self.pIs
        if hasattr(self, 'pIp'):
            del self.pIp

    def axelrod(self):
        sigma = np.arcsin(1.27/1.33)
        c1 = (2-3*np.cos(sigma)+np.cos(sigma)**3)/(6*(1-np.cos(sigma)))
        c2 = (1-3*np.cos(sigma)+3*np.cos(sigma)**2-np.cos(sigma)**3)/(24*(1-np.cos(sigma)))
        c3 = (5-3*np.cos(sigma)-np.cos(sigma)**2-np.cos(sigma)**3)/(8*(1-np.cos(sigma)))

        if ((hasattr(self, 'pIp')==True) & (hasattr(self, 'pIs')==True)):
            temp_par = ((c1+c3)*self.pIp-(c1+c2)*self.pIs)/(c3*(c1+c3)-c2*(c1+c2))
            temp_per = (c2*self.pIp-c3*self.pIs)/(c2*(c1+c3)-c3*(c1+c3))
            self.pIp = temp_par
            self.pIs = temp_per
        if ((hasattr(self, 'sIp')==True) & (hasattr(self, 'sIs')==True)):
            temp_par = ((c1+c3)*self.sIs-(c1+c2)*self.sIp)/(c3*(c1+c3)-c2*(c1+c2))
            temp_per = (c2*self.sIs-c3*self.sIp)/(c2*(c1+c3)-c3*(c1+c3))
            self.sIs = temp_par
            self.sIp = temp_per
        #add case where detection data is not loaded yet

    def s_sensitivity(self, missing = False):
        if ((hasattr(self, 'sIs') == False) & (hasattr(self, 'pIs') == False)):
            print('Error: no data loaded')
            return

        if missing == True:
            self.f_s = np.sqrt((np.mean(self.sIp)*np.mean(self.pIp))/(np.mean(self.sIs)*np.mean(self.pIs)))

        if (hasattr(self, 'f_s') == False):
            print('Warning, data not properly calibrated, s-detection sensitivity factor missing')
            return

        if hasattr(self, 'sIs'):
            self.sIs = self.sIs*self.f_s
        if hasattr(self, 'pIs'):
            self.pIs = self.pIs*self.f_s

    def load_mdata(self, fns):
        mdata = {}
        for i in range(self.prop['Nf']):
            temp = tdms.read_metadata(self.prop['fns'][i])
            mdata[i] = temp.groups()[0]
            return mdata
