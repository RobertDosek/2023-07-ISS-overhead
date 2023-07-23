import requests
from datetime import datetime
import smtplib
from time import sleep

MY_LATITUDE = 50.095050
MY_LONGITUDE = 14.465340
LOCAL_UTC_OFFSET = datetime.now().hour - datetime.utcnow().hour
SEND_EMAIL = "robert.d.python@gmail.com"
GMPSW = "mgtszwmykzrvkzkkx"
RECEIVE_EMAIL = "robert-dosek@seznam.cz"


def utc_to_local(utc_hour):
    utc_hour += LOCAL_UTC_OFFSET
    if LOCAL_UTC_OFFSET > 0:
        if utc_hour > 23:
            utc_hour -= 24
    elif LOCAL_UTC_OFFSET < 0:
        if utc_hour < 0:
            utc_hour += 24
    return utc_hour


def is_iss_overhead():
    response = requests.get(url="http://api.open-notify.org/iss-now.json")
    response.raise_for_status()
    data = response.json()

    iss_latitude = float(data["iss_position"]["latitude"])
    iss_longitude = float(data["iss_position"]["longitude"])

    if MY_LATITUDE-5 <= iss_latitude <= MY_LATITUDE+5 and MY_LONGITUDE-5 <= iss_longitude <= MY_LONGITUDE+5:
        return True


def is_night():
    parameters = {
        "lat": MY_LATITUDE,
        "lng": MY_LONGITUDE,
        "formatted": 0,
    }

    response = requests.get("https://api.sunrise-sunset.org/json", params=parameters)
    response.raise_for_status()
    data = response.json()
    utc_sunrise = int(data["results"]["sunrise"].split("T")[1].split(":")[0])
    utc_sunset = int(data["results"]["sunset"].split("T")[1].split(":")[0])

    lt_sunrise = utc_to_local(utc_sunrise)
    lt_sunset = utc_to_local(utc_sunset)

    time_now = datetime.now().hour

    if time_now >= lt_sunset or time_now <= lt_sunrise:
        return True


while True:
    if is_iss_overhead() and is_night():

        with open(f"email.txt.txt") as letter:
            content = letter.read()

        with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
            connection.starttls()
            connection.login(user=SEND_EMAIL, password=GMPSW)
            connection.sendmail(
                from_addr=SEND_EMAIL,
                to_addrs=RECEIVE_EMAIL,
                msg=f"Subject:Look up!! ISS overhear\n\n{content}"
            )
    else:
        print("waiting")
        sleep(60)

