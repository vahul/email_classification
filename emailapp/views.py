from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.http import HttpResponse
import os
import base64
from datetime import datetime,timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from bs4 import BeautifulSoup
from langchain_groq import ChatGroq
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
llm = ChatGroq(
        model="llama-3.1-70b-versatile",
        temperature=0,
        groq_api_key='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'
    )

# Configure ChatGroq
def classify_email(email):
    query = f"What class does this email belong to in the classes Finance, Social, News, Health, Promotions, Job Offers just give me the name ? Email: {email}"
    response = llm.invoke(query)
    return response.content


# Get Gmail service
def get_gmail_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)
def summarize(text):
    query=f'give me the overall summary and also mention the key points of the mail {text} and if the mail is empty then say that the mail is empty '
    t=llm.invoke(query)
    return t.content

# Fetch today's emails
def get_todays_emails(service):
    today_midnight = (datetime.now() - timedelta(hours=8)).replace(hour=0, minute=0, second=0, microsecond=0)
    print(today_midnight)    
    query = f"after:{int(today_midnight.timestamp())}"
    try:
        results = service.users().messages().list(userId='me', q=query).execute()
        messages = results.get('messages', [])
        emails = []
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            headers = msg.get('payload', {}).get('headers', [])

            email_data = {'sender': 'Unknown', 'subject': 'No Subject', 'body': 'No Content'}

            for header in headers:
                if header['name'] == 'From':
                    email_data['sender'] = header['value']
                elif header['name'] == 'Subject':
                    email_data['subject'] = header['value']

            parts = msg.get('payload', {}).get('parts', [])
            for part in parts:
                if part['mimeType'] == 'text/plain':
                    body_data = part.get('body', {}).get('data', '')
                    if body_data:
                        email_data['body'] = base64.urlsafe_b64decode(body_data).decode('utf-8')
                        break
                elif part['mimeType'] == 'text/html':
                    body_data = part.get('body', {}).get('data', '')
                    if body_data:
                        decoded_body = base64.urlsafe_b64decode(body_data).decode('utf-8')
                        email_data['body'] = BeautifulSoup(decoded_body, 'html.parser').get_text()
                        break
            email_data['body']=summarize(email_data['body'])
            # Classify the email and add classification to the email data
            email_text = email_data['subject'] + " " + email_data['body']
            email_data['classification'] = classify_email(email_text)

            emails.append(email_data)
        return emails
    except Exception as error:
        print(f"Error fetching emails: {error}")
        return []



def login_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'emailapp/login.html', {'form': form})


def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'emailapp/signup.html', {'form': form})


def home_view(request):
    return render(request, 'emailapp/index.html')


def classify_view(request):
    service = get_gmail_service()
    emails = get_todays_emails(service)
    for email in emails:
        email_text = email['subject'] + " " + email['body']
        email['classification'] = classify_email(email_text)

        # Save to the database
        Email.objects.create(
            sender=email['sender'],
            subject=email['subject'],
            body=email['body'],
            classification=email['classification']
        )

    return render(request, 'emailapp/allmails.html', {'emails': emails})

def categorized_emails_view(request, category):
    service = get_gmail_service()
    emails = get_todays_emails(service)
    categorized_emails = [email for email in emails if category.lower() in email['classification'].lower()]
    return render(request, f'emailapp/{category}_emails.html', {'emails': categorized_emails})

from django.shortcuts import render
from .models import Email

def finance_emails(request):
    emails = Email.objects.filter(classification='Finance')
    return render(request, 'emailapp/finance_emails.html', {'emails': emails})

def social_emails(request):
    emails = Email.objects.filter(classification='Social')
    return render(request, 'emailapp/social_emails.html', {'emails': emails})

def news_emails(request):
    emails = Email.objects.filter(classification='News')
    return render(request, 'emailapp/news_emails.html', {'emails': emails})

def health_emails(request):
    emails = Email.objects.filter(classification='Health')
    return render(request, 'emailapp/health_emails.html', {'emails': emails})

def promotions_emails(request):
    emails = Email.objects.filter(classification='Promotions')
    return render(request, 'emailapp/promotions_emails.html', {'emails': emails})

def job_emails(request):
    emails = Email.objects.filter(classification='Job Offers')
    return render(request, 'emailapp/job_emails.html', {'emails': emails})
