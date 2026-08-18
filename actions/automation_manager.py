import threading
import re
import time
from datetime import datetime, timedelta


from actions.automation_persistence import (
    load_automation_data,
    save_persistent_automation,
    remove_persistent_automation,
    text_to_datetime,
)


# =========================================================
# ACTIVE AUTOMATIONS
# =========================================================

ACTIVE_AUTOMATIONS = {}

AUTOMATION_COUNTER = 0

AUTOMATION_LOCK = threading.Lock()


# =========================================================
# CREATE AUTOMATION ID
# =========================================================

def create_automation_id():

    global AUTOMATION_COUNTER

    with AUTOMATION_LOCK:

        while True:

            AUTOMATION_COUNTER += 1

            automation_id = (
                f"automation_{AUTOMATION_COUNTER}"
            )

            if (
                automation_id
                not in ACTIVE_AUTOMATIONS
            ):

                return automation_id


# =========================================================
# RESERVE / PRESERVE AUTOMATION ID
# =========================================================

def reserve_automation_id(
    preferred_id=None
):

    global AUTOMATION_COUNTER

    preferred_id = (
        str(preferred_id)
        .strip()
        if preferred_id is not None
        else ""
    )

    if not preferred_id:

        return create_automation_id()

    with AUTOMATION_LOCK:

        if preferred_id in ACTIVE_AUTOMATIONS:

            return None

        match = re.fullmatch(
            r"automation_(\d+)",
            preferred_id
        )

        if match:

            number = int(
                match.group(1)
            )

            if number > AUTOMATION_COUNTER:

                AUTOMATION_COUNTER = number

        return preferred_id


# =========================================================
# PARSE DURATION
# =========================================================

def parse_duration(
    value,
    unit
):

    try:

        value = float(
            value
        )

    except (
        TypeError,
        ValueError,
    ):

        return None

    if value <= 0:

        return None

    unit = (
        str(unit)
        .lower()
        .strip()
    )

    if unit.endswith("s"):

        unit = unit[:-1]

    multipliers = {
        "second": 1,
        "minute": 60,
        "hour": 3600,
    }

    multiplier = multipliers.get(
        unit
    )

    if multiplier is None:

        return None

    return (
        value
        * multiplier
    )


# =========================================================
# PARSE CLOCK TIME
# =========================================================

def parse_clock_time(
    time_text
):

    time_text = (
        str(time_text)
        .lower()
        .strip()
    )

    formats = [
        "%I:%M %p",
        "%I %p",
        "%H:%M",
    ]

    for fmt in formats:

        try:

            parsed = datetime.strptime(
                time_text,
                fmt
            )

            return (
                parsed.hour,
                parsed.minute
            )

        except ValueError:

            continue

    return None


# =========================================================
# GET TARGET CLOCK DATETIME
# =========================================================

def get_target_datetime(
    time_text
):

    parsed = parse_clock_time(
        time_text
    )

    if parsed is None:

        return None

    hour, minute = parsed

    now = datetime.now()

    target = now.replace(
        hour=hour,
        minute=minute,
        second=0,
        microsecond=0
    )

    if target <= now:

        target += timedelta(
            days=1
        )

    return target


# =========================================================
# GET DELAY UNTIL CLOCK TIME
# =========================================================

def get_delay_until_time(
    time_text
):

    target = get_target_datetime(
        time_text
    )

    if target is None:

        return None

    now = datetime.now()

    return (
        target - now
    ).total_seconds()


# =========================================================
# FORMAT DATETIME
# =========================================================

def format_datetime(
    date_time
):

    if date_time is None:

        return "Unknown"

    try:

        return date_time.strftime(
            "%d %b %Y, %I:%M:%S %p"
        )

    except Exception:

        return str(
            date_time
        )


# =========================================================
# FORMAT REMAINING TIME
# =========================================================

