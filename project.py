from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, redirect, url_for
from PIL import Image
import io
import datetime
import os


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
        return '<User {} {} {} {} {}>'.format(self.id, self.username, self.email, self.password, self.avatar)

    def __getitem__(self, item):
        if item == 'id':
            return self.id
        elif item == 'username':
            return self.username
        elif item == 'email':
            return self.email
        elif item == 'password':
            return self.password
        elif item == 'avatar':
            return self.avatar


class Blog(db.Model):
    __tablename__ = 'blog'
    id = db.Column(db.Integer, primary_key=True)
    header = db.Column(db.String, unique=False, nullable=False)
    text = db.Column(db.String, unique=False, nullable=False)
    picture = db.Column(db.String, unique=False, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('blogs', lazy=True))
    likes = db.Column(db.Integer, unique=False, nullable=True, default=0)

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
        elif item == 'picture':
            return self.picture


class Liked(db.Model):
    __tablename__ = 'liked'
    id = db.Column(db.Integer, primary_key=True)
    blog_id = db.Column(db.Integer, unique=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('liked'), lazy=True)

    def __repr__(self):
        return '<Like id: {} user_id: {} blog_id: {}>'.format(self.id, self.user_id, self.blog_id)

    def __getitem__(self, item):
        if item == 'id':
            return self.id
        elif item == 'blog_id':
            return self.blog_id
        elif item == 'user.id':
            return self.user.id


class Subscribe(db.Model):
    __tablename__ = 'subscribe'
    id = db.Column(db.Integer, primary_key=True)
    subscribe_username = db.Column(db.String, unique=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('subscribes', lazy=True))

    def __repr__(self):
        return '<Subscribe id: {} subscriber: {} subscribe to : {}>'.format(self.id, self.user, self.subscribe_username)


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
                f.save('static/pictures_avatar/' + request.form['username']+'.PNG', 'PNG')

            else:
                user = User(username=request.form['username'],
                            email=request.form['email'],
                            password=request.form['password'],
                            avatar=request.form['username'] + '.PNG'
                            )
                f = Image.open('standart_avatar.PNG')
                f.save('static/pictures_avatar/' + request.form['username']+'.PNG', 'PNG')
            db.session.add(user)
            db.session.commit()
            current_user = user
            print(current_user)   # НЕ СТИРАТЬ!!! БЕЗ ЭТОГО НЕ РАБОТАЕТ, Я НЕ ЗНАЮ ПОЧЕМУ, не работает,
            # когда, создавая новый аккаунт, пытаюсь зайти в personal area

            return redirect('/')
        return render_template('sign_up.html', message='Such username or email is already taken')


@app.route('/create_blog', methods=['GET', 'POST'])
def create_blog():
    if request.method == 'GET':
        return render_template('create_blog.html')
    elif request.method == 'POST':
        if not request.files.get('picture'):

            blog = Blog(header=request.form['header'],
                        text=request.form['text'],
                        )
            user = User.query.filter_by(username=current_user['username']).first()
            user.blogs.append(blog)
            db.session.commit()
            return redirect('/')
        else:
            blog = Blog(header=request.form['header'],
                        text=request.form['text'],
                        )

            user = User.query.filter_by(username=current_user['username']).first()
            user.blogs.append(blog)
            db.session.commit()
            blog.picture = str(blog['id']) + '.PNG'

            f_data = request.files.get('picture')
            f = Image.open(io.BytesIO(f_data.read()))
            f.save('static/pictures_blogs/' + blog.picture, 'PNG')
            db.session.commit()
            return redirect('/')


@app.route('/')
def start():
    return redirect('/main')


"""ЗАВЕРШИТЬ ПОЗЖЕ"""


def like_blog(blog_id, where, username=None):
    blog = Blog.query.filter_by(id=blog_id).first()
    if not current_user:
        return redirect('/sign_in')
    if request.args.get('vote'):
        user = User.query.filter_by(username=current_user.username).first()
        my_like = Liked.query.filter_by(user_id=user.id, blog_id=blog_id).first()

        if my_like:
            blog.likes -= 1
            db.session.delete(my_like)
            db.session.commit()
            if username:
                return redirect('/' + where + '/' + username[0])
            return redirect('/' + where)

        like = Liked(blog_id=blog_id)
        user.liked.append(like)
        blog.likes += 1
        db.session.commit()
        if username:
            return redirect('/' + where + '/' + username[0])
        return redirect('/' + where)


