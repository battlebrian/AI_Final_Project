import cv2
import os
import sys
from PIL import Image
import numpy as np

import picture_dealing as pd
import detect_text as dt
import translate.translate as tl
import text_recognition.demo as demo
import image2text.main as m
if not os.path.isdir("return"):
    os.mkdir("return")
if not os.path.isdir("output"):
    os.mkdir("output")
def find_dir(path):
    l=[]
    for fd in os.listdir(path):
        fullpath=path+fd
        if os.path.isdir(fullpath):
            l=l+ find_dir(fullpath)
        else:
            l.append((fullpath,fd))
    return l

opt=demo.parser_setting("text_recognition/")
if opt.mode=='picture':
    for name in find_dir(opt.i):
        img=cv2.imread(name[0])
        region=dt.detect(img)
        i=1
        filename,ext=name[1].split('.')
        if not os.path.isdir("return/"+filename+'_'+ext):
            os.mkdir("return/"+filename+'_'+ext)
        if not(ext=="jpg" or ext=="png" or ext=="jpeg"):
            continue
        file=open("return/"+filename+'_'+ext+"/record.txt",mode='w')
        for box in region:
            x=max(min([box[0][0],box[1][0],box[2][0],box[3][0]]),0)
            y=max(min([box[0][1],box[1][1],box[2][1],box[3][1]]),0)
            w=min(max([box[0][0],box[1][0],box[2][0],box[3][0]]),img.shape[1])
            h=min(max([box[0][1],box[1][1],box[2][1],box[3][1]]),img.shape[0])
            file.write(str(x)+","+str(y)+"_"+str(w)+","+str(h)+'\n')
            crop_img = pd.crop_image(img,(y,x),h,w)
            cv2.imwrite("return/"+filename+'_'+ext+"/"+str(i)+"."+ext,crop_img)
            i+=1
        if len(region)<5 and len(region)!=1:
            for i in range(10-len(region)):
                cv2.imwrite("return/"+filename+'_'+ext+"/"+"blank"+str(i)+"."+ext,crop_img)
        opt.image_folder='./return/'+filename+'_'+ext+'/'
        text=demo.demo(opt)
        record=[]
        for i in range(len(text)):
            if text[i][1] in record:
                continue
            record.append(text[i][1])
            result=tl.google_translate(text[i][1])
            tl.write_txt(opt.o+filename+'_'+ext+".txt",text[i][1]+':'+result)
else:
    m.main(opt.i, opt.o)
    for name in find_dir(opt.o):
        filename,ext=name[1].split('.')
        if not ext=='txt':
            continue
        file=open(name[0],'r')
        content=file.read()
        file.close()
        tl.write_txt(opt.o+name[1],'\n'+'\n'+'Translation:\n')
        if len(content)>4891:
            i=0
            while 1:
                if i>=len(content):
                    break
                elif i+4891<=len(content):
                    result=tl.google_translate(content[i:i+4891])
                    tl.write_txt(opt.o+name[1],result)
                else:
                    result=tl.google_translate(content[i:len(content)])
                    tl.write_txt(opt.o+name[1],result)
        else:
            result=tl.google_translate(content)
            tl.write_txt(opt.o+name[1],result)

