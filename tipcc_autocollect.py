from asyncio import TimeoutError, sleep, CancelledError
from datetime import datetime, UTC
from logging import (
    CRITICAL,
    DEBUG,
    ERROR,
    INFO,
    WARNING,
    Formatter,
    StreamHandler,
    getLogger,
)
from math import acosh, asinh, atanh, ceil, cos, cosh, e, erf, exp
from math import fabs as abs
from math import factorial, floor
from math import fmod as mod
from math import (
    gamma,
    gcd,
    hypot,
    log,
    log1p,
    log2,
    log10,
    pi,
    pow,
    sin,
    sinh,
    sqrt,
    tan,
    tau,
)
from os import listdir
from random import randint, uniform
from re import compile
from time import time
from typing import Dict, List, Union, Optional
from urllib.parse import quote, unquote

from aiohttp import ClientSession
from art import tprint
from discord import Client, HTTPException, LoginFailure, Message, NotFound, Status, Embed, TextChannel, Button
from discord.ext import tasks
from questionary import checkbox, select, text


class ColourFormatter(
    Formatter
):  # Taken from discord.py-self and modified to my liking.

    LEVEL_COLOURS = [
        (DEBUG, "\x1b[40;1m"),
        (INFO, "\x1b[34;1m"),
        (WARNING, "\x1b[33;1m"),
        (ERROR, "\x1b[31m"),
        (CRITICAL, "\x1b[41m"),
    ]

    FORMATS = {
        level: Formatter(
            f"\x1b[30;1m%(asctime)s\x1b[0m {colour}%(levelname)-8s\x1b[0m \x1b[35m%(name)s\x1b[0m %(message)s \x1b[30;1m(%(filename)s:%(lineno)d)\x1b[0m",
            "%d-%b-%Y %I:%M:%S %p",
        )
        for level, colour in LEVEL_COLOURS
    }

    def format(self, record):
        formatter = self.FORMATS.get(record.levelno)
        if formatter is None:
            formatter = self.FORMATS[DEBUG]

        if record.exc_info:
            text = formatter.formatException(record.exc_info)
            record.exc_text = f"\x1b[31m{text}\x1b[0m"

        output = formatter.format(record)

        record.exc_text = None
        return output


handler = StreamHandler()
formatter = ColourFormatter()

handler.setFormatter(formatter)
logger = getLogger("tipcc_autocollect")
logger.addHandler(handler)
logger.setLevel("INFO")


def cbrt(x):
    return pow(x, 1 / 3)


try:
    from ujson import dump, load, JSONDecodeError
except (ModuleNotFoundError, ImportError):
    logger.warning("ujson not found, using json instead.")
    from json import dump, load, JSONDecodeError
else:
    logger.info("ujson found, using ujson.")

channel: Optional[TextChannel] = None
DropConfig = Dict[str, Union[bool, List[Union[int, float]], List[str], float, List[Dict[str, Union[float, int]]]]]

print("\033[0;35m")
tprint("QuartzWarrior", font="smslant")
print("\033[0m")

try:
    with open("config.json", "r") as f:
        config = load(f)
except (FileNotFoundError, JSONDecodeError):
    config = {
        "TOKEN": "",
        "PRESENCE": "",
        "FIRST": True,
        "ID": 0,
        "CHANNEL_ID": 0,
        "TARGET_AMOUNT": 0.0,
        "CPM": [],
        "WHITELIST": [],
        "BLACKLIST": [],
        "WHITELIST_ON": False,
        "BLACKLIST_ON": False,
        "TELEGRAM": {
            "TOKEN": "",
            "CHAT_ID": 0
        }
    }
    with open("config.json", "w") as f:
        dump(config, f, indent=4)

try:
    with open("servers/default.json", "r") as f:
        default: Dict[str, Union[List[str], DropConfig, bool, float, List[int]]] = load(f)
