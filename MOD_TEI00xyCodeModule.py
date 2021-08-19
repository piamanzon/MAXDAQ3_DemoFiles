"""
Author: Trenz Electronic GmbH / Kilian Jahn 27.09.2019 - last edited 06.10.2020
Edited within the Python version:   3.8.3 / 3.7.3

This module is part of the example on using the ADC of the Trenz modules TEI0015,
TEI0016 a/b and TEI023 a/b.
Further explonations are available in the Trenz Electronic wiki.
"""


import serial  # Serial/Comport connection
from scipy.fftpack import fft # FFT 
import numpy as np # FFT window function generating data
from matplotlib import pyplot as plt  # Plotting of Graphs

from datetime import datetime

def getModuleId(comport):
    moduleId = 0 # Default error value
    try:# Timeouts, because this function is a "gate keeper" to the program
        handleComport = serial.Serial(comport, 115200, timeout = 0.5, write_timeout = 0.5)
        handleComport.reset_output_buffer()
        handleComport.reset_input_buffer()
        handleComport.write(bytearray("?", 'utf8'))        
        moduleId = int(handleComport.read())
        handleComport.close()
    except:
        print("Error determine module ID")
    return moduleId
        

def sendCommand(comport, command):
    try:
        handleComport = serial.Serial(comport, 115200)
        handleComport.reset_output_buffer()
        handleComport.write(bytearray(str(command),'utf8'))
        handleComport.close()
    except:
        print("Error send command")
    

# Collect the samples and convert them.
# Return values are: real measured Volts/floats, Normalized to +/- 1/floats
# and as steps in between +/- maximumum integer 
def dataCollect(comport, adcSamples, target, gain):
    # Function variables / Lists for read values
    samples = 16384
    signalVolt = []
    signalFloatNormalized = []
    signalInteger = []
    # Connect to comport, clean buffer and get maximum sampling frequencie of the module
    handleComport = serial.Serial(comport, 115200)
    handleComport.reset_input_buffer()
    handleComport.reset_output_buffer()
    handleComport.write(bytearray("t",'utf8')) # Trigger the adc   
    # Collect the data in chunks of 16 kbyte / 16 k * nibbles
    for i in range(1, adcSamples, 16):
        try:
            handleComport.write(bytearray("*",'utf8')) # Read 16384 adc values 
            if target == 1: # Select the module according to target
                byteList = handleComport.read(5*samples)
                byte = dataConvertTEI0015(byteList, samples, signalVolt, signalFloatNormalized, signalInteger, gain)
            elif target == 2 or target == 3:
                byteList = handleComport.read(4*samples)
                byte = dataConvertTEI0016(byteList, samples, signalVolt, signalFloatNormalized, signalInteger, gain)
            elif target == 4:
                byteList = handleComport.read(5*samples)
                byte = dataConvertTEI0023A(byteList, samples, signalVolt, signalFloatNormalized, signalInteger, gain)
            elif target == 5:
                byteList = handleComport.read(5*samples)
                byte = dataConvertTEI0023B(byteList, samples, signalVolt, signalFloatNormalized, signalInteger, gain)
        except:
            print("ADC data not aquired, stored or processed")
    
    #name = str(datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p"))
    
    #with open(name, 'w') as f:
        # print(signalVolt)
     #   f.write("signalVolt: " + str(signalVolt) + "\n")
      #  f.write("signalFloatNormalized: " + str(signalFloatNormalized) + "\n")
       # f.write("signalInteger: " + str(signalInteger) + "\n")
        #f.close()

    handleComport.close()
    
    return [signalVolt, signalFloatNormalized, signalInteger]
    
    
# Separte binary data into single values and convert them to a voltage, integer and normalized list

# ADC = AD4003BCPZ-RL7 18-bit 2 MSps
def dataConvertTEI0015(byteList, samples, signalVolt, signalFloatNormalized, signalInteger, gain):
    for adcSingleValue in range(0, samples):
        adcSingleValue = ((adcSingleValue)*5) # 5 nibble = 20 > 18 bit
        # ADC resolution is 18bit, positive values reach from 0 to 131071, 
        # negatives values from 131072 to 262142        
        adcIntRaw = int(byteList[adcSingleValue:adcSingleValue+5], 16)
        if adcIntRaw > 131071:
            adcIntRaw = int(adcIntRaw - 262142)
        signalVolt.append(float(adcIntRaw)*(2*4.096*1/0.4)/262142/gain) # (2*Vref*ADCgain) / 2*maxInt        
        signalFloatNormalized.append(adcIntRaw/131071)
        signalInteger.append(adcIntRaw)
        
        
