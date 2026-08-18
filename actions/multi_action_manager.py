# =========================================================
# MULTI ACTION MANAGER
# PHASE 4
# =========================================================


# =========================================================
# SPLIT MULTI COMMAND
# =========================================================

def split_multi_command(command):

    command = (
        str(command)
        .strip()
    )

    if not command:
        return []

    separators = [
        " then ",
        " and then ",
    ]

    parts = [
        command
    ]

    for separator in separators:

        new_parts = []

        for part in parts:

            if separator in part:

                split_parts = part.split(
                    separator
                )

                for item in split_parts:

                    item = item.strip()

                    if item:
                        new_parts.append(
                            item
                        )

            else:

                new_parts.append(
                    part
                )

        parts = new_parts

    return parts


# =========================================================
# CHECK MULTI COMMAND
# =========================================================

def is_multi_command(command):

    command = (
        str(command)
        .lower()
        .strip()
    )

    return (
        " then " in command
        or
        " and then " in command
    )


# =========================================================
# EXECUTE MULTI COMMAND
# =========================================================

def execute_multi_command(
    command,
    executor
):

    commands = split_multi_command(
        command
    )

    if len(commands) <= 1:

        return None

    results = []

    for step_number, sub_command in enumerate(
        commands,
        start=1
    ):

        try:

            result = executor(
                sub_command
            )

        except Exception as error:

            result = (
                f"Step {step_number} failed: "
                f"{error}"
            )

            results.append(
                result
            )

            break

        if result is None:

            result = (
                f"Step {step_number}: "
                f"No result."
            )

        results.append(
            str(result)
        )

    return "\n".join(
        results
    )