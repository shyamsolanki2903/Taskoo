import os
import time
from flask import Flask, redirect, url_for, session, request, render_template, jsonify
import requests
import logging
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_graphql import GraphQLView
import graphene
import stripe
from werkzeug.utils import secure_filename

load_dotenv()

STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY')

stripe.api_key = STRIPE_SECRET_KEY

app = Flask(__name__)

app.secret_key = os.getenv('FLASK_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'  
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
logging.basicConfig(level=logging.DEBUG)

keycloak_server_url = os.getenv('KEYCLOAK_SERVER_URL')
realm_name = os.getenv('REALM_NAME')
client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
redirect_uri = os.getenv('REDIRECT_URI')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class PremiumUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    is_premium = db.Column(db.Boolean, default=True)

class UserTodo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    todo_id = db.Column(db.Integer, nullable=False)

    __table_args__ = (db.UniqueConstraint('todo_id'),)

class ToDo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text, nullable=False)
    time = db.Column(db.String(20), nullable=False)
    image_filename = db.Column(db.String(255), nullable=True)  

class ToDoType(graphene.ObjectType):
    id = graphene.Int()
    title = graphene.String()
    description = graphene.String()
    time = graphene.String()
    image_filename = graphene.String()
    image_url = graphene.String()
    
    def resolve_image_url(self, info):
        if self.image_filename:
            return f"/static/uploads/{self.image_filename}"
        return None

class Query(graphene.ObjectType):
    todos = graphene.List(ToDoType)

    def resolve_todos(self, info):
        return ToDo.query.all()

class CreateToDoMutation(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        description = graphene.String(required=True)
        time = graphene.String(required=True)
        image_filename = graphene.String(required=False)

    todo = graphene.Field(ToDoType)

    def mutate(self, info, title, description, time, image_filename=None):
        new_todo = ToDo(title=title, description=description, time=time, image_filename=image_filename)
        db.session.add(new_todo)
        db.session.commit()
        return CreateToDoMutation(todo=new_todo)

    
class Mutation(graphene.ObjectType):
    create_todo = CreateToDoMutation.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)

@app.route('/login')
def login():
    authorize_url = f"{keycloak_server_url}/realms/{realm_name}/protocol/openid-connect/auth"
    params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'openid profile email'
    }
    return redirect(f"{authorize_url}?{'&'.join([f'{key}={value}' for key, value in params.items()])}")

@app.route('/callback')
def callback():
    code = request.args.get('code')
    logging.debug(f"Callback received with code: {code}")
    token_endpoint = f"{keycloak_server_url}/realms/{realm_name}/protocol/openid-connect/token"
    payload = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri,
        'client_id': client_id,
        'client_secret': client_secret
    }
    try:
        response = requests.post(token_endpoint, data=payload)
        token_data = response.json()
        if 'access_token' in token_data:
            userinfo_endpoint = f"{keycloak_server_url}/realms/{realm_name}/protocol/openid-connect/userinfo"
            userinfo_response = requests.get(userinfo_endpoint, headers={'Authorization': f"Bearer {token_data['access_token']}"} )
            userinfo = userinfo_response.json()
            username = userinfo.get('preferred_username')
            logging.debug(f"Checking premium status for user: {username}")
            premium_user = PremiumUser.query.filter_by(username=username).first()
            if premium_user:
                logging.debug(f"Found premium user record: {premium_user.username}, is_premium={premium_user.is_premium}")
                if premium_user.is_premium:
                    session['pro_user'] = True
                    logging.debug(f"Set pro_user=True in session")
            else:
                logging.debug(f"No premium user record found for {username}")
            session['user'] = {
                'id_token': token_data.get('id_token'),
                'access_token': token_data.get('access_token'),
                'refresh_token': token_data.get('refresh_token'),
                'username': username,
                'email': userinfo.get('email')
            }
            logging.debug("User logged in successfully.")
            return redirect(url_for('index'))
        else:
            logging.error("Failed to fetch tokens.")
            return "Failed to fetch tokens."
    except Exception as e:
        logging.error(f"Exception during token exchange: {e}")
        return "Failed to fetch tokens."

@app.route('/logout')
def logout():
    logging.debug('Attempting to logout...')
    try:
        # Get the ID token before clearing the session
        id_token = session['user'].get('id_token') if 'user' in session else None
        
        # Clear the local session
        session.clear()
        logging.debug('Session cleared. Redirecting to Keycloak auth page...')
        
        # First logout from Keycloak if we have an ID token
        if id_token:
            # Perform Keycloak logout
            logout_url = f"{keycloak_server_url}/realms/{realm_name}/protocol/openid-connect/logout"
            params = {
                'id_token_hint': id_token
            }
            # We'll redirect to Keycloak auth page after clearing both sessions
            keycloak_logout_url = f"{logout_url}?{'&'.join([f'{key}={value}' for key, value in params.items()])}"
            requests.get(keycloak_logout_url)  # Make request but don't redirect
        
        # Redirect to Keycloak auth URL after logout
        authorize_url = f"{keycloak_server_url}/realms/{realm_name}/protocol/openid-connect/auth"
        params = {
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'scope': 'openid profile email'
        }
        keycloak_auth_url = f"{authorize_url}?{'&'.join([f'{key}={value}' for key, value in params.items()])}"
        
        return redirect(keycloak_auth_url)
    except Exception as e:
        logging.error(f"Exception during logout: {e}")
        session.clear()
        
        # Even in case of error, try to redirect to Keycloak auth
        try:
            authorize_url = f"{keycloak_server_url}/realms/{realm_name}/protocol/openid-connect/auth"
            params = {
                'client_id': client_id,
                'redirect_uri': redirect_uri,
                'response_type': 'code',
                'scope': 'openid profile email'
            }
            keycloak_auth_url = f"{authorize_url}?{'&'.join([f'{key}={value}' for key, value in params.items()])}"
            return redirect(keycloak_auth_url)
        except:
            # Last resort fallback to local login
            return redirect(url_for('login'))

