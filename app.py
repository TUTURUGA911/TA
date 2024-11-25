from flask import Flask, render_template, request, redirect, url_for, jsonify
from pymongo import MongoClient
from werkzeug.utils import secure_filename
from bson import ObjectId
import hashlib
from datetime import datetime, timedelta
import jwt
import os
from bs4 import BeautifulSoup

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["UPLOAD_FOLDER"] = "./static/profile_pics"
# Utility functions
def format_price(value):
    return "{:,.0f}".format(value)
app.jinja_env.filters['format_price'] = format_price

articles_per_page = 3

SECRET_KEY = "AMS"

client = MongoClient('mongodb+srv://test:sparta@cluster0.evhvrqa.mongodb.net/?retryWrites=true&w=majority')
db = client.dbams

TOKEN_KEY = "mytoken"

def is_logged_in():
    token_receive = request.cookies.get(TOKEN_KEY)
    if not token_receive:
        return False
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        return True
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return False

def get_user_info():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.user.find_one({'username': payload.get('id')})
        return user_info
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return None

def is_admin(user_info):
    return user_info and user_info.get('level') == 1

# Routes
@app.route('/auth_login')
def auth_login():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=["HS256"],
        )
        user_info = db.user.find_one({'username': payload.get('id')})
        count_unread = db.notif.count_documents(
            {'to':payload['id'], 'from':{'$ne':payload['id']}, 'read': False})
        data_user = {
            'username': user_info['username'],
            'profilename': user_info['profile_name'],
            'level': user_info['level'],
            'profile_icon': user_info['profile_pic_real']
        }
        return jsonify({"result": "success", "data": data_user, "notif":count_unread})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return jsonify({"result": "fail"})


@app.route('/auth_login/<postcreator>')
def auth_login_detail(postcreator):
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=["HS256"],
        )
        user_info = db.user.find_one({'username': payload.get('id')})
        if user_info['username'] == postcreator:
            return jsonify({"result": "success"})
        else:
            return jsonify({"result": "fail"})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return jsonify({"result": "fail"})


@app.route('/auth_login/<commentcreator>')
def auth_login_comment(commentcreator):
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=["HS256"],
        )
        user_info = db.user.find_one({'username': payload.get('id')})
        if user_info['username'] == commentcreator:
            return jsonify({"result": "success"})
        else:
            return jsonify({"result": "fail"})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return jsonify({"result": "fail"})


@app.route('/admin')
def page_login():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=["HS256"],
        )
        user_info = db.user.find_one({'username': payload.get('id')})

        print(user_info)

        return redirect(url_for("home", msg="Anda sudah login!"))
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return render_template('login.html')


@app.route('/register/check_dup', methods=["POST"])
def check_dup():
    username_receive = request.form.get("username_give")
    exists = bool(db.user.find_one({'username': username_receive}))
    return jsonify({"result": "success", "exists": exists})


@app.route('/register', methods=["POST"])
def register():
    username_receive = request.form.get("username_give")
    email_receive = request.form.get("email_give")
    password_receive = request.form.get("password_give")
    emailcheck = bool(db.user.find_one({'email': email_receive}))

    data_user = {
        "username": username_receive,
        "email": email_receive,
        "password": password_receive,
        "profile_name": username_receive,
        "profile_pic": "",
        "profile_pic_real": "profile_pics/profile_icon.png",
        "profile_info": "",
        "blocked": False,
        "level": 2
    }

    if emailcheck == False:
        db.user.insert_one(data_user)
        return jsonify({"result": "success", "data": email_receive})
    else:
        return jsonify({"result": "fail", "msg": 'Maaf, email yang anda gunakan sudah terdaftar!'})


@app.route('/login', methods=["POST"])
def login():
    email_receive = request.form["email_give"]
    password_receive = request.form["password_give"]

    result = db.user.find_one(
        {
            "email": email_receive,
            "password": password_receive,
        }
    )
 

    if result:
        data_user = {
        'profilename': result['profile_name'],
        'level': result['level']
        }
        if result['blocked'] == True:
            data_block = db.blocklist.find_one({'user':result['username']})
            data_user['reasonblock'] = data_block['reason']
            data_user['userblock'] = data_block['user']
            return jsonify(
            {
                "result": "fail",
                "data": data_user,
                "status":"block"
            }
            )
        else:
            payload = {
                "id": result['username'],
                # the token will be valid for 24 hours
                 "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 24),
            }
            token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
            return jsonify(
            {
                "result": "success",
                "token": token,
                "data": data_user,
            }
            )

    # Let's also handle the case where the id and
    # password combination cannot be found
    else:
        return jsonify(
            {
                "result": "fail",
                "msg": "Kami tidak dapat menemukan akun anda, silakan cek email dan password anda!",
                "status":"Not Found"
            }
        )

