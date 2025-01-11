import os
import re
import io
import pyrogram
import urllib
import imdb 
import json
ia = imdb.IMDb()
import random

from pyrogram import filters, Client
from pyrogram.enums import ChatType
from pyrogram.enums import ChatMemberStatus, ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup,WebAppInfo,KeyboardButton,ReplyKeyboardRemove

if bool(os.environ.get("WEBHOOK", False)):
    from config import Config
else:
    from config import Config

from database.filters_mdb import(
   add_filter,
   find_filter,
   find_filters,
   get_filters,
   delete_filter,
   count_filters
)
BDDONE = False
from database.connections_mdb import active_connection
from database.users_mdb import add_user, all_users

from plugins.helpers import parser,split_quotes,count_characters_custom


api_key=(
    "5a40141d",
    "6302a883",
    "3fdf086a",
    "598a9fda",
    "4dbe1117",
    "336c2676",
    "f8318839",
    "1d5c54fd",
    "3d690d35",
    "c336ba69",
    "1e0b8127",
    "3ef76477",
    "9b926251",
    "540f18a5",
    "1b368df8",
    "1eedb78f",
    "28ad23cc",
    "cf44929",
    "3c54b1ae",
    "45f3163",
    "84c1dab",
    "9a114799",
    "57b17298",
    "ac5a9f2",
    "76a20c7f",
    "2869b9e4",
    "a669b595",
    "9da058b",
    "8725cd26",
    "15b72301",
    "a1faa92a",
    "886948de",
    "ed8e84ef",
)

# Handler for the /buttonmake command
@Client.on_message(filters.command("buttonmake"))
async def buttonmake(client, message):
    button_data = {}
    chat_id = message.chat.id
    button_number = 1
    while True:
        answer = await message.chat.ask(
            f"Send me the name for Button {button_number}:"
        )
        button_name = answer.text
        if button_name == "/done":
            break
        
        link_data = {}
        for resolution in [480, 720, 1080]:
            link = None
            while link is None:
                answer = await message.chat.ask(
                    f"Send me the link for {resolution}:"
                )
                link = answer.text
                
                if link.lower() == "none":
                    link_data[resolution] = None
                    break
                
                if not link.startswith(("http://", "https://")):
                    link = None
                    await message.reply_text(
                        "Invalid link! Please send a valid URL."
                    )
                    continue
                
                try:
                    InlineKeyboardButton("Test Button", url=link)
                except ValueError:
                    link = None
                    await message.reply_text(
                        "Invalid link! Please send a valid URL."
                    )
                    continue
                
                link_data[resolution] = link
        button_data[button_name] = link_data
        button_number += 1
    buttons = []
    for key in button_data:
        callback_data = f"selectquality_{key.replace(' ', '%$').lower()}"
        button = InlineKeyboardButton(key, callback_data=callback_data)
        buttons.append([button])
    reply_markup = InlineKeyboardMarkup(buttons)
    message_text = "Demo Buttons"
    await message.reply_text(
    text=message_text,
    reply_markup=reply_markup
)

