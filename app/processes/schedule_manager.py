from croniter import croniter
from datetime import datetime

from app.db import process


def determine_next_schedule(previous_run, hook_cron):
  base = previous_run
  iter = croniter(hook_cron, base)  # every 5 minutes
  return iter.get_next(datetime)


async def run():
  print(" == RUN START PROCESS == ")
  not_scheduled_hooks = await process.find_not_scheduled_hooks()
  print(" == RUN found not_scheduled_hooks ", not_scheduled_hooks)
  for not_scheduled_hook in not_scheduled_hooks:
    print(" == RUN found not_scheduled_hook ", not_scheduled_hook.id)
    previous_run = await process.find_previous_runs(not_scheduled_hook.id)

    if not previous_run:
      previous_run = datetime.now()

    next_tick = determine_next_schedule(previous_run, not_scheduled_hook.cron)

    print(" == RUN adding run not_scheduled_hook.id, next_tick ", not_scheduled_hook.id, next_tick)
    await process.add_run(not_scheduled_hook.id, next_tick)

  print(" == RUN END PROCESS == ")