except (FileNotFoundError, JSONDecodeError):
    default: Dict[str, Union[List[str], DropConfig, bool, float, List[int]]] = {
        "BANNED_WORDS": [],
        "MESSAGES": [],
        "CHANNEL_WHITELIST": [],
        "CHANNEL_BLACKLIST": [],
        "IGNORE_USERS": [],
        "SEND_MESSAGE": False,
        "CHANNEL_WHITELIST_ON": False,
        "CHANNEL_BLACKLIST_ON": False,
        "IGNORE_DROPS_UNDER": 0.0,
        "IGNORE_TIME_UNDER": 0.0,
        "IGNORE_THRESHOLDS": [],
        "AIRDROP": {
            "ENABLED": True,
            "SMART_DELAY": {
                "ENABLED": True,
                "DELAY": [0.25, 0.50]
            },
            "RANGE_DELAY": False,
            "DELAY": [
                0,
                1
            ],
            "SEND_MESSAGE": False,
            "MESSAGE_CHANCE": 0.5,
            "MESSAGES": [],
            "IGNORE_DROP_UNDER": 0.0,
            "IGNORE_TIME_UNDER": 0.0,
            "IGNORE_THRESHOLDS": []
        },
        "TRIVIADROP": {
            "ENABLED": True,
            "SMART_DELAY": {
                "ENABLED": True,
                "DELAY": [0.25, 0.50]
            },
            "RANGE_DELAY": False,
            "DELAY": [
                0,
                1
            ],
            "SEND_MESSAGE": False,
            "MESSAGE_CHANCE": 0.5,
            "MESSAGES": [],
            "IGNORE_DROP_UNDER": 0.0,
            "IGNORE_TIME_UNDER": 0.0,
            "IGNORE_THRESHOLDS": []
        },
        "MATHDROP": {
            "ENABLED": True,
            "CPM": [
                200,
                310
            ],
            "SMART_DELAY": {
                "ENABLED": True,
                "DELAY": [0.25, 0.50]
            },
            "RANGE_DELAY": False,
            "DELAY": [
                0,
                1
            ],
            "SEND_MESSAGE": False,
            "MESSAGE_CHANCE": 0.5,
            "MESSAGES": [],
            "IGNORE_DROP_UNDER": 0.0,
            "IGNORE_TIME_UNDER": 0.0,
            "IGNORE_THRESHOLDS": []
        },
        "PHRASEDROP": {
            "ENABLED": True,
            "CPM": [
                200,
                310
            ],
            "SMART_DELAY": {
                "ENABLED": True,
                "DELAY": [0.25, 0.50]
            },
            "RANGE_DELAY": False,
            "DELAY": [
                0,
                1
            ],
            "SEND_MESSAGE": False,
            "MESSAGE_CHANCE": 0.5,
            "MESSAGES": [],
            "IGNORE_DROP_UNDER": 0.0,
            "IGNORE_TIME_UNDER": 0.0,
            "IGNORE_THRESHOLDS": []
        },
        "REDPACKET": {
            "ENABLED": True,
            "SMART_DELAY": {
                "ENABLED": True,
                "DELAY": [0.25, 0.50]
            },
            "RANGE_DELAY": False,
            "DELAY": [
                0,
                1
            ],
            "SEND_MESSAGE": False,
            "MESSAGE_CHANCE": 0.5,
            "MESSAGES": [],
            "IGNORE_DROP_UNDER": 0.0,
            "IGNORE_TIME_UNDER": 0.0,
            "IGNORE_THRESHOLDS": []
        }
    }
    with open("servers/default.json", "w") as f:
        dump(default, f, indent=4)

token_regex = compile(r"[\w-]{24}\.[\w-]{6}\.[\w-]{27,}")
decimal_regex = compile(r"^-?\d+\.\d+$")


def validate_token(token):
    if token_regex.search(token):
        return True
    else:
        return False


def validate_decimal(decimal):
    if decimal_regex.match(decimal):
        return True
    else:
        return False


def validate_threshold_chance(s):
    try:
        threshold, chance = s.split(":")
        return (
                validate_decimal(threshold)
                and chance.isnumeric()
                and 0 <= int(chance) <= 100
        )
    except ValueError:
        if s == "":
            return True
        return False


if config["TOKEN"] == "":
    token_input = text(
        "What is your discord token?",
        qmark="->",
        validate=lambda x: validate_token(x),
    ).ask()
    if token_input is not None:
        config["TOKEN"] = token_input
        with open("config.json", "w") as f:
            dump(config, f, indent=4)
        logger.debug("Token saved.")

