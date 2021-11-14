from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
import requests
from time import sleep
import os

from requests.api import head
from __main__ import *

from PyroBot.__main__ import ADMIN_IDS, getCredits, setCredits

path = os.path.join("PyroBot", "temp")
if not os.path.exists(path): 
  os.mkdir(path) 
  
@Client.on_message(filters.command(["start"]))
async def startcmd(client:Client, message:Message):
    user = message.from_user or message.sender_chat
    user_mention = user.mention if message.from_user else user.title  
    await message.reply_text(f'**Hello** {user_mention}, \n\n**Type /cmds to know all my commands!**', 
                  reply_markup=InlineKeyboardMarkup([
                               [InlineKeyboardButton("💠 Developer", url="t.me/ninjanaveen")],
                               [InlineKeyboardButton("💰 Buy Authorization", url="t.me/KING_ANONYMOUS_XD")]]), quote=True)
       
@Client.on_message(filters.command(["cmds"]))
async def cmds(_, m):
    if m.from_user.id not in ADMIN_IDS:
        return await m.reply("**Which commands would you like to check?**", 
                  reply_markup=InlineKeyboardMarkup([
                               [InlineKeyboardButton("☎️ SMS Gateway Commands", f"help_gateway")]]), quote=True)
    
    if m.from_user.id in ADMIN_IDS:
        return await m.reply("**Which commands would you like to check?**", 
                  reply_markup=InlineKeyboardMarkup([
                               [InlineKeyboardButton("☎️ SMS Gateway Commands", f"help_gateway")],
                               [InlineKeyboardButton("🎖 Admin Commands", f"help_admin")]]), quote=True)

@Client.on_message(filters.command(["myacc"]))
async def myaccmd(client:Client, message:Message):
    user_id = message.from_user.id
    if not isPremium(user_id):
        return
    user_mention = message.from_user.mention if message.from_user else message.from_user.title  
    await message.reply(f'**Name:**  `{user_mention}`\n**UserID:**  `{user_id}`\n**Type:**  `Premium`\n**Credits:**  `{getCredits(user_id)}`', quote=True)
        
@Client.on_callback_query(filters.regex(r"^help_.*"))
async def cbstart(_, query: CallbackQuery):
    data = query.data
    sp = data.split("_")[1]
    user_id = query.from_user.id
    
    
    if sp == "gateway":
        if not isPremium(user_id):
            return await query.answer("You're not allowed to perform this action!", show_alert=True)    
        
        text = """**━━SMS Gateway Commands━━**
  
**/spam | !spam** - Send as reply to leads file with message as caption
**/test &lt;number&gt; | !test &lt;number&gt;** - Test bot working status
**/myacc | !myacc** - Your details


You can use `{number}` in message to replace it with the phone number""" 
        markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("Back", f"help_back")]
            ]) 

    elif sp == "admin":
        if user_id not in ADMIN_IDS:
            return  
        
        text = """**━━Admin Commands━━**
  
**/credits &lt;userid&gt; | !credits &lt;userid&gt;** - Check credits of a user
**/add &lt;userid&gt;|&lt;credits&gt; | !add &lt;userid&gt;|&lt;credits&gt;** - Add credits to a user
**/set &lt;userid&gt;|&lt;credits&gt; | !set &lt;userid&gt;|&lt;credits&gt;** - Overwrite a user's existing credits
**/suspend &lt;userid&gt; | !suspend &lt;userid&gt;** - Ban a premium user
""" 
        markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("Back", f"help_back")]
            ]) 
               
    elif sp == "back":
        text = "**Which commands would you like to check?**" 
        
        if user_id not in ADMIN_IDS:
            markup=InlineKeyboardMarkup([
                               [InlineKeyboardButton("☎️ SMS Gateway Commands", f"help_gateway")]])
            
        if user_id in ADMIN_IDS:
            markup=InlineKeyboardMarkup([
                               [InlineKeyboardButton("☎️ SMS Gateway Commands", f"help_gateway")],
                               [InlineKeyboardButton("🎖 Admin Commands", f"help_admin")]])
        
    await query.edit_message_text(text, reply_markup=markup) 
        
        
