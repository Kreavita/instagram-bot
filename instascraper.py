
# WIP - this is the module that handles profile insights etc. idk if i will ever finish this, cause it is rather a not so harmless function

scraping_list = {} # {user: [post_urls, followers, following]}
posts_data = {} # {post_url : [caption, date, likes, comments, amount_of_photos, amount_of_videos]}

def init()
    load 
    
def refresh(driver):
    for user, known_posts_urls in scraping_list:
        i = 0
        while latest_post_url not in known_post_urls and i not -1
            i = get_next_post(driver, user, i)

def get_next_post()
    try: ...   

def add(username):
    #add the user to the scraping list

def get(username):
    return data
