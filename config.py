import os

class Config:
   SECRET_KEY = '123456789'  # 니중에 넣을 해쉬값
   SQLALCHEMY_DATABASE_URI = 'mysql://root:1234@localhost/kopo'
   SQLALCHEMY_TRACK_MODIFICATIONS = False
   WTF_CSRF_ENABLED = True