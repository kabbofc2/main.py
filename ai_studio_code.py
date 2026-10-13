import asyncio
import io
import re
import json
import html
import os
import httpx
import random
import string
import time
import struct
import hmac
import hashlib
import base64
from datetime import datetime, timedelta
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler

# Premium copy button (PTB 21+)
try:
    from telegram import CopyTextButton
    HAS_COPY_BTN = True
except ImportError:
    HAS_COPY_BTN = False

# ==================== CONFIG SECTION ====================

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
YESMS_AUTHKEY = os.getenv("YESMS_AUTHKEY", "").strip()

USER_DATA_FILE = "users.json"
PAID_SMS_FILE = "paid_sms.json"
STATS_FILE = "user_stats.json"
REFERRAL_DATA_FILE = "referral_data.json"
BANNED_USERS_FILE = "banned_users.json"
WITHDRAW_DATA_FILE = "withdraw_requests.json"
ACTIVITY_LOGS_FILE = "activity_logs.json"
DATA_RANGE_FILE = "datarange.json"
SETTINGS_FILE = "settings.json"
CONSOLE_SENT_FILE = "console_sent.json"

BOT_USERNAME = None  # set at runtime via post_init

# ==================== MULTIPLE ADMINS CONFIGURATION ====================
ADMINS = [7856511206]

OTP_GROUP_ID = -1004427550892

# ==================== PREMIUM EMOJI MAPPING ====================

EMOJI_ID_MAP = {
    "telegram": "5271801931814165886", "instagram": "5269682734820777950",
    "facebook": "5269427536453984598", "tiktok": "5271527792641595125",
    "x": "5269500885905468781",        "whatsapp": "5271536803482981220",
    "up": "5244837092042750681",        "down": "5246762912428603768",
    "add": "5397916757333654639",       "setting": "5341715473882955310",
    "1st": "5440539497383087970",       "2st": "5447203607294265305",
    "3rd": "5453902265922376865",       "free": "5406756500108501710",
    "msg": "5253742260054409879",       "link": "5271604874419647061",
    "status": "5231200819986047254",    "home": "5416041192905265756",
    "gift_box": "5970074171449808121",  "delete": "5422557736330106570",
    "number_change": "5267295703666824255", "refer_btn": "5420396762189831222",
    "get_number_btn": "5375338737028841420", "cross": "5420130255174145507",
    "stop": "5956074558044770726",      "ban": "5420323339723881652",
    "loading": "5386367538735104399",   "profile": "5352861489541714456",
    "done": "6298670698948724690",      "otp_success": "5190781475468915802",
    "nagad": "5352985330628730418",     "bkash": "5348469219761626211",
    "rocket": "5346042941196507141",    "binance": "5348212415077064131",
    "live": "5355102594886833928",      "developer": "5267294466716244344",
    "channel": "6215074610845585917",   "copy": "5429483843541284898",
    "admin": "5350396951407895212",     "waiting": "6217721388736712699",
    "back": "5267490665117275176",      "leader_board": "5280769763398671636",
    "money": "6233367447789899509",     "discord": "5807892405306791778",
    "custom_range": "5231012545799666522", "paypal": "5107533253946901363",
    "imo": "5337155807752524558",       "hi": "5353027129250453493",
    "off": "5352974971167611327",       "diamond": "5251562950698759162",
    "broadcast": "5251671501702196837", "key": "5296369303661067030",
    "bot_logo": "4943094697238201446",  "tk": "5201873447554145566",
    "roket": "5188481279963715781",     "all_done": "5859265295113261399",
    "yes": "5875017993909440887",       "no": "5875005555684152921",
    "fire_love": "5864093929275658617",
}

FALLBACK_EMOJI_MAP = {
    "telegram": "\u2708\ufe0f", "instagram": "\U0001f4f7", "facebook": "\U0001f535",
    "tiktok": "\U0001f3b5", "x": "\u274c", "whatsapp": "\U0001f4ac",
    "up": "\U0001f4c8", "down": "\U0001f4c9", "add": "\u2795", "setting": "\u2699\ufe0f",
    "1st": "\U0001f947", "2st": "\U0001f948", "3rd": "\U0001f949", "free": "\U0001f193",
    "msg": "\U0001f4ac", "link": "\U0001f517", "status": "\U0001f4ca", "home": "\U0001f3e0",
    "gift_box": "\U0001f381", "delete": "\U0001f5d1\ufe0f", "number_change": "\U0001f504",
    "get_number_btn": "\U0001f4de", "cross": "\u274c", "stop": "\U0001f6d1",
    "ban": "\U0001f6ab", "loading": "\u23f3", "profile": "\U0001f464", "done": "\u2705",
    "otp_success": "\u2b50", "nagad": "\U0001f7e0", "bkash": "\U0001f496",
    "rocket": "\U0001f680", "binance": "\U0001f7e1", "live": "\U0001f7e2",
    "developer": "\U0001f468\u200d\U0001f4bb", "channel": "\U0001f4e2",
    "copy": "\U0001f4cb", "admin": "\U0001f451", "waiting": "\u23f3", "back": "\U0001f519",
    "leader_board": "\U0001f3c6", "custom_range": "\U0001f3af", "refer_btn": "\U0001f517",
    "paypal": "\U0001f4b3", "imo": "\U0001f4ac", "hi": "\U0001f44b", "off": "\U0001f6d1",
    "diamond": "\U0001f48e", "broadcast": "\U0001f4e2", "key": "\U0001f511", "tk": "\u09f3",
    "roket": "\U0001f680", "all_done": "\u2705", "yes": "\u2714\ufe0f", "no": "\u274c",
    "fire_love": "\u2764\ufe0f",
}

PREMIUM_FLAGS = {
    "\U0001f1fa\U0001f1f8": "5913463998522592692",
    "\U0001f1fa\U0001f1e6": "5911406692007941050",
    "\U0001f1f5\U0001f1f1": "5913550391789752571",
    "\U0001f1f0\U0001f1ff": "5913724621433082323",
    "\U0001f1e6\U0001f1ff": "5911197578640233518",
    "\U0001f1ea\U0001f1fa": "5911106310585193018",
    "\U0001f1e6\U0001f1f2": "5913272455866093666",
    "\U0001f1f7\U0001f1fa": "5913274246867456342",
    "\U0001f1fa\U0001f1ff": "5911051846104912282",
    "\U0001f1e9\U0001f1ea": "5911096835887337583",
    "\U0001f1ef\U0001f1f5": "5913293711659241040",
    "\U0001f1f9\U0001f1f7": "5910995113881901195",
    "\U0001f1e7\U0001f1fe": "5911011185649521599",
    "\U0001f1ec\U0001f1e7": "5913443365499703513",
    "\U0001f1ee\U0001f1f3": "5913754823643107921",
    "\U0001f1e7\U0001f1f7": "5911148568768418614",
    "\U0001f1fe\U0001f1ea": "5913346492512341993",
    "\U0001f1fb\U0001f1f3": "5913428887164949581",
    "\U0001f1e6\U0001f1ea": "5913726554168365343",
    "\U0001f1fa\U0001f1ec": "5913488939397681980",
    "\U0001f1f9\U0001f1f2": "5913315521503170180",
    "\U0001f1f9\U0001f1f3": "5911332947419468671",
    "\U0001f1f9\U0001f1ed": "5913617968805187987",
    "\U0001f1f9\U0001f1ff": "5911418949844603556",
    "\U0001f1f8\U0001f1ea": "5911156510162949403",
    "\U0001f1f8\U0001f1e9": "5911387497799094470",
    "\U0001f1ea\U0001f1f8": "5911193287967904547",
    "\U0001f1f1\U0001f1f0": "5911293163137406640",
    "\U0001f1ff\U0001f1e6": "5911203119148044594",
    "\U0001f1f8\U0001f1ec": "5911531460808051849",
    "\U0001f1f7\U0001f1f8": "5913592598433369871",
    "\U0001f1f8\U0001f1f3": "5910995302860461643",
    "\U0001f1f6\U0001f1e6": "5911260864983339619",
    "\U0001f1f5\U0001f1f9": "5911023653939581472",
    "\U0001f1f5\U0001f1ed": "5911268638874145162",
    "\U0001f1f5\U0001f1ea": "5911207993935925780",
    "\U0001f1f5\U0001f1f0": "5913705895375672082",
    "\U0001f1f4\U0001f1f2": "5913570801474343473",
    "\U0001f1f3\U0001f1f4": "5913617397574537046",
    "\U0001f1f3\U0001f1ec": "5911143844304393105",
    "\U0001f1f3\U0001f1ff": "5913640044937089340",
    "\U0001f1f3\U0001f1f1": "5913367645226275100",
    "\U0001f1f3\U0001f1f5": "5913496520014958723",
    "\U0001f1f2\U0001f1e6": "5911482111633658301",
    "\U0001f1f2\U0001f1f3": "5911041383564580038",
    "\U0001f1f2\U0001f1e9": "5913456847402045950",
    "\U0001f1f2\U0001f1fd": "5913687302462246518",
    "\U0001f1f2\U0001f1fe": "5913654360063087453",
    "\U0001f1f0\U0001f1ea": "5911154710571651231",
    "\U0001f1f1\U0001f1f9": "5911172315642597775",
    "\U0001f1f1\U0001f1fb": "5913738489882480243",
    "\U0001f1f1\U0001f1e7": "5911504273664905447",
    "\U0001f1ee\U0001f1e9": "5913479361620611038",
    "\U0001f1ee\U0001f1f7": "5911308891307643032",
    "\U0001f1ee\U0001f1f6": "5911382442622587735",
    "\U0001f1ee\U0001f1f1": "5911471936856134692",
    "\U0001f1ee\U0001f1f9": "5913688444923547525",
    "\U0001f1ed\U0001f1fa": "5913767635530551104",
    "\U0001f1ec\U0001f1f7": "5911210399117611448",
    "\U0001f1ec\U0001f1ed": "5913391155877252952",
    "\U0001f1ec\U0001f1ea": "5913434771270144023",
    "\U0001f1eb\U0001f1f7": "5913605586414473124",
    "\U0001f1eb\U0001f1ee": "5911041344909873378",
    "\U0001f1ea\U0001f1f9": "5911078333168227043",
    "\U0001f1ea\U0001f1ec": "5913694831539916769",
    "\U0001f1e9\U0001f1f0": "5911206009661034712",
    "\U0001f1e8\U0001f1fe": "5911023550860366409",
    "\U0001f1ed\U0001f1f7": "5913692684056269311",
    "\U0001f1e8\U0001f1f3": "5913779335021466780",
    "\U0001f1e7\U0001f1e9": "5911365056594973179",
    "\U0001f1e7\U0001f1ea": "5913529642802745141",
    "\U0001f1e6\U0001f1fa": "5913632326880858455",
    "\U0001f1e6\U0001f1f9": "5911338831524664592",
    "\U0001f1e6\U0001f1f7": "5913573356979884082",
    "\U0001f1f0\U0001f1f7": "5913371673905598425",
    "\U0001f1f8\U0001f1e6": "4985897134424328239",
    "\U0001f1e8\U0001f1f4": "5913773060074246009",
    "\U0001f1e8\U0001f1f1": "5911470957603592832",
    "\U0001f1ff\U0001f1f2": "5913564754160389778",
}

def get_tg_emoji(key, default_char=""):
    custom = load_settings().get("custom_emojis", {}).get(key)
    if custom:
        cid = custom.get("id", "")
        cfb = custom.get("fallback", "") or default_char or FALLBACK_EMOJI_MAP.get(key, "\u2b50")
        if cid:
            return f'<tg-emoji emoji-id="{cid}">{cfb}</tg-emoji>'
        return cfb
    emoji_id = EMOJI_ID_MAP.get(key)
    fallback = default_char or FALLBACK_EMOJI_MAP.get(key, "\u2b50")
    if emoji_id:
        return f'<tg-emoji emoji-id="{emoji_id}">{fallback}</tg-emoji>'
    return fallback

def get_country_tg_flag(flag_emoji):
    emoji_id = PREMIUM_FLAGS.get(flag_emoji)
    if emoji_id:
        return f'<tg-emoji emoji-id="{emoji_id}">{flag_emoji}</tg-emoji>'
    return f'<tg-emoji emoji-id="5911106310585193018">{flag_emoji}</tg-emoji>'

# ==================== SYSTEM DYNAMIC SETTINGS ====================

_settings_cache = None

def load_settings():
    global _settings_cache
    if _settings_cache is not None:
        return _settings_cache
    default = {
        "active_panel": "zenex",
        "yesms_api_key": "",
        "zenex_base_url": "https://yesms.online",
        "panel_url": "https://t.me/Nextsmsbdbot",
        "allowed_services": ["Instagram","Facebook","WhatsApp","TikTok","Telegram","Discord","PayPal","Imo"],
        "otp_group_url": "https://t.me/zenoxaaotp",
        "channel_url": "https://t.me/kabbofc",
        "support_username": "@support",
        "maintenance_mode": False,
        "cooldown_time": 1.0,
        "min_withdraw": 50.0,
        "otp_bonus": 0.20,
        "referral_bonus": 0.0,
        "admins": [8346777366],
        "owners": [8346777366],
        "otp_group_chat_id": None,
        "force_join_channel": None,
        "force_join_channels": [],
        "manual_services": [],
        "live_console": False,
        "live_console_interval": 120,
        "live_console_delay": 2.0,
        "live_console_limit": 30,
    }
    if not os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "w") as f:
            json.dump(default, f, indent=4)
        _settings_cache = default
        return default
    try:
        with open(SETTINGS_FILE, "r") as f:
            data = json.load(f)
        updated = False
        for k, v in default.items():
            if k not in data:
                data[k] = v; updated = True
        if data.get("force_join_channel") and not data.get("force_join_channels"):
            data["force_join_channels"] = [data["force_join_channel"]]
            data["force_join_channel"] = None
            updated = True
        if updated:
            with open(SETTINGS_FILE, "w") as f:
                json.dump(data, f, indent=4)
        _settings_cache = data
        return data
    except Exception:
        _settings_cache = default
        return default

def save_settings(settings):
    global _settings_cache
    _settings_cache = settings
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)

def clean_base_url(url):
    url = str(url).strip().rstrip('/')
    url = re.sub(r'(/v1|/api|/api/v1)$', '', url)
    return url.rstrip('/')

def get_api_credentials():
    s = load_settings()
    api_key = s.get("yesms_api_key") or YESMS_AUTHKEY
    base_url = s.get("zenex_base_url") or "https://yesms.online"
    return api_key, base_url

def get_api_urls(base_url):
    base = "https://yesms.online"
    return {"getnum": f"{base}/api/allocate_number",
            "liveaccess": f"{base}/api/live_access_data",
            "otp": f"{base}/api/user_numbers",
            "console": f"{base}/api/console_data"}

def get_api_headers(api_key):
    return {"authkey": api_key, "Content-Type": "application/json"}

# ==================== WELCOME MESSAGE CONFIGURATION ====================
WELCOME_MESSAGE = """✨ আসসালামু আলাইকুম ✨

স্বাগত এবং ধন্যবাদ আপনারকে...

🌟 Premium Features Available!"""

# ==================== OTP RATE CONFIGURATION ====================
OTP_RATE = 0.20

# ==================== REFERRAL / WITHDRAW CONFIGURATION ====================
REFERRAL_PRICE = 0
MIN_WITHDRAW = 50
MAX_WITHDRAW = 10000

# ==================== SUPPORT & DEVELOPER LINKS ====================
SUPPORT_LINK = "https://t.me/DEM_Support_Chat"
DEVELOPER_LINK = "https://t.me/Davil_Raju"

request_queue = asyncio.Queue()
MAX_WORKERS = 5000

client_async = httpx.AsyncClient(
    http2=True,
    timeout=httpx.Timeout(4.0, connect=0.8, read=3.2),
    limits=httpx.Limits(max_connections=5000, max_keepalive_connections=2500),
    trust_env=False,
)

active_numbers = {}
last_range = {}
CHECK_INTERVAL = 2.0

# ==================== ZENEXA RANGES CACHE ====================
_ranges_cache = {"data": None, "updated_at": 0.0, "fetching": False}

def get_app_emoji_id(app_name):
    n = app_name.lower()
    SERVICE_EMOJI_MAP = [
        ("whatsapp business", "5336814486701514414"),
        ("whatsapp",          "5334759662677957452"),
        ("telegram",          "5337010556253543833"),
        ("facebook",          "5334807341109908955"),
        ("instagram",         "5334868205091459431"),
        ("amazon prime",      "6111801057061374810"),
        ("amazon",            "4995019580536524226"),
        ("imo",               "5337155807752524558"),
        ("apple",             "5334637951894722661"),
        ("google",            "5335010201005231986"),
        ("microsoft",         "5334880948259427772"),
        ("teams",             "5334590977837403844"),
        ("tiktok",            "5339213256001102461"),
        ("bkash",             "5348469219761626211"),
        ("bybit",             "5348372939479751825"),
        ("binance",           "5348212415077064131"),
        ("melbet",            "5337102391244263212"),
        ("snapchat",          "5359441366554255082"),
        ("uber",              "5298715455316303708"),
        ("paypal",            "5776103539872896061"),
        ("discord",           "5116246243646898866"),
        ("viber",             "5463060437572528782"),
        ("linkedin",          "6224222994265279792"),
        ("line",              "5399818044866327279"),
        ("wechat",            "5782757599560602950"),
        ("twitter",           "5215726959056662534"),
        ("reddit",            "4992421103847604984"),
        ("pinterest",         "5346103513120258857"),
        ("twitch",            "5233333563306301418"),
        ("zoom",              "5881799193219043268"),
        ("signal",            "5293998404404272267"),
        ("slack",             "4994972469040251302"),
        ("skype",             "4992613535562334989"),
        ("netflix",           "6255738712664050133"),
        ("spotify",           "5411392711146095115"),
        ("hoichoi",           "6104822598493801746"),
        ("daraz",             "5336879280578138635"),
        ("foodpanda",         "5336879280578138635"),
        ("pathao",            "5336879280578138635"),
        ("aliexpress",        "5336879280578138635"),
        ("shopee",            "5336879280578138635"),
        ("payoneer",          "5336879280578138635"),
        ("wise",              "5336879280578138635"),
        ("chatgpt",           "5296516998996445955"),
        ("notion",            "5336879280578138635"),
        ("github",            "5417836094098007862"),
        ("canva",             "5111661409008092227"),
        ("figma",             "5336879280578138635"),
        ("upwork",            "5336879280578138635"),
        ("fiverr",            "5336879280578138635"),
        ("yahoo",             "5336879280578138635"),
        ("dropbox",           "5336879280578138635"),
        ("coursera",          "5336879280578138635"),
        ("duolingo",          "5336879280578138635"),
        ("rocket",            "5346042941196507141"),
    ]
    for k, v in SERVICE_EMOJI_MAP:
        if k in n:
            return v
    return "5861680977994060034"

def get_platform_icon(platform_name):
    return f'<tg-emoji emoji-id="{get_app_emoji_id(platform_name)}">📞</tg-emoji>'

def get_clean_app_name(raw):
    n = raw.lower().strip()
    for k, v in [("facebook","Facebook"),("instagram","Instagram"),("whatsapp","WhatsApp"),
                  ("tiktok","TikTok"),("paypal","PayPal"),("telegram","Telegram"),
                  ("discord","Discord"),("imo","Imo"),("hsbc","HSBC")]:
        if k in n: return v
    return raw.strip().capitalize()

def make_bold_text(text):
    out = []
    for ch in str(text):
        o = ord(ch)
        if 65 <= o <= 90:    out.append(chr(o - 65 + 0x1D5D4))
        elif 97 <= o <= 122: out.append(chr(o - 97 + 0x1D5EE))
        elif 48 <= o <= 57:  out.append(chr(o - 48 + 0x1D7EC))
        else: out.append(ch)
    return "".join(out)

async def fetch_top55_ranges_by_app():
    api_key, base_url = get_api_credentials()
    urls = get_api_urls(base_url)
    headers = get_api_headers(api_key)
    top = None
    for attempt in range(2):
        try:
            r = await client_async.get(urls["liveaccess"], headers=headers,
                                        timeout=httpx.Timeout(5.0, connect=1.5))
            data = r.json()
            if isinstance(data, dict) and "ranges" in data:
                top = {}
                for svc_name, rng_list in data["ranges"].items():
                    clean = get_clean_app_name(svc_name)
                    if clean not in top: top[clean] = {"icon": get_platform_icon(clean), "ranges": []}
                    for rng_label in (rng_list if isinstance(rng_list, list) else []):
                        parts = str(rng_label).split("|")
                        range_id = parts[-1].strip() if parts else str(rng_label).strip()
                        top[clean]["ranges"].append(range_id)
                break
        except Exception:
            if attempt == 0: await asyncio.sleep(0.2)
    if top is None: return None, "Server unreachable or invalid API key."
    if not top:     return {}, None
    return dict(sorted(top.items(), key=lambda x: len(x[1]["ranges"]), reverse=True)), None

def build_app_buttons_from_cache(top):
    btns = []
    for app_name in list(top.keys())[:5]:
        btns.append([InlineKeyboardButton(make_bold_text(app_name),
            callback_data=f"sel_app_{app_name}",
            api_kwargs={"icon_custom_emoji_id": get_app_emoji_id(app_name), "style": "success"})])
    return btns

async def _bg_refresh_ranges():
    global _ranges_cache
    while True:
        try:
            if not _ranges_cache["fetching"]:
                _ranges_cache["fetching"] = True
                try:
                    data, _ = await fetch_top55_ranges_by_app()
                    if data:
                        _ranges_cache["data"] = data
                        _ranges_cache["updated_at"] = time.monotonic()
                except Exception: pass
                finally: _ranges_cache["fetching"] = False
        except Exception: pass
        await asyncio.sleep(200)

# ==================== CHECK IF USER IS ADMIN ====================

def is_admin(user_id):
    s = load_settings()
    return user_id in s.get("admins", ADMINS) or user_id in ADMINS

# ==================== WITHDRAW DATA FUNCTIONS ====================

def load_withdraw_requests():
    if not os.path.exists(WITHDRAW_DATA_FILE):
        with open(WITHDRAW_DATA_FILE, "w") as f:
            json.dump({}, f)
        return {}
    try:
        with open(WITHDRAW_DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_withdraw_requests(data):
    with open(WITHDRAW_DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def generate_payment_id():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))

# ==================== BANNED USERS FUNCTIONS ====================

