from django.shortcuts import redirect,render
from django.contrib.auth import login,logout,authenticate
from .models import *
from django.http import HttpResponse
import nltk
from nltk.corpus import PlaintextCorpusReader
from nltk.stem import SnowballStemmer
import subprocess
from django.http import FileResponse
import os
import time 
import speech_recognition as sr
from nltk.stem.isri import ISRIStemmer
import cv2
def qr_to_path():
    cap = cv2.VideoCapture(0)
    detector = cv2.QRCodeDetector()
    result=None
    while True:
      _, img = cap.read()
      data, vertices_array, _ = detector.detectAndDecode(img)
      if vertices_array is not None:
        if data:
            result=data
            break    
      cv2.imshow("img", img)
      if cv2.waitKey(1) == ord("q"):
        break
    cap.release()
    cv2.destroyAllWindows()
    return result
class static:
    audio_path='http://docs.google.com/uc?export=open&id={}'
    text_path="https://drive.google.com/file/d/{}/preview"
    video_path='https://drive.google.com/uc?export=download&id={}'
    img_path='https://drive.google.com/uc?export=view&id={}'
    z={}
    result='No Thing'
    path=''
    form=[{'q':'إذا أردت أن تذهب إلى مكان في الجوار، ما المساعدة التي تحبها؟','a1':'ترى خريطة','a2':'شخص ما يخبرك بالإشارات والتفاصيل والعنوان'},
    {'q':'عندما تقابل صديق قديم، هل من الأفضل أن ؟','a1':'تراه','a2':'تسمعه'},
    {'q':'ما الوسيلة التي تحب أن يستخدمها المعلم؟','a1':'الرسم والصور','a2':'الكلام والمناقشة'},
    {'q':'ما الشيء الذي تحب عمله أكثر؟','a1':'القراءة والنظر إلى الكتب','a2':'الاستماع إلى الموسيقى'},
    {'q':'كيف يمكنك الحكم على شخص ما؟','a1':'بالنظر الى وجهه','a2':'من خلال الاستماع إلى صوته'},
    {'q':'ما الذي يجعلك تتذكر بعض الاحداث التي مرت عليك؟','a1':'يريك شخص ما الصور','a2':'تستمتع الى التعليمات'},
    {'q':'هل تحب أن','a1':'تنظر إلى الصور','a2':'تسمع قصص'},
    {'q':'أي هذه الأشياء تفضل عملها أكثر؟','a1':'مقابلة الاصدقاء وجهاً لوجه','a2':'التحدث مع الاصدقاء في الهاتف'},
    {'q':'ما الذي تلاحظه غالباً على الناس؟','a1':'كيف يلبسون','a2':'كيف يتحدثون ويتكلمون'},
    {'q':'ما الذي يجعلك أكثر استمتاعاً في حياتك؟','a1':'النظر الى الصور','a2':'التحدث مع الاصدقاء'},
    {'q':'هل تتذكر أكثر عندما','a1':'ترى الأشياء','a2':'تسمع الأشياء'},
    {'q':'ما تتذكره أفضل عن الناس؟','a1':'الوجوه','a2':'الأسماء'},
    {'q':'أي من هذه الاشياء تحبه أكثر؟','a1':'تشاهد التلفزيون','a2':'الاستماع إلى الموسيقى'},
    {'q':'لو حصلت على سماعات مكبرة جديدة، ما الذي ستفعله لتشغيلها؟','a1':'تنظر الى التعليمات والصور','a2':'تسأل شخص ما كيف تعمل'}
    ]
def audio_search():
    r = sr.Recognizer()
    mic = sr.Microphone()
    while(True):
        with mic as source:
            audio = r.listen(source)
            time.sleep(1)
            break
    return r.recognize_google(audio)

