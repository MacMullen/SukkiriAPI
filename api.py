import datetime
import os
import uuid
import jwt
from functools import wraps
from flask import Flask, request, jsonify, make_response
from google.cloud import firestore
from werkzeug.security import generate_password_hash, check_password_hash
from lib.classes import User, RMACase, Product, DistributionCompany

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SUKKIRI_SECRET_KEY')

db = firestore.Client()


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user_doc = db.collection('users').document(data['public_id']).get()
            current_user = current_user_doc.to_dict()
        except:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated


@app.route('/api/rma_cases', methods=['GET'])
@token_required
def get_all_rma_cases(current_user):
    rma_cases = db.collection('rma_cases').get()

    output = []

    for rma_case in rma_cases:
        rma_case = rma_case.to_dict()
        rma_case_data = {'id': rma_case["id"], 'brand': rma_case["brand"], 'model': rma_case["model"],
                         'problem': rma_case["problem"], 'serial_number': rma_case["serial_number"],
                         'distribution_company': rma_case["distribution_company"],
                         'sent_date': rma_case["sent_date"], 'returned_date': rma_case["sent_date"],
                         'resolved_date': rma_case["resolved_date"], 'status': rma_case["status"],
                         'to_be_revised_date': rma_case["to_be_revised_date"],
                         'unresolved_date': rma_case["unresolved_date"],
                         'to_be_sent_date': rma_case["to_be_sent_date"],
                         'to_be_revised_by': rma_case["to_be_revised_by"],
                         'to_be_sent_by': rma_case["to_be_sent_by"], 'sent_by': rma_case["sent_by"],
                         'returned_by': rma_case["returned_by"],
                         'resolved_by': rma_case["resolved_by"], 'unresolved_by': rma_case["unresolved_by"]}
        output.append(rma_case_data)
    return jsonify({'rma_cases': output})


@app.route('/api/rma_cases', methods=['POST'])
@token_required
def create_new_rma_case(current_user):
    data = request.get_json()

    new_id = str(uuid.uuid4())[:6]
    rma_case = db.collection('rma_cases').document(new_id).get().to_dict()
    while rma_case is not None:
        new_id = str(uuid.uuid4())[:6]
        rma_case = db.collection('rma_cases').get().to_dict()

    new_rma_case = RMACase(case_id=new_id, brand=data['brand'], model=data['model'], problem=data['problem'],
                           serial_number=data['serial_number'], distribution_company=data['distribution_company'],
                           current_user=current_user["first_name"] + ' ' + current_user["last_name"])

    try:
        db.collection('rma_cases').document(new_rma_case.id).set(new_rma_case.to_dict())
        return jsonify({'message': 'RMA case created successfully!', 'id': new_id})
    except:
        return jsonify({'message': 'Could not create the RMA case.'})


@app.route('/api/rma_cases/<rma_case_id>', methods=['GET'])
@token_required
def get_rma_case(current_user, rma_case_id):
    rma_case = db.collection('rma_cases').document(rma_case_id).get().to_dict()

    if rma_case is None:
        return jsonify({'message': 'No RMA case found with that id!'})
    else:
        rma_case_data = {'id': rma_case["id"], 'brand': rma_case["brand"], 'model': rma_case["model"],
                         'problem': rma_case["problem"], 'serial_number': rma_case["serial_number"],
                         'distribution_company': rma_case["distribution_company"],
                         'sent_date': rma_case["sent_date"], 'returned_date': rma_case["sent_date"],
                         'resolved_date': rma_case["resolved_date"], 'status': rma_case["status"],
                         'to_be_revised_date': rma_case["to_be_revised_date"],
                         'unresolved_date': rma_case["unresolved_date"],
                         'to_be_sent_date': rma_case["to_be_sent_date"],
                         'to_be_revised_by': rma_case["to_be_revised_by"],
                         'to_be_sent_by': rma_case["to_be_sent_by"], 'sent_by': rma_case["sent_by"],
                         'returned_by': rma_case["returned_by"],
                         'resolved_by': rma_case["resolved_by"], 'unresolved_by': rma_case["unresolved_by"]}

        return jsonify({'rma_case': rma_case_data})


