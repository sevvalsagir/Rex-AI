from datetime import datetime, timedelta

attack_times = []
last_email_sent = None

def register_attack():
    global attack_times
    attack_times.append(datetime.now())

def check_alarm(threshold=15, window_sec=30):
    global attack_times
    now = datetime.now()
    recent = [t for t in attack_times if (now - t).total_seconds() < window_sec]
    return len(recent) >= threshold

def should_send_email(cooldown=300):  # 5 dakikada birden fazla atma
    global last_email_sent
    now = datetime.now()
    if not last_email_sent or (now - last_email_sent).total_seconds() > cooldown:
        last_email_sent = now
        return True
    return False