def load_banned_users():
    if not os.path.exists(BANNED_USERS_FILE):
        with open(BANNED_USERS_FILE, "w") as f:
            json.dump([], f)
        return []
    try:
        with open(BANNED_USERS_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_banned_users(banned_list):
    with open(BANNED_USERS_FILE, "w") as f:
        json.dump(banned_list, f, indent=4)

def is_user_banned(uid):
    banned_list = load_banned_users()
    return str(uid) in banned_list

def ban_user(uid):
    banned_list = load_banned_users()
    uid_str = str(uid)
    if uid_str not in banned_list:
        banned_list.append(uid_str)
        save_banned_users(banned_list)
        return True
    return False

def unban_user(uid):
    banned_list = load_banned_users()
    uid_str = str(uid)
    if uid_str in banned_list:
        banned_list.remove(uid_str)
        save_banned_users(banned_list)
        return True
    return False

# ==================== REFERRAL DATA FUNCTIONS ====================

def load_referral_data():
    if not os.path.exists(REFERRAL_DATA_FILE):
        with open(REFERRAL_DATA_FILE, "w") as f:
            json.dump({}, f)
        return {}
    try:
        with open(REFERRAL_DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_referral_data(data):
    with open(REFERRAL_DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def update_referral_count(uid, count):
    referral_data = load_referral_data()
    uid_str = str(uid)
    if uid_str not in referral_data:
        referral_data[uid_str] = {"referral_count": 0}
    referral_data[uid_str]["referral_count"] = count
    save_referral_data(referral_data)

def get_referral_count(uid):
    referral_data = load_referral_data()
    uid_str = str(uid)
    return referral_data.get(uid_str, {}).get("referral_count", 0)

# ==================== DATA RANGE FILE ====================

def load_range_db():
    if not os.path.exists(DATA_RANGE_FILE):
        return {}
    try:
        with open(DATA_RANGE_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_range_db(data):
    with open(DATA_RANGE_FILE, "w") as f:
        json.dump(data, f, indent=4)

def save_number_range_info(uid, number, range_text):
    db = load_range_db()
    flag, name = get_country_info(number)
    db[normalize_number(number)] = {
        "user_id": str(uid),
        "number": f"+{normalize_number(number)}",
        "range": range_text,
        "country": f"{flag} {name}"
    }
    save_range_db(db)

# ==================== COUNTRY MAPPING SECTION ====================

def get_country_info(number):
    number = str(number).strip()

    country_map = {
        "2376": ("🇨🇲", "Cameroon"), "2250": ("🇨🇮", "Ivory Coast"), "2613": ("🇲🇬", "Madagascar"),
        "4077": ("🇷🇴", "Romania"),   "237": ("🇨🇲", "Cameroon"),     "225": ("🇨🇮", "Ivory Coast"),
        "261": ("🇲🇬", "Madagascar"), "20": ("🇪🇬", "Egypt"),         "27": ("🇿🇦", "South Africa"),
        "234": ("🇳🇬", "Nigeria"),    "254": ("🇰🇪", "Kenya"),         "233": ("🇬🇭", "Ghana"),
        "212": ("🇲🇦", "Morocco"),    "213": ("🇩🇿", "Algeria"),       "216": ("🇹🇳", "Tunisia"),
        "218": ("🇱🇾", "Libya"),      "249": ("🇸🇩", "Sudan"),         "251": ("🇪🇹", "Ethiopia"),
        "252": ("🇸🇴", "Somalia"),    "253": ("🇩🇯", "Djibouti"),      "255": ("🇹🇿", "Tanzania"),
        "256": ("🇺🇬", "Uganda"),     "257": ("🇧🇮", "Burundi"),       "258": ("🇲🇿", "Mozambique"),
        "260": ("🇿🇲", "Zambia"),     "263": ("🇿🇼", "Zimbabwe"),      "264": ("🇳🇦", "Namibia"),
        "265": ("🇲🇼", "Malawi"),     "266": ("🇱🇸", "Lesotho"),       "267": ("🇧🇼", "Botswana"),
        "268": ("🇸🇿", "Swaziland"),  "269": ("🇰🇲", "Comoros"),       "220": ("🇬🇲", "Gambia"),
        "221": ("🇸🇳", "Senegal"),    "222": ("🇲🇷", "Mauritania"),    "223": ("🇲🇱", "Mali"),
        "224": ("🇬🇳", "Guinea"),     "226": ("🇧🇫", "Burkina Faso"),  "227": ("🇳🇪", "Niger"),
        "228": ("🇹🇬", "Togo"),       "229": ("🇧🇯", "Benin"),         "230": ("🇲🇺", "Mauritius"),
        "231": ("🇱🇷", "Liberia"),    "232": ("🇸🇱", "Sierra Leone"),  "235": ("🇹🇩", "Chad"),
        "236": ("🇨🇫", "Central African Republic"), "238": ("🇨🇻", "Cape Verde"),
        "239": ("🇸🇹", "Sao Tome and Principe"), "240": ("🇬🇶", "Equatorial Guinea"),
        "241": ("🇬🇦", "Gabon"),      "242": ("🇨🇬", "Congo"),         "243": ("🇨🇩", "DR Congo"),
        "244": ("🇦🇴", "Angola"),     "245": ("🇬🇼", "Guinea-Bissau"), "247": ("🇸🇭", "Saint Helena"),
        "248": ("🇸🇨", "Seychelles"), "250": ("🇷🇼", "Rwanda"),        "290": ("🇸🇭", "Saint Helena"),
        "291": ("🇪🇷", "Eritrea"),    "40": ("🇷🇴", "Romania"),        "44": ("🇬🇧", "United Kingdom"),
        "33": ("🇫🇷", "France"),      "49": ("🇩🇪", "Germany"),       "39": ("🇮🇹", "Italy"),
        "34": ("🇪🇸", "Spain"),        "31": ("🇳🇱", "Netherlands"),   "32": ("🇧🇪", "Belgium"),
        "41": ("🇨🇭", "Switzerland"), "43": ("🇦🇹", "Austria"),       "46": ("🇸🇪", "Sweden"),
        "47": ("🇳🇴", "Norway"),      "45": ("🇩🇰", "Denmark"),       "358": ("🇫🇮", "Finland"),
        "351": ("🇵🇹", "Portugal"),   "353": ("🇮🇪", "Ireland"),       "36": ("🇭🇺", "Hungary"),
        "48": ("🇵🇱", "Poland"),      "380": ("🇺🇦", "Ukraine"),       "370": ("🇱🇹", "Lithuania"),
        "371": ("🇱🇻", "Latvia"),     "372": ("🇪🇪", "Estonia"),       "373": ("🇲🇩", "Moldova"),
        "374": ("🇦🇲", "Armenia"),    "375": ("🇧🇾", "Belarus"),       "376": ("🇦🇩", "Andorra"),
        "377": ("🇲🇨", "Monaco"),     "381": ("🇷🇸", "Serbia"),        "382": ("🇲🇪", "Montenegro"),
        "385": ("🇭🇷", "Croatia"),    "386": ("🇸🇮", "Slovenia"),      "387": ("🇧🇦", "Bosnia and Herzegovina"),
        "389": ("🇲🇰", "North Macedonia"), "350": ("🇬🇮", "Gibraltar"), "352": ("🇱🇺", "Luxembourg"),
        "354": ("🇮🇸", "Iceland"),    "355": ("🇦🇱", "Albania"),       "356": ("🇲🇹", "Malta"),
        "357": ("🇨🇾", "Cyprus"),     "359": ("🇧🇬", "Bulgaria"),      "421": ("🇸🇰", "Slovakia"),
        "420": ("🇨🇿", "Czech Republic"), "298": ("🇫🇴", "Faroe Islands"), "299": ("🇬🇱", "Greenland"),
        "1": ("🇺🇸", "United States"), "7": ("🇷🇺", "Russia"),        "91": ("🇮🇳", "India"),
        "92": ("🇵🇰", "Pakistan"),    "880": ("🇧🇩", "Bangladesh"),   "86": ("🇨🇳", "China"),
        "81": ("🇯🇵", "Japan"),       "82": ("🇰🇷", "South Korea"),   "84": ("🇻🇳", "Vietnam"),
        "66": ("🇹🇭", "Thailand"),    "62": ("🇮🇩", "Indonesia"),     "60": ("🇲🇾", "Malaysia"),
        "65": ("🇸🇬", "Singapore"),   "63": ("🇵🇭", "Philippines"),   "95": ("🇲🇲", "Myanmar"),
        "94": ("🇱🇰", "Sri Lanka"),   "977": ("🇳🇵", "Nepal"),         "93": ("🇦🇫", "Afghanistan"),
        "98": ("🇮🇷", "Iran"),        "90": ("🇹🇷", "Turkey"),        "964": ("🇮🇶", "Iraq"),
        "963": ("🇸🇾", "Syria"),      "961": ("🇱🇧", "Lebanon"),       "962": ("🇯🇴", "Jordan"),
        "965": ("🇰🇼", "Kuwait"),     "966": ("🇸🇦", "Saudi Arabia"), "967": ("🇾🇲", "Yemen"),
        "968": ("🇴🇲", "Oman"),       "971": ("🇦🇪", "United Arab Emirates"), "972": ("🇮🇱", "Israel"),
        "973": ("🇧🇭", "Bahrain"),    "974": ("🇶🇦", "Qatar"),         "994": ("🇦🇿", "Azerbaijan"),
        "995": ("🇬🇪", "Georgia"),    "996": ("🇰🇬", "Kyrgyzstan"),    "992": ("🇹🇯", "Tajikistan"),
        "993": ("🇹🇲", "Turkmenistan"), "998": ("🇺🇿", "Uzbekistan"),  "855": ("🇰🇭", "Cambodia"),
        "856": ("🇱🇦", "Laos"),       "976": ("🇲🇳", "Mongolia"),      "850": ("🇰🇵", "North Korea"),
        "55": ("🇧🇷", "Brazil"),      "52": ("🇲🇽", "Mexico"),         "54": ("🇦🇷", "Argentina"),
        "57": ("🇨🇴", "Colombia"),    "51": ("🇵🇪", "Peru"),           "58": ("🇻🇪", "Venezuela"),
        "56": ("🇨🇱", "Chile"),       "593": ("🇪🇨", "Ecuador"),       "591": ("🇧🇴", "Bolivia"),
        "595": ("🇵🇾", "Paraguay"),   "598": ("🇺🇾", "Uruguay"),       "502": ("🇬🇹", "Guatemala"),
        "503": ("🇸🇻", "El Salvador"), "504": ("🇭🇳", "Honduras"),     "506": ("🇨🇷", "Costa Rica"),
        "507": ("🇵🇦", "Panama"),     "509": ("🇭🇹", "Haiti"),         "501": ("🇧🇿", "Belize"),
        "61": ("🇦🇺", "Australia"),   "64": ("🇳🇿", "New Zealand"),    "675": ("🇵🇬", "Papua New Guinea"),
        "679": ("🇫🇯", "Fiji"),       "1246": ("🇧🇧", "Barbados"),     "1876": ("🇯🇲", "Jamaica"),
        "53": ("🇨🇺", "Cuba"),        "592": ("🇬🇾", "Guyana"),
    }

    clean_num = str(number).replace('+', '').replace(' ', '').replace('-', '').strip()
    sorted_prefixes = sorted(country_map.keys(), key=len, reverse=True)

    for prefix in sorted_prefixes:
        if clean_num.startswith(prefix):
            return country_map[prefix]

    return ("🌍", "Unknown")

# ==================== SERVICE DETECTION SECTION ====================

def detect_service(full_sms):
    if not full_sms:
        return "SMS SERVICE"

    sms_lower = full_sms.lower()

    service_keywords = {
        "facebook": "FACEBOOK", "fb": "FACEBOOK",
        "instagram": "INSTAGRAM", "insta": "INSTAGRAM",
        "tiktok": "TIKTOK",
        "twitter": "TWITTER", "x.com": "TWITTER",
        "snapchat": "SNAPCHAT", "snap": "SNAPCHAT",
        "whatsapp": "WHATSAPP",
        "telegram": "TELEGRAM",
        "discord": "DISCORD",
        "messenger": "MESSENGER",
        "linkedin": "LINKEDIN",
        "google": "GOOGLE", "gmail": "GOOGLE",
        "amazon": "AMAZON",
        "microsoft": "MICROSOFT", "outlook": "MICROSOFT",
        "yahoo": "YAHOO",
        "paypal": "PAYPAL",
        "binance": "BINANCE",
        "coinbase": "COINBASE",
        "spotify": "SPOTIFY",
        "netflix": "NETFLIX",
        "uber": "UBER",
        "apple": "APPLE", "icloud": "APPLE",
        "bkash": "BKASH",
        "nagad": "NAGAD",
        "stripe": "STRIPE",
        "line": "LINE",
        "wechat": "WECHAT",
        "viber": "VIBER",
        "signal": "SIGNAL",
        "pubg": "PUBG",
        "free fire": "FREE FIRE",
    }

    for keyword, service_name in sorted(service_keywords.items(), key=lambda x: len(x[0]), reverse=True):
        if keyword in sms_lower:
            return service_name

    return "SMS SERVICE"

# ==================== KEYBOARDS SECTION ====================

def make_reply_btn(text, emoji_id=None, style=None):
    api_kwargs = {}
    if emoji_id:
        api_kwargs['icon_custom_emoji_id'] = str(emoji_id)
    if style:
        api_kwargs['style'] = style
    return KeyboardButton(
        text=text,
        api_kwargs=api_kwargs if api_kwargs else None
    )

def main_keyboard(user_id):
    keyboard = [
        [
            make_reply_btn("🆓 FREE NUMBER"),
            make_reply_btn("📂 STOCK"),
        ],
        [
            make_reply_btn("💳 BALANCE"),
            make_reply_btn("👋 REFER"),
        ],
        [
            make_reply_btn("💬 LIVE SUPPORT"),
        ],
    ]

    if is_admin(user_id):
        keyboard.append([
            make_reply_btn("ADMIN PANEL", emoji_id="5350396951407895212")
        ])

    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def cancel_keyboard():
    keyboard = [[make_reply_btn("CANCEL", emoji_id="5420130255174145507", style="danger")]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def admin_main_keyboard():
    keyboard = [
        [make_reply_btn("USER MANAGEMENT",      emoji_id="5193063022226086560", style="success")],
        [make_reply_btn("SYSTEM CONFIGURATION", emoji_id="5341715473882955310", style="success")],
        [make_reply_btn("BOT SETTINGS",         emoji_id="5282843764451195532", style="primary")],
        [make_reply_btn("SERVICE MANAGEMENT",   emoji_id="5375338737028841420", style="primary")],
        [make_reply_btn("BACK TO MAIN",         emoji_id="5267490665117275176", style="danger")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def user_management_keyboard():
    keyboard = [
        [make_reply_btn("SEND MESSAGE TO ALL USERS", emoji_id="5251671733630431622", style="success")],
        [make_reply_btn("ALL USER ID",               emoji_id="5352861489541714456", style="primary")],
        [make_reply_btn("BAN USER LIST",             emoji_id="5420323339723881652", style="primary")],
        [make_reply_btn("ALL USER BALANCE",          emoji_id="6233367447789899509", style="primary")],
        [make_reply_btn("BACK TO ADMIN",             emoji_id="5267490665117275176", style="danger")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def system_config_keyboard():
    keyboard = [
        [make_reply_btn("TODAY ALL STATUS",  emoji_id="5231200819986047254", style="success"),
         make_reply_btn("USER STATUS CHECK", emoji_id="5352861489541714456", style="success")],
        [make_reply_btn("BAN USER",          emoji_id="5420323339723881652", style="danger"),
         make_reply_btn("UNBAN USER",        emoji_id="5875017993909440887", style="primary")],
        [make_reply_btn("BAN USER LIST",     emoji_id="5956074558044770726", style="primary")],
        [make_reply_btn("REMOVE BALANCE",    emoji_id="5244837092042750681", style="danger"),
         make_reply_btn("ADD BALANCE",       emoji_id="5397916757333654639", style="success")],
        [make_reply_btn("BACK TO ADMIN",     emoji_id="5267490665117275176", style="danger")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def bot_settings_keyboard():
    s = load_settings()
    console_active = s.get("live_console", False)
    console_label = "LIVE CONSOLE: ON 🟢" if console_active else "LIVE CONSOLE: OFF 🔴"

    keyboard = [
        [make_reply_btn("ADD ADMIN",          emoji_id="5397916757333654639", style="success"),
         make_reply_btn("REMOVE ADMIN",       emoji_id="5244837092042750681", style="danger")],
        [make_reply_btn(console_label,        emoji_id="5355102594886833928", style="success" if console_active else "danger")],
        [make_reply_btn("SET OTP GROUP LINK", emoji_id="5253742260054409879", style="primary")],
        [make_reply_btn("SET FORCE CHANNEL",  emoji_id="5282843764451195532", style="primary")],
        [make_reply_btn("SET OTP CHAT ID",    emoji_id="5231200819986047254", style="primary")],
        [make_reply_btn("SET OTP RATE",       emoji_id="5368324170671202286", style="success"),
         make_reply_btn("SET MIN WITHDRAW",   emoji_id="6233367447789899509", style="success")],
        [make_reply_btn("SET OTP BTN LINKS",  emoji_id="5253742260054409879", style="primary")],
        [make_reply_btn("ZENEX CONFIG",       emoji_id="5350396951407895212", style="success")],
        [make_reply_btn("EMOJI SETTINGS",     emoji_id="5251562950698759162", style="primary")],
        [make_reply_btn("BACK TO ADMIN",      emoji_id="5267490665117275176", style="danger")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ==================== EMOJI SETTINGS HELPERS ====================

_EMOJI_KEYS_LIST = sorted(EMOJI_ID_MAP.keys())
_EMOJI_PAGE_SIZE = 8

def get_emoji_page_keyboard(page: int = 0) -> InlineKeyboardMarkup:
    total = len(_EMOJI_KEYS_LIST)
    total_pages = max(1, (total + _EMOJI_PAGE_SIZE - 1) // _EMOJI_PAGE_SIZE)
    page = max(0, min(page, total_pages - 1))
    start = page * _EMOJI_PAGE_SIZE
    keys_slice = _EMOJI_KEYS_LIST[start: start + _EMOJI_PAGE_SIZE]

    custom_set = set(load_settings().get("custom_emojis", {}).keys())

    rows = []
    for i in range(0, len(keys_slice), 2):
        row = []
        for k in keys_slice[i:i+2]:
            fb = FALLBACK_EMOJI_MAP.get(k, "⭐")
            label = f"{fb} {k}" + (" ✏️" if k in custom_set else "")
            row.append(InlineKeyboardButton(label, callback_data=f"emoji_ed:{k}"))
        rows.append(row)

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("◀️", callback_data=f"emoji_pg:{page-1}"))
    nav.append(InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data="emoji_noop"))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton("▶️", callback_data=f"emoji_pg:{page+1}"))
    rows.append(nav)
    rows.append([InlineKeyboardButton("❌ Close", callback_data="emoji_close")])
    return InlineKeyboardMarkup(rows)

def zenex_config_keyboard():
    keyboard = [
        [make_reply_btn("SET API KEY",          emoji_id="5397916757333654639", style="success")],
        [make_reply_btn("SET BASE URL",         emoji_id="5253742260054409879", style="primary")],
        [make_reply_btn("SET ALLOWED SERVICES", emoji_id="5341715473882955310", style="primary")],
        [make_reply_btn("VIEW ZENEX CONFIG",    emoji_id="5231200819986047254", style="success")],
        [make_reply_btn("BACK TO BOT SETTINGS", emoji_id="5267490665117275176", style="danger")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def service_management_keyboard():
    keyboard = [
        [make_reply_btn("ADD SERVICE",    emoji_id="5397916757333654639", style="success")],
        [make_reply_btn("REMOVE SERVICE", emoji_id="5244837092042750681", style="danger")],
        [make_reply_btn("LIST SERVICES",  emoji_id="5352861489541714456", style="primary")],
        [make_reply_btn("BACK TO ADMIN",  emoji_id="5267490665117275176", style="danger")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def withdraw_method_keyboard():
    keyboard = ReplyKeyboardMarkup([
        [make_reply_btn("BKASH",  emoji_id="5348469219761626211", style="success"),
         make_reply_btn("NAGAD",  emoji_id="5352985330628730418", style="success")],
        [make_reply_btn("ROCKET", emoji_id="5346042941196507141", style="primary"),
         make_reply_btn("BINANCE",emoji_id="5348212415077064131", style="primary")],
        [make_reply_btn("CANCEL", emoji_id="5420130255174145507", style="danger")]
    ], resize_keyboard=True)
    return keyboard

def wallet_actions_keyboard():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("💳 SET WALLET", callback_data="wallet_set", style="primary"),
        InlineKeyboardButton("💸 WITHDRAW", callback_data="withdraw_start", style="success"),
    ]])

def wallet_method_selection_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("bKash", callback_data="wallet_method_bkash", style="primary"),
            InlineKeyboardButton("Nagad", callback_data="wallet_method_nagad", style="primary"),
        ],
        [
            InlineKeyboardButton("Rocket", callback_data="wallet_method_rocket", style="primary"),
            InlineKeyboardButton("Binance BEP20", callback_data="wallet_method_bep20", style="success"),
        ],
        [InlineKeyboardButton("⬅️ BACK", callback_data="wallet_view", style="danger")],
    ])

# ==================== HELPER FUNCTIONS SECTION ====================

def format_balance(balance):
    return f"{balance:.2f}"

def extract_otp(text):
    if not text or text == "No Content":
        return "N/A"
    spaced_otp = re.search(r'\b(\d{3}\s\d{3})\b', text)
    if spaced_otp:
        return spaced_otp.group(1).replace(" ", "")
    match = re.search(r'\b(\d{4,8})\b', text)
    return match.group(1) if match else "N/A"

def normalize_number(num):
    return re.sub(r'\D', '', str(num))

def mask_number(num):
    if len(num) > 6:
        return f"{num[:4]}****{num[-6:]}"
    return num

def get_date_reset_time():
    now = datetime.now()
    today_midnight = datetime(now.year, now.month, now.day, 0, 0, 0)
    return today_midnight

def is_valid_bangladesh_number(number):
    number = re.sub(r'\D', '', str(number))
    return len(number) == 11 and number.startswith('01')

def is_range_request(param):
    return 'X' in param.upper()

def is_referral_request(param):
    return param.isdigit()

# ==================== DATABASE FUNCTIONS SECTION ====================

def load_data(filename=USER_DATA_FILE):
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            json.dump({}, f)
        return {}
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except:
        return {}

def save_data(data, filename=USER_DATA_FILE):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

def get_user(uid):
    uid = str(uid)
    data = load_data()
    if uid not in data:
        data[uid] = {"user_id": uid, "balance": 0.0, "total_numbers": 0, "referral_count": 0}
        save_data(data)
    return data[uid]

async def update_db_balance(uid, amount):
    uid = str(uid)
    data = load_data()
    if uid in data:
        data[uid]["balance"] = round(data[uid].get("balance", 0.0) + amount, 2)
        save_data(data)
        return data[uid]["balance"]
    return 0.0

def get_all_users():
    data = load_data(USER_DATA_FILE)
    return list(data.keys()) if data else []

def user_exists(uid):
    data = load_data(USER_DATA_FILE)
    return str(uid) in data

# ==================== STATS FUNCTIONS SECTION ====================

def load_stats():
    if not os.path.exists(STATS_FILE):
        with open(STATS_FILE, "w") as f:
            json.dump({}, f)
        return {}
    try:
        with open(STATS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_stats(stats):
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f, indent=4)

def add_number_taken(uid, count=1):
    uid = str(uid)
    stats = load_stats()
    if uid not in stats:
        stats[uid] = {"numbers_taken": [], "otps_received": []}
    now = datetime.now().isoformat()
    for _ in range(count):
        stats[uid]["numbers_taken"].append(now)
    log_global_activity(uid, "NUMBER_TAKEN", {"count": count})
    save_stats(stats)

def add_otp_received(uid):
    uid = str(uid)
    stats = load_stats()
    if uid not in stats:
        stats[uid] = {"numbers_taken": [], "otps_received": []}
    stats[uid]["otps_received"].append(datetime.now().isoformat())
    save_stats(stats)

def get_user_stats(uid):
    uid = str(uid)
    stats = load_stats()
    user_stats = stats.get(uid, {"numbers_taken": [], "otps_received": []})

    now = datetime.now()
    today_midnight = get_date_reset_time()
    last_24h = now - timedelta(hours=24)
    last_7d = now - timedelta(days=7)

    numbers_taken = user_stats.get("numbers_taken", [])
    otps_received = user_stats.get("otps_received", [])

    today_numbers = sum(1 for t in numbers_taken if datetime.fromisoformat(t) >= today_midnight)
    today_otps = sum(1 for t in otps_received if datetime.fromisoformat(t) >= today_midnight)
    last24h_numbers = sum(1 for t in numbers_taken if datetime.fromisoformat(t) > last_24h)
    last24h_otps = sum(1 for t in otps_received if datetime.fromisoformat(t) > last_24h)
    last7d_numbers = sum(1 for t in numbers_taken if datetime.fromisoformat(t) > last_7d)
    last7d_otps = sum(1 for t in otps_received if datetime.fromisoformat(t) > last_7d)
    total_numbers = len(numbers_taken)
    total_otps = len(otps_received)

    return {
        "total_numbers": total_numbers, "total_otps": total_otps,
        "today_numbers": today_numbers, "today_otps": today_otps,
        "last24h_numbers": last24h_numbers, "last24h_otps": last24h_otps,
        "last7d_numbers": last7d_numbers, "last7d_otps": last7d_otps
    }

def log_global_activity(uid, action, details):
    if not os.path.exists(ACTIVITY_LOGS_FILE):
        with open(ACTIVITY_LOGS_FILE, "w") as f:
            json.dump([], f)
    try:
        with open(ACTIVITY_LOGS_FILE, "r") as f:
            logs = json.load(f)
    except:
        logs = []
    now = datetime.now()
    logs.append({
        "uid": str(uid), "action": action, "details": details,
        "timestamp": now.isoformat(),
        "date": now.strftime("%d/%m/%Y"),
        "time": now.strftime("%H:%M:%S")
    })
    with open(ACTIVITY_LOGS_FILE, "w") as f:
        json.dump(logs, f, indent=4)

def get_global_system_stats():
    stats = load_stats()
    now = datetime.now()
    today_midnight = datetime(now.year, now.month, now.day)
    last_7d = now - timedelta(days=7)
    total_n = total_o = today_n = today_o = seven_n = seven_o = 0
    for uid in stats:
        u = stats[uid]
        n_list = u.get("numbers_taken", [])
        o_list = u.get("otps_received", [])
        total_n += len(n_list)
        total_o += len(o_list)
        for t in n_list:
            dt = datetime.fromisoformat(t)
            if dt >= today_midnight: today_n += 1
            if dt >= last_7d: seven_n += 1
        for t in o_list:
            dt = datetime.fromisoformat(t)
            if dt >= today_midnight: today_o += 1
            if dt >= last_7d: seven_o += 1
    return today_n, today_o, seven_n, seven_o, total_n, total_o

# ==================== LIVE CONSOLE MANAGEMENT (YESMS CONSOLE_DATA) ====================

def load_console_sent():
    if not os.path.exists(CONSOLE_SENT_FILE):
        return {}
    try:
        with open(CONSOLE_SENT_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def save_console_sent(data):
    if len(data) > 2000:
        data = dict(list(data.items())[-1200:])
    try:
        with open(CONSOLE_SENT_FILE, "w") as f:
            json.dump(data, f)
    except Exception:
        pass

async def live_console_loop(app):
    """
    Background worker for Live Console:
    - Runs periodically (every live_console_interval seconds, default 120s / 2 minutes).
    - Checks https://yesms.online/api/console_data if live_console is ON in settings.
    - Selects up to 30 latest messages per cycle.
    - Sends each message to OTP_GROUP_ID (or configured otp_group_chat_id) in the exact same design.
    - Rate limit: 2 seconds delay between each message.
    """
    while True:
        try:
            s = load_settings()
            if s.get("live_console", False):
                api_key, base_url = get_api_credentials()
                urls = get_api_urls(base_url)
                headers = get_api_headers(api_key)

                try:
                    r = await client_async.get(
                        urls["console"],
                        headers=headers,
                        timeout=httpx.Timeout(10.0, connect=3.0, read=7.0)
                    )
                    if r.status_code == 200:
                        try:
                            res = r.json()
                        except Exception:
                            res = None

                        raw_items = []
                        if isinstance(res, dict):
                            raw_items = res.get("logs") or res.get("data") or res.get("messages") or res.get("console") or []
                        elif isinstance(res, list):
                            raw_items = res

                        if raw_items:
                            sent_cache = load_console_sent()
                            new_items = []

                            for item in raw_items:
                                if not isinstance(item, dict):
                                    continue
                                num = normalize_number(item.get("number") or item.get("num") or item.get("phone") or "")
                                full_sms = item.get("full_message") or item.get("message") or item.get("sms") or item.get("otp_code") or ""
                                otp_code = item.get("otp_code") or item.get("otp") or extract_otp(full_sms)
                                time_str = str(item.get("time") or item.get("timestamp") or "")

                                if not num or not otp_code or otp_code == "N/A":
                                    continue

                                unique_key = f"{num}_{time_str}_{otp_code}"
                                if unique_key not in sent_cache:
                                    new_items.append({
                                        "key": unique_key,
                                        "num": num,
                                        "otp": otp_code,
                                        "sms": full_sms,
                                        "service": item.get("service") or item.get("app") or detect_service(full_sms)
                                    })

                            # Latest up to 30 items per cycle
                            limit = int(s.get("live_console_limit", 30))
                            batch = new_items[-limit:] if len(new_items) > limit else new_items

                            gid = s.get("otp_group_chat_id") or OTP_GROUP_ID
                            panel_url = s.get("panel_url", "https://t.me/Nextsmsbdbot")
                            channel_url = s.get("channel_url", "https://t.me/kabbofc")
                            send_delay = float(s.get("live_console_delay", 2.0))

                            for entry in batch:
                                cur_s = load_settings()
                                if not cur_s.get("live_console", False):
                                    break

                                num = entry["num"]
                                otp_code = entry["otp"]
                                full_sms = entry["sms"]
                                service_name = entry["service"] or detect_service(full_sms)

                                country_flag, country_name = get_country_info(num)
                                clean_num = num.replace("+", "").strip()
                                flag_tg = get_country_tg_flag(country_flag)
                                app_em = get_platform_icon(service_name)

                                if HAS_COPY_BTN:
                                    try:
                                        btn_copy = InlineKeyboardButton(
                                            text=otp_code,
                                            copy_text=CopyTextButton(text=otp_code),
                                            api_kwargs={"icon_custom_emoji_id": "5296369303661067030"}
                                        )
                                    except Exception:
                                        btn_copy = InlineKeyboardButton(
                                            otp_code, callback_data=f"copy_text_{otp_code}",
                                            api_kwargs={"icon_custom_emoji_id": "5296369303661067030"}
                                        )
                                else:
                                    btn_copy = InlineKeyboardButton(
                                        otp_code, callback_data=f"copy_text_{otp_code}",
                                        api_kwargs={"icon_custom_emoji_id": "5296369303661067030"}
                                    )

                                masked = mask_number(clean_num)
                                group_msg = f"{flag_tg} {app_em} +{masked}"
                                group_kb = InlineKeyboardMarkup([
                                    [btn_copy],
                                    [
                                        InlineKeyboardButton(
                                            " NUMBER", url=panel_url,
                                            api_kwargs={"icon_custom_emoji_id": "4943094697238201446", "style": "primary"}
                                        ),
                                        InlineKeyboardButton(
                                            " CHANNEL", url=channel_url,
                                            api_kwargs={"icon_custom_emoji_id": "6215074610845585917", "style": "primary"}
                                        )
                                    ]
                                ])

                                if gid:
                                    try:
                                        await app.bot.send_message(
                                            gid, group_msg, parse_mode="HTML", reply_markup=group_kb
                                        )
                                        print(f"[LiveConsole] OTP sent to group {gid}: +{masked}")
                                    except Exception as send_err:
                                        print(f"[LiveConsole] Send error gid={gid}: {send_err}")

                                sent_cache[entry["key"]] = int(time.time())
                                save_console_sent(sent_cache)

                                # 2 seconds limit per message
                                await asyncio.sleep(send_delay)
                    else:
                        print(f"[LiveConsole] API returned status {r.status_code}")
                except Exception as api_err:
                    print(f"[LiveConsole] Request error: {api_err}")

        except Exception as loop_err:
            print(f"[LiveConsole] Loop exception: {loop_err}")

        # Sleep interval (default 2 minutes = 120 seconds)
        interval = int(load_settings().get("live_console_interval", 120))
        await asyncio.sleep(interval)

# ==================== LEADERBOARD SECTION ====================

async def leaderboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if is_user_banned(uid):
        await update.message.reply_text("🚫 YOU ARE BANNED 🚫", reply_markup=main_keyboard(uid))
        return

    stats_data = load_stats()
    today_midnight = get_date_reset_time()
    user_data_all = load_data(USER_DATA_FILE)

    user_today_counts = []

    for uid_str, user_stats in stats_data.items():
        otps_received = user_stats.get("otps_received", [])
        today_count = 0
        for ts in otps_received:
            try:
                dt = datetime.fromisoformat(ts)
                if dt >= today_midnight:
                    today_count += 1
            except:
                continue
        if today_count > 0:
            name = user_data_all.get(uid_str, {}).get("full_name")
            if not name:
                name = user_data_all.get(uid_str, {}).get("username")
            if not name:
                name = f"User {uid_str}"
            user_today_counts.append((uid_str, today_count, html.escape(name)))

    user_today_counts.sort(key=lambda x: x[1], reverse=True)
    top10 = user_today_counts[:10]

    if not top10:
        msg = (
            "<b>🏆 TOP 10 OTP LEADERBOARD 🏆</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "❌ আজ পর্যন্ত কেউ OTP পায়নি।\n"
        )
    else:
        msg = (
            "<b>🏆 TOP 10 OTP RECEIVERS (TODAY) 🏆</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
        )
        for idx, (uid_str, count, name) in enumerate(top10, 1):
            if idx == 1:
                medal = "🥇"
            elif idx == 2:
                medal = "🥈"
            elif idx == 3:
                medal = "🥉"
            else:
                medal = f"{idx}️⃣"
            msg += f"{medal} <b>{name}</b>\n   🔑 <code>{count}</code> OTPs\n\n"
        msg += (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📊 <i>প্রতিদিন রাত ১২টায় রিসেট হয়</i>"
        )

    await update.message.reply_text(msg, parse_mode="HTML", reply_markup=main_keyboard(uid))

# ==================== 2FA CODE GENERATOR SECTION ====================

def generate_2fa_code(secret_key):
    try:
        clean_secret = secret_key.replace(" ", "").upper().strip()
        key = base64.b32decode(clean_secret, casefold=True)
        t = int(time.time()) // 30
        msg_bytes = struct.pack(">Q", t)
        h = hmac.new(key, msg_bytes, hashlib.sha1).digest()
        o = h[-1] & 0xf
        code = (struct.unpack(">I", h[o:o+4])[0] & 0x7fffffff) % 1_000_000
        return f"{code:06d}", clean_secret
    except:
        return None, None

async def get_2fa_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if is_user_banned(uid):
        await update.message.reply_text("🚫 YOU ARE BANNED 🚫", reply_markup=main_keyboard(uid))
        return
    context.user_data["mode"] = "get_2fa"
    await update.message.reply_text(
        "⚡ <b>GET 2FA CODE</b> ⚡\n\n"
        "<blockquote>🔑 ENTER YOUR 2FA SECRET KEY:</blockquote>",
        parse_mode="HTML"
    )

async def process_2fa_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    secret_key = update.message.text.strip()
    context.user_data["mode"] = None

    otp_code, clean_key = generate_2fa_code(secret_key)

    if otp_code is None:
        await update.message.reply_text(
            "❌ <b>INVALID 2FA SECRET KEY</b>\n\n⚠️ Please send a valid base32 key.",
            parse_mode="HTML",
            reply_markup=main_keyboard(uid)
        )
        return

    now = datetime.now()
    final_msg = (
        "✅ <b>2FA CODE GENERATED!</b>\n\n"
        f"<blockquote>🔑 KEY: <code>{clean_key}</code></blockquote>\n"
        f"<blockquote>🔢 CODE: <code>{otp_code}</code></blockquote>\n"
        f"<blockquote>⏳ EXPIRES IN: 30 SECONDS</blockquote>\n"
        f"📅 {now.strftime('%d %B, %Y')} | {now.strftime('%I:%M %p')}"
    )
    await update.message.reply_text(final_msg, parse_mode="HTML")

def build_manual_service_buttons():
    s = load_settings()
    manual = s.get("manual_services", [])
    rows = []
    for i, svc in enumerate(manual):
        rows.append([InlineKeyboardButton(
            make_bold_text(svc['name']),
            callback_data=f"manual_svc_{i}",
            api_kwargs={"icon_custom_emoji_id": get_app_emoji_id(svc['name']), "style": "success"}
        )])
    return rows

async def show_app_selection(update, context):
    uid = update.effective_user.id
    if is_user_banned(uid):
        await update.message.reply_text("🚫 YOU ARE BANNED 🚫", reply_markup=main_keyboard(uid))
        return
    context.user_data.pop("top_ranges_by_app", None)

    async def _build_full_keyboard(top):
        all_rows = build_app_buttons_from_cache(top)
        all_rows.append([InlineKeyboardButton(
            "🎯 Custom Range",
            callback_data="custom_range",
            api_kwargs={"icon_custom_emoji_id": "5231012545799666522", "style": "primary"})])
        all_rows.append([InlineKeyboardButton(
            "🏠 Main Menu",
            callback_data="back_main",
            api_kwargs={"style": "success"})])
        return all_rows

    cache_age = time.monotonic() - _ranges_cache["updated_at"]
    if _ranges_cache["data"] and cache_age < 300:
        top = _ranges_cache["data"]
        context.user_data["top_ranges_by_app"] = top
        msg = f'{get_tg_emoji("setting")} <b>Select Service:</b>'
        kb = await _build_full_keyboard(top)
        await update.message.reply_text(msg, parse_mode="HTML",
                                         reply_markup=InlineKeyboardMarkup(kb))
        return
    status = await update.message.reply_text(
        f'{get_tg_emoji("loading")} <b>Loading...</b>', parse_mode="HTML")
    top, err = await fetch_top55_ranges_by_app()
    if err or not top:
        top, err = await fetch_top55_ranges_by_app()
    if err:
        manual_rows = build_manual_service_buttons()
        if manual_rows:
            manual_rows.append([InlineKeyboardButton("🏠 Main Menu", callback_data="back_main",
                                                      api_kwargs={"style": "success"})])
            await status.edit_text(
                f'{get_tg_emoji("setting")} <b>Select Service:</b>',
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(manual_rows))
        else:
            await status.edit_text(
                f'{get_tg_emoji("cross")} <b>Could not load ranges.</b>\n<blockquote>{err}</blockquote>',
                parse_mode="HTML")
        return
    if not top:
        manual_rows = build_manual_service_buttons()
        if manual_rows:
            manual_rows.append([InlineKeyboardButton("🏠 Main Menu", callback_data="back_main",
                                                      api_kwargs={"style": "success"})])
            await status.edit_text(
                f'{get_tg_emoji("setting")} <b>Select Service:</b>',
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(manual_rows))
        else:
            await status.edit_text(
                f'{get_tg_emoji("stop")} No active ranges returned by the API.', parse_mode="HTML")
        return
    _ranges_cache["data"] = top
    _ranges_cache["updated_at"] = time.monotonic()
    context.user_data["top_ranges_by_app"] = top
    msg = f'{get_tg_emoji("setting")} <b>Select Service:</b>'
    kb = await _build_full_keyboard(top)
    await status.edit_text(msg, parse_mode="HTML",
                            reply_markup=InlineKeyboardMarkup(kb))

async def show_live_stock(update, context):
    uid = update.effective_user.id
    message = update.effective_message
    if is_user_banned(uid):
        await message.reply_text("🚫 YOU ARE BANNED 🚫", reply_markup=main_keyboard(uid))
        return

    status = await message.reply_text("📂 Loading live stock...")
    top, err = await fetch_top55_ranges_by_app()
    if err:
        await status.edit_text(
            "❌ <b>Live stock is unavailable right now.</b>\n\n"
            f"<blockquote>{html.escape(str(err))}</blockquote>",
            parse_mode="HTML",
        )
        return
    if not top:
        await status.edit_text(
            "📂 <b>No active services or ranges are available right now.</b>",
            parse_mode="HTML",
        )
        return

    _ranges_cache["data"] = top
    _ranges_cache["updated_at"] = time.monotonic()
    context.user_data["top_ranges_by_app"] = top
    total_ranges = sum(len(item.get("ranges", [])) for item in top.values())
    lines = []
    for app_name, item in list(top.items())[:16]:
        countries = []
        for range_text in item.get("ranges", [])[:4]:
            prefix = re.sub(r"[xX]+$", "", str(range_text)).strip()
            flag, country_name = get_country_info(re.sub(r"\D", "", prefix))
            label = f"{flag} {country_name}"
            if label not in countries:
                countries.append(label)
        country_text = ", ".join(countries) or "Active range"
        lines.append(
            f"• <b>{html.escape(str(app_name))}</b> — "
            f"{html.escape(country_text)}"
        )

    await status.edit_text(
        "📂 <b>LIVE STOCK</b>\n\n"
        f"<blockquote>🟢 Active services: <b>{len(top)}</b>\n"
        f"🌍 Active ranges: <b>{total_ranges}</b></blockquote>\n\n"
        f"{chr(10).join(lines)}\n\n"
        "<i>YESMS currently provides active ranges, not an exact remaining-number count.</i>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🆓 FREE NUMBER", callback_data="back_apps", style="success")
        ]]),
    )

# ==================== AUTO OTP MONITOR SECTION (ZENEXA USER MONITOR) ====================

async def monitor_loop(app):
    while True:
        try:
            settings = load_settings()
            api_key, base_url = get_api_credentials()
            urls = get_api_urls(base_url)
            headers = get_api_headers(api_key)
            r = await client_async.get(urls["otp"], headers=headers)
            if r.status_code != 200:
                await asyncio.sleep(5); continue
            try: res = r.json()
            except Exception: await asyncio.sleep(5); continue

            otps = []
            if isinstance(res, dict) and res.get("success"):
                otps = res.get("logs") or []
            elif isinstance(res, list):
                otps = res

            if otps:
                paid_data = load_data(PAID_SMS_FILE)
                paid_keys_set = set(paid_data.keys())
                processed_in_session = set()

                for otp in otps:
                    num = normalize_number(otp.get("number", ""))
                    full_sms = otp.get("full_message") or otp.get("otp_code") or "No SMS Content"
                    otp_code = otp.get("otp_code") or extract_otp(full_sms)
                    if not otp_code or otp_code == "N/A": continue
                    sms_key = f"{num}_{otp.get('time', '')}_{otp_code}"

                    if (num in active_numbers and
                            sms_key not in paid_keys_set and
                            sms_key not in processed_in_session):
                        details = active_numbers[num]
                        paid_keys_set.add(sms_key)
                        processed_in_session.add(sms_key)
                        paid_data[sms_key] = {"uid": details["uid"], "otp": otp_code}

                        otp_bonus = settings.get("otp_bonus", OTP_RATE)
                        await update_db_balance(details["uid"], otp_bonus)
                        add_otp_received(details["uid"])
                        log_global_activity(details["uid"], "OTP_RECEIVED",
                                            {"number": num, "otp": otp_code, "sms": full_sms})

                        country_flag, country_name = get_country_info(num)
                        clean_num = num.replace('+', '').strip()
                        flag_tg = get_country_tg_flag(country_flag)
                        purchased_app = details.get("app") or detect_service(full_sms)
                        app_em = get_platform_icon(purchased_app)

                        if HAS_COPY_BTN:
                            try:
                                btn_copy = InlineKeyboardButton(
                                    text=otp_code,
                                    copy_text=CopyTextButton(text=otp_code),
                                    api_kwargs={"icon_custom_emoji_id": "5296369303661067030"})
                            except Exception:
                                btn_copy = InlineKeyboardButton(
                                    otp_code, callback_data=f"copy_text_{otp_code}",
                                    api_kwargs={"icon_custom_emoji_id": "5296369303661067030"})
                        else:
                            btn_copy = InlineKeyboardButton(
                                otp_code, callback_data=f"copy_text_{otp_code}",
                                api_kwargs={"icon_custom_emoji_id": "5296369303661067030"})

                        _s = load_settings()
                        panel_url   = _s.get("panel_url",   "https://t.me/Nextsmsbdbot")
                        channel_url = _s.get("channel_url", "https://t.me/kabbofc")
                        masked = mask_number(clean_num)
                        user_msg  = f"{flag_tg} {app_em} +{clean_num}"
                        group_msg = f"{flag_tg} {app_em} +{masked}"
                        user_kb   = InlineKeyboardMarkup([[btn_copy]])
                        group_kb  = InlineKeyboardMarkup([
                            [btn_copy],
                            [InlineKeyboardButton(" NUMBER", url=panel_url,
                                api_kwargs={"icon_custom_emoji_id": "4943094697238201446", "style": "primary"}),
                             InlineKeyboardButton(" CHANNEL", url=channel_url,
                                api_kwargs={"icon_custom_emoji_id": "6215074610845585917", "style": "primary"})]])

                        try: await app.bot.send_message(details["uid"], user_msg, parse_mode="HTML", reply_markup=user_kb)
                        except Exception as e: print(f"[OTP] Failed to send to user uid={details['uid']}: {e}")
                        try:
                            gid = settings.get("otp_group_chat_id") or OTP_GROUP_ID
                            if gid:
                                await app.bot.send_message(gid, group_msg, parse_mode="HTML", reply_markup=group_kb)
                        except Exception as e: print(f"[OTP] Failed to send to group gid={gid}: {e}")
                        save_data(paid_data, PAID_SMS_FILE)

            now = datetime.now()
            for nk in [k for k, v in list(active_numbers.items())
                        if isinstance(v, dict) and "timestamp" in v
                        and (now - v["timestamp"]).total_seconds() > 3600]:
                del active_numbers[nk]
        except Exception: pass
        await asyncio.sleep(CHECK_INTERVAL)

# ==================== WORKER & API SECTION ====================

async def fetch_number_async(range_str):
    try:
        api_key, base_url = get_api_credentials()
        urls = get_api_urls(base_url)
        headers = get_api_headers(api_key)
        r = await client_async.post(urls["getnum"],
            json={"range_id": range_str},
            headers=headers, timeout=httpx.Timeout(3.0, connect=0.8, read=2.2))
        if r.status_code != 200: return None
        data = r.json()
        num = None
        if isinstance(data, dict) and data.get("success"):
            nd = data.get("data", {})
            if isinstance(nd, dict):
                num = nd.get("full_number") or nd.get("national_number") or nd.get("number")
        if num:
            return {"number": num, "otp_now": False, "otp": None, "sms": None}
    except Exception: pass
    return None

async def fast_allocate_number(query, context, range_text, sid):
    uid = query.from_user.id

    if is_user_banned(uid):
        await query.message.edit_text("🚫 YOU ARE BANNED 🚫")
        return

    try:
        results = await asyncio.gather(
            fetch_number_async(range_text),
            fetch_number_async(range_text)
        )
        valid_results = [r for r in results if r and r.get("number")]
    except Exception as e:
        await query.message.edit_text(f"❌ Server error: {str(e)[:100]}")
        return

    if not valid_results:
        await query.message.edit_text(
            "❌ <b>Number পাওয়া যায়নি।</b>\n\n"
            "<blockquote>⚠️ এই range-এ এখন number নেই বা server busy।\n"
            "আরেকটি range চেষ্টা করুন।</blockquote>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 BACK", callback_data="back_services", style="danger")
            ]])
        )
        return

    add_number_taken(uid, len(valid_results))
    last_range[uid] = range_text

    num_entries = []
    for r in valid_results:
        clean_num = normalize_number(r["number"])
        if clean_num:
            active_numbers[clean_num] = {"uid": uid, "range": range_text, "timestamp": datetime.now()}
            save_number_range_info(uid, clean_num, range_text)
            num_entries.append({
                "num":     clean_num,
                "otp_now": r.get("otp_now", False),
                "otp":     r.get("otp"),
                "sms":     r.get("sms"),
            })

    if not num_entries:
        await query.message.edit_text(
            "❌ <b>Number পাওয়া যায়নি।</b>\n\n"
            "<blockquote>⚠️ এই range-এ এখন number নেই বা server busy।\n"
            "আরেকটি range চেষ্টা করুন।</blockquote>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 BACK", callback_data="back_services", style="danger")
            ]])
        )
        return

    country_flag, country_name = get_country_info(num_entries[0]["num"])
    svc_icon = get_platform_icon(sid)

    any_instant = any(e["otp_now"] and e["otp"] for e in num_entries)

    if any_instant:
        msg_text = (
            f"<b>OTP Received ✅</b>\n"
            f"📞 Country : {country_flag} {html.escape(country_name)} {svc_icon}\n"
        )
        for entry in num_entries:
            if entry["otp_now"] and entry["otp"]:
                otp_safe = html.escape(str(entry["otp"]))
                sms_safe = html.escape(str(entry.get("sms") or ""))
                add_otp_received(uid)
                msg_text += f"\n🔑 OTP: <code>{otp_safe}</code>"
                if sms_safe:
                    msg_text += f"\n📩 SMS: <code>{sms_safe}</code>"
    else:
        msg_text = (
            f"<b>New Number Assigned ‼️</b>\n"
            f"📞 Country : {country_flag} {html.escape(country_name)} {svc_icon}\n\n"
            f"» Waiting For OTP ✉️"
        )

    num_buttons = []
    for entry in num_entries:
        num_display = f"{country_flag} 📋 +{entry['num']}"
        if HAS_COPY_BTN:
            try:
                btn = InlineKeyboardButton(
                    text=num_display,
                    copy_text=CopyTextButton(text=f"+{entry['num']}"),
                    style="success"
                )
            except Exception:
                btn = InlineKeyboardButton(num_display, callback_data=f"copy_text_+{entry['num']}", style="success")
        else:
            btn = InlineKeyboardButton(num_display, callback_data=f"copy_text_+{entry['num']}", style="success")
        num_buttons.append([btn])

    _otp_grp_url1 = load_settings().get("otp_group_url", "https://t.me/zenoxaaotp")
    keyboard = InlineKeyboardMarkup(
        num_buttons + [
            [InlineKeyboardButton("🔄 Change Number", callback_data="same_range", style="success"),
             InlineKeyboardButton("👉 Change Country", callback_data="back_services", style="success")],
            [InlineKeyboardButton("🔗 OTP Group", url=_otp_grp_url1, style="primary")],
            [InlineKeyboardButton("🏠 Back to Main", callback_data="back_main", style="primary")],
        ]
    )
    try:
        await query.message.edit_text(msg_text, parse_mode="HTML", reply_markup=keyboard)
    except Exception as e:
        print(f"fast_allocate edit error: {e}")