def laya_matching(data,query):
    def steming(data):
        stemmer = SnowballStemmer('english')
        st = ISRIStemmer()
        #st.stem(w)
        result=''
        for x in data.lower().split(' '):
            result+=st.stem(x)+' '
        return result[:-1]
    matching=0
    matching_list=[]
    matching_path=[]
    matching_titles=[]
    for f in data:
        matching=0
        for word in steming(query).split(' '):
            for x in (steming(f['title'])+steming(f['key_word'])).split(' '):
                if nltk.edit_distance(word,x) <2:
                    print(x,word)
            #if word in steming(f['title']) or word in steming(f['key_word']):
                    matching+=1
        matching_list.append(matching)
        matching_path.append(f['path'])
        matching_titles.append(f['title'])
    return matching_list,matching_path,matching_titles
def matching_sort(matching_list,matching_path,matching_titles):
    sorted_matching_path=[]
    sorted_matching_titles=[]
    length=len(matching_list)
    for x in range(length):
        index=matching_list.index(max(matching_list))
        sorted_matching_path.append(matching_path[index])
        sorted_matching_titles.append(matching_titles[index])
        del matching_list[index]
        del matching_path[index]
        del matching_titles[index]
    return sorted_matching_titles,sorted_matching_path

# Create your views here.
def home(request):
    context={
        'user':None,
        'form':None    }
    learning_type=''
    print(request.POST)
    if request.POST.get('login',None):
        username=request.POST.get('username')
        password=request.POST.get('password')
        static.user=username
        users=userModel.objects.all()
        current_user=list(users.filter(name=username,password=password).values())
        if current_user:
            if current_user[0]['learning_type']=='لفظي':
                return redirect('text_view')
            elif current_user[0]['learning_type']=='بصري':
                return redirect('video_view')

        else:
            userModel.objects.create(name=username,password=password,learning_type='_')
            context={'user':username,'form':static.form}

            return render(request,'form.html',context)            
    if request.POST.get('form1',None):
             user=userModel.objects.get(name=static.user)
             
             t=[]
             for x in static.form:
                try:
                    t.append(request.POST.get(x['q'])[0])
                except:
                    pass
             if t.count('1')>t.count('2'):
                 user.learning_type='بصري'
                 user.save()
                 return redirect('video_view')
             else:
                user.learning_type='لفظي'
                user.save()
                return redirect('text_view')


    if request.POST.get('main',None):
             return redirect('home')
    return render(request,'home.html',context)
