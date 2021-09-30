import sqlite3
from flask import Flask, render_template, request, redirect, session, url_for

# 画像アップ用
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# 秘密鍵
app.secret_key="hamanaka"

# 画像アップ用
UPLOAD_FOLDER = "./static/img"
ALLOWED_EXTENSIONS = set(['png','jpg','jpeg','gif','heic'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# -------------- この下から書く -----------------

#画像アップ
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/upload/<where>", methods=["POST"])
def upload(where):
    if "user_id" in session:
        
        # ファイルがなかった場合の処理
        if "img_file" not in request.files:
            print("ファイルがありません")
            return redirect(request.url)

        # データの取り出し
        img_file=request.files["img_file"]

        # ファイル名がなかった場合の処理
        if img_file.filename == "":
            print("ファイル名がみつかりません")
            return redirect(request.url)

        # ファイルのチェック
        if img_file and allowed_file(img_file.filename):
            filename = secure_filename(img_file.filename)
            img_url = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            img_file.save(img_url)
        else:
            return redirect(request.url)

        if where=="home":
            user_id=session["user_id"]
            # ---- データベースに接続 ----
            conn = sqlite3.connect("aeta.db")
            c = conn.cursor()
            c.execute("UPDATE user SET image=? WHERE id=?", (filename, user_id))
            conn.commit()
            c.close()
            # ---- データベース接続終了 ----
            return redirect("/home")

        elif where=="add":
            return render_template("addcard.html",filename=filename)

        elif where=="edit":
            id=request.form.get("edit_id")
            # ---- データベースに接続 ----
            conn = sqlite3.connect("aeta.db")
            c = conn.cursor()
            c.execute("UPDATE aeta SET image=? WHERE id=?", (filename, id))
            conn.commit()
            c.close()
            # ---- データベース接続終了 ----
            
            return redirect(url_for("edit_get",id=id))
        else:
            return redirect("/home")
    else:
        return render_template("regist.html")


# ユーザー登録ページの表示
@app.route("/regist", methods=["GET"])
def regist_get():
    if "user_id" in session:
        return redirect("/home")
    else:
        return render_template("regist.html")

# ユーザー登録
@app.route("/regist",methods=["POST"])
def regist_post():
    name = request.form.get("username")
    pw = request.form.get("password")
    img = "me.jpg"
    # ---- データベースに接続 ----
    conn = sqlite3.connect("aeta.db")
    c = conn.cursor()
    c.execute("INSERT INTO user VALUES(null,?,?,?)", (name, pw, img))
    conn.commit()
    c.close()
    # ---- データベース接続終了 ----
    return redirect("/")

# トップページ（ログインページ）の表示
@app.route("/", methods=["GET"])
def top_get():
    if "user_id" in session:
        return redirect("/home")
    else:
        return render_template("top.html")

# ログイン処理
@app.route("/", methods=["POST"])
def top_post():
    name = request.form.get("username")
    pw = request.form.get("password")
    # ---- データベースに接続 ----
    conn = sqlite3.connect("aeta.db")
    c = conn.cursor()
    c.execute("SELECT id FROM user WHERE name=? AND password=?",(name, pw))
    user_id=c.fetchone()
    conn.commit()
    c.close()
    # ---- データベース接続終了 ----
    if user_id is None:
        return render_template("top.html")
    else:
        session["user_id"] = user_id[0]
        return redirect("/home")

# ログアウト
@app.route("/logout", methods=["GET"])
def logout():
    session.pop("user_id", None)
    return redirect("/")

# aeta登録画面の表示
@app.route("/addcard", methods=["GET"])
def add_get():
    # ログイン判定
    if "user_id" in session:
        return render_template("addcard.html")
    else:
        return redirect("/")

# スコア計算用関数
def count_score(data):
    """
    aetaテーブルから取り出した一行から
    スコアをカウントし、テーブルを更新する
    """
    print(data)
    id = data[0]
    # タプルをリストに変える
    l = list(data) 
    # リストから空欄を取り除く
    realdata= [x for x in l if x != ""]
    # id, user_id, スコア, フラグの分は除く
    score = len(realdata) - 5
    # ---- データベースに接続 ----
    conn = sqlite3.connect("aeta.db")
    c = conn.cursor()
    c.execute("UPDATE aeta SET score = ? WHERE id = ?", (score, id))
    conn.commit()
    c.close()
    # ---- データベース接続終了 ----

# nakayoshi判定用関数
def nakayoshi_judge(user_id):
    # ---- データベースに接続 ----
    conn = sqlite3.connect("aeta.db")
    c = conn.cursor()
    c.execute("SELECT id,score FROM aeta WHERE user_id=?",(user_id,))
    scorelist=[]
    for row in c.fetchall():
        scorelist.append({"id":row[0],"score":row[1]})
    # scorelistリストからスコア値を取り出して判定
    for i in scorelist:
        id = i.get("id")
        score = i.get("score")
        if score >= 10:
            c.execute("UPDATE aeta SET nakayoshi_FLG = 1 WHERE id = ?", (id,))
        elif score >= 6 and score < 10:
            c.execute("UPDATE aeta SET misiri_FLG = 1 WHERE id = ?", (id,))
        else:
            c.execute("UPDATE aeta SET misiri_FLG = 0 ,nakayoshi_FLG = 0 WHERE id = ?", (id,))

    conn.commit()
    c.close()
    # ---- データベース接続終了 ----

@app.route("/addcard", methods=["POST"])
def add_post():
    #ログイン判定
    if "user_id" in session:
        user_id = session["user_id"]
        name = request.form.get("name")
        image = request.form.get("image")
        if image =="":
            image = "aeta.jpg"
        birthday_m = request.form.get("birthday_m")
        birthday_d = request.form.get("birthday_d")
        age = request.form.get("age")
        residence = request.form.get("residence")
        birthplace = request.form.get("birthplace")
        others = request.form.get("others")
        day = request.form.get("day")
        place = request.form.get("place")
        contents = request.form.get("contents")

        # ---- データベースに接続 ----
        conn = sqlite3.connect("aeta.db")
        c = conn.cursor()
        c.execute("INSERT INTO aeta VALUES(null,?,?,?,?,?,?,?,?,?,0,0,0)",\
            (user_id, name, image, birthday_m, birthday_d, age, residence, birthplace, others))
        conn.commit()
        c.execute("SELECT * FROM aeta WHERE user_id=? AND name=?",(user_id, name)) #確認：同姓同名の人を登録しようとすると多分エラーになる
        aeta_row=c.fetchone()
        c.execute("INSERT INTO situation VALUES(null,?,?,?,?)",(aeta_row[0], day, place, contents))
        conn.commit()
        c.close()
        # ---- データベース接続終了 ----

        count_score(aeta_row) #点数計算
        return redirect("/home")
    else:
        return redirect("/")


# ホーム画面表示
@app.route("/home")
def home():
    # ログイン判定
    if "user_id" in session:
        user_id = session["user_id"]
        nakayoshi_judge(user_id)
        # ---- データベースに接続 ----
        conn = sqlite3.connect("aeta.db")
        c = conn.cursor()
        c.execute("SELECT user.image, count(aeta.id), sum(aeta.nakayoshi_FLG) \
            FROM user LEFT JOIN aeta ON user.id=aeta.user_id WHERE user.id=?;",(user_id,))
        user_data = c.fetchone()
        c.execute("SELECT aeta.id, aeta.image, aeta.name, situation.day FROM aeta \
            JOIN situation ON aeta.id=situation.aeta_id WHERE aeta.user_id=? \
                GROUP BY aeta.id order by max(situation.day) DESC",(user_id,))
        aeta_list=[]
        for row in c.fetchall():
            aeta_list.append({"id":row[0],"image":row[1],"name":row[2],"day":row[3]})
        c.close()
        # ---- データベース接続終了 ----
        
        # aeta登録人数が0の時
        if not aeta_list:
            l = list(user_data)
            l[2] = 0
            aeta_none = tuple(l)
            return render_template("home.html",user_data = aeta_none, aeta_list = aeta_list)

        return render_template("home.html",user_data = user_data, aeta_list = aeta_list)
    else:
        return redirect("/")

# aeta参照画面の表示
@app.route("/card/<int:id>")
def show_card(id):
    # ログイン判定
    if "user_id" in session:
        # ---- データベースに接続 ----
        conn = sqlite3.connect("aeta.db")
        c = conn.cursor()
        c.execute("SELECT name, image, birthday_m, birthday_d, age, birthplace, residence, others, id, nakayoshi_FLG\
            FROM aeta WHERE id=?;",(id,))
        aeta_data = c.fetchone()
        c.execute("SELECT id, day, place, contents FROM situation WHERE aeta_id=? ORDER BY day DESC;",(id,))
        scene_data = []
        for row in c.fetchall():
            scene_data.append({"scene_id":row[0],"day":row[1],"place":row[2],"contents":row[3]})
        c.close()
        # ---- データベース接続終了 ----
        return render_template("card.html",aeta_data=aeta_data,scene_data=scene_data)
    else:
        return redirect("/")
        
# シーン追加によるscore加算
def add_score(id,p):
    # ---- データベースに接続 ----
    conn = sqlite3.connect("aeta.db")
    c = conn.cursor()
    c.execute("SELECT score FROM aeta WHERE id=?",(id,))
    score = c.fetchone()[0]
    if p == 1:
        score += 1
    else:
        score -= 1
    c.execute("UPDATE aeta SET score = ? WHERE id = ?", (score, id))
    conn.commit()
    c.close()
    # ---- データベース接続終了 ----

# シーン追加
@app.route("/situation", methods=["POST"])
def add_situation():
    if "user_id" in session:
        id = request.form.get("id")
        day = request.form.get("day")
        place = request.form.get("place")
        contents =request.form.get("contents")
        # ---- データベースに接続 ----
        conn = sqlite3.connect("aeta.db")
        c = conn.cursor()
        c.execute("INSERT INTO situation VALUES(null,?,?,?,?)",(id, day, place, contents))
        conn.commit()
        c.close()
        # ---- データベース接続終了 ----
        add_score(id,p=1)
        return redirect(url_for("show_card",id=id))
    else:
        return redirect("/")

# シーンの削除
@app.route("/del", methods=["POST"])
def delete_situation():
    if "user_id" in session:
        aeta_id=request.form.get("aeta_id")
        del_id=request.form.get("del_id")
        # ---- データベースに接続 ----
        conn = sqlite3.connect("aeta.db")
        c = conn.cursor()
        c.execute("DELETE FROM situation WHERE id=?",(del_id,))
        conn.commit()
        c.close()
        # ---- データベース接続終了 ----
        add_score(aeta_id,p=2)
        return redirect(url_for("show_card",id=aeta_id))
    else:
        return redirect("/")
    
# cardの編集
@app.route("/card/<int:id>/edit", methods=["GET"])
def edit_get(id):
    # ログイン判定
    if "user_id" in session:
        # ---- データベースに接続 ----
        conn = sqlite3.connect("aeta.db")
        c = conn.cursor()
        c.execute("SELECT name, image, birthday_m, birthday_d, age, birthplace, residence, others, id, nakayoshi_FLG\
            FROM aeta WHERE id=?",(id,))
        edit_data = c.fetchone()
        c.close()
        # ---- データベース接続終了 ----
        return render_template("editcard.html",edit_data=edit_data)
    else:
        return redirect("/")

@app.route("/editcard", methods=["POST"])
def edit_post():
    #ログイン判定
    if "user_id" in session:
        aeta_id = request.form.get("id")
        name = request.form.get("name")
        image = request.form.get("image")
        birthday_m = request.form.get("birthday_m")
        birthday_d = request.form.get("birthday_d")
        age = request.form.get("age")
        residence = request.form.get("residence")
        birthplace = request.form.get("birthplace")
        others = request.form.get("others")

        # ---- データベースに接続 ----
        conn = sqlite3.connect("aeta.db")
        c = conn.cursor()
        c.execute("UPDATE aeta SET name=?, image=?, birthday_m=?, birthday_d=?,\
            age=?, residence=?, birthplace=?, others=? WHERE id=?",\
            (name, image, birthday_m, birthday_d, age, residence, birthplace, others, aeta_id))
        conn.commit()
        c.execute("SELECT * FROM aeta WHERE id=?",(aeta_id,))
        aeta_row=c.fetchone()
        c.close()
        # ---- データベース接続終了 ----
        count_score(aeta_row) #点数計算
        return redirect(url_for("show_card",id=aeta_id))
    else:
        return redirect("/")


# -------------- この上までに書く -----------------

if __name__ == "__main__":
    app.run(debug=True) 
    # 確認：リリースするときはdebug=Trueを消す？