async def worker():
    while True:
        task = await request_queue.get()
        try:
            if task['type'] == 'process_numbers':
                await process_numbers(task['update'], task['context'], task['range_text'], task['count'])
            elif task['type'] == 'search_otp':
                await perform_otp_search(task['update'], task['context'], task['target_num'])
            elif task['type'] == 'auto_number':
                await process_auto_number(task['update'], task['context'], task['range_text'])
        except Exception as e:
            print(f"Worker Error: {e}")
        finally:
            request_queue.task_done()

# ==================== AUTO NUMBER FROM LINK / DEEP LINK ====================

async def process_auto_number(update, context, range_text):
    uid = update.effective_user.id
    chat_id = update.effective_chat.id

    if is_user_banned(uid):
        await context.bot.send_message(chat_id=chat_id, text="🚫 YOU ARE BANNED 🚫", reply_markup=main_keyboard(uid))
        return

    status_msg = await context.bot.send_message(chat_id=chat_id, text="🔍 SEARCHING...")

    try:
        res = await fetch_number_async(range_text)
        if not res:
            await status_msg.edit_text("❌ NO NUMBERS FOUND. TRY A VALID RANGE.")
            return

        generated_num = normalize_number(res["number"]) if res else None
        if not generated_num:
            await status_msg.edit_text("❌ NO NUMBERS FOUND. TRY A VALID RANGE.")
            return

        add_number_taken(uid, 1)
        last_range[uid] = range_text
        active_numbers[generated_num] = {"uid": uid, "range": range_text, "timestamp": datetime.now()}
        save_number_range_info(uid, generated_num, range_text)

        country_flag, country_name = get_country_info(generated_num)

        if res.get("otp_now") and res.get("otp"):
            instant_otp = html.escape(str(res["otp"]))
            instant_sms = html.escape(str(res.get("sms") or ""))
            add_otp_received(uid)
            final_text = (
                f"<b>OTP Received ✅</b>\n"
                f"📞 Country : {country_flag} {html.escape(country_name)}\n\n"
                f"🔑 OTP: <code>{instant_otp}</code>"
                + (f"\n📩 SMS: <code>{instant_sms}</code>" if instant_sms else "")
            )
        else:
            final_text = (
                f"<b>New Number Assigned ‼️</b>\n"
                f"📞 Country : {country_flag} {html.escape(country_name)}\n\n"
                f"» Waiting For OTP ✉️"
            )

        num_display = f"{country_flag} 📋 +{generated_num}"
        if HAS_COPY_BTN:
            try:
                num_btn = InlineKeyboardButton(text=num_display, copy_text=CopyTextButton(text=f"+{generated_num}"), style="success")
            except Exception:
                num_btn = InlineKeyboardButton(num_display, callback_data=f"copy_text_+{generated_num}", style="success")
        else:
            num_btn = InlineKeyboardButton(num_display, callback_data=f"copy_text_+{generated_num}", style="success")

        _otp_grp_url2 = load_settings().get("otp_group_url", "https://t.me/zenoxaaotp")
        keyboard = InlineKeyboardMarkup([
            [num_btn],
            [InlineKeyboardButton("🔄 Change Number", callback_data="same_range", style="success"),
             InlineKeyboardButton("👉 Change Country", callback_data="back_services", style="success")],
            [InlineKeyboardButton("🔗 OTP Group", url=_otp_grp_url2, style="primary")],
            [InlineKeyboardButton("🏠 Back to Main", callback_data="back_main", style="primary")],
        ])
        await status_msg.edit_text(final_text, parse_mode="HTML", reply_markup=keyboard)

    except Exception as e:
        print(f"Auto Number Error: {e}")
        await status_msg.edit_text(f"❌ Error: {str(e)}")