if config["FIRST"]:
    config["PRESENCE"] = select(
        "What do you want your presence to be?",
        choices=[
            "online",
            "idle",
            "dnd",
            "invisible",
        ],
        default="invisible",
        qmark="->",
    ).ask()
    config["FIRST"] = False
    user_id = int(
        text(
            "What is your main accounts id?\n\nIf you are sniping from your main, put your main accounts' id.",
            validate=lambda x: x.isnumeric() and 17 <= len(x) <= 19,
            qmark="->",
        ).ask()
    )
    config["ID"] = user_id
    channel_id = int(
        text(
            "What is the channel id where you want your alt to tip your main?\n(Remember, the tip.cc bot has to be in the server with this channel.)\n\nIf None, send 1.",
            validate=lambda x: x.isnumeric() and (17 <= len(x) <= 19 or int(x) == 1),
            default="1",
            qmark="->",
        ).ask()
    )
    config["CHANNEL_ID"] = channel_id
    if channel_id != 1:
        target_amount = float(
            text(
                "What is the target amount you want to tip your main at? Set it to 0 to disable.",
                validate=lambda x: validate_decimal(x) or x.isnumeric(),
                default="0",
                qmark="->",
            ).ask()
        )
        config["TARGET_AMOUNT"] = target_amount
        cpm = text(
            f"What is the minimum CPM you want to use for tipping?",
            validate=lambda x: x.isnumeric() and 0 <= int(x) <= 10000,
            qmark="->",
        ).ask()
        cpm_max = text(
            f"What is the maximum CPM you want to use for tipping?",
            validate=lambda x: x.isnumeric() and 0 <= int(x) <= 10000,
            qmark="->",
        ).ask()
        config["CPM"] = [int(cpm), int(cpm_max)]
    enable_whitelist = select(
        "Do you want to enable server whitelist?",
        choices=["yes", "no"],
        qmark="->",
    ).ask()
    config["WHITELIST_ON"] = enable_whitelist == "yes"
    if config["WHITELIST_ON"]:
        whitelist = text(
            "What servers do you want to whitelist? Separate each server ID with a comma.",
            validate=lambda x: (
                                       len(x) > 0
                                       and all(y.isnumeric() and 17 <= len(y) <= 19 for y in x.split(","))
                               )
                               or x == "",
            qmark="->",
        ).ask()
        if not whitelist:
            whitelist = []
        else:
            whitelist = [int(x) for x in whitelist.split(",")]
        config["WHITELIST"] = whitelist
    else:
        enable_blacklist = select(
            "Do you want to enable server blacklist?",
            choices=["yes", "no"],
            qmark="->",
        ).ask()
        config["BLACKLIST_ON"] = enable_blacklist == "yes"
        if config["BLACKLIST_ON"]:
            blacklist = text(
                "What servers do you want to blacklist? Separate each server ID with a comma.",
                validate=lambda x: (
                                           len(x) > 0
                                           and all(y.isnumeric() and 17 <= len(y) <= 19 for y in x.split(","))
                                   )
                                   or x == "",
                qmark="->",
            ).ask()
            if not blacklist:
                blacklist = []
            else:
                blacklist = [int(x) for x in blacklist.split(",")]
            config["BLACKLIST"] = blacklist
    tg = select(
        "Do you want to enable telegram notifications?",
        choices=["yes", "no"],
        qmark="->",
    ).ask()
    if tg == "yes":
        tg_token = text(
            "What is your telegram bot token?",
            validate=lambda x: len(x) > 0,
            qmark="->",
        ).ask()
        tg_chat_id = text(
            "What is your telegram chat id?",
            validate=lambda x: x.isnumeric() and 17 <= len(x) <= 19,
            qmark="->",
        ).ask()
        config["TELEGRAM"]["TOKEN"] = tg_token
        config["TELEGRAM"]["CHAT_ID"] = int(tg_chat_id)
    with open("config.json", "w") as f:
        dump(config, f, indent=4)
    logger.debug("Config saved.")
    logger.info("Account configuration finished. Now configuring server settings.")
    banned_words = text(
        "What words do you want to ban? Separate each word with a comma.",
        qmark="->",
    ).ask()
    if not banned_words:
        banned_words = ["bot", "ban", "kick", "raid", "scam", "scammer", "scamming", "scammed", "scamming",
                        "scamming", ]
    else:
        banned_words = banned_words.split(",")
    default["BANNED_WORDS"] = banned_words
    ignore_drops_under = text(
        "What is the minimum amount of money you want to ignore for all drops?",
        default="0",
        qmark="->",
        validate=lambda x: ((validate_decimal(x) or x.isnumeric()) and float(x) >= 0)
                           or x == "",
    ).ask()
    if ignore_drops_under != "":
        default["IGNORE_DROPS_UNDER"] = float(ignore_drops_under)
    else:
        default["IGNORE_DROPS_UNDER"] = 0.0
    ignore_time_under = text(
        "What is the minimum time you want to ignore for all drops?",
        default="0",
        qmark="->",
        validate=lambda x: ((validate_decimal(x) or x.isnumeric()) and float(x) >= 0)
                           or x == "",
    ).ask()
    if ignore_time_under != "":
        default["IGNORE_TIME_UNDER"] = float(ignore_time_under)
    else:
        default["IGNORE_TIME_UNDER"] = 0.0
    ignore_thresholds = text(
        "Enter your ignore thresholds and chances for all drops in the format 'threshold:chance', separated by commas (e.g. '0.10:10,0.20:20')",
        validate=lambda x: all(validate_threshold_chance(pair) for pair in x.split(","))
                           or x == "",
        default="",
        qmark="->",
    ).ask()
    if ignore_thresholds != "":
        default["IGNORE_THRESHOLDS"] = [
            {"threshold": float(pair.split(":")[0]), "chance": int(pair.split(":")[1])}
            for pair in ignore_thresholds.split(",")
        ]
    else:
        default["IGNORE_THRESHOLDS"] = []
    enable_channel_whitelist = select(
        "Do you want to enable channel whitelist for all drops?",
        choices=["yes", "no"],
        qmark="->",
    ).ask()
    default["CHANNEL_WHITELIST_ON"] = enable_channel_whitelist == "yes"
    if not default["CHANNEL_WHITELIST_ON"]:
        enable_channel_blacklist = select(
            "Do you want to enable channel blacklist for all drops?",
            choices=["yes", "no"],
            qmark="->",
        ).ask()
        default["CHANNEL_BLACKLIST_ON"] = enable_channel_blacklist == "yes"
        if default["CHANNEL_BLACKLIST_ON"]:
            blacklist = text(
                "What channels do you want to blacklist for all drops? Separate each channel ID with a comma.",
                validate=lambda x: (
                                           len(x) > 0
                                           and all(y.isnumeric() and 17 <= len(y) <= 19 for y in x.split(","))
                                   )
                                   or x == "",
                qmark="->",
            ).ask()
            if not blacklist:
                blacklist = []
            else:
                blacklist = [int(x) for x in blacklist.split(",")]
            default["CHANNEL_BLACKLIST"] = blacklist
    else:
        whitelist = text(
            "What channels do you want to whitelist for all drops? Separate each channel ID with a comma.",
            validate=lambda x: (
                                       len(x) > 0
                                       and all(y.isnumeric() and 17 <= len(y) <= 19 for y in x.split(","))
                               )
                               or x == "",
            qmark="->",
        ).ask()
        if not whitelist:
            whitelist = []
        else:
            whitelist = [int(x) for x in whitelist.split(",")]
        default["CHANNEL_WHITELIST"] = whitelist
    ignore_users = text(
        "What users do you want to ignore for all drops? Separate each user ID with a comma.",
        validate=lambda x: (
                                   len(x) > 0
                                   and all(y.isnumeric() and 17 <= len(y) <= 19 for y in x.split(","))
                           )
                           or x == "",
        qmark="->",
    ).ask()
    if not ignore_users:
        ignore_users = []
    else:
        ignore_users = [int(x) for x in ignore_users.split(",")]
    default["IGNORE_USERS"] = ignore_users
    choices = ["airdrop", "triviadrop", "mathdrop", "phrasedrop", "redpacket"]
    disable_drops = checkbox(
        "What drop types do you want to disable? (Leave blank for none)",
        choices=choices,
        qmark="->",
    ).ask()
    if not disable_drops:
        disable_drops = []
    for drop in disable_drops:
        default[drop.upper()]["ENABLED"] = False
    choices = [
        choice
        for choice in choices
        if choice not in disable_drops
    ]
    for drop in choices:
        if drop == "phrasedrop" or drop == "mathdrop":
            cpm = text(
                f"What is the minimum CPM you want to use for {drop}?",
                validate=lambda x: x.isnumeric() and 0 <= int(x) <= 1000,
                qmark="->",
            ).ask()
            cpm_max = text(
                f"What is the maximum CPM you want to use for {drop}?",
                validate=lambda x: x.isnumeric() and 0 <= int(x) <= 1000,
                qmark="->",
            ).ask()
            default[drop.upper()]["CPM"] = [int(cpm), int(cpm_max)]
        smart_delay = select(
            f"Do you want to enable smart delay for {drop}?",
            choices=["yes", "no"],
            qmark="->",
        ).ask()
        if smart_delay == "yes":
            default[drop.upper()]["SMART_DELAY"]["ENABLED"] = True
            min_delay = text(
                f"Enter the MINIMUM fraction of remaining drop time to wait (e.g., 0.25 means waiting at least 25% of the remaining time)",
                validate=lambda x: (validate_decimal(x) or x.isnumeric()) and 0 <= float(x) <= 1,
                qmark="->",
            ).ask()
            max_delay = text(
                f"Enter the MAXIMUM fraction of remaining drop time to wait (e.g., 0.5 means waiting up to 50% of the remaining time)",
                validate=lambda x: (validate_decimal(x) or x.isnumeric()) and 0 <= float(x) <= 1,
                qmark="->",
            ).ask()
            default[drop.upper()]["SMART_DELAY"]["DELAY"] = [float(min_delay), float(max_delay)]
        else:
            default[drop.upper()]["SMART_DELAY"]["ENABLED"] = False
            range_delay = select(
                f"Do you want to enable range delay for {drop}?",
                choices=["yes", "no"],
                qmark="->",
            ).ask()
            if range_delay == "yes":
                default[drop.upper()]["RANGE_DELAY"] = True
                min_delay = text(
                    f"What is the minimum delay you want to use for {drop} in seconds?",
                    validate=lambda x: (validate_decimal(x) or x.isnumeric()) and float(x) >= 0,
                    qmark="->",
                ).ask()
                max_delay = text(
                    f"What is the maximum delay you want to use for {drop} in seconds?",
                    validate=lambda x: (validate_decimal(x) or x.isnumeric()) and float(x) >= 0,
                    qmark="->",
                ).ask()
                default[drop.upper()]["DELAY"] = [float(min_delay), float(max_delay)]
            else:
                manual_delay = text(
                    f"What is the delay you want to use for {drop} in seconds? (Leave blank for none)",
                    validate=lambda x: (validate_decimal(x) or x.isnumeric()) or x == "",
                    default="0",
                    qmark="->",
                ).ask()
                if manual_delay != "":
                    default[drop.upper()]["DELAY"] = [float(manual_delay), float(manual_delay)]
                else:
                    default[drop.upper()]["DELAY"] = [0, 0]
        send_messages = select(
            f"Do you want to send messages after claiming a {drop}?",
            choices=["yes", "no"],
            qmark="->",
        ).ask()
        default[drop.upper()]["SEND_MESSAGE"] = send_messages == "yes"
        if default[drop.upper()]["SEND_MESSAGE"]:
            message_chance = text(
                f"What is the chance you want to send a message after claiming a {drop}? (e.g., 0.5 for 50%)",
                validate=lambda x: (validate_decimal(x) or x.isnumeric()) and 0 <= float(x) <= 1,
                default="0.5",
                qmark="->",
            ).ask()
            default[drop.upper()]["MESSAGE_CHANCE"] = float(message_chance)
            messages = text(
                f"What messages do you want to send after claiming a {drop}? Separate each message with a comma.",
                validate=lambda x: len(x) > 0 or x == "",
                qmark="->",
            ).ask()
            if not messages:
                messages = []
            else:
                messages = messages.split(",")
            default[drop.upper()]["MESSAGES"] = messages
        ignore_drops_under = text(
            f"What is the minimum amount of money you want to ignore for {drop}?",
            default="0",
            qmark="->",
            validate=lambda x: ((validate_decimal(x) or x.isnumeric()) and float(x) >= 0)
                               or x == "",
        ).ask()
        if ignore_drops_under != "":
            default[drop.upper()]["IGNORE_DROP_UNDER"] = float(ignore_drops_under)
        else:
            default[drop.upper()]["IGNORE_DROP_UNDER"] = 0.0
        ignore_time_under = text(
            f"What is the minimum time you want to ignore for {drop}?",
            default="0",
            qmark="->",
            validate=lambda x: ((validate_decimal(x) or x.isnumeric()) and float(x) >= 0)
                               or x == "",
        ).ask()
        if ignore_time_under != "":
            default[drop.upper()]["IGNORE_TIME_UNDER"] = float(ignore_time_under)
        else:
            default[drop.upper()]["IGNORE_TIME_UNDER"] = 0.0
        ignore_thresholds = text(
            f"Enter your ignore thresholds and chances for {drop} in the format 'threshold:chance', separated by commas (e.g. '0.10:10,0.20:20')",
            validate=lambda x: all(validate_threshold_chance(pair) for pair in x.split(","))
                               or x == "",
            default="",
            qmark="->",
        ).ask()
        if ignore_thresholds != "":
            default[drop.upper()]["IGNORE_THRESHOLDS"] = [
                {"threshold": float(pair.split(":")[0]), "chance": int(pair.split(":")[1])}
                for pair in ignore_thresholds.split(",")
            ]
        else:
            default[drop.upper()]["IGNORE_THRESHOLDS"] = []
    with open("servers/default.json", "w") as f:
        dump(default, f, indent=4)
    logger.debug("Default server config saved.")
    logger.info("Server configuration finished.")

