from calendar import weekday
from os import sep
import re
import requests
import datetime
from xml.etree import ElementTree as ET
import random
import json
import locale

#setting the language for later use of the weekday
locale.setlocale(locale.LC_TIME, 'de_DE')

#Legacycode from old APIs .......................................................................
def getUniNaerwaerthe(xml, makro):
    return xml.split(makro)[1].split("<td>")[1].split("</td>")[0]

def parseUniXMLV2(xml):
    menus = {}

    xmlSplit = xml.split("<h3>")

    #assemble Farm menu
    menus["*Farm* (5.80CHF)"] = xmlSplit[1].split("<p>")[1].split("</p>")[0].strip(' \n,').replace(" \n", ", ").replace("\n", ", ")
    fett = getUniNaerwaerthe(xmlSplit[1], "Fett")
    Eiweiss = getUniNaerwaerthe(xmlSplit[1], "Eiweiss")
    Kohlenhydrate = getUniNaerwaerthe(xmlSplit[1], "Kohlenhydrate")
    menus["*Farm* (5.80CHF)"] += "\nF: " + fett + ", K: " + Kohlenhydrate + ", P: " + Eiweiss

    #assemble Butcher menu
    menus["*Butcher* (6.90CHF)"] = re.sub('(\s\s)+', '', xmlSplit[2].split("<p>")[1].split("</p>")[0].split("Fleisch")[0].strip(' \n,').replace("\n", ", "))
    fett = getUniNaerwaerthe(xmlSplit[2], "Fett")
    Eiweiss = getUniNaerwaerthe(xmlSplit[2], "Eiweiss")
    Kohlenhydrate = getUniNaerwaerthe(xmlSplit[2], "Kohlenhydrate")
    menus["*Butcher* (6.90CHF)"] += "\nF: " + fett + ", K: " + Kohlenhydrate + ", P: " + Eiweiss

    return menus

def getUniMsg():
    isoWeekday = datetime.now().isoweekday()
    responseObereMensa = requests.get("https://zfv.ch/de/menus/rssMenuPlan?menuId=148&type=uzh2&dayOfWeek=" + str(isoWeekday))


    uniMsg = ""
    if(responseObereMensa.status_code == 200):
        #replace all <br/>s in the returned string
        responseObereMensa = responseObereMensa.text.replace("<br/>", "").replace("<br />", "")

        #process the data from the Uni-API
        menusObereMensa = parseUniXMLV2(responseObereMensa)

        uniMsg = generateMenuMSG(menusObereMensa)
    else:
        uniMsg = "Diese Daten sind leider nicht vorhanden.\n"

    return uniMsg

def parsePolyJson(json):
    out = {}

    menus = json.get("menu").get("meals")
    for menu in menus:
        description = menu.get("description")
        tmp = ""
        for parts in description:
            tmp += parts + ", "
        out["*"  + str(menu.get("label") + "* (" + menu.get("prices").get("student") + "CHF)")] = re.sub('(\s\s)+',' ',tmp.strip(', '))

    return out

def getPolyMsg():
    responsePolyMensa = requests.get("https://www.webservices.ethz.ch/gastro/v1/RVRI/Q1E1/mensas/12/de/menus/daily/"+ str(datetime.datetime.today()) +"/lunch?language=de")

    polyMsg = ""
    if(responsePolyMensa.status_code == 200):
        #process the data from the Poly-API
        menusPolyMensa = parsePolyJson(responsePolyMensa.json())
    
        polyMsg = generateMenuMSG(menusPolyMensa)
    else:
        polyMsg = "Diese Daten sind leider nicht vorhanden"

    return polyMsg
#End legacy code .................................................................................

def is_float(string):
    try:
        float(string)
        return True
    except ValueError:
        return False

def generateMenuMSG(menus):
    msg = ''
    for menu in menus:
        msg += menu + ":\n"
        msg += menus[menu] + "\n"

    return msg

