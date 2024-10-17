from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import time
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.mime.text import MIMEText

# Lists to store job details
links = []
job_titles = []
companies = []
locations = []
descriptions = []

# Initialize the Chrome driver
service = Service("C:/Users/Ghulam e Mustafa/OneDrive/Documents/chromedriver.exe")
driver = webdriver.Chrome(service=service)

# Define the number of pages to scrape
number_of_pages = 10  # Adjust this number as needed

# Loop through the specified range of pages
for page_number in range(number_of_pages):
    # Construct the URL for the current page
    url = f'https://www.indeed.com/jobs?q=usa&start={page_number * 10}'
    driver.get(url)
    time.sleep(5)  # Wait for the page to load

    # Parse the page source with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, "lxml")
    box = soup.find_all("div", class_="job_seen_beacon")

    # Check if job listings are found
    if not box:
        print(f"No job listings found on page {page_number + 1}.")
        break

    # Loop through each job listing to extract information
    for i in box:
        try:
            link = i.find('a').get('href')
            links.append(f"https://www.indeed.com{link}")  # Construct the full URL
        except AttributeError:
            links.append(None)

        try:
            job_title = i.find('a', class_='jcs-JobTitle css-1baag51 eu4oa1w0').text.strip()
            job_titles.append(job_title)
        except AttributeError:
            job_titles.append(None)

        try:
            company = i.find('span', class_='css-1h7lukg eu4oa1w0').text.strip()
            companies.append(company)
        except AttributeError:
            companies.append(None)

        try:
            location = i.find('div', class_='css-1restlb eu4oa1w0').text.strip()
            locations.append(location)
        except AttributeError:
            locations.append(None)

        try:
            description = i.find('div', class_='jobMetaDataGroup css-qspwa8 eu4oa1w0').text.strip()
            descriptions.append(description)
        except AttributeError:
            descriptions.append(None)

    print(f"Scraped {len(box)} jobs from page {page_number + 1}.")  # Print the number of jobs scraped

# Close the browser after scraping
driver.quit()

# Create a DataFrame with the extracted data
csv_filename = 'indeed_jobs.csv'
job_data = pd.DataFrame({
    'Job Title': job_titles,
    'Company': companies,
    'Location': locations,
    'Description': descriptions,
    'Link': links
})

# Save the data to a CSV file
job_data.to_csv(csv_filename, index=False)
print(f"Data saved to {csv_filename}")

# Email the CSV file using SMTP
def send_email_with_attachment(to_email, subject, body, attachment_path):
    # Email credentials
    from_email = 'gmpatel404@gmail.com'  # Replace with your email
    password = 'siya oprc klmr jdju'  # Replace with your email password

    # Set up the MIME
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    # Attach the body with the msg instance
    msg.attach(MIMEText(body, 'plain'))

    # Open the file to be sent
    with open(attachment_path, "rb") as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={attachment_path}')
        msg.attach(part)

    # Send the email
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()  # Upgrade the connection to a secure encrypted SSL/TLS
        server.login(from_email, password)  # Log in to your email account
        server.send_message(msg)  # Send the email

    print(f"Email sent to {to_email} with attachment {attachment_path}.")

# Usage
send_email_with_attachment(
    to_email='gmpatel404@gmail.com',  # Replace with the recipient's email
    subject='Scraped Job Listings',
    body='Please find the attached job listings CSV file.',
    attachment_path=csv_filename
)