@app.route('/api/rma_cases/<rma_case_id>/<new_status>', methods=['POST'])
@token_required
def modify_rma_case(current_user, rma_case_id, new_status):
    if current_user["role"] != ('admin' or 'rma_technician'):
        return jsonify({'message': 'Not authorized to change a RMA case status.'})

    try:
        rma_case_doc = db.collection('rma_cases').document(rma_case_id)

        rma_case = rma_case_doc.get().to_dict()

        if new_status not in ['to_be_sent', 'sent', 'returned', 'resolved', 'unresolved']:
            return jsonify({'message': 'Not a valid status'})

        updated_info = dict()

        if new_status == 'to_be_sent' and rma_case["status"] == 'to_be_revised':
            updated_info['status'] = 'to_be_sent'
            updated_info['to_be_sent_by'] = current_user["first_name"] + ' ' + current_user["last_name"]
            updated_info['to_be_sent_date'] = datetime.datetime.now()
        elif new_status == 'sent' and rma_case["status"] == 'to_be_sent':
            updated_info['status'] = 'sent'
            updated_info['sent_by'] = current_user["first_name"] + ' ' + current_user["last_name"]
            updated_info['sent_date'] = datetime.datetime.now()
        elif new_status == 'returned' and rma_case["status"] == 'sent':
            updated_info['status'] = 'returned'
            updated_info['returned_by'] = current_user["first_name"] + ' ' + current_user["last_name"]
            updated_info['returned_date'] = datetime.datetime.now()
        elif new_status == 'resolved' and rma_case["status"] == ('returned' or 'to_be_revised'):
            updated_info['status'] = 'resolved'
            updated_info['resolved_by'] = current_user["first_name"] + ' ' + current_user["last_name"]
            updated_info['resolved_date'] = datetime.datetime.now()
        elif new_status == 'unresolved' and rma_case["status"] == ('returned' or 'to_be_revised'):
            updated_info['status'] = 'unresolved'
            updated_info['unresolved_by'] = current_user["first_name"] + ' ' + current_user["last_name"]
            updated_info['unresolved_date'] = datetime.datetime.now()
        else:
            return jsonify({'message': 'Not a valid new status'})

        if updated_info:
            rma_case_doc.update(updated_info)

        return jsonify({'message': 'RMA case modified successfully!'})
    except:
        return jsonify({'message': 'No RMA case found'})


@app.route('/api/dist_companies', methods=['GET'])
@token_required
def get_all_dist_companies(current_user):
    dist_companies = db.session.query(DistributionCompany).all()

    output = []

    for dist_company in dist_companies:
        dist_company_data = {'id': dist_company.id, 'name': dist_company.name, 'email': dist_company.email,
                             'address': dist_company.address, 'hours': dist_company.hours,
                             'contact_name': dist_company.contact_name,
                             'phone': dist_company.phone}
        output.append(dist_company_data)
    return jsonify({'dist_companies': output})


@app.route('/api/dist_companies', methods=['POST'])
@token_required
def create_new_dist_company(current_user):
    data = request.get_json()

    new_dist_company = DistributionCompany(name=data['name'], email=data['email'], address=data['address'],
                                           hours=data['hours'], contact_name=data['contact_name'],
                                           phone=data['phone'])

    try:
        db.session.add(new_dist_company)
        db.session.commit()
        return jsonify({'message': 'New distribution company created!'})
    except:
        return jsonify({'message': 'Distribution company already exists!'})


@app.route('/api/dist_companies/<dist_company_id>', methods=['GET'])
@token_required
def get_dist_company(current_user, dist_company_id):
    dist_company = db.session.query(DistributionCompany).filter_by(id=dist_company_id).first()

    if not dist_company:
        return jsonify({'message': 'No distribution company found!'})

    dist_company_data = {'name': dist_company.name, 'email': dist_company.email, 'address': dist_company.address,
                         'hours': dist_company.hours, 'contact_name': dist_company.contact_name,
                         'phone': dist_company.phone}

    return jsonify({'dist_company': dist_company_data})


@app.route('/api/dist_companies/<dist_company_id>', methods=['PUT'])
@token_required
def modify_dist_company(current_user, dist_company_id):
    dist_company = db.session.query(DistributionCompany).filter_by(id=dist_company_id).first()

    if not dist_company:
        return jsonify({'message': 'No product found!'})

    data = request.get_json()

    dist_company.name = data['name']
    dist_company.email = data['email']
    dist_company.address = data['address']
    dist_company.hours = data['hours']
    dist_company.contact_name = data['contact_name']
    dist_company.phone = data['phone']

    db.session.commit()

    return jsonify({'message': 'Distribution company modified successfully!'})