def format_remaining_time(
    seconds
):

    try:

        seconds = int(
            max(
                0,
                seconds
            )
        )

    except Exception:

        return "Unknown"

    hours = (
        seconds // 3600
    )

    minutes = (
        (seconds % 3600)
        // 60
    )

    secs = (
        seconds % 60
    )

    parts = []

    if hours:

        parts.append(
            (
                f"{hours} hour"
                f"{'s' if hours != 1 else ''}"
            )
        )

    if minutes:

        parts.append(
            (
                f"{minutes} minute"
                f"{'s' if minutes != 1 else ''}"
            )
        )

    if secs or not parts:

        parts.append(
            (
                f"{secs} second"
                f"{'s' if secs != 1 else ''}"
            )
        )

    return " ".join(
        parts
    )


# =========================================================
# SYNC PERSISTENT AUTOMATION STATE
# =========================================================

def sync_persistent_automation(
    automation_id
):

    automation_id = (
        str(automation_id)
        .strip()
    )

    if not automation_id:

        return False

    with AUTOMATION_LOCK:

        automation = (
            ACTIVE_AUTOMATIONS.get(
                automation_id
            )
        )

        if not automation:

            return False

        if not automation.get(
            "persistent"
        ):

            return False

        automation_copy = dict(
            automation
        )

    return save_persistent_automation(
        automation_copy
    )


# =========================================================
# AUTOMATION SAFETY CHECK
# =========================================================

def is_unsafe_automation_command(
    command
):

    command = (
        str(command)
        .lower()
        .strip()
    )

    blocked_exact = {
        "shutdown",
        "restart",
        "lock computer",
    }

    if command in blocked_exact:

        return True

    blocked_prefixes = [
        "delete file ",
        "delete folder ",
    ]

    for prefix in blocked_prefixes:

        if command.startswith(
            prefix
        ):

            return True

    return False


# =========================================================
# RUN DELAYED COMMAND
# =========================================================

def _run_delayed_command(
    automation_id,
    delay_seconds,
    command,
    executor
):

    try:

        time.sleep(
            delay_seconds
        )

        with AUTOMATION_LOCK:

            automation = (
                ACTIVE_AUTOMATIONS.get(
                    automation_id
                )
            )

            if not automation:

                return

            if automation.get(
                "cancelled"
            ):

                return

            stop_at = automation.get(
                "stop_at"
            )

            if (
                stop_at is not None
                and
                datetime.now() >= stop_at
            ):

                automation[
                    "status"
                ] = "completed"

                automation[
                    "completed_at"
                ] = datetime.now()

                automation[
                    "run_at"
                ] = None

                return

            automation[
                "status"
            ] = "running"

        result = executor(
            command
        )

        with AUTOMATION_LOCK:

            if automation_id in ACTIVE_AUTOMATIONS:

                ACTIVE_AUTOMATIONS[
                    automation_id
                ][
                    "result"
                ] = result

                ACTIVE_AUTOMATIONS[
                    automation_id
                ][
                    "status"
                ] = "completed"

                ACTIVE_AUTOMATIONS[
                    automation_id
                ][
                    "completed_at"
                ] = datetime.now()

                was_persistent = bool(
                    ACTIVE_AUTOMATIONS[
                        automation_id
                    ].get(
                        "persistent"
                    )
                )

        if was_persistent:

            remove_persistent_automation(
                automation_id
            )

    except Exception as error:

        with AUTOMATION_LOCK:

            if automation_id in ACTIVE_AUTOMATIONS:

                ACTIVE_AUTOMATIONS[
                    automation_id
                ][
                    "result"
                ] = str(error)

                ACTIVE_AUTOMATIONS[
                    automation_id
                ][
                    "status"
                ] = "failed"


# =========================================================
# SCHEDULE DELAYED COMMAND
# =========================================================

