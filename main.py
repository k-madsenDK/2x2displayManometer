
''' Display Testing Demo '''

from machine import Pin, SPI , I2C
import machine
import random
import time
import st7789 #library of TFT display controller uses SPI interface
import vga1_bold_16x32 as font
import vga1_8x16 as font1
from time import sleep
import bme280 
import sys
import _thread
import network
import socket
import networds
import gc
import os
import ntptime
from time import gmtime
from ds3231 import DS3231

#from machine import WDT
#from picozero import pico_temp_sensor, pico_led

CT = bytearray(b'\x00\x16\x13\x01\x25\x08\x24') #00:00:10 friday 03/03/2022 

address = 0x68
register = 0x00
sidsteBarometerStand = 0
Justeringstal = 7 # justere hpa til korrekt værdi

ssid = networds.ssid
password = networds.password

sidstetempmaalt = 255
sidsteTekstvalg = 255
sidstemånedsvalg = 255
opdaterdisplay = 255
sidstetemp = 0.0
sidstehumid = 0.0
sidstepress = 0.0
sidstedato = CT
timeseterror = True
getnewTime = False

i2c = I2C(0,scl=Pin(21), sda=Pin(20), freq=40000)#all sensor connected through I2C
bme = bme280.BME280(i2c=i2c) 
ds = DS3231(i2c)

gc.enable()#enable auto mem clean

#define and configure display SPI interface
spi0 = SPI(0, baudrate=40000000, sck=Pin(18), mosi=Pin(19))
spi1 = SPI(1, baudrate=40000000, sck=Pin(10), mosi=Pin(11))
spi2 = SPI(0, baudrate=40000000, sck=Pin(2), mosi=Pin(3))
spi3 = SPI(0, baudrate=40000000, sck=Pin(6), mosi=Pin(7))

# Define TFT displays with different CS pins
tft0 = st7789.ST7789(spi0, 240, 240, cs=Pin(28, Pin.OUT), dc=Pin(16, Pin.OUT), backlight=Pin(14, Pin.OUT), rotation=145)
tft1 = st7789.ST7789(spi1, 240, 240, cs=Pin(13, Pin.OUT), dc=Pin(12, Pin.OUT), backlight=Pin(14, Pin.OUT), rotation=145)
tft2 = st7789.ST7789(spi2, 240, 240, cs=Pin(5, Pin.OUT), dc=Pin(4, Pin.OUT), backlight=Pin(14, Pin.OUT), rotation=145)
tft3 = st7789.ST7789(spi3, 240, 240, cs=Pin(9, Pin.OUT), dc=Pin(8, Pin.OUT), backlight=Pin(14, Pin.OUT), rotation=145)

#initialize tft display
tft0.init()
tft1.init()
tft2.init()
tft3.init()

def datoTilStreng(data):
    t = time.time()
    text = time.gmtime(t)
    sidstedato = text
    year = text[0]-2000 # Can be yyyy or yy format
    month = text[1]
    mday = text[2]
    hour = text[3] # 24 hour format only
    minute = text[4]
    second = text[5] # Optional
    
    streng = "20%d/%02d/%02d %02d:%02d:%02d " %(year,month,mday,hour,minute,second)
    return(streng)
def hentDS3231Clock():
    tm = ds.datetime()
    machine.RTC().datetime((tm[0], tm[1], tm[2], tm[3] , tm[4], tm[5], tm[6], 0))
    
def hentinternettid():
    ntptime.settime()
    t = ntptime.time()
    text = time.gmtime(t)
    if(text[3] < 22):
        year = text[0]-2000 # Can be yyyy or yy format
        month = text[1]
        mday = text[2]
        hour = text[3]+2 # 24 hour format only
        minute = text[4]
        second = text[5] # Optional
        weekday = text[6]+1 # Optional
        datetime = (year, month, mday, hour, minute, second, weekday)
        timeseterror = False
        ds.datetime(datetime)
    else:
        timeseterror = True;
        

def clear_text(tft, x, y, width, height):
  """Clears a rectangular area on the TFT display."""
  tft.fill(bg, x, y, width, height)

