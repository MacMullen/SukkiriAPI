# models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()




class Product(db.Model):
    __tablename__ = 'products'
    __table_args__ = (
        db.UniqueConstraint('brand', 'model'),
    )

    id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(120), index=True)
    model = db.Column(db.String(120), index=True)
    description = db.Column(db.Text)
    stock = db.Column(db.Integer, default=0)
    stock_under_control = db.Column(db.Boolean)
    distribution_company = db.Column(db.String(120))
    ean = db.Column(db.String(13))


class RMAProduct(db.Model):
    __tablename__ = 'rma_products'

    id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(120), index=True, unique=True)
    model = db.Column(db.String(120))
    problem = db.Column(db.Text)
    serial_number = db.Column(db.String(120))
    distribution_company = db.Column(db.String(60), index=True)
    status = db.Column(db.String(60), default="to_be_revised")
    to_be_revised_date = db.Column(db.DateTime)
    to_be_sent_date = db.Column(db.DateTime)
    sent_date = db.Column(db.DateTime)
    returned_date = db.Column(db.DateTime)
    resolved_date = db.Column(db.DateTime)
    unresolved_date = db.Column(db.DateTime)
    to_be_revised_by = db.Column(db.String(60))
    to_be_sent_by = db.Column(db.String(60))
    sent_by = db.Column(db.String(60))
    returned_by = db.Column(db.String(60))
    resolved_by = db.Column(db.String(60))
    unresolved_by = db.Column(db.String(60))