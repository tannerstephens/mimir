from datetime import datetime
from enum import unique
from .extensions import db

Column = db.Column
relationship = db.relationship

def db_commit():
  db.session.commit()


class Model(db.Model):
  __abstract__ = True
  id = Column(db.Integer, primary_key=True)

  def save(self, commit=True):
    db.session.add(self)
    if commit:
      db.session.commit()
    return self

  def delete(self, commit=True):
    db.session.delete(self)
    return commit and db.session.commit()


class ReleaseDate(Model):
  date = Column(db.DateTime, unique=False, nullable=False)
  distributor_id = Column(db.Integer, db.ForeignKey('distributor.id'), nullable=True)
  releases = relationship('Release', backref='release_date', lazy=True)


class Distributor(Model):
  name = Column(db.String, unique=True, nullable=False)
  releases = relationship('Release', backref='distributor', lazy=True)
  lowres_image_url_format = Column(db.String, unique=False, nullable=True)
  highres_image_url_format = Column(db.String, unique=False, nullable=True)
  series_url_format = Column(db.String, unique=False, nullable=True)
  release_dates = relationship('ReleaseDate', backref='distributor', lazy=True)


class Publisher(Model):
  name = Column(db.String, unique=True, nullable=False)
  releases = relationship('Release', backref='publisher', lazy=True)


class Series(Model):
  title = Column(db.String, unique=False, nullable=False)
  series_id = Column(db.String, unique=True, nullable=False)
  releases = relationship('Release', backref='series', lazy=True)

  def serialize(self):
    return {
      'title': self.title,
      'release_count': len(self.releases),
      'id': self.id,
      'series_id': self.series_id
    }


class Release(Model):
  title = Column(db.String, unique=False, nullable=False)
  image_id = Column(db.String, unique=False, nullable=False)
  publisher_id = Column(db.Integer, db.ForeignKey('publisher.id'), nullable=False)
  release_id = Column(db.String, unique=False, nullable=False)
  series_id = Column(db.Integer, db.ForeignKey('series.id'), nullable=True)
  distributor_id = Column(db.Integer, db.ForeignKey('distributor.id'), nullable=True)
  releasedate_id = Column(db.Integer, db.ForeignKey('release_date.id'), nullable=True)

  def serialize(self):
    return {
      'id': self.id,
      'title': self.title,
      'publisher_id': self.publisher_id,
      'series_id': self.series_id,
      'distributor_id': self.distributor_id,
      'highres_image_url': self.distributor.highres_image_url_format.format(image_id=self.image_id),
      'lowres_image_url': self.distributor.lowres_image_url_format.format(image_id=self.image_id),
      'release_date': self.release_date.date.strftime('%Y-%m-%d')
    }
