from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, redirect, url_for
import time
import requests
import os
import sys

app_path = os.getcwd()
sleepTime = 0.2
log_space = '    '
print("\n" + app_path + "\n" + "***************************")
log_file_path = f"{app_path}/logs.txt"
logs = open(f"{log_file_path}", "a")
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///domains.db'
app.config['SECRET_KEY'] = '<write_your_secret_key>' #fill this with secret key
db = SQLAlchemy(app)

class Domains(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(25))
    domain = db.Column(db.String(50))
    power = db.Column(db.Boolean)
    message = db.Column(db.Boolean)

db.create_all()

@app.route("/")
def index():
    domains = Domains.query.all()
    if domains:
        try:

            b = os.path.getsize(log_file_path)

            for i in domains:
                ip = i.ip
                host = i.domain

                res = os.popen(f"ping {ip} -n 1").read()

                time.sleep(1.5)

                logTime = time.strftime("%Y:%m:%d-%H:%M:%S")

                if "Request timed out" in res:
                    i.power = 0
                    f_log = open(log_file_path, "a")
                    f_log.write(str(logTime) + log_space + str(host) + log_space + str(ip) + log_space + 'down' + '\n')

                elif "Destination host unreachable" in res:
                    i.power = 0
                    f_log = open(log_file_path, "a")
                    f_log.write(str(logTime) + log_space + str(host) + log_space + str(ip) + log_space + 'down' + '\n')

                elif "Ping request could not find host" in res:
                    i.power = 0
                    f_log = open(log_file_path, "a")
                    f_log.write(str(logTime) + log_space + str(host) + log_space + str(ip) + log_space + 'down' + '\n')

                else:
                    i.power = 1
                    i.message = 0
                    f_log = open(log_file_path, "a")
                    f_log.write(str(logTime) + log_space + str(host) + log_space + str(ip) + log_space + 'up' + '\n')

            time.sleep(sleepTime)

            if (b > 5368709120):
                with open(log_file_path, "w"):
                    pass

        except(KeyboardInterrupt):
            pass

    return render_template("index.html", domains=domains)


@app.route("/check")
def checkServer():
    domains = Domains.query.all()
    try:

        b = os.path.getsize(log_file_path)

        for i in domains:
            ip = i.ip
            host = i.domain

            res = os.popen(f"ping {ip} -n 1").read()

            time.sleep(1.5)

            logTime = time.strftime("%Y:%m:%d-%H:%M:%S")

            if "Request timed out" in res:
                i.power = 0
                f_log = open(log_file_path, "a")
                f_log.write(str(logTime) + log_space + str(host) + log_space + str(ip) + log_space + 'down' + '\n')

            elif "Destination host unreachable" in res:
                i.power = 0
                f_log = open(log_file_path, "a")
                f_log.write(str(logTime) + log_space + str(host) + log_space + str(ip) + log_space + 'down' + '\n')

            elif "Ping request could not find host" in res:
                i.power = 0
                f_log = open(log_file_path, "a")
                f_log.write(str(logTime) + log_space + str(host) + log_space + str(ip) + log_space + 'down' + '\n')


            else:
                i.power = 1
                i.message = 0
                f_log = open(log_file_path, "a")
                f_log.write(str(logTime) + log_space + str(host) + log_space + str(ip) + log_space + 'up' + '\n')

                time.sleep(sleepTime)
        if (b > 5368709120):
            with open(log_file_path, "w"):
                pass

    except(KeyboardInterrupt):
        pass

    return render_template("check.html", domains=domains)

@app.route("/add", methods=["POST"])
def addDomains():
    ip = request.form.get("ip")
    domain = request.form.get("domain")

    newDomain = Domains(ip=ip, domain=domain, power=False, message=False)

    db.session.add(newDomain)
    db.session.commit()
    return redirect(url_for("index"))


@app.route("/delete/<string:id>")
def deleteDomain(id):
    domain = Domains.query.filter_by(id=id).first()

    db.session.delete(domain)
    db.session.commit()

    return redirect(url_for("index"))

@app.route("/details/<string:id>")
def detailsDomain(id):
    domain = Domains.query.filter_by(id=id).first()
    print("*******************************")
    print(domain.ip)
    files = open(log_file_path, "r")
    lines = files.readlines()
    up_list = []
    down_list = []
    len_log = max(len(x) for x in lines)
    for line in lines:
        if domain.ip in line:
            if 'down' in line:
                down_list.append(line)
            else:
                up_list.append(line)

    time.sleep(sleepTime)

    return render_template("details.html", domain_name = domain.domain, domain_ip = domain.ip, up_list = up_list, down_list = down_list, len_down = len(down_list), stars = (len_log*'*'))

if __name__ == "__main__":
    app.run(debug=False)

