```sh
# Install MySQL
sudo apt install mysql-server

# Initialize the database || Replace dbname, dbuser and password with
# your desired database name user and password.
sudo ./mysql-db-create.sh dbname dbuser dbpassword

# Install Python packages 
sudo pip install -r requirements.txt

# Save your Secret Key and Database URI to Environment Variables
export SUKKIRI_SECRET_KEY='your secret key goes here'
export SUKKIRI_DATABASE_URI='the URI for the database create before'

# Import the database schema
mysql -u dbuser -p
use dbname;
source create_db_schema.sql;
exit;

# Create an admin user
python3 create_admin.py dbname dbuser dbpassword api_username api_password

# Start the API
python3 api.py
```