@app.route('/api/dist_companies/<dist_company_id>', methods=['DELETE'])
@token_required
def delete_dist_company(current_user, dist_company_id):
    dist_company = db.session.query(DistributionCompany).filter_by(id=dist_company_id).first()

    if not dist_company:
        return jsonify({'message': 'No distribution company found!'})

    db.session.delete(dist_company)
    db.session.commit()

    return jsonify({'message': 'Distribution company deleted successfully!'})


@app.route('/api/products', methods=['GET'])
@token_required
def get_all_products(current_user):
    products_docs = db.collection('products').get()

    output = []

    for product in products_docs:
        product = product.to_dict()
        product_data = {'id': product['id'], 'brand': product['brand'], 'model': product['model'],
                        'description': product['description'], 'stock': product['stock'],
                        'stock_under_control': product['stock_under_control'],
                        'distribution_company': product['distribution_company'], 'ean': product['ean']}
        output.append(product_data)
    return jsonify({'products': output})


@app.route('/api/products', methods=['POST'])
@token_required
def create_new_product(current_user):
    data = request.get_json()

    # Check if product already exists.
    product = db.collection('products').document(data['brand'] + ' ' + data['model']).get().to_dict()

    if product:
        return jsonify({'message': 'That product already exists'})

    if not data['brand']:
        return jsonify({'message': 'Product must have a brand'})
    if not data['model']:
        return jsonify({'message': 'Product must have a model'})
    if not data['description']:
        data['description'] = ""
    if not data['stock']:
        data['stock'] = 0
    if not data['stock_under_control']:
        data['stock_under_control'] = False
    if not data['ean']:
        data['ean'] = ""
    if not data['distribution_company']:
        data['distribution_company'] = ""

    new_product = Product(brand=data['brand'], model=data['model'], description=data['description'],
                          stock=data['stock'], stock_under_control=data['stock_under_control'],
                          distribution_company=data['distribution_company'], ean=data['ean'])

    try:
        db.collection('products').document(new_product.brand + ' ' + new_product.model).set(new_product.to_dict())
        return jsonify({'message': 'Product added successfully!'})
    except:
        return jsonify({'message': 'Could not add the product'})


@app.route('/api/products/<product_name>', methods=['GET'])
@token_required
def get_product(current_user, product_name):
    product = db.collection('products').document(product_name).get().to_dict()

    if not product:
        return jsonify({'message': 'No product found!'})

    product_data = {'brand': product['brand'], 'model': product['model'],
                    'description': product['description'], 'stock': product['stock'],
                    'stock_under_control': product['stock_under_control'],
                    'distribution_company': product['distribution_company'], 'ean': product['ean']}

    return jsonify({'product': product_data})


@app.route('/api/products/ean/<ean>', methods=['GET'])
@token_required
def get_product_with_ean(current_user, ean):
    products = db.session.query(Product).filter_by(ean=ean).all()

    if len(products) == 0:
        return jsonify({'message': 'No product found with that EAN!'})
    elif len(products) == 1:
        product_data = {'id': products[0].id, 'brand': products[0].brand, 'model': products[0].model,
                        'description': products[0].description, 'stock': products[0].stock,
                        'stock_under_control': products[0].stock_under_control,
                        'distribution_company': products[0].distribution_company, 'ean': products[0].ean}

        return jsonify({'product': product_data})
    else:
        output = []
        for product in products:
            product_data = {'id': product.id, 'brand': product.brand, 'model': product.model,
                            'description': product.description, 'stock': product.stock,
                            'stock_under_control': product.stock_under_control,
                            'distribution_company': product.distribution_company, 'ean': product.ean}
            output.append(product_data)
        return jsonify({'products': output})


@app.route('/api/products/<product_id>', methods=['PUT'])
@token_required
def modify_product(current_user, product_id):
    product = db.session.query(Product).filter_by(id=product_id).first()

    if not product:
        return jsonify({'message': 'No product found!'})

    data = request.get_json()

    product.brand = data['brand']
    product.model = data['model']
    product.description = data['description']
    product.stock = int(data['stock'])
    product.stock_under_control = bool(data['stock_under_control'])
    product.distribution_company = data['distribution_company']
    product.ean = data['ean']

    db.session.commit()

    return jsonify({'message': 'Product modified successfully!'})


