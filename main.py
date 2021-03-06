import asyncio
import datetime
import json
import logging
import os
import re
import time
import constant
from typing import List, Optional, Union

import wechaty
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from wechaty import (Contact, ContactType, FileBox, Message, MessageType,
                     MiniProgram, Room, ScanStatus, UrlLink, Wechaty, user)
from wechaty_puppet.schemas.contact import ContactQueryFilter
from wechaty_puppet.schemas.event import EventErrorPayload
from wechaty_puppet.schemas.mini_program import MiniProgramPayload
from wechaty_puppet.schemas.room import RoomQueryFilter
from wechaty_puppet.schemas.url_link import UrlLinkPayload

from ai_dialogue import DialogueBot
from weather import get_weather
from ocr import get_content_from_img

logging.basicConfig(
    level=logging.INFO,
    format=
    '%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
log = logging.getLogger(__name__)

# coupons code from Taobao
coupons = '7ðï¿¥5XbkXP4TW3Oï¿¥'
chat_friend: list = []
ai_bot = DialogueBot()
help_doc = """æä¼ä»¥ä¸æè½ï¼
1. åé `#ä½ ä¼å¥`ï¼æ¨éå¸®å©æä»¤
2. åé `#å¤©æ° å°å`æ¥å¤©æ°ï¼å¦ï¼`#å¤©æ° åäº¬`
3. åé `#å åäº` å¼å¯é²èæ¨¡å¼
4. åé `#ææ` å³é­é²èæ¨¡å¼
5. åé `#å¹²é¥­` æ¨éå¤ç ä¼æ ç 
6. å®æ¶æ¯å¤© 10ï¼30 æéå«å¤åæå¡ï¼å«ä¼æ ç ï¼
7. å¾çæå­ä¿¡æ¯æåï¼å­¦ä¹ æè½ä¸­ï¼
"""


async def check_room_join(bot: Optional[Wechaty], room: Optional[Room],
                          invitee_list: List[Contact], inviter: Contact):
    try:
        user_self = bot.user_self()
        if inviter.get_id() != user_self.contact_id:
            await room.say(
                'RULE1: Invitation is limited to me, the owner only. '
                'Please do not invite people without notify me.' + inviter)
            await room.say(
                'Please contact me: by send "ding" to me, I will re-send you a invitation. '
                'Now I will remove you out, sorry.' + ''.join(invitee_list))
            await room.topic('ding - warn ' + inviter.name)
            scheduler = AsyncIOScheduler()
            for i in invitee_list:
                scheduler.add_job(room.delete, args=[i], seconds=10)
            scheduler.start()
        else:
            await room.say("Welcom to my room! :)")
            welcomTopic = ','.join(map(lambda c: c.name), invitee_list)
            await room.topic(f'ding - welcom: {welcomTopic}')
    except Exception as e:
        log.exception(e)


async def manager_ding_room(bot: Optional[Wechaty]):
    time.sleep(3)
    log.info('Bot' + 'manager_ding_room()')
    try:
        room = await bot.Room.find(RoomQueryFilter(topic='HowlerBot'))
        log.info(f'room: {room}')
        if not room:
            log.warn('room is not find')
            return
        log.info(
            f"Bot start monitor <{room.payload.topic}> room join/leave/topic event"
        )

        def on_join(invitee_list, inviter):
            log.info('room.on(join) id:', room.room_id)
            check_room_join(bot, room, invitee_list, inviter)

    except Exception as e:
        log.error(f'something has wrong, {e}')


class HowlerBot(Wechaty):
    """
    listen wechaty event with inherited functions
    """
    def __init__(self):
        super().__init__()

    async def on_error(self, payload: EventErrorPayload):
        log.info(f"payload --> {str(payload)}")
        return await super().on_error(payload)

    async def on_logout(self, contact: Contact):
        log.info(f"Bot: {contact.name} logouted")
        return await super().on_logout(contact)

    async def on_login(self, contact: Contact):
        msg = f'{contact.payload.name} logined. datatime: {datetime.datetime.now()}'
        log.info(f'Bot: {msg}')
        contact.ready()
        master = await self.Contact.find(ContactQueryFilter(alias='master'))
        await master.say(msg)
        return await super().on_login(contact)

    async def on_scan(self, qr_code: str, status: ScanStatus,
                      data: Optional[str]):
        return await super().on_scan(qr_code, status, data=data)

    async def on_room_join(self, room: Room, invitees: List[Contact],
                           inviter: Contact, date: datetime):
        invitees_name = ','.join(map(lambda c: c.name, invitees))
        topic = await room.topic()
        log.info(
            f'Bot EVENT: room-join - Room "{topic}" got new member "{invitees_name}", invited by "{inviter.name}", date: {date}'
        )
        log.info('bot room-join room id:', room.room_id)
        await room.say('welcome {0} to "{1}"!'.format(invitees_name, topic))

    async def on_room_leave(self, room: Room, leavers: List[Contact],
                            remover: Contact, date: datetime):
        leavers_name = ','.join(map(lambda c: c.name, leavers))
        topic = await room.topic()
        log.info(
            f'Bot EVENT: room-leave - Room "{topic}" kick off member "{leavers_name}", removed by: "{remover.name}", date: {date}'
        )
        log.info('bot room-join room id:', room.room_id)
        await room.say(f'kick off "{leavers_name}" from "{topic}"')

    async def on_room_topic(self, room: Room, new_topic: str, old_topic: str,
                            changer: Contact, date: datetime):
        try:
            log.info(
                f'Bot EVENT: room-topic - Room "{room}" change topic from "{old_topic}" to "{new_topic}" by member "{changer.name}" at "{date}"'
            )
            await room.say(
                f'room topic - change topic from "{old_topic}" to "{new_topic}"'
            )
        except Exception as e:
            log.exception(e)

    async def on_message(self, msg: Message):
        from_contact = msg.talker()
        text = msg.text()
        send_contact = msg.to()
        room = msg.room()
        msg_type = msg.type()
        conversation: Union[Room,
                            Contact] = from_contact if room is None else room
        await conversation.ready()

        global chat_friend
        log.info(f"text: {text}")

        at_me = await msg.mention_self()

        rooms = await self.Room.find_all()
        log.info(f'rooms: {rooms}, nums: {len(rooms)}')

        # empty message (only open chat windows)
        if msg_type == MessageType.MESSAGE_TYPE_UNSPECIFIED:
            log.info(
                f"this msg may be empty. username: {conversation}, msg: {text}"
            )
            return

        if '#ä½ ä¼å¥' in text:
            await conversation.say(help_doc)
            return

        if '#å¤©æ°' in text:
            match_obj = re.match(r'^#å¤©æ°_[u4e00-u9fa5]?', text)

            match_obj = re.match(r'^(#å¤©æ°) ([\u4e00-\u9fa5]+)', text)

            if match_obj:
                log.info(f"match_obj.group(): {match_obj.group()}")
                weather = await get_weather(match_obj.group(2))
                await conversation.say(weather)
                return
            else:
                await conversation.say('è¯·å¨#å¤©æ°åç©ºä¸æ ¼è·ä¸è¦æ¥å¯»çå°åï¼ä¾å¦: #å¤©æ° åäº¬')
                return

        if '#å¹²é¥­' == text:
            await conversation.say('æå¼æ·å®ï¼å°å£ä»¤ç²è´´å°æç´¢æ¡ä¸­:')
            await conversation.say(coupons)
            return

        if '#ææ' == text:
            try:
                chat_friend.remove(conversation)
                ai_bot.history_clean()
            except Exception as e:
                log.error(e)
                return
            await conversation.say('ä¸æ¬¡å ï¼')
            return

        if '#å åäº' == text:
            chat_friend.append(conversation)
            await conversation.say('ä½ æ³å ç¹å¥ï¼')
            return

        if conversation in chat_friend:
            data = ai_bot.response(text)
            await conversation.say(data)
            return

        if msg_type == Message.Type.MESSAGE_TYPE_IMAGE:
            await conversation.say('å·²æ¶å°å¾åï¼æå­æåä¸­...')
            file_box_user_image = await msg.to_file_box()
            img_name = file_box_user_image.name
            img_path = f'./recieve_img/{img_name}'
            await file_box_user_image.to_file(file_path=img_path)
            word = await get_content_from_img(img_path)
            await conversation.say(word)
            return

        if msg_type == MessageType.MESSAGE_TYPE_RECALLED:
            recalled_msg = await msg.to_recalled()
            log.info(
                f"{from_contact.name} recalled msg: {recalled_msg.text()}")
            await conversation.say(f"{from_contact} recalled msg.")


bot: Optional[HowlerBot] = None


async def food_delivery(bot: Optional[Wechaty]):
    # sp_room = bot.Room.load(room_id="19363635010@chatroom")
    rooms = await bot.Room.find_all()
    for sp_room in rooms:
        sp_room_topic = await sp_room.topic()
        log.info(f'sp room topic: [{sp_room_topic}]')
        ding = "å¹²é¥­äºï¼å«å¿ç¨ä¼æ å¸ï¼æå¼æ·å®ï¼å°å£ä»¤ç²è´´å°æç´¢æ¡ä¸­ã"
        await sp_room.say(ding)
        await sp_room.say(coupons)


async def weather_forcast(bot: Optional[Wechaty]):
    pass


async def main():
    global bot
    bot = HowlerBot()
    scheduler = AsyncIOScheduler()
    trigger = CronTrigger(hour="10", minute="30")
    scheduler.add_job(food_delivery,
                      trigger=trigger,
                      args=[bot],
                      coalesce=True,
                      misfire_grace_time=60)
    scheduler.start()
    await bot.start()


os.environ['WECHATY_PUPPET'] = "wechaty-puppet-service"
# Replace it with your Token
os.environ[
    'WECHATY_PUPPET_SERVICE_TOKEN'] = constant.WECHATY_PUPPET_SERVICE_TOKEN
asyncio.run(main())
