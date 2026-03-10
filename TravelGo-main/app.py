from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import random
import boto3
import os
from botocore.exceptions import NoCredentialsError

app = Flask(__name__)
app.secret_key = "travelgo_secret"

# -------------------------
# Local fallback storage
# -------------------------
local_users = []
local_bookings = []

# -------------------------
# Cities list
# -------------------------
cities = [
    "Bangalore",
    "Delhi",
    "Mumbai",
    "Chennai",
    "Hyderabad",
    "Kolkata"
]

# -------------------------
# AWS Configuration
# -------------------------
region = os.getenv("AWS_REGION", "us-east-1")
sns_topic_arn = os.getenv("SNS_TOPIC_ARN")

#AWS_AVAILABLE = True

try:
    dynamodb = boto3.resource("dynamodb", region_name=region)
    users_table = dynamodb.Table("travelgo_users")
    bookings_table = dynamodb.Table("travelgo_bookings")
    sns = boto3.client("sns", region_name=region)
except NoCredentialsError:
    AWS_AVAILABLE = False


# -------------------------
# SNS Notification Helper
# -------------------------
def send_notification(message):

    if not sns_topic_arn:
        return

    try:
        sns.publish(
            TopicArn=sns_topic_arn,
            Message=message,
            Subject="TravelGo Notification"
        )
    except Exception as e:
        print("SNS error:", e)


# -------------------------
# Routes
# -------------------------

@app.route('/')
def home():
    return render_template("home.html")


@app.route('/register', methods=["GET", "POST"])
def register():

    if request.method == "POST":

        email = request.form['email']
        password = request.form['password']

        hashed_password = generate_password_hash(password)

        try:
            users_table.put_item(
                Item={
                    "email": email,
                    "password": hashed_password
                }
            )
        except NoCredentialsError:
            local_users.append({
                "email": email,
                "password": hashed_password
            })

        return redirect("/login")

    return render_template("register.html")


@app.route('/login', methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form['email']
        password = request.form['password']

        try:

            response = users_table.get_item(Key={"email": email})
            user = response.get("Item")

        except NoCredentialsError:

            user = next((u for u in local_users if u["email"] == email), None)

        if user and check_password_hash(user["password"], password):
            session['user'] = email
            return redirect("/dashboard")

        return "Invalid email or password"

    return render_template("login.html")


@app.route('/dashboard')
def dashboard():

    if 'user' not in session:
        return redirect("/login")

    return render_template("dashboard.html")


@app.route('/booking', methods=["GET", "POST"])
def booking():

    if 'user' not in session:
        return redirect("/login")

    if request.method == "POST":

        transport = request.form['transport']
        source = request.form['source']
        destination = request.form['destination']
        date = request.form['date']

        if source == destination:
            return "Source and destination cannot be the same"

        booking_id = str(uuid.uuid4())

        seat = f"S{random.randint(1,40)}"

        if transport == "Bus":
            price = random.randint(400, 1200)
        elif transport == "Train":
            price = random.randint(600, 1800)
        elif transport == "Flight":
            price = random.randint(3000, 9000)
        else:
            price = random.randint(1500, 7000)

        booking_data = {
            "booking_id": booking_id,
            "user": session['user'],
            "transport": transport,
            "source": source,
            "destination": destination,
            "date": date,
            "seat": seat,
            "price": price,
            "status": "CONFIRMED"
        }

        try:
            bookings_table.put_item(Item=booking_data)
        except NoCredentialsError:
            local_bookings.append(booking_data)

        send_notification(
            f"Booking confirmed!\n"
            f"{transport} from {source} to {destination}\n"
            f"Date: {date}\n"
            f"Seat: {seat}\n"
            f"Price: ₹{price}"
        )

        return redirect("/history")

    return render_template("booking.html", cities=cities)


@app.route('/history')
def history():

    if 'user' not in session:
        return redirect("/login")

    try:

        response = bookings_table.scan()

        user_bookings = [
            b for b in response["Items"]
            if b["user"] == session['user']
        ]

    except NoCredentialsError:

        user_bookings = [
            b for b in local_bookings
            if b["user"] == session['user']
        ]

    return render_template("history.html", bookings=user_bookings)


@app.route('/cancel/<booking_id>')
def cancel_booking(booking_id):

    if 'user' not in session:
        return redirect("/login")

    try:

        bookings_table.update_item(
            Key={"booking_id": booking_id},
            UpdateExpression="SET #s = :s",
            ExpressionAttributeNames={"#s": "status"},
            ExpressionAttributeValues={":s": "CANCELLED"}
        )

    except NoCredentialsError:

        for booking in local_bookings:
            if booking["booking_id"] == booking_id:
                booking["status"] = "CANCELLED"

    send_notification(f"Booking {booking_id} has been cancelled.")

    return redirect("/history")


@app.route('/logout')
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)