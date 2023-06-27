#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  7 11:03:15 2023

@author: ianlinux
"""

#es necsario descargar estas liberias para DSP
# Run these lines of code if this is your first time using this Jupyter Notebook
#! pip install scikit-dsp-comm
#! pip install scikit-commpy
#este codigo es muy importante
import adi
Uri = "ip:192.168.1.31"
sdr = adi.Pluto(Uri)
import numpy as np
import matplotlib.pyplot as plt
#from commpy.filters import rrcosfilter
#from sk_dsp_comm import digitalcom as dc
#import scipy.signal as signal

def complexExp(N,Fc,Fs):
    # N : Number of samples to transmit at once
    # Fc: Carrier frequency in Hz
    # Fs: Sampling frequency in Hz
    if Fs < 2*Fc:
        raise ValueError(
            "Error: Fs must be at least 2 time Fc"
        )
    Tsamp  = 1/Fs;
    n      = np.arange(N)
    signal = 1.0*np.exp(1j*2.0*np.pi*Fc*n*Tsamp) 
    return signal

nSamples     = 2**12
samplingRate = 16.0e6
frec         = samplingRate/16
txSignal     = complexExp(nSamples,frec,samplingRate)

def plotSignal(signal):
#------------------------------- Transmitted I component ------------------------------- 
# Plot time domain
    plt.figure(figsize=(20,8), dpi= 80, facecolor='w', edgecolor='k')
    plt.subplot(2,1,1)
    plt.plot(np.real(signal))
    plt.xlabel('n')
    plt.ylabel('Amplitud')
    plt.title('Componente en fase de la señal')
    plt.grid()
#------------------------------- Transmitted Q component -------------------------------
# Plot time domain
    plt.subplot(2,1,2)
    plt.plot(np.imag(signal))
    plt.xlabel('n')
    plt.ylabel('Amplitud')
    plt.title('Componente en cuadratura de la señal')
    plt.grid()
    plt.show()
    #la grafica de espectro de potencia se puede relizar a partir de este codigo
    
    
    def plotSpect(signal,samplingRate):
    plt.subplots(figsize=(15, 3))
    plt.grid()
    plt.title("Power Spectral Density")
    plt.psd(signal, len(signal), samplingRate, color='C1')
    plt.show()
    plotSpect(txSignal,samplingRate)
        ##################################
   #la segunda es una señal implemetada en QPSK
    #Create transmit waveform (QPSK, 16 samples per symbol)
num_symbols = 2048
x_int = np.random.randint(0, 4, num_symbols) # 0 to 3
x_degrees = x_int*360/4.0 + 45 # 45, 135, 225, 315 degrees
x_radians = x_degrees*np.pi/180.0 # sin() and cos() takes in radians
x_symbols = np.cos(x_radians) + 1j*np.sin(x_radians) # this produces our QPSK complex symbols
samples = np.repeat(x_symbols, 16) # 16 samples per symbol (rectangular pulses)
    
    plotSignal(samples[1:400])
    #la segunda es una señal implemetada en QPSK
    
    plotSpect(samples,samplingRate)
    
    
    plt.figure(figsize=(3,3))
plt.plot(np.real(x_symbols[0:num_symbols]),np.imag(x_symbols[0:num_symbols]),'b*')
plt.grid()
plt.show()

#########################################
##PARAMETROS DE CONFIGURACON DEL SDR

#------------------------------- SDR Parameter Configuration -------------------------------

Uri              = Uri
Loopback         = 0             # 0=Disabled, 1=Digital, 2=RF
SamplingRate     = samplingRate  # Sample rate RX and TX paths[Samples/Sec]

TxLOFreq         = 910e6         # Carrier frequency of TX path [Hz]
TxAtten          = -40           # Attenuation applied to TX path, valid range is -89 to 0 dB [dB]
TxRfBw           = 16.0e6         # Bandwidth of front-end analog filter of TX path [Hz]

RxLOFreq         = TxLOFreq      # Carrier frequency of RX path [Hz]
GainControlModes = "slow_attack" # Receive path AGC Options: slow_attack, fast_attack, manual
RxHardwareGain   = 70             # Gain applied to RX path. Only applicable when gain_control_mode is set to 'manual'    
RxRfBw           = TxRfBw        # Bandwidth of front-end analog filter of RX path [Hz] 
RxBufferSize     = 2**20-1

#LAZO DE rETORNO
"""
0 DESACTIVADO
1 REALIMENTACION DE LA SEÑAL DIGITAL
2 RELIMENTACION DE LA SEÑAL DE RF ACUA COMO REPETIDO DE RX

"""
#FRECUENCIA DE MUESTREO
"""
RANGO DE FRECUENCIA DE MUESTREO
520.833 KSPS A 61.44MSPS
"""
sdr.sample_rate = sdr_user_1  # Sample rate RX and TX paths[Samples/Sec]

"""
RANGO ANCHO BANDA BW 200KHZ A 20MHZ

"""
 sdr.tx_rf_bandwidth = int(TxRfBw)  # Bandwidth of front-end analog filter of TX path [Hz]
sdr.rx_rf_bandwidth = int(RxRfBw)  # Bandwidth of front-end analog filter of RX path [Hz] 

"""
gANANCIA DEL HARDWARE
"""

dr.tx_hardwaregain_chan0   = TxAtten # Attenuation applied to TX path, valid range is -90 to 0 dB [dB]
sdr.rx_hardwaregain_chan0   = RxHardwareGain   # Gain applied to RX path. Only applicable when gain_control_mode is set to 'manual'
sdr.gain_control_mode_chan0 = GainControlModes # Receive path AGC Options: slow_attack, fast_attack, manual

"""
RANGO DE LOS OSCILADORES D RF EN EL TRANSMISOR
Y RECEPTOR
"""
Sdr.tx_lo = int(TxLOFreq)# Carrier frequency of TX path [Hz]
sdr.rx_lo = int(RxLOFreq) # Carrier frequency of RX path [Hz]

#BUFFER
sdr.tx_cyclic_buffer = True
sdr.rx_cyclic_buffer = False

##EJEMPLO TRANSMITIENDO Y RECIBIENDO
sdr.tx(txSignal*2**14) # The PlutoSDR expects samples to be between -2^14 and +2^14, not -1 and +1 like some SDRs
rxSignal = sdr.rx()/2**14

#SEÑAL RECIBIDA
plotSignal(rxSignal[1:200])

#ESPECTRO DE LA SEÑAL RECIBIDA
plotSpect(rxSignal,samplingRate)


#DELETE LA MEMORIA CLEAR
# Since it is not possible to turn off Tx, it is configured to transmit at low power and on a different frequency than Rx.
sdr.tx_destroy_buffer()
sdr.tx_hardwaregain_chan0 = -89 
sdr.tx_lo                 = int(2400e6)
sdr.rx_lo                 = int(950e6)
sdr.tx(np.zeros(2048))
# Destroy radio object
del(sdr)