@Client.on_message(filters.command(["spam"]))
async def spamleads(_, m):
    user_id = m.from_user.id
    if not isPremium(user_id):
        return await m.reply("You are not authorized!")
    leadscount = 0
    file_id = m.reply_to_message.document.file_id
    filecaption = m.reply_to_message.caption
    filereq = requests.get('https://api.telegram.org/bot'+BOT_TOKEN+'/getFile?file_id='+file_id)
    filepath = filereq.json()['result']['file_path']
    
    filedl = requests.get('https://api.telegram.org/file/bot'+BOT_TOKEN+'/'+filepath)
    dllines = filedl.text.splitlines()
    with open('PyroBot/temp/leads'+str(m.from_user.id)+'.txt', 'w') as file:
        for line in dllines:
            leadscount+=1
            file.write(line+'\n')
        hasCredits = hasSufficientCredits(user_id,leadscount)
        
        if hasCredits != True:
            return await m.reply(f"**You don't have enough credits!\n\nYour Credits:- `{getCredits(user_id)}`**\n**This costs:-** `{costofLeads(leadscount)}`**", quote=True)
    
    with open('PyroBot/temp/msg'+str(m.from_user.id)+'.txt', 'w', encoding="utf-8") as file:
            file.write(filecaption)
    
    if user_id not in ADMIN_IDS:        
     await m.reply(f"**This costs `{costofLeads(leadscount)}` credits. Are you Sure? **", 
                  reply_markup=InlineKeyboardMarkup([
                               [InlineKeyboardButton("Yes!", f"sure_yes1"),
                               InlineKeyboardButton("No!", f"sure_no1")]]), quote=True)
    elif user_id in ADMIN_IDS:        
     await m.reply(f"**This doesn't cost credits coz you are admin <3. Are you Sure? **", 
                  reply_markup=InlineKeyboardMarkup([
                               [InlineKeyboardButton("Yes!", f"sure_yes1"),
                               InlineKeyboardButton("No!", f"sure_no1")]]), quote=True)

@Client.on_message(filters.command(["test"]))
async def testcmd(_, m):
    user_id = m.from_user.id
    
    if not isPremium(user_id):
        return await m.reply("You are not authorized!", quote=True)
    
    try:
        sp = m.text.split(None, 1)
    except:
        return await m.reply("**Provide Number! Format: /test +number**", quote=True)
    if sp:
        responsesms = await sendSMS(sp[1],"Test message by Spammer Bot")
        await m.reply(f"""Sent SMS to {sp[1]} - {responsesms}

**Spamming /test command will lead to BAN!**""", quote=True)
        for admin in ADMIN_IDS:
            await Client.send_message(chat_id=admin, text=f"{m.from_user.id} Sent a test SMS to {sp[1]}", self=app)

