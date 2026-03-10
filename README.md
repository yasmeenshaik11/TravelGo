TravelGo ✈️
TravelGo is a cloud-based travel booking platform built using Flask. It allows users to register, log in, and book buses, trains, flights, and hotels from a unified interface.

The application integrates with AWS DynamoDB for data storage and AWS SNS for email notifications when bookings are created or cancelled.

🚀 Features
Authentication: User registration and login with password hashing via Werkzeug.
Booking System: Unified interface for Bus, Train, Flight, and Hotel bookings.
Automation: Automatic seat assignment and ticket pricing.
Management: View booking history and perform cancellations.
Cloud Integration: DynamoDB for persistent storage and SNS for automated notifications.

travelgo_project/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── .gitignore          # Files to exclude from Git
├── .env.example        # Template for environment variables
├── README.md           # Project documentation
├── templates/          # HTML files
│   ├── base.html
│   ├── home.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── booking.html
│   └── history.html
└── static/             # Static assets
    └── css/
        └── style.css
🛠️ Setup Instructions
Follow these steps to run the project locally.

1. Clone the Repository

git clone [https://github.com/amarnath0038/TravelGo.git](https://github.com/amarnath0038/TravelGo.git)
cd travelgo_project
2. Create a Virtual Environment
Linux / Mac:

python3 -m venv venv

Windows:

python -m venv venv


3. Activate the Virtual Environment
Linux / Mac:

source venv/bin/activate

Windows:

venv\Scripts\activate

4. Install Dependencies

pip install -r requirements.txt

5. Configure Environment Variables

Create a .env file in the project root:

# For Linux/Mac
cp .env.example .env

# For Windows
copy .env.example .env
Edit the .env file with your credentials:

Ini, TOML
AWS_REGION=us-east-1
SNS_TOPIC_ARN=your_sns_topic_arn
USE_AWS=true

Note: If AWS is not configured, the app falls back to local in-memory storage.

6. Run the Application
python app.py
OR
flask run
The server will start at: http://127.0.0.1:5000

☁️ AWS Setup (For Deployment)
DynamoDB Tables
Users Table: travelgo_users (Primary key: email [String])

Bookings Table: travelgo_bookings (Primary key: booking_id [String])

SNS Topic
Create a topic named travelgo_notifications and subscribe your email address to receive updates.

🚢 Deployment
For production on AWS EC2, use a WSGI server like gunicorn:

pip install gunicorn
gunicorn --bind 0.0.0.0:8000 app:app
💻 Technologies Used
Backend: Python, Flask

Cloud: AWS DynamoDB, AWS SNS

Frontend: HTML5, CSS3
