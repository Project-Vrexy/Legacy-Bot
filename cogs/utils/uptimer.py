# StdLib
import datetime

# Third Party
import uptime


class Uptimer:
    def __init__(self, start_time):
        self.start_time = start_time

    def get_bot_uptime(self):
        now = datetime.datetime.utcnow()
        delta = now - self.start_time

        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)

        if days:
            return f"`{days}` days, `{hours}` hours, `{minutes}` minutes, and `{seconds}` seconds."

        else:
            return f"`{hours}` hours, `{minutes}` minutes, and `{seconds}` seconds."
    
    @staticmethod
    def get_sys_uptime():
        hours, remainder = divmod(int(uptime.uptime()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)

        if days:
            return f"`{days}` days, `{hours}` hours, `{minutes}` minutes, and `{seconds}` seconds."

        else:
            return f"`{hours}` hours, `{minutes}` minutes, and `{seconds}` seconds."
