from __future__ import annotations

import statistics
import time


def measure(label, func, runs=1):
    times = []
    value = None

    for _ in range(runs):
        started = time.perf_counter()
        value = func()
        elapsed = time.perf_counter() - started
        times.append(elapsed)

    avg = statistics.mean(times)

    print(
        f"{label:<34} "
        f"{avg:>7.2f}s"
    )

    return avg, value


def main():

    print("=" * 70)
    print("WizzArc Phase 9.4 - AI Performance Benchmark")
    print("=" * 70)

    from brain.ai_engine import AI_ENGINE
    from brain.ollama_backend import connect_ollama
    from brain.intent_engine import IntentEngine
    from brain.ai_controller import AIController

    connect_ollama(
        AI_ENGINE
    )

    controller = AIController(
        AI_ENGINE,
        lambda command: f"DRY: {command}",
    )

    intent_engine = IntentEngine(
        AI_ENGINE
    )

    print()
    print("Warming model...")

    warm_start = time.perf_counter()

    try:
        AI_ENGINE.generate(
            "Reply with only: ready"
        )
    except Exception as error:
        raise RuntimeError(
            f"Ollama warm-up failed: {error}"
        ) from error

    warm_time = (
        time.perf_counter()
        - warm_start
    )

    print(
        f"Warm-up/load time: {warm_time:.2f}s"
    )

    print()
    print("-" * 70)
    print("BENCHMARK")
    print("-" * 70)

    direct_time, direct_value = measure(
        "Direct AI final answer",
        lambda: AI_ENGINE.generate(
            "What is Python? Answer in one short sentence."
        ),
    )

    intent_action_time, action_intent = measure(
        "Intent recognition - action",
        lambda: intent_engine.understand(
            "open notepad"
        ),
    )

    intent_chat_time, chat_intent = measure(
        "Intent recognition - conversation",
        lambda: intent_engine.understand(
            "What is Python?"
        ),
    )

    controller_action_time, controller_action = measure(
        "Controller - action",
        lambda: controller.handle(
            "open notepad"
        ),
    )

    controller_chat_time, controller_chat = measure(
        "Controller - conversation",
        lambda: controller.handle(
            "What is Python? Answer briefly."
        ),
    )

    controller_multi_time, controller_multi = measure(
        "Controller - multi action",
        lambda: controller.handle(
            "open chrome and search youtube for python tutorial"
        ),
    )

    print()
    print("-" * 70)
    print("RESULT DETAILS")
    print("-" * 70)

    print(
        "Direct answer:",
        str(direct_value)[:240],
    )

    print(
        "Action intent:",
        getattr(
            action_intent,
            "intent",
            None,
        ),
        "/",
        getattr(
            action_intent,
            "action",
            None,
        ),
    )

    print(
        "Chat intent:",
        getattr(
            chat_intent,
            "intent",
            None,
        ),
    )

    print(
        "Controller action route:",
        getattr(
            controller_action,
            "route",
            None,
        ),
    )

    print(
        "Controller chat route:",
        getattr(
            controller_chat,
            "route",
            None,
        ),
    )

    print(
        "Controller multi route:",
        getattr(
            controller_multi,
            "route",
            None,
        ),
    )

    print()
    print("-" * 70)
    print("QUICK DIAGNOSIS")
    print("-" * 70)

    extra_chat = (
        controller_chat_time
        - direct_time
    )

    print(
        f"Conversation overhead vs direct AI: "
        f"{extra_chat:.2f}s"
    )

    if (
        direct_time > 8
    ):
        print(
            "Main bottleneck appears to be local model generation."
        )
    elif (
        extra_chat > 3
    ):
        print(
            "Main bottleneck appears to be controller/intent routing "
            "before the final answer."
        )
    else:
        print(
            "AI pipeline overhead looks reasonable; "
            "optimization can focus on smaller latency reductions."
        )

    print()
    print("PHASE 9.4 BENCHMARK: COMPLETE")


if __name__ == "__main__":
    main()