@Client.on_message(filters.command(Config.ADD_FILTER_CMD))
async def addfilter(client, message):
    userid = message.from_user.id
    chat_type = message.chat.type
    if message.text.endswith("-m"):
        AI = False
        args = message.text.html.split(None, 1)
        args[1] = args[1].replace(" -m", "")
    else:
        AI = True
        args = message.text.split(None, 1)
    if chat_type == ChatType.PRIVATE:
        grpid = await active_connection(str(userid))
        if grpid is not None:
            grp_id = grpid
            try:
                chat = await client.get_chat(grpid)
                title = chat.title
            except:
                await message.reply_text("Make sure I'm present in your group!!", quote=True)
                return
        else:
            await message.reply_text("I'm not connected to any groups!", quote=True)
            return

    elif (chat_type == ChatType.GROUP) or (chat_type == ChatType.SUPERGROUP):
        grp_id = message.chat.id
        title = message.chat.title

    else:
        return

    st = await client.get_chat_member(grp_id, userid)
    if not ((st.status == ChatMemberStatus.ADMINISTRATOR) or (st.status == ChatMemberStatus.OWNER) or (str(userid) in Config.AUTH_USERS)):
        return
        
    print(args)
    if len(args) < 2:
        await message.reply_text("Command Incomplete :(", quote=True)
        return
    
    extracted = split_quotes(args[1])
    text = extracted[0].lower()
    if " -k" in message.text:
        text = text.replace("-k", "")
        answer = await message.chat.ask(
            "Send me the keyword to search for"
        )
        text = answer.text
    if not AI:
        if not message.reply_to_message and len(extracted) < 2:
            await message.reply_text("Add some content to save your filter!", quote=True)
            return
    if AI:
        x2 = await message.reply_text(f"Searching for `{args[1].replace(' -k', '')}` on Internet Movie Database...")
        search = ia.search_movie(args[1].replace(" -k", "")) 

        id='tt'+search[0].movieID 
        
        key=random.choice(api_key)
        
        url= 'http://www.omdbapi.com/?i='+id+'&plot=full&apikey='+key+'&type=series'
        
        x=urllib.request.urlopen(url)
        
        for line in x:
            x=line.decode()
        
        data=json.loads(x)
        try:
            rating = data['imdbRating']
        except KeyError:
            rating = 0
        
        if rating == "N/A":
            rating2 = 0
        else:
            rating2 = round(float(rating))
        
        try:
            genre = data['Genre']
        except KeyError:
            genre = "Can't Recognize Movie 🎥"
        
        try:
            poster = data['Poster']
        except KeyError:
            poster = "https://telegra.ph/file/c9bbe7aef0cb672ecbd76.jpg"
        name = data['Title']
        year = data['Year']
        poster = data['Poster']
        genre = data['Genre']
        try:
            seasons = data['totalSeasons']
        except KeyError:
            await x2.edit("Series Not Found 🚫 use Manual Mode\n\nHow ? \nUse -m in the end of the commadd and send the name of the series")
            return
        rating = data['imdbRating']
        rating2 = "("+rating+"/10)"
        cast = data['Actors']
        plot = data['Plot']
        votes = data['imdbVotes']
        director = data['Director']
        lang = data['Language']
        date = data['Released']
        m1 = await message.reply_photo(
                photo=poster,
                caption=f"""
    **🍿 Series Name :** `{name} ({year[0:4]})`
    **🌟 Rating :** `{'' if rating == 'N/A' else rating2} {'' if votes == 'N/A' else '('+votes+' votes)'}`
    **🗣️ Languages :** `{lang}`
    **🎭 Cast :** `{cast}`
    **🎞️ Genre :** `{genre}`
    """,
                )
        tfileid = m1.photo.file_id
        tcaption = m1.caption.html
        message = await m1.reply_text(
            "Initializing, AI filters are processing...", 
            quote=True
        )
        seasons = int(data['totalSeasons'])
        print(seasons)
    if (len(extracted) >= 2) and not message.reply_to_message:
        reply_text, alert = parser(extracted[1], text)
        fileid = None
        if not reply_text:
            await message.reply_text("You cannot have buttons alone, give some text to go with it!", quote=True)
            return

    elif message.reply_to_message and message.reply_to_message.reply_markup:
        try:
            rm = message.reply_to_message.reply_markup
            btn = rm.inline_keyboard
            msg = message.reply_to_message.document or\
                  message.reply_to_message.video or\
                  message.reply_to_message.photo or\
                  message.reply_to_message.audio or\
                  message.reply_to_message.animation or\
                  message.reply_to_message.sticker
            if msg:
                fileid = msg.file_id
                reply_text = message.reply_to_message.caption.html
            else:
                reply_text = message.reply_to_message.text.html
                fileid = None
            alert = None
        except:
            reply_text = ""
            btn = "[]" 
            fileid = None
            alert = None

    elif message.reply_to_message and message.reply_to_message.photo:
        try:
            fileid = message.reply_to_message.photo.file_id
            reply_text, alert = parser(message.reply_to_message.caption.html, text)
        except:
            reply_text = ""
            btn = "[]"
            alert = None

    elif message.reply_to_message and message.reply_to_message.video:
        try:
            fileid = message.reply_to_message.video.file_id
            reply_text, alert = parser(message.reply_to_message.caption.html, text)
        except:
            reply_text = ""
            btn = "[]"
            alert = None

    elif message.reply_to_message and message.reply_to_message.audio:
        try:
            fileid = message.reply_to_message.audio.file_id
            reply_text, alert = parser(message.reply_to_message.caption.html, text)
        except:
            reply_text = ""
            btn = "[]"
            alert = None
   
    elif message.reply_to_message and message.reply_to_message.document:
        try:
            fileid = message.reply_to_message.document.file_id
            reply_text, alert = parser(message.reply_to_message.caption.html, text)
        except:
            reply_text = ""
            btn = "[]"
            alert = None

    elif message.reply_to_message and message.reply_to_message.animation:
        try:
            fileid = message.reply_to_message.animation.file_id
            reply_text, alert = parser(message.reply_to_message.caption.html, text)
        except:
            reply_text = ""
            btn = "[]"
            alert = None

    elif message.reply_to_message and message.reply_to_message.sticker:
        try:
            fileid = message.reply_to_message.sticker.file_id
            reply_text, alert =  parser(extracted[1], text)
        except:
            reply_text = ""
            btn = "[]"
            alert = None

    elif message.reply_to_message and message.reply_to_message.text:
        try:
            fileid = None
            reply_text, alert = parser(message.reply_to_message.text.html, text)
        except:
            reply_text = ""
            btn = "[]"
            alert = None
    elif AI:
        alert = None
        print("Nothing")
    else:
        print("Nothing")
        return
    button_data = {}
    chat_id = message.chat.id
    button_number = 1
    season_counter = 1
    if True:
        try:
            button = KeyboardButton("Create", web_app=WebAppInfo(url=f"https://trencoin-frontend.vercel.app"))
            answer = await message.chat.ask(
                "Click on the button to create filters",
                timeout=None,
                filters=filters.service,
                reply_markup=ReplyKeyboardMarkup(
                    [[button]],
                    one_time_keyboard=True,
                    resize_keyboard=True
                ),
                
            )
            # await message.reply(answer.web_app_data.data,reply_markup=ReplyKeyboardRemove())
            # turn string into json
            data = json.loads(answer.web_app_data.data)
            text = data['keyword']
            button_data = data['buttonData']
            if AI:
                reply_text = tcaption
                fileid = tfileid
            else:
                reply_text = reply_text
                fileid = fileid
            # print(data)
            await add_filter(grp_id, text, reply_text, button_data, fileid, alert)
            await message.reply_text(
                f"Filter for  `{text}`  added in  **{title}**",
                quote=True
            )
            return
        except Exception as e:
            print(e)
        return
        
    while True:
        if AI:
            button_name = "Season " + str(season_counter)
            season_counter += 1
            if season_counter > (seasons+1):
                break
        else:
            answer = await message.chat.ask(
                f"Send me the name for Button {button_number}:\n\nSend /done After Done"
            )
            if count_characters_custom(answer.text) > 25:
                await message.reply_text(
                    "⚠ Name too long. Please send a name with less than 25 characters."
                )
                continue
            button_name = answer.text
            if button_name == "/done":
                break
        
        link_data = {}
        for resolution in [480, 720, 1080]:
            link = None
            while link is None:
                if AI:
                    answer = await message.chat.ask(
                        f"Season {season_counter-1}\nSend me the link for {resolution}:\n\nSend /skip if you don't want that resolution"
                    )
                else:
                    answer = await message.chat.ask(
                        f"Send me the link for {resolution}:\n\nSend /skip if you don't want that resolution"
                    )
                link = answer.text
                
                if link.lower() == "/skip":
                    link_data[resolution] = None
                    break
                
                if not link.startswith(("http://", "https://")):
                    link = None
                    await message.reply_text(
                        "Invalid link! Please send a valid URL."
                    )
                    continue
                
                try:
                    InlineKeyboardButton("Test Button", url=link)
                except ValueError:
                    link = None
                    await message.reply_text(
                        "Invalid link! Please send a valid URL."
                    )
                    continue
                link_data[resolution] = link
        button_data[button_name] = link_data
        button_number += 1
    if AI:
        reply_text = tcaption
        fileid = tfileid
    await add_filter(grp_id, text, reply_text, button_data, fileid, alert)
    await message.reply_text(
        f"Filter for  `{text}`  added in  **{title}**",
        quote=True
    )


