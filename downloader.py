import os
import requests
import cfscrape
from yaspin import yaspin
from yaspin.spinners import Spinners
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

print('\n ------------------------------\n|                              |\n|  KissAnime Batch Downloader  |\n|                              |\n| Made With ❤️  By Ravi Jotwani |\n|                              |\n ------------------------------\n')

anime_url = ''
while True:
    anime_url = input('Please paste the KissAnime URL for the show you would like to download.\nNote: this program only works with kissanime.ac, not kissanime.ru\n\n')
    if isinstance(anime_url, str) and len(anime_url) > 26 and anime_url[:27] == 'https://kissanime.ac/Anime/':
        break
    print('Please enter a valid https://kissanime.ac URL.\n')

spinner = yaspin(Spinners.bouncingBall, text='Scraping data from KissAnime...')
spinner.start()
scraper = cfscrape.create_scraper()
main_page = str(scraper.get(anime_url).content)
soup = BeautifulSoup(main_page, 'html.parser')

show_title = soup.select('.bigChar')[0].get_text()
kissanime_url_list = soup.select('.episodeList .full div div h3 a')
kissanime_urls = [url.get('href') for url in kissanime_url_list]
episode_names = [url.get_text() for url in kissanime_url_list]

kissanime_urls.reverse()
episode_names.reverse()
num_episodes = len(episode_names)

spinner.stop()
print('\nFound ' + str(num_episodes) + " episodes for '" + show_title + "'\n")

start_episode = 0
while True:
    start_episode = eval(input('Which episode would you like to start the download at?  '))
    if isinstance(start_episode, int) and start_episode > 0 and start_episode <= num_episodes:
        break
    elif not isinstance(start_episode, int):
        print('The episode number must be an integer. Please try again\n')
    else:
        print(show_title + ' has ' + str(num_episodes) + ' episodes.\nPlease enter a number between 1 and ' + str(num_episodes) + '.\n')

end_episode = 0
while True:
    end_episode = eval(input('Which episode would you like to end the download at?    '))
    if isinstance(end_episode, int) and end_episode >= start_episode and end_episode <= num_episodes:
        break
    elif not isinstance(end_episode, int):
        print('The episode number must be an integer. Please try again\n')
    else:
        print('You chose to start the download at episode ' + str(start_episode) + ' and ' + show_title + ' has ' + str(num_episodes) + ' episodes.\nPlease enter a number between ' + start_episode + ' and ' + num_episodes + '.\n')

start_episode -= 1
kissanime_urls = kissanime_urls[start_episode:end_episode]
episode_names = episode_names[start_episode:end_episode]
num_episodes = len(episode_names)

print('')
spinner = yaspin(Spinners.bouncingBall)
if num_episodes == 1:
    spinner.text = 'Gathering video source...'
else:
    spinner.text = 'Gathering video sources...'
spinner.start()

urls = []
tokens, user_agent = cfscrape.get_tokens(anime_url)
chrome_path = os.getcwd() + '/chromedriver'
options = Options()
options.add_argument(f'user-agent={user_agent}')
driver = webdriver.Chrome(executable_path=chrome_path, chrome_options=options)

for kissanime_url in kissanime_urls:
    driver.get(kissanime_url)
    driver.delete_all_cookies()
    for token in tokens:
        driver.add_cookie({'name':token, 'value':tokens[token], 'path':'/'})
    WebDriverWait(driver, 120).until(EC.presence_of_element_located((By.ID, 'player_html5_html5_api')))
    video = driver.find_element_by_id('player_html5_html5_api')
    url = video.get_attribute('src')
    urls.append(url.replace('&amp;', '&'))

driver.quit()
spinner.stop()
print('Found video source for:')
[print(episode_name) for episode_name in episode_names]

if num_episodes == 1:
  print('\nDownloading ' + str(num_episodes) + ' ' + show_title + ' episode~\n')
else:
  print('\nDownloading ' + str(num_episodes) + ' ' + show_title + ' episodes~\n')

try:
  os.makedirs(show_title)
  print("Created folder '" + show_title + "'\nin directory " + os.getcwd() + '\n')
except:
  print("It seems you already have a folder named '" + show_title + "'\nYour download will be placed in this folder.\n")

for i in range(len(urls)):
    with open(show_title + '/' + episode_names[i] + '.mp4', 'wb') as handle:
        r = requests.get(urls[i], stream=True)
        spinner = yaspin(text='Downloading ' + episode_names[i])
        spinner.spinner = Spinners.bouncingBall
        spinner.start()
        if not r.ok:
            print('Could not download ' + episode_names[i] + '.')
            continue
        else:
            for block in r.iter_content(1024):
                if not block:
                    break
                handle.write(block)
        spinner.stop()
        print(episode_names[i] + ' downloaded.\n')
print("Your show has been downloaded. Enjoy!\n")
