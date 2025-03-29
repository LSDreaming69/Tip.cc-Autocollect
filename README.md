# Tip.cc-AutoCollector

An autonomous tip.cc collector bot developed from scratch.

---

## Capabilities

### Core Features

- Autonomous Airdrop Collection ✉️
- Stealthy Phrasedrop Collection 🗣️
- Red Packet Acquisition 🧧

### Advanced Features

- Mathdrop Collection (supports all math functions + anti-detection) ➕➖✖️➗
- Triviadrop Collection (utilizes [OpenTDB](https://github.com/QuartzWarrior/OTDB-Source)) ❓

### Extra Features

- Word Filtering 🚫
- Auto Transfer of Earnings to Primary Account 💸
- Smart Delay: Wait a configurable fraction of the drop duration before claiming ⏳
- Customizable Delay: Set your own min-max delay time ranges ⏰
- Earnings Threshold: Configurable thresholds with percentage chances 💰
- Server and Channel Whitelists/Blacklists: Control where the bot operates 📋
- Banned Words List: Avoids claiming drops with specified words 🙊
- Drop Type Disabling: Choose to disable any specific drop type ❌
- Random Message Responses: Send customizable messages after claiming drops 💬
- Telegram Notifications: Get alerts when drops are claimed 📱
- Per-Server Configurations: Set different settings for different servers 🔧

## Motivation

This bot was developed to address doubts and accusations of code plagiarism on the [Self-bots subreddit](https://www.reddit.com/r/Discord_selfbots/). Rest assured, it is an original creation. ✅

## Setup Guide

1. Install [Python](https://www.python.org/downloads/). 🐍
2. Open your terminal in the downloaded folder. 💻
3. Install dependencies:

- Linux: `python3 -m pip install -U -r requirements.txt`
- Windows: `py -m pip install -U -r requirements.txt`
<!-- markdownlint-disable-next-line MD029 -->
4. Run the script and follow the guided setup process: ▶️

- Linux: `python3 tipcc_autocollect.py`
- Windows: `py tipcc_autocollect.py`

## Configuration

The bot uses two types of configuration files:

1. `config.json` - Global settings for your account
2. `servers/default.json` - Default settings for all servers
3. `servers/{channel_id}.json` - Optional channel-specific settings

The first time you run the script, it will guide you through setting up both configurations.

<!-- markdownlint-disable MD033 -->
<details>
<summary>Global Configuration Options (config.json)</summary>

```json
{
    "TOKEN": "",                   // Your Discord token
    "PRESENCE": "",                // Your presence status (online, idle, dnd, invisible)
    "FIRST": true,                 // First run flag, automatically changes to false
    "ID": 0,                       // Your main account's Discord ID
    "CHANNEL_ID": 0,               // Channel ID where earnings will be sent to your main
    "TARGET_AMOUNT": 0.0,          // Amount to accumulate before transferring
    "CPM": [],                     // [Min, Max] typing speed for transferring
    "WHITELIST": [],               // Server IDs to whitelist
    "BLACKLIST": [],               // Server IDs to blacklist
    "WHITELIST_ON": false,         // Enable server whitelist
    "BLACKLIST_ON": false,         // Enable server blacklist
    "TELEGRAM": {                  // Telegram notification settings
        "TOKEN": "",               // Bot token for notifications
        "CHAT_ID": 0               // Chat ID to send notifications to
    }
}
```

</details>

<details>
<summary>Server Configuration Options (servers/default.json or servers/{channel_id}.json)</summary>

```json
{
    "BANNED_WORDS": [],             // Words that will cause drops to be ignored
    "MESSAGES": [],                 // Messages to potentially send after claiming
    "CHANNEL_WHITELIST": [],        // Channel IDs to whitelist
    "CHANNEL_BLACKLIST": [],        // Channel IDs to blacklist
    "IGNORE_USERS": [],             // User IDs to ignore drops from
    "SEND_MESSAGE": false,          // Whether to send messages after claiming
    "CHANNEL_WHITELIST_ON": false,  // Enable channel whitelist
    "CHANNEL_BLACKLIST_ON": false,  // Enable channel blacklist
    "IGNORE_DROPS_UNDER": 0.0,      // Min USD value to consider claiming
    "IGNORE_TIME_UNDER": 0.0,       // Min time remaining to consider claiming
    "IGNORE_THRESHOLDS": [],        // Value thresholds with ignore chances
    
    // Settings for each drop type (all have similar structure)
    "AIRDROP": {
        "ENABLED": true,            // Whether this drop type is enabled
        "SMART_DELAY": {            // Use relative time-based delay
            "ENABLED": true,
            "DELAY": [0.25, 0.50]   // [Min, Max] fraction of remaining time
        },
        "RANGE_DELAY": false,       // Use absolute time-based delay
        "DELAY": [0, 1],            // [Min, Max] seconds to wait
        "SEND_MESSAGE": false,      // Send message after claiming
        "MESSAGE_CHANCE": 0.5,      // Chance to send message (0-1)
        "MESSAGES": [],             // Specific messages for this drop type
        "IGNORE_DROP_UNDER": 0.0,   // Min value specific to this drop type
        "IGNORE_TIME_UNDER": 0.0,   // Min time specific to this drop type
        "IGNORE_THRESHOLDS": []     // Value thresholds specific to this drop type
    },
    
    // Other drop types have the same structure
    "TRIVIADROP": { /* Same structure as AIRDROP */ },
    "MATHDROP": { /* Same structure plus CPM setting */ },
    "PHRASEDROP": { /* Same structure plus CPM setting */ },
    "REDPACKET": { /* Same structure as AIRDROP */ }
}
```

</details>
<!-- markdownlint-enable MD033 -->

## Disclaimer

---

> Tip.cc-AutoCollector was created for educational purposes only. The developers and contributors do not take any responsibility for your Discord account. ⚠️