def clock(sidstemånedsvalg):
    global sidstedato
    

    #print(data)
    t = time.time()
    text = time.gmtime(t)
    sidstedato = text
    year = text[0]-2000 # Can be yyyy or yy format
    month = text[1]
    mday = text[2]
    hour = text[3] # 24 hour format only
    minute = text[4]
    second = text[5] # Optional
    weekday = text[6]+1 # Optional
        
    if sidstemånedsvalg != month:
        sidstemånedsvalg = month
        filnavn = 'img/%x240.jpg'%(month-1)
        print("filnavn "+ filnavn)
        tft3.jpg(filnavn,0,0,st7789.FAST)
    #dt = "20%x/%02x/%02x %02x:%02x:%02x %s" %(g,f,e,c,b,a,week[d-1])
    t = "%02d:%02d:%02d" %(hour,minute,second)
    dt = "%02d/%02d/20%d"%(mday,month,year)
    dw = weekday
    if dw == 7:
        dagtext = " Soendag "
    elif dw == 1:
        dagtext = " Mandag  "
    elif dw == 2:
        dagtext = " Tirsdag "
    elif dw ==3:
        dagtext = " Onsdag  "
    elif dw == 4:
        dagtext = " Torsdag "
    elif dw == 5:
        dagtext = " Fredag  "
    else:
        dagtext = " Loerdag "
        
    tft3.text(font,dagtext, 50, 0, st7789.BLACK, st7789.WHITE)  
    tft3.text(font," "+ t + " ", 40, 160, st7789.BLACK, st7789.WHITE)
    tft3.text(font, " "+ dt + " ", 25, 200, st7789.BLACK, st7789.WHITE)
    #print(t+" "+ds) #year,month,day,hour,min,sec,week
    #print(d)
    #tft1.text(font,d, 40,60,st7789.YELLOW)
    #tft1.fill_rect(0, 100, 240,8, st7789.RED)
    
    #time.sleep(1)
    return(sidstemånedsvalg)

# clear display
tft0.fill(0)
tft1.fill(0)
tft2.fill(0)
tft3.fill(0)

# fill color 
tft0.jpg("img/temp240.jpg",0,0,st7789.SLOW)
#tft0.fill(st7789.WHITE)
tft1.jpg("img/fugtighed240.jpg",0,0,st7789.SLOW)
#tft1.fill(st7789.WHITE)
#tft2.fill(st7789.WHITE)


def clear_text(tft, x, y, width, height):
  """Clears a rectangular area on the TFT display."""
  tft.fill(st7789.WHITE, x, y, width, height)

def rettemperatur(temp):
    temp = temp.replace("C"," ",1)  # Remove the "C" from the temperature string
    vaerdi = float(temp) - 4.0  # Subtract 4.0 from the temperature value
    temp = '%.1fC' % vaerdi  # Format the adjusted value back to a string with "C"
    return temp

def retluftfugtighed(humid):
    humid = humid.replace("%"," ",1)  # Remove the "%" from the humidity string
    vaerdi = float(humid)  # Convert the value to a float
    vaerdi = vaerdi + ((50.0 / 15.0)*4.0)  # Adjust the value based on a 50% change for a 15°C increase
    humid = '%.1f%%' % vaerdi  # Format the adjusted value back to a string with "%"
    return humid

def vishpatryk(tryk,sidsteTekstvalg ):
    vaerdi = int(float(tryk))  #dmi  incl højde kompenserin 18m = 2.25hpa
     
    
    if vaerdi < 950 :
        Tekstvalg = 0
    elif vaerdi < 983:
        Tekstvalg = 1
    elif vaerdi < 1018:
        Tekstvalg = 2
    elif vaerdi < 1050:
        Tekstvalg = 3
    else :
        Tekstvalg = 4
        
    if sidsteTekstvalg  != Tekstvalg:
        sidsteTekstvalg = Tekstvalg
        if Tekstvalg == 0:
                tft2.jpg("img/thunder240.jpg",0,0,st7789.SLOW)
                tft2.text(font, " STORM ", 80, 200, st7789.BLACK, st7789.WHITE)
        elif Tekstvalg == 1:
                tft2.jpg("img/regn240.jpg",0,0,st7789.SLOW)
                tft2.text(font, " REGN ", 83, 200, st7789.BLACK, st7789.WHITE)
        elif Tekstvalg == 2:
                tft2.jpg("img/skyer240.jpg",0,0,st7789.SLOW)
                tft2.text(font, " USTADIGT ", 40, 200, st7789.BLACK, st7789.WHITE)
        elif Tekstvalg == 3:
                tft2.jpg("img/letteskyer240.jpg",0,0,st7789.SLOW)
                tft2.text(font, " FINT ", 83, 200, st7789.BLACK, st7789.WHITE)
        else: 
                tft2.jpg("img/sol240.jpg",0,0,st7789.SLOW)
                tft2.text(font, " MEGET FINT ", 40, 200, st7789.BLACK, st7789.WHITE)
            
    tft2.text(font, " "+ tryk +" ", 55, 100, st7789.BLACK, st7789.WHITE)
    tft2.text(font, " Hpa ", 80, 60, st7789.BLACK, st7789.WHITE)
    return(sidsteTekstvalg)