# ==================== USER PANEL — PROCESS NUMBERS ====================

async def process_numbers(update_or_query, context, range_text, count):
    if isinstance(update_or_query, Update) and update_or_query.callback_query:
        uid = update_or_query.callback_query.from_user.id
        chat_id = update_or_query.callback_query.message.chat_id
    else:
        uid = update_or_query.effective_user.id
        chat_id = update_or_query.effective_chat.id

    if is_user_banned(uid):
        await context.bot.send_message(chat_id=chat_id, text="🚫 YOU ARE BANNED 🚫", reply_markup=main_keyboard(uid))
        return

    status_msg = await context.bot.send_message(chat_id=chat_id, text="🔍 SEARCHING . . .")

    try:
        add_number_taken(uid, count)
        last_range[uid] = range_text

        tasks = [fetch_number_async(range_text) for _ in range(count)]
        results = await asyncio.gather(*tasks)
        valid_results = [r for r in results if r and r.get("number")]

        if not valid_results:
            await status_msg.edit_text("❌ NO NUMBERS FOUND. TRY A VALID RANGE.")
            return

        num_entries = []
        for r in valid_results:
            clean_num = normalize_number(r["number"])
            if clean_num:
                active_numbers[clean_num] = {"uid": uid, "range": range_text, "timestamp": datetime.now()}
                save_number_range_info(uid, clean_num, range_text)
                num_entries.append({
                    "num":     clean_num,
                    "otp_now": r.get("otp_now", False),
                    "otp":     r.get("otp"),
                    "sms":     r.get("sms"),
                })

        if not num_entries:
            await status_msg.edit_text("❌ NO NUMBERS FOUND. TRY A VALID RANGE.")
            return

        country_flag, country_name = get_country_info(num_entries[0]["num"])
        any_instant = any(e["otp_now"] and e["otp"] for e in num_entries)

        if any_instant:
            final_text = (
                f"<b>OTP Received ✅</b>\n"
                f"📞 Country : {country_flag} {html.escape(country_name)}\n"
            )
            for entry in num_entries:
                if entry["otp_now"] and entry["otp"]:
                    otp_safe = html.escape(str(entry["otp"]))
                    sms_safe = html.escape(str(entry.get("sms") or ""))
                    add_otp_received(uid)
                    final_text += f"\n🔑 OTP: <code>{otp_safe}</code>"
                    if sms_safe:
                        final_text += f"\n📩 SMS: <code>{sms_safe}</code>"
        else:
            final_text = (
                f"<b>New Number Assigned ‼️</b>\n"
                f"📞 Country : {country_flag} {html.escape(country_name)}\n\n"
                f"» Waiting For OTP ✉️"
            )

        num_buttons = []
        for entry in num_entries:
            num_display = f"{country_flag} 📋 +{entry['num']}"
            if HAS_COPY_BTN:
                try:
                    btn = InlineKeyboardButton(
                        text=num_display,
                        copy_text=CopyTextButton(text=f"+{entry['num']}"),
                        style="success"
                    )
                except Exception:
                    btn = InlineKeyboardButton(num_display, callback_data=f"copy_text_+{entry['num']}", style="success")
            else:
                btn = InlineKeyboardButton(num_display, callback_data=f"copy_text_+{entry['num']}", style="success")
            num_buttons.append([btn])

        _otp_grp_url3 = load_settings().get("otp_group_url", "https://t.me/zenoxaaotp")
        keyboard = InlineKeyboardMarkup(
            num_buttons + [
                [InlineKeyboardButton("🔄 Change Number", callback_data="same_range", style="success"),
                 InlineKeyboardButton("👉 Change Country", callback_data="back_services", style="success")],
                [InlineKeyboardButton("🔗 OTP Group", url=_otp_grp_url3, style="primary")],
                [InlineKeyboardButton("🏠 Back to Main", callback_data="back_main", style="primary")],
            ]
        )

        await status_msg.edit_text(final_text, parse_mode="HTML", reply_markup=keyboard)

    except Exception as e:
        print(f"Process Number Error: {e}")
        await status_msg.edit_text(f"❌ System Error: {str(e)}")

async def perform_otp_search(update, context, target_num):
    uid = str(update.effective_user.id)

    if is_user_banned(int(uid)):
        await update.message.reply_text("🚫 YOU ARE BANNED 🚫", reply_markup=main_keyboard(int(uid)))
        return

    status_msg = await update.message.reply_text("🔍 SEARCHING IN SERVER...")

    try:
        api_key, base_url = get_api_credentials()
        urls = get_api_urls(base_url)
        headers = get_api_headers(api_key)
        r = await client_async.get(urls["otp"], headers=headers)
        res = r.json()
        raw_otps = []
        if isinstance(res, dict) and res.get("success"):
            raw_otps = res.get("logs") or []
        elif isinstance(res, list):
            raw_otps = res
        if r.status_code == 200:
            all_otps = raw_otps
            found_otps = [o for o in all_otps if normalize_number(o.get("number", "")) == target_num]

            if not found_otps:
                error_msg = (
                    "━━━━━━━━━━━━━━━━━━\n❌ NO OTP FOUND\n━━━━━━━━━━━━━━━━━━\n\n"
                    f"📞 NUMBER:\n`+{target_num}`\n\n⏳ PLEASE TRY AGAIN LATER\n━━━━━━━━━━━━━━━━━━"
                )
                await status_msg.edit_text(error_msg, parse_mode="Markdown")
                await update.message.reply_text("🔙 RETURNING TO MAIN MENU...", reply_markup=main_keyboard(int(uid)))
            else:
                await status_msg.delete()
                paid_data = load_data(PAID_SMS_FILE)

                for o in found_otps:
                    full_sms = o.get('full_message') or o.get('otp_code') or "No Content Found"
                    otp_code = o.get('otp_code') or extract_otp(full_sms)
                    sms_key = f"{target_num}_{o.get('time', '')}_{otp_code}"

                    if sms_key in paid_data:
                        payment_status = "❌ ALREADY PAID"
                    else:
                        await update_db_balance(uid, OTP_RATE)
                        add_otp_received(uid)
                        paid_data[sms_key] = {"uid": uid, "otp": otp_code}
                        payment_status = f"💵 ADD BALANCE FOR {OTP_RATE:.2f} BDT"

                    save_data(paid_data, PAID_SMS_FILE)
                    country_flag, country_name = get_country_info(target_num)
                    service_name = detect_service(full_sms)

                    msg = (
                        f"✅ <b>OTP FOUND!</b>\n\n"
                        f"<blockquote>🌍 COUNTRY: <code>{country_flag} {country_name}</code></blockquote>\n"
                        f"<blockquote>📱 SERVICE: <code>{service_name}</code></blockquote>\n"
                        f"<blockquote>📞 NUMBER: <code>+{target_num}</code></blockquote>\n"
                        f"<blockquote>🔑 OTP: <code>{html.escape(otp_code)}</code></blockquote>\n\n"
                        f"<blockquote>📩 FULL SMS:\n<code>{html.escape(str(full_sms))}</code></blockquote>\n\n"
                        f"<b>{payment_status}</b>"
                    )
                    await update.message.reply_text(msg, parse_mode="HTML", reply_markup=main_keyboard(int(uid)))
        else:
            await status_msg.edit_text("❌ SERVER RETURNED AN ERROR.")
            await update.message.reply_text("🔙 Returning to Main Menu...", reply_markup=main_keyboard(int(uid)))

    except Exception as e:
        try:
            await status_msg.edit_text(f"❌ Error: {str(e)}")
        except:
            await update.message.reply_text(f"❌ Error: {str(e)}")
        await update.message.reply_text("🔙 Returning to Main Menu...", reply_markup=main_keyboard(int(uid)))

# ==================== REFER AND EARN SECTION ====================

async def refer_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id

    if is_user_banned(uid):
        await update.message.reply_text("🚫 YOU ARE BANNED 🚫", reply_markup=main_keyboard(uid))
        return

    user_data = get_user(uid)
    bot_info = await context.bot.get_me()

    referral_link = f"https://t.me/{bot_info.username}?start={uid}"
    successful_refers = get_referral_count(uid)
    total_reward = float(successful_refers) * REFERRAL_PRICE

    refer_msg = (
        f"🎁 <b>REFER AND EARN SYSTEM</b> 🎁\n\n"
        f"<blockquote>🚀 INVITE FRIENDS &amp; EARN {int(REFERRAL_PRICE)} BDT EACH! 💸</blockquote>\n\n"
        f"<b>🔗 YOUR REFERRAL LINK:</b>\n"
        f"<blockquote><code>{referral_link}</code></blockquote>\n\n"
        f"<b>📊 YOUR STATS:</b>\n"
        f"<blockquote>👥 TOTAL REFERS: {successful_refers}\n"
        f"💰 TOTAL EARNED: {format_balance(total_reward)} BDT</blockquote>\n\n"
        f"✨ <b>SHARE LINK &amp; EARN MONEY!</b> ✨"
    )

    await update.message.reply_text(
        refer_msg,
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("👥 YOUR REFERRAL", callback_data=f"my_ref_{uid}", style="primary")
        ]])
    )

# ==================== WITHDRAW FUNCTIONS ====================

def format_wallet_amount(amount):
    try:
        return f"{float(amount):.4f}"
    except (TypeError, ValueError):
        return "0.0000"

def mask_wallet_destination(destination):
    destination = str(destination or "").strip()
    if not destination:
        return "Not set"
    if len(destination) <= 8:
        return "••••••"
    return f"{destination[:5]}••••••{destination[-4:]}"

def get_total_withdrawn(uid):
    total = 0.0
    for request in load_withdraw_requests().values():
        if str(request.get("user_id")) != str(uid):
            continue
        if str(request.get("status", "")).lower() != "approved":
            continue
        try:
            total += float(request.get("amount", 0))
        except (TypeError, ValueError):
            continue
    return total

def wallet_method_label(method):
    labels = {
        "BKASH": "bKash",
        "NAGAD": "Nagad",
        "ROCKET": "Rocket",
        "BINANCE": "Binance (BEP20)",
        "BINANCE BEP20": "Binance (BEP20)",
    }
    return labels.get(str(method or "").upper(), "Not set")

def payment_destination_label(method):
    method = str(method or "").upper()
    return "ADDRESS" if "BINANCE" in method or "BEP20" in method else "NUMBER"

def get_minimum_withdraw_amount():
    return float(load_settings().get("min_withdraw", MIN_WITHDRAW))

async def show_wallet_screen(update, context):
    uid = update.effective_user.id
    user_data = get_user(uid)
    stats = get_user_stats(uid)
    method = user_data.get("wallet_method")
    destination = user_data.get("wallet_address")
    minimum = get_minimum_withdraw_amount()
    wallet_text = (
        "👛 <b>My Wallet</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 User ID: <code>{uid}</code>\n"
        f"💰 Balance: <b>{format_wallet_amount(user_data.get('balance', 0))} BDT</b>\n"
        f"📤 Total Withdrawn: <b>{format_wallet_amount(get_total_withdrawn(uid))} BDT</b>\n"
        f"👥 Referrals: <b>{get_referral_count(uid)}</b>\n"
        f"📲 OTP Received: <b>{stats['total_otps']}</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"⚠️ Minimum Withdraw: <b>{minimum:.1f} BDT</b>\n"
        "🎁 Fee: <b>Free 0%</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"💳 Method: <b>{html.escape(wallet_method_label(method))}</b>\n"
        f"📬 Address: <code>{html.escape(mask_wallet_destination(destination))}</code>"
    )
    await update.effective_message.reply_text(
        wallet_text,
        parse_mode="HTML",
        reply_markup=wallet_actions_keyboard(),
    )

async def wallet_address_received(update, context):
    uid = update.effective_user.id
    address = update.message.text.strip()
    if address.upper() == "CANCEL":
        context.user_data["wallet_mode"] = None
        context.user_data["pending_wallet_method"] = None
        await update.message.reply_text("Wallet setup cancelled.", reply_markup=main_keyboard(uid))
        return

    method = context.user_data.get("pending_wallet_method")
    if not method:
        context.user_data["wallet_mode"] = None
        await update.message.reply_text(
            "Wallet setup expired. Open My Wallet and try again.",
            reply_markup=main_keyboard(uid),
        )
        return

    if method == "BINANCE BEP20":
        valid = bool(re.fullmatch(r"0x[a-fA-F0-9]{40}", address))
        expected = "Send a valid BEP20 (BSC) address starting with 0x and containing 40 hexadecimal characters."
    else:
        valid = is_valid_bangladesh_number(address)
        expected = "Send a valid Bangladesh wallet number, for example 017XXXXXXXX."

    if not valid:
        await update.message.reply_text(
            f"⚠️ Invalid wallet destination.\n\n{expected}\n\nSend CANCEL to stop.",
            reply_markup=cancel_keyboard(),
        )
        return

    data = load_data()
    user_key = str(uid)
    user_data = data.setdefault(user_key, {
        "user_id": user_key,
        "balance": 0.0,
        "total_numbers": 0,
        "referral_count": 0,
    })
    user_data["wallet_method"] = method
    user_data["wallet_address"] = address
    save_data(data)
    context.user_data["wallet_mode"] = None
    context.user_data["pending_wallet_method"] = None

    await update.message.reply_text(
        "✅ <b>Wallet destination saved.</b>",
        parse_mode="HTML",
        reply_markup=main_keyboard(uid),
    )
    await show_wallet_screen(update, context)

async def withdraw_method_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    uid = update.effective_user.id

    if text == "CANCEL":
        context.user_data["withdraw_mode"] = None
        await update.message.reply_text("❌ WITHDRAW CANCELLED", reply_markup=main_keyboard(uid))
        return

    method_map = {"BKASH": "BKASH", "NAGAD": "NAGAD", "ROCKET": "ROCKET", "BINANCE": "BINANCE"}
    if text in method_map:
        balance = get_user(uid)['balance']
        context.user_data["withdraw_method"] = method_map[text]
        context.user_data["withdraw_mode"] = "amount"
        msg = (
            f"<blockquote>💸 SEND YOUR AMOUNT!\n"
            f"💵 TOTAL BALANCE: {format_balance(balance)} BDT</blockquote>\n\n"
            f"<blockquote>📉 MINIMUM WITHDRAW {load_settings().get('min_withdraw', MIN_WITHDRAW)} BDT</blockquote>"
        )
        await update.message.reply_text(msg, parse_mode="HTML", reply_markup=cancel_keyboard())
    else:
        await update.message.reply_text("⚠️ PLEASE SELECT A VALID PAYMENT METHOD!", reply_markup=withdraw_method_keyboard())

async def withdraw_amount_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    uid = update.effective_user.id

    if text.upper() == "CANCEL":
        context.user_data["withdraw_mode"] = None
        await update.message.reply_text("❌ WITHDRAW CANCELLED", reply_markup=main_keyboard(uid))
        return

    try:
        amount = float(text)
    except (TypeError, ValueError):
        await update.message.reply_text("⚠️ PLEASE SEND A VALID AMOUNT!", reply_markup=cancel_keyboard())
        return

    balance = float(get_user(uid).get("balance", 0) or 0)
    _min_wd = get_minimum_withdraw_amount()
    if not (amount > 0 and amount < float("inf")):
        await update.message.reply_text("⚠️ PLEASE SEND A VALID AMOUNT!", reply_markup=cancel_keyboard())
        return
    if amount < _min_wd or amount > MAX_WITHDRAW:
        await update.message.reply_text(f"📉 MIN: {_min_wd} BDT | MAX: {MAX_WITHDRAW} BDT", reply_markup=cancel_keyboard())
        return
    if amount > balance:
        await update.message.reply_text("🚫 INSUFFICIENT BALANCE!", reply_markup=cancel_keyboard())
        return

    user_data = get_user(uid)
    method = user_data.get("wallet_method")
    destination = user_data.get("wallet_address")
    if not method or not destination:
        context.user_data["withdraw_mode"] = None
        await update.message.reply_text(
            "⚠️ Set a wallet destination before requesting a withdrawal.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("💳 SET WALLET", callback_data="wallet_set", style="primary")
            ]]),
        )
        return

    payment_id = generate_payment_id()
    context.user_data["temp_withdraw"] = {
        "method": method,
        "amount": amount,
        "number": destination,
        "payment_id": payment_id,
    }
    context.user_data["withdraw_amount"] = amount
    context.user_data["withdraw_mode"] = None
    destination_type = payment_destination_label(method)
    display_method = html.escape(wallet_method_label(method))
    display_destination = html.escape(destination)
    await update.message.reply_text(
        "✨ <b>CONFIRM WITHDRAWAL DETAILS</b>\n\n"
        f"<blockquote>📝 METHOD: <b>{display_method}</b>\n"
        f"📬 {destination_type}: <code>{display_destination}</code>\n"
        f"💰 AMOUNT: <code>{format_balance(amount)} BDT</code>\n\n"
        "✅ Confirm to submit or cancel.</blockquote>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("❌ CANCEL", callback_data="withdraw_cancel", style="danger"),
            InlineKeyboardButton("✅ CONFIRM", callback_data="withdraw_confirm", style="success"),
        ]]),
    )

async def withdraw_number_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    uid = update.effective_user.id

    if text == "CANCEL":
        context.user_data["withdraw_mode"] = None
        await update.message.reply_text("❌ WITHDRAW CANCELLED", reply_markup=main_keyboard(uid))
        return

    if not is_valid_bangladesh_number(text):
        await update.message.reply_text("⚠️ PLEASE SEND VALID NUMBER! 017XXXXXXXX", reply_markup=cancel_keyboard())
        return

    method = context.user_data.get("withdraw_method")
    amount = context.user_data.get("withdraw_amount")
    payment_number = text
    payment_id = generate_payment_id()

    context.user_data["temp_withdraw"] = {
        "method": method, "amount": amount,
        "number": payment_number, "payment_id": payment_id
    }

    msg = (
        "✨ <b>YOUR PAYMENT DETAILS!</b> ✨\n\n"
        f"<blockquote>📝 METHOD: {method}\n"
        f"📞 NUMBER: {payment_number}\n\n"
        f"✅ CORRECT → CONFIRM\n❌ WRONG → CANCEL</blockquote>"
    )
    await update.message.reply_text(
        msg, parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("❌ CANCEL", callback_data="withdraw_cancel", style="danger"),
            InlineKeyboardButton("✅ CONFIRM", callback_data="withdraw_confirm", style="success")
        ]])
    )

