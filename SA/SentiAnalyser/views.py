from multiprocessing import AuthenticationError
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template import loader
import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
from textblob import TextBlob
import joblib
from . import matplotlib_init 

from django.urls import reverse
from django.contrib.auth.models import User
from .models import RegisteredUser,AnalyzerData
from django.contrib import messages
from django.db import models
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib import auth

import re
import googleapiclient.discovery 
from django.contrib.auth.decorators import login_required






class MyModel(models.Model):
    file = models.FileField(upload_to='uploads/')

def home(request):
  return render(request, 'home.html')

def register(request):
  return render(request, 'register.html')

def login(request):
    return render(request, 'login')

def about(request):
    return render(request, 'about.html')

def about1(request):
    return render(request, 'about1.html')

@login_required
def home1(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    data= AnalyzerData.objects.filter(u_name = request.user.username).values()
    context = {
    'data': data,
    }
    return render(request, 'home1.html',context)


from django.shortcuts import redirect

@login_required
def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    data= AnalyzerData.objects.filter(u_name = request.user.username).values()
    context = {
    'data': data,
  }
    return render(request, 'dashboard.html',context)




def colName(file_name):
    try:
        # Check file extension to determine file type
        file_extension = file_name.name.split('.')[-1]
        if file_extension.lower() == 'csv':
            df = pd.read_csv(file_name, on_bad_lines='skip')
        elif file_extension.lower() in ['xlsx', 'xls']:
            df = pd.read_excel(file_name)
        else:
            print("Unsupported file format.")
            return None, None
        
        possible_columns = ["text", "tweet", "comment", "comments", "feedback"]
        for col_name in possible_columns:
            df.columns = df.columns.str.lower()
            if col_name in df.columns:
                j = col_name
                df1 = df[[col_name]]
                return df1, j
        
        print("None of the specified columns found.")
        return None, None

    except Exception as e:
        print("Something went wrong:", e)
        return None, None




            
    
def cleanData(txt):

    if isinstance(txt, str):  # Check if the value is a string
        txt = re.sub(r'@[A-Za-z0-9]+', '', txt)
        txt = re.sub(r'#', '', txt)
        txt = re.sub(r'RT:', '', txt)
        txt=re.sub( r'https?:\/\/[A-Za-z0-9\.\/]+' ,'' ,txt)
    return txt

def getSubjectivity(text):
    if isinstance(text, str):
        return TextBlob(text).sentiment.subjectivity
    else:
        return None
    
def getPolarity(text):
    if isinstance(text, str):
        return TextBlob(text).sentiment.polarity
    else:
        return None
    

def getAnalysis(n):
    if n>0.1:
        return "Positive"
    elif n<-0.1:
        return "Negative"
    else:
        return "Neutral"
    

@login_required
def analyzer(request):
    error_message = None
    pos = 0
    neg = 0
    neu = 0

    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        print(uploaded_file)
        df1, col_name = colName(uploaded_file)

        if df1 is not None and col_name is not None:
            df1[col_name] = df1[col_name].apply(cleanData)
            # finding subjectivity and polarity to each text
            df1["Subjectivity"] = df1[col_name].apply(getSubjectivity)
            df1["Polarity"] = df1[col_name].apply(getPolarity)
            df1 = df1.drop(df1[df1[col_name] == ""].index)
            df1["Score"] = df1["Polarity"].apply(getAnalysis)
            file_data=df1.head(10)

            # Positive comments
            positive = df1[df1["Score"] == "Positive"]
            pos = positive.shape[0] / df1.shape[0] * 100

            # Negative comments
            negative = df1[df1["Score"] == "Negative"]
            neg = negative.shape[0] / df1.shape[0] * 100

            # Neutral comments
            neutral = df1[df1["Score"] == "Neutral"]
            neu = neutral.shape[0] / df1.shape[0] * 100

            explode = (0, 0.1, 0)
            labels = "Positive", "Negative", "Neutral"
            sizes = [pos, neg, neu]
            colors = ["green", "red", "yellow"]
            plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', startangle=120)
            plt.axis('equal')
            plt.title("Sentiment Analysis Results (Pie Chart)")

            
            chart_path = 'D:\Project\SA\SentiAnalyser\static\pie_chart.jpeg'
            plt.savefig(chart_path,dpi=100)
            print("Chart path:", chart_path)
            
            print("Image saved at:", chart_path)

            # Clear the current figure to release memory
            plt.clf()

            #-----------------Hate Speech Detection---------------------------
            
            new_data_df = df1
            new_data_df.dropna(subset=[col_name], inplace=True)

            # Load the trained model
            model = joblib.load('trained_model.pkl')

            # Make predictions
            predictions = model.predict(new_data_df[col_name])

            # hate speech percentage
            hate_speech_percentage = (predictions.sum() / len(predictions)) * 100

            
            categories = ['Non-hate speech', 'Hate speech']
            percentages = [(len(predictions) - predictions.sum()) / len(predictions) * 100, hate_speech_percentage]
            plt.bar(categories, percentages, color=['blue', 'red'])
            plt.ylabel('Percentage')

            chart_path1 = 'D:\Project\SA\SentiAnalyser\static\Bar_chart.jpeg'
            plt.savefig(chart_path1)

            plt.clf()


            
            return render(request, 'display.html', {'chart_path': chart_path ,'chart_path1':chart_path1 , 'file_data': file_data})

        else:
            error_message = "File not found or specified column not found."

    return render(request, 'analyzer.html', {'error_message': error_message})





def register_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        cnf_password = request.POST.get('cnf_password')

        

        if password != cnf_password:
            messages.error(request, "Passwords do not match.",extra_tags='error')
            return redirect(reverse('register'))
        # Check if the username is already taken
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken.",extra_tags='error')
            return redirect('register')

        # Create a new user
        user = User.objects.create_user(username=username, email=email, password=password)

        
        registered_user = RegisteredUser.objects.create(username=username, email=email, password=password)

        
        auth.login(request, user)

        messages.success(request, "Registration successful. You can now log in.",extra_tags='success')
         

    return render(request, 'register.html')  




from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            #messages.success(request, "Login successful.")
            return redirect('home1')  
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('user_login')  

    return render(request, 'login.html')




# -----------------analyzing comments from youtube videos-----------------------
from SentiAnalyser.youtube_data import get_youtube_comments,colName1,extract_video_id

    
@login_required
def youtube_comments_analyzer(request):
    error_message = None
    pos = 0
    neg = 0
    neu = 0

    if request.method == 'POST':
        video_url = request.POST.get('video_url')
        try:
            comments_df = get_youtube_comments(video_url)
            if comments_df is not None and len(comments_df) > 0:
                df1,col_name = colName1(comments_df)

                if df1 is not None and col_name is not None:
                    df1[col_name] = df1[col_name].apply(cleanData)
                    
                    df1["Subjectivity"] = df1[col_name].apply(getSubjectivity)
                    df1["Polarity"] = df1[col_name].apply(getPolarity)
                    df1 = df1.drop(df1[df1[col_name] == ""].index)
                    df1["Score"] = df1["Polarity"].apply(getAnalysis)
                    file_data=df1.head(10)

                    # Positive comments
                    positive = df1[df1["Score"] == "Positive"]
                    pos = positive.shape[0] / df1.shape[0] * 100

                    # Negative comments
                    negative = df1[df1["Score"] == "Negative"]
                    neg = negative.shape[0] / df1.shape[0] * 100

                    # Neutral comments
                    neutral = df1[df1["Score"] == "Neutral"]
                    neu = neutral.shape[0] / df1.shape[0] * 100

                    explode = (0, 0.1, 0)
                    labels = "Positive", "Negative", "Neutral"
                    sizes = [pos, neg, neu]
                    colors = ["green", "red", "yellow"]
                    plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', startangle=120)
                    plt.axis('equal')
                    #plt.title("Sentiment Analysis Results (Pie Chart)")

                    chart_path = 'D:\Project\SA\SentiAnalyser\static\pie_chart.jpeg'
                    plt.savefig(chart_path,dpi=100)
                    print("Chart path:", chart_path)
                    
                    print("Image saved at:", chart_path)

                    # Clear the current figure to release memory
                    plt.clf()

                    #-----------------Hate Speech Detection---------------------------
                    
                    new_data_df = df1
                    new_data_df.dropna(subset=[col_name], inplace=True)

                    model = joblib.load('trained_model.pkl')

                    predictions = model.predict(new_data_df[col_name])

                    hate_speech_percentage = (predictions.sum() / len(predictions)) * 100

                    categories = ['Non-hate speech', 'Hate speech']
                    percentages = [(len(predictions) - predictions.sum()) / len(predictions) * 100, hate_speech_percentage]
                    plt.bar(categories, percentages, color=['blue', 'red'])
                    plt.ylabel('Percentage')

                    chart_path1 = 'D:\Project\SA\SentiAnalyser\static\Bar_chart.jpeg'
                    plt.savefig(chart_path1)

                    plt.clf()

                    return render(request, 'display.html', {'chart_path': chart_path ,'chart_path1':chart_path1 , 'file_data': file_data})

                else:
                    error_message = "File not found or specified column not found."
        except Exception as e:
          
            error_message = f"Error occurred: {str(e)}"
            return render(request, 'display.html', {'error_message': error_message})           

    else:
        # Render the initial form page if the request method is not POST
        return render(request, 'analyzer.html', {'error_message': error_message})

    



from django.shortcuts import render
from django.http import HttpResponse

from .models import AnalyzerData
def analyze_content(request):
    error_message = None

    if request.method == 'POST':
        uploaded_file = request.FILES.get('file')
        video_url = request.POST.get('video_url')

        if uploaded_file and video_url:
            error_message = "Please provide either a file or a YouTube video link, not both."

        elif not uploaded_file and not video_url:
            error_message = "Please provide either a file or a YouTube video link."

        elif uploaded_file:
            file_extension = uploaded_file.name.split('.')[-1].lower()
            if file_extension not in ['csv', 'xlsx', 'xls']:
                error_message = "Please upload a CSV or Excel file."
            else:
                
                u_name=request.user.username
                content_name=request.POST['content_name']
                content_description=request.POST['content_description']
                video_url=request.POST['video_url']
                uploaded_file=request.FILES.get('file')
                new_data=AnalyzerData(u_name=u_name,content_name=content_name,content_description=content_description,video_url=video_url,uploaded_file=uploaded_file)
                new_data.save()
                return analyzer(request)

        elif video_url:
            
            u_name=request.user.username
            content_name=request.POST['content_name']
            content_description=request.POST['content_description']
            video_url=request.POST['video_url']
            uploaded_file=request.FILES.get('file')
            new_data=AnalyzerData(u_name=u_name,content_name=content_name,content_description=content_description,video_url=video_url,uploaded_file=uploaded_file)
            new_data.save()
            return youtube_comments_analyzer(request)

   
    return render(request, 'analyzer.html', {'error_message': error_message})

        

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect

def delete_row(request, pk):
    data_object = AnalyzerData.objects.get(id=pk)
    data_object.delete()
    return HttpResponseRedirect(reverse('dashboard'))




     


from django.shortcuts import render
from django.http import HttpResponse

def view_content(request,url):
    error_message = None
    pos = 0
    neg = 0
    neu = 0

    
    video_url = url
    try:
        comments_df = get_youtube_comments(video_url)
        
        if comments_df is not None and len(comments_df) > 0:
            df1,col_name = colName1(comments_df)
            if df1 is not None and col_name is not None:
                    df1[col_name] = df1[col_name].apply(cleanData)
                    
                    df1["Subjectivity"] = df1[col_name].apply(getSubjectivity)
                    df1["Polarity"] = df1[col_name].apply(getPolarity)
                    df1 = df1.drop(df1[df1[col_name] == ""].index)
                    df1["Score"] = df1["Polarity"].apply(getAnalysis)
                    file_data=df1.head(10)

                    # Positive comments
                    positive = df1[df1["Score"] == "Positive"]
                    pos = positive.shape[0] / df1.shape[0] * 100

                    # Negative comments
                    negative = df1[df1["Score"] == "Negative"]
                    neg = negative.shape[0] / df1.shape[0] * 100

                    # Neutral comments
                    neutral = df1[df1["Score"] == "Neutral"]
                    neu = neutral.shape[0] / df1.shape[0] * 100

                    explode = (0, 0.1, 0)
                    labels = "Positive", "Negative", "Neutral"
                    sizes = [pos, neg, neu]
                    colors = ["green", "red", "yellow"]
                    plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', startangle=120)
                    plt.axis('equal')
                    plt.title("Sentiment Analysis Results (Pie Chart)")

                    chart_path = 'D:\Project\SA\SentiAnalyser\static\pie_chart.jpeg'
                    plt.savefig(chart_path,dpi=100)
                    print("Chart path:", chart_path)
                    
                    print("Image saved at:", chart_path)

                    # Clear the current figure to release memory
                    plt.clf()

                    #-----------------Hate Speech Detection---------------------------
                    
                    new_data_df = df1
                    new_data_df.dropna(subset=[col_name], inplace=True)

                    model = joblib.load('trained_model.pkl')

                    predictions = model.predict(new_data_df[col_name])

                    hate_speech_percentage = (predictions.sum() / len(predictions)) * 100

                    categories = ['Non-hate speech', 'Hate speech']
                    percentages = [(len(predictions) - predictions.sum()) / len(predictions) * 100, hate_speech_percentage]
                    plt.bar(categories, percentages, color=['blue', 'red'])
                    plt.ylabel('Percentage')

                    chart_path1 = 'D:\Project\SA\SentiAnalyser\static\Bar_chart.jpeg'
                    plt.savefig(chart_path1)

                    plt.clf()

                    return render(request, 'display.html', {'chart_path': chart_path ,'chart_path1':chart_path1 , 'file_data': file_data})

            else:
                error_message = "File not found or specified column not found."
                    
            
    except Exception as e:
            
            error_message = f"Error occurred: {str(e)}"
            return render(request, 'display.html', {'error_message': error_message})           

    else:
        
        return HttpResponseRedirect(reverse('dashboard'))



