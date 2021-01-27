from classes.tsum_monitor import TsumMonitor
import json

try:
    config = json.load(open('config.json'))

    webhooks = config['webhooks']
    refresh_time = config['refresh_time']

    print("Loaded %d proxies"%len(open('proxies.txt').readlines()))
    monitor = TsumMonitor(webhooks, refresh_time)
    monitor.start()

# case where config file is missing
except FileNotFoundError:
    print("FATAL ERROR: Could not find config file")

# case where config file is not valid json
except json.decoder.JSONDecodeError:
    print("FATAL ERROR: Could not read config file, invalid JSON")

# case where we don't know the cause of the exception
except Exception as e:
    print("Unknown error: " + str(e))