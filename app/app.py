from flask import Flask, render_template, request
import requests
import re
from bs4 import BeautifulSoup
from operator import itemgetter

list_of_spaceship = [] #global list of spaceship, need to be reinitialize everytime you want to retrieve the list, otherwise you will have double value
app = Flask(__name__)

def get_urls_and_vehicules_list(table):
    #get the urls to get data from and the list of all the starwars vehicules
    vehicules = []
    urls = []
    for a in table.find_all('a', href=True, title=True):
        base_url = 'https://starwars.fandom.com'
        url = base_url + a['href']
        urls.append(url)
        vehicules.append(a['title'])

    return vehicules, urls

def extract_text_from_html(html, type_class):
    #extract and apply some changes to the text in order to format it correctly
    text = html.find('div').get_text()
    res = text.split("[",maxsplit=1)[0]
    res = res.split("(",maxsplit=1)[0]
    if type_class == "hyperdrive" and 'Class' in res: #get only the number from the text
        res = re.findall('\d*\.?\d+',res)[0]
    return res

def save_to_list(tuple):
    #save tuple into the global list_of_spaceship
    if not tuple[1].startswith('None'): #dont add to the list if None in tuple
        list_of_spaceship.append(tuple)

def sort_list(list):
    #sort list of tuple with the hyperdrive rating from fastest to slowest
    list.sort(key=itemgetter(1))

def extract_and_save_hyperdrive_spaceships(vehicules, urls):
    #For each url we look if we can get the hyperdrive rating (hyperdrive variable) and if we can't, we look if the starship has a hyperdrive system (hdsystem variable)
    # Then we save the starship and the variable(hyperdrive or hdsystem into a global list called list_of_spaceships) 
    i = 0
    for i in range(len(urls)):
        response_url = requests.get(urls[i])
        soup_url = BeautifulSoup(response_url.text, 'html.parser')
        hyperdrive = soup_url.find_all('div', {"data-source": "hyperdrive"})
        hdsystem = soup_url.find_all('div', {"data-source": "hdsystem"})
        if hyperdrive:
            hyperdrive_class = extract_text_from_html(hyperdrive[0], "hyperdrive")
            save_to_list((vehicules[i], hyperdrive_class))
        if hdsystem and not hyperdrive:
            hdsystem_class = extract_text_from_html(hdsystem[0], "hdsystem")
            save_to_list((vehicules[i], hdsystem_class))


@app.route("/get_starships/", methods=['POST'])
def start_request():
    #Get the vehicules name + url to request
    #Then Extract the data from url and save it into a list
    #Finally we sort the list of tuple and display it on the starships_ranking.html template
    #Starships are ranked from fastest to slowest in case we know the hyperdrive rating, otherwise we just show that the starship has a hyperdrive system
    res = requests.get('https://starwars.fandom.com/wiki/Databank_(website)')
    soup = BeautifulSoup(res.text, 'html.parser')
    table = soup.find_all('table')[12] # Grab the Vehicule table 
    vehicules, urls = get_urls_and_vehicules_list(table)
    extract_and_save_hyperdrive_spaceships(vehicules, urls)
    sort_list(list_of_spaceship)
    return render_template('starships_ranking.html', list_of_spaceship=list_of_spaceship);


@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.debug = True
    app.run()