def text_view(request):
    if request.POST.get('main',None):
             return redirect('home')
    search='# *'
    d=None
    if request.method=='POST':
        if request.POST.get('read_btn',None):
            context={
            'results':static.result,
            'path_text':static.text_path,
            'path_audio':static.audio_path
               }
            return render(request,'textfile.html',context)
            
        if request.POST.get('search_btn',None):
            search=request.POST.get('search')
            files=FilesModel.objects.all()
            all_files=list(files.filter().values())
            a,b,c=laya_matching(all_files,search)
            d,e=matching_sort(a,b,c)
            static.result=d
            title=d[0]
            x1,x2,x3=0,0,0
            txt_path=[]
            aud_path=[]
            img_path=[]
            main=list(files.filter(title=title).values())[0]['main']
            try:
                txt_files=list(files.filter(main=main,file_type='text').values())[0]
                txt_path=static.text_path.format(txt_files['path'])
                x1=1
            except:
                pass
            try:
                aud_files=list(files.filter(main=main,file_type='sound').values())
                aud_files[0]
                for x in aud_files:
                    aud_path.append(static.audio_path.format(x['path']))
                x2=1
            except:
                pass
            try:
                img_files=list(files.filter(main=main,file_type='image').values())
                img_files[0]
                for x in img_files:
                    img_path.append(static.img_path.format(x['path']))
                x3=1
            except:
                pass
            
            
            
            context={
                'results':d,
                'read':True,
                'text_path':txt_path,
                'text':x1,
                'audio_path':aud_path,
                'audio':x2,
                'image_path':img_path,
                'image':x3
            }
            return render(request,'textfile.html',context)
    if request.POST.get('audio_btn',None):
        try:
            search=audio_search()
        except:
            search='error'
        files=FilesModel.objects.all()
        all_files=list(files.filter().values())
        a,b,c=laya_matching(all_files,search)
        d,e=matching_sort(a,b,c)
        static.result=d
        title=d[0]
        x1,x2,x3=0,0,0
        txt_path=[]
        aud_path=[]
        img_path=[]
        main=list(files.filter(title=title).values())[0]['main']
        try:
            txt_files=list(files.filter(main=main,file_type='text').values())[0]
            txt_path=static.text_path.format(txt_files['path'])
            x1=1
        except:
            pass
        try:
            aud_files=list(files.filter(main=main,file_type='sound').values())
            aud_files[0]
            for x in aud_files:
                aud_path.append(static.audio_path.format(x['path']))
            x2=1
        except:
            pass
        try:
            img_files=list(files.filter(main=main,file_type='image').values())
            img_files[0]
            for x in img_files:
                img_path.append(static.img_path.format(x['path']))
            x3=1
        except:
            pass
            
            
            
        context={
                'results':d,
                'read':True,
                'text_path':txt_path,
                'text':x1,
                'audio_path':aud_path,
                'audio':x2,
                'image_path':img_path,
                'image':x3
            }
        return render(request,'textfile.html',context)
    if request.POST.get('QR_btn',None):
        search= qr_to_path()
        files=FilesModel.objects.all()
        f=FilesModel.objects.get(path=search)
        x1,x2,x3=0,0,0
        txt_path=[]
        aud_path=[]
        img_path=[]
        main=f.main
        print('###',main)
        try:
            txt_files=list(files.filter(main=main,file_type='text').values())[0]
            txt_path=static.text_path.format(txt_files['path'])
            x1=1
        except:
            pass
        try:
            aud_files=list(files.filter(main=main,file_type='sound').values())
            aud_files[0]
            for x in aud_files:
                aud_path.append(static.audio_path.format(x['path']))
            x2=1
        except:
            pass
        try:
            img_files=list(files.filter(main=main,file_type='image').values())
            img_files[0]
            for x in img_files:
                img_path.append(static.img_path.format(x['path']))
            x3=1
        except:
            pass    
        print(2222,txt_path)
        context={
                'results':[f.title],
                'read':True,
                'text_path':txt_path,
                'text':x1,
                'audio_path':aud_path,
                'audio':x2,
                'image_path':img_path,
                'image':x3
            }
        return render(request,'textfile.html',context)
    context={
            'results':d,
            'title_path':None
        } 
    return render(request,'textfile.html',context)

