import cvzone
import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import google.generativeai as genai
from PIL import Image
import webbrowser
import time
import subprocess
import pywhatkit 

last_triggered = {
    "whatsapp": 0,
    "notion": 0,
    "gmail": 0
}
cooldown_seconds = 5 



genai.configure(api_key="AIzaSyCNNHchzXeSH4kc383ixfdg4qyxVqcQjtI")  
model = genai.GenerativeModel("gemini-1.5-flash")  


cap = cv2.VideoCapture(0) 
detector = HandDetector(staticMode=False, maxHands=2, modelComplexity=1, detectionCon=0.7, minTrackCon=0.3)

def getHandInfo(img):
      hands, img = detector.findHands(img, draw=True, flipType=True)

      if hands:
        
        hand1 = hands[0]  
        lmList = hand1["lmList"]  

        fingers1 = detector.fingersUp(hand1)
        print(fingers1)
        return fingers1,lmList
      
      else:
          return None,None
    

def draw(info,prev_pos,canvas):
    fingers1,lmList=info
    current_pos=None

    if fingers1 ==[0,1,0,0,0]:
        current_pos=lmList[8][0:2]
        if prev_pos is None:
            prev_pos=current_pos
        cv2.line(canvas,current_pos,prev_pos,color=(235, 206, 135),thickness=5)

    elif fingers1==[0,1,1,0,0]:
         canvas=np.zeros_like(img)

    return current_pos ,canvas


def sendToAI(model,canvas,fingers1):
    if fingers1==[0,1,0,0,1]: 
        pil_image=Image.fromarray(canvas)
        response = model.generate_content(["Find the side of the triangle", pil_image])
        print("\nThe answer of the problem:")
        print(response.text)
        return True
    
    return False


def send_whatsapp_message(phone_number,message):
    
    now = time.localtime()
    hour = now.tm_hour
    minute = now.tm_min + 1  # Sends message one minute ahead

    try:
        pywhatkit.sendwhatmsg(phone_number, message, hour, minute)
        print(f"Message sent to {phone_number}")
    except Exception as e:
        print(f"Failed to send message: {e}")



def performActionOnGesture(fingers):
    current_time = time.time()

    if fingers == [0, 1, 1, 1, 1] and current_time - last_triggered["whatsapp"] > cooldown_seconds:
        pywhatkit.sendwhatmsg_instantly("+918865033965", "Hello! This is a gesture-triggered message.", wait_time=0, tab_close=True)
        last_triggered["whatsapp"] = current_time
        return True

    elif fingers == [0, 1, 1, 0, 1] and current_time - last_triggered["whatsapp"] > cooldown_seconds:
        subprocess.Popen([r"C:\Users\shiva\OneDrive\Desktop\WhatsApp.lnk"], shell=True)
        print("Opening WhatsApp Desktop...")
        last_triggered["whatsapp"] = current_time
        return True

    elif fingers == [0, 1, 1, 0, 0] and current_time - last_triggered["notion"] > cooldown_seconds:
        subprocess.Popen([r"C:\Users\shiva\AppData\Local\Programs\Notion\Notion.exe"])
        print("Opening Notion Desktop...")
        last_triggered["notion"] = current_time
        return True

    elif fingers == [0, 1, 1, 1, 0] and current_time - last_triggered["gmail"] > cooldown_seconds:
        webbrowser.open("https://mail.google.com/mail/u/3/#inbox")
        print("Opening Gmail...")
        last_triggered["gmail"] = current_time
        return True

    return False





prev_pos =None
canvas =None
image_combined =None


while True:
    success, img = cap.read()
    img=cv2.flip(img,flipCode=1)

    if canvas is None:
        canvas=np.zeros_like(img)



    info=getHandInfo(img)
    if info:
        fingers1, lmList=info
        print(fingers1)
        prev_pos,canvas=draw(info,prev_pos,canvas)

        if performActionOnGesture(fingers1):
            continue

        should_stop=sendToAI(model,canvas,fingers1)
        if should_stop:
            break



    image_combined = cv2.addWeighted(img, 0.7, canvas, 0.25, 0)


    if not success:
        print("Failed to capture image")
        break


        print(" ")  
   # cv2.imshow("Image", img)
   # cv2.imshow("Canvas", canvas)
    cv2.imshow("Image Combined",image_combined)


    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
