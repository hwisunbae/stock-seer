import csv
import json
import os
import pandas as pd
from django.core import serializers
import json

from django.db.models.functions import TruncMonth, TruncDay, Trunc
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db.models import ObjectDoesNotExist, Sum, DateTimeField, Count
from django.views.decorators.csrf import csrf_exempt

from .backend import m_rf, m_xgboost
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


# def generate_finance_report(request):
#     if request.GET:
#         pass
#     else:
#         dirname = os.path.dirname
#         # Creating stock obj
#         path = os.path.join(dirname(dirname(__file__)), 'backend', 'data', 'yfinance', 'preprocessed_yfinance.csv')
#         with open(path) as f:
#             reader = csv.reader(f)
#             next(reader)
#             for row in reader:
#                 obj, created = Stock.objects.get_or_create(
#                     date=row[0],
#                     adj_close=row[1],
#                     close=row[2],
#                     volume=row[3]
#                 )
#                 obj.save()
#         print(Stock.objects.all())
#         return HttpResponse('successfully generated report')
#
#
# def generate_tweet_report(request):
#     if request.GET:
#         pass
#     else:
#         dirname = os.path.dirname
#         # Creating tweet obj
#         path = os.path.join(dirname(dirname(__file__)), 'backend', 'data', 'sa_tweets.csv')
#         with open(path) as f:
#             reader = csv.reader(f)
#             next(reader)
#             for row in reader:
#                 obj, created = Tweets.objects.get_or_create(
#                     tweet_id=row[0],
#                     created_at=row[1],
#                     user_name=row[2],
#                     text=row[3],
#                     lang=row[4],
#                     tokens=row[5],
#                     subjectivity=row[6],
#                     polarity=row[7],
#                     analysis=row[8]
#                 )
#                 obj.save()
#         print(Tweets.objects.all())
#         return HttpResponse('successfully generated report')

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


def visualize_tweet_report(request):
    picked_start = request.GET['picked_start']
    picked_end = request.GET['picked_end']
    print(picked_start, picked_end)

    # -------------------------------
    # Polarity Ratio
    ratio_labels = ['1', '0', '-1']
    ratio_data = [0, 0, 0]

    queryset = Tweets.objects.all().filter(created_at__range=[picked_start, picked_end])
    for entry in queryset:
        if str(entry.analysis) == ratio_labels[0]:
            ratio_data[0] = ratio_data[0] + 1
        elif str(entry.analysis) == ratio_labels[2]:
            ratio_data[2] = ratio_data[2] + 1
        else:
            ratio_data[1] = ratio_data[1] + 1
    print(ratio_labels, ratio_data)

    # -------------------------------
    # Stock Index
    stock_labels = []
    stock_data = []

    queryset = Stock.objects.all().filter(date__range=[picked_start, picked_end]).order_by('date')
    for entry in queryset:
        stock_labels.append(entry.date)
        stock_data.append(entry.adj_close)

    # -------------------------------
    # Stock Prediction

    # polarity score each day
    obj_tweet_pol = Tweets.objects.filter(created_at__range=[picked_start, picked_end]) \
        .annotate(date=Trunc('created_at', 'day', output_field=DateTimeField())) \
        .values('date') \
        .annotate(total_polarity=Sum('polarity')) \
        .order_by('date')

    # twitter volume each day
    obj_tweet_vol = Tweets.objects.filter(created_at__range=[picked_start, picked_end]) \
        .annotate(date=Trunc('created_at', 'day', output_field=DateTimeField())) \
        .values('date') \
        .annotate(total_tweets=Count('text')) \
        .order_by('date')

    obj_stock = Stock.objects.values('date', 'adj_close')

    rf_pred_stock, rf_accuracy = m_rf.get_random_forest(obj_tweet_pol, obj_tweet_vol, obj_stock)
    xgb_pred_stock, xgb_accuracy = m_xgboost.get_xgboost(obj_tweet_pol, obj_tweet_vol, obj_stock)
    return JsonResponse(data={
        'ratio_labels': ratio_labels,
        'ratio_data': ratio_data,
        'stock_labels': stock_labels,
        'stock_data': stock_data,
        'rf_real': rf_pred_stock['Real'].to_json(),
        'rf_pred': rf_pred_stock['Predicted'].to_json(),
        'xgb_pred': xgb_pred_stock['Predicted'].to_json(),
        'rf_accuracy': rf_accuracy,
        'xgb_accuracy': xgb_accuracy
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
