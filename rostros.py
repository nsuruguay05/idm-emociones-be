import serial
import time

def most_common(lst):
    return max(set(lst), key=lst.count)
    
def enviar_arduino(data):
    arduino.write(bytes(data, encoding='utf8'))
    print("Esperando recibir")
    print(arduino.read())

# Conecta el Arduino
arduino = serial.Serial("/dev/ttyUSB0", 115200)

def send_robot(entrada):
    emotions = [entrada] 


    try:
        dominant_emotion = most_common(emotions)
        print(f"Emoción dominante: {dominant_emotion}")
        
        if dominant_emotion == "happy":
            enviar_arduino('2:70:3:12:4:150:5:90:8:170:7:90:9:110:10:150:11:60:')
            time.sleep(1)
            enviar_arduino('8:100:7:10:')
            time.sleep(1)
            enviar_arduino('8:170:7:90:')
            time.sleep(0.5)
            enviar_arduino('8:100:7:10:')
            time.sleep(0.5)
            
        elif dominant_emotion == "sad":
            enviar_arduino('2:110:3:12:4:150:5:90:6:40:7:130:9:60:10:150:11:50:')
            time.sleep(2)
            enviar_arduino('3:55:4:120:6:70:7:110:')
            time.sleep(1)
            enviar_arduino('3:25:4:150:6:40:7:130:')
            time.sleep(2)
        
        elif dominant_emotion == "angry":
            enviar_arduino('2:90:3:45:4:120:5:90:6:80:7:100:9:80:10:20:11:170:')
            time.sleep(1)

        elif dominant_emotion == "surprise":
            enviar_arduino('2:90:3:100:4:85:5:90:6:130:7:50:8:90:9:90:10:90:11:90:')
            time.sleep(2)
            enviar_arduino('3:12:4:150:')
            time.sleep(0.5)
            enviar_arduino('3:100:4:85:')
            time.sleep(2)
            enviar_arduino('3:12:4:150:')
            time.sleep(1)
            enviar_arduino('3:100:4:850:')
        
        elif dominant_emotion == "fear":
            enviar_arduino('2:90:3:65:4:110:5:150:6:90:7:90:8:90:9:90:10:90:11:90:')
            time.sleep(2)
            enviar_arduino('5:45:8:150:')
            time.sleep(2)
            enviar_arduino('3:50:4:120:5:90:6:75:7:115:8:90:10:70:11:110:')
            time.sleep(0.8)
            enviar_arduino('3:100:4:85:6:130:7:60:10:140:11:70:')
            time.sleep(2)

    except Exception as e:
        print(f"Error: {str(e)}")


arduino.close()