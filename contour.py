
from opencv import cv
from opencv import highgui as hg

import nxt.locator
from nxt.motor import *

# Localiza e conecta o NXT
# Find and connect NXT
sock = nxt.locator.find_one_brick()
brick = sock.connect()
right = Motor(brick, PORT_B)
left = Motor(brick, PORT_C)

capture = hg.cvCreateCameraCapture(1)

# padroes reconhecidos
# known patterns
padroes = ("triangulo.png", "circulo.png", "H.png", "F.png")
color = (cv.CV_RGB(255,0,0),cv.CV_RGB(0,255,0),cv.CV_RGB(0,0,255),cv.CV_RGB(255,255,0))
limiar = (0.01, 0.001, 0.21, 0.18)
target = []
target_mod = []
target_c = []

# Armazenamento temporario
# Temporary storage
storage1 = cv.cvCreateMemStorage()
storage2 = cv.cvCreateMemStorage()

# Carrega, binariza e procura o contorno dos padroes
# Load, binarize and find contours
for i in range(0,len(padroes)):
    target.append(hg.cvLoadImage(padroes[i], hg.CV_LOAD_IMAGE_GRAYSCALE))
    target_mod.append(cv.cvCreateImage((target[i].width,target[i].height), cv.IPL_DEPTH_8U, 1))
    cv.cvThreshold(target[i],target_mod[i],200,254,cv.CV_THRESH_BINARY)
    target_c.append(cv.cvFindContours(target_mod[i], storage1)[1])
    target_c[i] = cv.cvApproxPoly(target_c[i],cv.sizeof_CvContour,storage1,cv.CV_POLY_APPROX_DP,1)

frame_mod = cv.cvCreateImage((hg.cvGetCaptureProperty(capture,hg.CV_CAP_PROP_FRAME_WIDTH), hg.cvGetCaptureProperty(capture,hg.CV_CAP_PROP_FRAME_HEIGHT)), cv.IPL_DEPTH_8U, 1)

hg.cvNamedWindow("Resultado")
hg.cvNamedWindow("Binarizado")
#strut = cv.cvCreateStructuringElementEx(3,3,0,0,cv.CV_SHAPE_CROSS)

while True:
    turn = -1
    # Captura o frame, binariza, procura por contornos e checa com os padroes
    # Capture frame, binarize, find contours and check with known patterns
    frame = hg.cvQueryFrame(capture)
    cv.cvCvtColor(frame, frame_mod,cv.CV_RGB2GRAY)
    cv.cvThreshold(frame_mod,frame_mod,120,254,cv.CV_THRESH_BINARY)
    hg.cvShowImage("Binarizado", frame_mod)
    source_c = cv.cvFindContours(frame_mod, storage2)[1]
    if source_c:
        for contour in source_c.hrange():
            seq = cv.cvApproxPoly(contour,cv.sizeof_CvContour,storage2,cv.CV_POLY_APPROX_DP,2)
            for i in range(0,4):
                res = cv.cvMatchShapes(target_c[i], contour, cv.CV_CONTOURS_MATCH_I3)
                if res > 0 and res < limiar[i] and cv.cvContourArea(seq) > 1000:
                    cv.cvDrawContours(frame,seq,color[i],color[i], 100,4)
                    #print padroes[i] + ": " + str(res)
                    turn = i
# move o NXT
# move NXT
    # esquerda
    # left
    if turn == 0:
        left.update(-25,170)
        right.update(25,170)
    # direita
    # right
    elif turn == 1:
        left.update(25,170)
        right.update(-25,170)
    # tras
    # back
    elif turn == 2:
        left.update(-25,170)
        right.update(-25,170)
    # frente
    # forward
    elif turn == 3:
        left.update(25,170)
        right.update(25,170)

    hg.cvShowImage("Resultado",frame)
    hg.cvWaitKey(10)
