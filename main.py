import asyncio
import logging
import os
import datetime
import time
from typing import List, Optional, Union

from wechaty import (Wechaty, Contact, ContactType, Message, MessageType,
                     FileBox, UrlLink, MiniProgram, ScanStatus, Room, user)
import wechaty
from wechaty_puppet.schemas.contact import ContactQueryFilter
from wechaty_puppet.schemas.event import EventErrorPayload
from wechaty_puppet.schemas.mini_program import MiniProgramPayload
from wechaty_puppet.schemas.room import RoomQueryFilter
from wechaty_puppet.schemas.url_link import UrlLinkPayload
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from ai_dialogue import DialogueBot

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
log = logging.getLogger(__name__)

# coupons code from Taobao
coupons = '7👈￥5XbkXP4TW3O￥'
chat_friend: list = []
ai_bot = DialogueBot()

async def check_room_join(bot: Optional[Wechaty],
                          room: Optional[Room],
                          invitee_list: List[Contact],
                          inviter: Contact):
    try:
        user_self = bot.user_self()
        if inviter.get_id() != user_self.contact_id:
            await room.say('RULE1: Invitation is limited to me, the owner only. '
                           'Please do not invite people without notify me.' + inviter)
            await room.say('Please contact me: by send "ding" to me, I will re-send you a invitation. '
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
            f"Bot start monitor <{room.payload.topic}> room join/leave/topic event")

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

    async def on_scan(self, qr_code: str, status: ScanStatus, data: Optional[str]):
        return await super().on_scan(qr_code, status, data=data)

    async def on_room_join(self, room: Room, invitees: List[Contact],
                           inviter: Contact, date: datetime):
        invitees_name = ','.join(map(lambda c: c.name, invitees))
        topic = await room.topic()
        log.info(
            f'Bot EVENT: room-join - Room "{topic}" got new member "{invitees_name}", invited by "{inviter.name}", date: {date}')
        log.info('bot room-join room id:', room.room_id)
        await room.say('welcome {0} to "{1}"!'.format(invitees_name, topic))

    async def on_room_leave(self, room: Room, leavers: List[Contact],
                            remover: Contact, date: datetime):
        leavers_name = ','.join(map(lambda c: c.name, leavers))
        topic = await room.topic()
        log.info(
            f'Bot EVENT: room-leave - Room "{topic}" kick off member "{leavers_name}", removed by: "{remover.name}", date: {date}')
        log.info('bot room-join room id:', room.room_id)
        await room.say(f'kick off "{leavers_name}" from "{topic}"')

    async def on_room_topic(self, room: Room, new_topic: str, old_topic: str, changer: Contact, date: datetime):
        try:
            log.info(
                f'Bot EVENT: room-topic - Room "{room}" change topic from "{old_topic}" to "{new_topic}" by member "{changer.name}" at "{date}"')
            await room.say(f'room topic - change topic from "{old_topic}" to "{new_topic}"')
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
                f"this msg may be empty. username: {conversation}, msg: {text}")
            return
        
        if '#干饭' == text:
            await conversation.say('打开淘宝，将口令粘贴到搜索框中:')
            await conversation.say(coupons)
            return

        if '#拜拜' == text:
            try:
                chat_friend.remove(conversation)
                ai_bot.history_clean()
            except Exception as e:
                log.error(e)
                return
            await conversation.say('下次唠！')
            return

        if '#唠嗑了' == text:
            chat_friend.append(conversation)
            await conversation.say('你想唠点啥？')
            return

        if conversation in chat_friend:
            data = ai_bot.response(text)
            await conversation.say(data)
            return

        if msg_type == Message.Type.MESSAGE_TYPE_IMAGE:
            # await conversation.say('已收到图像，开始变换')
            # file_box_user_image = await msg.to_file_box()
            # img_name = file_box_user_image.name
            # img_path = f'./recieve_img/{img_name}'
            # await file_box_user_image.to_file(file_path=img_path)
            # await conversation.say(f"image file path: {img_path}")
            return

        if msg_type == MessageType.MESSAGE_TYPE_RECALLED:
            recalled_msg = await msg.to_recalled()
            log.info(f"{from_contact.name} recalled msg: {recalled_msg.text()}")
            await conversation.say(f"{from_contact} recalled msg.")


bot: Optional[HowlerBot] = None


async def food_delivery(bot: Optional[Wechaty]):
    # sp_room = bot.Room.load(room_id="19363635010@chatroom")
    rooms = await bot.Room.find_all()
    for sp_room in rooms:
        sp_room_topic = await sp_room.topic()
        log.info(f'sp room topic: [{sp_room_topic}]')
        ding = "干饭了！别忘用优惠券！打开淘宝，将口令粘贴到搜索框中。"
        await sp_room.say(ding)
        await sp_room.say(coupons)


async def weather_forcast(bot: Optional[Wechaty]):
    pass


async def main():
    global bot
    bot = HowlerBot()
    scheduler = AsyncIOScheduler()
    trigger = CronTrigger(hour="10", minute="30, 45")
    scheduler.add_job(food_delivery,
                      trigger=trigger,
                      args=[bot],
                      coalesce=True,
                      misfire_grace_time=60)
    scheduler.start()
    await bot.start()

os.environ['WECHATY_PUPPET'] = "wechaty-puppet-service"
os.environ['WECHATY_PUPPET_SERVICE_TOKEN'] = "60788d8e-4ea7-4d81-9349-8b0d697866b1"
asyncio.run(main())
