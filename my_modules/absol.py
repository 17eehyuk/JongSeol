from urllib.request import urlopen
from bs4 import BeautifulSoup

url = "https://www.absolutdrinks.com/ko/drinks/yellowhammer/"
html = urlopen(url)

soup = BeautifulSoup(html, "html.parser") 
selector = "body > main > div > div > article > div.hidden.md\:block.recipe-wrapper > div.drinks-content > ul"

recipe = soup.select_one(selector)
li_tags = recipe.find_all('li')

absol_recipe = []


for li_tag in li_tags:
    if len(li_tag) != 7:
        continue
    else:
        tmp_list = []
        for j in li_tag:
            for k in j:
                tmp_list.append(k)
        try:
            if tmp_list[2][-2:]=='ml':
                drink_ml = tmp_list[2][:-3]     # tmp_list[2] : ml       ex) 30 ml
                drink_name = tmp_list[6]        # tmp_list[6] : 음료명
                absol_recipe.append([drink_ml, drink_name])
        except:
            pass

print(absol_recipe)