banned_words = set(default["BANNED_WORDS"])

client = Client(
    status=(
        Status.invisible
        if config["PRESENCE"] == "invisible"
        else (
            Status.online
            if config["PRESENCE"] == "online"
            else (
                Status.idle
                if config["PRESENCE"] == "idle"
                else Status.dnd if config["PRESENCE"] == "dnd" else Status.unknown
            )
        )
    )
)


@client.event
async def on_ready():
    global channel
    channel = client.get_channel(config["CHANNEL_ID"])
    logger.info(f"Logged in as {client.user.name}#{client.user.discriminator}")
    if config["CHANNEL_ID"] != 1 and client.user.id != config["ID"]:
        tipping.start()
        logger.info("Tipping started.")
    else:
        logger.warning("Disabling tipping as requested.")


@tasks.loop(minutes=10.0)
async def tipping():
    await channel.send("$bals top")
    logger.debug("Sent command: $bals top")
    answer = await client.wait_for(
        "message",
        check=lambda message: message.author.id == 617037497574359050
                              and message.embeds,
    )
    try:
        total_money = float(
            answer.embeds[0]
            .fields[-1]
            .value.split("$")[1]
            .replace(",", "")
            .replace("**", "")
            .replace(")", "")
            .replace("\u200b", "")
            .strip()
        )
    except Exception as e:
        logger.exception("Error occurred while getting total money, skipping tipping.")
        total_money = 0.0
    logger.debug(f"Total money: {total_money}")
    if total_money < config["TARGET_AMOUNT"]:
        logger.info("Target amount not reached, skipping tipping.")
        return
    try:
        pages = int(answer.embeds[0].author.name.split("/")[1].replace(")", ""))
    except:
        pages = 1
    if not answer.components:
        button_disabled = True
    for _ in range(pages):
        try:
            button: Button = answer.components[0].children[1]
            button_disabled = button.disabled
        except:
            button_disabled = True
        for crypto in answer.embeds[0].fields:
            if "Estimated total" in crypto.name:
                continue
            if "DexKit" in crypto.name:
                content = f"$tip <@{config['ID']}> all {crypto.name.replace('*', '').replace('DexKit (BSC)', 'bKIT')}"
            else:
                content = f"$tip <@{config['ID']}> all {crypto.name.replace('*', '')}"
            async with channel.typing():
                await sleep(len(content) / randint(config["CPM"][0], config["CPM"][1]) * 60)
            await channel.send(content)
            logger.debug(f"Sent tip: {content}")
        if button_disabled:
            try:
                await answer.components[0].children[2].click()
                logger.debug("Clicked next page button")
                return
            except IndexError:
                try:
                    await answer.components[0].children[0].click()
                    logger.debug("Clicked first page button")
                    return
                except IndexError:
                    return
        else:
            await button.click()
            await sleep(1)
            answer = await channel.fetch_message(answer.id)
    await telegram(f"Tipped {config['ID']} {total_money} in {answer.channel.name}.")


