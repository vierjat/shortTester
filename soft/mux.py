import time
from machine import Pin
import rp2
import array
from machine import ADC
from machine import Pin, I2C
from time import sleep
from ssd1306 import SSD1306_I2C              # sirve para el I2C del display (hay otra libreria para manejarlo por SPI)
import machine
import framebuf
import sys

nCh = 76;
max_volt = 3.3
max_adc = 65536 #2^16
R1 = 15000
r0 = array.array('f', (0 for _ in range(nCh)))
war=array.array('f',[0])
p1=array.array('i',[0])
p2=array.array('i',[0])


# Define the SIG pins used to select the input channel on the CD74HC4067
SIG_PINS = {
    "A01": [Pin(0, Pin.OUT), Pin(1, Pin.OUT), Pin(2, Pin.OUT), Pin(3, Pin.OUT)],
    "A02": [Pin(4, Pin.OUT), Pin(5, Pin.OUT), Pin(6, Pin.OUT), Pin(7, Pin.OUT)],
    "B01": [Pin(11, Pin.OUT), Pin(10, Pin.OUT), Pin(9, Pin.OUT), Pin(8, Pin.OUT)],
    "B02": [Pin(15, Pin.OUT), Pin(14, Pin.OUT), Pin(13, Pin.OUT), Pin(12, Pin.OUT)]
}

# Define the analog input pin on the microcontroller
ANALOG_PIN = machine.ADC(28)