def vistemproutine():

    global sidstemånedsvalg
    global opdaterdisplay
    global sidsteTekstvalg
    global sidstetemp
    global sidstehumid
    global sidstepress
    global sidstedato
    global sidsteAiQ
    global timeseterror
    
    while True:
        sidstemånedsvalg = clock(sidstemånedsvalg)
    
        press = bme.pressure # we use only pressure from BME sensor, you can also read temperature and humidity as ewll
        humid = bme.humidity
        temp = bme.temperature
        iqhumid = humid
        
        temp = rettemperatur(temp)
        humid = retluftfugtighed(humid)
        
        #juster måling af hpa højde ect
        press ='%.2f' % (float(press) + Justeringstal)
        
        sidstetemp = temp
        sidstehumid = humid
        sidstepress = press
        
        opdaterdisplay = opdaterdisplay +1
        if opdaterdisplay > 5:
            opdaterdisplay = 0
            sidsteTekstvalg = vishpatryk(press,sidsteTekstvalg)
        
        tft0.text(font, " Temp ", 85, 80, st7789.BLACK, st7789.WHITE)
        #tft0.text(font, "                 ", 0, 110, st7789.BLACK, st7789.WHITE)
        # tryk ='%.1f' % (float(tryk)) 
        tft0.text(font," "+temp+" ", 75, 120, st7789.BLACK, st7789.WHITE)
  
        tft1.text(font, " Fugtighed ", 35, 80, st7789.BLACK, st7789.WHITE)
        tft1.text(font, " "+humid+" ", 60, 120, st7789.BLACK, st7789.WHITE)
        sleep(0.1)
        
def webpage(tryk, temp,fugtighed,dato):
    html = f"""
        <!DOCTYPE html>
        <html>
        <style type="text/plain"> </style>
        <head>
            <title>Kirkebakken 39 6705 Esbjerg Barometer </title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
        </head>
        <script>
            setInterval(() => location.reload(), 1000)
        </script>
        <body>
            <h1>Barometer Kirkebakken 39 6705 Esbjerg </h1>
            <font size="3" style="font-size: 12pt">Tid = {dato}</font></p><p style="line-height: 100%; margin-bottom: 0cm"><font size="3" style="font-size: 12pt">Tryk
= {tryk} Hpa</font></p><p style="line-height: 100%; margin-bottom: 0cm"><font size="3" style="font-size: 12pt">Temperatur
= {temp} </font></p><p style="line-height: 100%; margin-bottom: 0cm"><font size="3" style="font-size: 12pt">Luftfugtighed
= {fugtighed}</font></p>
        </body>
        </html>
        
        """
    return str(html)

def vismen():
    s = os.statvfs('/')
    print(f"Free storage: {s[0]*s[3]/1024} KB")
    print(f"Memory: {gc.mem_alloc()} of {gc.mem_free()} bytes used.")
#    print(f"CPU Freq: {machine.freq()/1000000}Mhz")

#sleep 3 seconds to get core1 initialized
sleep(3)
#wdt = WDT(timeout=10000) #start watcdog timeren
# Connect to WLAN

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

# Wait for Wi-Fi connection
connection_timeout = 10
while connection_timeout > 0:
    if wlan.status() >= 3:
        break
    connection_timeout -= 1
    print('Waiting for Wi-Fi connection...')
    time.sleep(1)

# Check if connection is successful
if wlan.status() != 3:
    raise RuntimeError('Failed to establish a network connection')
    hentDS3231Clock()
else:
    print('Connection successful!')
    network_info = wlan.ifconfig()
    print('IP address:', network_info[0])
    hentinternettid()
    if(timeseterror):
        hentDS3231Clock()
        
retur = _thread.start_new_thread(vistemproutine , [])

# Set up socket and start listening
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen()

# Initialize variables
state = "OFF"
random_value = 0
lock = _thread.allocate_lock()
        
print('Listening on', addr)
while True:
    try:
        conn, addr = s.accept()
        #print('Got a connection from', addr)
        
        # Receive and parse the request
        request = conn.recv(1024)
        request = str(request)
        #print('Request content = %s' % request)

                
        streng = datoTilStreng(sidstedato)
        # Generate HTML response
        response = webpage(sidstepress, sidstetemp, sidstehumid, streng )  

        # Send the HTTP response and close the connection
        conn.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        conn.send(response)
        conn.close()
        lock.acquire(1,-1)
        gc.collect()
        lock.release()
        vismen()

    except OSError as e:
        conn.close()
        print('Connection closed')

        sleep(0.001)
    


