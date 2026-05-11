import asyncio

# Patch the loop on ZYRO BEFORE importing anything else,
# so that @app.on_message decorators schedule their tasks
# on the correct running loop.
async def main() -> None:
    import importlib
    from pyrogram import idle
    from TEAMZYRO import ZYRO, LOGGER
    from TEAMZYRO.modules import ALL_MODULES

    # Point ZYRO at the loop that is actually running RIGHT NOW
    ZYRO.loop = asyncio.get_running_loop()

    for module_name in ALL_MODULES:
        importlib.import_module("TEAMZYRO.modules." + module_name)

    # Let all the create_task() calls from @app.on_message decorators execute
    await asyncio.sleep(0)

    LOGGER("TEAMZYRO.modules").info("𝐀𝐥𝐥 𝐅𝐞𝐚𝐭𝐮𝐫𝐞𝐬 𝐋𝐨𝐚𝐝𝐞𝐝 𝐁𝐚𝐛𝐲🥳...")

    await ZYRO.start()

    LOGGER("TEAMZYRO").info(
        "╔═════ஜ۩۞۩ஜ════╗\n  ☠︎︎BOT IS ONLINE☠︎︎\n╚═════ஜ۩۞۩ஜ════╝"
    )

    await idle()
    await ZYRO.stop()


if __name__ == "__main__":
    asyncio.run(main())
