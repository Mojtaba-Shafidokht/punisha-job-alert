import schedule
import time
from main import run_scrape_cycle

run_scrape_cycle()

schedule.every(1).hours.do(run_scrape_cycle)

try:
    while True:
        try:
            schedule.run_pending()

        except Exception as e:
            print(f"⚠️ Unexpected error during scheduled run: {e}")
        time.sleep(60)

except KeyboardInterrupt:
    print("\n👋 Scheduler stopped by user.")
