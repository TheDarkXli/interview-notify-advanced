# interview-notify
Push notifications from IRC for your private tracker interviews

<img src="https://i.imgur.com/ZLFyxgY.png">

## features

this script parses log files from your irc client and attempts to be client-agnostic.

it sends push notifications when:
- interviews are happening
- YOUR interview is happening!
- someone mentions you
- you get disconnected from IRC
- you lose your spot in the queue due to a netsplit
- you get kicked

**new in v1.4.0:**
- **GUI application** – optional graphical interface for easy configuration (use `python3 interview_notify_gui.py`)
- **rate limiting** – prevents notification spam during mass events like netsplits (configurable with `--rate-limit`)
- **notification history** – logs all notifications to a file for review (enable with `--notification-log`)
- **multi-channel support** – watch multiple IRC channels simultaneously (specify `--log-dir` multiple times)

## installing

- install python3. i suggest homebrew, winget, or just use the installer: https://www.python.org/downloads/
  - _this script might require python3.11_
- install the `requests` module with `pip3 install requests` (or use `pipenv install` to automatically install dependencies)
- clone this repo
  - `git clone https://github.com/ftc2/interview-notify.git`
- `python3 interview_notify.py`

### for GUI users

if you want to use the GUI, you need tkinter:

- **macOS (Homebrew Python)**: `brew install python-tk@3.13` (or your Python version)
- **macOS (alternative)**: use system Python `/usr/bin/python3 interview_notify_gui.py`
- **Linux (Debian/Ubuntu)**: `sudo apt-get install python3-tk`
- **Linux (Fedora/RHEL)**: `sudo dnf install python3-tkinter`
- **Windows**: tkinter is usually included, if not reinstall Python with tcl/tk option

## using

### GUI (recommended for beginners)

for a user-friendly graphical interface:

```bash
python3 interview_notify_gui.py
```

the GUI provides:
- easy configuration with forms instead of command-line arguments
- start/stop monitoring with buttons
- live log viewer
- save/load configuration
- multi-channel support with add/remove buttons

### command line

for advanced users and automation, use the CLI:

pretty self explanatory if you read the help:

```
./interview_notify.py -h

usage: interview_notify.py [-h] --topic TOPIC [--server SERVER] --log-dir PATH --nick NICK [--check-bot-nicks | --no-check-bot-nicks] [--bot-nicks NICKS] [--mode {red,orp}] [-v] [--version]

IRC Interview Notifier v1.4.0
https://github.com/ftc2/interview-notify

options:
  -h, --help            show this help message and exit
  --topic TOPIC         ntfy topic name to POST notifications to
  --server SERVER       ntfy server to POST notifications to – default: https://ntfy.sh
  --log-dir PATH        path to IRC logs (continuously checks for newest file to parse)
  --nick NICK           your IRC nick
  --check-bot-nicks, --no-check-bot-nicks
                        attempt to parse bot's nick. disable if your log files are not like '<nick> message' – default: enabled
  --bot-nicks NICKS     comma-separated list of bot nicks to watch – default: Gatekeeper
  --mode {red,orp}      interview mode (affects triggers) – default: red
  -v                    verbose (invoke multiple times for more verbosity)
  --version             show program's version number and exit

Sends a push notification with https://ntfy.sh/ when it's your turn to interview.
They have a web client and mobile clients. You can have multiple clients subscribed to this.
Wherever you want notifications: open the client, 'Subscribe to topic', pick a unique topic
  name for this script, and use that everywhere.
On mobile, I suggest enabling the 'Instant delivery' feature as well as 'Keep alerting for
  highest priority'. These will enable fastest and most reliable delivery of the
  notification, and your phone will continuously alarm when your interview is ready.
```

## testing/troubleshooting

first, use `-v` and make sure you can see new messages from IRC showing up:

`interview_notify.py --topic your_topic --log-dir /path/to/logs --nick your_nick -v`

### testing notifications

`interview_notify.py --topic your_topic --log-dir /path/to/logs --nick your_nick --bot-nicks Gatekeeper,your_nick -v`

then type `Currently interviewing: your_nick` in IRC.

if it doesn't work, maybe you have a wonky log file format. try with `--no-check-bot-nicks`:

`interview_notify.py --topic your_topic --log-dir /path/to/logs --nick your_nick --no-check-bot-nicks -v`

## advanced features

### multi-channel support

watch multiple IRC channels simultaneously by specifying `--log-dir` multiple times:

```bash
interview_notify.py --topic your_topic \
  --log-dir /path/to/red/logs \
  --log-dir /path/to/ops/logs \
  --nick your_nick
```

### notification history

log all notifications to a file for review:

```bash
interview_notify.py --topic your_topic --log-dir /path/to/logs --nick your_nick \
  --notification-log ~/interview-notifications.log
```

### rate limiting

prevent notification spam during mass events (like netsplits). default is 60 seconds. critical notifications (your interview, disconnect, kick) are never rate-limited:

```bash
# set rate limit to 120 seconds
interview_notify.py --topic your_topic --log-dir /path/to/logs --nick your_nick \
  --rate-limit 120
```
