from app.models.base import db

user_roles = db.Table(
    'user_roles',
    db.Column('email', db.String(120), db.ForeignKey('users.email', ondelete='CASCADE'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True)
)

report_data_sources = db.Table(
    'report_data_sources',
    db.Column('report_id', db.Integer, db.ForeignKey('reports.id'), primary_key=True),
    db.Column('data_source_id', db.Integer, db.ForeignKey('data_sources.id'), primary_key=True)
)

visor_data_sources = db.Table(
    'visor_data_sources',
    db.Column('visor_id', db.Integer, db.ForeignKey('visors.id'), primary_key=True),
    db.Column('data_source_id', db.Integer, db.ForeignKey('data_sources.id'), primary_key=True)
)

simulator_data_sources = db.Table(
    'simulator_data_sources',
    db.Column('simulator_id', db.Integer, db.ForeignKey('simulators.id'), primary_key=True),
    db.Column('data_source_id', db.Integer, db.ForeignKey('data_sources.id'), primary_key=True)
)

role_reports = db.Table(
    'role_reports',
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True),
    db.Column('report_id', db.Integer, db.ForeignKey('reports.id'), primary_key=True)
)

role_visors = db.Table(
    'role_visors',
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True),
    db.Column('visor_id', db.Integer, db.ForeignKey('visors.id'), primary_key=True)
)

role_simulators = db.Table(
    'role_simulators',
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True),
    db.Column('simulator_id', db.Integer, db.ForeignKey('simulators.id'), primary_key=True)
)