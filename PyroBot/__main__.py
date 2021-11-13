import os
import logging
import pyrogram
from decouple import config
import pymysql, requests
from pyrogram.filters import user

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)

# vars
APP_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
AUTH_IDS = set(int(x) for x in os.environ.get("AUTH_IDS").split())
ADMIN_IDS = set(int(x) for x in os.environ.get("ADMIN_IDS").split())


TWILIO_SID = "ACf15c73e78baba374db270f259ded078c"
TWILIO_AUTHTOKEN = "c5495026c2b915f875aa4c1004e77de2"
TWILIO_SERVICEID = "MG962b4acdc6e5cf23b4e601d61e87b350"
DEDUCTION_PER_SEND = 0.02
AMOUNT_PER_CREDIT = 0.02


mydb = pymysql.connect(
  host="sql3.freesqldatabase.com",
  user="sql3450594",
  password="65DvDAPiGJ",
  database="sql3450594",
  autocommit=True
)
mycursor = mydb.cursor()

def num(s):
    try:
        return int(s)
    except ValueError:
        return float(s)
      
def isPremium(userid):
  if userid in ADMIN_IDS:
    return True
  sql = f"SELECT * FROM premium WHERE userid = {userid}"
  resp = mycursor.execute(sql)
  result = mycursor.fetchall()
  if result:
    return True
  else:
    return False

def addPremium(userid,credits):
    if isPremium(userid) != True:
        sql = f"INSERT INTO premium (userid, credits) VALUES ('{userid}','{float(credits)}')"
        mycursor.execute(sql)
        mydb.commit()
        return True
    elif isPremium(userid) == True:
        currentcredits = getCredits(userid)
        newcredits = num(currentcredits)+num(credits)
        
        sql = f"UPDATE premium SET credits = '{newcredits}' WHERE userid = '{userid}'"
        mycursor.execute(sql)
        mydb.commit()
        return True
        

def banPremium(userid):
  if userid in ADMIN_IDS:
    return False
  sql = f"DELETE FROM premium WHERE userid='{userid}'"
  mycursor.execute(sql)
  mydb.commit()
  return True

def getCredits(userid):
  sql = f"SELECT credits FROM premium WHERE userid = '{userid}'"
  mycursor.execute(sql)
  result = mycursor.fetchall()
  return result[0][0]

def costofLeads(totalleads):
  return totalleads*DEDUCTION_PER_SEND

def hasSufficientCredits(userid,totalleads):
  usercredits = getCredits(userid)
  cost = costofLeads(totalleads)
  
  if userid in ADMIN_IDS:
    return True
  elif num(usercredits) >= cost:
    return True
  else:
    return False

def deductCredits(userid,totalleads):
  usercredits = getCredits(userid)
  cost = costofLeads(totalleads)
  newcredits = num(usercredits)-cost
  
  sql = f"UPDATE premium SET credits = '{newcredits}' WHERE userid = '{userid}'"
  mycursor.execute(sql)
  mydb.commit()
  
async def sendSMS(number,smsmessage):
    smsmessage = smsmessage.replace('{number}',number)
    
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    postdata = {

    'To': number,
    'Body': smsmessage,
    'MessagingServiceSid': TWILIO_SERVICEID

    }
    postsms = requests.post(f'https://api.twilio.com/2010-04-01/Accounts/{TWILIO_SID}/Messages.json', headers=headers, data=postdata, auth=(TWILIO_SID, TWILIO_AUTHTOKEN))
    
    if postsms.json()['status'] == 'accepted':
        return True
    else:
        return False
  

if __name__ == "__main__" :
    print("Starting Bot...")
    plugins = dict(root="PyroBot/plugins")
    app = pyrogram.Client(
        "Ninja",
        bot_token=BOT_TOKEN,
        api_id=APP_ID,
        api_hash=API_HASH,
        plugins=plugins
    )
    print("Bot has been successfully deployed!")
    app.run()
    
    
