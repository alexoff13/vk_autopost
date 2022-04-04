from itertools import count
import pandas as pd
import vk_api
import time
from selenium import webdriver


posts = pd.read_excel('posts.xlsx')
users = pd.read_excel('acounts.xlsx')
dict_posts = dict()
dict_users = dict()
browser = webdriver.Firefox()
# получаем список постов и аккаунтов
for post in posts.itertuples():
    try:
        dict_posts[post.text] = post.images_paths.split(';')
    except:
        dict_posts[post.text] = ''
for user in users.itertuples():
    dict_users[user.login] = user.password

keys_posts = list(dict_posts.keys())
keys_users = list(dict_users.keys())
links = list()
login_with_errors = list()
#=============================================#
# Проверка аккаунтов
#=============================================#
print('Проверка аккаунтов.....')
for login, password in dict_users.items():
    vk_session = vk_api.VkApi(login, password)
    for i in range(4):
        try:
            login_with_errors.append(login)
            vk_session.auth()
            login_with_errors.pop(-1)
            break
        except:
            time.sleep(2)
login_without_errors = list(set(keys_users) - set(login_with_errors))
print('Не удалось авторизоваться под следующими логинами:')
print(*set(login_with_errors), sep='\n')
#=============================================#
# Постинг с аккаунтов, в которые удалось авторизоваться
#=============================================#
print('Постим...')
for i, text in enumerate(keys_posts):
    photos = dict_posts[text]
    login = login_without_errors[i % len(login_without_errors)]
    password = dict_users[login]
    vk_session = vk_api.VkApi(login, password)
    for i in range(5):
        try:
            vk_session.auth()
            break
        except:
            time.sleep(2)
    upload = vk_api.VkUpload(vk_session)
    tools = vk_api.VkTools(vk_session)
    vk = vk_session.get_api()
    if isinstance(photos, str):
        result = vk.wall.post(message=text)
    else:
        photo_list = upload.photo_wall(photos)
        attachment = ','.join('photo{owner_id}_{id}'.format(
            **item) for item in photo_list)
        result = vk.wall.post(message=text, attachment=attachment)
    wall = tools.get_all('wall.get', 100)
    for post in wall['items']:
        if post['id'] == result['post_id']:
            browser.get(f"http://vk.com/wall{post['owner_id']}_{post['id']}")
            browser.save_screenshot(
                f"report/{post['owner_id']}_{post['id']}.png")
            break
