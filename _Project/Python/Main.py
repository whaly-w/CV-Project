from Apply import find_pingpong
import cv2
import serial
from time import sleep as delay

# Set Serial port
ser = serial.Serial('COM12', 115200, timeout=1)
ser.reset_input_buffer()   

# Ser camera
cam = cv2.VideoCapture(1)

# Functions
def transmit(txt):
    txt = str(txt)
    txt += '\n'
    ser.write(bytes(txt, 'utf-8'))

if __name__ == '__main__':
    print('Begin')
    
    # Initiate loop
    while True:
        # Wait for responce from Arduino
        while True:
            data = (ser.readline().decode('utf-8').strip())
            # print(data)
            if data == 'Begin':
                print('Start CV Process')
                break
            delay(0.2)
            
        # Cap image to process
        _, frame = cam.read()
        result, summary, qualify = find_pingpong(frame)
        
        # Send command back to arduino
        if qualify == 2:
            print('Qualified\n')
            transmit(2)
        else:
            print('Ejected\n')
            transmit(1)
        
        delay(1)

    
    