def schedule_delayed_command(
    command,
    delay_seconds,
    executor,
    automation_id=None,
    persistent=False
):

    try:

        delay_seconds = float(
            delay_seconds
        )

    except (
        TypeError,
        ValueError,
    ):

        return (
            "Delay must be a number."
        )

    if delay_seconds <= 0:

        return (
            "Delay must be greater than 0."
        )

    command = (
        str(command)
        .strip()
    )

    if not command:

        return (
            "Command is empty."
        )

    if is_unsafe_automation_command(
        command
    ):

        return (
            "For safety, this command cannot "
            "run automatically."
        )

    automation_id = reserve_automation_id(
        automation_id
    )

    if automation_id is None:

        return (
            "That automation ID is already active."
        )

    created_at = (
        datetime.now()
    )

    run_at = (
        created_at
        + timedelta(
            seconds=delay_seconds
        )
    )

    automation_data = {
        "id":
            automation_id,

        "command":
            command,

        "automation_type":
            "delayed",

        "delay_seconds":
            delay_seconds,

        "created_at":
            created_at,

        "run_at":
            run_at,

        "completed_at":
            None,

        "last_run_at":
            None,

        "status":
            "waiting",

        "cancelled":
            False,

        "persistent":
            bool(persistent),

        "result":
            None,
    }

    with AUTOMATION_LOCK:

        ACTIVE_AUTOMATIONS[
            automation_id
        ] = automation_data

    thread = threading.Thread(
        target=_run_delayed_command,
        args=(
            automation_id,
            delay_seconds,
            command,
            executor,
        ),
        daemon=True
    )

    thread.start()

    return (
        f"Automation scheduled. "
        f"ID: {automation_id}. "
        f"Command: '{command}'. "
        f"Scheduled for: "
        f"{format_datetime(run_at)}."
    )


# =========================================================
# RUN REPEATING COMMAND
# =========================================================

def _run_repeating_command(
    automation_id,
    interval_seconds,
    command,
    executor,
    max_runs=None,
    stop_after_seconds=None
):

    while True:

        with AUTOMATION_LOCK:

            automation = (
                ACTIVE_AUTOMATIONS.get(
                    automation_id
                )
            )

            if not automation:
                return

            if automation.get(
                "cancelled"
            ):
                return

            stop_at = automation.get(
                "stop_at"
            )

            if (
                stop_at is not None
                and
                datetime.now() >= stop_at
            ):

                automation[
                    "status"
                ] = "completed"

                automation[
                    "completed_at"
                ] = datetime.now()

                automation[
                    "run_at"
                ] = None

                return

        time.sleep(
            interval_seconds
        )

        with AUTOMATION_LOCK:

            automation = (
                ACTIVE_AUTOMATIONS.get(
                    automation_id
                )
            )

            if not automation:

                return

            if automation.get(
                "cancelled"
            ):

                return

            automation[
                "status"
            ] = "running"

        try:

            result = executor(
                command
            )

            now = datetime.now()

            with AUTOMATION_LOCK:

                if automation_id not in ACTIVE_AUTOMATIONS:

                    return

                data = ACTIVE_AUTOMATIONS[
                    automation_id
                ]

                data[
                    "result"
                ] = result

                data[
                    "last_run_at"
                ] = now

                data[
                    "run_count"
                ] = (
                    data.get(
                        "run_count",
                        0
                    )
                    + 1
                )

                if (
                    max_runs is not None
                    and
                    data[
                        "run_count"
                    ]
                    >= max_runs
                ):

                    data[
                        "status"
                    ] = "completed"

                    data[
                        "completed_at"
                    ] = now

                    data[
                        "run_at"
                    ] = None

                    was_persistent = bool(
                        data.get(
                            "persistent"
                        )
                    )

                if was_persistent:

                    remove_persistent_automation(
                        automation_id
                    )

                return

                data[
                    "status"
                ] = "waiting"

                data[
                    "run_at"
                ] = (
                    now
                    + timedelta(
                        seconds=interval_seconds
                    )
                )

            sync_persistent_automation(
                automation_id
            )

        except Exception as error:

            with AUTOMATION_LOCK:

                if automation_id in ACTIVE_AUTOMATIONS:

                    ACTIVE_AUTOMATIONS[
                        automation_id
                    ][
                        "result"
                    ] = str(error)

                    ACTIVE_AUTOMATIONS[
                        automation_id
                    ][
                        "status"
                    ] = "failed"

            return


