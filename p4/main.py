# project: p4
# submitter: bli378
# partner: none
# hours: 10
# https://www.kaggle.com/datasets/unsdsn/world-happiness?select=2019.csv

from urllib import response
from bs4 import BeautifulSoup
import pandas as pd
from flask import Flask, request, jsonify, Response, make_response
import re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import numpy as np

app = Flask(__name__)
df = pd.read_csv("main.csv")
counter = 0
a_counter = 0
b_counter = 0
ip_list = {}

@app.route('/')
def home():
    global counter
    with open("index.html") as f:
        html = f.read()
        soup = BeautifulSoup(html,"html.parser")
        button = soup.find("button")
        if counter < 10:   
            counter+=1
            version = counter%2
            if version == 0:
                button.attrs['style'] = "color:red"
            else:
                button.attrs['style'] = "color:blue"  
            html =  soup   
        else:
            if a_counter >= b_counter:
                button.attrs['style'] = "color:red"
            else:
                button.attrs['style'] = "color:blue" 
            html = soup
    return str(html)

@app.route("/browse.html")
def browse():
    html = df.to_html()
    soup = BeautifulSoup(html, "html.parser")
    head = soup.new_tag("h1")
    head.string = "Browse"
    soup.insert(0,head)
    return str(soup)

@app.route("/donate.html")
def donate():
    global counter, a_counter, b_counter
    version = counter%2
    if counter <10:
        if version == 0:
            a_counter += 1
        else:
            b_counter += 1
    with open("donate.html") as f:
        html = f.read()
        return html

@app.route('/email', methods=["POST"])
def email():
    email = str(request.data, "utf-8")
    if re.match(r"[a-z0-9]+@[a-z]+\.[a-z]{2,3}", email): # 1

        with open("emails.txt", "a") as f: # open file in append mode
            f.write(email + "\n") # 2
        with open("emails.txt", "r") as f:
            num_subscribed = len(f.readlines())
        return jsonify(f"thanks, you're subscriber number {num_subscribed}!")
    return jsonify(f"INVALID EMAIL ADDRESS: BE MORE CAREFUL") # 3

@app.route('/browse.json')
def browse_json():
    import time
    global ip_list
    df_json = df.to_dict()
    ip = request.remote_addr
    current = time.time()
    ip_time = ip_list.get(ip)
    if ip not in ip_list.keys():
        ip_list[ip] = current
    elif current - ip_time < 60:
        resp = Response("PLEASE WAIT " + str(60 - (current - ip_time)) + " SECONDS", status=429)
        resp.headers["Retry-After"] = 60 - (current - ip_time)
        return resp
    ip_list[ip] = current
    return jsonify(df_json)

@app.route("/overall_country.svg")
def country():
    country = df["Country or region"][:10]
    score = df["Score"][:10]
    fig, ax = plt.subplots(figsize=(6,5))
    ax = fig.add_axes([0,0,1,1])  
    ax.bar(country,score)
    ax.tick_params(axis="x",labelrotation=30)
    ax.set_xlabel("Country")
    ax.set_ylabel("Overall Score")
    ax.set_title("Overall Score of Top Ten Nations")
    fake_file = BytesIO()
    ax.get_figure().savefig(fake_file, format="svg", bbox_inches="tight")
    plt.close(fig)
    return Response(fake_file.getvalue(),
                    headers={"Content-Type": "image/svg+xml"})

@app.route("/specific_country.svg")
def specific():
    country = request.args["country"]
    country_df = df[df["Country or region"] == country]
    country_df = country_df.drop("Score",axis=1)
    country_df = country_df.drop("Overall rank",axis=1)
    country_df = country_df.set_index("Country or region")
    scores = []
    for value in country_df.keys():
        scores.append(float(country_df[value]))

    fig, ax = plt.subplots(figsize=(6,5))
    ax = fig.add_axes([0,0,1,1])
    ax.set_ylim([0,2])
    ax.bar(country_df.keys(),scores)
    ax.tick_params(axis="x",labelrotation=20)
    ax.set_xlabel("Variables")
    ax.set_ylabel("Score")
    ax.set_title("Scores for " + country)
    fake_file = BytesIO()
    ax.get_figure().savefig(fake_file, format="svg", bbox_inches="tight")
    plt.close(fig)
    return Response(fake_file.getvalue(),
                    headers={"Content-Type": "image/svg+xml"})

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, threaded=False) # don't change this line!

# NOTE: app.run never returns (it runs for ever, unless you kill the process)
# Thus, don't define any functions after the app.run call, because it will
# never get that far.