async def process_withdraw_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    await query.answer()

    temp_data = context.user_data.get("temp_withdraw")
    if not temp_data:
        await query.message.reply_text("⚠️ SESSION EXPIRED.", reply_markup=main_keyboard(uid))
        return

    method = temp_data["method"]
    amount = temp_data["amount"]
    payment_number = temp_data["number"]
    payment_id = temp_data["payment_id"]

    wr = load_withdraw_requests()
    if str(payment_id) in wr:
        context.user_data["temp_withdraw"] = None
        await query.message.edit_text("⚠️ This withdrawal request was already submitted.")
        return
    if float(amount) > float(get_user(uid).get("balance", 0) or 0):
        context.user_data["temp_withdraw"] = None
        await query.message.edit_text("🚫 Insufficient balance. Please check your wallet.")
        return

    new_balance = await update_db_balance(uid, -amount)
    wr[str(payment_id)] = {
        "user_id": uid, "method": method, "amount": amount,
        "number": payment_number, "payment_id": payment_id,
        "destination": payment_number,
        "destination_type": payment_destination_label(method),
        "status": "pending", "timestamp": datetime.now().isoformat()
    }
    save_withdraw_requests(wr)

    await query.message.edit_text(
        f"✅ <b>WITHDRAWAL REQUEST SUBMITTED</b> ✅\n\n"
        f"<blockquote>📝 METHOD: <code>{html.escape(wallet_method_label(method))}</code>\n"
        f"📬 {payment_destination_label(method)}: <code>{html.escape(payment_number)}</code>\n"
        f"💰 AMOUNT: <code>{format_balance(amount)} BDT</code>\n"
        f"🆔 ID: <code>{payment_id}</code></blockquote>",
        parse_mode="HTML",
        reply_markup=None,
    )
    await context.bot.send_message(uid, "🎉 <b>WITHDRAW REQUEST SUBMITTED!</b>", parse_mode="HTML", reply_markup=main_keyboard(uid))

    admin_msg = (
        f"✅ <b>NEW WITHDRAWAL REQUEST</b>\n\n"
        f"<blockquote>🆔 USER: <code>{uid}</code>\n"
        f"📝 METHOD: <code>{html.escape(wallet_method_label(method))}</code>\n"
        f"📬 {payment_destination_label(method)}: <code>{html.escape(payment_number)}</code>\n"
        f"💰 AMOUNT: <code>{format_balance(amount)} BDT</code>\n"
        f"🆔 ID: <code>{payment_id}</code></blockquote>"
    )
    admin_kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("❌ REJECT", callback_data=f"admin_reject_{payment_id}", style="danger"),
        InlineKeyboardButton("✅ APPROVE", callback_data=f"admin_approve_{payment_id}", style="success")
    ]])
    for admin_id in ADMINS:
        try:
            await context.bot.send_message(admin_id, admin_msg, parse_mode="HTML", reply_markup=admin_kb)
        except Exception as e:
            print(f"Admin notify fail {admin_id}: {e}")

    context.user_data["temp_withdraw"] = None
    context.user_data["withdraw_mode"] = None

async def process_withdraw_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    await query.answer()
    context.user_data["temp_withdraw"] = None
    context.user_data["withdraw_mode"] = None
    await query.message.edit_text("❌ WITHDRAW CANCELLED")
    await context.bot.send_message(uid, "🔹 PLEASE USE THE BUTTONS BELOW:", reply_markup=main_keyboard(uid))

# ==================== ADMIN PANEL - WITHDRAW APPROVAL ====================

async def admin_approve_withdraw(update, context, payment_id):
    query = update.callback_query
    await query.answer()
    wr = load_withdraw_requests()
    if payment_id not in wr:
        await query.message.reply_text("⚠️ REQUEST NOT FOUND!")
        return
    rd = wr[payment_id]
    if str(rd.get("status", "")).lower() != "pending":
        await query.message.reply_text("⚠️ This withdrawal request is already finalized.")
        return
    uid = rd["user_id"]
    method = rd["method"]
    amount = rd["amount"]
    payment_number = rd.get("destination") or rd.get("number", "")
    wr[payment_id]["status"] = "approved"
    save_withdraw_requests(wr)

    try:
        await context.bot.send_message(
            uid,
            f"🎉 <b>WITHDRAWAL APPROVED!</b>\n\n"
            f"<blockquote>📝 METHOD: <code>{html.escape(wallet_method_label(method))}</code>\n"
            f"📬 {payment_destination_label(method)}: <code>{html.escape(payment_number)}</code>\n"
            f"💰 AMOUNT: <code>{format_balance(amount)} BDT</code></blockquote>",
            parse_mode="HTML"
        )
    except:
        pass
    await query.message.edit_text(f"✅ APPROVED | User: {uid} | Amount: {format_balance(amount)} BDT")

async def admin_reject_withdraw(update, context, payment_id):
    query = update.callback_query
    await query.answer()
    wr = load_withdraw_requests()
    if payment_id not in wr:
        await query.message.reply_text("⚠️ REQUEST NOT FOUND!")
        return
    rd = wr[payment_id]
    if str(rd.get("status", "")).lower() != "pending":
        await query.message.reply_text("⚠️ This withdrawal request is already finalized.")
        return
    uid = int(rd["user_id"])
    amount = float(rd["amount"])
    if amount <= 0:
        await query.message.reply_text("⚠️ Invalid request amount; please review it manually.")
        return
    if not rd.get("refund_issued"):
        await update_db_balance(uid, amount)
        wr[payment_id]["refund_issued"] = True
    wr[payment_id]["status"] = "rejected"
    save_withdraw_requests(wr)

    try:
        await context.bot.send_message(
            uid,
            "❌ <b>WITHDRAWAL REQUEST REJECTED</b>\n"
            f"💰 <b>{format_balance(amount)} BDT</b> has been refunded to your wallet.",
            parse_mode="HTML",
        )
    except:
        pass
    await query.message.edit_text(f"❌ REJECTED + REFUNDED | User: {uid} | Amount: {format_balance(amount)} BDT")

# ==================== ADMIN PANEL - BALANCE MANAGEMENT ====================

async def admin_add_balance_start(update, context):
    context.user_data["add_balance_mode"] = True
    context.user_data["remove_balance_mode"] = False
    await update.message.reply_text("💰 SEND USER ID TO ADD BALANCE:")

async def admin_remove_balance_start(update, context):
    context.user_data["remove_balance_mode"] = True
    context.user_data["add_balance_mode"] = False
    await update.message.reply_text("💸 SEND USER ID TO REMOVE BALANCE:")

async def process_add_balance_user(update, context):
    uid_to_add = update.message.text.strip()
    if not uid_to_add.isdigit():
        await update.message.reply_text("❌ INVALID USER ID!")
        return
    uid_to_add_int = int(uid_to_add)
    if not user_exists(uid_to_add_int):
        await update.message.reply_text("❌ USER NOT FOUND!")
        context.user_data["add_balance_mode"] = False
        return
    context.user_data["pending_add_user"] = uid_to_add_int
    await update.message.reply_text("💵 SEND AMOUNT TO ADD:")

async def process_remove_balance_user(update, context):
    uid_to_remove = update.message.text.strip()
    if not uid_to_remove.isdigit():
        await update.message.reply_text("❌ INVALID USER ID!")
        return
    uid_to_remove_int = int(uid_to_remove)
    if not user_exists(uid_to_remove_int):
        await update.message.reply_text("❌ USER NOT FOUND!")
        context.user_data["remove_balance_mode"] = False
        return
    context.user_data["pending_remove_user"] = uid_to_remove_int
    await update.message.reply_text("💸 SEND AMOUNT TO REMOVE:")

async def process_add_balance_amount(update, context):
    try:
        amount = float(update.message.text.strip())
        if amount <= 0: raise ValueError
    except:
        await update.message.reply_text("❌ INVALID AMOUNT!")
        return
    uid = context.user_data.get("pending_add_user")
    if not uid:
        context.user_data["add_balance_mode"] = False
        await update.message.reply_text("⚠️ SESSION EXPIRED.")
        return
    old_balance = get_user(uid).get("balance", 0)
    new_balance = await update_db_balance(uid, amount)
    await update.message.reply_text(
        f"✅ **ADD BALANCE SUCCESSFUL**\n🆔 USER: `{uid}`\n"
        f"💰 ADDED: `{format_balance(amount)} BDT`\n"
        f"📈 NEW BALANCE: `{format_balance(new_balance)} BDT`",
        parse_mode="Markdown"
    )
    try:
        await context.bot.send_message(uid, f"🎉 ADMIN ADDED `{format_balance(amount)} BDT` TO YOUR ACCOUNT!\n💵 NEW BALANCE: `{format_balance(new_balance)} BDT`", parse_mode="Markdown")
    except:
        pass
    context.user_data["add_balance_mode"] = False
    context.user_data["pending_add_user"] = None

async def process_remove_balance_amount(update, context):
    try:
        amount = float(update.message.text.strip())
        if amount <= 0: raise ValueError
    except:
        await update.message.reply_text("❌ INVALID AMOUNT!")
        return
    uid = context.user_data.get("pending_remove_user")
    if not uid:
        context.user_data["remove_balance_mode"] = False
        await update.message.reply_text("⚠️ SESSION EXPIRED.")
        return
    old_balance = get_user(uid).get("balance", 0)
    if amount > old_balance:
        await update.message.reply_text(f"❌ INSUFFICIENT BALANCE! Current: {format_balance(old_balance)} BDT")
        context.user_data["remove_balance_mode"] = False
        context.user_data["pending_remove_user"] = None
        return
    new_balance = await update_db_balance(uid, -amount)
    await update.message.reply_text(
        f"✅ **REMOVE BALANCE SUCCESSFUL**\n🆔 USER: `{uid}`\n"
        f"💸 REMOVED: `{format_balance(amount)} BDT`\n"
        f"📉 NEW BALANCE: `{format_balance(new_balance)} BDT`",
        parse_mode="Markdown"
    )
    try:
        await context.bot.send_message(uid, f"⚠️ ADMIN REMOVED `{format_balance(amount)} BDT` FROM YOUR ACCOUNT!\n💵 NEW BALANCE: `{format_balance(new_balance)} BDT`", parse_mode="Markdown")
    except:
        pass
    context.user_data["remove_balance_mode"] = False
    context.user_data["pending_remove_user"] = None

# ==================== ADMIN PANEL - BAN/UNBAN ====================

async def admin_ban_user_start(update, context):
    context.user_data["admin_ban_mode"] = True
    context.user_data["admin_unban_mode"] = False
    await update.message.reply_text("🚫 SEND TELEGRAM ID TO BAN USER:")

async def admin_unban_user_start(update, context):
    context.user_data["admin_unban_mode"] = True
    context.user_data["admin_ban_mode"] = False
    await update.message.reply_text("🔓 SEND TELEGRAM ID TO UNBAN USER:")

async def process_ban_user(update, context):
    uid_to_ban = update.message.text.strip()
    if not uid_to_ban.isdigit():
        await update.message.reply_text("❌ INVALID USER ID!")
        return
    uid_to_ban_int = int(uid_to_ban)
    if not user_exists(uid_to_ban_int):
        await update.message.reply_text("❌ USER NOT FOUND!")
        context.user_data["admin_ban_mode"] = False
        return
    if is_user_banned(uid_to_ban_int):
        await update.message.reply_text("⚠️ USER IS ALREADY BANNED!")
        context.user_data["admin_ban_mode"] = False
        return
    ban_user(uid_to_ban_int)
    try:
        await context.bot.send_message(uid_to_ban_int, "🚫 **YOU HAVE BEEN BANNED**\n📞 Contact support.", parse_mode="Markdown")
    except:
        pass
    await update.message.reply_text(f"✅ USER `{uid_to_ban}` BANNED!", parse_mode="Markdown", reply_markup=system_config_keyboard())
    context.user_data["admin_ban_mode"] = False

async def process_unban_user(update, context):
    uid_to_unban = update.message.text.strip()
    if not uid_to_unban.isdigit():
        await update.message.reply_text("❌ INVALID USER ID!")
        return
    uid_to_unban_int = int(uid_to_unban)
    if not is_user_banned(uid_to_unban_int):
        await update.message.reply_text("⚠️ THIS USER IS NOT BANNED!")
        context.user_data["admin_unban_mode"] = False
        return
    unban_user(uid_to_unban_int)
    try:
        await context.bot.send_message(uid_to_unban_int, "✅ **YOU HAVE BEEN UNBANNED!** Use /start", parse_mode="Markdown")
    except:
        pass
    await update.message.reply_text(f"✅ USER `{uid_to_unban}` UNBANNED!", parse_mode="Markdown", reply_markup=system_config_keyboard())
    context.user_data["admin_unban_mode"] = False

async def show_banned_users_list(update, context):
    banned_list = load_banned_users()
    if not banned_list:
        await update.message.reply_text("📜 NO BANNED USERS.", reply_markup=system_config_keyboard())
        return
    text = "📜 **BANNED USER LIST**\n━━━━━━━━━━━━━━━━━━━━\n\n"
    for i, uid in enumerate(banned_list, 1):
        text += f"{i}. `{uid}`\n"
    text += f"\n📊 Total: {len(banned_list)}"
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=system_config_keyboard())