# =========================================================
# SCHEDULE REPEATING COMMAND
# =========================================================

def schedule_repeating_command(
    command,
    interval_seconds,
    executor,
    max_runs=None,
    stop_after_seconds=None,
    automation_id=None,
    initial_run_count=0,
    persistent=False
):

    try:

        interval_seconds = float(
            interval_seconds
        )

    except (
        TypeError,
        ValueError,
    ):

        return (
            "Interval must be a number."
        )

    if interval_seconds <= 0:

        return (
            "Interval must be greater than 0."
        )

    if max_runs is not None:

        try:

            max_runs = int(
                max_runs
            )

        except (
            TypeError,
            ValueError,
        ):

            return (
                "Repeat count must be a number."
            )

        if max_runs <= 0:

            return (
                "Repeat count must be greater than 0."
            )

    if stop_after_seconds is not None:

        try:

            stop_after_seconds = float(
                stop_after_seconds
            )

        except (
            TypeError,
            ValueError,
        ):

            return (
                "Stop-after duration must be a number."
            )

        if stop_after_seconds <= 0:

            return (
                "Stop-after duration must be greater than 0."
            )

        if stop_after_seconds < interval_seconds:

            return (
                "Stop-after duration must be at least "
                "as long as the repeat interval."
            )

    try:

        initial_run_count = int(
            initial_run_count
        )

    except (
        TypeError,
        ValueError,
    ):

        initial_run_count = 0

    if initial_run_count < 0:

        initial_run_count = 0

    command = (
        str(command)
        .strip()
    )

    if not command:

        return (
            "Command is empty."
        )

    if is_unsafe_automation_command(
        command
    ):

        return (
            "For safety, this command cannot "
            "run automatically."
        )

    automation_id = reserve_automation_id(
        automation_id
    )

    if automation_id is None:

        return (
            "That automation ID is already active."
        )

    created_at = datetime.now()

    next_run = (
        created_at
        + timedelta(
            seconds=interval_seconds
        )
    )

    stop_at = None

    if stop_after_seconds is not None:

        stop_at = (
            created_at
            + timedelta(
                seconds=stop_after_seconds
            )
        )

    automation_data = {
        "id":
            automation_id,

        "command":
            command,

        "automation_type":
            "repeating",

        "interval_seconds":
            interval_seconds,

        "created_at":
            created_at,

        "run_at":
            next_run,

        "completed_at":
            None,

        "last_run_at":
            None,

        "run_count":
            initial_run_count,

        "max_runs":
            max_runs,

        "stop_after_seconds":
            stop_after_seconds,

        "stop_at":
            stop_at,

        "status":
            "waiting",

        "cancelled":
            False,

        "persistent":
            bool(persistent),

        "result":
            None,
    }

    with AUTOMATION_LOCK:

        ACTIVE_AUTOMATIONS[
            automation_id
        ] = automation_data

    thread = threading.Thread(
        target=_run_repeating_command,
        args=(
            automation_id,
            interval_seconds,
            command,
            executor,
            max_runs,
            stop_after_seconds,
        ),
        daemon=True
    )

    thread.start()

    message = (
        f"Repeating automation scheduled. "
        f"ID: {automation_id}. "
        f"Command: '{command}'. "
        f"Repeats every "
        f"{format_remaining_time(interval_seconds)}."
    )

    if max_runs is not None:

        message += (
            f" It will run "
            f"{max_runs} time"
            f"{'s' if max_runs != 1 else ''}."
        )

    if stop_after_seconds is not None:

        message += (
            f" It will stop after "
            f"{format_remaining_time(stop_after_seconds)}."
        )

    return message