@Client.on_message(filters.command('viewfilters'))
async def get_all(client, message):
    
    chat_type = message.chat.type

    if chat_type == ChatType.PRIVATE:
        userid = message.from_user.id
        grpid = await active_connection(str(userid))
        if grpid is not None:
            grp_id = grpid
            try:
                chat = await client.get_chat(grpid)
                title = chat.title
            except:
                await message.reply_text("Make sure I'm present in your group!!", quote=True)
                return
        else:
            await message.reply_text("I'm not connected to any groups!", quote=True)
            return

    elif (chat_type == ChatType.GROUP) or (chat_type == ChatType.SUPERGROUP):
        grp_id = message.chat.id
        title = message.chat.title

    else:
        return

    st = await client.get_chat_member(grp_id, userid)
    if not ((st.status == ChatMemberStatus.ADMINISTRATOR) or (st.status == ChatMemberStatus.OWNER) or (str(userid) in Config.AUTH_USERS)):
        return

    texts = await get_filters(grp_id)
    # count = await count_filters(grp_id)
    count = 0
    if texts:
        filterlist = f"Total number of filters in **{title}** : {count}\n\n"

        for text in texts:
            count += 1
            keywords = " ×  `{}`\n".format(text)
            
            filterlist += keywords

        if len(filterlist) > 4096:
            with io.BytesIO(str.encode(filterlist.replace("`", ""))) as keyword_file:
                keyword_file.name = "keywords.txt"
                await message.reply_document(
                    document=keyword_file,
                    quote=True
                )
            return
    else:
        filterlist = f"There are no active filters in **{title}**"

    await message.reply_text(
        text=filterlist,
        quote=True,
    )
        