@app.route('/')
def index():
    logged_in = is_logged_in()
    user_info = get_user_info()
    is_admin_flag = is_admin(user_info)
    
    if logged_in and is_admin_flag:
        return redirect(url_for('dashboard'))  # Redirect to admin dashboard if logged in as admin
    

    product_list = db.product.find()
    return render_template("index.html", user_info=user_info, is_admin=is_admin_flag, logged_in=logged_in, product_list=product_list)

@app.route('/produk')
def produk():
    logged_in = is_logged_in()
    user_info = get_user_info()
    is_admin_flag = is_admin(user_info)

    product_list = db.product.find()
    return render_template("produk.html", user_info=user_info, is_admin=is_admin_flag, logged_in=logged_in, product_list=product_list)

@app.route('/dashboard')
def dashboard():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_login = db.user.find_one({"username": payload["id"]})
        if(user_login['level'] == 1):
            return render_template('adminDashboard.html')
        else:
            return redirect(url_for("index", msg="Anda tidak diizinkan masuk halaman dashboard!"))
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("index", msg="Anda belum login!"))

@app.route('/addproduct', methods=['GET'])
def addproduct():
    user_info = get_user_info()
    if not user_info or not is_admin(user_info):
        return redirect(url_for("index"))

    return render_template("addProduct.html", user_info=user_info, is_admin=True, logged_in=True)

@app.route('/add_product', methods=['POST'])
def posting():
    name_receive = request.form.get('name_give')
    price_receive = int(request.form.get('price_give'))
    stock_receive = int(request.form.get('stock_give'))
    deskripsi_receive = request.form.get('deskripsi_give')
    kategori_receive = request.form.get('category_give')

    print(f"Received category: {kategori_receive}")  # Debugging line

    today = datetime.now()
    mytime = today.strftime("%Y-%m-%d-%H-%M-%S")

    if 'file_give' in request.files:
        file = request.files.get('file_give')
        file_name = secure_filename(file.filename)
        picture_name = file_name.split(".")[0]
        ekstensi = file_name.split(".")[1]
        picture_name = f"{picture_name}[{name_receive}]-{mytime}.{ekstensi}"
        file_path = f'./static/product_pics/{picture_name}'
        file.save(file_path)
    else:
        picture_name = "default.jpg"

    if 'file_give2' in request.files:
        file2 = request.files.get('file_give2')
        file2_name = secure_filename(file2.filename)
        picture_name2 = file2_name.split(".")[0]
        ekstensi2 = file2_name.split(".")[1]
        picture_name2 = f"{picture_name2}[{name_receive}]-{mytime}.{ekstensi2}"
        file2_path = f'./static/product_pics/{picture_name2}'
        file2.save(file2_path)
    else:
        picture_name2 = "default2.jpg"

    if 'file_give3' in request.files:
        file3 = request.files.get('file_give3')
        file3_name = secure_filename(file3.filename)
        picture_name3 = file3_name.split(".")[0]
        ekstensi3 = file3_name.split(".")[1]
        picture_name3 = f"{picture_name3}[{name_receive}]-{mytime}.{ekstensi3}"
        file3_path = f'./static/product_pics/{picture_name3}'
        file3.save(file3_path)
    else:
        picture_name3 = "default3.jpg"

    if 'file_give4' in request.files:
        file4 = request.files.get('file_give4')
        file4_name = secure_filename(file4.filename)
        picture_name4 = file4_name.split(".")[0]
        ekstensi4 = file4_name.split(".")[1]
        picture_name4 = f"{picture_name4}[{name_receive}]-{mytime}.{ekstensi4}"
        file4_path = f'./static/product_pics/{picture_name4}'
        file4.save(file4_path)
    else:
        picture_name4 = "default4.jpg"

    doc = {
        'product_name': name_receive,
        'product_price': price_receive,
        'product_stock': stock_receive,
        'kategori': kategori_receive,
        'image': picture_name,
        'image2': picture_name2,
        'image3': picture_name3,
        'image4': picture_name4,
        'description': deskripsi_receive,
    }
    db.product.insert_one(doc)
    return jsonify({
        'result': 'success',
        'msg': 'Product added!'
    })

