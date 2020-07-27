# coding=utf-8

from splinter import Browser
from subprocess import call
from time import time, sleep


# refresh limit (seconds)
limit = 60

# request URL
url = "https://service.berlin.de/terminvereinbarung/termin/tag.php?dienstleister=122219&herkunft=http%3A%2F%2Fservice.berlin.de%2Fstandort%2F122219%2F&termin=1&anliegen%5B%5D=120686"

# who to send notifications to
recipients = ["name@provider.com", "name.alternative@proider.com"]

# who sends the notifications
sender = "name@provider.com"

# mail subject
subject = "Notifier: Free dates at Bezirksamt"

# message template
msg_template = """Found free dates:\n\n<DATES>.\n\n
Click here to quickly book appointment:\n\n<URL>"""

# location of the mailer script
# assumes mailer script to be called with API
# SCRIPT <recipient_list> <subject> <msg> <sender>
mailer_script_location = "./sendmail.sh"


def notify(dates):
    """ Notifier: uses shell script to send mail to recipients with the dates."""

    dates_str = "\n".join([" ".join(map(str, date)) for date in dates])
    msg = msg_template.replace("<DATES>", dates_str).replace("<URL>", url)
    cmd = [
        mailer_script_location,
        ",".join(recipients),
        subject,
        msg,
        sender,
    ]
    call(cmd)


class Session:
    def __init__(self, browser="chrome"):
        self.browser = Browser(browser)
        self.last_reloaded = time()
        self.browser.visit(url)

    def reload(self):
        """Reloads the URL"""

        while time() - self.last_reloaded < limit:
            sleep(1)
        self.last_reloaded = time()
        self.browser.visit(url)

    def search(self):
        """Searches the returned HTML page for free appointment dates.
           Check current website to see whether the HTML element class is the correct one"""

        print("Start new search")
        found = False
        collected = []
        for table in self.browser.find_by_css(".calendar-month-table"):
            month = table.find_by_css("th.month").text.strip()
            for field in table.find_by_tag("td"):
                cls = field["class"]

                # check whether appointment is bookable
                # might be different for different services
                if cls and "buchbar" in cls and ("nichtbuchbar" not in cls):
                    day = int(field.text)
                    date = day, month
                    collected.append(date)
                    found = True
        if found:
            notify(collected)
        return found


if __name__ == "__main__":
    session = Session()
    while True:
        if session.search():
            input()
        session.reload()
