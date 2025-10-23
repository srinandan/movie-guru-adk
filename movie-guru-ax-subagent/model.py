# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from typing import Any
from google.adk.models.lite_llm import LiteLlm


API_BASE = os.environ.setdefault("API_BASE", "http://localhost:11434")
GEMINI25 = "gemini-2.5-flash"
GEMINI20 = "gemini-2.0-flash"
OLLAMA_MODEL = os.environ.setdefault("OLLAMA_MODEL","ollama_chat/gemma3:4b")
MODEL = os.environ.setdefault("MODEL", GEMINI25)

def get_model() -> Any:
    if MODEL == "ollama":
        print(f"using ollama model {OLLAMA_MODEL}")
        ollama_model = LiteLlm(model=OLLAMA_MODEL, api_base=API_BASE)
        return ollama_model
    elif MODEL == "gemini-2.0-flash":
        print(f"using gemini 2.0 model {GEMINI20}")
        return GEMINI20
    else:
        print(f"using gemini 2.5 model {GEMINI25}")
        return MODEL
