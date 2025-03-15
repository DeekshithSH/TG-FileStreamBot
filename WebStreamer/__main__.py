# This file is a part of FileStreamBot

import sys
import asyncio
import logging
import traceback
import logging.handlers as handlers


from .vars import Var
from aiohttp import web
from WebStreamer.bot import StreamBot
from WebStreamer.server import web_server
from WebStreamer.utils.keepalive import ping_server
from WebStreamer.utils.utils import load_plugins, startup
from WebStreamer.bot.clients import initialize_clients


logging.basicConfig(
    level=logging.DEBUG if Var.DEBUG else logging.INFO,
    datefmt="%d/%m/%Y %H:%M:%S",
    format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(stream=sys.stdout),
              handlers.RotatingFileHandler("streambot.log", mode="a", maxBytes=104857600, backupCount=2, encoding="utf-8")],)

logging.getLogger("aiohttp").setLevel(logging.ERROR)
logging.getLogger("aiohttp.web").setLevel(logging.ERROR)
logging.getLogger("telethon").setLevel(logging.ERROR)

server = web.AppRunner(web_server())

#if sys.version_info[1] > 9:
#    loop = asyncio.new_event_loop()
#    asyncio.set_event_loop(loop)
#else:
loop = asyncio.get_event_loop()

async def start_services():
    print()
    print("-------------------- Initializing Telegram Bot --------------------")
    # await StreamBot.connect()
    await StreamBot.start(bot_token=Var.BOT_TOKEN)
    await startup(StreamBot)
    bot_info = await StreamBot.get_me()
    StreamBot.id = bot_info.id
    StreamBot.username = bot_info.username
    StreamBot.fname=bot_info.first_name
    print("------------------------------ DONE ------------------------------")
    print()
    print("---------------------- Initializing Clients ----------------------")
    await initialize_clients()
    if not Var.NO_UPDATE:
        print('--------------------------- Importing ---------------------------')
        load_plugins("WebStreamer/bot/plugins")
        print()
        print("------------------------------ DONE ------------------------------")
    if Var.KEEP_ALIVE:
        print("------------------ Starting Keep Alive Service ------------------")
        print()
        asyncio.create_task(ping_server())
    print()
    print("--------------------- Initializing Web Server ---------------------")
    await server.setup()
    await web.TCPSite(server, Var.BIND_ADDRESS, Var.PORT).start()
    print("------------------------------ DONE ------------------------------")
    print()
    print("------------------------- Service Started -------------------------")
    print("                        bot =>> {}".format(bot_info.first_name))
    print("                        DC ID =>> {}".format(str(StreamBot.session.dc_id)))
    print(" URL =>> {}".format(Var.URL))
    print("------------------------------------------------------------------")
    await StreamBot.run_until_disconnected()

async def cleanup():
    await server.cleanup()
    await StreamBot.disconnect()

if __name__ == "__main__":
    try:
        loop.run_until_complete(start_services())
    except KeyboardInterrupt:
        pass
    except Exception as err:
        logging.error(traceback.format_exc())
    finally:
        loop.run_until_complete(cleanup())
        loop.stop()
        print("------------------------ Stopped Services ------------------------")