@app.route('/editproduct/<id_product>', methods=['GET'])
def editproduct(id_product):
    user_info = get_user_info()
    if not user_info or not is_admin(user_info):
        return redirect(url_for("index"))

    info_product = db.product.find_one({'_id': ObjectId(id_product)})
    return render_template("editProduct.html", info_product=info_product)

@app.route('/edit_product/<id_product>', methods=['PUT'])
def edit(id_product):
    user_info = get_user_info()
    if not user_info or not is_admin(user_info):
        return jsonify({'result': 'fail', 'msg': 'Access denied'})

    name_receive = request.form.get('name_give')
    price_receive = int(request.form.get('price_give'))
    stock_receive = int(request.form.get('stock_give'))
    deskripsi_receive = request.form.get('deskripsi_give')

    today = datetime.now()
    mytime = today.strftime("%Y-%m-%d-%H-%M-%S")

    if 'file_give' in request.files:
        data_lama = db.product.find_one({'_id': ObjectId(id_product)})
        gambar_lama = data_lama['image']
        if gambar_lama != "default.jpg":
            os.remove(f'./static/product_pics/{gambar_lama}')

        file = request.files.get('file_give')
        file_name = secure_filename(file.filename)
        picture_name = file_name.split(".")[0]
        ekstensi = file_name.split(".")[1]
        picture_name = f"{picture_name}[{name_receive}]-{mytime}.{ekstensi}"
        file_path = f'./static/product_pics/{picture_name}'
        file.save(file_path)

        doc = {
            'product_name': name_receive,
            'product_price': price_receive,
            'product_stock': stock_receive,
            'image': picture_name,
            'description': deskripsi_receive,
        }

    else:
        doc = {
            'product_name': name_receive,
            'product_price': price_receive,
            'product_stock': stock_receive,
            'description': deskripsi_receive,
        }

    if 'file_give2' in request.files:
        data_lama = db.product.find_one({'_id': ObjectId(id_product)})
        gambar_lama2 = data_lama.get('image2', 'default2.jpg')
        if gambar_lama2 != "default2.jpg":
            os.remove(f'./static/product_pics/{gambar_lama2}')

        file2 = request.files.get('file_give2')
        file2_name = secure_filename(file2.filename)
        picture_name2 = file2_name.split(".")[0]
        ekstensi2 = file2_name.split(".")[1]
        picture_name2 = f"{picture_name2}[{name_receive}]-{mytime}.{ekstensi2}"
        file2_path = f'./static/product_pics/{picture_name2}'
        file2.save(file2_path)

        doc['image2'] = picture_name2
    
    if 'file_give3' in request.files:
        data_lama = db.product.find_one({'_id': ObjectId(id_product)})
        gambar_lama3 = data_lama.get('image3', 'default3.jpg')
        if gambar_lama3 != "default3.jpg":
            os.remove(f'./static/product_pics/{gambar_lama3}')

        file3 = request.files.get('file_give3')
        file3_name = secure_filename(file3.filename)
        picture_name3 = file3_name.split(".")[0]
        ekstensi3 = file3_name.split(".")[1]
        picture_name3 = f"{picture_name3}[{name_receive}]-{mytime}.{ekstensi3}"
        file3_path = f'./static/product_pics/{picture_name3}'
        file3.save(file3_path)

        doc['image3'] = picture_name3

    if 'file_give4' in request.files:
        data_lama = db.product.find_one({'_id': ObjectId(id_product)})
        gambar_lama4 = data_lama.get('image4', 'default4.jpg')
        if gambar_lama4 != "default4.jpg":
            os.remove(f'./static/product_pics/{gambar_lama4}')

        file4 = request.files.get('file_give4')
        file4_name = secure_filename(file4.filename)
        picture_name4 = file4_name.split(".")[0]
        ekstensi4 = file4_name.split(".")[1]
        picture_name4 = f"{picture_name4}[{name_receive}]-{mytime}.{ekstensi4}"
        file4_path = f'./static/product_pics/{picture_name4}'
        file4.save(file4_path)

        doc['image4'] = picture_name4

    db.product.update_one({'_id': ObjectId(id_product)}, {'$set': doc})
    return jsonify({
        'result': 'success',
        'msg': 'Product updated'
    })