@app.route('/like_blog/<string:where>/<int:blog_id>', methods=['POST', 'GET'])
@app.route('/like_blog/<string:where>/<string:username>/<int:blog_id>', methods=['POST', 'GET'])
def like_blog(blog_id, where, username=None):
    blog = Blog.query.filter_by(id=blog_id).first()
    if not current_user:
        return redirect('/sign_in')
    if request.args.get('vote'):
        user = User.query.filter_by(username=current_user.username).first()
        my_like = Liked.query.filter_by(user_id=user.id, blog_id=blog_id).first()

        if my_like:
            blog.likes -= 1
            db.session.delete(my_like)
            db.session.commit()
            if username:
                return redirect('/' + where + '/' + username)
            return redirect('/' + where)
        like = Liked(blog_id=blog_id)
        user.liked.append(like)
        blog.likes += 1
        db.session.commit()
        if username:
            return redirect('/' + where + '/' + username)
        return redirect('/' + where)


@app.route('/subscribe/<string:username>', methods=['GET', 'POST'])
def subscribe(username):
    subscriber = User.query.filter_by(username=current_user.username).first()
    sub = Subscribe(subscribe_username=username)
    subscriber.subscribes.append(sub)
    db.session.commit()
    return redirect('/personal_area/' + username)


@app.route('/unsubscribe/<string:username>', methods=['GET', 'POST'])
def unsubscribe(username):
    subscriber = User.query.filter_by(username=current_user.username).first()
    sub = Subscribe.query.filter_by(subscribe_username=username, user_id=subscriber.id).first()
    db.session.delete(sub)
    db.session.commit()
    return redirect('/personal_area/' + username)


@app.route('/main')
def main():
    return render_template('main.html', blogs=Blog.query.all()[-1::-1], all_users=User.query)


@app.route('/personal_area/<string:who>', methods=['GET', 'POST'])
@app.route('/personal_area/<string:islikedblogs>/<string:who>', methods=['GET', 'POST'])
def personal_area(who, islikedblogs=''):
    if who == 'me':

        if current_user != None:
            if request.method == 'GET':
                user = User.query.filter_by(username=current_user['username']).first()

                return render_template('personal_area.html', user=user,
                                       img='/static/pictures_avatar/' + user['avatar'], isMe=True, liked=user.liked,
                                       Blog=Blog, isLikedBlogs=islikedblogs)

            elif request.method == 'POST':

                user = User.query.filter_by(username=current_user['username']).first()
                if request.files.get('photo'):
                    f_data = request.files.get('photo')

                    f = Image.open(io.BytesIO(f_data.read()))

                    old_avatar = user.avatar

                    date = datetime.datetime.today().strftime("%Y-%m-%d,%H_%M_%S")
                    user.avatar = user['username'] + date + '.PNG'
                    db.session.commit()
                    f.save('static/pictures_avatar/' + user['avatar'], 'PNG')
                    os.remove('static/pictures_avatar/' + old_avatar)
                    return render_template('personal_area.html', user=user,
                                           img='/static/pictures_avatar/' + user['avatar'], isMe=True,
                                           liked=user.liked, Blog=Blog, isLikedBlogs=islikedblogs)
                return render_template('personal_area.html', user=user,
                                           img='/static/pictures_avatar/' + user['avatar'], isMe=True,
                                       liked=user.liked, Blog=Blog, isLikedBlogs=islikedblogs)
        return redirect('/sign_in')
    else:
        if request.method == 'GET':
            # перенос на личный профиль
            if current_user and who == User.query.filter_by(username=current_user['username']).first().username:
                return redirect('/personal_area/me')

            user = User.query.filter_by(username=who).first()

            if not current_user:
                return render_template('personal_area.html', user=user,
                                   img='/static/pictures_avatar/' + user['avatar'], current_user=current_user,
                                       liked=user.liked, Blog=Blog, isLikedBlogs=islikedblogs)
            user2 = User.query.filter_by(username=current_user.username).first()
            if Subscribe.query.filter_by(subscribe_username=user.username, user_id=user2.id).first() in user2.subscribes:
                unsubscribe = True
            else:
                unsubscribe = False

            return render_template('personal_area.html', user=user,
                                   img='/static/pictures_avatar/' + user['avatar'], current_user=current_user,
                                   unsubscribe=unsubscribe, liked=user.liked, Blog=Blog, isLikedBlogs=islikedblogs)


db.create_all()


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
