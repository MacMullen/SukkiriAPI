# lib/classes.py

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