# =========================================================
# CANCEL AUTOMATION
# =========================================================

def cancel_automation(
    automation_id
):

    automation_id = (
        str(automation_id)
        .strip()
    )

    with AUTOMATION_LOCK:

        automation = (
            ACTIVE_AUTOMATIONS.get(
                automation_id
            )
        )

        if not automation:

            return (
                f"Automation "
                f"'{automation_id}' "
                "was not found."
            )

        status = automation.get(
            "status"
        )

        if status == "completed":

            return (
                f"Automation "
                f"'{automation_id}' "
                "has already completed."
            )

        if status == "cancelled":

            return (
                f"Automation "
                f"'{automation_id}' "
                "is already cancelled."
            )

        automation[
            "cancelled"
        ] = True

        automation[
            "status"
        ] = "cancelled"

        was_persistent = bool(
            automation.get(
                "persistent"
            )
        )

    if was_persistent:

        remove_persistent_automation(
            automation_id
        )

    return (
        f"Automation "
        f"'{automation_id}' cancelled."
    )


# =========================================================
# LIST AUTOMATIONS
# =========================================================

def list_automations():

    with AUTOMATION_LOCK:

        if not ACTIVE_AUTOMATIONS:

            return (
                "No automations found."
            )

        now = datetime.now()

        lines = [
            "Automations:",
            "",
        ]

        for automation_id, data in (
            ACTIVE_AUTOMATIONS.items()
        ):

            status = data.get(
                "status",
                "unknown"
            )

            run_at = data.get(
                "run_at"
            )

            automation_type = data.get(
                "automation_type",
                "delayed"
            )

            lines.append(
                f"ID: {automation_id}"
            )

            lines.append(
                (
                    f"Type: "
                    f"{automation_type}"
                )
            )

            lines.append(
                (
                    f"Command: "
                    f"{data.get('command', '')}"
                )
            )

            lines.append(
                f"Status: {status}"
            )

            lines.append(
                (
                    "Next run: "
                    + format_datetime(
                        run_at
                    )
                )
            )

            if (
                automation_type
                == "repeating"
            ):

                interval_seconds = data.get(
                    "interval_seconds"
                )

                if interval_seconds is not None:

                    lines.append(
                        (
                            "Repeats every: "
                            + format_remaining_time(
                                interval_seconds
                            )
                        )
                    )

                run_count = data.get(
                    "run_count",
                    0
                )

                max_runs = data.get(
                    "max_runs"
                )

                lines.append(
                    f"Run count: {run_count}"
                )

                if max_runs is not None:

                    lines.append(
                        f"Max runs: {max_runs}"
                    )

                stop_after_seconds = data.get(
                    "stop_after_seconds"
                )

                if stop_after_seconds is not None:

                    lines.append(
                        (
                            "Stop after: "
                            + format_remaining_time(
                                stop_after_seconds
                            )
                        )
                    )

                stop_at = data.get(
                    "stop_at"
                )

                if stop_at is not None:

                    lines.append(
                        (
                            "Stops at: "
                            + format_datetime(
                                stop_at
                            )
                        )
                    )

                last_run_at = data.get(
                    "last_run_at"
                )

                if last_run_at is not None:

                    lines.append(
                        (
                            "Last run: "
                            + format_datetime(
                                last_run_at
                            )
                        )
                    )

            if (
                status == "waiting"
                and
                run_at is not None
            ):

                remaining = (
                    run_at
                    - now
                ).total_seconds()

                lines.append(
                    (
                        "Remaining: "
                        + format_remaining_time(
                            remaining
                        )
                    )
                )

            if (
                status == "completed"
            ):

                completed_at = data.get(
                    "completed_at"
                )

                if completed_at:

                    lines.append(
                        (
                            "Completed at: "
                            + format_datetime(
                                completed_at
                            )
                        )
                    )

            if (
                data.get(
                    "result"
                )
                is not None
            ):

                lines.append(
                    (
                        f"Result: "
                        f"{data['result']}"
                    )
                )

            lines.append("")

    return "\n".join(
        lines
    )


