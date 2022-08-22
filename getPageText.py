import time

import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver

xl_name = "scrapedList.xlsx"
sheet_name = "URLs"
listdocument = pd.read_excel(xl_name, engine='openpyxl', sheet_name="URLs")
toScrape = listdocument['URL'].tolist()  # takes links from URL column into python list for easier manipulation
scrapedtitles = []


# iterates through list of links, retrieves text displayed to the user
def scrape(links):
    for index, url in enumerate(links):
        # url = "http://" + url #for lists without protocol appended
        printOutput = []

        browser = webdriver.PhantomJS()
        browser.get(url)
        html = browser.page_source
        soup = BeautifulSoup(html, 'lxml')
        a = soup.find_all('script')
        a = str(a)

        try:
            url = requests.get(
                url)  # makes a request to a url in the list, try and switch to a better browser agent using urlib.request to avoid 403 errors
            url_content = url.content
            time.sleep(
                5)
            soup_url = BeautifulSoup(url_content,
                                     'html.parser')  # initialise beautifulsoup, it is later called via soup_url
            text = soup_url.get_text(" ",
                                     strip=True)  # extracts text from page, does not work 100% of the time but has a higher success rate than other methods
            with open("file%d.txt" % index, "w", encoding="utf-8") as f:  # creates new text file with text from url
                f.write(str(text))  # + "\n",
            scrapedtitles.append("file%d.txt" % index)
            printOutput.append(text)
            print(scrapedtitles)
        # print(printOutput)

        except requests.exceptions.ConnectionError:  # skips the url if the connection fails
            requests.status_code = "Connection refused"
            scrapedtitles.append("Connection refused")
            continue


def updateExcel(urllst, txtlst):
    tuple(urllst)
    tuple(txtlst)
    # Load list to dataframe
    df = pd.DataFrame(list(zip(urllst, txtlst)), columns=('URL', 'Text'))  #
    df.index += 1  # responsible for the 55/56 error as well as the int/str/int error

    # Write dataframe to excel
    xlw = pd.ExcelWriter(xl_name)
    df.to_excel(xlw, sheet_name=sheet_name, index_label="#", columns=["URL", "Text"])
    xlw.save()


print(scrape(toScrape))

updateExcel(toScrape, scrapedtitles)
