from pyrogram import Client, filters
import Config
from ForceSubscribeBot.database.chats_sql import get_force_chat, get_action, get_ignore_service
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, ChatPermissions
from pyrogram.errors import ChatAdminRequired, UserNotParticipant, ChatWriteForbidden


@Client.on_message(filters.group, group=-1)
async def main(bot: Client, msg: Message):
    if not msg.from_user:
        return
    user_id = msg.from_user.id
    if user_id in Config.DEVS:
        return
    chat_id = msg.chat.id
    force_chat = await get_force_chat(chat_id)
    ignore_service = await get_ignore_service(chat_id)
    if ignore_service and msg.service:
        return
    if not force_chat:
        return
    try:
        try:
            await bot.get_chat_member(force_chat, user_id)
        except UserNotParticipant:
            chat_member = await msg.chat.get_member(user_id)
            if chat_member.status in ("creator", "administrator"):
                return
            chat = await bot.get_chat(force_chat)
            mention = '@' + chat.username if chat.username else f"[{chat.title}]({chat.invite_link})"
            link = chat.invite_link
            try:
                action = await get_action(chat_id)
                if action == 'kick':
                    await msg.chat.kick_member(user_id)
                    await msg.chat.unban_member(user_id)
                    await msg.reply("Kicked member because not joined Force Subscribe Chat")
                    return
                elif action == 'ban':
                    await msg.chat.kick_member(user_id)
                    await msg.reply("Banned member because not joined Force Subscribe Chat")
                    return
                buttons = [[InlineKeyboardButton("🔰 Join TamilRoars 🔰", url=link)]]
                if action == 'mute':
                    await msg.chat.restrict_member(user_id, ChatPermissions(can_send_messages=False))
                    buttons.append([InlineKeyboardButton("Joined ✅ ", callback_data=f"joined+{msg.from_user.id}")])
                await msg.reply(
                    f"💖 நீங்கள் இன்னும் @Tamil_Roars சேனலில் சேரவில்லை. நீங்கள் இணைந்தால் மட்டுமே இந்த குழுவிற்கு செய்தி அனுப்ப முடியும். இணைந்த பிறகு, joined என்பதைக் கிளிக் செய்யவும். 💖\n\n💖 ʏᴏᴜ ʜᴀᴠᴇ ɴᴏᴛ ʏᴇᴛ ᴊᴏɪɴᴇᴅ ᴛʜᴇ ᴛᴀᴍɪʟʀᴏᴀʀs ᴄʜᴀɴɴᴇʟ. ʏᴏᴜ ᴄᴀɴ ᴏɴʟʏ ᴍᴇssᴀɢᴇ ᴛʜɪs ɢʀᴏᴜᴘ ɪꜰ ʏᴏᴜ ᴊᴏɪɴ. ᴀꜰᴛᴇʀ ᴊᴏɪɴɪɴɢ, ᴄʟɪᴄᴋ ᴏɴ ᴊᴏɪɴᴇᴅ 💖",
                    disable_web_page_preview=True,
                    reply_markup=InlineKeyboardMarkup(buttons),
                )
                await msg.stop_propagation()
            except ChatWriteForbidden:
                pass
    except ChatAdminRequired:
        await msg.reply(f"I have been demoted in `{force_chat}` (force subscribe chat)!")
