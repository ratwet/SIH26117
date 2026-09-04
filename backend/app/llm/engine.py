"""
SovereignWorkbench — Unified LLM Serving Engine (app/llm/engine.py)
Orchestrates enterprise foundation models for air-gapped refinery engineering:
- Laptop/Edge (8B/3B Tier): Ollama OpenAI-compatible endpoint (http://127.0.0.1:11434/v1)
- Datacenter (100B+ Tier): vLLM / SGLang multi-GPU cluster (e.g., http://127.0.0.1:8001/v1)

Hardware Scaling Formula:
- Laptop:   Qwen 2.5 3B/8B, DeepSeek-R1 8B via Ollama
- Cluster:  DeepSeek-R1 671B/70B, Qwen-2.5 72B, Qwen2-VL 72B via vLLM TP=4

Strict Air-Gapped Policy:
- If no model server is connected, the system refuses to run and raises ConnectionError.
- Emulation is strictly disabled unless explicitly opted-in via settings.ALLOW_EMULATION = True.
"""

import json
import logging
import re
from typing import Dict, Any, Optional, Tuple, List
import httpx

from app.config import settings

logger = logging.getLogger("sovereign_llm_engine")


def normalize_v1_url(url: str) -> str:
    """Ensure URL has scheme and ends with /v1 without duplicate slashes."""
    url = url.strip()
    if not url.startswith("http://") and not url.startswith("https://"):
        url = f"http://{url}"
    url = url.rstrip("/")
    if not url.endswith("/v1"):
        url = f"{url}/v1"
    return url


