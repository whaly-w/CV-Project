import cv2
import numpy as np
import math


def find_pingpong(img, multiplier = 0.95):
    summary = []
    qualify = 0
    # img = cv2.imread(frame)
    img = cv2.resize(img, None, fx=0.2, fy=0.2)
    # print('-------------------------------| file:', frame)
    
    
    ## ------ Image Proparation
    HSV_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Get white mask (pinpong ball colour mask)
    lower = np.array([0, 0, 130])
    upper = np.array([40,80, 255])
    white_mask = cv2.inRange(HSV_img, lower, upper)
    out = cv2.bitwise_and(img, img, mask = white_mask)
    img_res = cv2.morphologyEx(white_mask, cv2.MORPH_OPEN, np.ones((9, 9)), iterations= 2)


    ## ------ Significant Roundness Detection
    circles = cv2.HoughCircles(img_res, cv2.HOUGH_GRADIENT,
                           dp= 0.8, minDist= 200,
                           param1= 10, param2= 10, 
                           minRadius= 112, maxRadius= 130)
    
    # Can't fit circle
    if circles is None:
        summary = ["Significant not round", "-", "-"]
        return None, summary , qualify
        
    img_rgb = img.copy()
    pingPong = (0, 0, 0)
    img_rgb = img.copy()
    pingPong = (0, 0, 0)
    X,Y,R = 0,0,0
    for x, y, r in circles[0]:
        if r > R:
            X,Y,R = x, y, r
    cv2.circle(img_rgb, (int(X), int(Y)), int(R), (255, 0, 0), thickness= 5)
    cv2.circle(img_rgb, (int(X), int(Y)), 5, (255, 0, 0), thickness= -1)
        
    pingPong = ((int(X), int(Y)), int(R))
    print('R:', pingPong)


    ## ------ Crop Out Background
    mask = np.zeros(img.shape, dtype=np.uint8) 
    cv2.circle(mask, pingPong[0], pingPong[1], (255,255,255), thickness=-1)  
    mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
    img_pingpong = cv2.bitwise_and(img, img, mask=mask)
    img_pingpong_cropped = cv2.getRectSubPix(img_pingpong, (pingPong[1]*2+20, pingPong[1]*2+20), pingPong[0])
    img_pingpong_cropped_gray = cv2.cvtColor(img_pingpong_cropped, cv2.COLOR_BGR2GRAY)


    ## ------ Roundness Detection
    _,tsh = cv2.threshold(img_pingpong_cropped_gray, 130, 255, cv2.THRESH_BINARY)
    tsh = cv2.morphologyEx(tsh, cv2.MORPH_CLOSE, np.ones((5, 5)), iterations= 2)
    
    contour, H = cv2.findContours(tsh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    contourArea = []
    imgTest = img_pingpong_cropped.copy()
    for i in range(len(contour)):
        area = cv2.contourArea(contour[i])
        print("index", i, "\tContourArea", area)
        contourArea.append(area)
        
    # Calculate contour area
    max_contour_area = max(contourArea)
    max_contour_index = contourArea.index(max_contour_area)
    cv2.drawContours(imgTest, contour, max_contour_index, (255,0,0), thickness = -1)
    
    # Calculate Hough Circle area
    conditionArea = multiplier*(math.pi * ((pingPong[1])**2))
    
    print(f"Condition the area: {conditionArea} ")
    print(f"Contur Area: {max_contour_area}")
    if area < conditionArea:
        print("Not round")
        summary.append("NOT round")
    else:
        print("pass")
        summary.append("round")
        qualify += 1
    summary.append(str(max_contour_area))
    
    
    ## ------ Filter Branding Text
    text_edge = cv2.Canny(img_pingpong_cropped, 20, 220)
    edge = cv2.Canny(img_pingpong_cropped, 30, 100)
    defects = cv2.bitwise_xor(edge, text_edge)


    ## ------ Defection Detection
    defects_connect = cv2.morphologyEx(defects, cv2.MORPH_CLOSE, np.ones((9, 9)), iterations= 2)
    contours_9, _ = cv2.findContours(defects, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    
    # If length over the threshold, draw the bounding contour 
    img_contour = img_pingpong_cropped.copy()
    n_defect = 0
    for contour in contours_9:
        arc_length = cv2.arcLength(contour, True)
        
        # print(arc_length)
        if arc_length > 100:
            cv2.drawContours(img_contour, [contour], -1, (0, 255, 0), 3)
            n_defect+= 1
        # if cv2.arcLength(contour, True)
    
    
    ## ------ Conclude
    if n_defect != 0:
        print('found defection')
        summary.append("DEFECTED")
    else:
        print('not found')
        summary.append("no defection")
        qualify += 1
    img_list = [img_pingpong_cropped, imgTest, text_edge, edge, defects, defects_connect,  img_contour]
    img_list_rgb = []
    for image in img_list:
        # print(image.shape)
        if len(image.shape) < 3:
            imgPREP = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        else:
            # imgPREP = image[:,:, ::-1]
            imgPREP = image
        img_list_rgb.append(imgPREP)
        
    result = cv2.hconcat(img_list_rgb)
    # plt.imshow(result)
    return result, summary, qualify

if __name__ == '__main__':
    print('Begin test')
    
    img = cv2.imread(r'D:\KMITL\KMITL\Year 02 - 02\Computer Vision\Work\A02_17_2024_Project\V2\dataset\IMG_5064.JPG')
    result, summary, qualify = find_pingpong(img)
    
    print('\n\nResult: ', end='')
    if qualify == 2:
        print('Qualified')
    else:
        print('Ejected')
    print(summary)
    cv2.imshow('Result', result)
    
    cv2.waitKey(0)

    
