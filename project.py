from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, redirect, url_for
from PIL import Image
import io


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data_base.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
current_user = None
db.create_all()


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    avatar = db.Column(db.String(80), unique=False, nullable=True)

    def __repr__(self):
        return '<User {} {} {} {}>'.format(self.id, self.username, self.email, self.password)

    def __getitem__(self, item):
        if item == 'id':
            return self.id
        elif item == 'username':
            return self.username
        elif item == 'email':
            return self.email
        elif item == 'password':
            return self.password


class Blog(db.Model):
    __tablename__ = 'blog'
    id = db.Column(db.Integer, primary_key=True)
    header = db.Column(db.String, unique=False, nullable=False)
    text = db.Column(db.String, unique=False, nullable=False)
    picture = db.Column(db.String, unique=False, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('blogs', lazy='subquery'))

    def __repr__(self):
        return '<Blog {} {} {} {}>'.format(self.id, self.header, self.text, self.user_id)

    def __getitem__(self, item):
        if item == 'id':
            return self.id
        elif item == 'header':
            return self.header
        elif item == 'text':
            return self.text
        elif item == 'user_id':
            return self.user_id


@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    global current_user
    if request.method == 'GET':
        return render_template('sign_in.html')
    elif request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        try:
            if user['password'] != request.form['password']:
                return render_template('sign_in.html', message='incorrect login or password, try again')
        except TypeError:
            return render_template('sign_in.html', message='incorrect login or password, try again')
        current_user = user
        return redirect('/')


@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    global current_user
    if request.method == 'GET':
        return render_template('sign_up.html')
    elif request.method == 'POST':
        if not User.query.filter_by(username=request.form['username']).first() and not User.query.filter_by(email=request.form['email']).first():
            if request.files.get('photo'):
                user = User(username=request.form['username'],
                            email=request.form['email'],
                            password=request.form['password'],
                            avatar=request.form['username'] + '.PNG'
                            )
                f_data = request.files['photo'].read()
                f = Image.open(io.BytesIO(f_data))
                f.save('static/pictures_avatar' + request.form['username']+'.PNG', 'PNG')

            else:
                user = User(username=request.form['username'],
                            email=request.form['email'],
                            password=request.form['password'])
            db.session.add(user)
            db.session.commit()
            current_user = user

            return redirect('/')
        return render_template('sign_up.html', message='Such username or email is already taken')


@app.route('/create_blog', methods=['GET', 'POST'])
def create_blog():
    if request.method == 'GET':
        return render_template('create_blog.html')
    elif request.method == 'POST':
        blog = Blog(header=request.form['header'],
                    text=request.form['text'],
                    )
        print(current_user)
        current_user.blogs.append(blog)
        print(current_user.blogs[0], current_user.blogs[1])
        db.session.commit()
        return redirect('/')


@app.route('/')
def main():
    return 'Hello'


db.create_all()

if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')