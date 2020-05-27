#dm-listener Script begins

import os, time, sys, random, traceback
import util, config
from selenium.webdriver.common.keys import Keys

mod_list = []
comment_accs = []
comment_texts = []
suggestions = []

activities = []

service_on = True

def backup_reload(save_first):
    global mod_list, comment_accs, comment_texts, suggestions
    
    if save_first:
        util.save_list_as(mod_list, os.path.join('data', 'mod_list'))
        util.save_list_as(comment_accs, os.path.join('data', 'comment_accs'))
        util.save_list_as(comment_texts, os.path.join('data', 'comment_texts'))
        util.save_list_as(suggestions, os.path.join('data', 'suggestions'))
        
    mod_list = util.read_list(os.path.join('data', 'mod_list'))
    comment_accs = util.read_list(os.path.join('data', 'comment_accs'))
    comment_texts = util.read_list(os.path.join('data', 'comment_texts'))
    suggestions = util.read_list(os.path.join('data', 'suggestions'))

def start_listener():
    global activities
    
    backup_reload(False)
    
    while service_on:
        with util.get_driver(True) as driver:
            insta_login(driver)
            
            x = 0
            while service_on and x < 500:
                if x == 0:
                    do_follows(driver)
                    x = 40
                else: x = x - 1
                
                messages = load_messages(driver)
                
                for user, msgs in messages.items():
                    for msg in msgs:
                        if isinstance(msg, list) and len(msg) == 2:
                            
                            activity_type = "sent a Text '{0}'".format(msg[1])
                            if msg[0] == "Image":
                                
                                activity_type = "shared a photo. URL '{0}'".format(msg[1])                            
                                send_message(driver, user, [":robot_face: {0} - Hübsches Foto :heart_eyes:, aber damit kann ich im Moment nichts anfangen :confounded:".format(config.BOT_NAME)])
                            if msg[0] == "Video":
                                
                                activity_type = "shared a video. URL '{0}'".format(msg[1]) 
                                send_message(driver, user, [":robot_face: {0} - Super Video :ok_hand:, aber damit kann ich im Moment nichts anfangen :confounded:".format(config.BOT_NAME)])
                            if msg[0] == "Post":
                                
                                activity_type = "shared a Post or Story. URLs: '{0}'".format(msg[1]) 
                                if msg[1]:    
                                    send_message(driver, user, [":arrow_down: Post Downloader - hier sind die Links zu den Medien:"])
                                    for url in msg[1]: send_message(driver, user, [url])
                                    send_message(driver, user, [":muscle: powered by: @{0} :sunglasses:".format(config.INSTA_USER)])
                                else: send_message(driver, user, [":warning: Post Downloader - keine Medien gefunden!"])
                            if msg[0] == "Text":
                                if msg[1].startswith("!"):
                                    cmd = msg[1].split(" ")

                                    activity_type = "issued Command: '{0}' with Args: '{1}'".format(cmd[0], " ".join(cmd[1:]))
                                    process_command(driver, user, cmd[0], cmd[1:])
                                    
                            log_activity("[{0}] '{1}' {2}".format(time.ctime(time.time()), user, activity_type))

                util.append_list(activities, os.path.join('data', 'activities_log'))
                activities = []
                
                time.sleep(random.uniform(5,10))
            backup_reload(True)
            
def insta_login(driver):
    driver.get("https://www.instagram.com/direct/inbox/")
    driver.find_element_by_name("username").send_keys(config.INSTA_USER)
    driver.find_element_by_name("password").send_keys(config.INSTA_PASS)
    driver.find_element_by_xpath("//button[@type='submit']").click()
    
    try:
        driver.find_element_by_xpath("//button[contains(@class, 'yWX7d') and contains(text(), 'Not Now')]").click()
    except: pass
    
    driver.find_element_by_xpath("//button[contains(@class, 'HoLwm')]").click()

def do_follows(driver):
    driver.get("https://www.instagram.com/{0}/".format(config.INSTA_USER))
    driver.find_element_by_xpath("//a[@class='-nal3 ']").click()
    not_followed = driver.find_elements_by_xpath("//div[@class='PZuss']//button[contains(@class, 'y3zKF')]")
    for guy in not_followed: guy.click()

