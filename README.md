# Flask-ToDo_with_Keycloak-Stripe

This project is a Flask-based To-Do list application with Keycloak authentication and Stripe payment integration. The project demonstrates how to use Flask with Keycloak for user authentication and integrate Stripe to handle payments for premium features.

## Features
- User authentication via Keycloak.
- Users can log in, add, edit, and delete to-do items.
- Stripe integration for premium features (e.g., Pro License purchase).
- A clean, responsive UI with Bootstrap.

## Project Demosntration Video
[CLick Here](https://drive.google.com/file/d/11sYyxpB2J_Fi7BnztSZNfyrNJ4j0-0fU/view?usp=sharing)

[Click here to view the video](https://github.com/Kalparatna/Flask-ToDo_with_keycloak-stripe/blob/main/video.mp4)




## Prerequisites
Before setting up the project, make sure you have the following installed:

- Python 3.x
- Docker (for running Keycloak and setting up the development environment)
- Stripe account (for the payment integration)
- Keycloak instance (either running locally or using the Docker setup)
- Node.js and npm (for front-end dependencies, if applicable)

## Project Setup

### 1. Clone the Repository
Clone the project repository to your local machine:

```bash
git clone https://github.com/Kalparatna/Flask-ToDo_with_keycloak-stripe.git
cd Flask-ToDo_with_keycloak-stripe
2. Set Up the Virtual Environment
It's recommended to use a virtual environment to manage your Python dependencies:
```

```bash
Copy code
python -m venv venv
source venv/bin/activate  # On Windows, use 'venv\Scripts\activate'
```
3. Install Dependencies
Install the required Python packages:

```bash
Copy code
pip install -r requirements.txt
```
Dependencies:

flask: For the Flask web application.
flask_sqlalchemy: For SQLite database integration.
stripe: For Stripe payment processing.
python-dotenv: For loading environment variables from a .env file.
requests: For HTTP requests.
flask-graphql: For integrating GraphQL with Flask.
4. Set Up Keycloak (Authentication)
Running Keycloak Locally with Docker:
If you want to run Keycloak locally in a Docker container, you can use the official Keycloak Docker image.

Run the following command to pull and start Keycloak with Docker:

```bash
Copy code
docker run -d -p 8080:8080 \
  -e KEYCLOAK_USER=admin \
  -e KEYCLOAK_PASSWORD=new-password \
  --name keycloak \
  quay.io/keycloak/keycloak:latest
```
This will start Keycloak and expose it on http://localhost:8080. The default admin credentials are:
```
Username: admin
Password: new-password
You can access the Keycloak Admin Console by navigating to http://localhost:8080 in your browser.
```

Configure Keycloak:
Create a Realm (e.g., master).
Create a Client (e.g., flask-client).
Set Valid Redirect URIs (e.g., http://localhost:5000/callback).
Copy the Client ID and Client Secret and store them in the .env file.
5. Set Up Stripe
Create a Stripe Account:
If you don’t have one, you can sign up at Stripe.

Get API Keys:
Go to the Stripe Dashboard and get your Secret Key and Publishable Key.
Add the Stripe keys to your .env file.
6. Configure Environment Variables
Create a .env file in the root of the project and add the following configuration:

ini
Copy code
# Keycloak Configuration
KEYCLOAK_SERVER_URL=http://localhost:8080
REALM_NAME=master
CLIENT_ID=flask-client
CLIENT_SECRET=new-password
REDIRECT_URI=http://localhost:5000/callback

# Flask Configuration
FLASK_SECRET_KEY=your-flask-secret-key

# Stripe Configuration
STRIPE_SECRET_KEY=your-stripe-secret-key
STRIPE_PUBLIC_KEY=your-stripe-public-key

# Database Configuration
DATABASE_URI=sqlite:///todos.db
7. Initialize the Database
Run the following command to initialize the SQLite database for the To-Do list:

```bash
Copy code
python
from app import db
db.create_all()
exit()
```
8. Running the Application
To run the Flask application, use the following command:

```bash
Copy code
python app.py
```
This will start the Flask development server on http://localhost:5000.

9. Accessing the Application
Navigate to http://localhost:5000 in your browser.

If not logged in, you will be redirected to Keycloak for authentication.
Once logged in, you can manage your To-Do list.
To access the Buy Pro feature, click the "Buy Pro" button which will redirect to Stripe for payment.
10. Payment Integration
The Pro License functionality is implemented using Stripe. When a user clicks "Buy Pro", they will be redirected to Stripe's checkout page to complete the payment. Upon success, they will be redirected to a success page.

11. Stopping Keycloak (if running in Docker)
To stop the Keycloak container, use the following command:

```bash
Copy code
docker stop keycloak
docker rm keycloak
```
Troubleshooting
Keycloak Authentication Issues:
Ensure that the Client ID and Client Secret in the .env file match those configured in Keycloak.
Verify that Keycloak is running and accessible at the configured URL (http://localhost:8080).
Stripe Payment Issues:
Make sure the API keys in the .env file are correct.
Check that your Stripe account is active and in test mode for development.
vbnet
Copy code

This `README.md` provides a step-by-step guide to setting up the Flask-ToDo_with_Keycloak-Stripe project, including prerequisites, installation, and troubleshooting. Let me know if you'd like any more details or adjustments!