@Client.on_message(filters.command(Config.DELETE_FILTER_CMD))
async def deletefilter(client, message):
    userid = message.from_user.id
    chat_type = message.chat.type

    if chat_type == ChatType.PRIVATE:
        grpid  = await active_connection(str(userid))
        if grpid is not None:
            grp_id = grpid
            try:
                chat = await client.get_chat(grpid)
                title = chat.title
            except:
                await message.reply_text("Make sure I'm present in your group!!", quote=True)
                return
        else:
            await message.reply_text("I'm not connected to any groups!", quote=True)

    elif (chat_type == ChatType.GROUP) or (chat_type == ChatType.SUPERGROUP):
        grp_id = message.chat.id
        title = message.chat.title

    else:
        return

    st = await client.get_chat_member(grp_id, userid)
    if not ((st.status == ChatMemberStatus.ADMINISTRATOR) or (st.status == ChatMemberStatus.OWNER) or (str(userid) in Config.AUTH_USERS)):
        return

    try:
        cmd, text = message.text.split(" ", 1)
    except:
        await message.reply_text(
            "<i>Mention the filtername which you wanna delete!</i>\n\n"
            "<code>/del filtername</code>\n\n"
            "Use /viewfilters to view all available filters",
            quote=True
        )
        return

    query = text.lower()

    await delete_filter(message, query, grp_id)
        

