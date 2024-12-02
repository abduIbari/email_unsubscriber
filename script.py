from dotenv import load_dotenv
import os
import email
import imaplib
from bs4 import BeautifulSoup
import requests

load_dotenv()

username = os.getenv("EMAIL")
password = os.getenv("PASSWORD")


def connect_mail():
  mail = imaplib.IMAP4_SSL("imap.gmail.com")
  mail.login(username, password)
  mail.select("inbox")
  return mail

def extract_unsubscribe_links(html_content):
  soup = BeautifulSoup(html_content, "html.parser")

  # filter out all the links where there is a link in the a tag that contains the string "unsubscribe"
  links = [link["href"] for link in soup.find_all("a", href=True) if "unsubscribe" in link["href"].lower()]
  return links

def click_link(link):
  try:
    response = requests.get(link)
    if response.status_code == 200:
      print("Successfully clicked" + link)
    else:
      print("Failed to click" + link)
  except Exception as e:
    print("Error with", link, str(e))


def search_for_email():
    mail = connect_mail()
    _, data = mail.search(None, '(BODY "unsubscribe")')
    
    if not data[0]:
        print("No emails found with 'unsubscribe' in the body.")
        return []

    links = []
    for email_id in data[0].split():
        _, data = mail.fetch(email_id, '(RFC822)')
        email_message = email.message_from_bytes(data[0][1])

        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                if content_type == "text/html":
                    html_part = part.get_payload(decode=True)
                    if html_part:
                        html_part = html_part.decode(errors='ignore')
                        links.extend(extract_unsubscribe_links(html_content=html_part))
        else:
            content_type = email_message.get_content_type()
            content = email_message.get_payload(decode=True)
            if content:
                content = content.decode(errors='ignore')
                if content_type == "text/html":
                    links.extend(extract_unsubscribe_links(html_content=content))

    print("Final Extracted Links:", links)
    mail.logout()
    return links


def save_links(links):
  with open("links.txt", "w") as l:
    l.write("\n".join(links))


links = search_for_email()
for link in links:
  click_link(link=link)

save_links(links=links)