# ==================== MESSAGE HANDLER SECTION ====================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    uid = update.effective_user.id
    text = update.message.text.strip()

    if not is_admin(uid):
        if not await check_force_join(update, context):
            return

    menu_actions = {
        "🆓 FREE NUMBER", "FREE NUMBER", "GET NUMBER",
        "📂 STOCK", "STOCK",
        "💳 BALANCE", "BALANCE", "MY WALLET", "👛 MY WALLET",
        "👋 REFER", "REFER", "REFER AND EARN",
        "💬 LIVE SUPPORT", "LIVE SUPPORT", "SUPPORT",
        "SEARCH OTP", "GET 2FA", "PROFILE", "LEADERBOARD", "ADMIN PANEL",
    }
    if text in menu_actions and context.user_data.get("mode") in {
        "custom_range", "search_otp", "get_2fa"
    }:
        context.user_data["mode"] = None

    # Wallet setup flow
    if context.user_data.get("wallet_mode") == "address":
        await wallet_address_received(update, context)
        return
    if context.user_data.get("wallet_mode") == "select_method":
        if text.upper() == "CANCEL":
            context.user_data["wallet_mode"] = None
            context.user_data["pending_wallet_method"] = None
            await update.message.reply_text("Wallet setup cancelled.", reply_markup=main_keyboard(uid))
        else:
            await update.message.reply_text(
                "Choose a wallet method using the buttons below:",
                reply_markup=wallet_method_selection_keyboard(),
            )
        return

    # Withdraw flow
    if context.user_data.get("withdraw_mode") == "select_method":
        await withdraw_method_selected(update, context)
        return
    if context.user_data.get("withdraw_mode") == "amount":
        await withdraw_amount_received(update, context)
        return
    if context.user_data.get("withdraw_mode") == "number":
        await withdraw_number_received(update, context)
        return

    # Admin balance
    if context.user_data.get("add_balance_mode") and is_admin(uid):
        if context.user_data.get("pending_add_user"):
            await process_add_balance_amount(update, context)
        else:
            await process_add_balance_user(update, context)
        return
    if context.user_data.get("remove_balance_mode") and is_admin(uid):
        if context.user_data.get("pending_remove_user"):
            await process_remove_balance_amount(update, context)
        else:
            await process_remove_balance_user(update, context)
        return

    # Admin ban/unban
    if context.user_data.get("admin_ban_mode") and is_admin(uid):
        await process_ban_user(update, context)
        return
    if context.user_data.get("admin_unban_mode") and is_admin(uid):
        await process_unban_user(update, context)
        return

    # EMOJI EDIT INPUT
    if context.user_data.get("emoji_edit_key") and is_admin(uid):
        key = context.user_data.pop("emoji_edit_key")
        inp = text.strip()
        emoji_id = ""
        fallback = ""

        if ":" in inp:
            parts = inp.split(":", 1)
            if parts[1].strip().isdigit():
                fallback = parts[0].strip()
                emoji_id = parts[1].strip()
            else:
                fallback = inp
        elif inp.isdigit() and len(inp) >= 10:
            emoji_id = inp
            fallback = FALLBACK_EMOJI_MAP.get(key, "⭐")
        else:
            fallback = inp

        s = load_settings()
        if "custom_emojis" not in s:
            s["custom_emojis"] = {}
        s["custom_emojis"][key] = {"id": emoji_id, "fallback": fallback}
        save_settings(s)

        if emoji_id:
            preview = f'<tg-emoji emoji-id="{emoji_id}">{fallback or "⭐"}</tg-emoji>'
        else:
            preview = fallback

        page = context.user_data.pop("emoji_edit_page", 0)
        kb = get_emoji_page_keyboard(page)
        await update.message.reply_text(
            f"✅ <b>Emoji আপডেট হয়েছে!</b>\n\n"
            f"<blockquote>🔑 Key: <code>{key}</code>\n"
            f"👁 Preview: {preview}</blockquote>\n\n"
            f"আরও emoji কাস্টমাইজ করুন:",
            parse_mode="HTML",
            reply_markup=kb
        )
        return

    # CUSTOM RANGE — user sent a range text
    if context.user_data.get("mode") == "custom_range":
        context.user_data["mode"] = None
        range_text = text.strip().upper()
        if not re.search(r'\d', range_text):
            await update.message.reply_text(
                "❌ <b>INVALID RANGE!</b>\n\n"
                "<blockquote>সঠিক উদাহরণ: <code>234XXX</code></blockquote>",
                parse_mode="HTML",
                reply_markup=main_keyboard(uid)
            )
            return
        await request_queue.put({
            'type': 'process_numbers',
            'update': update,
            'context': context,
            'range_text': range_text,
            'count': 1
        })
        return

    # Ban check
    if not is_admin(uid) and is_user_banned(uid):
        await update.message.reply_text("🚫 YOU ARE BANNED 🚫", reply_markup=main_keyboard(uid))
        return

    # Cancel
    if text == "CANCEL":
        context.user_data.clear()
        await update.message.reply_text("❌ CANCELLED", reply_markup=main_keyboard(uid))
        return

    # Main menu buttons
    if text == "Stats":
        stats = get_user_stats(uid)
        user_data = get_user(uid)
        stats_text = (
            f"📊 <b>YOUR STATS</b>\n\n"
            f"✨ <b>TODAY</b>\n"
            f"<blockquote>📱 Numbers: {stats['today_numbers']}\n🔑 OTPs: {stats['today_otps']}</blockquote>\n\n"
            f"🔥 <b>LAST 7 DAYS</b>\n"
            f"<blockquote>📱 Numbers: {stats['last7d_numbers']}\n🔑 OTPs: {stats['last7d_otps']}</blockquote>\n\n"
            f"🌐 <b>ALL TIME</b>\n"
            f"<blockquote>📱 Numbers: {stats['total_numbers']}\n🔑 OTPs: {stats['total_otps']}</blockquote>\n\n"
            f"💰 <b>Balance: {format_balance(user_data.get('balance', 0))} BDT</b>"
        )
        await update.message.reply_text(stats_text, parse_mode="HTML")
        return

    if text == "Live Traffic":
        try:
            all_logs = load_data(ACTIVITY_LOGS_FILE)
            otp_logs = [log for log in all_logs if log.get('action') == "OTP_RECEIVED"]
            recent = otp_logs[-10:] if len(otp_logs) >= 10 else otp_logs
            recent = list(reversed(recent))
            if not recent:
                await update.message.reply_text("📡 <b>LIVE TRAFFIC</b>\n\nNo recent OTP activity.", parse_mode="HTML")
                return
            msg = "📡 <b>LIVE TRAFFIC — RECENT OTPs</b>\n━━━━━━━━━━━━━━━━━━━━\n\n"
            for log in recent:
                try:
                    dt_obj = datetime.fromisoformat(log['timestamp'])
                    d = log.get('details', {})
                    num = d.get('number', 'N/A')
                    otp = d.get('otp', 'N/A')
                    app = d.get('app', '')
                    time_str = dt_obj.strftime('%I:%M %p')
                    msg += f"🔑 <code>{otp}</code>  📱 <code>{num}</code>  ⏰ {time_str}\n"
                    if app:
                        msg += f"   📲 {app}\n"
                except:
                    continue
            await update.message.reply_text(msg, parse_mode="HTML")
        except Exception as e:
            await update.message.reply_text("📡 <b>LIVE TRAFFIC</b>\n\nNo activity data found.", parse_mode="HTML")
        return

    if text == "Help":
        help_text = (
            "❓ <b>HELP & SUPPORT</b>\n\n"
            "<blockquote>📱 <b>Get Number</b> — Get a virtual number for OTP verification</blockquote>\n\n"
            "<blockquote>💰 <b>Balance</b> — Check your current balance & withdraw</blockquote>\n\n"
            "<blockquote>📊 <b>Stats</b> — View your usage statistics</blockquote>\n\n"
            "<blockquote>📡 <b>Live Traffic</b> — See recent OTP activity</blockquote>\n\n"
            "💬 Need help? Contact support below 👇"
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 SUPPORT", url=SUPPORT_LINK, style="primary")],
            [InlineKeyboardButton("👨‍💻 DEVELOPER", url=DEVELOPER_LINK, style="danger")]
        ])
        await update.message.reply_text(help_text, reply_markup=keyboard, parse_mode="HTML")
        return

    if text == "PROFILE":
        user_data = get_user(uid)
        stats = get_user_stats(uid)
        user = update.effective_user
        full_name = html.escape(user.full_name)
        username = html.escape(user.username or "No username")
        profile_text = (
            f"👤 <b>YOUR PROFILE</b>\n\n"
            f"<blockquote>🏷️ NAME: <b>{full_name}</b></blockquote>\n"
            f"<blockquote>🆔 USERNAME: @{username}</blockquote>\n"
            f"<blockquote>🗝️ TELEGRAM ID: <code>{uid}</code></blockquote>\n\n"
            f"<blockquote>💵 BALANCE: <b>{format_balance(user_data.get('balance', 0))} BDT</b></blockquote>\n\n"
            f"✨ <b>TODAY</b>\n"
            f"<blockquote>📱 NUMBERS: {stats['today_numbers']}\n🔑 OTPS: {stats['today_otps']}</blockquote>\n\n"
            f"🔥 <b>LAST 7 DAYS</b>\n"
            f"<blockquote>📱 NUMBERS: {stats['last7d_numbers']}\n🔑 OTPS: {stats['last7d_otps']}</blockquote>\n\n"
            f"🌐 <b>ALL TIME</b>\n"
            f"<blockquote>📱 NUMBERS: {stats['total_numbers']}\n🔑 OTPS: {stats['total_otps']}</blockquote>"
        )
        await update.message.reply_text(profile_text, parse_mode="HTML")
        return

    if text.strip().upper() in (
        "BALANCE", "💳 BALANCE", "MY WALLET", "👛 MY WALLET", "WALLET"
    ):
        await show_wallet_screen(update, context)
        return

    if text in ("REFER AND EARN", "REFER", "👋 REFER"):
        await refer_command(update, context)
        return

    if text in ("STOCK", "📂 STOCK"):
        await show_live_stock(update, context)
        return

    # SEARCH OTP
    if text == "SEARCH OTP":
        context.user_data["mode"] = "search_otp"
        await update.message.reply_text("🔍 **ENTER THE NUMBER TO SEARCH OTP:**", parse_mode="Markdown")
        return

    if context.user_data.get("mode") == "search_otp":
        context.user_data["mode"] = None
        await request_queue.put({'type': 'search_otp', 'update': update, 'context': context, 'target_num': normalize_number(text)})
        return

    # GET 2FA
    if text == "GET 2FA":
        await get_2fa_code(update, context)
        return

    # GET NUMBER
    if text in ("GET NUMBER", "Get Number", "FREE NUMBER", "🆓 FREE NUMBER"):
        await show_app_selection(update, context)
        return

    if context.user_data.get("mode") == "get_2fa":
        await process_2fa_key(update, context)
        return

    # LEADERBOARD
    if text == "LEADERBOARD":
        await leaderboard_command(update, context)
        return

    # SUPPORT BUTTON HANDLER
    if text in ("SUPPORT", "LIVE SUPPORT", "💬 LIVE SUPPORT"):
        support_text = "💬 SUPPORT 🎧\n\nCLICK THE BUTTON BELOW TO CONTACT SUPPORT 📩"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 SUPPORT", url=SUPPORT_LINK, style="primary")],
            [InlineKeyboardButton("👨‍💻 DEVELOPER BY", url=DEVELOPER_LINK, style="danger")]
        ])
        await update.message.reply_text(support_text, reply_markup=keyboard, parse_mode="Markdown")
        return

    # Admin panel
    if text == "ADMIN PANEL" and is_admin(uid):
        context.user_data["admin_mode"] = "main"
        await update.message.reply_text(
            "⌬━━━━━━━━━━━━━━━━━━━━⌬\n   WELCOME ADMIN PANEL\n⌬━━━━━━━━━━━━━━━━━━━━⌬",
            reply_markup=admin_main_keyboard()
        )
        return

    if text == "BACK TO MAIN" and context.user_data.get("admin_mode"):
        context.user_data["admin_mode"] = None
        await update.message.reply_text("🔙 Back to main menu.", reply_markup=main_keyboard(uid))
        return

    if text == "BACK TO ADMIN":
        context.user_data["user_management_mode"] = None
        context.user_data["system_config_mode"] = None
        context.user_data["admin_mode"] = "main"
        await update.message.reply_text("🔙 Back to admin panel.", reply_markup=admin_main_keyboard())
        return

    if text == "USER MANAGEMENT" and context.user_data.get("admin_mode") == "main" and is_admin(uid):
        context.user_data["user_management_mode"] = "main"
        await update.message.reply_text("👥 User Management:", reply_markup=user_management_keyboard())
        return

    if text == "SYSTEM CONFIGURATION" and context.user_data.get("admin_mode") == "main" and is_admin(uid):
        context.user_data["system_config_mode"] = "main"
        await update.message.reply_text("⚙️ System Configuration:", reply_markup=system_config_keyboard())
        return

    if text == "TODAY ALL STATUS" and context.user_data.get("system_config_mode") == "main" and is_admin(uid):
        t_n, t_o, s_n, s_o, tot_n, tot_o = get_global_system_stats()
        msg = (
            f"📊 <b>SYSTEM STATUS</b>\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"✨ <b>TODAY</b>\n📱 NUMBERS: {t_n}\n🔑 OTPS: {t_o}\n\n"
            f"🔥 <b>LAST 7 DAYS</b>\n📱 NUMBERS: {s_n}\n🔑 OTPS: {s_o}\n\n"
            f"🌐 <b>ALL TIME</b>\n📱 NUMBERS: {tot_n}\n🔑 OTPS: {tot_o}"
        )
        await update.message.reply_text(msg, parse_mode="HTML")
        return

    if text == "USER STATUS CHECK" and is_admin(uid):
        context.user_data["mode"] = "input_user_id"
        await update.message.reply_text("🔍 ENTER TELEGRAM ID:", reply_markup=cancel_keyboard())
        return

    if context.user_data.get("mode") == "input_user_id" and is_admin(uid):
        target_uid = text.strip()
        if not target_uid.isdigit():
            await update.message.reply_text("❌ INVALID ID!")
            return
        context.user_data["mode"] = None
        stats = get_user_stats(target_uid)
        msg = (
            f"👤 <b>USER STATUS</b> — <code>{target_uid}</code>\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"✨ TODAY: 📱 {stats['today_numbers']} | 🔑 {stats['today_otps']}\n"
            f"🔥 7 DAYS: 📱 {stats['last7d_numbers']} | 🔑 {stats['last7d_otps']}\n"
            f"🌐 ALL TIME: 📱 {stats['total_numbers']} | 🔑 {stats['total_otps']}"
        )
        await update.message.reply_text(
            msg, parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("📂 CHECK ALL DATA", callback_data=f"full_logs_{target_uid}", style="primary")
            ]])
        )
        return

    if text == "ALL USER ID" and context.user_data.get("user_management_mode") == "main" and is_admin(uid):
        users = get_all_users()
        if users:
            content = "\n".join(f"{i}. {u}" for i, u in enumerate(users, 1))
            f = io.BytesIO(content.encode()); f.name = f"ALL_USERS_{len(users)}.txt"
            await update.message.reply_document(document=f, caption=f"👥 Total Users: {len(users)}", reply_markup=user_management_keyboard())
        else:
            await update.message.reply_text("No users found.", reply_markup=user_management_keyboard())
        return

    if text == "ALL USER BALANCE" and context.user_data.get("user_management_mode") == "main" and is_admin(uid):
        user_db = load_data(USER_DATA_FILE)
        if user_db:
            total_bal = sum(v.get("balance", 0) for v in user_db.values())
            lines = [f"{i}. {uid_}: {v.get('balance', 0):.2f} BDT" for i, (uid_, v) in enumerate(user_db.items(), 1)]
            content = f"💰 TOTAL BALANCE: {total_bal:.2f} BDT\n\n" + "\n".join(lines)
            f = io.BytesIO(content.encode()); f.name = f"BALANCES_{total_bal:.0f}.txt"
            await update.message.reply_document(document=f, caption=f"💵 Total Balance: {total_bal:.2f} BDT", reply_markup=user_management_keyboard())
        else:
            await update.message.reply_text("No data.", reply_markup=user_management_keyboard())
        return

    if text == "BAN USER LIST" and is_admin(uid):
        await show_banned_users_list(update, context)
        return

    if text == "BAN USER" and context.user_data.get("system_config_mode") == "main" and is_admin(uid):
        await admin_ban_user_start(update, context)
        return

    if text == "UNBAN USER" and context.user_data.get("system_config_mode") == "main" and is_admin(uid):
        await admin_unban_user_start(update, context)
        return

    if text == "ADD BALANCE" and context.user_data.get("system_config_mode") == "main" and is_admin(uid):
        await admin_add_balance_start(update, context)
        return

    if text == "REMOVE BALANCE" and context.user_data.get("system_config_mode") == "main" and is_admin(uid):
        await admin_remove_balance_start(update, context)
        return

    # ==================== LIVE CONSOLE TOGGLE BUTTON HANDLER ====================
    if (text.startswith("LIVE CONSOLE") or text in ("LIVE CONSOLE ON", "LIVE CONSOLE OFF")) and is_admin(uid):
        s = load_settings()
        cur_status = s.get("live_console", False)
        new_status = not cur_status
        s["live_console"] = new_status
        save_settings(s)

        status_str = "ON 🟢" if new_status else "OFF 🔴"
        desc = (
            "✅ <b>Live Console এখন সক্রিয় (ON)!</b>\n\n"
            "<blockquote>📡 API: <code>https://yesms.online/api/console_data</code>\n"
            "⏱️ প্রতি ২ মিনিট পর পর সর্বশেষ ৩০টি ওটিপি চেক করা হবে।\n"
            "⏳ প্রতি ২ সেকেন্ডে ১টি করে ওটিপি গ্রুপে পোস্ট হবে।\n"
            "🎨 ডিজাইন: আপনার বটের স্ট্যান্ডার্ড গ্রুপ পোস্টের মতোই।</blockquote>"
            if new_status else
            "🔴 <b>Live Console এখন বন্ধ (OFF)!</b>\n\n"
            "<blockquote>কনসোল থেকে ওটিপি গ্রুপে আর অটো-পোস্ট হবে না।</blockquote>"
        )
        await update.message.reply_text(
            f"📡 <b>LIVE CONSOLE: {status_str}</b>\n━━━━━━━━━━━━━━━━━━━━━━\n\n{desc}",
            parse_mode="HTML",
            reply_markup=bot_settings_keyboard()
        )
        return

    # ==================== BROADCAST (TEXT, PHOTO, VIDEO, FILE, ETC.) ====================
    if text == "SEND MESSAGE TO ALL USERS" and is_admin(uid):
        context.user_data["broadcast_mode"] = True
        await update.message.reply_text(
            "📢 <b>ADMIN BROADCAST SYSTEM (PRO)</b>\n\n"
            "💬 আপনি এখন যা পাঠাবেন (Text, Photo, Video, Document, Voice, Audio, Animation, Sticker) – সকল ইউজারের কাছে প্রফেশনাল হেডারসহ চলে যাবে।\n\n"
            "✨ রেঞ্জ (যেমন: 237XXX) থাকলে তা অটোমেটিক ক্লিক-টু-কপি হয়ে যাবে।", 
            parse_mode="HTML", 
            reply_markup=cancel_keyboard()
        )
        return

    if context.user_data.get("broadcast_mode") and is_admin(uid):
        context.user_data["broadcast_mode"] = False
        
        user_db = load_data(USER_DATA_FILE)
        all_uids = list(user_db.keys())
        
        if not all_uids:
            await update.message.reply_text("❌ পাঠানোর জন্য কোনো ইউজার পাওয়া যায়নি!")
            return

        success_ids, fail_ids = [], []
        status_msg = await update.message.reply_text(f"🚀 <b>ব্রডকাস্ট শুরু হয়েছে...</b>\n🎯 টার্গেট: {len(all_uids)} জন ইউজার।", parse_mode="HTML")

        def format_broadcast_caption(caption_text):
            if not caption_text:
                return "<blockquote>📢 <b>ADMIN NOTICE :</b></blockquote>"
            formatted = re.sub(r'(\d{3,}[xX]{3,})', r'<code>\1</code>', str(caption_text))
            return f"<blockquote>📢 <b>ADMIN NOTICE :</b></blockquote>\n\n{formatted}"

        for user_id_str in all_uids:
            try:
                target_id = int(user_id_str)
                if update.message.text:
                    await context.bot.send_message(
                        chat_id=target_id, 
                        text=format_broadcast_caption(update.message.text), 
                        parse_mode="HTML"
                    )
                elif update.message.photo:
                    caption = format_broadcast_caption(update.message.caption) if update.message.caption else None
                    await context.bot.send_photo(
                        chat_id=target_id,
                        photo=update.message.photo[-1].file_id,
                        caption=caption,
                        parse_mode="HTML" if caption else None
                    )
                elif update.message.video:
                    caption = format_broadcast_caption(update.message.caption) if update.message.caption else None
                    await context.bot.send_video(
                        chat_id=target_id,
                        video=update.message.video.file_id,
                        caption=caption,
                        parse_mode="HTML" if caption else None
                    )
                elif update.message.document:
                    caption = format_broadcast_caption(update.message.caption) if update.message.caption else None
                    await context.bot.send_document(
                        chat_id=target_id,
                        document=update.message.document.file_id,
                        caption=caption,
                        parse_mode="HTML" if caption else None
                    )
                elif update.message.audio:
                    caption = format_broadcast_caption(update.message.caption) if update.message.caption else None
                    await context.bot.send_audio(
                        chat_id=target_id,
                        audio=update.message.audio.file_id,
                        caption=caption,
                        parse_mode="HTML" if caption else None
                    )
                elif update.message.voice:
                    caption = format_broadcast_caption(update.message.caption) if update.message.caption else None
                    await context.bot.send_voice(
                        chat_id=target_id,
                        voice=update.message.voice.file_id,
                        caption=caption,
                        parse_mode="HTML" if caption else None
                    )
                elif update.message.animation:
                    caption = format_broadcast_caption(update.message.caption) if update.message.caption else None
                    await context.bot.send_animation(
                        chat_id=target_id,
                        animation=update.message.animation.file_id,
                        caption=caption,
                        parse_mode="HTML" if caption else None
                    )
                elif update.message.sticker:
                    await context.bot.send_sticker(
                        chat_id=target_id,
                        sticker=update.message.sticker.file_id
                    )
                else:
                    try:
                        await context.bot.copy_message(
                            chat_id=target_id,
                            from_chat_id=update.message.chat_id,
                            message_id=update.message.message_id
                        )
                    except:
                        await context.bot.send_message(
                            chat_id=target_id,
                            text="📢 <b>ADMIN NOTICE :</b>\n\nআপনার জন্য একটি নতুন বার্তা আছে।",
                            parse_mode="HTML"
                        )
                success_ids.append(user_id_str)
            except Exception as e:
                print(f"Broadcast fail to {user_id_str}: {e}")
                fail_ids.append(user_id_str)
            
            await asyncio.sleep(0.05)

        report_text = (
            f"✅ <b>ADMIN NOTICE COMPLETE !</b>\n\n"
            f"📊 <b>BROADCAST REPORT:</b>\n\n"
            f"<blockquote>✅ SUCCESSFULLY SENT: {len(success_ids)} USERS !</blockquote>\n"
            f"<blockquote>❌ FAILED TO SEND: {len(fail_ids)} USERS !</blockquote>"
        )
        
        await status_msg.delete()
        await context.bot.send_message(chat_id=uid, text=report_text, parse_mode="HTML", reply_markup=main_keyboard(uid))

        random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        if success_ids:
            s_file = io.BytesIO(("\n".join(success_ids)).encode()); s_file.name = f"SUCCESS_{random_suffix}.txt"
            await context.bot.send_document(chat_id=uid, document=s_file, caption="✅ Success User List")
        if fail_ids:
            f_file = io.BytesIO(("\n".join(fail_ids)).encode()); f_file.name = f"FAILED_{random_suffix}.txt"
            await context.bot.send_document(chat_id=uid, document=f_file, caption="❌ Failed User List")
        
        return

    # BOT SETTINGS NAVIGATION
    if text == "BOT SETTINGS" and context.user_data.get("admin_mode") == "main" and is_admin(uid):
        context.user_data["bot_settings_mode"] = "main"
        context.user_data["zenex_config_mode"] = None
        await update.message.reply_text("⚙️ <b>BOT SETTINGS</b>", parse_mode="HTML", reply_markup=bot_settings_keyboard())
        return

    if text == "BACK TO BOT SETTINGS" and is_admin(uid):
        context.user_data["bot_settings_mode"] = "main"
        context.user_data["zenex_config_mode"] = None
        await update.message.reply_text("⚙️ <b>BOT SETTINGS</b>", parse_mode="HTML", reply_markup=bot_settings_keyboard())
        return

    if text == "ZENEX CONFIG" and context.user_data.get("bot_settings_mode") == "main" and is_admin(uid):
        context.user_data["zenex_config_mode"] = "main"
        await update.message.reply_text("📡 <b>ZENEX PANEL CONFIG</b>", parse_mode="HTML", reply_markup=zenex_config_keyboard())
        return

    if text == "SERVICE MANAGEMENT" and context.user_data.get("admin_mode") == "main" and is_admin(uid):
        context.user_data["service_mgmt_mode"] = "main"
        await update.message.reply_text("🔧 <b>SERVICE MANAGEMENT</b>", parse_mode="HTML", reply_markup=service_management_keyboard())
        return

    # EMOJI SETTINGS NAVIGATION
    if text == "EMOJI SETTINGS" and context.user_data.get("bot_settings_mode") == "main" and is_admin(uid):
        s = load_settings()
        custom_count = len(s.get("custom_emojis", {}))
        kb = get_emoji_page_keyboard(0)
        await update.message.reply_text(
            f"🎨 <b>EMOJI SETTINGS</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"<blockquote>ইউজার প্যানেলের সব emoji এখান থেকে কাস্টমাইজ করুন।\n\n"
            f"✏️ = কাস্টম সেট করা আছে\n"
            f"মোট কাস্টম: <b>{custom_count}টি</b>\n\n"
            f"<b>কোনো emoji key বাটনে ক্লিক করুন।</b></blockquote>",
            parse_mode="HTML",
            reply_markup=kb
        )
        return

    # ADD / REMOVE ADMIN
    if text == "ADD ADMIN" and context.user_data.get("bot_settings_mode") == "main" and is_admin(uid):
        context.user_data["bot_settings_mode"] = "add_admin"
        s = load_settings()
        admin_list = "\n".join(f"• <code>{a}</code>" for a in s.get("admins", []))
        await update.message.reply_text(
            f"➕ <b>ADD ADMIN</b>\n\n<blockquote>Current admins:\n{admin_list}</blockquote>\n\n"
            f"Send the <b>Telegram User ID</b> to add as admin:",
            parse_mode="HTML", reply_markup=cancel_keyboard())
        return

    if context.user_data.get("bot_settings_mode") == "add_admin" and is_admin(uid):
        if not text.lstrip("-").isdigit():
            await update.message.reply_text("❌ Invalid ID! Send a numeric Telegram ID.")
            return
        new_admin_id = int(text)
        s = load_settings()
        admins = s.get("admins", [])
        if new_admin_id in admins:
            await update.message.reply_text("⚠️ This user is already an admin!", reply_markup=bot_settings_keyboard())
        else:
            admins.append(new_admin_id)
            s["admins"] = admins
            save_settings(s)
            await update.message.reply_text(
                f"✅ <b>ADMIN ADDED!</b>\n<blockquote>🆔 ID: <code>{new_admin_id}</code></blockquote>",
                parse_mode="HTML", reply_markup=bot_settings_keyboard())
        context.user_data["bot_settings_mode"] = "main"
        return

    if text == "REMOVE ADMIN" and context.user_data.get("bot_settings_mode") == "main" and is_admin(uid):
        context.user_data["bot_settings_mode"] = "remove_admin"
        s = load_settings()
        admin_list = "\n".join(f"• <code>{a}</code>" for a in s.get("admins", []))
        await update.message.reply_text(
            f"➖ <b>REMOVE ADMIN</b>\n\n<blockquote>Current admins:\n{admin_list}</blockquote>\n\n"
            f"Send the <b>Telegram User ID</b> to remove from admin:",
            parse_mode="HTML", reply_markup=cancel_keyboard())
        return

    if context.user_data.get("bot_settings_mode") == "remove_admin" and is_admin(uid):
        if not text.lstrip("-").isdigit():
            await update.message.reply_text("❌ Invalid ID! Send a numeric Telegram ID.")
            return
        rem_id = int(text)
        s = load_settings()
        admins = s.get("admins", [])
        owners = s.get("owners", [])
        if rem_id in owners and rem_id == uid:
            await update.message.reply_text("❌ Cannot remove yourself (owner)!", reply_markup=bot_settings_keyboard())
        elif rem_id not in admins:
            await update.message.reply_text("⚠️ This user is not an admin!", reply_markup=bot_settings_keyboard())
        else:
            admins.remove(rem_id)
            s["admins"] = admins
            save_settings(s)
            await update.message.reply_text(
                f"✅ <b>ADMIN REMOVED!</b>\n<blockquote>🆔 ID: <code>{rem_id}</code></blockquote>",
                parse_mode="HTML", reply_markup=bot_settings_keyboard())
        context.user_data["bot_settings_mode"] = "main"
        return

    # SET OTP GROUP LINK
    if text == "SET OTP GROUP LINK" and context.user_data.get("bot_settings_mode") == "main" and is_admin(uid):
        context.user_data["bot_settings_mode"] = "set_otp_link"
        s = load_settings()
        cur = s.get("otp_group_url", "Not set")
        await update.message.reply_text(
            f"🔗 <b>SET OTP GROUP LINK</b>\n\n<blockquote>Current: <code>{cur}</code></blockquote>\n\n"
            f"Send the new OTP group invite link (e.g. https://t.me/+xxxxx):",
            parse_mode="HTML", reply_markup=cancel_keyboard())
        return

    if context.user_data.get("bot_settings_mode") == "set_otp_link" and is_admin(uid):
        s = load_settings()
        s["otp_group_url"] = text.strip()
        save_settings(s)
        await update.message.reply_text(
            f"✅ <b>OTP GROUP LINK UPDATED!</b>\n<blockquote>{html.escape(text.strip())}</blockquote>",
            parse_mode="HTML", reply_markup=bot_settings_keyboard())
        context.user_data["bot_settings_mode"] = "main"
        return

    # SET FORCE JOIN CHANNEL
    if text == "SET FORCE CHANNEL" and context.user_data.get("bot_settings_mode") == "main" and is_admin(uid):
        context.user_data["bot_settings_mode"] = "set_force_channel"
        s = load_settings()
        chs = s.get("force_join_channels") or []
        cur_text = "\n".join(f"  • <code>{c}</code>" for c in chs) if chs else "  <i>কোনো চ্যানেল সেট নেই (disabled)</i>"
        await update.message.reply_text(
            f"📢 <b>FORCE JOIN CHANNELS</b>\n\n"
            f"<b>বর্তমান চ্যানেল লিস্ট:</b>\n{cur_text}\n\n"
            f"<blockquote>"
            f"➕ চ্যানেল <b>যোগ করতে</b>: @username পাঠান\n"
            f"➖ চ্যানেল <b>সরাতে</b>: REMOVE @username পাঠান\n"
            f"🗑️ <b>সব বন্ধ করতে</b>: CLEAR পাঠান"
            f"</blockquote>",
            parse_mode="HTML", reply_markup=cancel_keyboard())
        return

    if context.user_data.get("bot_settings_mode") == "set_force_channel" and is_admin(uid):
        s = load_settings()
        val = text.strip()
        chs = s.get("force_join_channels") or []

        if val.upper() == "CLEAR":
            s["force_join_channels"] = []
            save_settings(s)
            await update.message.reply_text("✅ <b>Force Join সব চ্যানেল সরানো হয়েছে (Disabled)!</b>", parse_mode="HTML", reply_markup=bot_settings_keyboard())
            context.user_data["bot_settings_mode"] = "main"
            return

        if val.upper().startswith("REMOVE "):
            ch = val[7:].strip()
            if not ch.startswith("@") and not ch.lstrip("-").isdigit():
                ch = "@" + ch
            if ch in chs:
                chs.remove(ch)
                s["force_join_channels"] = chs
                save_settings(s)
                await update.message.reply_text(
                    f"✅ <b>সরানো হয়েছে:</b> <code>{html.escape(ch)}</code>\n\n"
                    f"বাকি চ্যানেল: {len(chs)}টি",
                    parse_mode="HTML", reply_markup=bot_settings_keyboard())
            else:
                await update.message.reply_text(
                    f"⚠️ <code>{html.escape(ch)}</code> লিস্টে নেই।",
                    parse_mode="HTML", reply_markup=bot_settings_keyboard())
            context.user_data["bot_settings_mode"] = "main"
            return

        if not val.startswith("@") and not val.lstrip("-").isdigit():
            val = "@" + val
        if val not in chs:
            chs.append(val)
            s["force_join_channels"] = chs
            save_settings(s)
        ch_list = "\n".join(f"  • <code>{c}</code>" for c in chs)
        await update.message.reply_text(
            f"✅ <b>চ্যানেল যোগ হয়েছে:</b> <code>{html.escape(val)}</code>\n\n"
            f"<b>এখন মোট {len(chs)}টি চ্যানেল:</b>\n{ch_list}",
            parse_mode="HTML", reply_markup=bot_settings_keyboard())
        context.user_data["bot_settings_mode"] = "main"
        return

    # SET OTP FORWARD CHAT ID
    if text == "SET OTP CHAT ID" and context.user_data.get("bot_settings_mode") == "main" and is_admin(uid):
        context.user_data["bot_settings_mode"] = "set_otp_chat_id"
        s = load_settings()
        cur = s.get("otp_group_chat_id") or "Not set"
        await update.message.reply_text(
            f"📋 <b>SET OTP FORWARD CHAT ID</b>\n\n<blockquote>Current: <code>{cur}</code></blockquote>\n\n"
            f"Send the Chat ID where OTPs are forwarded (e.g. -1001234567890):\n"
            f"Or send <b>DISABLE</b> to clear:",
            parse_mode="HTML", reply_markup=cancel_keyboard())
        return

    if context.user_data.get("bot_settings_mode") == "set_otp_chat_id" and is_admin(uid):
        s = load_settings()
        val = text.strip()
        if val.upper() == "DISABLE":
            s["otp_group_chat_id"] = None
            await update.message.reply_text("✅ <b>OTP Chat ID CLEARED!</b>", parse_mode="HTML", reply_markup=bot_settings_keyboard())
        elif val.lstrip("-").isdigit():
            s["otp_group_chat_id"] = int(val)
            await update.message.reply_text(
                f"✅ <b>OTP CHAT ID SET!</b>\n<blockquote><code>{val}</code></blockquote>",
                parse_mode="HTML", reply_markup=bot_settings_keyboard())
        else:
            await update.message.reply_text("❌ Invalid! Send a numeric chat ID (e.g. -1001234567890)")
            return
        save_settings(s)
        context.user_data["bot_settings_mode"] = "main"
        return

    # SET OTP RATE
    if text == "SET OTP RATE" and context.user_data.get("bot_settings_mode") == "main" and is_admin(uid):
        context.user_data["bot_settings_mode"] = "set_otp_rate"
        s = load_settings()
        cur = s.get("otp_bonus", 0.20)
        await update.message.reply_text(
            f"💰 <b>SET OTP RATE</b>\n\n"
            f"<blockquote>📌 বর্তমান রেট: <code>{cur} BDT</code> প্রতি OTP</blockquote>\n\n"
            f"নতুন রেট পাঠান (শুধু সংখ্যা):\n"
            f"<i>উদাহরণ: 0.5 বা 1 বা 2</i>",
            parse_mode="HTML", reply_markup=cancel_keyboard())
        return

    if context.user_data.get("bot_settings_mode") == "set_otp_rate" and is_admin(uid):
        try:
            new_rate = float(text.strip())
            if new_rate < 0:
                raise ValueError
        except ValueError:
            await update.message.reply_text("❌ Invalid! সংখ্যা দিন। যেমন: <code>0.5</code>", parse_mode="HTML")
            return
        s = load_settings()
        s["otp_bonus"] = new_rate
        save_settings(s)
        await update.message.reply_text(
            f"✅ <b>OTP RATE আপডেট হয়েছে!</b>\n\n"
            f"<blockquote>💰 নতুন রেট: <code>{new_rate} BDT</code> প্রতি OTP</blockquote>",
            parse_mode="HTML", reply_markup=bot_settings_keyboard())
        context.user_data["bot_settings_mode"] = "main"
        return

    # SET MIN WITHDRAW
    if text == "SET MIN WITHDRAW" and context.user_data.get("bot_settings_mode") == "main" and is_admin(uid):
        context.user_data["bot_settings_mode"] = "set_min_withdraw"
        s = load_settings()
        cur = s.get("min_withdraw", MIN_WITHDRAW)
        await update.message.reply_text(
            f"💸 <b>SET MINIMUM WITHDRAW</b>\n\n"
            f"<blockquote>📌 বর্তমান মিনিমাম: <code>{cur} BDT</code></blockquote>\n\n"
            f"নতুন মিনিমাম amount পাঠান (শুধু সংখ্যা):\n"
            f"<i>উদাহরণ: 50 বা 100</i>",
            parse_mode="HTML", reply_markup=cancel_keyboard())
        return

    if context.user_data.get("bot_settings_mode") == "set_min_withdraw" and is_admin(uid):
        try:
            new_min = float(text.strip())
            if new_min < 0:
                raise ValueError
        except ValueError:
            await update.message.reply_text("❌ Invalid! সংখ্যা দিন। যেমন: <code>50</code>", parse_mode="HTML")
            return
        s = load_settings()
        s["min_withdraw"] = new_min
        save_settings(s)
        await update.message.reply_text(
            f"✅ <b>MINIMUM WITHDRAW আপডেট হয়েছে!</b>\n\n"
            f"<blockquote>💸 নতুন মিনিমাম: <code>{new_min} BDT</code></blockquote>",
            parse_mode="HTML", reply_markup=bot_settings_keyboard())
        context.user_data["bot_settings_mode"] = "main"
        return

    # SET OTP BTN LINKS
    if text == "SET OTP BTN LINKS" and context.user_data.get("bot_settings_mode") == "main" and is_admin(uid):
        context.user_data["bot_settings_mode"] = "set_otp_btn_number"
        s = load_settings()
        cur_num = s.get("panel_url", "https://t.me/Nextsmsbdbot")
        cur_ch  = s.get("channel_url", "https://t.me/kabbofc")
        await update.message.reply_text(
            f"🔗 <b>SET OTP GROUP BUTTON LINKS</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"<blockquote>📌 বর্তমান NUMBER লিঙ্ক:\n<code>{html.escape(cur_num)}</code>\n\n"
            f"📌 বর্তমান CHANNEL লিঙ্ক:\n<code>{html.escape(cur_ch)}</code></blockquote>\n\n"
            f"<b>① NUMBER বাটনের নতুন লিঙ্ক পাঠান:</b>\n"
            f"<i>উদাহরণ: https://t.me/yourbotname</i>",
            parse_mode="HTML", reply_markup=cancel_keyboard())
        return

    if context.user_data.get("bot_settings_mode") == "set_otp_btn_number" and is_admin(uid):
        if text == "CANCEL":
            context.user_data["bot_settings_mode"] = "main"
            await update.message.reply_text("❌ বাতিল হয়েছে।", reply_markup=bot_settings_keyboard())
            return
        link = text.strip()
        if not link.startswith("http"):
            await update.message.reply_text("❌ সঠিক URL দিন। যেমন: <code>https://t.me/yourbotname</code>", parse_mode="HTML")
            return
        context.user_data["pending_panel_url"] = link
        context.user_data["bot_settings_mode"] = "set_otp_btn_channel"
        s = load_settings()
        cur_ch = s.get("channel_url", "https://t.me/kabbofc")
        await update.message.reply_text(
            f"✅ NUMBER লিঙ্ক সেভ রাখা হয়েছে।\n\n"
            f"<blockquote>📌 বর্তমান CHANNEL লিঙ্ক:\n<code>{html.escape(cur_ch)}</code></blockquote>\n\n"
            f"<b>② CHANNEL বাটনের নতুন লিঙ্ক পাঠান:</b>\n"
            f"<i>উদাহরণ: https://t.me/yourchannel</i>",
            parse_mode="HTML", reply_markup=cancel_keyboard())
        return

    if context.user_data.get("bot_settings_mode") == "set_otp_btn_channel" and is_admin(uid):
        if text == "CANCEL":
            context.user_data.pop("pending_panel_url", None)
            context.user_data["bot_settings_mode"] = "main"
            await update.message.reply_text("❌ বাতিল হয়েছে।", reply_markup=bot_settings_keyboard())
            return
        link = text.strip()
        if not link.startswith("http"):
            await update.message.reply_text("❌ সঠিক URL দিন। যেমন: <code>https://t.me/yourchannel</code>", parse_mode="HTML")
            return
        panel_url   = context.user_data.pop("pending_panel_url", "")
        channel_url = link
        s = load_settings()
        s["panel_url"]   = panel_url
        s["channel_url"] = channel_url
        save_settings(s)
        context.user_data["bot_settings_mode"] = "main"
        await update.message.reply_text(
            f"✅ <b>OTP গ্রুপ বাটন লিঙ্ক আপডেট হয়েছে!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"<blockquote>🔢 NUMBER: <code>{html.escape(panel_url)}</code>\n\n"
            f"📢 CHANNEL: <code>{html.escape(channel_url)}</code></blockquote>",
            parse_mode="HTML", reply_markup=bot_settings_keyboard())
        return

    # ZENEX CONFIG HANDLERS
    if text == "SET API KEY" and context.user_data.get("zenex_config_mode") == "main" and is_admin(uid):
        context.user_data["zenex_config_mode"] = "set_api_key"
        s = load_settings()
        cur = s.get("yesms_api_key", "Not set")
        await update.message.reply_text(
            f"🔑 <b>SET YESMS API KEY</b>\n\n<blockquote>Current: <code>{cur[:20]}...</code></blockquote>\n\nSend new API key:",
            parse_mode="HTML", reply_markup=cancel_keyboard())
        return

    if context.user_data.get("zenex_config_mode") == "set_api_key" and is_admin(uid):
        s = load_settings()
        s["yesms_api_key"] = text.strip()
        save_settings(s)
        await update.message.reply_text(
            f"✅ <b>YESMS API KEY UPDATED!</b>\n<blockquote><code>{html.escape(text.strip()[:20])}...</code></blockquote>",
            parse_mode="HTML", reply_markup=zenex_config_keyboard())
        context.user_data["zenex_config_mode"] = "main"
        return

    if text == "SET ALLOWED SERVICES" and context.user_data.get("zenex_config_mode") == "main" and is_admin(uid):
        context.user_data["zenex_config_mode"] = "set_services"
        s = load_settings()
        cur = ", ".join(s.get("allowed_services", []))
        await update.message.reply_text(
            f"📋 <b>SET ALLOWED ZENEX SERVICES</b>\n\n<blockquote>Current:\n<code>{cur}</code></blockquote>\n\n"
            f"Send comma-separated list:\n<i>e.g. Instagram,Facebook,WhatsApp,TikTok</i>",
            parse_mode="HTML", reply_markup=cancel_keyboard())
        return

    if context.user_data.get("zenex_config_mode") == "set_services" and is_admin(uid):
        services = [x.strip() for x in text.split(",") if x.strip()]
        s = load_settings()
        s["allowed_services"] = services
        save_settings(s)
        _ranges_cache["data"] = {}
        _ranges_cache["updated_at"] = 0
        svc_text = "\n".join(f"• {sv}" for sv in services)
        await update.message.reply_text(
            f"✅ <b>ALLOWED SERVICES UPDATED!</b>\n\n<blockquote>{svc_text}</blockquote>",
            parse_mode="HTML", reply_markup=zenex_config_keyboard())
        context.user_data["zenex_config_mode"] = "main"
        return

    if text == "VIEW ZENEX CONFIG" and context.user_data.get("zenex_config_mode") == "main" and is_admin(uid):
        s = load_settings()
        api_key = s.get("yesms_api_key", "N/A")
        base_url = "https://yesms.online"
        services = ", ".join(s.get("allowed_services", []))
        otp_link = s.get("otp_group_url", "N/A")
        chs = s.get("force_join_channels") or []
        force_ch = ", ".join(chs) if chs else "Disabled"
        otp_chat = s.get("otp_group_chat_id") or "Not set"
        console_st = "ON 🟢" if s.get("live_console") else "OFF 🔴"
        msg = (
            f"📡 <b>YESMS PANEL CONFIGURATION</b>\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<blockquote>🔑 API KEY: <code>{html.escape(api_key[:30])}...</code></blockquote>\n"
            f"<blockquote>🌐 BASE URL: <code>{html.escape(base_url)}</code></blockquote>\n"
            f"<blockquote>📋 ALLOWED SERVICES:\n{html.escape(services)}</blockquote>\n"
            f"<blockquote>🔗 OTP GROUP LINK: {html.escape(otp_link)}</blockquote>\n"
            f"<blockquote>📢 FORCE CHANNEL: {html.escape(str(force_ch))}</blockquote>\n"
            f"<blockquote>📋 OTP CHAT ID: <code>{otp_chat}</code></blockquote>\n"
            f"<blockquote>📡 LIVE CONSOLE: <b>{console_st}</b></blockquote>"
        )
        await update.message.reply_text(msg, parse_mode="HTML", reply_markup=zenex_config_keyboard())
        return

    # SERVICE MANAGEMENT HANDLERS
    if text == "LIST SERVICES" and context.user_data.get("service_mgmt_mode") == "main" and is_admin(uid):
        s = load_settings()
        manual = s.get("manual_services", [])
        if not manual:
            await update.message.reply_text("📋 No manual services added yet.", reply_markup=service_management_keyboard())
        else:
            lines = []
            for i, svc in enumerate(manual):
                countries = svc.get("countries", [])
                clines = "\n".join(
                    f"   {c.get('flag','🌍')} {c.get('name','?')} — <code>{', '.join(c.get('ranges',[]))}</code>"
                    for c in countries
                )
                lines.append(f"{i+1}. <b>{html.escape(svc['name'])}</b>\n{clines}")
            msg = f"📋 <b>MANUAL SERVICES ({len(manual)})</b>\n━━━━━━━━━━━━━━━━━━━━━━\n\n" + "\n\n".join(lines)
            await update.message.reply_text(msg, parse_mode="HTML", reply_markup=service_management_keyboard())
        return

    if text == "ADD SERVICE" and context.user_data.get("service_mgmt_mode") == "main" and is_admin(uid):
        context.user_data["service_mgmt_mode"] = "add_name"
        await update.message.reply_text(
            "➕ <b>ADD MANUAL SERVICE</b>\n\n"
            "<blockquote>Step 1: Send the <b>Service Name</b>\n"
            "e.g. FACEBOOK, WHATSAPP, INSTAGRAM</blockquote>",
            parse_mode="HTML", reply_markup=cancel_keyboard())
        return

    if context.user_data.get("service_mgmt_mode") == "add_name" and is_admin(uid):
        context.user_data["new_svc_name"] = text.strip().upper()
        context.user_data["new_svc_countries"] = []
        context.user_data["service_mgmt_mode"] = "add_country"
        await update.message.reply_text(
            f"➕ <b>{html.escape(context.user_data['new_svc_name'])}</b>\n\n"
            f"<blockquote>Step 2: Send the <b>Country Name</b>\n"
            f"e.g. Bangladesh, Nigeria, India</blockquote>\n\n"
            f"Send country name ↓",
            parse_mode="HTML", reply_markup=cancel_keyboard())
        return

    if text.upper() == "DONE" and context.user_data.get("service_mgmt_mode") == "add_country" and is_admin(uid):
        svc_name = context.user_data.get("new_svc_name")
        countries_done = context.user_data.get("new_svc_countries", [])
        if not svc_name or not countries_done:
            await update.message.reply_text("❌ No data to save. Start again.", reply_markup=service_management_keyboard())
            context.user_data["service_mgmt_mode"] = "main"
            return
        s = load_settings()
        manual = s.get("manual_services", [])
        manual.append({"name": svc_name, "countries": countries_done})
        s["manual_services"] = manual
        save_settings(s)
        done_lines = "\n".join(f"  {c['flag']} {c['name']} — <code>{', '.join(c['ranges'])}</code>" for c in countries_done)
        await update.message.reply_text(
            f"✅ <b>SERVICE SAVED!</b>\n\n"
            f"<blockquote>📱 <b>{html.escape(svc_name)}</b>\n{done_lines}</blockquote>",
            parse_mode="HTML", reply_markup=service_management_keyboard())
        context.user_data["service_mgmt_mode"] = "main"
        for k in ["new_svc_name", "new_svc_countries", "new_svc_cur_country"]:
            context.user_data.pop(k, None)
        return

    if context.user_data.get("service_mgmt_mode") == "add_country" and is_admin(uid):
        country_name = text.strip().title()
        context.user_data["new_svc_cur_country"] = country_name
        context.user_data["service_mgmt_mode"] = "add_range"
        svc_name = context.user_data.get("new_svc_name", "?")
        countries_done = context.user_data.get("new_svc_countries", [])
        done_text = ""
        if countries_done:
            done_text = "\n\n<blockquote>✅ Already added:\n" + "\n".join(
                f"  {c['flag']} {c['name']}" for c in countries_done) + "</blockquote>"
        await update.message.reply_text(
            f"➕ <b>{html.escape(svc_name)}</b> — 🌍 <b>{html.escape(country_name)}</b>{done_text}\n\n"
            f"<blockquote>Step 3: Send the <b>Range</b> for {html.escape(country_name)}\n\n"
            f"Format: Country Code + XXX\n"
            f"🇧🇩 Bangladesh → <code>880XXX</code>\n"
            f"🇳🇬 Nigeria → <code>234XXX</code>\n"
            f"🇮🇳 India → <code>91XXXXX</code>\n\n"
            f"Multiple ranges: <code>880XXX, 8801XXX</code></blockquote>",
            parse_mode="HTML", reply_markup=cancel_keyboard())
        return

    if context.user_data.get("service_mgmt_mode") == "add_range" and is_admin(uid):
        raw_ranges = [r.strip().upper() for r in text.split(",") if r.strip()]
        country_name = context.user_data.get("new_svc_cur_country", "Unknown")
        flag, detected = "🌍", country_name
        if raw_ranges:
            prefix = re.sub(r'[xX]+$', '', raw_ranges[0]).strip()
            pfx_d  = re.sub(r'\D', '', prefix)
            flag, detected = get_country_info(pfx_d)
        countries_done = context.user_data.get("new_svc_countries", [])
        countries_done.append({"name": country_name, "flag": flag, "ranges": raw_ranges})
        context.user_data["new_svc_countries"] = countries_done
        context.user_data["service_mgmt_mode"] = "add_country"
        context.user_data.pop("new_svc_cur_country", None)
        ranges_text = ", ".join(raw_ranges)
        done_lines = "\n".join(f"  {c['flag']} {c['name']} — <code>{', '.join(c['ranges'])}</code>" for c in countries_done)
        await update.message.reply_text(
            f"✅ <b>{flag} {html.escape(country_name)}</b> added!\n"
            f"<blockquote>Ranges: <code>{html.escape(ranges_text)}</code></blockquote>\n\n"
            f"<blockquote>Countries so far:\n{done_lines}</blockquote>\n\n"
            f"Send another <b>Country Name</b> to add more,\n"
            f"or send <b>DONE</b> to save the service.",
            parse_mode="HTML", reply_markup=cancel_keyboard())
        return

    if text == "REMOVE SERVICE" and context.user_data.get("service_mgmt_mode") == "main" and is_admin(uid):
        s = load_settings()
        manual = s.get("manual_services", [])
        if not manual:
            await update.message.reply_text("📋 No services to remove.", reply_markup=service_management_keyboard())
            return
        lines = "\n".join(f"{i+1}. <b>{html.escape(svc['name'])}</b>" for i, svc in enumerate(manual))
        context.user_data["service_mgmt_mode"] = "remove"
        await update.message.reply_text(
            f"➖ <b>REMOVE SERVICE</b>\n\n<blockquote>{lines}</blockquote>\n\n"
            f"Send the <b>number</b> of the service to remove:",
            parse_mode="HTML", reply_markup=cancel_keyboard())
        return

    if context.user_data.get("service_mgmt_mode") == "remove" and is_admin(uid):
        if not text.isdigit():
            await update.message.reply_text("❌ Send a valid number from the list.")
            return
        idx = int(text) - 1
        s = load_settings()
        manual = s.get("manual_services", [])
        if idx < 0 or idx >= len(manual):
            await update.message.reply_text(f"❌ Invalid number! Choose 1-{len(manual)}.")
            return
        removed = manual.pop(idx)
        s["manual_services"] = manual
        save_settings(s)
        await update.message.reply_text(
            f"✅ <b>SERVICE REMOVED!</b>\n<blockquote>📱 {html.escape(removed['name'])}</blockquote>",
            parse_mode="HTML", reply_markup=service_management_keyboard())
        context.user_data["service_mgmt_mode"] = "main"
        return

    await update.message.reply_text("🔹 PLEASE USE THE BUTTONS BELOW:", reply_markup=main_keyboard(uid))