@Client.on_message(filters.command(Config.DELETE_ALL_CMD))
async def delallconfirm(client, message):
    userid = message.from_user.id
    chat_type = message.chat.type

    if chat_type == ChatType.PRIVATE:
        grpid  = await active_connection(str(userid))
        if grpid is not None:
            grp_id = grpid
            try:
                chat = await client.get_chat(grpid)
                title = chat.title
            except:
                await message.reply_text("Make sure I'm present in your group!!", quote=True)
                return
        else:
            await message.reply_text("I'm not connected to any groups!", quote=True)
            return

    elif (chat_type == ChatType.GROUP) or (chat_type == ChatType.SUPERGROUP):
        grp_id = message.chat.id
        title = message.chat.title

    else:
        return

    st = await client.get_chat_member(grp_id, userid)
    if (st.status == ChatMemberStatus.OWNER) or (str(userid) in Config.AUTH_USERS):
        await message.reply_text(
            f"This will delete all filters from '{title}'.\nDo you want to continue??",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(text="YES",callback_data="delallconfirm")],
                [InlineKeyboardButton(text="CANCEL",callback_data="delallcancel")]
            ]),
            quote=True
        )


@Client.on_message(filters.group & filters.text)
async def give_filter(client,message):
    # global BDDONE
    # if not BDDONE:
    #     for adminid in Config.AUTH_USERS:
    #         await client.copy_message(adminid, -1001662470317, 1106)
    #     BDDONE = True
    group_id = message.chat.id
    name = message.text
    print(name)
    try:
        keywords = await get_filters(group_id)
        print(keywords)
        index = 0
        for keyword in reversed(sorted(keywords, key=len)):
            pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
            if re.search(pattern, name, flags=re.IGNORECASE):
                sfilters = await find_filters(group_id, keyword)
                length = len(sfilters)
                print(length)
                print(index)
                for x in range(length):
                    x = sfilters[index]
                    index += 1
                    dataid = x["id"]
                    fileid = x["fileid"]
                    btn = x["btn"]
                    reply_text = x["reply_text"]
                    if reply_text:
                        reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")

                    if btn is not None:
                        try:
                            if fileid == "None":
                                if btn == "[]":
                                    await message.reply_text(reply_text, disable_web_page_preview=True)
                                else:
                                    button_data = eval(btn)
                                    buttons = []
                                    for key in button_data:
                                        callback_data = f"selectquality_{key.replace(' ', '%$')}_{dataid}"
                                        button = InlineKeyboardButton(key, callback_data=callback_data)
                                        buttons.append([button])
                                    
                                    await message.reply_text(
                                        reply_text,
                                        disable_web_page_preview=True,
                                        reply_markup=InlineKeyboardMarkup(buttons)
                                    )
                            else:
                                if btn == "[]":
                                    await message.reply_cached_media(
                                        fileid,
                                        caption=reply_text or ""
                                    )
                                else:
                                    button_data = eval(btn)
                                    buttons = []
                                    for key in button_data:
                                        callback_data = f"selectquality_{key.replace(' ', '%$')}_{dataid}"
                                        button = InlineKeyboardButton(key, callback_data=callback_data)
                                        buttons.append([button])
                                    await message.reply_cached_media(
                                        fileid,
                                        caption=reply_text or "",
                                        reply_markup=InlineKeyboardMarkup(buttons)
                                    )
                        except Exception as e:
                            print(e)
                            pass
                        break 
    except Exception as e:
        print(e)                
    if Config.SAVE_USER == "yes":
        try:
            await add_user(
                str(message.from_user.id),
                str(message.from_user.username),
                str(message.from_user.first_name + " " + (message.from_user.last_name or "")),
                str(message.from_user.dc_id)
            )
        except:
            pass
      
