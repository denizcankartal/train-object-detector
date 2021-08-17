from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from time import sleep
from urllib.request import urlretrieve
from bs4 import BeautifulSoup as bs
from argparse import ArgumentParser
import sys
import os

def convertableToInteger(x):
    try:
        int(x)
        return True
    except ValueError:
        return False


def create_chrome_driver(chrome_driver_path):
    # chrome driver in headless mode
    # for headfull mode, do not create the chrome_options object
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_driver = webdriver.Chrome(options=chrome_options, executable_path=chrome_driver_path)
    
    return chrome_driver


def get_page_source(chrome_driver, search_keyword, load_level):
    # go to google images url
    chrome_driver.get('https://www.google.de/imghp?hl=en&ogbl')
    # get the google search form
    google_search_form = chrome_driver.find_element_by_id('searchform')
    # get the google search input inside google search form
    google_search_input = google_search_form.find_element_by_tag_name('input')
    # write on google search input
    google_search_input.send_keys(search_keyword)
    # hit enter to search
    google_search_input.send_keys(Keys.RETURN)
    # execute javascipt to move the page down to load more images
    num_of_loads = int(load_level) - 1
    for _ in range(num_of_loads):
        print("loading more images")
        chrome_driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        sleep(4)

    sleep(2)
    # return the source HTML of the page
    return chrome_driver.page_source


def get_img_divs(page_source):
    # get the body element
    soup = bs(page_source, 'html.parser')
    body = soup.find(name="body")

    # get the div tag which contains all the div containers of images as parent
    div = body.find("div", id="islrg").find("div", class_="islrc")

    # get all the divs inside div, aka child divs
    # those divs have the image elements
    divs = div.find_all("div", recursive=False)

    # get only the divs that has an image element as a child
    # every div, which has the img element, has a data-ved attribute
    # for more info check out tree structure of the html source
    img_divs = [div for div in divs if div.has_attr("data-ved")]

    return img_divs


def get_image_links(img_divs):
    # some img elements' attribute is src
    # some has data-src as an attribute
    # src or data-src attribute contain the image link
    links = []

    print("Getting inside of each div container to get the link of each image")

    for div in img_divs:
        img_element = div.a.div.img
        if img_element.has_attr("src"):
            links.append(img_element["src"])
        elif img_element.has_attr("data-src"):
            links.append(img_element["data-src"])
        else:
            print('Could not find the image link for the current image, because img element does not contain "src" or "data-src" attribute.')
    
    print("Amount of links gathered: {}".format(str(len(links))))
    return links


def install_images(links, search_keyword, folder_name):
    print("Starting to instal {} images to {}".format(search_keyword,folder_name))

    if not os.path.exists(folder_name):
        sys.exit("{} is not existed please provide an existing path to load the images")
    
    for idx, link in enumerate(links):
        img_path = "{}/{}-{}.jpg".format(folder_name, search_keyword, idx)
        urlretrieve(link, img_path)
    
    print("Amount of images installed: {}".format(str(len(links))))


def main():
    parser = ArgumentParser()

    parser.add_argument("-c", "--chromedriver", required=True,
                        help="Chromedriver executable path.")
    parser.add_argument("-k", "--keyword", required=True,
                        help="Search keyword to search image on google images.")
    parser.add_argument("-o", "--output", required=True,
                        help="Output path to write the images in.")
    parser.add_argument("-l", "--level", required=True,
                        help="Amount of images installed is proportional to the level. Must be an integer, ranging from 1 to 5.")

    args = vars(parser.parse_args())

    if(not convertableToInteger(args["level"])):
        sys.exit("--level argument must be an integer between 1 and 5")

    # create the chrome driver in headless mode
    chrome_driver = create_chrome_driver(args["chromedriver"])

    # get page source, HTML
    page_source = get_page_source(chrome_driver, args["keyword"], args["level"])

    # get divs that has all the image elements inside
    img_divs = get_img_divs(page_source)

    # get the image links
    links = get_image_links(img_divs)

    # install images using the links
    install_images(links, args["keyword"], args["output"])


if __name__ == "__main__":
    main()