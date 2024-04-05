from app import db
from app.models import Machine


class DBMethods:
    def __init__(self, app):
        self.app = app

    def create_tables(self):
        with self.app.app_context():
            db.create_all()

    def drop_tables(self):
        with self.app.app_context():
            db.drop_all()

    def get_all_machines(self):
        machines = Machine.query.all()
        return machines
    
    def get_machine(self, id):
        machine = Machine.query.get(id)
        return machine

    def add_machine(self, name):
        machine = Machine(name)
        db.session.add(machine)
        db.session.commit()
        return machine

    def delete_machine(self, id):
        machine = Machine.query.filter_by(id=id).delete()
        db.session.commit()
        return machine