# ==================== COMMAND HANDLERS SECTION ====================

async def get1number_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if is_user_banned(uid):
        await update.message.reply_text("🚫 YOU ARE BANNED 🚫", reply_markup=main_keyboard(uid))
        return
    if not is_admin(uid):
        if not await check_force_join(update, context):
            return
    await show_app_selection(update, context)

async def searchotp_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if is_user_banned(uid):
        await update.message.reply_text("🚫 YOU ARE BANNED 🚫", reply_markup=main_keyboard(uid))
        return
    if not is_admin(uid):
        if not await check_force_join(update, context):
            return
    context.user_data["mode"] = "search_otp"
    await update.message.reply_text("🔍 **ENTER THE NUMBER TO SEARCH OTP:**", parse_mode="Markdown")

async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if is_user_banned(uid):
        await update.message.reply_text("🚫 YOU ARE BANNED 🚫", reply_markup=main_keyboard(uid))
        return
    await show_wallet_screen(update, context)

async def wallet_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if is_user_banned(uid):
        await update.message.reply_text("🚫 YOU ARE BANNED 🚫", reply_markup=main_keyboard(uid))
        return
    if not is_admin(uid) and not await check_force_join(update, context):
        return
    await show_wallet_screen(update, context)

async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if is_user_banned(uid):
        await update.message.reply_text("🚫 YOU ARE BANNED 🚫", reply_markup=main_keyboard(uid))
        return
    user_data = get_user(uid)
    stats = get_user_stats(uid)
    user = update.effective_user
    profile_text = (
        f"👤 **YOUR PROFILE**\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🏷️ NAME: `{user.full_name}`\n"
        f"🆔 USERNAME: @{user.username or 'No username'}\n"
        f"🗝️ ID: `{uid}`\n\n"
        f"💵 BALANCE: {format_balance(user_data.get('balance', 0))} BDT\n\n"
        f"✨ TODAY: 📱 {stats['today_numbers']} | 🔑 {stats['today_otps']}\n"
        f"🔥 7 DAYS: 📱 {stats['last7d_numbers']} | 🔑 {stats['last7d_otps']}\n"
        f"🌐 ALL TIME: 📱 {stats['total_numbers']} | 🔑 {stats['total_otps']}"
    )
    await update.message.reply_text(profile_text, parse_mode="Markdown")

async def refer_command_slash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if is_user_banned(uid):
        await update.message.reply_text("🚫 YOU ARE BANNED 🚫", reply_markup=main_keyboard(uid))
        return
    await refer_command(update, context)

async def leaderboard_command_slash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if is_user_banned(uid):
        await update.message.reply_text("🚫 YOU ARE BANNED 🚫", reply_markup=main_keyboard(uid))
        return
    await leaderboard_command(update, context)

async def liveconsole_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_admin(uid):
        await update.message.reply_text("❌ <b>শুধুমাত্র অ্যাডমিন এই কমান্ড ব্যবহার করতে পারবেন।</b>", parse_mode="HTML")
        return
    s = load_settings()
    cur_status = s.get("live_console", False)
    new_status = not cur_status
    s["live_console"] = new_status
    save_settings(s)
    status_str = "ON 🟢" if new_status else "OFF 🔴"
    await update.message.reply_text(
        f"📡 <b>Live Console এখন: {status_str}</b>\n\n"
        f"<blockquote>API: https://yesms.online/api/console_data\n"
        f"সাইকেল: প্রতি ১২০ সেকেন্ড (২ মিনিট)\n"
        f"লিমিট: প্রতি সাইকেলে ৩০টি পর্যন্ত মেসেজ\n"
        f"রেট লিমিট: প্রতি ২ সেকেন্ডে ১টি মেসেজ</blockquote>",
        parse_mode="HTML",
        reply_markup=bot_settings_keyboard()
    )

# ==================== START & CALLBACK SECTION ====================

