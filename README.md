# 2x2displayManometer
#This is the code to make a Barometer out of the 2x2 Display with Pico
#https://www.thingiverse.com/thing:6738354 is my Actual box for the display

The web interface is only caple of handling 1 or 2 request pr second
Use it only for data transfer to another program
Justeringstal = 7 is used for opdating hpa hight wrong mesument etc
At line 97 is the ajustment for timezone DK = 2 hours
the vismen() is showing aktuel data usage commit it out when not debugging

Ihave dicovered major memory leaks with the print() command and the 
tft2.jpg("img/thunder240.jpg",0,0,st7789.FAST) command

Sorry img/10240.jpg and 11240.jpg has to be renamed a240.jpg and b240.jpg