@app.route('/api/products/<product_id>', methods=['DELETE'])
@token_required
def delete_product(current_user, product_id):
    product = db.session.query(Product).filter_by(id=product_id).first()

    if not product:
        return jsonify({'message': 'No product found!'})

    db.session.delete(product)
    db.session.commit()

    return jsonify({'message': 'Product deleted successfully!'})


@app.route('/api/users', methods=['GET'])
@token_required
def get_all_users(current_user):
    if not current_user['role'] == 'admin':
        return jsonify({'message': 'Invalid permissions'})

    users = db.collection('users').get()

    output = []

    for user in users:
        user = user.to_dict()
        user_data = {'public_id': user['public_id'], 'username': user['username'], 'first_name': user['first_name'],
                     'last_name': user['last_name'], 'email': user['email'],
                     'role': user['role']}
        output.append(user_data)
    return jsonify({'users': output})


@app.route('/api/users', methods=['POST'])
@token_required
def create_new_user(current_user):
    if not current_user['role'] == 'admin':
        return jsonify({'message': 'Invalid permissions'})

    data = request.get_json()

    if 'username' not in data or 'password' not in data or 'role' not in data:
        return jsonify({'message': 'Invalid input data'})

    new_user = User(email=data['email'] if 'email' in data else None,
                    username=data['username'],
                    password=data['password'],
                    first_name=data['first_name'] if 'first_name' in data else None,
                    last_name=data['last_name'] if 'last_name' in data else None,
                    role=data['role'])

    db.collection('users').document(new_user.public_id).set(new_user.to_dict())

    return jsonify({'message': 'New user created!'})


@app.route('/api/users/<user_public_id>', methods=['GET'])
@token_required
def get_user(current_user, user_public_id):
    if not current_user['role'] == 'admin':
        return jsonify({'message': 'Invalid permissions'})

    user_doc = db.collection('users').document(user_public_id).get()

    try:
        user = user_doc.to_dict()
        user_data = {'public_id': user['public_id'], 'username': user['username'], 'first_name': user['first_name'],
                     'last_name': user['last_name'], 'email': user['email'], 'role': user['role']}
        return jsonify({'user': user_data})
    except:
        return jsonify({'message': 'No user found!'})


@app.route('/api/users/<user_public_id>', methods=['PUT'])
@token_required
def modify_user(current_user, user_public_id):
    if not current_user['role'] == 'admin':
        return jsonify({'message': 'Invalid permissions'})

    data = request.get_json()

    user_doc = db.collection('users').document(user_public_id)

    try:
        updated_info = dict()
        if 'email' in data:
            updated_info['email'] = data['email']
        if 'first_name' in data:
            updated_info['first_name'] = data['first_name']
        if 'last_name' in data:
            updated_info['last_name'] = data['last_name']
        if 'role' in data:
            updated_info['role'] = data['role']
        if 'password' in data:
            updated_info['password'] = generate_password_hash(data['password'], method='SHA256')
        if updated_info:
            user_doc.update(updated_info)
    except:
        return jsonify({'message': 'No user found!'})

    return jsonify({'message': 'User modified successfully!'})


@app.route('/api/users/<user_public_id>', methods=['DELETE'])
@token_required
def delete_user(current_user, user_public_id):
    if not current_user['role'] == 'admin':
        return jsonify({'message': 'Invalid permissions'})

    user_doc = db.collection('users').document(user_public_id)

    try:
        user_doc.delete()
        return jsonify({'message': 'User deleted successfully!'})
    except:
        return jsonify({'message': 'No user found!'})


@app.route('/api/auth')
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login Required!"'})

    user_doc = db.collection('users').where('username', '==', auth.username).limit(1).get()
    try:
        for user in user_doc:
            user = user.to_dict()
        if check_password_hash(user['password'], auth.password):
            token = jwt.encode(
                {'public_id': user['public_id'], 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)},
                app.config['SECRET_KEY'])
            return jsonify({'token': token.decode('UTF-8')})

        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login Required!"'})
    except:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login Required!"'})


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
