#util script
import os, time, sys, requests, subprocess, re, math, html

requests.packages.urllib3.disable_warnings()

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    import wikipedia
    from googletrans import Translator
    import emoji
    import requests as req
    import lyricsgenius
except:
    proc = subprocess.check_call([sys.executable, "-m", "pip", "install", "selenium", "requests", "wikipedia", "googletrans", "emoji", "lyricsgenius"])

    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    import wikipedia
    from googletrans import Translator
    import emoji
    import requests as req
    import lyricsgenius

exe = ""
if os.name == "nt": exe = ".exe"

launch_path = os.path.dirname(os.path.abspath(__file__))
timeout = 5

def get_driver(headless):
    try:
        options = webdriver.firefox.options.Options()
        options.headless = headless
        driver = webdriver.Firefox(options=options, executable_path=os.path.join(launch_path, "driver", "geckodriver" + exe))
    except Exception as e:
        print("WebDriver: Error occured with Firefox: {0}, forcing Chrome...".format(e))
        options = webdriver.chrome.options.Options()
        options.headless = headless
        driver = webdriver.Chrome(options=options, executable_path=os.path.join(launch_path, "driver", "chromedriver" + exe))
    
    driver.maximize_window()
    driver.implicitly_wait(timeout)
    return driver

def download(driver, url, path):
        localpath = ""
        s = ""
        headers = {}
        if not driver == False:
            headers['User-Agent'] = driver.execute_script("return navigator.userAgent")
            cookies = driver.get_cookies()
            cookiestr = ""
            for cookie in cookies:
                cookiestr = cookiestr + cookie["name"] + "=" + cookie["value"] + ";"
            headers['Cookie'] = cookiestr
        try:
            verify=True
            req = requests.get(url, headers = headers, verify=True, stream = True)
        except requests.exceptions.SSLError as e:
            verify=False
            s = s + "\ndelta DL: Error with SSL Certificates, disabled Verify."
            req = requests.get(url, headers = headers, verify=False, stream = True)
        if req.status_code < 300:
            if not (ignore and req.headers['content-type'].startswith(("text/", "application/javascript", "application/x-javascript", "application/json", "image/"))):
                try:
                    fname = self.get_filename(re.findall("filename=\"(.+)\"", req.headers['content-disposition'])[0])
                    path = os.path.join(os.path.dirname(path), fname)
                except:
                    pass
                with open(path, "wb") as f: 
                    for chunk in req.iter_content(chunk_size=64000):
                        f.write(chunk)
                localpath = path
        else: s = s + "\ndelta DL: Got Error Code: {0} with URL: {1}".format(req.status_code, url)
        
        s = s.strip("\n")
        if len(s) > 0: print(s + " " * max(line_length - len(s), 0))
        return localpath

def file_read(path):
    with open(path, "r") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

def file_write(path, data):
    with open(path, "r") as f:
        lines = [line for line in f if line.startswith("#")]
    with open(path, "w") as f:
        f.writelines(lines)
        if not exe == "": data = data.encode("utf-8").decode("ansi")
        f.write(data)
    return True

def save_list_as(lst, path):
    if isinstance(lst, list) and lst:
        string = lst[0]
        for item in lst[1:]: string  = string + "\n" + item
        file_write(os.path.join(launch_path, path), string)
    else: print("'{0}' is not a List or empty".format(lst))

def append_list(lst, path):
    for item in lst:
        with open(os.path.join(launch_path, path), "a+") as f:
            if f.readline().strip(): f.write("\n")
            if not exe == "": item = item.encode("utf-8").decode("ansi")
            f.write(item)
            f.write("\n")


def read_list(path): return file_read(os.path.join(launch_path, path))

def wiki_text(string):
    wikipedia.set_lang("de")
    return wikipedia.summary(string)

def lyrics(string):
    genius = lyricsgenius.Genius("MWfMMAEkv-1z90FvLNFqFU-Vi7-RTkWTEJhmo6f3POWnBcOjk7AEj0k4_yAvCa7i")
    song = genius.search_song(string)
    return "{0} \n Lied: {1} - {2}".format(song.lyrics, song.artist, song.title)

def get_parenthesis(string):
    out = []
    stack = 0
    first = True
    for c in string:
        if c == "(" and (stack > 0 or first):
            stack = stack + 1
            first = False
        if c == ")": stack = stack - 1
        
        if stack > 0: out.append(c)
    if stack == 0: return ("".join(out))[1:]
    else: return False

