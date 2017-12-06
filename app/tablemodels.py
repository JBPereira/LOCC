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
    longitude = db.Column(db.FLOAT(), index=True)
    wind_direction = db.Column(db.String(10))
    latitude = db.Column(db.FLOAT(), index=True)
    humidity = db.Column(db.FLOAT())
    temperature_10cm = db.Column(db.FLOAT())
    wind_direction_degrees = db.Column(db.FLOAT())
    temperature = db.Column(db.FLOAT())
    wind_blast = db.Column(db.FLOAT())
    wind_speedMS = db.Column(db.FLOAT())
    visibility_meters = db.Column(db.FLOAT())
    wind_speedBF = db.Column(db.FLOAT())
    sun_intensity = db.Column(db.FLOAT())
    datetime = db.Column(db.String(20))
    water_flow = db.Column(db.FLOAT())
    waves_height = db.Column(db.FLOAT())
    water_drainage = db.Column(db.FLOAT())
    water_level = db.Column(db.FLOAT())
    water_level_belgium_border = db.Column(db.FLOAT())
    tide = db.Column(db.FLOAT())
    
    def __repr__(self):
        return '<Data %r>' % (self.datetime)
  
class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post %r>' % (self.body)