# lib/classes.py

import datetime
import uuid

from werkzeug.security import generate_password_hash


class User(object):
    def __init__(self, username, email, first_name, last_name, password, role):
        self.public_id = str(uuid.uuid4())
        self.username = username
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.password_hash = generate_password_hash(password, method='SHA256')
        self.role = role

    def to_dict(self):
        return {
            'public_id': self.public_id,
            'username': self.username,
            'password': self.password_hash,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role
        }

    def __repr__(self):
        return (
            'User(public_id={}, username={}, email={}, first_name={}, last_name={}, role={})'.format(self.public_id,
                                                                                                     self.username,
                                                                                                     self.email,
                                                                                                     self.first_name,
                                                                                                     self.last_name,
                                                                                                     self.role))


class DistributionCompany(object):
    def __init__(self, name, email, address, hours, contact_name, phone):
        self.name = name
        self.email = email
        self.address = address
        self.hours = hours
        self.contact_name = contact_name
        self.phone = phone

    def to_dict(self):
        return {
            'name': self.name,
            'email': self.email,
            'address': self.address,
            'hours': self.hours,
            'contact_name': self.contact_name,
            'phone': self.phone
        }

    def __repr__(self):
        return (
            'Distribution Company(name={}, email={}, address={}, hours={}, contact_name={}, phone={})'.format(
                self.name,
                self.email,
                self.address,
                self.hours,
                self.contact_name,
                self.phone))


class RMACase(object):
    def __init__(self, case_id, brand, model, problem, serial_number, distribution_company, current_user):
        self.id = case_id
        self.brand = brand
        self.model = model
        self.problem = problem
        self.serial_number = serial_number
        self.distribution_company = distribution_company
        self.to_be_revised_by = current_user
        self.status = 'to_be_revised'
        self.to_be_revised_date = datetime.datetime.now()
        self.sent_date = None
        self.returned_date = None
        self.resolved_date = None
        self.unresolved_date = None
        self.to_be_sent_date = None
        self.to_be_sent_by = None
        self.sent_by = None
        self.returned_by = None
        self.resolved_by = None
        self.unresolved_by = None

    def to_dict(self):
        return {
            'id': self.id,
            'brand': self.brand,
            'model': self.model,
            'problem': self.problem,
            'serial_number': self.serial_number,
            'distribution_company': self.distribution_company,
            'sent_date': self.sent_date,
            'returned_date': self.returned_date,
            'resolved_date': self.resolved_date,
            'status': self.status,
            'to_be_revised_date': self.to_be_revised_date,
            'unresolved_date': self.unresolved_date,
            'to_be_sent_date': self.to_be_sent_date,
            'to_be_revised_by': self.to_be_revised_by,
            'to_be_sent_by': self.to_be_sent_by,
            'sent_by': self.sent_by,
            'returned_by': self.returned_by,
            'resolved_by': self.resolved_by,
            'unresolved_by': self.unresolved_by
        }


class Product(object):
    def __init__(self, brand, model, description, stock, stock_under_control, distribution_company, ean):
        self.brand = brand
        self.model = model
        self.description = description
        self.stock = stock
        self.stock_under_control = stock_under_control
        self.distribution_company = distribution_company
        self.ean = ean

    def to_dict(self):
        return {
            'brand': self.brand,
            'model': self.model,
            'description': self.description,
            'stock': self.stock,
            'stock_under_control': self.stock_under_control,
            'distribution_company': self.distribution_company,
            'ean': self.ean
        }
