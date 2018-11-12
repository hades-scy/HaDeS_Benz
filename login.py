from flask import Flask, render_template, flash, url_for, request, session, redirect, Response
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
import re
from wtforms.validators import input_required
from bs4 import BeautifulSoup
import requests
import datetime

app = Flask(__name__)
bcrypt = Bcrypt(None)

app.config['db'] = "HaDeSBenz"
app.config['MONGO_URI'] = 'mongodb://127.0.0.1:27017/HaDeSBenz'
app.secret_key = 'HaDeS'
mongo = PyMongo(app)


@app.route('/')
def index():
    if 'username' in session:
        users = mongo.db.user
        rol = users.find_one({'name': session['username'], 'role': 'admin'})
        if rol:
            return render_template('adminindex.html')
        return render_template('index.html')
    return render_template('signin.html')


@app.route('/signout')
def signout():
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route('/myaccount', methods=['POST', 'GET'])
def account():
    user = mongo.db.user
    fghj = user.find_one({'name': session['username']})
    if fghj:
        if request.method == 'POST':
            asd = request.form['badd']
            user.update_one({'name': session['username']}, {"$set": {'dl': request.form['bdl'], 'phno': request.form['bph'],
                          'email': request.form['bemail'],
                          'address': asd, 'date': datetime.datetime.utcnow(),
                          'role': 'user'}})
            return redirect(url_for('account'))
        return render_template('useracc.html', un=fghj)

@app.route('/bookings')
def mybook():
    jkl = mongo.db.testdrive
    car = jkl.find({'name': session['username']})
    for nm in car:
        return render_template('userbook.html', test=nm, wq=car)


@app.route('/model/<name>')
def product(name):
    amg = mongo.db.carfull
    car = amg.find_one({'product_name': name})
    coview = mongo.db.caroverview
    oview = coview.find_one({'product_name': name})
    cprice = mongo.db.carpriceloc
    priceloc = cprice.find_one({'product_name': name})
    cvar = mongo.db.carvariant
    var = cvar.find_one({'product_name': name})
    cfull = mongo.db.scrape
    full = cfull.find_one({'product_name': name})
    if car:
        for nm in oview:
            session['carname'] = car['product_name']
            return render_template('product.html', full=full, nm=nm, car=car, oview=oview, priceloc=priceloc, var=var)
    return redirect(url_for('index'))


@app.route('/Traditional/<name>')
def prod(name):
    tdw = mongo.db.traditional
    car = tdw.find_one({'name': name})
    if car:
        session['carname'] = car['name']
        return render_template('prod.html', car=car)
    return redirect(url_for('index'))


@app.route('/vehicle/<name>', methods=['POST', 'GET'])
def book(name):
    if request.method == 'POST':
        td = mongo.db.testdrive
        amg = mongo.db.carfull
        car = amg.find_one({'product_name': name})
        dt = mongo.db.user
        user = dt.find_one({'name': session['username']})
        if user:
            td.insert({'name': session['username'], 'dl': user['dl'], 'ph': user['phno'], 'email': user['email'],
                   'address': user['address'], 'car': name, 'img': car['img'], 'date': datetime.datetime.utcnow(), 'status': 'booked'})
        return redirect(url_for('messag', name='Successfully booked'))
    return redirect(url_for('index'))


