from TEAMZYRO import *
import importlib
import asyncio
from pyrogram import idle
from TEAMZYRO.modules import ALL_MODULES


async def main() -> None:
    for module_name in ALL_MODULES:
        importlib.import_module("TEAMZYRO.modules." + module_name)
    LOGGER("TEAMZYRO.modules").info("𝐀𝐥𝐥 𝐅𝐞𝐚𝐭𝐮𝐫𝐞𝐬 𝐋𝐨𝐚𝐝𝐞𝐝 𝐁𝐚𝐛𝐲🥳...")

    await ZYRO.start()

    LOGGER("TEAMZYRO").info(
        "╔═════ஜ۩۞۩ஜ════╗\n  ☠︎︎BOT IS ONLINE☠︎︎\n╚═════ஜ۩۞۩ஜ════╝"
    )

    await idle()
    await ZYRO.stop()


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