def next_op(string, op_list):
    if any(ops in string for ops in op_list):
        chars = []
        op = ""
        i = 0
        if string.startswith(tuple(op_list)):
            op = string[0]
            i = i + 1
        while i < len(string) and not string[i] in op_list:
            chars.append(string[i])
            i = i + 1
        return ["".join(chars), op]
    else: return []

def calculate(string):
    print("in: " + string)
    # Replace Constants by approximation and whitespaces
    string = string.replace("pi", str(math.pi))
    string = string.replace(" ", "")
    
    # Do Trigon first
    for trig in ["sin", "cos", "tan"]:
        if trig in string:
            eq = get_parenthesis(string.split(trig, 1)[1])
            string = string.replace(eq, "", 1)
            string = string.replace(trig + "()", "{0}", 1)
            string = string.format(str(eval("math.{0}".format(trig))(calculate(eq))))
   
    # Do Brackets after Trigon
    
    parenthesis = get_parenthesis(string)
    if len(parenthesis) > 0: 
        while len(parenthesis) > 0:
            string = string.replace("(" + parenthesis + ")", str(calculate(parenthesis)))
            parenthesis = get_parenthesis(string)
    
    #This is performed on every bracket and on the bracket results
    res = ''
    
    #just return it if its a legit number
    try: return(float(string.format("-")))
    except: pass
                
    if any(dashop in string for dashop in ["+", "-"]):
        string = string.replace("+-", "+{0}")
        string = string.replace("--", "-{0}")
        string = string.replace("/-", "/{0}")
        string = string.replace("*-", "*{0}")
        string = string.replace("^-", "^{0}")
        string = string.replace("r-", "r{0}")
        
        res = 0
        while any(dotop in string for dotop in ["+", "-"]) and not string.endswith(tuple(["+", "-"])):
            eq = next_op(string, ["+", "-"])
            if not eq == [] and not eq[0] == "":
                string = string.replace(eq[1]+eq[0], "", 1)
                if eq[1] == "": res = calculate(eq[0])
                if eq[1] == "+": res = res + calculate(eq[0])
                if eq[1] == "-": res = res - calculate(eq[0])
            
    elif any(dotop in string for dotop in ["*", "/"]):
        res = 1
        while any(dotop in string for dotop in ["*", "/"]) and not string.endswith(tuple(["*", "/"])):
            eq = next_op(string, ["*", "/"])
            if not eq == [] and not eq[0] == "":
                string = string.replace(eq[1]+eq[0], "", 1)
                if eq[1] == "": res = calculate(eq[0])
                if eq[1] == "*": res = res * calculate(eq[0])
                if eq[1] == "/": res = res / calculate(eq[0])
        
    elif any(opop in string for opop in ["^", "r"]): # Root and Power
        calcstr = string.split("r", 1)

        atom = calcstr[0].format("-").split("^")
        exp = float(atom[-1])
        
        for quark in atom[:-1][::-1]: exp = float(quark) ** exp
        calcstr[0] = exp

        if len(calcstr) == 2:
            res = max(calculate(calcstr[1]), 0) ** ( 1 / calcstr[0])
        else: res = calcstr[0]

    if res == int(res): res = int(res) 

    print("out-res: " + str(res))
    
    return res

def translate(string, lang_list):
    translator = Translator()
    emoji_flags = {"en" : "Englisch :flag_for_United_Kingdom:",
             "de" : "Deutsch :Germany:",
             "es" : "Spanisch :flag_for_Spain:",
             "fr" : "Französisch :flag_for_France:",
             "ja" : "Japanisch :flag_for_Japan:",
             "ko" : "Koreanisch :flag_for_South_Korea:",
             "fi" : "Finnisch :flag_for_Finland:",
             "la" : "Latein"}
    res = []
    for lang in lang_list:
        res.append("Auf {0}: {1}".format(emoji_flags[lang], translator.translate(string, dest=lang).text))
    return res

def ani_search(string):
    search = req.get("https://myanimelist.net/search/all?q={0}".format(string))

    anime_url = re.findall("<a href=\"(https:\/\/myanimelist\.net\/anime\/[0-9]*\/[^\/]*?)\"", search.text)[0]

    anime = req.get(anime_url)
    
    return html.unescape(anime.text.split("<span itemprop=\"description\">")[1].split('</span>')[0].replace("<br />", ""))+ "\n Link: {0}".format(anime_url)

def inline_prt(s):
    sys.stdout.write(s)
    sys.stdout.flush()
    sys.stdout.write("\b" * (len(s) + 1))