async def check_force_join(update, context):
    s = load_settings()
    channels = s.get("force_join_channels") or []
    if not channels:
        return True
    uid = update.effective_user.id
    if is_admin(uid):
        return True

    unjoined_btns = []
    for channel in channels:
        try:
            member = await context.bot.get_chat_member(channel, uid)
            if member.status in ("member", "administrator", "creator", "restricted"):
                continue
        except Exception:
            pass
        channel_clean = str(channel).lstrip("@")
        try:
            chat = await context.bot.get_chat(channel)
            invite_url = chat.invite_link or f"https://t.me/{channel_clean}"
            label = f"✅ JOIN — {chat.title or channel}"
        except Exception:
            invite_url = f"https://t.me/{channel_clean}"
            label = f"✅ JOIN — {channel}"
        unjoined_btns.append([InlineKeyboardButton(label, url=invite_url)])

    if not unjoined_btns:
        return True

    await update.effective_message.reply_text(
        f"⚠️ <b>FORCE JOIN REQUIRED!</b>\n\n"
        f"<blockquote>বট ব্যবহার করতে নিচের সব চ্যানেলে জয়েন করুন।\n"
        f"জয়েন করার পর আবার /start দিন।</blockquote>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(unjoined_btns)
    )
    return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    uid_str = str(uid)

    existing_data = load_data(USER_DATA_FILE)
    is_new_user = uid_str not in existing_data
    if is_new_user:
        get_user(uid)

    if not await check_force_join(update, context):
        return

    args = context.args
    if args:
        param = args[0]
        if is_range_request(param):
            await request_queue.put({'type': 'auto_number', 'update': update, 'context': context, 'range_text': param})
            return
        elif is_referral_request(param) and is_new_user:
            try:
                referrer_id = int(param)
                if referrer_id != uid and str(referrer_id) in existing_data:
                    current_count = get_referral_count(referrer_id)
                    new_count = current_count + 1
                    update_referral_count(referrer_id, new_count)
                    await update_db_balance(referrer_id, REFERRAL_PRICE)
                    log_global_activity(referrer_id, "REFERRAL_JOINED", {"referred_user": uid})
                    try:
                        await context.bot.send_message(
                            referrer_id,
                            f"🎉 <b>NEW REFERRAL!</b>\n\n<blockquote>🗝️ ID: <code>{uid}</code>\n💰 REWARD: {format_balance(REFERRAL_PRICE)} BDT\n👥 TOTAL REFERS: {new_count}</blockquote>",
                            parse_mode="HTML"
                        )
                    except:
                        pass
            except Exception as e:
                print(f"Referral error: {e}")

    context.user_data.clear()
    await update.message.reply_text(
        WELCOME_MESSAGE,
        parse_mode="HTML",
        reply_markup=main_keyboard(uid),
    )
    await show_app_selection(update, context)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    data = query.data
    await query.answer()

    if not is_admin(uid) and is_user_banned(uid):
        await query.edit_message_text("🚫 YOU ARE BANNED 🚫")
        return

    if not is_admin(uid):
        if not await check_force_join(update, context):
            return

    # ZENEXA — APP SELECTION
    if data.startswith("sel_app_"):
        app_name = data[8:]
        top = context.user_data.get("top_ranges_by_app") or (_ranges_cache.get("data") or {})
        if not top or app_name not in top:
            await query.answer("App not found. Please try again.", show_alert=True); return
        ranges = top[app_name].get("ranges", [])
        if not ranges:
            await query.answer("No ranges available for this app right now.", show_alert=True); return
        context.user_data["sel_app"] = app_name
        context.user_data["sel_ranges"] = ranges
        btns, seen = [], {}
        clrs = ["primary","success","danger"]
        ci = 0
        for i, r in enumerate(ranges[:24]):
            prefix = re.sub(r'[xX]+$', '', str(r)).strip()
            pfx_d = re.sub(r'\D', '', prefix)
            flag, cname = get_country_info(pfx_d)
            label = f"{flag} {cname}"
            if label not in seen:
                seen[label] = i
                btns.append(InlineKeyboardButton(label, callback_data=f"sel_rng_{i}",
                    api_kwargs={"style": clrs[ci % 3]}))
                ci += 1
        rows = [btns[j:j+2] for j in range(0, len(btns), 2)]
        rows.append([InlineKeyboardButton("\u25c0\ufe0f BACK", callback_data="back_apps",
                                          api_kwargs={"style": "danger"})])
        await query.message.edit_text(
            f'{get_tg_emoji("get_number_btn")} <b>SELECT COUNTRY</b>\n'
            f'\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n'
            f'<blockquote>\U0001f4f1 App: <b>{html.escape(app_name)}</b></blockquote>\n'
            f'<blockquote>\U0001f30d Select your Country:</blockquote>',
            parse_mode="HTML", reply_markup=InlineKeyboardMarkup(rows))
        return

    # ZENEXA — RANGE SELECTION
    if data.startswith("sel_rng_"):
        idx = int(data[8:])
        ranges = context.user_data.get("sel_ranges", [])
        app_name = context.user_data.get("sel_app", "")
        if idx >= len(ranges):
            await query.answer("Range not found. Please try again.", show_alert=True); return
        asyncio.create_task(fast_allocate_number(query, context, ranges[idx], app_name))
        return

    # CUSTOM RANGE
    if data == "custom_range":
        context.user_data["mode"] = "custom_range"
        await query.message.edit_text(
            "\u2699\ufe0f <b>CUSTOM RANGE</b>\n\n"
            "<blockquote>\U0001f4f6 Type your custom range.\n"
            "Example: <code>234XXX</code> or <code>225XXX</code></blockquote>\n\n"
            "<blockquote>\u2328\ufe0f Type range below and Send:</blockquote>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("\u25c0\ufe0f BACK", callback_data="back_apps",
                                      api_kwargs={"style": "danger"})
            ]]))
        return

    # MANUAL SERVICE
    if data.startswith("manual_svc_"):
        idx = int(data[len("manual_svc_"):])
        s = load_settings()
        manual = s.get("manual_services", [])
        if idx >= len(manual):
            await query.answer("Service not found.", show_alert=True); return
        svc = manual[idx]
        countries = svc.get("countries", [])
        if not countries:
            await query.answer("No countries added for this service yet.", show_alert=True); return

        clrs = ["primary", "success", "danger"]
        btns = []
        for ci, c in enumerate(countries):
            flag = c.get("flag", "🌍")
            cname = c.get("name", "Unknown")
            btns.append(InlineKeyboardButton(
                f"{flag} {cname}",
                callback_data=f"manual_cnt_{idx}_{ci}",
                api_kwargs={"style": clrs[ci % 3]}
            ))
        rows = [btns[j:j+2] for j in range(0, len(btns), 2)]
        rows.append([InlineKeyboardButton(
            "\u25c0\ufe0f BACK", callback_data="back_apps",
            api_kwargs={"style": "danger"}
        )])
        await query.message.edit_text(
            f'\U0001f527 <b>{html.escape(svc["name"])}</b>\n'
            f'\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n'
            f'<blockquote>\U0001f4f1 App: <b>{html.escape(svc["name"])}</b></blockquote>\n'
            f'<blockquote>\U0001f30d Select your Country:</blockquote>',
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(rows)
        )
        return

    if data.startswith("manual_cnt_"):
        parts = data.split("_")
        svc_idx = int(parts[2])
        cnt_idx = int(parts[3])
        s = load_settings()
        manual = s.get("manual_services", [])
        if svc_idx >= len(manual):
            await query.answer("Service not found.", show_alert=True); return
        svc = manual[svc_idx]
        countries = svc.get("countries", [])
        if cnt_idx >= len(countries):
            await query.answer("Country not found.", show_alert=True); return
        country = countries[cnt_idx]
        ranges = country.get("ranges", [])
        if not ranges:
            await query.answer("No ranges for this country.", show_alert=True); return
        range_text = random.choice(ranges).strip().upper()
        svc_name = svc["name"]
        asyncio.create_task(fast_allocate_number(query, context, range_text, svc_name))
        return

    # BACK TO APP LIST
    if data in ("back_apps", "back_services"):
        top = context.user_data.get("top_ranges_by_app") or (_ranges_cache["data"] or {})
        all_rows = build_app_buttons_from_cache(top) if top else []
        all_rows.append([InlineKeyboardButton(
            "🎯 Custom Range",
            callback_data="custom_range",
            api_kwargs={"icon_custom_emoji_id": "5231012545799666522", "style": "primary"})])
        all_rows.append([InlineKeyboardButton(
            "🏠 Main Menu",
            callback_data="back_main",
            api_kwargs={"style": "success"})])
        msg = f'{get_tg_emoji("setting")} <b>Select Service:</b>'
        await query.message.edit_text(msg, parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(all_rows))
        return

    if data == "same_range":
        r_text = last_range.get(uid)
        if r_text:
            try:
                await query.message.delete()
            except:
                pass
            await process_numbers(update, context, r_text, 2)
        return

    if data == "back_main":
        try:
            await query.message.delete()
        except:
            pass
        await query.message.reply_text("🏠 Main Menu", reply_markup=main_keyboard(uid))
        return

    # WALLET + WITHDRAW
    if data == "wallet_view":
        context.user_data["wallet_mode"] = None
        context.user_data["pending_wallet_method"] = None
        context.user_data["withdraw_mode"] = None
        await show_wallet_screen(update, context)
        return

    if data == "wallet_set":
        context.user_data["wallet_mode"] = "select_method"
        context.user_data["pending_wallet_method"] = None
        context.user_data["withdraw_mode"] = None
        await query.message.reply_text(
            "💳 <b>Set your withdrawal wallet</b>\nChoose a payment method:",
            parse_mode="HTML",
            reply_markup=wallet_method_selection_keyboard(),
        )
        return

    if data.startswith("wallet_method_"):
        method_key = data.removeprefix("wallet_method_")
        method_map = {
            "bkash": "BKASH",
            "nagad": "NAGAD",
            "rocket": "ROCKET",
            "bep20": "BINANCE BEP20",
        }
        method = method_map.get(method_key)
        if not method:
            await query.answer("Wallet method not recognized.", show_alert=True)
            return
        context.user_data["pending_wallet_method"] = method
        context.user_data["wallet_mode"] = "address"
        if method == "BINANCE BEP20":
            prompt = "Send your Binance BEP20 (BSC) wallet address (0x + 40 hexadecimal characters)."
        else:
            prompt = f"Send the Bangladesh {wallet_method_label(method)} wallet number (for example 017XXXXXXXX)."
        await query.message.reply_text(
            f"📬 {prompt}\n\nSend CANCEL to stop.",
            reply_markup=cancel_keyboard(),
        )
        return

    if data == "withdraw_start":
        user_data = get_user(uid)
        method = user_data.get("wallet_method")
        destination = user_data.get("wallet_address")
        if not method or not destination:
            await query.message.reply_text(
                "⚠️ Set your withdrawal wallet first.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("💳 SET WALLET", callback_data="wallet_set", style="primary"),
                    InlineKeyboardButton("⬅️ BACK", callback_data="wallet_view", style="danger"),
                ]]),
            )
            return

        balance = float(user_data.get("balance", 0) or 0)
        minimum = get_minimum_withdraw_amount()
        payment_label = "BEP20" if "BINANCE" in str(method).upper() else wallet_method_label(method)
        withdraw_text = (
            "💳 <b>Withdrawal</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"💰 Balance: <b>{format_wallet_amount(balance)} BDT</b>\n"
            f"📉 Minimum: <b>{minimum:.1f} BDT</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "<i>Select your payment method:</i>"
        )
        await query.message.reply_text(
            withdraw_text,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    f"💳 {payment_label}",
                    callback_data="withdraw_use_wallet",
                    style="primary",
                )],
                [InlineKeyboardButton("⬅️ Back", callback_data="wallet_view", style="danger")],
            ]),
        )
        return

    if data == "withdraw_use_wallet":
        user_data = get_user(uid)
        minimum = get_minimum_withdraw_amount()
        balance = float(user_data.get("balance", 0) or 0)
        if not user_data.get("wallet_method") or not user_data.get("wallet_address"):
            await query.message.reply_text(
                "⚠️ Set your withdrawal wallet first.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("💳 SET WALLET", callback_data="wallet_set", style="primary")
                ]]),
            )
            return
        if balance < minimum:
            await query.message.reply_text(
                f"⚠️ Minimum withdrawal is {minimum:.1f} BDT. "
                f"Your current balance is {format_wallet_amount(balance)} BDT.",
                reply_markup=main_keyboard(uid),
            )
            return
        context.user_data["wallet_mode"] = None
        context.user_data["withdraw_mode"] = "amount"
        await query.message.reply_text(
            f"💸 Send the withdrawal amount in BDT.\n"
            f"Minimum: {minimum:.1f} BDT | Maximum: {MAX_WITHDRAW} BDT\n"
            f"Available balance: {format_wallet_amount(balance)} BDT",
            reply_markup=cancel_keyboard(),
        )
        return

    if data == "withdraw_confirm":
        await process_withdraw_confirm(update, context)
        return

    if data == "withdraw_cancel":
        await process_withdraw_cancel(update, context)
        return

    if data.startswith("admin_approve_"):
        await admin_approve_withdraw(update, context, data.replace("admin_approve_", ""))
        return

    if data.startswith("admin_reject_"):
        await admin_reject_withdraw(update, context, data.replace("admin_reject_", ""))
        return

    # EMOJI SETTINGS CALLBACKS
    if data == "emoji_noop":
        return

    if data == "emoji_close":
        await query.edit_message_text("🎨 Emoji Settings বন্ধ হয়েছে।")
        return

    if data.startswith("emoji_pg:"):
        page = int(data.split(":")[1])
        kb = get_emoji_page_keyboard(page)
        await query.edit_message_reply_markup(reply_markup=kb)
        return

    if data.startswith("emoji_ed:"):
        key = data.split(":", 1)[1]
        s = load_settings()
        custom = s.get("custom_emojis", {}).get(key, {})
        default_id = EMOJI_ID_MAP.get(key, "")
        default_fb = FALLBACK_EMOJI_MAP.get(key, "⭐")
        cur_id  = custom.get("id",       default_id)
        cur_fb  = custom.get("fallback", default_fb)
        is_custom = bool(custom)

        if cur_id:
            cur_preview = f'<tg-emoji emoji-id="{cur_id}">{cur_fb}</tg-emoji>'
        else:
            cur_preview = cur_fb

        buttons = []
        if is_custom:
            buttons.append([InlineKeyboardButton("🔄 Default-এ রিসেট করুন", callback_data=f"emoji_rs:{key}")])
        buttons.append([InlineKeyboardButton("◀️ ফিরে যান", callback_data="emoji_pg:0")])

        try:
            await query.edit_message_text(
                f"🎨 <b>EMOJI EDIT: <code>{key}</code></b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"<blockquote>📌 বর্তমান: {cur_preview}\n"
                f"🆔 Premium ID: <code>{cur_id or 'নেই'}</code>\n"
                f"🔤 Fallback: {cur_fb}\n"
                f"{'✏️ কাস্টম সেট আছে' if is_custom else '🔹 ডিফল্ট মান ব্যবহার হচ্ছে'}</blockquote>\n\n"
                f"<b>নতুন মান পাঠান (নিচে type করুন):</b>\n\n"
                f"• শুধু normal emoji → <code>🚀</code>\n"
                f"• শুধু premium ID → <code>5244837092042750681</code>\n"
                f"• উভয় → <code>🚀:5244837092042750681</code>",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        except Exception:
            pass

        context.user_data["emoji_edit_key"]  = key
        context.user_data["emoji_edit_page"] = 0
        return

    if data.startswith("emoji_rs:"):
        key = data.split(":", 1)[1]
        s = load_settings()
        custom = s.get("custom_emojis", {})
        if key in custom:
            del custom[key]
            s["custom_emojis"] = custom
            save_settings(s)

        kb = get_emoji_page_keyboard(0)
        await query.edit_message_text(
            f"✅ <b><code>{key}</code> emoji ডিফল্টে রিসেট হয়েছে!</b>\n\n"
            f"আরও emoji কাস্টমাইজ করুন:",
            parse_mode="HTML",
            reply_markup=kb
        )
        return

    if data.startswith("copy_id_"):
        await query.answer(f"✅ Copied ID: {data.replace('copy_id_', '')}", show_alert=True)
        return

    if data.startswith("copy_text_"):
        await query.answer(f"✅ Copied: {data.replace('copy_text_', '')}", show_alert=True)
        return

    if data.startswith("my_ref_"):
        target_uid = data.replace("my_ref_", "")
        all_logs = load_data(ACTIVITY_LOGS_FILE)
        my_referrals = [log for log in all_logs if str(log.get('uid')) == str(target_uid) and log.get('action') == "REFERRAL_JOINED"]
        content = f"👥 REFERRAL REPORT — {target_uid}\n━━━━━━━━━━━━\nTOTAL: {len(my_referrals)}\n\n"
        for i, log in enumerate(my_referrals, 1):
            try:
                dt_obj = datetime.fromisoformat(log['timestamp'])
                ref_id = log.get('details', {}).get('referred_user', 'N/A')
                content += f"{i}. ID: {ref_id} | {dt_obj.strftime('%d/%m/%Y %I:%M %p')}\n"
            except:
                continue
        f = io.BytesIO(content.encode())
        f.name = f"REF_{target_uid}.txt"
        await context.bot.send_document(chat_id=uid, document=f, caption="✅ **REFERRAL DATA**", parse_mode="Markdown")
        return

    if data.startswith("full_logs_"):
        target_uid = data.replace("full_logs_", "")
        stats = get_user_stats(target_uid)
        all_logs = load_data(ACTIVITY_LOGS_FILE)
        user_db = load_data(USER_DATA_FILE)
        user_info = user_db.get(str(target_uid), {})
        user_otps = [log for log in all_logs if str(log.get('uid')) == str(target_uid) and log.get('action') == "OTP_RECEIVED"]
        content = (
            f"📊 USER DATA REPORT — {target_uid}\n"
            f"💰 BALANCE: {user_info.get('balance', 0):.2f} BDT\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"TODAY NUMBERS: {stats['today_numbers']}\n"
            f"TODAY OTPS: {stats['today_otps']}\n"
            f"7D NUMBERS: {stats['last7d_numbers']}\n"
            f"7D OTPS: {stats['last7d_otps']}\n"
            f"TOTAL NUMBERS: {stats['total_numbers']}\n"
            f"TOTAL OTPS: {stats['total_otps']}\n"
            f"━━━━━━━━━━━━━━━━━━\n\nOTP LOGS:\n"
        )
        for i, log in enumerate(user_otps, 1):
            try:
                dt_obj = datetime.fromisoformat(log['timestamp'])
                d = log.get('details', {})
                content += f"{i}. {dt_obj.strftime('%d/%m/%Y %I:%M %p')}\n   📞 {d.get('number', 'N/A')}\n   🔑 {d.get('otp', 'N/A')}\n\n"
            except:
                continue
        f = io.BytesIO(content.encode())
        f.name = f"USER_{target_uid}.txt"
        await context.bot.send_document(
            chat_id=uid, document=f,
            caption=f"✅ <b>DATA FOR USER: <code>{target_uid}</code></b>",
            parse_mode="HTML"
        )
        return

# ==================== MAIN & POST INIT SECTION ====================

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_admin(uid):
        await update.message.reply_text("❌ <b>শুধুমাত্র অ্যাডমিন এই কমান্ড ব্যবহার করতে পারবেন।</b>", parse_mode="HTML")
        return
    context.user_data["admin_mode"] = "main"
    await update.message.reply_text(
        "⌬━━━━━━━━━━━━━━━━━━━━⌬\n   WELCOME ADMIN PANEL\n⌬━━━━━━━━━━━━━━━━━━━━⌬",
        reply_markup=admin_main_keyboard()
    )

# ==================== BACKUP / RESTORE COMMANDS ====================

async def backup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_admin(uid):
        await update.message.reply_text("❌ <b>শুধুমাত্র অ্যাডমিন এই কমান্ড ব্যবহার করতে পারবেন।</b>", parse_mode="HTML")
        return

    import zipfile, datetime

    DATA_FILES = [
        USER_DATA_FILE,
        PAID_SMS_FILE,
        STATS_FILE,
        REFERRAL_DATA_FILE,
        BANNED_USERS_FILE,
        WITHDRAW_DATA_FILE,
        ACTIVITY_LOGS_FILE,
        DATA_RANGE_FILE,
        SETTINGS_FILE,
        CONSOLE_SENT_FILE,
    ]

    try:
        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_buffer = io.BytesIO()
        added, skipped = [], []

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for path in DATA_FILES:
                if os.path.exists(path):
                    arcname = os.path.basename(path)
                    zf.write(path, arcname)
                    added.append(arcname)
                else:
                    skipped.append(os.path.basename(path))

        zip_buffer.seek(0)
        zip_buffer.name = f"backup_{now}.zip"

        file_list = "\n".join(f"  ✅ <code>{f}</code>" for f in added)
        skip_list = ("\n⚠️ <b>পাওয়া যায়নি:</b>\n" + "\n".join(f"  ➖ <code>{f}</code>" for f in skipped)) if skipped else ""

        caption = (
            f"📦 <b>সম্পূর্ণ বট ব্যাকআপ</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🗓 <b>তারিখ:</b> <code>{now}</code>\n\n"
            f"📁 <b>ফাইলসমূহ ({len(added)}টি):</b>\n{file_list}"
            f"{skip_list}"
        )

        await update.message.reply_document(
            document=zip_buffer,
            filename=zip_buffer.name,
            caption=caption,
            parse_mode="HTML"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ ব্যাকআপ পাঠাতে সমস্যা হয়েছে: <code>{e}</code>", parse_mode="HTML")

async def restore_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_admin(uid):
        await update.message.reply_text("❌ <b>শুধুমাত্র অ্যাডমিন এই কমান্ড ব্যবহার করতে পারবেন।</b>", parse_mode="HTML")
        return
    context.user_data["restore_mode"] = True
    await update.message.reply_text(
        "📂 <b>Restore Mode চালু হয়েছে</b>\n\n"
        "<blockquote>এখন /backup থেকে পাওয়া <code>backup_*.zip</code> ফাইলটি পাঠান।\n\n"
        "✅ zip-এর মধ্যে থাকা সব ডেটা restore হবে:\n"
        "• users.json, settings.json\n"
        "• banned_users.json, withdraw_requests.json\n"
        "• activity_logs.json, user_stats.json ইত্যাদি</blockquote>",
        parse_mode="HTML"
    )

async def handle_restore_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_admin(uid):
        return
    if not context.user_data.get("restore_mode"):
        return

    doc = update.message.document
    if not doc:
        return

    fname = doc.file_name or ""
    is_zip = fname.endswith(".zip")

    if not is_zip:
        await update.message.reply_text(
            "⚠️ <b>শুধুমাত্র .zip ফাইল গ্রহণযোগ্য।</b>\n"
            "/restore দিয়ে আবার শুরু করুন।",
            parse_mode="HTML"
        )
        return

    context.user_data["restore_mode"] = False
    msg = await update.message.reply_text("⏳ <b>ফাইল ডাউনলোড হচ্ছে...</b>", parse_mode="HTML")

    try:
        import zipfile, tempfile

        tg_file = await context.bot.get_file(doc.file_id)

        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
            tmp_path = tmp.name
        await tg_file.download_to_drive(tmp_path)

        restored, skipped = [], []
        bot_dir = os.path.dirname(os.path.abspath(__file__))

        ALLOWED = {
            "users.json", "user_stats.json", "settings.json",
            "banned_users.json", "withdraw_requests.json",
            "activity_logs.json", "paid_sms.json",
            "datarange.json", "referral_data.json",
            "console_sent.json"
        }

        with zipfile.ZipFile(tmp_path, "r") as zf:
            for name in zf.namelist():
                if name not in ALLOWED:
                    skipped.append(name)
                    continue
                dest = os.path.join(bot_dir, name)
                with zf.open(name) as src, open(dest, "wb") as dst:
                    dst.write(src.read())
                restored.append(name)

        os.unlink(tmp_path)

        r_list = "\n".join(f"  ✅ <code>{f}</code>" for f in restored)
        s_list = ("\n⚠️ skip হয়েছে:\n" + "\n".join(f"  ➖ <code>{f}</code>" for f in skipped)) if skipped else ""

        await msg.edit_text(
            f"✅ <b>Restore সম্পন্ন হয়েছে!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📁 <b>Restore হয়েছে ({len(restored)}টি ফাইল):</b>\n{r_list}"
            f"{s_list}",
            parse_mode="HTML"
        )

    except Exception as e:
        await msg.edit_text(f"❌ <b>Restore ব্যর্থ হয়েছে:</b> <code>{e}</code>", parse_mode="HTML")

# ==================== BROADCAST COMMAND ====================

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_admin(uid):
        await update.message.reply_text("❌ <b>শুধুমাত্র অ্যাডমিন এই কমান্ড ব্যবহার করতে পারবেন।</b>", parse_mode="HTML")
        return
    context.user_data["broadcast_mode"] = True
    await update.message.reply_text(
        "📢 <b>ADMIN BROADCAST SYSTEM (PRO)</b>\n\n"
        "💬 আপনি এখন যা পাঠাবেন (Text, Photo, Video, Document, Voice, Audio, Animation, Sticker) – সকল ইউজারের কাছে প্রফেশনাল হেডারসহ চলে যাবে।\n\n"
        "✨ রেঞ্জ (যেমন: 237XXX) থাকলে তা অটোমেটিক ক্লিক-টু-কপি হয়ে যাবে।",
        parse_mode="HTML",
        reply_markup=cancel_keyboard()
    )

async def post_init(application):
    for _ in range(20):
        asyncio.create_task(worker())
    asyncio.create_task(monitor_loop(application))
    asyncio.create_task(live_console_loop(application))
    asyncio.create_task(_bg_refresh_ranges())

def main():
    if not BOT_TOKEN:
        print("⚠️ Warning: BOT_TOKEN is empty. Set BOT_TOKEN in environment or .env")
    app = ApplicationBuilder().token(BOT_TOKEN).concurrent_updates(True).post_init(post_init).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("get1number", get1number_command))
    app.add_handler(CommandHandler("searchotp", searchotp_command))
    app.add_handler(CommandHandler("balance", balance_command))
    app.add_handler(CommandHandler("wallet", wallet_command))
    app.add_handler(CommandHandler("profile", profile_command))
    app.add_handler(CommandHandler("refer", refer_command_slash))
    app.add_handler(CommandHandler("leaderboard", leaderboard_command_slash))
    app.add_handler(CommandHandler("admin", admin_command))
    app.add_handler(CommandHandler("console", liveconsole_command))
    app.add_handler(CommandHandler("liveconsole", liveconsole_command))
    app.add_handler(CommandHandler("backup", backup_command))
    app.add_handler(CommandHandler("restore", restore_command))
    app.add_handler(CommandHandler("broadcast", broadcast_command))
    app.add_handler(MessageHandler(filters.Document.FileExtension("py") | filters.Document.FileExtension("zip"), handle_restore_file))

    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("🚀 BOT RUNNING...")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == "__main__":
    import asyncio
    asyncio.set_event_loop(asyncio.new_event_loop())
    main()