@app.route('/signin', methods=['POST', 'GET'])
def signin():
    if request.method == 'POST':
        user = mongo.db.user
        login_user = user.find_one({'name': request.form['username']})
        if login_user:
            hashpass = bcrypt.check_password_hash(login_user['password'], request.form['password'])
            if hashpass == True:
                session['username'] = request.form['username']
                return redirect(url_for('index'))
        return redirect(url_for('messagebasic', vbn='Invalid username or password combination'))
    return render_template('signin.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        user = mongo.db.user
        existing_user = user.find_one({'name': request.form['username']})
        if existing_user is None:
            if request.form['password'] == request.form['password_confirmation']:
                hashpass = bcrypt.generate_password_hash(request.form['password'])
                user.insert({'name': request.form['username'], 'password': hashpass, 'role': 'user', 'dl': '',
                             'phno': '', 'email': '', 'address': ''})
                session['username'] = request.form['username']
                return redirect(url_for('index'))
            return redirect(url_for('messagebasic', vbn='Invalid password'))
        return redirect(url_for('messagebasic', vbn='Username already exists'))
    return render_template('signup.html')


@app.route('/Traditional.html')
def traditional():
    return render_template('traditional.html')


@app.route('/Reset Password', methods=['POST', 'GET'])
def resetus():
    if request.method == 'POST':
        user = mongo.db.user
        pass_reset = user.find_one({'name': session['username']})
        if pass_reset:
            hashpass = bcrypt.check_password_hash(pass_reset['password'], request.form['oldpass'])
            if hashpass == True:
                if request.form['newpass'] == request.form['newpassword_confirmation']:
                    hallpass = bcrypt.generate_password_hash(request.form['newpass'])
                    user.update_one({'name': session['username']}, {"$set": {'password': hallpass}})
                    return redirect(url_for('messag', name='The password has been changed successfully'))
        return redirect(url_for('messag', name='The password you have typed is incorrect'))
    return render_template('reset.html')


@app.route('/408 message/<name>')
def messag(name):
    return render_template('404.html', msg=name)


@app.route('/406 message/<vbn>')
def messagebasic(vbn):
    return render_template('basicinfo.html', msg=vbn)


@app.route('/admin bookings details')
def bookings():
    jkl = mongo.db.testdrive
    car = jkl.find({'status': 'booked'})
    for nm in car:
        return render_template('adminbook.html', test=nm, wq=car)


@app.route('/Car Model')
def allcar():
    jkl = mongo.db.scrape
    car = jkl.find()
    for nm in car:
        return render_template('allcar.html', test=nm, wq=car)


@app.route('/User Comments')
def admincomment():
    jkl = mongo.db.comment
    car = jkl.find()
    for nm in car:
        return render_template('admincomment.html', comm=nm, io=car)


@app.route('/about HaDeS Benz')
def about():
    return render_template('about.html')


@app.route('/contact_us', methods=['POST', 'GET'])
def send():
    if request.method == 'POST':
        comment = mongo.db.comment
        asd = request.form['inputMessage']
        comment.insert({'name': session['username'],  'email': request.form['inputEmail'], 'message': asd})
        return redirect(url_for('messag', name='Thank you for your Feedback'))
    return render_template('contact_us.html', test=session["username"])


@app.route('/AMG')
def amg():
    return render_template('AMG.html')



@app.route('/Reset Admin', methods=['POST', 'GET'])
def reset():
    if request.method == 'POST':
        user = mongo.db.user
        pass_reset = user.find_one({'name': session['username']})
        if pass_reset:
            hashpass = bcrypt.check_password_hash(pass_reset['password'], request.form['oldpass'])
            if hashpass == True:
                if request.form['newpass'] == request.form['newpassword_confirmation']:
                    hallpass = bcrypt.generate_password_hash(request.form['newpass'])
                    user.update_one({'name': session['username']}, {"$set": {'password': hallpass}})
                    return redirect(url_for('messagadmin', vbna='The password has been changed successfully'))
        return redirect(url_for('messagadmin', vbna='The password you have typed is incorrect'))
    return render_template('adminreset.html')


@app.route('/Chafe')
def scrap():
    return render_template('scrap.html')

@app.route('/407 message/<vbna>')
def messagadmin(vbna):
    return render_template('404admin.html', msg=vbna)

@app.route('/basic chafe')
def scrape():
        base_url = 'https://auto.ndtv.com/mercedes-benz-cars'
        scr = mongo.db.scrape
        scr.remove()
        r = requests.get(base_url)
        soup = BeautifulSoup(r.text, "html.parser")

        all_product = soup.find_all('div', class_="newmodel__grid grid grid__gap16")

        for item in all_product:
            d = {}

            # name & link
            product_name = item.find("h2", {"class":"newmodel__ttl h__mb15"})
            product_name = product_name.text.replace('\n', "").strip()
            product_link = item.find('a', attrs={'href': re.compile("^https://")})
            product_link = product_link.get('href')
            info = (product_name[14:] + '') if len(product_name) > 2 else product_name
            d['product_name'] = info
            d['product_link'] = product_link

            # price
            product_price = item.find("div", {"class":"newmodel__price"})
            product_price = product_price.text.replace('\n', "").strip()
            d['product_price'] = product_price

            #images
            images = item.find("img", {"data-webp": "1"})
            d['img'] = images['data-src']

            #specifications
            l=[]
            product_p = item.find_all("div", {"class": "newmodel__spec grid-flex"})
            for gh in product_p:
                product_var = gh.find("div", {"class": "newmodel__spec-label"})
                product_var = product_var.text.replace('\n', "").strip()
                l.append(product_var)
            we = l.pop()
            d['fuel'] = we
            we = l.pop()
            d['gear'] = we
            we = l.pop()
            d['mileage'] = we
            we = l.pop()
            d['type'] = we


            # review
            product_review = item.find("div", {"class":"rating-score__grade"})
            try:
                product_review = product_review.text
                d['product_review'] = float(product_review)
            except:
                d['product_review'] = "New Car"

            d['time'] = datetime.datetime.utcnow()

            scr.insert_one(d)

        return redirect(url_for('messagadmin', vbna='New values updated successfully'))


@app.route('/model chafe')
def scrapefull():
    jkl = mongo.db.scrape
    car = jkl.find()
    fgh = mongo.db.carfull
    fgh.remove()
    for ov in car:
        base_url = ov['product_link']
        r = requests.get(base_url)
        soup = BeautifulSoup(r.text, "html.parser")
        all_product = soup.find_all('div', class_="cnb-page")

        for item in all_product:
            d = {}

            product_name = item.find("h1", {"class": "model-hero__title h__mr10"})
            product_name = product_name.text.replace('\n', "").strip()
            info = (product_name[14:] + '') if len(product_name) > 2 else product_name
            d['product_name'] = info

            # price
            product_price = item.find("span", {"class":"h__mr10 js-price-range"})
            product_price = product_price.text.replace('\n', "").strip()
            d['product_price'] = product_price

            product_engine = item.find("div", {"class": "model-overview__spec-txt"})
            product_engine = product_engine.text.replace('\n', "").strip()
            d['product_engine'] = product_engine

            #images
            images = item.find("img", {"id": "product-image"})
            d['img'] = images['data-src']

            product_review = item.find("div", {"class": "rating-score__grade"})
            try:
                product_review = product_review.text
                d['product_review'] = float(product_review)
            except:
                d['product_review'] = "New Car"

            product_emi = item.find("span", {"class": "js-emi-price"})
            product_emi = product_emi.text.replace('\n', "").strip()
            d['product_emi'] = product_emi


            d['time'] = datetime.datetime.utcnow()

            fgh.insert_one(d)

    return redirect(url_for('messagadmin', vbna='New values updated successfully'))


@app.route('/overview chafe')
def caroverview():
    jkl = mongo.db.scrape
    car = jkl.find()
    fgh = mongo.db.caroverview
    fgh.remove()
    for ov in car:
        base_url = ov['product_link']

        r = requests.get(base_url)
        soup = BeautifulSoup(r.text, "html.parser")
        all_product = soup.find_all('div', class_="cnb-page")

        for item in all_product:
            d = {}

            product_name = item.find("h1", {"class": "model-hero__title h__mr10"})
            product_name = product_name.text.replace('\n', "").strip()
            info = (product_name[14:] + '') if len(product_name) > 2 else product_name
            d['product_name'] = info

            all_pro = soup.find_all('li', class_="model-overview__item")
            for gh in all_pro:
                product_type = gh.find("div", {"class": "spec-card__val"})
                product_type = product_type.text.replace('\n', "").strip()
                product_name = gh.find("div", {"class": "spec-card__label"})
                product_name = product_name.text.replace('\n', "").strip()
                d[product_name] = product_type

            d['time'] = datetime.datetime.utcnow()

            fgh.insert_one(d)

    return redirect(url_for('messagadmin', vbna='New car values updated successfully'))


@app.route('/variant chafe')
def carvariant():
    jkl = mongo.db.scrape
    car = jkl.find()
    fgh = mongo.db.carvariant
    fgh.remove()
    l=[]
    for ov in car:
        base_url = ov['product_link']

        r = requests.get(base_url)
        soup = BeautifulSoup(r.text, "html.parser")
        all_product = soup.find_all('div', class_="cnb-page")

        for item in all_product:
            d = {}

            product_name = item.find("h1", {"class": "model-hero__title h__mr10"})
            product_name = product_name.text.replace('\n', "").strip()
            info = (product_name[14:] + '') if len(product_name) > 2 else product_name
            d['product_name'] = info

            all_pro = soup.find_all('li', class_="model-overview__list-item")
            y = 1

            for gh in all_pro:
                    product_var = gh.find("a", {"class": "model-overview__list-link"})
                    product_var = product_var.text.replace('\n', "").strip()
                    l.append(product_var)

            g = ['v1','v2','v3','v4','v5','v6','v7']
            for o in g:
                try:
                    we = l.pop()
                    d[o] = we
                except:
                    break

            d['time'] = datetime.datetime.utcnow()

            fgh.insert_one(d)

    return redirect(url_for('messagadmin', vbna='New car values updated successfully'))


@app.route('/model onroad price chafe')
def carpriceloc():
    jkl = mongo.db.scrape
    car = jkl.find()
    fgh = mongo.db.carpriceloc
    fgh.remove()
    l=[]
    for ov in car:
        base_url = ov['product_link']

        r = requests.get(base_url)
        soup = BeautifulSoup(r.text, "html.parser")
        all_product = soup.find_all('div', class_="cnb-page")

        for item in all_product:
            d = {}

            product_name = item.find("h1", {"class": "model-hero__title h__mr10"})
            product_name = product_name.text.replace('\n', "").strip()
            info = (product_name[14:] + '') if len(product_name) > 2 else product_name
            d['product_name'] = info

            all_pro = soup.find_all('a', class_="price-otc__subgrid grid grid-2 grid__gap15")
            for gh in all_pro:
                product_city = gh.find("div", {"class": "text-truncate"})
                product_city = product_city.text.replace('\n', "").strip()
                product_cityprice = gh.find("div", {"class": "price-otc__val"})
                product_cityprice = product_cityprice.text.replace('\n', "").strip()
                d[product_city] = product_cityprice

            d['time'] = datetime.datetime.utcnow()

            fgh.insert_one(d)

    return redirect(url_for('messagadmin', vbna='New car values updated successfully'))

'''
@app.route('/carfeature')
def carfeature():
    jkl = mongo.db.scrape
    car = jkl.find()
    fgh = mongo.db.carfeature
    fgh.remove()
    l=[]
    for ov in car:
        base_url = ov['product_link']
        l = []
        r = requests.get(base_url)
        soup = BeautifulSoup(r.text, "html.parser")
        all_product = soup.find_all('div', class_="cnb-page")

        for item in all_product:
            d = {}

            product_name = item.find("h1", {"class": "model-hero__title h__mr10"})
            product_name = product_name.text.replace('\n', "").strip()
            d['product_name'] = product_name

            # features

            all_pr = item.find_all('div', class_="feature")
            o = []
            skl = all_pr.find('div', class_="feature__no")
            product_f = skl.text.replace('\n', " ").strip()
            product_f = product_f.replace('0', " ").strip()
            product_f = product_f.replace('1', " ").strip()
            product_f = product_f.replace('2', " ").strip()
            product_f = product_f.replace('3', " ").strip()
            product_f = product_f.replace('7', " ").strip()
            product_f = product_f.replace('4', " ").strip()
            product_f = product_f.replace('5', " ").strip()
            product_f = product_f.replace('6', " ").strip()
            product_f = product_f.replace('7', " ").strip()
            product_f = product_f.replace('8', " ").strip()
            product_f = product_f.replace('9', " ").strip()
            o.append(product_f)

            fgh = item.find_all('li', class_="feature__list-item")
            for lkj in fgh:
                    product_fe = lkj.text.replace('\n', " ").strip()
                    o.append(product_fe)
            l = ['f1','f2','f3','f4','f5','f6','f7','f8','f9','f10','f11','f12','f13','f14','f15','f16','f17','f18',
                    'f19', 'f20','f21', 'f22', 'f23', 'f24', 'f25', 'f26', 'f27', 'f28', 'f29', 'f30']
            for x in l:
                try:
                    d[x] = o.pop()
                except:
                    break

            d['time'] = datetime.datetime.utcnow()

            fgh.insert_one(d)

    return redirect(url_for('messagadmin', vbna='New car values updated successfully'))
'''

if __name__ == '__main__':
    app.run(debug=True)