#Multiply Naehwert relative To Gesamtgewicht
def mnrtg(gesamtgewicht, naehrwert):
    #get rid of unit in e.g. "5 g"
    naehrwertNumber = naehrwert.split(" ")[0]
    gesamtgewichtNumber = gesamtgewicht.split(" ")[0]

    if (is_float(naehrwertNumber) and is_float(gesamtgewichtNumber)):
        naehrwertNumber = float(naehrwertNumber)
        gesamtgewichtNumber = float(gesamtgewichtNumber)
        return str(round(naehrwertNumber * (gesamtgewichtNumber/100))) + " g"
    else:
        return "N/A"

def parseUniHTML(menuType: str ,html: str):
    menu = html.split("<h1 class=\"sc-dd6b703-3 jAgsDf\">")[1].split("<!-- --> <!-- --></h1>")[0]
    preis = html.split("<p class=\"sc-f9bc0ed9-2 ktmykt\">")[1].split("</p>")[0]
    fett = html.split("<p class=\"sc-4cf605e8-2 BFqus\">Fett</p><p class=\"sc-4cf605e8-2 BFqus\">")[1].split("</p>")[0]
    kohlenhydrate = html.split("<p class=\"sc-4cf605e8-2 BFqus\">Kohlenhydrate</p><p class=\"sc-4cf605e8-2 BFqus\">")[1].split("</p>")[0]
    protein = html.split("<p class=\"sc-4cf605e8-2 BFqus\">Protein</p><p class=\"sc-4cf605e8-2 BFqus\">")[1].split("</p>")[0]
    gesamtgewicht = html.split("<h3 class=\"sc-4cf605e8-1 cDQYwP\">Gesamtgewicht</h3><p class=\"sc-4cf605e8-2 sc-4cf605e8-3 BFqus geMwVZ\">")[1].split("</p>")[0]
    
    return {"*" + menuType + "* (" + preis + ")": menu + "\nF: " + mnrtg(gesamtgewicht, fett) + ", K: " + mnrtg(gesamtgewicht, kohlenhydrate) + ", P: " + mnrtg(gesamtgewicht, protein)}


#get Uni-Mensa data from new HTML-"API"
def getUniMsgV2():
    date = str(datetime.date.today())

    uniMsg = ""

    responseObereMensaFarm = requests.get("https://app.food2050.ch/uzh-zentrum/obere-mensa/food-profile/" + date + "-mittagsverpflegung-farm")
    if(responseObereMensaFarm.status_code == 200):
        #process the HTML data from the Uni-"API" for the Farm Menu
        menuFarmObereMensa = parseUniHTML("Farm", responseObereMensaFarm.text)
        uniMsg += generateMenuMSG(menuFarmObereMensa)
        
    else:
        uniMsg += "Diese Daten sind leider nicht vorhanden.\n"

    responseObereMensaButcher = requests.get("https://app.food2050.ch/uzh-zentrum/obere-mensa/food-profile/" + date +"-mittagsverpflegung-butcher")
    if(responseObereMensaButcher.status_code == 200):
        #process the HTML data from the Uni-"API" for the Butcher Menu
        responseObereMensaButcher = parseUniHTML("Butcher", responseObereMensaButcher.text)
        uniMsg += generateMenuMSG( responseObereMensaButcher)
        
    else:
        uniMsg += "Diese Daten sind leider nicht vorhanden.\n"

    return uniMsg

def parsePolyJsonV2(json):
    out = {}

    menus = json.get("weekly-rota-array")[0].get("day-of-week-array")[datetime.datetime.now().weekday()].get("opening-hour-array")[0].get("meal-time-array")[0].get("line-array")
    for menu in menus:
        menuType = menu.get("name")
        menuName = menu.get("meal").get("name")
        menuDescription = menu.get("meal").get("description")
        menuPrice = str(format(menu.get("meal").get("meal-price-array")[0].get("price"),".1f"))

        out["*" + menuType + "* (" + menuPrice + "0CHF)"] = menuName + "\n" + menuDescription
    
    return out

