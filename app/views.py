from flask import render_template, flash, redirect, session, url_for, request, g
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db, lm, oid
from .forms import LoginForm
from .models import Create_map,update_all_data

import folium
import utm
import pandas as pd
from IPython.display import HTML

@app.route('/') #creates mapping form URL / and URL /index to this function
@app.route('/index')
#@login_required for now no login required
def index():
   user = g.user
   posts = [  # fake array of posts
        { 
            'author': {'nickname': 'Andriy'}, 
            'body': 'Beautiful day in Ukraine!' 
        },
        { 
            'author': {'nickname': 'Kristina'}, 
            'body': 'Zootopia is so cool!' 
        }
    ]
   Create_map()
   return render_template('index.html',
                          title='Home',
                          user=user,
                          posts=posts) #takes pre template name with variable list and renders the template

@app.before_request
def before_request():
    g.user = None
    if 'openid' in session:
        g.user = User.query.filter_by(openid=session['openid']).first()

@app.route('/login', methods=['GET','POST'])
@oid.loginhandler
def login():
    print("Into loginhandler")
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index'))    
    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        openid = request.form.get('openid')
        return oid.try_login(openid, ask_for=['nickname', 'email']) #https://me.yahoo.com/a/B5Aic_cdr_QeLSuVBZbqPffbYXZ4GH0Cgxktan8-
    return render_template('login.html', 
                           title='Sign In',
                           form=form,
                           next=oid.get_next_url(),
                           providers=app.config['OPENID_PROVIDERS'])

@oid.after_login
def after_login(resp):
    print("Into after login")
    if resp.email is None or resp.email == "":
        flash('Invalid login. Please try again.')
        return redirect(url_for('login'))
    user = User.query.filter_by(email=resp.email).first()
    if user is None:
        nickname = resp.nickname
        if nickname is None or nickname == "":
            nickname = resp.email.split('@')[0]
        user = User(nickname=nickname, email=resp.email)
        db.session.add(user)
        db.session.commit()
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember = remember_me)
    return redirect(request.args.get('next') or url_for('index'))

@lm.user_loader
def load_user(id):
    print("Into userloader")
    return User.query.get(int(id))
    
@app.route('/logout')
def logout():
    print("Into logout")
    logout_user()
    return redirect(url_for('index'))

@app.route('/update')
def update():
    update_all_data()
    return redirect(request.referrer)

   
   
#==============================================================================
# def embed_map(map, path="app/templates/map.html"):
#     """
#     Embeds a linked iframe to the map into the IPython notebook.
#     
#     Note: this method will not capture the source of the map into the notebook.
#     This method should work for all maps (as long as they use relative urls).
#     """
# 
#     print("into embed map")
#     #map.create_map(path=path)
#     return HTML('<iframe src="files/{path}" style="width: 100%; height: 510px; border: none"></iframe>'.format(path=path))
# 
#==============================================================================
 

#map.save(path)  
#maphtml = embed_map(map)
#print(maphtml)
#map.save("Map1.html")



#https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-ii-templates
#==============================================================================
# from app import app
# 
# @app.route('/') #creates mapping form URL / and URL /index to this function
# @app.route('/index')
# def index():
#    return "hello, World"
#==============================================================================
