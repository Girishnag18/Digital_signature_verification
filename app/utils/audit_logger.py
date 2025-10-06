import datetime
def log_action(user, action):
    print(f"[{datetime.datetime.now()}] {user} - {action}")