# =========================================================
# SAVE ACTIVE AUTOMATION PERMANENTLY
# =========================================================

def save_automation(
    automation_id
):

    automation_id = (
        str(automation_id)
        .strip()
    )

    if not automation_id:

        return (
            "Please tell me which automation to save."
        )

    with AUTOMATION_LOCK:

        automation = (
            ACTIVE_AUTOMATIONS.get(
                automation_id
            )
        )

        if not automation:

            return (
                f"Automation '{automation_id}' "
                "was not found."
            )

        status = automation.get(
            "status"
        )

        if status in {
            "completed",
            "cancelled",
            "failed",
        }:

            return (
                f"Automation '{automation_id}' "
                f"cannot be saved because its "
                f"status is {status}."
            )

        automation[
            "persistent"
        ] = True

        automation_copy = dict(
            automation
        )

    saved = save_persistent_automation(
        automation_copy
    )

    if not saved:

        with AUTOMATION_LOCK:

            if automation_id in ACTIVE_AUTOMATIONS:

                ACTIVE_AUTOMATIONS[
                    automation_id
                ][
                    "persistent"
                ] = False

        return (
            f"Couldn't save automation "
            f"'{automation_id}'."
        )

    return (
        f"Automation '{automation_id}' "
        "saved permanently."
    )


# =========================================================
# REMOVE SAVED AUTOMATION
# =========================================================

def remove_saved_automation(
    automation_id
):

    automation_id = (
        str(automation_id)
        .strip()
    )

    if not automation_id:

        return (
            "Please tell me which saved "
            "automation to remove."
        )

    saved_items = load_automation_data()

    exists = any(
        item.get(
            "id"
        )
        == automation_id
        for item in saved_items
    )

    if not exists:

        return (
            f"Saved automation "
            f"'{automation_id}' "
            "was not found."
        )

    removed = remove_persistent_automation(
        automation_id
    )

    if not removed:

        return (
            f"Couldn't remove saved automation "
            f"'{automation_id}'."
        )

    with AUTOMATION_LOCK:

        if automation_id in ACTIVE_AUTOMATIONS:

            ACTIVE_AUTOMATIONS[
                automation_id
            ][
                "persistent"
            ] = False

    return (
        f"Saved automation "
        f"'{automation_id}' removed."
    )


# =========================================================
# SHOW SAVED AUTOMATIONS
# =========================================================

def list_saved_automations():

    saved_items = load_automation_data()

    if not saved_items:

        return (
            "No saved automations found."
        )

    lines = [
        "Saved automations:",
        "",
    ]

    for item in saved_items:

        automation_id = item.get(
            "id",
            "unknown"
        )

        command = item.get(
            "command",
            ""
        )

        automation_type = item.get(
            "automation_type",
            "unknown"
        )

        run_at = item.get(
            "run_at"
        )

        stop_at = item.get(
            "stop_at"
        )

        lines.append(
            f"ID: {automation_id}"
        )

        lines.append(
            f"Type: {automation_type}"
        )

        lines.append(
            f"Command: {command}"
        )

        if run_at:

            lines.append(
                f"Saved next run: {run_at}"
            )

        if stop_at:

            lines.append(
                f"Saved stop time: {stop_at}"
            )

        max_runs = item.get(
            "max_runs"
        )

        if max_runs is not None:

            lines.append(
                f"Max runs: {max_runs}"
            )

        run_count = item.get(
            "run_count"
        )

        if run_count is not None:

            lines.append(
                f"Run count: {run_count}"
            )

        lines.append("")

    return "\n".join(
        lines
    )


