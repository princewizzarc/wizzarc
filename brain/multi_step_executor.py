from dataclasses import dataclass, field
from typing import Any, List, Optional

from brain.action_planner import (
    ActionPlanner,
    plan_step_to_intent,
)

from brain.tool_executor import (
    ToolExecutor,
)


# =========================================================
# STEP EXECUTION RESULT
# =========================================================

@dataclass
class StepExecutionResult:
    step_number: int
    success: bool
    command: str = ""
    result: Any = None
    error: Optional[str] = None
    intent: Any = None
    confirmation_required: bool = False
    dangerous_action: Any = None


# =========================================================
# MULTI-STEP EXECUTION RESULT
# =========================================================

@dataclass
class MultiStepExecutionResult:
    success: bool
    request: str
    steps: List[StepExecutionResult] = field(
        default_factory=list
    )
    error: Optional[str] = None
    plan: Any = None
    confirmation_required: bool = False
    dangerous_action: Any = None
    pending_command: str = ""


# =========================================================
# MULTI-STEP EXECUTOR
# =========================================================

class MultiStepExecutor:

    def __init__(
        self,
        ai_engine,
        command_executor,
    ):

        self.planner = ActionPlanner(
            ai_engine
        )

        self.tool_executor = ToolExecutor(
            command_executor
        )

    # =====================================================
    # EXECUTE REQUEST
    # =====================================================

    def execute(
        self,
        user_text,
        stop_on_error=True,
    ):

        user_text = str(
            user_text
        ).strip()

        if not user_text:

            return MultiStepExecutionResult(
                success=False,
                request="",
                error="User request is empty.",
            )

        plan = self.planner.plan(
            user_text
        )

        if not plan.success:

            return MultiStepExecutionResult(
                success=False,
                request=user_text,
                error=plan.error,
                plan=plan,
            )

        # =================================================
        # PHASE 9.7 - SECURITY PREFLIGHT
        # =================================================
        #
        # Check the ENTIRE plan before executing step 1.
        # This prevents partial execution when a later step
        # requires user confirmation.
        #
        # Example:
        #   open chrome and then delete file x
        #
        # Without preflight, Chrome could open before WizzArc
        # notices the destructive second step. With preflight,
        # nothing executes until the dangerous action is
        # explicitly confirmed by the user.

        prepared_steps = []

        for step in plan.steps:

            intent = plan_step_to_intent(
                step
            )

            command = (
                self.tool_executor.build_command(
                    intent
                )
            )

            if not command:
                return MultiStepExecutionResult(
                    success=False,
                    request=user_text,
                    error=(
                        f"Step {step.number} has no safe "
                        "command mapping."
                    ),
                    plan=plan,
                )

            dangerous_action = (
                self.tool_executor
                .confirmation_for(
                    command
                )
            )

            if dangerous_action is not None:
                return MultiStepExecutionResult(
                    success=False,
                    request=user_text,
                    error="User confirmation is required.",
                    plan=plan,
                    confirmation_required=True,
                    dangerous_action=dangerous_action,
                    pending_command=command,
                )

            prepared_steps.append(
                (
                    step,
                    intent,
                )
            )

        results = []

        for step, intent in prepared_steps:

            execution = (
                self.tool_executor.execute(
                    intent
                )
            )

            step_result = (
                StepExecutionResult(
                    step_number=step.number,
                    success=execution.success,
                    command=execution.command,
                    result=execution.result,
                    error=execution.error,
                    intent=intent,
                    confirmation_required=(
                        execution.confirmation_required
                    ),
                    dangerous_action=(
                        execution.dangerous_action
                    ),
                )
            )

            results.append(
                step_result
            )

            if (
                stop_on_error
                and
                not execution.success
            ):

                if execution.confirmation_required:
                    return MultiStepExecutionResult(
                        success=False,
                        request=user_text,
                        steps=results,
                        error="User confirmation is required.",
                        plan=plan,
                        confirmation_required=True,
                        dangerous_action=(
                            execution.dangerous_action
                        ),
                        pending_command=(
                            execution.command
                        ),
                    )

                return MultiStepExecutionResult(
                    success=False,
                    request=user_text,
                    steps=results,
                    error=(
                        f"Step {step.number} failed: "
                        f"{execution.error}"
                    ),
                    plan=plan,
                )

        all_success = all(
            item.success
            for item in results
        )

        return MultiStepExecutionResult(
            success=all_success,
            request=user_text,
            steps=results,
            error=(
                None
                if all_success
                else "One or more steps failed."
            ),
            plan=plan,
        )


# =========================================================
# FACTORY
# =========================================================

def create_multi_step_executor(
    ai_engine,
    command_executor,
):

    return MultiStepExecutor(
        ai_engine=ai_engine,
        command_executor=command_executor,
    )