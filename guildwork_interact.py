from bs4 import  BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import  Keys
import datetime
from tqdm import *
from config import *

class GuildworkInteract(object):

    def __init__(self,domain):
        self.driver = webdriver.Chrome(VCHROME)
        #self.driver = webdriver.PhantomJS(VPHANTOMJS)
        self.driver.set_window_size(1120,550)
        self.domain = domain
        self.guildwork_url = 'http://%s' % domain


    def login(self, user, password):
        """Logs into a Guildwork page and initializes the webdriver for this class
        Args:
            User - email address
            Password

        Returns:
            None
        """
        login_page = self.guildwork_url + '/login'
        d = self.driver
        d.get(login_page)
        elem = d.find_element_by_name('email')
        elem.clear()
        elem.send_keys(user)
        elem = d.find_element_by_name('password')
        elem.clear()
        elem.send_keys(password)
        elem.send_keys(Keys.RETURN)


    def scrape_recruitment(self):
        """
        Scrapes the Guildwork recruitment page application table

        Returns:
            A list of all dictionaries representing application data
        """
        d = self.driver
        recruitment_page = self.guildwork_url + '/recruitment'
        d.get(recruitment_page)
        soup = BeautifulSoup(d.page_source, 'lxml')
        apps = soup.find('table', {'id': 'applications'})

        all_apps = []
        for row in tqdm(apps.find_all('tr')):
            if not (row.find('th', {'class':'header'})):
                name_field = row.find('a', href=True)
                app_url = self.guildwork_url + name_field.get('href')
                app_name =  name_field.text
                app_status = row.find('span',{'class':'label'}).text

                # Note that this is only returning information on accepted applications
                if (app_status == 'Accepted'):
                    d.get(app_url)
                    soup = BeautifulSoup(d.page_source, 'lxml')
                    timestamp = soup.find('span', attrs={'data-timestamp': True})['data-timestamp']

                    app_data = {
                        'url' : app_url,
                        'name' : app_name,
                        'joined' : datetime.datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S'),
                        'lodestone_link' : soup.find('label',text='Lodestone Link').find_next('div').text.strip()

                    }
                    all_apps.append(app_data)
        d.close()
        return all_apps


    def print_items(self, data):
        for item in data:
            print (item)


if __name__ == '__main__':
    session = GuildworkInteract(DOMAIN)
    session.login(EMAIL,PASSWORD)
    data = session.scrape_recruitment()
    session.print_items(data)