def load_messages(driver):
    if not any(ext in driver.current_url for ext in ["https://www.instagram.com/direct/inbox/", "https://www.instagram.com/direct/t/"]):
        driver.get("https://www.instagram.com/direct/inbox/")
        
    messages = {}
    users = driver.find_elements_by_xpath("//div[@class='N9abW']//div[contains(@class, 'KV-D4')]")
    
    for j in range(int(len(users) / 2)):
        try: name = users[2 * j + 1].get_attribute("innerText")
        except:
            users = driver.find_elements_by_xpath("//div[@class='N9abW']//div[contains(@class, 'KV-D4')]")            
            name = users[2 * j + 1].get_attribute("innerText")
        users[2 * j + 1].click()
        driver.find_element_by_class_name("PjuAP")
        
        path_ml = "//div[contains(@class, 'e9_tN')]"
        ml = driver.find_elements_by_xpath(path_ml)
        i = 0

        try:
            while not "VdURK" in ml[len(ml) - 1 - i].get_attribute("class").split(" ")  and i < len(ml):
                data = ""
                msg = ml[len(ml) - 1 - i]
                
                driver.implicitly_wait(0)
                if len(msg.find_elements_by_xpath("./div/div/div/div/div/div/span")) == 1:
                    data = ["Text", msg.find_element_by_xpath("./div/div/div/div/div/div/span").get_attribute("innerText")]
                        
                if "_6JFwq" in msg.get_attribute("class").split(" "):
                    if msg.find_elements_by_xpath(".//div[contains(@class, 'z82Jr')]"):
                        data = ["Post", post_url(driver, msg)] #Post
                    else:
                        if len(msg.find_elements_by_xpath(".//img")) > 0: # Image
                            driver.implicitly_wait(util.timeout)
                            msg.click()
                            
                            try:
                                data = ["Image", driver.find_element_by_xpath("//div[@role='presentation']//img").get_attribute("src")]
                                driver.execute_script("document.getElementsByClassName('Yx5HN')[0].remove()")
                            except Exception as e: log_activity("Element has already been clicked and forcefully removed from DOM \n {0}".format(e))
                            
                elif len(msg.find_elements_by_xpath(".//img[@class='_3NlKJ']")) == 1: data = ["Post", post_url(driver, msg)] #Story
                
                if not data == "":
                    try:
                        if not data in messages[name]: messages[name].append(data)
                    except: messages[name] = [data]
                
                driver.implicitly_wait(util.timeout)
                
                try: users[2 * j + 1].click()
                except:
                    users = driver.find_elements_by_xpath("//div[@class='N9abW']//div[contains(@class, 'KV-D4')]")
                    users[2 * j + 1].click()
                
                try: msg.get_attribute("class").split(" ")
                except:
                    driver.find_element_by_class_name("PjuAP")
                    ml = driver.find_elements_by_xpath(path_ml)
                    
                i = i + 1
                
        except Exception as e:
            log_activity("[{0}] Message Sync Job failed for '{1}': {2}".format(time.ctime(time.time()), name, e))
            log_activity(len(ml), i)
            log_activity(traceback.format_exc())
        
    return messages

def post_url(driver, clickable):
    driver.implicitly_wait(util.timeout)
    
    clickable.click()

    urls = get_media(driver)
    
    if urls == []:
        driver.get(driver.current_url)
        urls = get_media(driver)
    
    driver.get("https://www.instagram.com/direct/inbox/")
    
    return urls
    
def get_media(driver):  
    urls = []
    
    post_div = driver.find_elements_by_xpath("//div[contains(@class, 'wKWK0')]")
    driver.implicitly_wait(0)

    if post_div: # Its a post
        
        slider_post = driver.find_elements_by_xpath("//ul[@class = 'vi798']/li")
        
        if len(slider_post): # Slider Post
            
            Next_element = True
            while Next_element:
                for slide in slider_post[1:]:

                    if slide.find_elements_by_xpath(".//div[@class = 'PyenC']"):
                        el = slide.find_element_by_xpath(".//video[@class='tWeCl']")
                    else:
                        el = slide.find_element_by_xpath(".//img[@class='FFVAD']")

                    if not el.get_attribute("src") in urls: urls.append(el.get_attribute("src"))
                
                try: driver.find_element_by_xpath("//div[contains(@class, 'coreSpriteRightChevron')]").click()
                except: Next_element = False
                
                time.sleep(0.25)

                slider_post = driver.find_elements_by_xpath("//ul[@class = 'vi798']/li")
            
        else: # Normal Post
            
            try: el = post_div[0].find_element_by_xpath(".//video[@class='tWeCl']")
            except:el = post_div[0].find_element_by_xpath(".//img[@class='FFVAD']")

            if not el.get_attribute("src") in urls: urls.append(el.get_attribute("src"))
            
    else: # Story or Highlights
        story_div = driver.find_elements_by_xpath("//div[contains(@class, 'GHEPc')]")
        if story_div:
            
            try: driver.find_element_by_xpath("//button[contains(@class, '_8A5w5')]").click()
            except: pass
            
            Next_element = True
            driver.implicitly_wait(0)
            
            while Next_element:
                if story_div:
                    
                    try: el = story_div[0].find_elements_by_xpath(".//video[contains(@class, 'y-yJ5')]//source")[-1]
                    except: el = story_div[0].find_element_by_xpath(".//img[contains(@class, 'y-yJ5')]")

                    if not el.get_attribute("src") in urls: urls.append(el.get_attribute("src"))
                    
                    try: driver.find_element_by_xpath("//div[contains(@class, 'coreSpriteRightChevron')]").click()
                    except: Next_element = False

                    time.sleep(0.25)

                    story_div = driver.find_elements_by_xpath("//div[contains(@class, 'GHEPc')]")

                else: Next_element = False
                
    driver.implicitly_wait(util.timeout)
            
    return urls

