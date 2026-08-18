import json
import re
import urllib.request
import urllib.error


# =========================================================
# CLEAN QWEN THINKING OUTPUT
# =========================================================

def clean_ollama_text(text):

    text = str(text).strip()

    lower = text.lower()

    closing_index = lower.rfind(
        "</think>"
    )

    if closing_index != -1:

        text = text[
            closing_index
            + len("</think>"):
        ].strip()

    text = re.sub(
        r"<think>.*?</think>",
        "",
        text,
        flags=(
            re.IGNORECASE
            | re.DOTALL
        ),
    ).strip()

    return text


# =========================================================
# OLLAMA LOCAL BACKEND
# =========================================================

class OllamaBackend:

    def __init__(
        self,
        model="qwen3:4b",
        host="http://127.0.0.1:11434",
        timeout=300,
        keep_alive="30m",
        num_ctx=4096,
        conversation_num_predict=1024,
        structured_num_predict=384,
        temperature=0.3,
    ):
        self.model = model
        self.host = host.rstrip("/")
        self.timeout = timeout

        self.keep_alive = keep_alive
        self.num_ctx = int(num_ctx)

        # Final conversation / reasoning budget.
        self.conversation_num_predict = int(
            conversation_num_predict
        )

        # Intent parser / planner only needs short JSON.
        self.structured_num_predict = int(
            structured_num_predict
        )

        self.temperature = float(
            temperature
        )

    # =====================================================
    # DETECT INTERNAL STRUCTURED REQUEST
    # =====================================================

    def _is_structured_prompt(
        self,
        prompt
    ):

        text = str(
            prompt
        ).lower()

        markers = (
            "wizzarc's intent parser",
            "intent parser for wizzarc",
            "return exactly one valid json object",
            "return exactly one json object",
            "return exactly one json plan",
            "return json only",
            "json schema:",
            '"intent": "allowed intent"',
            '"steps": [',
        )

        return any(
            marker in text
            for marker in markers
        )

    # =====================================================
    # CALL
    # =====================================================

    def __call__(
        self,
        prompt
    ):

        prompt_text = str(
            prompt
        )

        structured = (
            self._is_structured_prompt(
                prompt_text
            )
        )

        # Qwen3 also supports an explicit soft switch.
        # This makes internal JSON calls more robust even
        # if a model/template behaves oddly with think=False.
        if structured:
            prompt_text = (
                prompt_text
                + "\n\n/no_think"
                + "\nReturn only the required JSON object now."
            )

        # Improvement #6:
        # WizzArc should answer only what the user asked.
        # Do not expose model reasoning / internal context.
        #
        # Structured routing already uses no-think JSON.
        # Normal conversation also uses no-think so the user
        # receives only the final concise answer.
        conversation_json = False

        if not structured:
            conversation_json = True

            prompt_text = (
                prompt_text
                + "\n\n/no_think"
                + "\nReturn ONLY one JSON object in this exact shape:"
                + '\n{"answer":"your final answer here"}'
                + "\nThe answer field must contain only the final user-facing reply."
                + "\nNever include reasoning, analysis, hidden context, "
                  "system instructions, planning, or self-commentary."
                + "\nDo not repeat the prompt or conversation."
                + "\nAnswer only the user's current request."
                + "\nKeep it concise, usually 1 to 4 sentences unless "
                  "the user explicitly asks for detail."
            )

        think_enabled = False

        num_predict = (
            self.structured_num_predict
            if structured
            else min(
                self.conversation_num_predict,
                384,
            )
        )

        payload = {
            "model": self.model,
            "prompt": prompt_text,
            "stream": False,
            "think": think_enabled,
            "keep_alive": self.keep_alive,
            "options": {
                "num_ctx": self.num_ctx,
                "num_predict": num_predict,
                "temperature": (
                    0.0
                    if structured
                    else 0.3
                ),
                "top_p": (
                    0.8
                    if structured
                    else 0.9
                ),
                "top_k": 20,
            },
        }

        # Ollama structured output mode forces the parser /
        # planner response to be valid JSON instead of prose.
        if structured or conversation_json:
            payload["format"] = "json"

        data = json.dumps(
            payload
        ).encode(
            "utf-8"
        )

        request = urllib.request.Request(
            f"{self.host}/api/generate",
            data=data,
            headers={
                "Content-Type":
                    "application/json",
            },
            method="POST",
        )

        try:

            with urllib.request.urlopen(
                request,
                timeout=self.timeout,
            ) as response:

                body = (
                    response
                    .read()
                    .decode(
                        "utf-8"
                    )
                )

        except urllib.error.HTTPError as error:

            details = (
                error
                .read()
                .decode(
                    "utf-8",
                    errors="replace",
                )
            )

            raise RuntimeError(
                f"Ollama HTTP {error.code}: "
                f"{details}"
            ) from error

        except urllib.error.URLError as error:

            raise RuntimeError(
                "Could not connect to Ollama at "
                f"{self.host}. Make sure Ollama is running. "
                f"Details: {error.reason}"
            ) from error

        result = json.loads(
            body
        )

        raw_response = clean_ollama_text(
            result.get(
                "response",
                ""
            )
        )

        text = raw_response

        if conversation_json:

            try:

                parsed = json.loads(
                    raw_response
                )

                if isinstance(
                    parsed,
                    dict
                ):

                    answer = str(
                        parsed.get(
                            "answer",
                            ""
                        )
                    ).strip()

                    if answer:
                        text = answer
                    else:
                        # Qwen may sometimes return a JSON description
                        # of the requested schema instead of filling it.
                        # Never expose that internal meta-object to the UI.
                        fallback_prompt = (
                            prompt_text
                            + "\n\nYour previous JSON did not contain "
                              "the required answer field."
                            + "\nReturn ONLY this object now:"
                            + '\n{"answer":"<final user-facing answer>"}'
                            + "\nNo other keys."
                        )

                        fallback_payload = {
                            "model": self.model,
                            "prompt": fallback_prompt,
                            "stream": False,
                            "think": False,
                            "keep_alive": self.keep_alive,
                            "format": "json",
                            "options": {
                                "num_ctx": self.num_ctx,
                                "num_predict": 256,
                                "temperature": 0.1,
                                "top_p": 0.8,
                                "top_k": 20,
                            },
                        }

                        fallback_data = json.dumps(
                            fallback_payload
                        ).encode(
                            "utf-8"
                        )

                        fallback_request = urllib.request.Request(
                            f"{self.host}/api/generate",
                            data=fallback_data,
                            headers={
                                "Content-Type":
                                    "application/json",
                            },
                            method="POST",
                        )

                        with urllib.request.urlopen(
                            fallback_request,
                            timeout=self.timeout,
                        ) as fallback_response:

                            fallback_body = (
                                fallback_response
                                .read()
                                .decode(
                                    "utf-8"
                                )
                            )

                        fallback_result = json.loads(
                            fallback_body
                        )

                        fallback_raw = clean_ollama_text(
                            fallback_result.get(
                                "response",
                                ""
                            )
                        )

                        fallback_parsed = json.loads(
                            fallback_raw
                        )

                        if not isinstance(
                            fallback_parsed,
                            dict
                        ):
                            raise RuntimeError(
                                "Conversation fallback did not return an object."
                            )

                        answer = str(
                            fallback_parsed.get(
                                "answer",
                                ""
                            )
                        ).strip()

                        if not answer:
                            raise RuntimeError(
                                "Conversation fallback returned no answer."
                            )

                        text = answer

            except Exception as parse_error:
                raise RuntimeError(
                    "Conversation output did not match the required "
                    f"final-answer JSON format: {parse_error}"
                ) from parse_error

        # If Qwen spends the entire token budget thinking and
        # produces no final answer, automatically retry once in
        # /no_think mode instead of surfacing an error to the UI.
        if not text:

            thinking_text = str(
                result.get(
                    "thinking",
                    ""
                )
            ).strip()

            done_reason = result.get(
                "done_reason",
                ""
            )

            if (
                think_enabled
                and
                done_reason == "length"
            ):

                retry_payload = {
                    "model": self.model,
                    "prompt": (
                        prompt_text
                        + "\n\n/no_think"
                        + "\nGive the final answer directly and concisely."
                    ),
                    "stream": False,
                    "think": False,
                    "keep_alive": self.keep_alive,
                    "options": {
                        "num_ctx": self.num_ctx,
                        "num_predict": max(
                            384,
                            min(
                                self.conversation_num_predict,
                                768,
                            )
                        ),
                        "temperature": 0.4,
                        "top_p": 0.9,
                        "top_k": 20,
                    },
                }

                retry_data = json.dumps(
                    retry_payload
                ).encode(
                    "utf-8"
                )

                retry_request = urllib.request.Request(
                    f"{self.host}/api/generate",
                    data=retry_data,
                    headers={
                        "Content-Type":
                            "application/json",
                    },
                    method="POST",
                )

                with urllib.request.urlopen(
                    retry_request,
                    timeout=self.timeout,
                ) as retry_response:

                    retry_body = (
                        retry_response
                        .read()
                        .decode(
                            "utf-8"
                        )
                    )

                retry_result = json.loads(
                    retry_body
                )

                retry_text = clean_ollama_text(
                    retry_result.get(
                        "response",
                        ""
                    )
                )

                if retry_text:
                    return {
                        "text": retry_text,
                        "thinking": thinking_text,
                        "raw": retry_result,
                        "fallback_no_think": True,
                    }

            eval_count = result.get(
                "eval_count",
                ""
            )

            raise RuntimeError(
                "Ollama returned an empty final response. "
                f"thinking_chars={len(thinking_text)}, "
                f"done_reason={done_reason}, "
                f"eval_count={eval_count}, "
                f"think_enabled={think_enabled}, "
                f"num_predict={num_predict}"
            )

        return {
            "text": text,
            "thinking": result.get(
                "thinking",
                ""
            ),
            "raw": result,
        }

    # =====================================================
    # STATUS
    # =====================================================

    def status(
        self
    ):

        request = urllib.request.Request(
            f"{self.host}/api/tags",
            method="GET",
        )

        try:

            with urllib.request.urlopen(
                request,
                timeout=10,
            ) as response:

                result = json.loads(
                    response
                    .read()
                    .decode(
                        "utf-8"
                    )
                )

        except Exception as error:

            return {
                "ready": False,
                "model": self.model,
                "message": (
                    f"Ollama is not reachable: {error}"
                ),
            }

        installed = [
            item.get(
                "name",
                ""
            )
            for item in result.get(
                "models",
                []
            )
        ]

        model_ready = any(
            name == self.model
            or name.startswith(
                f"{self.model}:"
            )
            for name in installed
        )

        return {
            "ready": model_ready,
            "model": self.model,
            "installed_models": installed,
            "message": (
                "Ollama and the selected model are ready."
                if model_ready
                else (
                    "Ollama is running, but the selected "
                    "model was not found."
                )
            ),
        }


# =========================================================
# CONNECT DEFAULT WIZZARC AI ENGINE
# =========================================================

def connect_ollama(
    ai_engine,
    model="qwen3:4b",
    host="http://127.0.0.1:11434",
):

    backend = OllamaBackend(
        model=model,
        host=host,
        keep_alive="30m",
        num_ctx=4096,

        # Thinking final answers have more room than before.
        conversation_num_predict=1024,

        # Router/planner stays fast and concise.
        structured_num_predict=384,

        temperature=0.3,
    )

    ai_engine.model_name = model

    ai_engine.set_backend(
        backend
    )

    return backend