class FoundationModelEngine:
    """
    Production-grade enterprise LLM gateway with native vLLM and Ollama integration.
    Strictly fails if no model server is running.
    """

    def __init__(self):
        self.vllm_url = normalize_v1_url(getattr(settings, "VLLM_HOST", "http://127.0.0.1:8001/v1"))
        self.ollama_url = normalize_v1_url(getattr(settings, "OLLAMA_HOST", "http://127.0.0.1:11434"))
        self.base_url = self.vllm_url
        # 1.5s connect timeout for fast offline detection; 120s read timeout for reasoning models
        self.timeout = httpx.Timeout(120.0, connect=1.5)

    async def check_cluster_health(self) -> Dict[str, Any]:
        """
        Probe connected model servers (vLLM datacenter or Ollama workstation/laptop)
        to determine live GPU topology, active weights, and connection status.
        """
        profile = getattr(settings, "active_model_profile", {})
        tier = getattr(settings, "MODEL_TIER", "ENTERPRISE_100B")

        telemetry: Dict[str, Any] = {
            "tier": tier,
            "profile_name": profile.get("tier_name", "Enterprise Refinery Datacenter (100B+)"),
            "target_hardware": profile.get("hardware_spec", "Dual AMD EPYC 9654 + 4x NVIDIA A100 (80GB SXM4)"),
            "tensor_parallel_size": getattr(settings, "TENSOR_PARALLEL_SIZE", 4),
            "max_context_window": getattr(settings, "MAX_MODEL_LEN", 131072),
            "primary_model": profile.get("reasoning", getattr(settings, "MODEL_REASONING", "deepseek-r1:70b-q8_0")),
            "vision_model": profile.get("vision", getattr(settings, "MODEL_VISION", "qwen2-vl:72b-instruct")),
            "coder_model": profile.get("coder", getattr(settings, "MODEL_CODER", "qwen2.5-coder:32b-instruct")),
            "router_model": profile.get("router", getattr(settings, "MODEL_ROUTER", "qwen2.5:72b-instruct")),
            "vllm_endpoint": self.vllm_url,
            "ollama_endpoint": self.ollama_url,
            "is_connected_to_vllm": False,
            "is_connected_to_ollama": False,
            "is_connected": False,
            "active_endpoint": None,
            "mode": "DISCONNECTED",
            "datacenter_node_status": "OFFLINE — No model server reachable (vLLM or Ollama)",
            "available_models": [],
        }

        # 1. Probe vLLM Cluster (Datacenter)
        try:
            async with httpx.AsyncClient(timeout=1.5) as client:
                res = await client.get(f"{self.vllm_url}/models")
                if res.status_code == 200:
                    models_data = res.json().get("data", [])
                    telemetry["is_connected_to_vllm"] = True
                    telemetry["is_connected"] = True
                    telemetry["active_endpoint"] = self.vllm_url
                    telemetry["mode"] = "CONNECTED_DATACENTER_VLLM"
                    telemetry["datacenter_node_status"] = "LIVE_GPU_CLUSTER_ACTIVE"
                    telemetry["available_models"] = [m.get("id") for m in models_data]
                    return telemetry
        except Exception as e:
            logger.debug(f"vLLM cluster offline ({self.vllm_url}): {e}")

        # 2. Probe Ollama Node (Workstation / Laptop)
        try:
            async with httpx.AsyncClient(timeout=1.5) as client:
                res = await client.get(f"{self.ollama_url}/models")
                if res.status_code == 200:
                    models_data = res.json().get("data", [])
                    telemetry["is_connected_to_ollama"] = True
                    telemetry["is_connected"] = True
                    telemetry["active_endpoint"] = self.ollama_url
                    telemetry["mode"] = "CONNECTED_LOCAL_OLLAMA"
                    telemetry["datacenter_node_status"] = "LIVE_OLLAMA_NODE_ACTIVE"
                    telemetry["available_models"] = [m.get("id") for m in models_data]
                    return telemetry
        except Exception as e:
            logger.debug(f"Ollama server offline ({self.ollama_url}): {e}")

        return telemetry

    async def generate_response(
        self,
        prompt: str,
        system_prompt: str = "",
        model_type: str = "reasoning",  # "reasoning", "vision", "coder", "general", "router"
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> Tuple[str, Optional[str]]:
        """
        Generate a response using live connected models (vLLM or Ollama).
        Returns: (content, thought_trace)

        Strict Contract:
        If no model is connected and ALLOW_EMULATION is False, raises ConnectionError.
        The system will NOT run without a live model.
        """
        profile = getattr(settings, "active_model_profile", {})
        if model_type == "vision":
            model_name = profile.get("vision", getattr(settings, "MODEL_VISION", "qwen2-vl:72b-instruct"))
        elif model_type == "coder":
            model_name = profile.get("coder", getattr(settings, "MODEL_CODER", "qwen2.5-coder:32b-instruct"))
        elif model_type == "router":
            model_name = profile.get("router", getattr(settings, "MODEL_ROUTER", "qwen2.5:72b-instruct"))
        else:
            model_name = profile.get("reasoning", getattr(settings, "MODEL_REASONING", "deepseek-r1:70b-q8_0"))

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        # Try live model endpoints in priority order:
        # Datacenter vLLM first, then Workstation/Laptop Ollama
        candidate_endpoints = [
            ("vLLM (Datacenter)", self.vllm_url),
            ("Ollama (Local/Workstation)", self.ollama_url),
        ]

        last_error = None
        for server_label, base_url in candidate_endpoints:
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    res = await client.post(f"{base_url}/chat/completions", json=payload)
                    if res.status_code == 200:
                        data = res.json()
                        choices = data.get("choices", [])
                        if choices:
                            raw_content = choices[0].get("message", {}).get("content", "")
                            thought, content = self._extract_deepseek_r1_thought(raw_content)
                            return content, thought
                    else:
                        logger.warning(
                            f"{server_label} returned HTTP {res.status_code}: {res.text[:200]}"
                        )
            except Exception as e:
                last_error = e
                logger.debug(f"{server_label} dispatch failed at {base_url}: {e}")

        # Check if emulation is explicitly permitted (e.g. for offline mock tests)
        allow_emulation = getattr(settings, "ALLOW_EMULATION", False)
        if allow_emulation:
            logger.info("ALLOW_EMULATION=True: using synthetic execution fallback.")
            return self._emulate_100b_execution(prompt, system_prompt, model_type)

        # STRICT INDUSTRIAL POLICY: No fake outputs. If no model is connected, the system DOES NOT RUN.
        raise ConnectionError(
            f"NO LLM MODEL CONNECTED: System execution halted.\n"
            f"SovereignWorkbench requires an active model server.\n"
            f"Attempted connections:\n"
            f"  - vLLM Datacenter Cluster: {self.vllm_url}\n"
            f"  - Ollama Local/Workstation: {self.ollama_url}\n"
            f"Neither server is reachable (Last error: {last_error}).\n"
            f"Hardware-agnostic emulation is strictly disabled. Please start Ollama or vLLM to run."
        )

    def _extract_deepseek_r1_thought(self, text: str) -> Tuple[Optional[str], str]:
        """Extract DeepSeek-R1 <think>...</think> reasoning traces."""
        match = re.search(r"<think>(.*?)</think>", text, re.DOTALL)
        if match:
            thought = match.group(1).strip()
            content = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
            return thought, content
        return None, text

    def _emulate_100b_execution(
        self,
        prompt: str,
        system_prompt: str,
        model_type: str,
    ) -> Tuple[str, Optional[str]]:
        """
        Emulate pure 100B execution contract with high-fidelity DeepSeek-R1 CoT
        and deterministic structured outputs (Only used when ALLOW_EMULATION=True in tests).
        """
        p_upper = prompt.upper()
        s_upper = system_prompt.upper()

        if model_type == "vision" or "VISION" in s_upper or "P&ID" in p_upper or "ULTRASONIC" in p_upper:
            thought = (
                "DeepSeek-R1 (671B MoE) / Qwen2-VL-72B Visual Analysis:\n"
                "1. Analyzing uploaded refinery asset (P&ID Sheet 4 / Ultrasonic NDT Thickness Log).\n"
                "2. Identifying line tag 'CDU-2-04-150-A1A' in Crude Distillation Unit 2 column overhead.\n"
                "3. Reading ultrasonic grid thickness measurements: nominal t_nom = 4.8 mm, measured t_act = 3.2 mm.\n"
                "4. ASME B31.3 Schedule 40 Carbon Steel design limits: P = 150 psi, T = 135 deg C.\n"
                "5. Determining retirement minimum thickness t_min = 2.1 mm per Section 7.1.1 API 570."
            )
            content = json.dumps({
                "line_tag": "CDU-2-04-150-A1A",
                "material": "ASTM A106 Grade B Carbon Steel",
                "nominal_thickness_mm": 4.8,
                "actual_thickness_mm": 3.2,
                "design_pressure_psi": 150.0,
                "design_temp_celsius": 135.0,
                "unit": "Crude Distillation Unit 2 (CDU-2)",
                "fluid_service": "Hydrocarbon Vapor / Sour Gas",
                "corrosion_mechanism": "Sulfidation & Wet H2S Internal Thinning",
            }, indent=2)
            return content, thought

        elif model_type == "coder" or "CODE" in s_upper or "SANDBOX" in s_upper:
            thought = (
                "Qwen-2.5-Coder-72B Execution:\n"
                "Synthesizing deterministic Python verification script for API 570 remaining life calculation."
            )
            content = (
                "def calculate_api570(t_nom=4.8, t_act=3.2, t_min=2.1, years=10.0):\n"
                "    corrosion_rate = (t_nom - t_act) / years\n"
                "    remaining_life = (t_act - t_min) / corrosion_rate if corrosion_rate > 0 else 99.0\n"
                "    return {'corrosion_rate': corrosion_rate, 'remaining_life_years': remaining_life}\n"
            )
            return content, thought

        elif "ROUTER" in s_upper:
            thought = "DeepSeek-R1 100B Router: Classifying industrial refinery query intent."
            return "VISION_AUDIT", thought

        # General industrial query
        thought = (
            "DeepSeek-R1 (671B MoE) General Engineering Query:\n"
            "Retrieving MRPL Refinery Operations & Engineering Manual standard operating limits."
        )
        content = (
            "Verified against MRPL refinery operating manuals and statutory ASME B31.3 / API 570 guidelines. "
            "All calculations executed deterministically within isolated sandbox environments."
        )
        return content, thought


# Global singleton instance
foundation_engine = FoundationModelEngine()


def get_llm_engine() -> FoundationModelEngine:
    """Returns the singleton FoundationModelEngine gateway instance."""
    return foundation_engine