def send_message(driver, user, txtlist):
    if len(txtlist) > 0 and isinstance(txtlist, list):
        
        if not any(ext in driver.current_url for ext in ["https://www.instagram.com/direct/inbox/", "https://www.instagram.com/direct/t/"]):
            driver.get("https://www.instagram.com/direct/inbox/")
            
        driver.find_element_by_xpath("//div[@class='N9abW']//div[contains(@class, 'KV-D4')]//div[normalize-space(.) = '{0}']".format(user)).click()

        txtarea = driver.find_element_by_xpath("//div[@class='uueGX']//textarea")
        text_length = 0
        
        for item in txtlist:
            for paragraph in item.split("\n"):
                text = util.emoji.emojize(paragraph, use_aliases = True)
                while len(text) > 0:
                    
                    if text_length > 900:
                        driver.find_element_by_xpath("//div[contains(@class, 'JI_ht')]//button[contains(@class, 'y3zKF')]").click()
                        text_length = 0
                        
                    txtarea.send_keys(text[:20])  
                    text_length = text_length + len(text[:20])
                    text = text.split(text[:20], 1)[1]
                    
                txtarea.send_keys(Keys.SHIFT + '\n') 
                text_length = text_length + 1

        if text_length > 0:
            driver.find_element_by_xpath("//div[contains(@class, 'JI_ht')]//button[contains(@class, 'y3zKF')]").click()
        
    else: log_activity("ERROR: Message could not be parsed")

