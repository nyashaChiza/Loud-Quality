from flask import Flask, flash, session, render_template, request, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename
from methods import File_handler


app = Flask(__name__)

app.config['ALLOWED_EXTENSIONS'] = [ 'png', 'jpg', 'jpeg','gif','jfif''zip','rar','rar4' ]
app.config['ART_FOLDER'] = "static/Uploads/ART"
app.config['FIlE_FOLDER'] = "static/Uploads/FILES"
app.config['SINGLES_FOLDER'] = "static/Uploads/FILES/SINGLES"
app.config['ALBUMS_FOLDER'] = "static/Uploads/FILES/ALBUMS"
app.config['SECRET_KEY'] = "this_is_my_secret_key"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///Content.db"


db = SQLAlchemy(app)

#-----------------------------------------------------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    First_Name  = db.Column(db.String(50))
    Last_Name  = db.Column(db.String(50))
    Status  = db.Column(db.String(50))
    User_Type  = db.Column(db.String(50))
    Username  = db.Column(db.String(50))
    Password  = db.Column(db.String(50))
    Email  = db.Column(db.String(50))
    Phone_Number = db.Column(db.String(50))

class Content(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    Project_Name  = db.Column(db.String(50))
    Project_Type  = db.Column(db.String(50))
    Artist_Name  = db.Column(db.String(50))
    Year = db.Column(db.Integer())
    User_id = db.Column(db.Integer())
    Description  = db.Column(db.String(375)) 
    Genre  = db.Column(db.String(50)) 
    Image_Name  = db.Column(db.String(50)) 
    File_Name  = db.Column(db.String(50)) 
    Views = db.Column(db.Integer(),default= 0)
    Downloads = db.Column(db.Integer(),default= 0)

class Image(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    Image_Name  = db.Column(db.String(50)) 
    Project_id  = db.Column(db.Integer())

class File(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    File_Name  = db.Column(db.String(50)) 
    Project_id  = db.Column(db.Integer())
    Downloads = db.Column(db.Integer())

#-----------------------------------------------------------------------
def auth(auth_id,auth_pass):
    login_Object =  User.query.filter_by(Email = auth_id,Password = auth_pass).first()
    if login_Object  == None:
            alert = "login-failed" 
            return render_template('Account/account.html',alert = alert)
    
    elif login_Object.Status == "Logged_In":
            alert = "in_use" 
            return render_template('Account/account.html',alert = alert)

    else:
            session['name'] = login_Object.Username
            session['user_id'] = login_Object.id
            login_Object.Status = "Logged_In"
            db.session.add(login_Object)
            db.session.commit()
            return render_template('Account/Manage/manage.html', name = session['name'], user_id = session['user_id'])



#-----------------------------------------------------------------------
@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    pagination = Content.query.order_by(Content.id.desc()).paginate(
    page, per_page= 6,error_out=False)
    
    content =  Content.query.all()
    return render_template("Music/home.html", content = content, pagination=pagination)

@app.route('/test') 
def test():
    session['test'] = session['test'] + 1
    return render_template("test.html",data = session['test'])

@app.route('/news')
def news():
    y= ["a","b","a","b","a","b"]
    return render_template("News/news.html",y= y)

@app.route("/newsDetails/<string:id>")
def newsDetails(id):
     return render_template('News/details.html')

@app.route("/details/<string:id>")
def details(id):
    item =  Content.query.filter_by(id = id).first()
    if item.Views == None:
        item.Views = 1
    else:
        item.Views = item.Views+1
    db.session.add(item)
    db.session.commit()
    return render_template('Music/details.html', item = item)

@app.route('/latest')
def latest():
    c= ["a","b","b"]
    return render_template('latest.html',c= c)

@app.route('/account')
def account():
    return render_template('Account/account.html')


@app.route('/upload/<string:id>')
def upload(id):
    return render_template('Account/Manage/upload.html', id = id )

@app.route('/sign_up_process',methods = ['POST','GET'])
def sign_up_process():
    if request.method == 'POST':
        
            Name = request.form['Name'].capitalize()
            Surname = request.form['Surname'].capitalize()
            Username = request.form['Username'].capitalize()
            Email = request.form['Email']
            Password = generate_password_hash(request.form['Password'])
            Phone_Number = request.form['Phone_Number']
            User_Type = "Client"
            Status = "Logged_Out"
        

            user = User(First_Name = Name, Last_Name = Surname, Username = Username, Password = Password,
            Phone_Number = Phone_Number, Email = Email)
            
            db.session.add(user)
            
    
            db.session.commit()

            alert = "signup-success"
    else:
        alert = "signup-failed"
    

    return render_template('Account/account.html',alert = alert)

@app.route('/edit_process',methods = ['POST','GET'])
def edit_process():
    if request.method == 'POST':
        User_id = request.form['User_id']
        User_data =  User.query.filter_by(id = User_id).first()
       
        User_data.First_Name = request.form['Name'].capitalize()
        User_data.Last_Name = request.form['Surname'].capitalize()
        User_data.Username = request.form['Username'].capitalize()
        User_data.Email = request.form['Email']
        User_data.Password = request.form['Password']
        User_data.Phone_Number = request.form['Phone_Number']


        #user = User(First_Name = Name, Last_Name = Surname, Username = Username, Password = Password,
        #Phone_Number = Phone_Number, Email = Email)

        db.session.add(User_data)
        db.session.commit()

        alert = "update-success"
    
    else:
        alert = "update-failed"

    return render_template('Account/Manage/manage.html',alert = alert)


@app.route('/sign_in', methods = ['POST','GET'])
def sign_in():
    if request.method == 'POST':
        
        return auth(request.form['Email'], request.form['Password'])
    

@app.route('/viewContent/<string:id>')
def viewContent(id):
    content = Content.query.filter_by(User_id = id).all()
    print(content)
    if content == []:
        alert = "empty"
    else:
        alert = "ok"
    return render_template('Account/Manage/viewContent.html',content = content, alert= alert,id =id)

@app.route('/manage',methods = ['POST','GET'])
def manage():
    if session['user_id'] == None or session['name'] == None:
        return account()
    return render_template('Account/Manage/manage.html')


@app.route('/search',methods = ['POST','GET'])
def search():
    
    
    if request.method == 'POST':
        key = request.form['key']

        key1 =  Content.query.filter_by(Artist_Name = key).all()
        key2 =  Content.query.filter_by(Project_Name = key).all()
        keys = key1 + key2   
       
        if keys == []:
            alert = "none"
        else:
            alert = "ok"
        
    return render_template('Misc/search.html',key= key, keys = keys, alert = alert )

@app.route('/searches/<string:key>')
def searches(key):
    key1 =  Content.query.filter_by(Artist_Name = key).all()
    key2 =  Content.query.filter_by(Genre = key).all()
    keys = key1 +key2
    return render_template('Misc/searches.html',key= key, keys = keys )

@app.route('/edit/<string:id>',methods = ['POST','GET'])
def edit(id):
    User_data =  User.query.filter_by(id = id).first()
    return render_template('Account/Manage/edit.html', User_data = User_data)

@app.route("/download/<string:id>")
def download(id):
    item = Content.query.filter_by(id = id).first()
   
    if item.Downloads == None:
        item.Downloads = 1
    else:
        item.Downloads = item.Downloads+1
    db.session.add(item)
    db.session.commit()
    
    download_file = item.File_Name
    return send_file(download_file, as_attachment = True) 

@app.route('/upload_process', methods = ['POST','GET'])
def upload_process():
    if request.method == 'POST' and request.files:
        Project_Name = request.form['Project_Name'].lower()
        Project_Type = request.form['Project_Type'].lower()
        Artist_Name = request.form['Artist_Name'].lower()
        Year = request.form['Year']
        Description = request.form['Description']
        Genre = request.form['Genre'].lower()
        User_id = request.form['User_id']
        
        
        Art  = File_handler(request.files['Image'],app.config['ART_FOLDER'])
        if Project_Type == 'Single':
            Files  = File_handler(request.files['File'],app.config['SINGLES_FOLDER'])
        else:
            Files  = File_handler(request.files['File'],app.config['ALBUMS_FOLDER'])
        
        if (Art[0],Files[0]) == (True,True):

            request.files['Image'].save(os.path.join("static/Uploads/ART", Art[2]))
            if Project_Type == 'Single':
                request.files['File'].save(os.path.join(app.config['SINGLES_FOLDER'], Files[2]))
            else:
                request.files['File'].save(os.path.join(app.config['ALBUMS_FOLDER'], Files[2]))

            content = Content(Project_Name = Project_Name, Project_Type = Project_Type, Artist_Name  = Artist_Name,
            Year = Year, User_id = User_id, Description = Description, Genre = Genre, Image_Name = Art[1], File_Name = Files[1]
            )
           
            db.session.add(content)

            content_search = Content.query.filter_by(Project_Name = Project_Name, Project_Type = Project_Type, Artist_Name  = Artist_Name,
            Year = Year, User_id = User_id, Description = Description, Genre = Genre, Image_Name = Art[1], File_Name = Files[1]).first()
 
            Art = Image(Image_Name = Art[1], Project_id = content_search.id)
            file = File(File_Name = Files[1], Project_id = content_search.id)
            
            
            db.session.add(Art)
            db.session.add(file)
            
            db.session.commit()
            status = "success"
        else:
            status = "failed"
    
        

    else:   
        status = "failed"

    return render_template('Account/Manage/manage.html', status = status)

@app.route('/signup')
def signup():
    return render_template('Account/signup.html')

@app.route('/logout')
def logout():
    login_Object =  User.query.filter_by(id = session['user_id']).first()
    login_Object.Status =  "Logged_Out"
    db.session.add(login_Object)
    db.session.commit()
    session.pop('name', None)
    session.pop('user_id', None)
    return account()

@app.route('/about')
def about():
    return render_template('Misc/about.html')

@app.route('/albums')
def albums():
    v= ["a","b","a","b","a","b"]
    return render_template('Music/albums.html',v = v)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('Misc/not_found.html'), 404

if __name__ == '__main__':
    app.run(debug=True,host = '0.0.0.0')