def show_logo(oled):
    if(oled==0): return
    WIDTH_LOGO  = 115
    HEIGHT_LOGO = 32
    buffer = bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1e@\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1e@\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x7f\xfc\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\xe0>\x00\xf0\x01\xe0x<\x7f\xc3\xfe\x03\xc0\x00\x07\x80\x03\x00p\x01\xe0\xf8|\x7f\xe3\xff\x03\xc0\x00\x0c\x04\x01\xc0\xc0\x03\xf0~|`c\x07\x87\xe0\x00\x0c\x04\x01\xc0\xc0\x03\xf0~|`c\x07\x87\xe0\x00\x0c\x1e\x00\xe0p\x03\xb0x|`a\x81\x87`\x00\x18\x07\x80\xe0\xf0\x03\xb0\xf6L\x7f\xc3\x01\x87`\x00\x18\x03\x800p\x06\x1cv\xcc\x7f\xc3\x81\x8c`\x00\x18\x03\x800p\x06\x1cv\xcc\x7f\xc3\x81\x8c`\x00\x10\x07\x800\xc0\x07\xbcv\xcc`c\x01\x8f8\x00p\x07\xc00p\x07\xfc\xf7\xcc`c\x07\x8f\xf8\x00\x10\x1f\xc00\xf0\x1e.w\x8ca\xe3\x97<\xbc\x00p\x1d\xe00\x7f\xdc\x0eq\x8c\x7f\xc3\xff8\x1c\x00p\x1d\xe00\x7f\xdc\x0eq\x8c\x7f\xc3\xff8\x1c\x00\x18<`0KX\x0c\x91\x08Z\x00\x900\x18\x00\x188` \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x18x~\xe0\x00\x00\x00\x00\x00\x00\x00\x00@\x00\x00\x0c\xe0>\xe0\x80\x01\x92\x00\x08\xc4L\x00@\x00\x00\x0c\xe0>\xe0\x80\x01\x92\x00\x08\xc4L\x00@\x00\x00\x0c\x00\x01\xc0\x08D\x00\x06\x00\x00\x00\x08\x04\x00\x00\x07\x80\x0f\x00\x00\x00@\x80\x00 \x01\x00\x00\x00\x00\x03\xe0>\x003\x02,\x11\x08\xa4P`\x00\x00\x00\x03\xe0>\x003\x02,\x11\x08\xa4P`\x00\x00\x00\x00\x7f\xf0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1f\xa0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
    fb = framebuf.FrameBuffer(buffer, WIDTH_LOGO, HEIGHT_LOGO, framebuf.MONO_HLSB)
    oled.blit(fb, 6, 0)# coordenadas iniciales, centrado --> (x,y) = (6,0)
    oled.show()

def erase_display(oled):
    if(oled==0): return
    oled.fill(0)
    oled.show()
    
def print_params(oled):
    if(oled==0): return
    erase_display(oled)
    line = "Calibration done"
    oled.text(line,1, 0)

    line = "T1:"
    line += "T2:"            
    oled.text(line, 1, 10)
    
    line = "Set:"
    line += " PW:"
    oled.text(line, 1, 20)
    oled.show()

def print_pairs(oled,i):
    if(oled==0): return
    oled.fill(0)
    line = "  Testing " + "{:.0f}".format(i) + "%"
    oled.text(line,2, 0)
    oled.show()

def print_text(oled,t):
    if(oled==0): return
    oled.fill(0)
    line = t
    oled.text(line,0, 10)
    oled.show()

def oversample_adc(adc, num_samples=128):
    """
    Reads the specified pin on the ADC with oversampling to improve accuracy.
    :param pin: The pin number to read on the ADC (0-3).
    :param num_samples: The number of samples to take for each conversion.
    :return: The average of the oversampled ADC readings.
    """
    readings = []
    for i in range(num_samples):
        readings.append(adc.read_u16())
        
    return sum(readings) // num_samples

# Function to read a specific channel on the CD74HC4067
def select_mux_channel(board, channel):
    # Set the SIG pins to the binary representation of the channel number
    for i in range(4):
        SIG_PINS[board][i].value((channel >> i) & 1)    


def route_pins(i,j):
    sa01 = int((i-1)/16)
    sa02 = (16-(i%16))%16
    sb01 = int((j-1)/16)
    sb02 = (16-(j%16))%16
    
    if sa01>3: sa01 = (16-(i%16))%16
    if sb01>3: sb01 = (16-(j%16))%16
    
    select_mux_channel("A01", sa01)
    select_mux_channel("A02", sa02)
    select_mux_channel("B01", sb01)
    select_mux_channel("B02", sb02)


def measure_r(i,j):
    route_pins(i,j)
    time.sleep(0.0001)
    # Read the analog voltage on the selected channel
    adc = oversample_adc(ANALOG_PIN)
    R_mux = r0[i-1]+r0[j-1]
    V_out = max_volt*adc/max_adc
    R2 = V_out * R1 / (max_volt - V_out) - R_mux
    return R2
    
############
### main ###
############
# Inicializa I2C y OLED SSD1306
try:
    i2c = I2C(0, sda=machine.Pin(20), scl=machine.Pin(21), freq=300000)     # I2C 0, sda pin, scl pin, freq (entre 200K y 400K)
    oled = SSD1306_I2C(128, 32, i2c)
except:
    oled = 0
    print("Warning: screen not connected!")
    
show_logo(oled)
time.sleep(3)
#sys.exit(0)

## Calibrate
for c in range(1,nCh+1):
    R2 = measure_r(c,c)
    r0[c-1]=R2/2.
    #print(c,"\t R0:", R2)
print("\nCalibration completed!\n")

# Dimensiones del Display y Logo
WIDTH       = 128
HEIGHT      = 32

print_text(oled, "Calibration done")
time.sleep(1)

total_checks = nCh*(nCh-1)/2
a = 0
for c in range(1,nCh+1):
    for p in range(c+1,nCh+1):
        a=a+1
        if a%28==0: print_pairs(oled,(a+1)*100/total_checks)
        R2 = measure_r(c,p)
        if R2<2e6 :
            war.append(R2)
            p1.append(c)
            p2.append(p)
            #print(c,"-",p,"\t R0:", R2)

print_pairs(oled,100)
if(len(war)==1):
    print_text(oled,"   ALL OK! :)")
else:
    t="Shorts found :("
    print_text(oled,t)
    for i in range(1,len(war)):
        print(p1[i], "-", p2[i],"R: ", war[i], "Ohm")

print("\t DONE!\n")
    
    
    