# ADC = ADAQ7988, 16-bit 0.5 MSps
# ADC = ADAQ7980, 16-bit   1 MSps
def dataConvertTEI0016(byteList, samples, signalVolt, signalFloatNormalized, signalInteger, gain):
    for adcSingleValue in range(0, samples):
        adcSingleValue = ((adcSingleValue)*4)
        # ADC resolution  is 16bit, negative full scale is 0, 
        # mid scale is 0x8000 / 32768 and pos full scale is 0xffff / 65536
        adcIntRaw = int(byteList[adcSingleValue:adcSingleValue+4], 16)
        adcIntRaw = int(adcIntRaw - 65536 / 2)
        signalVolt.append(float(-1*(adcIntRaw)*2*4*0.5*5.0/65536/gain)) # (2*Vref*ADCgain) / 2*maxInt
        signalFloatNormalized.append(adcIntRaw / 65536)
        signalInteger.append(adcIntRaw)
        
        
# ADC = ADAQ4003BBCZ 18-bit 2 MSps
def dataConvertTEI0023A(byteList, samples, signalVolt, signalFloatNormalized, signalInteger, gain):
    for adcSingleValue in range(0, samples):
        adcSingleValue = ((adcSingleValue)*5) # 5 nibble = 20 > 18 bit
        # ADC resolution is 18bit, positive values reach from 0 to 131071, 
        # negatives values from 131072 to 262142        
        adcIntRaw = int(byteList[adcSingleValue:adcSingleValue+5], 16)
        if adcIntRaw > 131071:
            adcIntRaw = int(adcIntRaw - 262142)
        signalVolt.append(float(adcIntRaw)*(2*5.0*1/0.45)/262142/gain) # (2*Vref*ADCgain) / 2*maxInt
        signalFloatNormalized.append(adcIntRaw/131071)
        signalInteger.append(adcIntRaw)


# ADC = XYZ 20-bit 1.8 MSps
def dataConvertTEI0023B(byteList, samples, signalVolt, signalFloatNormalized, signalInteger, gain):
    for adcSingleValue in range(0, samples):
        adcSingleValue = ((adcSingleValue)*5) # 5 nibble = 20 > 18 bit
        # ADC resolution is 18bit, positive values reach from 0 to 131071, 
        # negatives values from 131072 to 262142        
        adcIntRaw = int(byteList[adcSingleValue:adcSingleValue+5], 16)
        if adcIntRaw > 524287:  # 2^19 - 1
            adcIntRaw = int(adcIntRaw - 1048574)  # 2^20 - 2
        signalVolt.append(float(adcIntRaw)*(2*5.0*1/0.45)/1048574/gain) # (2*Vref*ADCgain) / 2*maxInt
        signalFloatNormalized.append(adcIntRaw/524287)
        signalInteger.append(adcIntRaw)
        
    
# Generate the FFT and ists Frequencye list
def performeFFTdbFS(samplerate, signal):    
    # Function variables
    frequencies = 0
    sampleLength = 0
    window = 0
    windowed = 0
    fftSignal = 0  
    
    # Generate list of frequencies for the x axis
    sampleLength = int(len(signal)/2+1)
    frequencies = np.linspace(0, samplerate/2, sampleLength, endpoint=True)
    # Generate windowed signal and perform Fourier transformation on it + some math
    window = np.hanning(len(signal))
    fftSignal = np.fft.fft(window*signal)
    # Convert to the usefull spectrum
    fftSignal = 2*np.abs(fftSignal[:sampleLength])/sampleLength
    # Convert to dbFS
    with np.errstate(divide='ignore', invalid='ignore'):
        fftSignal = 20 * np.log10(fftSignal)  
    
    return [frequencies, fftSignal]   

    
# Check if the data exceeds the ADC range too often
def signalLimitsExceed(signal, maxAbsValue):
    exceedCounter = 0    
    for element in signal:
        if abs(element) > maxAbsValue:
            exceedCounter += 1
    return exceedCounter
    
    
    