#get the polymensa data from the new API (new since HS 2023)
def getPolyMsgV2():
    responsePolyMensa = requests.get("https://idapps.ethz.ch/cookpit-pub-services/v1/weeklyrotas/?client-id=ethz-wcms&lang=de&rs-first=0&rs-size=50&valid-after=" + str(datetime.date.today()) + "&valid-before=" + str(datetime.date.today()) + "&facility=9")

    polyMsg = ""
    if(responsePolyMensa.status_code == 200):
        #process the data from the Poly-API
        menusPolyMensa = parsePolyJsonV2(responsePolyMensa.json())
    
        polyMsg = generateMenuMSG(menusPolyMensa)
    else:
        polyMsg = "Diese Daten sind leider nicht vorhanden"

    return polyMsg

def sendMsg():
    return requests.post(
        url,
        headers=headers,
        data=json.dumps(data)
    )

#Main -----------------------------------------------------------------------------------------------------------------------------------------------

#create BODY of MSG
uniMsg = getUniMsgV2()

polyMsg = getPolyMsgV2()


#create MSG for Whatsapp API
phone_number_id = ""
access_token = ""
recipient_phone_number = ""

url = f"https://graph.facebook.com/v13.0/{phone_number_id}/messages"
headers = {
    "Authorization": f"Bearer {access_token}",
    'Content-Type': 'application/json'
}

msg_header_params = [
    {
        "type": "text",
        "text": random.choice(['Ahoihoi'
,'Aloha'
,'Alles cool im Pool?'
,'Alles fit im Schritt?'
,'Alles klar im BH?'
,'Alles Schritt im fit?'
,'Alles klar in Kanada?'
,'Alles Roger in Kambodscha?'
,'Buenas Tardes, Muchachos'
,'Buongiorno, Adorno'
,'Buongiorno, Mr Porno'
,'Butem w Morde'
,'Cello'
,'Challo'
,'Gib Flosse, Genosse'
,'Good Morning, Vietnam'
,'Good Morning in the Morning'
,'Grüetzi'
,'Grüßli Müsli'
,'Halo i bims'
,'Hallihallohallöle'
,'Hallöchen Popöchen'
,'Hallöchen mit Öchen'
,'Heroin-spaziert'
,'Hi, Fisch'
,'Hola'
,'Howdy'
,'Juten Tach'
,'Lange nicht gesehen, und doch wiedererkannt'
,'Ja, hallo erstmaaal'
,'John Porno'
,'Mensch, du hier und nicht in Istanbul?'
,'Moin Diggi'
,'Moingiorno'
,'Moinjour'
,'Namasté'
,'Palim Palim'
,'Salve'
,'Sdrasdwuij'
,'Servus, Haselnuss'
,'Soos was los?'
,'Tuten Gag'
,'Whazuuuuuuuup?'
,'Yo Moinsen!'
])
    }
]

msg_body_params = [
        {
            "type": "text",
            "text": datetime.datetime.now().strftime("%A %d.%b")
        },
        {
            "type": "text",
            "text": uniMsg.replace("\n", "\\n")
        },
        {
            "type": "text",
            "text": polyMsg.replace("\n", "\\n")
        }
]

data = {
    'messaging_product': 'whatsapp',
    'to': recipient_phone_number,
    'type': 'template',
    'template': {
        'name': 'menas_menues',
        'language': {
            'code': 'de'
        },
        'components': [
            {
                'type': 'header',
                'parameters': msg_header_params
            },
            {
                'type': 'body',
                'parameters': msg_body_params
            }
                
        ]
    }
}

response = sendMsg()

#print("Whatsapp API status: " + str(response.content) + "\n")
#print(msgOut)

#End main -------------------------------------------------------------------------------------------------------------------------------------