@app.route('/manageproduct', methods=['GET'])
def manageproduct():
    user_info = get_user_info()
    if not user_info or not is_admin(user_info):
        return redirect(url_for("index"))

    product_list = db.product.find()
    return render_template("manageProduct.html", user_info=user_info, is_admin=True, logged_in=True, product_list=product_list)

@app.route('/delete_product/<string:id_delete>', methods=['DELETE'])
def delete_product(id_delete):
    user_info = get_user_info()
    if not user_info or not is_admin(user_info):
        return jsonify({'result': 'fail', 'msg': 'Access denied'})

    try:
        info_product = db.product.find_one({'_id': ObjectId(id_delete)})
        image = info_product['image']
        if image != "default.jpg":
            os.remove(f'./static/product_pics/{image}')

        db.product.delete_one({'_id': ObjectId(id_delete)})
        return jsonify({'result': 'success', 'msg': 'Product Deleted'})
    except Exception as e:
        return jsonify({'result': 'fail', 'msg': str(e)})

@app.route('/detail/<id_product>', methods=['GET'])
def detail(id_product):
    logged_in = is_logged_in()
    user_info = get_user_info()
    is_admin_flag = is_admin(user_info)

    info_product = db.product.find_one({'_id': ObjectId(id_product)})


    return render_template("detail.html", user_info=user_info, is_admin=is_admin_flag, logged_in=logged_in, info_product=info_product)
    
@app.route('/search', methods=['GET'])
def search():
    logged_in = is_logged_in()
    user_info = None
    is_admin = False

    query = request.args.get('q')
    product_list = db.product.find({"product_name": {"$regex": query, "$options": "i"}})

    return render_template("produk.html", user_info=user_info, is_admin=is_admin, logged_in=logged_in, product_list=product_list, query=query)
    
