import httpx
from datetime import datetime

from app.db import process


def make_call(verb, url):
    # fetch only up to 10kb
    # timeout in 60 seconds
    print(f" == HIT >> start: {verb} {url}")

    if verb == 'GET':
        return httpx.get(url)
    if verb == 'POST':
        return httpx.post(url)

    print(f" == HIT << finished call: {verb} {url}")

async def run():
    print(" == HIT START PROCESS == ")
    # retrieve all scheduled hooks (ticks without effectively ran at)
    hooks = await process.find_pending_runs()
    # update the effectivelly ran for each
    for hook in hooks:
        try:
            print(" == HIT run.id, hook.id, url, cron == ", hook.run_id, hook.id, hook.url, hook.cron)

            started_at = datetime.now()
            # TODO: deal with time zones eventually

            # update the run date time of start
            await process.update_run_effectively_run(hook.run_id, started_at)

            try:
                print(" == HIT make call", hook.method, hook.url)
                res = make_call(hook.method, hook.url)
                response_text = res.text
                finished_at = datetime.now()
                # update last hit date on hook
                print(" == HIT update_hook_last_hit", hook.id, started_at)
                await process.update_hook_last_hit(hook.id, started_at)
                # create a hits record with the response of the http call
                print(" == HIT response ", res.text, res.status_code)
                await process.add_hit(hook.id, res.status_code, response_text, started_at, finished_at)
            except Exception as e:
                print(" == HIT EXCEPTION ", e)
                finished_at = datetime.now()

                # create a hits record with the error, but don't update the last hit
                await process.add_hit(hook.id, None, str(e), started_at, finished_at)

        except Exception as e:
            print(" == HIT MAIN EXCEPTION ", e)

    print(" == HIT END PROCESS == ")









