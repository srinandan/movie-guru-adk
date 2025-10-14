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

from typing import Any
from google.adk.models.lite_llm import LiteLlm
from app.utils.envvars import API_BASE, MODEL, GEMINI25, GEMINI20, OLLAMA


def get_model() -> Any:
    if MODEL == "ollama":
        print(f"using ollama model {OLLAMA}")
        ollama_model = LiteLlm(model=OLLAMA, api_base=API_BASE)
        return ollama_model
    elif MODEL == "gemini-2.0-flash":
        print(f"using gemini 2.0 model {GEMINI20}")
        return GEMINI20
    else:
        print(f"using gemini 2.5 model {GEMINI25}")
        return MODEL