@app.route('/about')
def about():
    token_receive = request.cookies.get("mytoken")
    data = list(db.saran.find({}))
    print(data)
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_login = db.user.find_one({"username": payload["id"]})
        return render_template('about.html', user_login=user_login, datasaran=data)
    except(jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return render_template('about.html', datasaran=data)
    
@app.route('/layanan')
def layanan():
    return render_template('layanan.html')

@app.route('/contact')
def contact():
    logged_in = is_logged_in()
    user_info = None
    is_admin = False

    if logged_in:
        token_receive = request.cookies.get("mytoken")
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.user.find_one({"username": payload["id"]})
        if user_info:
            is_admin = user_info.get("role") == "admin"

    return render_template("contact.html", user_info=user_info, is_admin=is_admin, logged_in=logged_in)

@app.route('/mark_as_best_product/<product_id>', methods=['POST'])
def mark_as_best_product(product_id):
    try:
        result = db.product.update_one(
            {'_id': ObjectId(product_id)},
            {'$set': {'is_best_product': True}}
        )
        if result.modified_count > 0:
            return jsonify({'result': 'success', 'msg': 'Product marked as Best Product!'})
        else:
            return jsonify({'result': 'failure', 'msg': 'Product not found or already marked as Best Product.'})
    except Exception as e:
        return jsonify({'result': 'error', 'msg': str(e)})

@app.route('/remove_best_product/<product_id>', methods=['POST'])
def remove_best_product(product_id):
    try:
        result = db.product.update_one(
            {'_id': ObjectId(product_id)},
            {'$unset': {'is_best_product': ""}}
        )
        if result.modified_count > 0:
            return jsonify({'result': 'success', 'msg': 'Best Product status removed!'})
        else:
            return jsonify({'result': 'failure', 'msg': 'Product not found or not marked as Best Product.'})
    except Exception as e:
        return jsonify({'result': 'error', 'msg': str(e)})
    
@app.route('/tambah_artikel', methods=['POST'])
def tambah_artikel():
    from datetime import datetime
    user_info = get_user_info()
    if not user_info or not is_admin(user_info):
        return redirect(url_for("index"))
    nama_receive = request.form.get('nama_give')
    keterangan_gambar_receive = request.form.get('keterangan_gambar')
    keterangan_artikel_receive = request.form.get('keterangan_artikel')
    link_receive = request.form.get('link_give')

    # Get the current date and time
    current_date = datetime.now()

    if 'gambar_artikel' in request.files:
        file = request.files.get('gambar_artikel')
        file_name = secure_filename(file.filename)
        picture_name = f"{file_name.split('.')[0]}[{nama_receive}].{file_name.split('.')[1]}"
        file_path = f'./static/img_artikel/{picture_name}'
        file.save(file_path)
    else:
        picture_name = 'default.jpg'

    doc = {
        'nama_artikel': nama_receive,
        'keterangan_gambar': keterangan_gambar_receive,
        'keterangan_artikel': keterangan_artikel_receive,
        'gambar_artikel': picture_name,
        'tanggal_upload': current_date,
        'link' : link_receive,
    }
    db.articles.insert_one(doc)

    return redirect(url_for('artikel'))

@app.route('/artikel')
def artikel():
    articles = list(db.articles.find().sort('_id', -1))
    return render_template('artikel.html', articles=articles)


# Route for updating an article
@app.route('/update_artikel/<article_id>', methods=['POST'])
def update_artikel(article_id):
    user_info = get_user_info()
    if not user_info or not is_admin(user_info):
        return redirect(url_for("index"))
    
    # Retrieve the existing article
    article = db.articles.find_one({'_id': ObjectId(article_id)})

    if article:
        # Get updated data from form
        nama_receive = request.form.get('nama_give')
        keterangan_gambar_receive = request.form.get('keterangan_gambar')
        keterangan_artikel_receive = request.form.get('keterangan_artikel')
        link_receive = request.form.get('link_give')

        # Check if a new image is uploaded
        if 'gambar_artikel' in request.files and request.files['gambar_artikel'].filename != '':
            file = request.files.get('gambar_artikel')
            file_name = secure_filename(file.filename)
            picture_name = f"{file_name.split('.')[0]}[{nama_receive}].{file_name.split('.')[1]}"
            file_path = f'./static/img_artikel/{picture_name}'
            file.save(file_path)
        else:
            picture_name = article['gambar_artikel']  # Keep old image if not changed

        # Update the article in the database
        db.articles.update_one(
            {'_id': ObjectId(article_id)},
            {
                '$set': {
                    'nama_artikel': nama_receive,
                    'keterangan_gambar': keterangan_gambar_receive,
                    'keterangan_artikel': keterangan_artikel_receive,
                    'gambar_artikel': picture_name,
                    'link': link_receive
                }
            }
        )

        return redirect(url_for('artikel'))
    else:
        return "Artikel tidak ditemukan."


@app.route('/hapus_artikel/<article_id>', methods=['GET'])
def hapus_artikel(article_id):
    user_info = get_user_info()
    if not user_info or not is_admin(user_info):
        return redirect(url_for("index"))
    
    article = db.articles.find_one({'_id': ObjectId(article_id)})

    if article:
        db.articles.delete_one({'_id': ObjectId(article_id)})

        image_path = os.path.join("static", "img_artikel", article['gambar_artikel'])
        if os.path.exists(image_path):
            os.remove(image_path)

        return redirect(url_for('artikel'))
    else:
        return "Artikel tidak ditemukan."

@app.route('/artikel/<article_id>')
def artikel_detail(article_id):
    article = db.articles.find_one({'_id': ObjectId(article_id)})

    if article:
        return render_template('detail_artikel.html', article=article)
    else:
        return "Artikel tidak ditemukan."

@app.route('/blog')
def blog():
    per_page = 5  # Number of articles per page
    page = int(request.args.get('page', 1))  # Get current page from query parameter, default to 1

    total_articles = db.articles.count_documents({})  # Total number of articles
    total_pages = (total_articles + per_page - 1) // per_page  # Calculate total pages

    # Fetch articles for the current page
    articles = list(
        db.articles.find()
        .sort('_id', -1)
        .skip((page - 1) * per_page)
        .limit(per_page)
    )
    for article in articles:
        article['keterangan_artikel_truncated'] = truncate_html(article['keterangan_artikel'], 10)

    return render_template(
        'daftarartikel.html',
        articles=articles,
        page=page,
        total_pages=total_pages
    )


def truncate_html(html, word_limit):
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text().split()
    if len(text) > word_limit:
        truncated_text = ' '.join(text[:word_limit]) + '...'
        return truncated_text
    return html


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)