@tipping.before_loop
async def before_tipping():
    logger.info("Waiting for bot to be ready before tipping starts...")
    await client.wait_until_ready()


async def telegram(message: str):
    if config.get("TELEGRAM", {}).get("TOKEN") and config.get("TELEGRAM", {}).get("CHAT_ID"):
        try:
            async with ClientSession() as session:
                async with session.post(f"https://api.telegram.org/bot{config['TELEGRAM']['TOKEN']}/sendMessage", json={
                    "chat_id": config["TELEGRAM"]["CHAT_ID"],
                    "text": message,
                    "parse_mode": "Markdown"}
                                        ) as response:
                    if response.status == 200:
                        logger.debug(f"Telegram notification sent: {message}")
                    else:
                        response_text = await response.text()
                        logger.warning(f"Failed to send Telegram notification: {response_text}")
        except Exception as e:
            logger.exception(f"Error sending Telegram notification: {e}")


@client.event
async def on_message(original_message: Message):
    if f"{original_message.channel.id}.json" in listdir("servers"):
        try:
            with open(f"servers/{original_message.channel.id}.json", "r") as f:
                configuration = load(f)
        except (FileNotFoundError, JSONDecodeError):
            configuration = default
    else:
        configuration = default
    droptype = False
    message_content_lowered = original_message.content.lower().split(" ")[0]
    if any([True if word in message_content_lowered else False for word in
            ["airdrop", "phrasedrop", "triviadrop", "mathdrop", "redenvelope", "redpacket"]]):
        if "airdrop" in message_content_lowered:
            droptype = "AIRDROP"
        elif "phrasedrop" in message_content_lowered:
            droptype = "PHRASEDROP"
        elif "triviadrop" in message_content_lowered:
            droptype = "TRIVIADROP"
        elif "mathdrop" in message_content_lowered:
            droptype = "MATHDROP"
        elif "redenvelope" in message_content_lowered or "redpacket" in message_content_lowered:
            droptype = "REDPACKET"
        else:
            return
    if (droptype and configuration[droptype]["ENABLED"]
            and
            not any(word in original_message.content.lower() for word in banned_words)
            and (
                    not config["WHITELIST_ON"]
                    or (
                            config["WHITELIST_ON"]
                            and original_message.guild.id in config["WHITELIST"]
                    )
            )
            and (
                    not config["BLACKLIST_ON"]
                    or (
                            config["BLACKLIST_ON"]
                            and original_message.guild.id not in config["BLACKLIST"]
                    )
            )
            and (
                    not configuration["CHANNEL_WHITELIST_ON"]
                    or (
                            configuration["CHANNEL_WHITELIST_ON"]
                            and original_message.channel.id in configuration["CHANNEL_WHITELIST"]
                    )
            )
            and (
                    not configuration["CHANNEL_BLACKLIST_ON"]
                    or (
                            configuration["CHANNEL_BLACKLIST_ON"]
                            and original_message.channel.id not in configuration["CHANNEL_BLACKLIST"]
                    )
            )
            and original_message.author.id not in configuration["IGNORE_USERS"]
    ):
        logger.debug(
            f"Detected drop in {original_message.channel.name}: {original_message.content}"
        )
        try:
            tip_cc_message = await client.wait_for(
                "message",
                check=lambda message: message.author.id == 617037497574359050
                                      and message.channel.id == original_message.channel.id
                                      and ((message.embeds
                                            and message.embeds[0].footer
                                            and "ends" in message.embeds[0].footer.text.lower()
                                            and str(original_message.author.id) in message.embeds[0].description) or (
                                                   "ends" in message.content.lower() and str(
                                               original_message.author.id) in message.content)),
                timeout=15,
            )
            logger.debug("Detected tip.cc message from drop.")
        except (TimeoutError, CancelledError):
            logger.exception(
                "Timeout occurred while waiting for tip.cc message, skipping."
            )
            return
        if tip_cc_message.embeds:
            embed = tip_cc_message.embeds[0]
        else:
            content_lines = tip_cc_message.content.split("\n")
            logger.debug(content_lines)
            timestamp = datetime.fromtimestamp(int(content_lines[-1].split("<t:")[1].split(":")[0].split(">")[0]), UTC)
            logger.debug(timestamp)
            embed = Embed(title=content_lines[0], description="\n".join(content_lines[1:len(content_lines) - 1]),
                          timestamp=timestamp)
            embed.set_footer(text=content_lines[-1])
        if "$" not in embed.description or "≈" not in embed.description:
            money = 0.0
            logger.debug("No money found, defaulting to 0")
        else:
            try:
                money = float(
                    embed.description.split("≈")[1]
                    .split(")")[0]
                    .strip()
                    .replace("$", "")
                    .replace(",", "")
                )
            except IndexError:
                logger.exception(
                    "Index error occurred during money splitting, skipping..."
                )
                return
        if money < configuration["IGNORE_DROPS_UNDER"] or money < configuration[droptype]["IGNORE_DROP_UNDER"]:
            logger.info(
                f"Ignored drop for {embed.description.split('**')[1]} {embed.description.split('**')[2].split(')')[0].replace(' (', '')}"
            )
            return
        for threshold in configuration["IGNORE_THRESHOLDS"]:
            logger.debug(
                f"Checking threshold: {threshold['threshold']} with chance: {threshold['chance']}"
            )
            if money <= threshold["threshold"]:
                logger.debug(
                    f"Drop value {money} is less than or equal to threshold {threshold['threshold']}"
                )
                random_number = randint(0, 100)
                if random_number < threshold["chance"]:
                    logger.info(
                        f"Ignored drop from failed threshold for {embed.description.split('**')[1]} {embed.description.split('**')[2].split(')')[0].replace(' (', '')}"
                    )
                    return
        for threshold in configuration[droptype]["IGNORE_THRESHOLDS"]:
            logger.debug(
                f"Checking threshold: {threshold['threshold']} with chance: {threshold['chance']}"
            )
            if money <= threshold["threshold"]:
                logger.debug(
                    f"Drop value {money} is less than or equal to threshold {threshold['threshold']}"
                )
                random_number = randint(0, 100)
                if random_number < threshold["chance"]:
                    logger.info(
                        f"Ignored drop from failed threshold for {embed.description.split('**')[1]} {embed.description.split('**')[2].split(')')[0].replace(' (', '')}"
                    )
                    return
        logger.debug(f"Money: {money}")
        logger.debug(f"Drop ends in: {embed.timestamp.timestamp() - time()}")
        drop_ends_in = embed.timestamp.timestamp() - time()
        if drop_ends_in < configuration["IGNORE_TIME_UNDER"] or drop_ends_in < configuration[droptype][
            "IGNORE_TIME_UNDER"]:
            logger.info(
                f"Ignored drop for {embed.description.split('**')[1]} {embed.description.split('**')[2].split(')')[0].replace(' (', '')}"
            )
            return
        if (configuration[droptype]["DELAY"] != [0, 0] or configuration[droptype]["SMART_DELAY"]["ENABLED"] or
                configuration[droptype]["RANGE_DELAY"]):
            if configuration[droptype]["SMART_DELAY"]["ENABLED"]:
                logger.debug("Smart delay enabled, waiting...")
                if drop_ends_in < 0:
                    logger.debug("Drop ended, skipping...")
                    return
                delay = drop_ends_in * uniform(
                    configuration[droptype]["SMART_DELAY"]["DELAY"][0],
                    configuration[droptype]["SMART_DELAY"]["DELAY"][1]
                )
                logger.debug(f"Delay: {round(delay, 2)}")
                await sleep(delay)
                logger.info(f"Waited {round(delay, 2)} seconds before proceeding.")
            elif configuration[droptype]["RANGE_DELAY"]:
                logger.debug("Range delay enabled, waiting...")
                delay = uniform(configuration[droptype]["DELAY"][0], configuration[droptype]["DELAY"][1])
                logger.debug(f"Delay: {delay}")
                await sleep(delay)
                logger.info(f"Waited {delay} seconds before proceeding.")
            elif configuration[droptype]["DELAY"] != [0, 0]:
                logger.debug(f"Manual delay enabled, waiting {configuration[droptype]['DELAY'][0]}...")
                await sleep(configuration[droptype]["DELAY"][0])
                logger.info(f"Waited {configuration[droptype]['DELAY'][0]} seconds before proceeding.")
        try:
            if "ended" in embed.footer.text.lower():
                logger.debug("Drop ended, skipping...")
                return
            elif droptype == "AIRDROP":
                logger.debug("Airdrop detected, entering...")
                try:
                    button = tip_cc_message.components[0].children[0]
                except IndexError:
                    logger.exception(
                        "Index error occurred, meaning the drop most likely ended, skipping..."
                    )
                    return
                if "Enter airdrop" in button.label:
                    await button.click()
                    logger.info(
                        f"Entered airdrop in {original_message.channel.name} for {embed.description.split('**')[1]} {embed.description.split('**')[2].split(')')[0].replace(' (', '')}"
                    )
                    await telegram(
                        f"💰 **Drop Entered**\nType: Airdrop\nServer: {original_message.guild.name}\nChannel: {original_message.channel.name}\nAmount: {money} USD")
                else:
                    logger.exception("Button label not found, skipping...")
                    return
            elif droptype == "PHRASEDROP":
                logger.debug("Phrasedrop detected, entering...")
                content = embed.description.replace("\n", "").replace("**", "")
                content = content.split("*")
                try:
                    content = content[1].replace("​", "").replace("\u200b", "").strip()
                except IndexError:
                    logger.exception("Index error occurred, skipping...")
                    return
                else:
                    logger.debug("Typing and sending message...")
                    length = len(content) / randint(configuration[droptype]["CPM"][0],
                                                    configuration[droptype]["CPM"][1]) * 60
                    async with original_message.channel.typing():
                        await sleep(length)
                    await original_message.channel.send(content)
                    logger.info(
                        f"Entered phrasedrop in {original_message.channel.name} for {embed.description.split('**')[1]} {embed.description.split('**')[2].split(')')[0].replace(' (', '')}"
                    )
                    await telegram(
                        f"💰 **Drop Entered**\nType: Phrasedrop\nServer: {original_message.guild.name}\nChannel: {original_message.channel.name}\nAmount: {money} USD")
            elif droptype == "REDPACKET":
                logger.debug("Redpacket detected, claiming...")
                try:
                    button = tip_cc_message.components[0].children[0]
                except IndexError:
                    logger.exception(
                        "Index error occurred, meaning the drop most likely ended, skipping..."
                    )
                    return
                if "envelope" in button.label:
                    await button.click()
                    logger.info(
                        f"Claimed envelope in {original_message.channel.name} for {embed.description.split('**')[1]} {embed.description.split('**')[2].split(')')[0].replace(' (', '')}"
                    )
                    await telegram(
                        f"💰 **Drop Entered**\nType: Redpacket/Envelope\nServer: {original_message.guild.name}\nChannel: {original_message.channel.name}\nAmount: {money} USD")
                else:
                    logger.exception("Button label not found, skipping...")
                    return
            elif droptype == "MATHDROP":
                logger.debug("Mathdrop detected, entering...")
                content = embed.description.replace("\n", "").replace("**", "")
                content = content.split("`")
                try:
                    content = content[1].replace("​", "").replace("\u200b", "")
                except IndexError:
                    logger.exception("Index error occurred, skipping...")
                    return
                else:
                    logger.debug("Evaluating math and sending message...")
                    answer = eval(content)
                    if isinstance(answer, float) and answer.is_integer():
                        answer = int(answer)
                    logger.debug(f"Answer: {answer}")
                    if not configuration[droptype]["SMART_DELAY"]["ENABLED"] and configuration[droptype]["DELAY"] == 0:
                        length = len(str(answer)) / randint(configuration[droptype]["CPM"][0],
                                                            configuration[droptype]["CPM"][1]) * 60
                        async with original_message.channel.typing():
                            await sleep(length)
                    await original_message.channel.send(answer)
                    logger.info(
                        f"Entered mathdrop in {original_message.channel.name} for {embed.description.split('**')[1]} {embed.description.split('**')[2].split(')')[0].replace(' (', '')}"
                    )
                    await telegram(
                        f"💰 **Drop Entered**\nType: Mathdrop\nServer: {original_message.guild.name}\nChannel: {original_message.channel.name}\nAmount: {money} USD")
            elif droptype == "TRIVIADROP":
                logger.debug("Triviadrop detected, entering...")
                category = embed.title.split("Trivia time - ")[1].strip()
                bot_question = embed.description.replace("**", "").split("*")[1]
                async with ClientSession() as session:
                    async with session.get(
                            f"https://raw.githubusercontent.com/QuartzWarrior/OTDB-Source/main/{quote(category)}.csv"
                    ) as resp:
                        lines = (await resp.text()).splitlines()
                        entered = False
                        for line in lines:
                            question, answer = line.split(",")
                            if bot_question.strip() == unquote(question).strip():
                                answer = unquote(answer).strip()
                                try:
                                    buttons = tip_cc_message.components[0].children
                                except IndexError:
                                    logger.exception(
                                        "Index error occurred, meaning the drop most likely ended, skipping..."
                                    )
                                    return
                                for button in buttons:
                                    if button.label.strip() == answer:
                                        entered = True
                                        await button.click()
                                        break
                                if not entered:
                                    logger.exception(
                                        "Answer not found in buttons, skipping..."
                                    )
                                    return
                                logger.info(
                                    f"Entered triviadrop in {original_message.channel.name} for {embed.description.split('**')[1]} {embed.description.split('**')[2].split(')')[0].replace(' (', '')}"
                                )
                                await telegram(
                                    f"💰 **Drop Entered**\nType: Triviadrop\nServer: {original_message.guild.name}\nChannel: {original_message.channel.name}\nAmount: {money} USD")
                                break
                        if not entered:
                            logger.exception("Question not found in database, skipping...")
                            return
            else:
                logger.debug(f"Drop type non existent?!, skipping...\n{embed.title}")
                return
            if configuration[droptype]["SEND_MESSAGE"]:
                if randint(0, 100) < configuration[droptype]["MESSAGE_CHANCE"] * 100:
                    logger.debug("Not sending message...")
                    return
                logger.debug("Sending message...")
                message = configuration[droptype]["MESSAGES"][
                    randint(0, len(configuration[droptype]["MESSAGES"]) - 1)
                ]
                length = len(message) / randint(configuration["PHRASEDROP"]["CPM"][0],
                                                configuration["PHRASEDROP"]["CPM"][1]) * 60
                async with original_message.channel.typing():
                    await sleep(length)
                await original_message.channel.send(message)
                logger.info(f"Sent message: {message}")
            return

        except AttributeError:
            logger.exception("Attribute error occurred")
            return
        except HTTPException:
            logger.exception("HTTP exception occurred")
            return
        except NotFound:
            logger.exception("Not found exception occurred")
            return
    elif original_message.content.startswith(
            ("$airdrop", "$triviadrop", "$mathdrop", "$phrasedrop", "$redpacket")
    ) and any(word in original_message.content.lower() for word in banned_words):
        logger.info(
            f"Banned word detected in {original_message.channel.name}, skipping..."
        )
    elif original_message.content.startswith(
            ("$airdrop", "$triviadrop", "$mathdrop", "$phrasedrop", "$redpacket")
    ) and (
            config["WHITELIST_ON"] and original_message.guild.id not in config["WHITELIST"]
    ):
        logger.info(
            f"Whitelist enabled and drop not in whitelist, skipping {original_message.channel.name}..."
        )
    elif original_message.content.startswith(
            ("$airdrop", "$triviadrop", "$mathdrop", "$phrasedrop", "$redpacket")
    ) and (config["BLACKLIST_ON"] and original_message.guild.id in config["BLACKLIST"]):
        logger.info(
            f"Blacklist enabled and drop in blacklist, skipping {original_message.channel.name}..."
        )
    elif original_message.content.startswith(
            ("$airdrop", "$triviadrop", "$mathdrop", "$phrasedrop", "$redpacket")
    ) and (
            configuration["CHANNEL_BLACKLIST_ON"]
            and original_message.channel.id in configuration["CHANNEL_BLACKLIST"]
    ):
        logger.info(
            f"Channel blacklist enabled and drop in channel blacklist, skipping {original_message.channel.name}..."
        )
    elif (
            original_message.content.startswith(
                ("$airdrop", "$triviadrop", "$mathdrop", "$phrasedrop", "$redpacket")
            )
            and original_message.author.id in configuration["IGNORE_USERS"]
    ):
        logger.info(
            f"User in ignore list detected in {original_message.channel.name}, skipping..."
        )
    else:
        return


if __name__ == "__main__":
    try:
        client.run(config["TOKEN"], log_handler=handler, log_formatter=formatter)
    except LoginFailure:
        logger.critical("Invalid token, restart the program.")
        config["TOKEN"] = ""
        with open("config.json", "w") as f:
            dump(config, f, indent=4)
