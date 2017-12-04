from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3
            
    def __repr__(self):
        return '<User %r>' % (self.nickname)

class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    index = db.Column(db.Integer,  index=True)
    longitude = db.Column(db.Integer(), index=True)
    wind_direction = db.Column(db.Integer())
    latitude = db.Column(db.Integer(), index=True)
    humidity = db.Column(db.Integer())
    temperature_10cm = db.Column(db.Integer())
    wind_direction_degrees = db.Column(db.Integer())
    temperature = db.Column(db.Integer())
    wind_blast = db.Column(db.Integer())
    wind_speedMS = db.Column(db.Integer())
    visibility_meters = db.Column(db.Integer())
    wind_speedBF = db.Column(db.Integer())
    sun_intensity = db.Column(db.Integer())
    datetime = db.Column(db.Integer())
    water_flow = db.Column(db.Integer())
    waves_height = db.Column(db.Integer())
    water_drainage = db.Column(db.Integer())
    water_level = db.Column(db.Integer())
    water_level_belgium_border = db.Column(db.Integer())
    tide = db.Column(db.Integer())
    
    def __repr__(self):
        return '<Data %r>' % (self.datetime)
  
class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post %r>' % (self.body)