def video_view(request):
    if request.POST.get('main',None):
             return redirect('home')
    search='# *'
    d=None
    if request.method=='POST':
        if request.POST.get('read_btn',None):
            context={
            'results':static.result,
            'path_text':static.text_path,
            'path_audio':static.audio_path
               }
            return render(request,'videofile.html',context)
            
        if request.POST.get('search_btn',None):
            search=request.POST.get('search')
            files=FilesModel.objects.all()
            all_files=list(files.filter().values())
            a,b,c=laya_matching(all_files,search)
            d,e=matching_sort(a,b,c)
            static.result=d
            title=d[0]
            x1,x2,x3,x4=0,0,0,0
            txt_path=[]
            aud_path=[]
            img_path=[]
            vid_path=[]
            main=list(files.filter(title=title).values())[0]['main']
            try:
                txt_files=list(files.filter(main=main,file_type='text').values())[0]
                txt_path=static.text_path.format(txt_files['path'])
                x1=1
            except:
                pass
            try:
                aud_files=list(files.filter(main=main,file_type='sound').values())
                aud_files[0]
                for x in aud_files:
                    aud_path.append(static.audio_path.format(x['path']))
                x2=1
            except:
                pass
            try:
                img_files=list(files.filter(main=main,file_type='image').values())
                img_files[0]
                for x in img_files:
                    img_path.append(static.img_path.format(x['path']))
                x3=1
            except:
                pass
            try:
                vid_files=list(files.filter(main=main,file_type='video').values())
                for x in vid_files:
                    vid_path.append(static.video_path.format(x['path']))
                vid_path=vid_path[0]
                x4=1
            except:
                pass

          
            
            context={
                'results':d,
                'read':True,
                'text_path':txt_path,
                'text':x1,
                'audio_path':aud_path,
                'audio':x2,
                'image_path':img_path,
                'image':x3,
                'video':x4,
                'video_path':vid_path
            }
            return render(request,'videofile.html',context)
    if request.POST.get('audio_btn',None):
        try:
            search=audio_search()
        except:
            search='error'
        files=FilesModel.objects.all()
        all_files=list(files.filter().values())
        a,b,c=laya_matching(all_files,search)
        d,e=matching_sort(a,b,c)
        static.result=d
        title=d[0]
        x1,x2,x3,x4=0,0,0,0
        txt_path=[]
        aud_path=[]
        img_path=[]
        vid_path=[]
        main=list(files.filter(title=title).values())[0]['main']
        try:
            txt_files=list(files.filter(main=main,file_type='text').values())[0]
            txt_path=static.text_path.format(txt_files['path'])
            x1=1
        except:
            pass
        try:
            aud_files=list(files.filter(main=main,file_type='sound').values())
            aud_files[0]
            for x in aud_files:
                aud_path.append(static.audio_path.format(x['path']))
            x2=1
        except:
            pass
        try:
            img_files=list(files.filter(main=main,file_type='image').values())
            img_files[0]
            for x in img_files:
                img_path.append(static.img_path.format(x['path']))
            x3=1
        except:
            pass
        try:
                vid_files=list(files.filter(main=main,file_type='video').values())
                for x in vid_files:
                    vid_path.append(static.video_path.format(x['path']))
                vid_path=vid_path[0]
                x4=1
        except:
            pass

          
            
        context={
                'results':d,
                'read':True,
                'text_path':txt_path,
                'text':x1,
                'audio_path':aud_path,
                'audio':x2,
                'image_path':img_path,
                'image':x3,
                'video':x4,
                'video_path':vid_path
            }
        return render(request,'videofile.html',context)
    if request.POST.get('QR_btn',None):
        search= qr_to_path()
        files=FilesModel.objects.all()
        f=FilesModel.objects.get(path=search)
        main=f.main
        x1,x2,x3,x4=0,0,0,0
        txt_path=[]
        aud_path=[]
        img_path=[]
        vid_path=[]
            
        try:
            txt_files=list(files.filter(main=main,file_type='text').values())[0]
            txt_path=static.text_path.format(txt_files['path'])
            x1=1
        except:
            pass
        try:
            aud_files=list(files.filter(main=main,file_type='sound').values())
            aud_files[0]
            for x in aud_files:
                aud_path.append(static.audio_path.format(x['path']))
            x2=1
        except:
            pass
        try:
            img_files=list(files.filter(main=main,file_type='image').values())
            img_files[0]
            for x in img_files:
                img_path.append(static.img_path.format(x['path']))
            x3=1
        except:
            pass
        try:
                vid_files=list(files.filter(main=main,file_type='video').values())
                for x in vid_files:
                    vid_path.append(static.video_path.format(x['path']))
                vid_path=vid_path[0]
                x4=1
        except:
            pass

          
        print(txt_path,'%%%') 
        context={
                'results':[f.title],
                'read':True,
                'text_path':txt_path,
                'text':x1,
                'audio_path':aud_path,
                'audio':x2,
                'image_path':img_path,
                'image':x3,
                'video':x4,
                'video_path':vid_path
            }
        return render(request,'videofile.html',context)
    context={
            'results':d,
            'title_path':None
        } 
    return render(request,'videofile.html',context)
    