def process_command(driver, user, cmd, args):
    global mod_list, comment_accs, comment_texts, suggestions
    
    if cmd.lower() in ["!help", "!h", "!hilfe"]:
        txt = [":information_source: HILFE: Alle Funktionen:"]
        txt.append(":information_source: !help, !h, !hilfe: zeigt diese Hilfe an")
        txt.append(" ")
        txt.append(":mag: !wiki, !w <Wort>: Hole dir schnell Informationen zu einem Wort aus Wikipedia")
        txt.append(" ")
        txt.append(":heavy_division_sign: !calc, !math, !m <Term>: Taschenrechner mit Klammern 2*(2+2), Potenzen: 2^2, Wurzeln: 2r4 und + - * /")
        txt.append(" ")
        txt.append(":speech_balloon: !translate, !trans, !t <Sprache> <Text> oder nur <Text>:"+
                   "Übersetze in: en :flag_for_United_Kingdom:,de :Germany:, es :flag_for_Spain:, fr :flag_for_France:, ja :flag_for_Japan:, ko :flag_for_South_Korea:, fi :flag_for_Finland:, la (latein)")
        txt.append(" ")
        txt.append(":musical_note: !lyrics, !l <Wort>: Hole dir schnell einen Sontext von einem Lied")
        txt.append(" ")
        txt.append(":mag: !anime, !a <Anime>: Hole dir schnell die Zusammenfassung von einem Anime von MAL")
        txt.append(" ")
        
        if user in mod_list:
            txt.append("") 
            txt.append(":lock: VIP - Funktionen: ")  
            #txt.append("!stats, !s <@Name>: zeigt Statistiken zu dir oder dem eingegebenen Account an")
            txt.append("!list: Liste der Nutzer und Texte auf der Liste anzeigen")
            txt.append(" ")
            txt.append("!adduser, !add <@Name>: Nutzer zur Scraping-Liste hinzufügen")
            txt.append(" ")
            txt.append("!deluser, !del <@Name>: Nutzer aus der Scraping-Liste entfernen")
            txt.append(" ")
            txt.append("!addtext, !addt <Text>: Text zur Liste der Kommentarinhalte hinzufügen")
            txt.append(" ")
            txt.append("!deltext, !delt <Text>: Text aus der Liste der Kommentarinhalte entfernen")
            txt.append(" ")

        txt.append(" ")         
        txt.append(":point_up: !vorschlag, !v <Text>: Sende mir eine Verbesserungsmöglichkeit oder ein gewünschtes Feature :100:")   
        txt.append(" ")
        txt.append(" ")
        txt.append(":sparkles: Weitere Features:")
        txt.append(" ")
        txt.append(":arrow_down: Post / Story Download: Post / Story teilen (:point_up: muss mir zugänglich sein!)")
        
        send_message(driver, user, txt)
        send_message(driver, user, ["", ":muscle: powered by: @{0} :sunglasses:".format(config.INSTA_USER)])
        
    elif cmd.lower() in ["!anime", "!a"]:
        if len(args) > 0:
            try:
                anistr = util.ani_search(" ".join(args))
                send_message(driver, user, [":mag: ANIME - Synopsis zu '{0}':".format(" ".join(args)), anistr])
                send_message(driver, user, ["", ":muscle: powered by: @{0} :sunglasses:".format(config.INSTA_USER)])
            except Exception as e:
                log_activity(str(e))
                send_message(driver, user, [":warning: ANIME - Anime '{0}' nicht gefunden :x:".format(" ".join(args))])
        else:
            send_message(driver, user, [":warning: ANIME - !anime benötigt einen Suchbegriff! :point_up:"])
            
    elif cmd.lower() in ["!wiki", "!w"]:
        if len(args) > 0:
            try:
                wikistr = util.wiki_text(" ".join(args))
                send_message(driver, user, [":mag: WIKIPEDIA - Ergebnis zu '{0}':".format(" ".join(args)), wikistr])
                send_message(driver, user, ["", ":muscle: powered by: @{0} :sunglasses:".format(config.INSTA_USER)])
            except Exception as e:
                log_activity(str(e))
                send_message(driver, user, [":warning: WIKIPEDIA - Begriff '{0}' nicht gefunden :x:".format(" ".join(args))])
        else:
            send_message(driver, user, [":warning: WIKIPEDIA - !wiki benötigt einen Suchbegriff! :point_up:"])
                
    elif cmd.lower() in ["!lyrics", "!l"]:
        if len(args) > 0:
            try:
                lstr = util.lyrics(" ".join(args))
                send_message(driver, user, [":musical_note: GENIUS - Ergebnis zu '{0}':".format(" ".join(args)), lstr])
                send_message(driver, user, ["", ":muscle: powered by: @{0} :sunglasses:".format(config.INSTA_USER)])
            except Exception as e:
                log_activity(str(e))
                send_message(driver, user, [":warning: GENIUS - Keine Lyrics zu '{0}' gefunden :x:".format(" ".join(args))])
        else:
            send_message(driver, user, [":warning: GENIUS - !lyrics benötigt einen Suchbegriff! :point_up:"])
                
    elif cmd.lower() in ["!calc", "!math", "!m"]:
        if len(args) > 0:
            try:
                result = util.calculate(" ".join(args))
                send_message(driver, user, [":heavy_division_sign: MATH - Ergebnis zu '{0}': {1}".format(" ".join(args), result)])
                send_message(driver, user, ["", ":muscle: powered by: @{0} :sunglasses:".format(config.INSTA_USER)])
            except Exception as e:
                log_activity(str(e))
                send_message(driver, user, [":warning: MATH - Term '{0}' konnte nicht berechnet werden :x:".format(" ".join(args))])
        else:
            send_message(driver, user, [":warning: MATH - !math benötigt einen mathematischen Ausdruck! :point_up:"])            

    elif cmd.lower() in ["!translate", "!trans", "!t"]:
        lang_list = ["en", "de", "es", "fr", "ja", "ko", "fi", "la"]
        if len(args) > 0:
            if len(args) > 1 and args[0] in lang_list:
                lang = [args[0]]
                text = " ".join(args[1:])
            else:
                lang = lang_list
                text = " ".join(args)
            try:
                res_list = util.translate(text, lang)  
                send_message(driver, user, [":speech_balloon: TRANSLATOR - Ergebnis zu '{0}':".format(" ".join(args))] + res_list)
                send_message(driver, user, ["", ":muscle: powered by: @{0} :sunglasses:".format(config.INSTA_USER)])
            except Exception as e:
                log_activity(str(e))
                send_message(driver, user, [":warning: TRANSLATOR - Eingabe '{0}' konnte nicht übersetzt werden :x:".format(" ".join(args))])
        else:
            send_message(driver, user, [":warning: TRANSLATOR - !trans benötigt einen Text! :point_up:"])
            
    elif cmd.lower() in ["!stats", "!s"]:
        if len(args) == 1:
            pass #Account args[0]
        else:
            pass #Account user
        send_message(driver, user, [":no_entry: {0} - Du hast keinen Zugriff auf diesen Befehl!".format(config.BOT_NAME)])

    # mod and admin commands

    elif cmd.lower() in ["!list"] and user in mod_list:
        if user in mod_list: msg = ["{0} - :memo: Die Liste:".format(config.BOT_NAME), ":memo: Accounts: ", str(comment_accs), "", ":memo: Kommentarinhalte: ", str(comment_texts)]
        if user in config.ADMINS: msg = msg + ["", ":memo: Moderatoren: ", str(mod_list), "",  ":memo: Vorschläge: ", "\n".join(suggestions)]
        send_message(driver, user, msg)
        
    elif cmd.lower() in ["!adduser", "!add"] and user in mod_list:
        comment_accs = mod_msg(driver, user, comment_accs, [cmd.lower(), "Account", args, "Accounts"], False, len(args) == 1)
        
    elif cmd.lower() in ["!deluser", "!del"] and user in mod_list:
        comment_accs = mod_msg(driver, user, comment_accs, [cmd.lower(), "Account", args, "Accounts"], True, len(args) == 1)

    elif cmd.lower() in ["!addmod", "!addm"] and user in config.ADMINS:
        mod_list = mod_msg(driver, user, mod_list, [cmd.lower(), "Account", args, "Moderatoren"], False, len(args) == 1)
        
    elif cmd.lower() in ["!delmod", "!delm"] and user in config.ADMINS:
        mod_list = mod_msg(driver, user, mod_list, [cmd.lower(), "Account", args, "Moderatoren"], True, len(args) == 1)
        
    elif cmd.lower() in ["!addtext", "!addt"] and user in mod_list:
        comment_texts = mod_msg(driver, user, comment_texts, [cmd.lower(), "Text", args, "Kommentarinhalte"], False, len(args) > 1)

    elif cmd.lower() in ["!deltext", "!delt"] and user in mod_list:
        comment_texts = mod_msg(driver, user, comment_texts, [cmd.lower(), "Text", args, "Kommentarinhalte"], True, len(args) > 1)

    elif cmd.lower() in ["!vorschlag", "!v"]:
        suggestions.append("{0} says: {1}".format(user, " ".join(args)))
        send_message(driver, user, [":point_up: VORSCHLAG - Vielen Dank! Ich habe deine Nachricht erhalten :100: :thumbsup:!"])

    else: send_message(driver, user, [":warning: {0} - Befehl nicht gefunden oder du hast keinen Zugriff auf diesen Befehl :no_entry: !".format(config.BOT_NAME)])
        
def mod_msg(driver, user, lst, data, delete, correct_args):
    msg = ":warning: {2} - '{0}' braucht einen {1}! :expressionless:".format(data[0], data[1], config.INSTA_USER)
    
    if correct_args:
        arg = " ".join(data[2]).lstrip("@")
        if delete:
            msg = ":white_check_mark: {2} - '{0}' wurde aus der :memo: Liste der {1} entfernt!".format(arg, data[3], config.BOT_NAME)
            if not arg in lst:
                lst.remove(arg)
                msg = ":white_check_mark: {2}: '{0}' ist nicht in der :memo: Liste der {1}!".format(arg, data[3], config.BOT_NAME)
        else:
            msg = ":white_check_mark: {2}: - '{0}' wurde zur :memo: Liste der {1} hinzugefügt!".format(arg, data[3], config.BOT_NAME)
            if arg in lst:
                lst.append(arg)
                msg = ":white_check_mark: {2}: '{0}' ist bereits in der :memo: Liste der {1}!".format(arg, data[3], config.BOT_NAME)

    send_message(driver, user, [msg])
    return lst

def log_activity(string):
    global activities
    
    print(string)
    activities.append(string)
    
#Here begins ze magick
start_listener()
