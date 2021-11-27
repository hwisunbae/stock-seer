import csv
import json
import os
import pandas as pd
from django.core import serializers
import json

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db.models import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt

from .backend.tweet_sa import *
from .models import *


@csrf_exempt
def html(request, filename, *args):
    context = {"filename": filename,
               "collapse": ""}
    if request.user.is_anonymous and filename not in ["login", "register", "forgot-password"]:
        return redirect("/login.html")
    if filename == "logout":
        logout(request)
        return redirect("/")
    if filename == "login" and request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        try:
            if "@" in username:
                user = User.objects.get(email=username)
            else:
                user = User.objects.get(username=username)
            user = authenticate(request, username=user.username, password=password)
            if user is not None:
                login(request, user)
                return redirect("/")
            else:
                context["error"] = "Wrong password"
        except ObjectDoesNotExist:
            context["error"] = "User not found"

        print("login")
        print(username, password)
    print(filename, request.method)
    if filename in ["register"]:
        print('register...')
        if request.POST:
            userObj = User.objects.create_user(first_name=request.POST.get('first_name'),
                                               last_name=request.POST.get('last_name'),
                                               username=request.POST.get('user_name'),
                                               email=request.POST.get('email'),
                                               password=request.POST.get('password'))
            userObj.save()
    if filename in ["404", "blank"]:
        context["collapse"] = "pages"

    return render(request, f"{filename}.html", context=context)


def index(request):
    if request.user.is_anonymous:
        return redirect("/login.html")
    return html(request, "index")


def generate_finance_report(request):
    if request.GET:
        pass
    else:
        dirname = os.path.dirname
        # Creating stock obj
        path = os.path.join(dirname(dirname(__file__)), 'backend', 'data', 'yfinance', 'preprocessed_yfinance.csv')
        with open(path) as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                obj, created = Stock.objects.get_or_create(
                    date=row[0],
                    adj_close=row[1],
                    close=row[2],
                    volume=row[3]
                )
                obj.save()
        print(Stock.objects.all())
        return HttpResponse('successfully generated report')


def visualize_finance_report(request):
    labels = []
    data = []

    queryset = Stock.objects.all().order_by('date')
    for entry in queryset:
        labels.append(entry.date)
        data.append(entry.adj_close)

    return JsonResponse(data={
        'labels': labels,
        'data': data,
    })


def generate_tweet_report(request):
    if request.GET:
        pass
    else:
        dirname = os.path.dirname
        # Creating tweet obj
        path = os.path.join(dirname(dirname(__file__)), 'backend', 'data', 'sa_tweets.csv')
        with open(path) as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                obj, created = Tweets.objects.get_or_create(
                    tweet_id=row[0],
                    created_at=row[1],
                    user_name=row[2],
                    text=row[3],
                    lang=row[4],
                    tokens=row[5],
                    subjectivity=row[6],
                    polarity=row[7],
                    analysis=row[8]
                )
                obj.save()
        print(Tweets.objects.all())
        return HttpResponse('successfully generated report')


def visualize_tweet_report(request):
    labels = ['1', '0', '-1']
    data = [0, 0, 0]

    queryset = Tweets.objects.all().order_by('created_at')
    for entry in queryset:
        if str(entry.analysis) == labels[0]:
            data[0] = data[0] + 1
        elif str(entry.analysis) == labels[2]:
            data[2] = data[2] + 1
        else:
            data[1] = data[1] + 1
    print(data, labels)

    return JsonResponse(data={
        'labels': labels,
        'data': data,
    })


def fetch_word_cloud(request):
    picked_start = request.GET['picked_start']
    picked_end = request.GET['picked_end']
    print(picked_start, picked_end)
    tweet_df = pd.DataFrame(list(Tweets.objects.filter(created_at__range=[picked_start, picked_end]).values()))
    data, doc_num, word_count_vector_num = get_idf_value(tweet_df)
    print(data, doc_num, word_count_vector_num)
    return JsonResponse(data={
        'data': data,
        'doc_num': doc_num,
        'word_count_vector_num': word_count_vector_num
    })


def fetch_tweet(request):
    picked_start = request.GET['picked_start']
    picked_end = request.GET['picked_end']

    objs = Tweets.objects.filter(created_at__range=[picked_start, picked_end])
    all_tweets = objs.all()

    data = serializers.serialize('json', all_tweets)
    # print(data)

    return HttpResponse(data, content_type="application/json")
