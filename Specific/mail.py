import smtplib


class Email:
  def __init__(self, sender, sender_pw, recievers, subject, text):
    self.sender = sender
    self.sender_pw = sender_pw
    self.recievers = recievers
    self.subject = subject
    self.text = text


  def send_email(self):
    message = f'From: {self.sender}\nTo: {", ".join(self.recievers)}\nSubject: {self.subject}\n\n{self.text}'

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.login(self.sender, self.sender_pw)
    server.sendmail(self.sender, self.recievers, message)
    server.close()