from app import db
import random

class Machine(db.Model):

    __tablename__ = 'MACHINE'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    def __init__(self, name):
        self.id = random.randint(1, 1000)
        self.name = name

    def __repr__(self):
        return "<Machine(name='%s')>" % (self.name)
