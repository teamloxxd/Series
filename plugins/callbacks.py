import os
import ast
import re
from pyrogram.enums import ChatType
from pyrogram.enums import ChatMemberStatus, ParseMode
from pyrogram import Client as trojanz
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

if bool(os.environ.get("WEBHOOK", False)):
    from config import Config
else:
    from config import Config

from script import Script
from database.filters_mdb import del_all, find_filter,get_filters,find_filter_byid


from database.connections_mdb import(
    all_connections,
    active_connection,
    if_active,
    delete_connection,
    make_active,
    make_inactive
)


@trojanz.on_callback_query()
async def cb_handler(client, query):
    original_message = query.message.reply_to_message
        
    if query.data == "start_data":
        await query.answer()
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Command Help", callback_data="help_data")
                ]
            ]
        )

        await query.message.edit_text(
            Script.START_MSG.format(query.from_user.mention),
            reply_markup=keyboard,
            disable_web_page_preview=True
        )
        return
    elif query.data.startswith("backselect_"):
        if original_message.from_user.id == query.from_user.id:
            old_caption = query.message.caption or ""
            old_caption = old_caption.replace("Select Quality","")
            search = query.data.split("_")
            search = search[1]
            print(search)
            name = query.message.reply_to_message.text
            group_id = query.message.chat.id
            keywords = await get_filters(group_id)
            for keyword in reversed(sorted(keywords, key=len)):
                pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
                if re.search(pattern, name, flags=re.IGNORECASE):
                    reply_text, btn, alert, fileid = await find_filter_byid(id=search, group_id=group_id)
                    button_data = eval(btn)
                    buttons = []
                    for key in button_data:
                        callback_data = f"selectquality_{key.replace(' ', '%$')}_{search}"
                        button = InlineKeyboardButton(key, callback_data=callback_data)
                        buttons.append([button])
                    reply_markup = InlineKeyboardMarkup(buttons)
            await query.message.edit_text(f"{old_caption}",reply_markup=reply_markup)
        else:
            await client.answer_callback_query(query.id, text="This callback is only for the sender.")
    elif query.data.startswith("selectquality_"):
        if original_message.from_user.id == query.from_user.id:
            old_caption = query.message.caption or ""
            search = query.data.split("_")
            dataid = search[2]
            search = search[1]
            season = search.replace("%$"," ")
            name = query.message.reply_to_message.text
            group_id = query.message.chat.id
            keywords = await get_filters(group_id)
            for keyword in reversed(sorted(keywords, key=len)):
                pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
                if re.search(pattern, name, flags=re.IGNORECASE):
                    print(await find_filter_byid(group_id, dataid))
                    reply_text, btn, alert, fileid = await find_filter_byid(group_id, dataid)
                    button_data = eval(btn)
                    links = button_data[season]
                    first_row = []
                    second_row = []
                    keyboard = []
                    for resolution, url in links.items():
                        if url is not None and url != "":
                            url = url.replace("https://t.me/God_pluto_bot?start=", "https://t.me/dcfusionbot/betalab?startapp=tgseries_")
                            if len(first_row) < 2:
                                first_row.append(InlineKeyboardButton(f"{resolution}", url=url))
                            else:
                                second_row.append(InlineKeyboardButton(f"{resolution}", url=url))
                    keyboard = [first_row, second_row]
                    keyboard.append([InlineKeyboardButton("Back ↩", callback_data=f"backselect_{dataid}")])
                    reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.edit_text(f"{old_caption}\n\nSelect Quality",reply_markup=reply_markup)
        else:
            await client.answer_callback_query(query.id, text="This callback is only for the sender.")
    elif query.data == "help_data":
        await query.answer()
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("How to Deploy?", url="https://youtu.be/hkmc3e7U7R4"),
                    InlineKeyboardButton("About Me", callback_data="about_data")
                ],
                [
                    InlineKeyboardButton("BOT Channel", url="https://t.me/TroJanzHEX"),
                    InlineKeyboardButton("Support Group", url="https://t.me/TroJanzSupport")
                ]
            ]
        )

        await query.message.edit_text(
            Script.HELP_MSG,
            reply_markup=keyboard,
            disable_web_page_preview=True
        )
        return

    elif query.data == "about_data":
        await query.answer()
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "SOURCE CODE", url="https://github.com/TroJanzHEX/Unlimited-Filter-Bot")
                ],
                [
                    InlineKeyboardButton("BACK", callback_data="help_data"),
                    InlineKeyboardButton("CLOSE", callback_data="close_data"),
                ]                
            ]
        )

        await query.message.edit_text(
            Script.ABOUT_MSG,
            reply_markup=keyboard,
            disable_web_page_preview=True
        )
        return

    elif query.data == "close_data":
        await query.message.delete()
        

    elif query.data == "delallconfirm":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == ChatType.PRIVATE:
            grpid  = await active_connection(str(userid))
            if grpid is not None:
                grp_id = grpid
                try:
                    chat = await client.get_chat(grpid)
                    title = chat.title
                except:
                    await query.message.edit_text("Make sure I'm present in your group!!", quote=True)
                    return
            else:
                await query.message.edit_text(
                    "I'm not connected to any groups!\nCheck /connections or connect to any groups",
                    quote=True
                )
                return

        elif (chat_type == ChatType.GROUP) or (chat_type == ChatType.SUPERGROUP):
            grp_id = query.message.chat.id
            title = query.message.chat.title

        else:
            return

        st = await client.get_chat_member(grp_id, userid)
        if (st.status == ChatMemberStatus.OWNER) or (str(userid) in Config.AUTH_USERS):    
            await del_all(query.message, grp_id, title)
        else:
            await query.answer("You need to be Group Owner or an Auth User to do that!",show_alert=True)
    
    elif query.data == "delallcancel":
        userid = query.from_user.id
        chat_type = query.message.chat.type
        
        if chat_type == ChatType.PRIVATE:
            await query.message.reply_to_message.delete()
            await query.message.delete()

        elif (chat_type == ChatType.GROUP) or (chat_type == ChatType.SUPERGROUP):
            grp_id = query.message.chat.id
            st = await client.get_chat_member(grp_id, userid)
            if (st.status == ChatMemberStatus.OWNER) or (str(userid) in Config.AUTH_USERS):
                await query.message.delete()
                try:
                    await query.message.reply_to_message.delete()
                except:
                    pass
            else:
                await query.answer("Thats not for you!!",show_alert=True)


    elif "groupcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]
        title = query.data.split(":")[2]
        act = query.data.split(":")[3]
        user_id = query.from_user.id

        if act == "":
            stat = "CONNECT"
            cb = "connectcb"
        else:
            stat = "DISCONNECT"
            cb = "disconnect"

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{stat}", callback_data=f"{cb}:{group_id}:{title}"),
                InlineKeyboardButton("DELETE", callback_data=f"deletecb:{group_id}")],
            [InlineKeyboardButton("BACK", callback_data="backcb")]
        ])

        await query.message.edit_text(
            f"Group Name : **{title}**\nGroup ID : `{group_id}`",
            reply_markup=keyboard,
            parse_mode="md"
        )
        return

    elif "connectcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]
        title = query.data.split(":")[2]
        user_id = query.from_user.id

        mkact = await make_active(str(user_id), str(group_id))

        if mkact:
            await query.message.edit_text(
                f"Connected to **{title}**",
                parse_mode="md"
            )
            return
        else:
            await query.message.edit_text(
                f"Some error occured!!",
                parse_mode="md"
            )
            return

    elif "disconnect" in query.data:
        await query.answer()

        title = query.data.split(":")[2]
        user_id = query.from_user.id

        mkinact = await make_inactive(str(user_id))

        if mkinact:
            await query.message.edit_text(
                f"Disconnected from **{title}**",
                parse_mode="md"
            )
            return
        else:
            await query.message.edit_text(
                f"Some error occured!!",
                parse_mode="md"
            )
            return
    elif "deletecb" in query.data:
        await query.answer()

        user_id = query.from_user.id
        group_id = query.data.split(":")[1]

        delcon = await delete_connection(str(user_id), str(group_id))

        if delcon:
            await query.message.edit_text(
                "Successfully deleted connection"
            )
            return
        else:
            await query.message.edit_text(
                f"Some error occured!!",
                parse_mode="md"
            )
            return
    
    elif query.data == "backcb":
        await query.answer()

        userid = query.from_user.id

        groupids = await all_connections(str(userid))
        if groupids is None:
            await query.message.edit_text(
                "There are no active connections!! Connect to some groups first.",
            )
            return
        buttons = []
        for groupid in groupids:
            try:
                ttl = await client.get_chat(int(groupid))
                title = ttl.title
                active = await if_active(str(userid), str(groupid))
                if active:
                    act = " - ACTIVE"
                else:
                    act = ""
                buttons.append(
                    [
                        InlineKeyboardButton(
                            text=f"{title}{act}", callback_data=f"groupcb:{groupid}:{title}:{act}"
                        )
                    ]
                )
            except:
                pass
        if buttons:
            await query.message.edit_text(
                "Your connected group details ;\n\n",
                reply_markup=InlineKeyboardMarkup(buttons)
            )

    elif "alertmessage" in query.data:
        grp_id = query.message.chat.id
        i = query.data.split(":")[1]
        keyword = query.data.split(":")[2]
        reply_text, btn, alerts, fileid = await find_filter(grp_id, keyword)
        if alerts is not None:
            alerts = ast.literal_eval(alerts)
            alert = alerts[int(i)]
            alert = alert.replace("\\n", "\n").replace("\\t", "\t")
            await query.answer(alert,show_alert=True)