# =========================================================
# RESTORE SAVED AUTOMATIONS
# =========================================================

def restore_saved_automations(
    executor
):

    saved_items = load_automation_data()

    if not saved_items:

        return (
            "No saved automations to restore."
        )

    restored = 0
    skipped = 0

    now = datetime.now()

    for item in saved_items:

        command = (
            str(
                item.get(
                    "command",
                    ""
                )
            )
            .strip()
        )

        if not command:

            skipped += 1
            continue

        automation_type = item.get(
            "automation_type"
        )

        saved_id = item.get(
            "id"
        )

        # =================================================
        # REPEATING AUTOMATION
        # =================================================

        if automation_type == "repeating":

            interval_seconds = item.get(
                "interval_seconds"
            )

            try:
                interval_seconds = float(
                    interval_seconds
                )
            except (
                TypeError,
                ValueError,
            ):
                skipped += 1
                continue

            if interval_seconds <= 0:
                skipped += 1
                continue

            stop_at = text_to_datetime(
                item.get(
                    "stop_at"
                )
            )

            if (
                stop_at is not None
                and
                stop_at <= now
            ):

                skipped += 1

                if saved_id:
                    remove_persistent_automation(
                        saved_id
                    )

                continue

            max_runs = item.get(
                "max_runs"
            )

            try:
                old_run_count = int(
                    item.get(
                        "run_count",
                        0
                    )
                    or 0
                )
            except (
                TypeError,
                ValueError,
            ):
                old_run_count = 0

            if max_runs is not None:

                try:
                    max_runs = int(
                        max_runs
                    )
                except (
                    TypeError,
                    ValueError,
                ):
                    max_runs = None

                if max_runs is not None:

                    if old_run_count >= max_runs:

                        skipped += 1

                        if saved_id:
                            remove_persistent_automation(
                                saved_id
                            )

                        continue

            stop_after_seconds = None

            if stop_at is not None:

                stop_after_seconds = (
                    stop_at
                    - now
                ).total_seconds()

                if stop_after_seconds <= 0:

                    skipped += 1

                    if saved_id:
                        remove_persistent_automation(
                            saved_id
                        )

                    continue

            schedule_repeating_command(
                command,
                interval_seconds,
                executor,
                max_runs=max_runs,
                stop_after_seconds=stop_after_seconds,
                automation_id=saved_id,
                initial_run_count=old_run_count,
                persistent=True
            )

            restored += 1
            continue

        # =================================================
        # ONE-TIME / DELAYED AUTOMATION
        # =================================================

        run_at = text_to_datetime(
            item.get(
                "run_at"
            )
        )

        if run_at is None:

            skipped += 1
            continue

        if run_at <= now:

            skipped += 1

            if saved_id:
                remove_persistent_automation(
                    saved_id
                )

            continue

        delay_seconds = (
            run_at
            - now
        ).total_seconds()

        schedule_delayed_command(
            command,
            delay_seconds,
            executor,
            automation_id=saved_id,
            persistent=True
        )

        restored += 1

    return (
        f"Restored {restored} "
        f"automation(s). "
        f"Skipped {skipped}."
    )


# =========================================================
# CLEAR FINISHED AUTOMATIONS
# =========================================================

def clear_finished_automations():

    removed = 0

    with AUTOMATION_LOCK:

        automation_ids = list(
            ACTIVE_AUTOMATIONS.keys()
        )

        for automation_id in automation_ids:

            status = (
                ACTIVE_AUTOMATIONS[
                    automation_id
                ].get(
                    "status"
                )
            )

            if status in {
                "completed",
                "cancelled",
                "failed",
            }:

                del ACTIVE_AUTOMATIONS[
                    automation_id
                ]

                removed += 1

    return (
        f"Removed {removed} finished "
        f"automation(s)."
    )