@app.route('/')
def index():
    if 'user' in session:
        username = session['user']['username']
        if 'pro_user' not in session:
            premium_user = PremiumUser.query.filter_by(username=username).first()
            if premium_user and premium_user.is_premium:
                session['pro_user'] = True
                logging.debug(f"Restored premium status for user {username} on page load")
        
        user_todo_links = UserTodo.query.filter_by(username=username).all()
        todo_ids = [link.todo_id for link in user_todo_links]
        todos = ToDo.query.filter(ToDo.id.in_(todo_ids)).all() if todo_ids else []
        
        return render_template('home.html', username=username, 
                              todos=todos, pro_license='pro_user' in session)
    else:
        return redirect(url_for('login'))

@app.route('/add_todo', methods=['POST'])
def add_todo():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    username = session['user']['username']
    title = request.form['title']
    description = request.form['description']
    time_value = request.form['time']
    image_filename = None
    
    if 'pro_user' in session and 'image' in request.files:
        image_file = request.files['image']
        if image_file and image_file.filename != '' and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            timestamp = int(time.time())
            filename = f"{timestamp}_{filename}"
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_filename = filename

    new_todo = ToDo(title=title, description=description, time=time_value, image_filename=image_filename)
    db.session.add(new_todo)
    db.session.flush() 
    
    user_todo_link = UserTodo(username=username, todo_id=new_todo.id)
    db.session.add(user_todo_link)
    
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/edit_todo/<int:id>', methods=['GET', 'POST'])
def edit_todo(id):
    if 'user' not in session:
        return redirect(url_for('login'))
        
    username = session['user']['username']
    
    user_todo_link = UserTodo.query.filter_by(username=username, todo_id=id).first()
    if not user_todo_link:
        return redirect(url_for('index'))
    
    todo = ToDo.query.get(id)
    if not todo:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        todo.title = request.form['title']
        todo.description = request.form['description']
        todo.time = request.form['time']
        
        if 'pro_user' in session:
            remove_image = 'remove_image' in request.form
            if remove_image and todo.image_filename:
                old_image_path = os.path.join(app.config['UPLOAD_FOLDER'], todo.image_filename)
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)
                todo.image_filename = None
            elif 'image' in request.files:
                image_file = request.files['image']
                if image_file and image_file.filename != '' and allowed_file(image_file.filename):
                    if todo.image_filename:
                        old_image_path = os.path.join(app.config['UPLOAD_FOLDER'], todo.image_filename)
                        if os.path.exists(old_image_path):
                            os.remove(old_image_path)
                    filename = secure_filename(image_file.filename)
                    timestamp = int(time.time())
                    filename = f"{timestamp}_{filename}"
                    image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    todo.image_filename = filename        
        
        db.session.commit()
        return redirect(url_for('index'))
        
    return render_template('edit_todo.html', todo=todo, pro_license='pro_user' in session)

@app.route('/delete_todo/<int:id>', methods=['POST'])
def delete_todo(id):
    if 'user' not in session:
        return redirect(url_for('login'))
        
    username = session['user']['username']
    user_todo_link = UserTodo.query.filter_by(username=username, todo_id=id).first()
    if user_todo_link:
        todo = ToDo.query.get(id)
        if todo:
            if todo.image_filename:
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], todo.image_filename)
                if os.path.exists(image_path):
                    os.remove(image_path)
            db.session.delete(user_todo_link)
            db.session.delete(todo)
            db.session.commit()
        
    return redirect(url_for('index'))

app.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True))

@app.route('/buy_pro', methods=['GET'])
def buy_pro():
    if 'user' not in session:
        return redirect(url_for('login'))
    stripe_session = stripe.checkout.Session.create(  
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': 'Pro License',
                },
                'unit_amount': 4999,  
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=url_for('payment_success', _external=True),
        cancel_url=url_for('payment_cancel', _external=True),
        client_reference_id=session['user'].get('username', ''),
    )
    return redirect(stripe_session.url, code=303)

@app.route('/payment_success')
def payment_success():
    if 'user' in session:
        username = session['user'].get('username')
        if username:
            premium_user = PremiumUser.query.filter_by(username=username).first()
            if not premium_user:
                premium_user = PremiumUser(username=username, is_premium=True)
                db.session.add(premium_user)
                db.session.commit()
                logging.debug(f"Added {username} as premium user")
        session['pro_user'] = True    
    return render_template('payment_success.html', message="Thank you for purchasing the Pro License!")

@app.route('/payment_cancel')
def payment_cancel():
    return render_template('payment_cancel.html', message="Your payment was canceled.")

@app.route('/migrate_existing_todos')
def migrate_existing_todos():
    """
    A one-time helper route to migrate existing todos to the new system.
    In a production app, you'd use a proper migration script instead.
    """
    if 'user' in session and session['user'].get('username') == 'admin123':
        try:
            todos = ToDo.query.all()
            username = session['user'].get('username')
            
            existing_todo_ids = [link.todo_id for link in UserTodo.query.all()]
            
            count = 0
            for todo in todos:
                if todo.id not in existing_todo_ids:
                    user_todo_link = UserTodo(username=username, todo_id=todo.id)
                    db.session.add(user_todo_link)
                    count += 1
            
            db.session.commit()
            return f"Successfully migrated {count} todos to user {username}"
        except Exception as e:
            db.session.rollback()
            return f"Error during migration: {str(e)}"
    return "Unauthorized", 401

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)