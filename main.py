import cv2
import os
from cvzone.HandTrackingModule import HandDetector
import numpy as np

# Define dimensions for the captured video and the images

width, height = 1200, 720
gestureThreshold = 300
buttonPressed = False
buttonCounter = 0
buttonDelay = 30
annotations = [[]]
annotationNumber = 0
annotationStart = False #to identify the starting and ending point

folder_path = 'images'

# Initialize video capture
cap = cv2.VideoCapture(0)
cap.set(3, width)
cap.set(4, height)

# Get and sort the list of image paths
path_of_images = sorted(os.listdir(folder_path), key=len)
print(path_of_images)

imgNumber = 0
hs, ws = 240, 400
# Initialize hand detector
detector = HandDetector(detectionCon=0.8, maxHands=1)

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)  # 1-horizontal flip, 0-vertical flip
    if not success:
        print("Failed to capture image")
        break

    pathFullImage = os.path.join(folder_path, path_of_images[imgNumber])
    imgCurrent = cv2.imread(pathFullImage)
    if imgCurrent is None:
        print(f"Failed to read image {pathFullImage}")
        break

    hands, img = detector.findHands(img)
    cv2.line(img, (0, gestureThreshold), (width, gestureThreshold), (0, 255, 0), 5)

    if hands and buttonPressed is False:
        hand = hands[0]
        fingers = detector.fingersUp(hand)
        cx, cy = hand['center']
        print(fingers)
        handType = hand['type']

        lmList = hand['lmList']
        # contraint values for easier drawing
        if handType == "Left":
            xVal = int(np.interp(lmList[8][0], [width//2, width], [0, w]))
        else:
            xVal = int(np.interp(lmList[8][0], [0, width // 2], [0, w]))
        yVal = int(np.interp(lmList[8][1], [0, height-150], [0, h]))
        indexFinger = xVal, yVal

        if cy <= gestureThreshold: #if hand is at the height of the face
            #gesture 1 - left
            if fingers == [1,0,0,0,0]:
                print("Left")
                if imgNumber > 0:
                    buttonPressed = True
                    annotations = [[]] # to delete the drawing in the upcoming slides
                    annotationNumber = 0
                    annotationStart = False
                    imgNumber -= 1

            # gesture 2 - Right
            if fingers == [0, 0, 0, 0, 1]:
                print("Right")
                if imgNumber < len(path_of_images)-1:
                    buttonPressed = True
                    annotations = [[]] # to delete the drawing in the upcoming slides
                    annotationNumber = 0
                    annotationStart = False
                    imgNumber += 1

        # gesture 3 - shows pointer
        if fingers == [0, 1, 1, 0, 0]:
            cv2.circle(imgCurrent, indexFinger, 12, (0, 0, 255), cv2.FILLED )

        # gesture 4 - draw pointer
        if fingers == [0, 1, 0, 0, 0]:
            if annotationStart is False: # to prevent continuity of drawing
                annotationStart = True
                annotationNumber += 1
                annotations.append([])
            cv2.circle(imgCurrent, indexFinger, 12, (0, 0, 255), cv2.FILLED)
            annotations[annotationNumber].append(indexFinger)
        else:
            annotationStart = False

        # gesture 5 - erase
        if fingers == [0, 1, 1, 1, 0]:
            if annotations:
                if annotationNumber >=0:
                    annotations.pop(-1) #undo drawing
                    annotationNumber -= 1
                    buttonPressed =True
    # button pressed iterations
    if buttonPressed:
        buttonCounter += 1
        if buttonCounter > buttonDelay:
            buttonCounter = 0
            buttonPressed = False

    for i in range (len(annotations)):
        for j in range(len(annotations[i])):
            if(j != 0):#cuz when we start i will be zero, then will show an error
                cv2.line(imgCurrent, annotations[i][j-1], annotations[i][j], (0, 0, 200), 12)

    # Resize captured image
    image_small = cv2.resize(img, (ws, hs))

    # Ensure the main image is large enough
    h, w, _ = imgCurrent.shape
    if h >= height and w >= width:
        # Place the resized video capture on the main image at the top-right corner
        imgCurrent[0:hs, w - ws:w] = image_small

    # Display the images with specified window sizes
    cv2.namedWindow('Image', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Image', w, h)
    cv2.imshow('Image', img)

    cv2.namedWindow('Slides', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Slides', w, h)
    cv2.imshow('Slides', imgCurrent)

    key = cv2.waitKey(1)
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()