@Client.on_callback_query(filters.regex(r"^sure_.*"))
async def cb(bot: Client, query: CallbackQuery):
    data = query.data
    sp = data.split("_")[1]
    user_id = query.from_user.id
    
    
    if sp == "yes1":
        await query.message.edit("**Are you 100% Sure?**", 
                  reply_markup=InlineKeyboardMarkup([
                               [InlineKeyboardButton("No!", f"sure_no2"),
                                InlineKeyboardButton("Yes I'm 100% sure", f"sure_yes2")]]))
    
    if sp == "no1" or sp == 'no2':
        await query.message.edit("**Cancelled Process.**")
        os.remove('PyroBot/temp/leads'+str(user_id)+'.txt')
        os.remove('PyroBot/temp/msg'+str(user_id)+'.txt')
        
    if sp == "yes2":
        await query.message.edit("**You'll be notified once the process is over**")
        
        file=open('PyroBot/temp/leads'+str(user_id)+'.txt',"r",encoding="utf8",errors="ignore")
        numbers=file.readlines()
        
        file=open('PyroBot/temp/msg'+str(user_id)+'.txt',"r",encoding="utf8",errors="ignore")
        messagebody=file.read()
        
        sentleads = 0
        failedleads = 0
        completedleads = 0
        totalleads = len(numbers)
        
        for number in numbers:
            smsresponse = await sendSMS(number,messagebody)
            
            if smsresponse == True:
                sentleads+=1
            else:
                failedleads+=1
            
            completedleads+=1
            
        if completedleads == totalleads:
            deductCredits(user_id,totalleads)
            await query.message.edit(f"""**💠 Status - <u>SENT!</u> ✔️**
    
    
__🔲 Progress = {completedleads}/{totalleads}

🔳 Queued = {totalleads-completedleads}


🟩 Sent = {sentleads}

🟥 Failed = {failedleads}__""")
            
            
@Client.on_message(filters.command(["add"]))
async def upgrade(client:Client, message:Message):
    if not message.from_user.id in ADMIN_IDS:
        return 
    
    sp = message.text.split(None, 1)
    if len(sp) == 1:
        return await message.reply("**Provide UserId And Credits! Format: UserId|Credits**", quote=True)  
    
    kek = await message.reply("**Adding...**", quote=True)

    try:
        user_id = sp[1].split("|")[0]
        credits = sp[1].split("|")[1]
    except:
        return await kek.edit("**Provide UserId And Credits! Format: UserId|Credits**", quote=True)
    
    
    upgrade = addPremium(user_id,credits)
    if upgrade != True:
        txt = f"**Couldn't add user to database**"
    else:
        txt = f"**Added credits to user!**\n**User ID:** `{user_id}`\n**Message:** `Added to database`\n**Current Credits:** `"+getCredits(user_id)+f"`\n**Added credits:** `{credits}`"
     

    await kek.edit(txt)

@Client.on_message(filters.command(["set"]))
async def setthecredits (client:Client, message:Message):
    if not message.from_user.id in ADMIN_IDS:
        return 
    
    sp = message.text.split(None, 1)
    if len(sp) == 1:
        return await message.reply("**Provide UserId And Credits! Format: UserId|Credits**", quote=True)  
    
    kek = await message.reply("**Adding...**", quote=True)

    try:
        user_id = sp[1].split("|")[0]
        credits = sp[1].split("|")[1]
    except:
        return await kek.edit("**Provide UserId And Credits! Format: UserId|Credits**", quote=True)
    
    previouscredits = getCredits(user_id)
    upgrade = setCredits(user_id,credits)
    if upgrade != True:
        txt = f"**Couldn't set credits to database**"
    else:
        txt = f"**Set user's credits!**\n**User ID:** `{user_id}`\n**Message:** `Success`\n**Current Credits:** `"+getCredits(user_id)+f"`\n**Previous credits:** `{previouscredits}`"
     

    await kek.edit(txt)
    
@Client.on_message(filters.command(["credits"]))
async def showcreditsadmin(client:Client, message:Message):
    if not message.from_user.id in ADMIN_IDS:
        return 
    
    sp = message.text.split(None, 1)
    if len(sp) == 1:
        return await message.reply("**Provide UserId! Format: UserId**", quote=True)  
    
    kek = await message.reply("**Getting credits...**", quote=True)

    try:
        user_id = sp[1].split("|")[0]
    except:
        return await kek.edit("**Provide UserId! Format: UserId**")
    
    
    upgrade = getCredits(user_id)
    if not upgrade:
        txt = f"**Couldn't fetch user credits from database**"
    else:
        txt = f"**Fetched credits!**\n**User ID:** `{user_id}`\n**Credits:** `{upgrade}`"
     

    await kek.edit(txt)
    
    
@Client.on_message(filters.command(["suspend"]))
async def suspend(client:Client, message:Message):
    if not message.from_user.id in ADMIN_IDS:
        return 
    
    sp = message.text.split(None, 1)
    if not sp:
        return await message.reply("**Provide UserId! Format: UserId**", quote=True)  
    
    kek = await message.reply("**Adding...**", quote=True)

    try:
        user_id = sp[1].split("|")[0]
    except:
        return await kek.edit("**Provide UserId! Format: UserId**")
    
    try:
        suspend = banPremium(user_id)

        if suspend != True:
            txt = f"**Couldn't ban user from database**"
        else:
            txt = f"**Banned premium user!**\n**User ID:** `{user_id}`"
    except Exception as e:
        txt = e    
    

    await kek.edit(txt)
