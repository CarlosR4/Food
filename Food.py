import RPi.GPIO as GPIO
import time
import os

PIN_TRIGGER = 18 #pin 11

PIN_ECHO = 11 #pin 13

RoAPin = 31
RoBPin = 33
BtnPin = 35

TouchBtn = 12
LedPin = 22

BUZZER = 38

flag = 0
globalCounter = 0
Last_RoB_Status = 0
Current_RoB_Status = 0

firstTemp = 0
currentTemp = 0
def readSensor(id):
    tfile = open("/sys/bus/w1/devices/"+id+"/w1_slave")
    text = tfile.read()
    tfile.close()
    secondline = text.split("\n")[1]
    temperaturedata = secondline.split(" ")[9]
    temperature = float(temperaturedata[2:])
    temperature = temperature/1000
    print("Sensor" + id + " - Current temperature : %0.3f C"  % temperature)
    global currentTem
    currentTemp = temperature
    
def readSensors():
    count = 0
    sensor = ""
    for file in os.listdir("/sys/bus/w1/devices/"):
        if (file.startswith("28-")):
            readSensor(file)
            count+=1
    if (count == 0):
        print("No sensor found. Check Connection.")
        
def initialreadSensor(id):
    tfile = open("/sys/bus/w1/devices/"+id+"/w1_slave")
    text = tfile.read()
    tfile.close()
    secondline = text.split("\n")[1]
    temperaturedata = secondline.split(" ")[9]
    temperature = float(temperaturedata[2:])
    temperature = temperature/1000
    print("Sensor" + id + " - Current temperature : %0.3f C"  % temperature)
    global firstTemp
    firstTemp = temperature
    
def initialreadSensors():
    count = 0
    sensor = ""
    for file in os.listdir("/sys/bus/w1/devices/"):
        if (file.startswith("28-")):
            initialreadSensor(file)
            count+=1
    if (count == 0):
        print("No sensor found. Check Connection.")
def setup():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(PIN_TRIGGER, GPIO.OUT)
    GPIO.setup(PIN_ECHO, GPIO.IN)
    
    GPIO.output(PIN_TRIGGER, GPIO.LOW)
    print("Waiting for sensor to settle")
    
    time.sleep(1)
    
    GPIO.setup(RoAPin, GPIO.IN)
    GPIO.setup(RoBPin,GPIO.IN)
    GPIO.setup(BtnPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(BtnPin, GPIO.FALLING, callback=btnISR)
    
    GPIO.setup(LedPin, GPIO.OUT)
    GPIO.setup(TouchBtn, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.output(LedPin, GPIO.HIGH)
    initialreadSensors()
    
    GPIO.setwarnings(False)
    GPIO.setup(BUZZER, GPIO.OUT)

def buzz(noteFreq, duration):
    halveWaveTime = 1 / (noteFreq * 2 )
    waves = int(duration * noteFreq)
    for i in range(waves):
       GPIO.output(BUZZER, True)
       time.sleep(halveWaveTime)
       GPIO.output(BUZZER, False)
       time.sleep(halveWaveTime)
       
def play():
    t=0
    notes=[262,294,330,262,262,294,330,262,330,349,392,330,349,392,392,440,392,349,330,262,392,440,392,349,330,262,262,196,262,262,196,262]
    duration=[0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,1,0.5,0.5,1,0.25,0.25,0.25,0.25,0.5,0.5,0.25,0.25,0.25,0.25,0.5,0.5,0.5,0.5,1,0.5,0.5,1]
    for n in notes:
        buzz(n, duration[t])
        time.sleep(duration[t] *0.1)
        t+=1
        
        
def rotaryDeal():
    global flag
    global Last_RoB_Status
    global Current_RoB_Status
    global globalCounter
    
    Last_RoB_Status = GPIO.input(RoBPin)
    while(not GPIO.input(RoAPin)):
        Current_RoB_Status = GPIO.input(RoBPin)
        flag = 1
        
    if flag == 1:
        flag = 0
        if(Last_RoB_Status == 0 ) and (Current_RoB_Status == 1):
            globalCounter = globalCounter - 1
            print(str(globalCounter) + " minus one")
        if (Last_RoB_Status == 1 ) and (Current_RoB_Status == 0):
            globalCounter = globalCounter + 1
            print(str(globalCounter) + " plus one")
            
def btnISR(channel):
    global globalCounter
    globalCounter = 0
    
ispressed = 0
def loop():
    status = True
    global globalCounter
    global firstTemp
    global currentTemp
    tmp = 0 # Rotary temporary
    while True:
        rotaryDeal()
        
        print("Calculating distance")
        GPIO.output(PIN_TRIGGER, GPIO.HIGH)
        
        time.sleep(0.5)
        
        GPIO.output(PIN_TRIGGER, GPIO.LOW)
        
        pulse_start_time = 0
        
        pulse_end_time= 0
        
        while GPIO.input(PIN_ECHO)==0:
            pulse_start_time = time.time()
        while GPIO.input(PIN_ECHO)==1:
            pulse_end_time = time.time()
            
        pulse_duration = pulse_end_time - pulse_start_time
        distance = round(pulse_duration * 17150, 2)
        print ("Distance:",distance,"cm")
        if distance < 50:
            play()
            if GPIO.input(TouchBtn) == GPIO.HIGH:
                status = not status
                GPIO.output(LedPin, status)
                print("Beep boop light on")
                print(status)
                #time.sleep(1)
                readSensors()
                print("Initial temp:" + str(firstTemp))
                if currentTemp  < firstTemp + 3:
                    print ("FOOD HEATED")
                time.sleep(1)
                
        if tmp != globalCounter:
            print(globalCounter)
            tmp = globalCounter

        
    
def destroy():
    GPIO.output(LedPin, GPIO.HIGH)
    GPIO.cleanup()
    
if __name__ == '__main__':
    setup()
    try:
        loop()
    except KeyboardInterrupt:
        destroy()