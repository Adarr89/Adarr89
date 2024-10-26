#Getting to the desired page with the flights loaded

from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import datetime as dt

options = webdriver.ChromeOptions()
#options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

driver.get("https://www.google.com/travel/flights")
driver.implicitly_wait(5)
from_location = "London"
destination = "Sao Paolo"
travel_date = "15/06/2025"


# Click trip dropdown
driver.find_element(By.XPATH, "/html/body/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div[1]/div[1]/div/div[1]/div[1]/div/div/div/div[1]/div").click()
# Click One-way
driver.find_element(By.XPATH, "/html/body/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div[1]/div[1]/div/div[1]/div[1]/div/div/div/div[2]/ul/li[2]").click()

# Click on From part of trip
driver.find_element(By.XPATH, "/html/body/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div[1]/div[1]/div/div[2]/div[1]/div[1]/div/div/div[1]/div/div/input").click()
driver.find_element(By.XPATH, "/html/body/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div[1]/div[1]/div/div[2]/div[1]/div[6]/div[2]/div[2]/div[1]/div/input").send_keys(from_location)

# Click correct city 
driver.find_element(By.XPATH, "/html/body/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div[1]/div[1]/div/div[2]/div[1]/div[6]/div[3]/ul/li[1]/div[2]/div[1]/div").click()

# Send value to destination part of trip
driver.find_element(By.XPATH, "/html/body/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div[1]/div[1]/div/div[2]/div[1]/div[4]/div/div/div[1]/div/div/input").send_keys(destination)

# Click correct city
driver.find_element(By.XPATH, "/html/body/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div[1]/div[1]/div/div[2]/div[1]/div[6]/div[3]/ul/li[1]/div[2]/div[1]/div").click()

# Send Key to departure date
driver.find_element(By.XPATH, "/html/body/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div[1]/div[1]/div/div[2]/div[2]/div/div/div[1]/div/div/div[1]/div/div[1]/div/input").send_keys(travel_date)

# Click Explore
driver.find_element(By.XPATH, "/html/body/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div[1]/div[2]/div/button").click()

time.sleep(5)
with open("htmlpage.html", "w") as html:
    html.write(driver.page_source)

driver.quit()

#Reading the HTML with BeautfiulSoup4 to extract the data


from bs4 import BeautifulSoup
import csv
import re
import pandas


#Creating a BeautifulSoup object for the parsing process
prices_csv = []
ftp = { "Departure time" : [],
                         "Price" : [],
                         "Travel time" : [],
                         "Airline" : []}
flight_element_class = "pIav2d"
with open("htmlpage.html") as html:
    soup = BeautifulSoup(html, "html5lib")
    flights_html_lists = soup.find_all(attrs={"class" : flight_element_class})



for indx, element in enumerate(flights_html_lists):
    for tag in element.find_all(attrs={"aria-label" : re.compile(r"^Departure time")}):
        departure_Time = tag.get_text()
    for tag in element.find_all(attrs={"aria-label" : re.compile(r"\b\d+ British pounds\b")}):
        price = tag.get_text()
    for tag in element.find_all("span", string=re.compile(r"\b\d+ hr \d+ min\b")):
        print(tag.get_text())

        travel_Time = tag.get_text()
    for tag in element.find_all("span", attrs={"class" : "h1fkLb"}):
        airline = tag.get_text()
    ftp["Departure time"].append(departure_Time)
    ftp["Price"].append(price)
    ftp["Travel time"].append(travel_Time)
    ftp["Airline"].append(airline)

data = pandas.DataFrame.from_dict(data=ftp)
data.to_csv("Flights.csv", index=False)


