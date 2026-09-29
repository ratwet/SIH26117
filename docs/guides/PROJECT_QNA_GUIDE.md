# Aquanex Sovereign AI Workbench - Complete Technology Learning Guide

> **Purpose**: Teach every AI/ML and engineering technology used in this project from first principles, then demonstrate exactly how each one is applied.  
> **Audience**: Students, evaluators, and new team members  
> **Philosophy**: Understand the concept → See the real code → Know why it was chosen  
> **Last Updated**: September 2026

---

## Table of Contents

1. [Large Language Models (LLMs) - The Brain](#1-large-language-models-llms--the-brain)
2. [Transformer Architecture - How LLMs Think](#2-transformer-architecture--how-llms-think)
3. [Model Quantization - Fitting Giants on Laptops](#3-model-quantization--fitting-giants-on-laptops)
4. [Agentic AI & LangGraph - Orchestrating Intelligence](#4-agentic-ai--langgraph--orchestrating-intelligence)
5. [Retrieval-Augmented Generation (RAG) - Grounding AI in Facts](#5-retrieval-augmented-generation-rag--grounding-ai-in-facts)
6. [Vector Databases & Embeddings - The Memory System](#6-vector-databases--embeddings--the-memory-system)
7. [Program-Aided Language (PAL) - Deterministic Math via Code](#7-program-aided-language-pal--deterministic-math-via-code)
8. [Sandbox Isolation & Linux Namespaces - Safe Code Execution](#8-sandbox-isolation--linux-namespaces--safe-code-execution)
9. [Cryptography in Practice - HMAC, SHA-256, Audit Chains](#9-cryptography-in-practice--hmac-sha-256-audit-chains)
10. [Access Control - RBAC vs ABAC](#10-access-control--rbac-vs-abac)
11. [Server-Sent Events (SSE) & Async Architecture](#11-server-sent-events-sse--async-architecture)
12. [FastAPI & Pydantic - The Backend Framework](#12-fastapi--pydantic--the-backend-framework)
13. [Frontend Architecture - Vanilla JS, Vite, CSS Design Systems](#13-frontend-architecture--vanilla-js-vite-css-design-systems)
14. [Multimodal Vision Models - Reading Engineering Drawings](#14-multimodal-vision-models--reading-engineering-drawings)
15. [Speech-to-Text (STT) - Local Voice Processing](#15-speech-to-text-stt--local-voice-processing)
16. [Industrial File Compilers - From Data to Engineering Deliverables](#16-industrial-file-compilers--from-data-to-engineering-deliverables)
17. [Air-Gap Network Security - Kernel-Level Enforcement](#17-air-gap-network-security--kernel-level-enforcement)
18. [End-to-End Data Flow - Putting It All Together](#18-end-to-end-data-flow--putting-it-all-together)
19. [Rapid-Fire Viva Q&A](#19-rapid-fire-viva-qa)

---

## 1. Large Language Models (LLMs) - The Brain

### What is an LLM?

A Large Language Model is a deep neural network trained on trillions of tokens of text to predict the next token in a sequence. Given a prompt like "The capital of France is," the model predicts "Paris" with high probability. But modern LLMs go far beyond simple completion - they can reason, write code, analyze documents, and follow complex instructions.

**Key characteristics:**
- **Parameters**: The "weights" of the neural network. More parameters = more capacity to learn patterns. A 7B model has 7 billion parameters; a 70B model has 70 billion.
- **Context Window**: How many tokens the model can "see" at once. A 128K context window means it can process ~100,000 words simultaneously.
- **Temperature**: Controls randomness. Temperature 0.0 = deterministic (always picks the most likely token). Temperature 1.0 = creative/random.
- **Inference**: The process of running a trained model to generate outputs. Unlike training (which updates weights), inference only reads weights.

### Models Used in Aquanex

| Model | Parameters | Purpose in Aquanex | Why This Model? |
|-------|-----------|-------------------|-----------------|
| **DeepSeek-R1** | 8B / 32B / 70B / 671B | Reasoning & engineering analysis | Best open-source chain-of-thought reasoner; emits `<think>` traces for auditability |
| **Qwen2.5** | 3B / 14B / 72B | Intent routing & general queries | Strong multilingual instruction-following; efficient at classification tasks |
| **Qwen2-VL** | 7B / 72B | Reading P&ID drawings and NDT sheets | State-of-the-art open-source vision-language model |
| **Qwen2.5-Coder** | 7B / 14B / 32B | Generating Python calculation scripts | Purpose-built for code generation with high accuracy |

### How LLMs Are Used in Aquanex

The `FoundationModelEngine` in [`engine.py`](backend/app/llm/engine.py) is the unified gateway. It talks to local model servers via the **OpenAI-compatible REST API** (`/v1/chat/completions`):

```python
# engine.py - Dispatching inference to Ollama or vLLM
payload = {
    "model": "deepseek-r1:70b-q8_0",
    "messages": [
        {"role": "system", "content": "You are an expert piping engineer..."},
        {"role": "user", "content": "Calculate remaining life for line CDU-2-04-150-A1A"}
    ],
    "temperature": 0.2,   # Low temperature for deterministic engineering answers
    "max_tokens": 4096,
}
response = await client.post(f"{base_url}/chat/completions", json=payload)
```

**Why this design?**
- Any model served via Ollama, vLLM, or SGLang can be used without code changes.
- The refinery is never locked into a single AI vendor (**BYOM: Bring Your Own Model**).
- If no model server is running, the system **refuses to fabricate outputs** (raises `ConnectionError`). Generating fictional engineering calculations could cause physical harm.

### DeepSeek-R1's Chain-of-Thought (CoT)

DeepSeek-R1 wraps its reasoning in `<think>...</think>` tags. Aquanex extracts this:

```python
# engine.py - Extracting the reasoning trace
def _extract_deepseek_r1_thought(self, text):
    match = re.search(r"<think>(.*?)</think>", text, re.DOTALL)
    if match:
        thought = match.group(1).strip()    # The reasoning process
        content = re.sub(r"<think>.*?</think>", "", text).strip()  # The final answer
        return thought, content
    return None, text
```

The "thought" is streamed live to the UI as the model reasons, giving engineers transparency into *how* the AI arrived at its conclusion - critical for statutory audit trails.

---

## 2. Transformer Architecture - How LLMs Think

### What is a Transformer?

The Transformer (Vaswani et al., 2017, "Attention Is All You Need") is the neural network architecture behind every modern LLM. Before Transformers, sequential models (RNNs, LSTMs) processed text one word at a time. Transformers process **all words simultaneously** using a mechanism called **self-attention**.

### Self-Attention - The Core Idea

For each word in a sentence, self-attention asks: "How much should I pay attention to every other word?"

Example: *"The pipe **corroded** because the **acid** was too concentrated."*

When processing "corroded," the attention mechanism assigns high weight to "acid" and "concentrated" - understanding that these explain why corrosion happened. This is computed as:

```
Attention(Q, K, V) = softmax(Q × K^T / √d_k) × V
```

Where:
- **Q** (Query): "What am I looking for?"
- **K** (Key): "What do I contain?"
- **V** (Value): "What information do I provide?"
- **d_k**: Dimension of the key vectors (scaling factor to prevent extreme values)

### Multi-Head Attention

Instead of one attention mechanism, Transformers use multiple "heads" running in parallel. Each head learns different types of relationships:
- Head 1 might learn syntactic structure (subject-verb agreement)
- Head 2 might learn semantic relationships (cause-effect)
- Head 3 might learn positional patterns (which noun a pronoun refers to)

### Why This Matters for Aquanex

When a user prompts: *"Audit line CDU-2-04-150-A1A for remaining safe life per API 570. Nominal thickness 4.8mm, measured 3.2mm"*

The Transformer's attention mechanism simultaneously:
1. Identifies "CDU-2-04-150-A1A" as a piping asset tag
2. Connects "4.8mm" to "nominal thickness" and "3.2mm" to "measured"
3. Links "API 570" to the specific regulatory standard governing the calculation
4. Understands "remaining safe life" requires the corrosion rate formula

This parallel comprehension across all tokens is why Transformers outperform sequential models at understanding complex engineering prompts.

---

## 3. Model Quantization - Fitting Giants on Laptops

### What is Quantization?

Full-precision models store each parameter as a 32-bit float (FP32). A 70B parameter model at FP32 requires:

```
70,000,000,000 × 4 bytes = 280 GB of VRAM
```

That's 4× more than the best consumer GPU (RTX 4090 = 24GB). **Quantization** reduces the precision of each parameter:

| Format | Bits per Weight | 70B Model Size | Quality Loss |
|--------|----------------|----------------|-------------|
| FP32 | 32 bits | 280 GB | None (baseline) |
| FP16 | 16 bits | 140 GB | Negligible |
| Q8_0 | 8 bits | 70 GB | Very slight |
| Q4_K_M | 4.5 bits (avg) | ~40 GB | Minor, excellent quality/size tradeoff |
| Q4_0 | 4 bits | ~35 GB | Noticeable on complex reasoning |

### GGUF Format

GGUF (GPT-Generated Unified Format) is the standard file format for quantized models used by `llama.cpp` and Ollama. It stores:
- Quantized weight tensors
- Tokenizer vocabulary
- Model architecture metadata (attention heads, hidden dim, layers)

### How Quantization Is Used in Aquanex

The 3-tier hardware profile in [`config.py`](backend/app/config.py) uses different quantization levels:

```python
# config.py - Hardware tier profiles
"ENTERPRISE_100B": {
    "reasoning": "deepseek-r1:70b-q8_0",      # Q8 - best quality, needs 4x A100
    "coder": "qwen2.5-coder:32b-instruct",    # Full precision on cluster
},
"EDGE_LAPTOP_8B": {
    "reasoning": "deepseek-r1:8b",             # Already small, no quantization needed
    "coder": "qwen2.5-coder:7b-instruct-q4_K_M",  # Q4_K_M to fit in 6GB VRAM
},
```

**VRAM Management - Sequential Model Unloading:**

On a laptop with 8GB VRAM, you can't load a 7B vision model AND an 8B reasoning model simultaneously. Aquanex sends `"keep_alive": 0` to Ollama, which unloads the vision model from GPU after extraction completes, freeing VRAM for the reasoning model:

```
Vision Node (Qwen2-VL-7B loads, ~5GB) → unload → 
Math Node (DeepSeek-R1-8B loads, ~5GB) → unload → done
Peak VRAM: 5.5GB (never both loaded simultaneously)
```

---

## 4. Agentic AI & LangGraph - Orchestrating Intelligence

### What is Agentic AI?

Traditional AI chatbots are **reactive**: you send a message, get a response. An **AI agent** is **proactive**: it can plan multi-step workflows, use tools, observe results, and adapt its behavior based on outcomes.

Key capabilities of an agent:
1. **Planning**: Breaking a complex task into subtasks
2. **Tool Use**: Calling external functions (calculators, databases, file generators)
3. **Observation**: Reading the result of a tool call
4. **Reasoning**: Deciding what to do next based on observations
5. **Memory**: Maintaining state across multiple steps

### What is LangGraph?

LangGraph is a framework for building **stateful, multi-step AI agent workflows** as directed graphs. Each node in the graph is a function that:
- Receives the current state
- Performs some operation (LLM call, tool use, computation)
- Returns an updated state

Unlike simple chains (A → B → C), LangGraph supports **cycles** - a node can loop back to a previous node. This is critical for self-healing error recovery.

### How LangGraph Works (General Concept)

```python
from langgraph.graph import StateGraph

# 1. Define your state (what data flows between nodes)
class MyState(TypedDict):
    question: str
    answer: str
    retry_count: int

# 2. Define node functions
def research_node(state):
    # Do something with state["question"]
    return {"answer": "Some result"}

def validate_node(state):
    if state["answer"] is not None:
        return {"retry_count": 0}  # success
    return {"retry_count": state["retry_count"] + 1}  # failure

# 3. Build the graph
graph = StateGraph(MyState)
graph.add_node("research", research_node)
graph.add_node("validate", validate_node)
graph.add_edge("research", "validate")
# Conditional edge - this creates a CYCLE for retry
graph.add_conditional_edges("validate", lambda s: "research" if s["retry_count"] > 0 else "end")
```

### How LangGraph Is Used in Aquanex

The [`AgentState`](backend/app/graph/state.py) is a TypedDict with 30+ fields tracking the entire lifecycle of one user interaction:

```python
class AgentState(TypedDict):
    # User input
    session_id: str
    user_prompt: str
    user_role: Literal["admin", "senior", "junior"]
    
    # Routing decisions
    task_type: Optional[str]       # "VISION_AUDIT", "SOP_LOOKUP", "GENERAL_QUERY"
    active_model: Optional[str]    # Which model is serving this step
    
    # Extracted engineering data
    pipe_data: Optional[PipeInspectionData]  # Validated piping metrics
    
    # RAG context
    rag_chunks: Optional[List[RagChunk]]     # Retrieved statutory clauses
    
    # Code generation & execution
    generated_code: Optional[str]            # Python script
    sandbox_result: Optional[SandboxResult]  # Execution result
    retry_count: int                         # Self-healing counter (0..3)
    
    # Compiled outputs
    deliverables: Optional[List[Dict]]       # Generated files (DOCX, PDF, DXF, etc.)
    
    # Real-time streaming
    thought_stream: List[str]                # Live progress updates for UI
```

**The 8-Node Graph:**

```
User Prompt
    │
    ▼
[1. route_task_node] ──────── Classify intent (vision/SOP/general)
    │
    ├── VISION_AUDIT ──► [2. vision_extraction_node] ──── Extract piping specs from drawings
    │                         │
    │                         ▼
    │                    [3. rag_retrieval_node] ──── Get API 570/ASME B31.3 clauses
    │                         │
    │                         ▼
    │                    [4. math_generation_node] ── Generate Python calculation script
    │                         │
    │                         ▼
    │                    [5. sandbox_execution_node]── Execute in isolated sandbox
    │                         │
    │                    ┌────┴────┐
    │                    │         │
    │               exit=0    exit≠0
    │                    │         │
    │                    ▼         ▼
    │     [7. compile_deliverables] [6. distill_error_node]
    │                    │              │
    │                    │         retry < 3? ──YES──► back to Node 4 (CYCLE!)
    │                    │              │
    │                    │         retry >= 3? ──► graceful text-only response
    │                    ▼
    │              [8. audit_ledger_node] ──── SHA-256 chain commit
    │
    ├── SOP_LOOKUP ──► [RAG lookup] ──► [general response]
    └── GENERAL ──► [direct LLM response]
```

**Why LangGraph over LangChain chains?**
1. **Self-healing**: If sandbox code crashes, the error loops back. A linear chain would crash entirely.
2. **Typed state**: Every node mutation is explicit in the typed state - auditors can trace exactly what happened at each step.
3. **Deterministic routing**: Transitions are pure functions, not LLM hallucinations.

---

## 5. Retrieval-Augmented Generation (RAG) - Grounding AI in Facts

### What is RAG?

LLMs are trained on general internet text - they don't have access to your private documents, proprietary standards, or recent data. **RAG** solves this by:

1. **Indexing**: Breaking your documents into chunks and converting them to vector embeddings
2. **Retrieving**: When a user asks a question, finding the most relevant chunks
3. **Augmenting**: Injecting those chunks into the LLM's prompt as context
4. **Generating**: The LLM answers based on the retrieved context, not just its training data

```
Without RAG: "What is API 570 Section 7.1?" → LLM might hallucinate or give vague answer
With RAG:    "What is API 570 Section 7.1?" → Retrieves actual clause text → LLM quotes it accurately
```

### The RAG Pipeline (General)

```
Documents ──► Chunk (split into 500-word segments)
          ──► Embed (convert text to 384-dim vectors using an embedding model)
          ──► Store (save vectors + metadata in a vector database)

User Query ──► Embed (same embedding model)
           ──► Search (find nearest vectors using cosine similarity)
           ──► Retrieve (get the original text chunks)
           ──► Inject (add to LLM prompt as context)
           ──► Generate (LLM answers with grounded context)
```

### How RAG Is Used in Aquanex

The [`retriever.py`](backend/app/rag/retriever.py) implements RAG with a critical addition: **Pre-Retrieval ABAC filtering** (explained in Section 10).

```python
# retriever.py - The 5-step retrieval pipeline
def query_sovereign_rag(query, top_k=5, user_role="senior", clearance="CONFIDENTIAL"):
    
    # Step 1: Query ChromaDB with semantic embeddings
    results = collection.query(query_embeddings=embeddings, n_results=top_k * 3)
    
    # Step 2: ABAC filter - remove chunks the user isn't authorized to see
    for chunk in results:
        if not _is_authorized(chunk.classification, chunk.roles, user_role, clearance):
            continue  # DENIED: chunk never enters the pipeline
        candidates.append(chunk)
    
    # Step 3: Add curated baseline knowledge (API 570, ASME B31.3, OISD-118)
    for item in BASELINE_KNOWLEDGE:
        if _is_authorized(...):
            candidates.append(item)
    
    # Step 4: Rank by relevance score
    candidates.sort(key=lambda c: c.relevance_score, reverse=True)
    
    # Step 5: Return top-k chunks with combined context
    return RagQueryResponse(chunks=candidates[:top_k], combined_context=...)
```

**What documents are indexed?**
- API 570 (Piping Inspection Code) - corrosion rate and remaining life formulas
- ASME B31.3 (Process Piping) - minimum wall thickness calculations
- OISD-STD-118 (Oil Industry Safety Directorate) - inspection frequency mandates
- MRPL internal engineering standards and audit documents

---

## 6. Vector Databases & Embeddings - The Memory System

### What is a Vector Embedding?

An embedding is a **fixed-length numerical representation** of text. The key property: **semantically similar texts have similar vectors** (close in high-dimensional space).

```
"pipe corrosion rate" → [0.23, -0.71, 0.42, ..., 0.18]   (384 dimensions)
"metal wall thinning" → [0.21, -0.69, 0.45, ..., 0.16]   (similar vector!)
"weather forecast"    → [-0.81, 0.33, -0.55, ..., 0.92]  (very different vector)
```

**How embeddings are computed:**
A small neural network (the "embedding model") processes the text and outputs a fixed-size vector. Popular models:
- `bge-small-en-v1.5` (33M params, 384-dim vectors) - used in Aquanex
- `text-embedding-3-small` (OpenAI) - cloud-only, can't be used here
- `all-MiniLM-L6-v2` (22M params, 384-dim) - another popular local option

### What is a Vector Database?

A vector database stores embedding vectors and supports **similarity search** - given a query vector, find the K nearest vectors in the database. This is fundamentally different from SQL (`WHERE name = 'X'`) or keyword search (`LIKE '%keyword%'`).

**Similarity metrics:**
- **Cosine Similarity**: Measures the angle between two vectors. Score 1.0 = identical, 0.0 = unrelated.
- **Euclidean Distance**: Measures the straight-line distance. Smaller = more similar.

### How ChromaDB Is Used in Aquanex

**Why ChromaDB?**
- **Embedded** - runs as a Python library, no external server process
- **Persistent** - stores data in a local directory (`data/chromadb/`)
- **CPU-only embeddings** - uses `FastEmbed` with `bge-small-en-v1.5` on CPU, avoiding GPU VRAM contention with LLMs
- **Metadata support** - each chunk stores classification level, department, and authorized roles for ABAC filtering

```python
# config.py - ChromaDB configuration
EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"
CHROMA_PERSIST_DIR: Path = Path("data/chromadb")
RAG_CHUNK_SIZE: int = 500      # 500-word chunks
RAG_CHUNK_OVERLAP: int = 50    # 50-word overlap between chunks
RAG_TOP_K: int = 5             # Return top 5 most relevant chunks
```

**Why not OpenAI embeddings?** They require an API call to `api.openai.com` - violating the zero-egress air-gap invariant. `bge-small-en-v1.5` runs entirely locally with competitive quality.

**Why not FAISS?** FAISS is a vector similarity library, not a database. It doesn't persist data to disk or support metadata filtering. ChromaDB wraps similarity search with persistence and metadata - a better fit for ABAC.

---

## 7. Program-Aided Language (PAL) - Deterministic Math via Code

### What is PAL?

PAL (Gao et al., 2023) is a technique where instead of asking an LLM to directly compute a mathematical answer, you ask it to **write a program** that computes the answer. The program is then executed in a separate runtime.

**Why PAL exists:**
LLMs perform arithmetic in their attention layers - essentially doing "vibes-based math." They frequently make errors:
```
LLM without PAL: "23.7 × 4.2 = 99.54"  (correct: 99.54 ✓ - but only by luck)
LLM without PAL: "156.3 × 0.87 = 135.981"  (correct: 135.981 ✓ - lucky again)
LLM without PAL: "4.8 - 3.2 / 4.57 = 0.35"  (correct: 0.350... ✓ - but what about edge cases?)
```

The problem: you can't tell when the LLM got lucky vs. when it's wrong. In a refinery, a 0.4mm error in corrosion calculation means the difference between safe operation and **catastrophic pipe rupture**.

### How PAL Works

```
Step 1: User asks "Calculate remaining life for CDU-2-04-150-A1A"

Step 2: LLM generates Python code:
    t_nom = 4.8    # nominal thickness (mm)
    t_act = 3.2    # actual measured thickness (mm)  
    t_min = 2.1    # minimum per ASME B31.3 (mm)
    years = 4.57   # time in service
    
    corrosion_rate = (t_nom - t_act) / years    # 0.35 mm/year
    remaining_life = (t_act - t_min) / corrosion_rate  # 3.14 years
    
    print(json.dumps({"remaining_life_years": remaining_life}))

Step 3: Code executes in sandbox → stdout = {"remaining_life_years": 3.14}

Step 4: The number 3.14 is the DEFINITIVE answer - computed by Python, not by LLM weights
```

### How PAL Is Used in Aquanex

Node 4 (`math_generation_node`) in [`nodes.py`](backend/app/graph/nodes.py) asks the coder model (Qwen2.5-Coder) to generate a self-contained Python script. Node 5 (`sandbox_execution_node`) executes it in an isolated Bubblewrap container. The result is parsed from stdout.

**The engineering formulas computed by PAL:**

```
Corrosion Rate (CR) = (t_nominal - t_actual) / years_in_service   [mm/year]

t_minimum = (P × D) / (2 × (S × E + P × Y))   [per ASME B31.3 Clause 304.1.2]

Remaining Life (RL) = (t_actual - t_minimum) / CR   [years]

Statutory Action:
    if RL < 5.0 years → "MANDATORY SHUTDOWN REPLACEMENT"
    if RL ≥ 5.0 years → "NORMAL IN-SERVICE MONITORING"
```

**Self-Healing Loop:** If the generated code crashes (e.g., division by zero), the error is parsed by `distill_error_node`, and the graph cycles back to `math_generation_node` with the error as additional context. Up to 3 retries. After 3 failures, the system gracefully degrades to a text-only response rather than producing unverified calculations.

---

## 8. Sandbox Isolation & Linux Namespaces - Safe Code Execution

### What is Sandboxing?

When an AI generates code, you cannot trust it. It might:
- Read sensitive files (`/etc/passwd`, SSH keys)
- Open network connections (data exfiltration)
- Fork bomb (`:(){ :|:& };:`) - crashing the system
- Consume unlimited RAM (out-of-memory kill)

**Sandboxing** runs untrusted code in an isolated environment where it cannot affect the host system.

### Linux Namespaces - The Kernel Mechanism

Linux namespaces are kernel features that isolate what a process can see and access:

| Namespace | Flag | What It Isolates |
|-----------|------|-----------------|
| **PID** | `CLONE_NEWPID` | Process IDs - sandbox sees only its own processes |
| **NET** | `CLONE_NEWNET` | Network - sandbox has NO network interfaces at all |
| **MNT** | `CLONE_NEWNS` | Filesystem - sandbox sees only whitelisted directories |
| **IPC** | `CLONE_NEWIPC` | Inter-process communication - no shared memory with host |
| **USER** | `CLONE_NEWUSER` | UID/GID mapping - sandbox user has no host privileges |

These are the same primitives that Docker uses, but Bubblewrap (`bwrap`) applies them directly without needing a daemon or root.

### What is Bubblewrap (bwrap)?

Bubblewrap is a lightweight, unprivileged sandboxing tool. It creates an isolated environment using Linux namespaces with a single command:

```bash
/usr/bin/bwrap \
  --unshare-all \              # Isolate ALL namespaces
  --unshare-net \              # NO network (not even loopback)
  --die-with-parent \          # Kill sandbox if parent dies
  --ro-bind /usr /usr \        # Read-only access to system libraries
  --ro-bind /lib /lib \        # Read-only access to shared libraries
  --ro-bind /bin /bin \        # Read-only access to binaries
  --proc /proc \               # Provide /proc for Python stdlib
  --dev /dev \                 # Provide /dev for basic I/O
  --tmpfs /tmp \               # Ephemeral ramdisk (destroyed on exit)
  python3 script.py            # Execute the untrusted code
```

### How Sandboxing Is Used in Aquanex

When Node 4 generates a Python script, Node 5 (`sandbox_execution_node`) dispatches it to `execute_in_sandbox()`:

```python
# nodes.py - Sandbox execution node
async def sandbox_execution_node(state):
    code = state.get("generated_code", "")
    
    # Run in thread to avoid blocking async event loop
    result = await asyncio.to_thread(
        execute_in_sandbox,
        code=code,
        timeout=5,              # 5-second wall-clock timeout
        mem_limit_mb=256,       # 256MB maximum RAM
    )
    
    return {"sandbox_result": result}
```

**Security guarantees:**
1. **No network**: Even if the LLM generates `requests.get("http://evil.com")`, it fails with `EPERM`
2. **No file access**: Host `/home`, `/etc`, SSH keys are unmapped - invisible to the script
3. **No resource abuse**: 256MB RAM cap, 5-second timeout, SIGKILL on violation
4. **No orphans**: `--die-with-parent` prevents zombie processes
5. **Fail-closed**: If `/usr/bin/bwrap` is missing, `ALLOW_UNSANDBOXED_FALLBACK = False` prevents unsandboxed execution entirely

**Why not Docker?**
- Docker requires root daemon (`dockerd`) - attack surface
- Docker images need registries - impossible in air-gap without pre-staging
- Docker adds ~200MB overhead per image; bwrap adds zero
- Bwrap is a single binary, already installed on most Linux systems

---

## 9. Cryptography in Practice - HMAC, SHA-256, Audit Chains

### What is SHA-256?

SHA-256 (Secure Hash Algorithm, 256-bit) is a one-way function that takes any input and produces a fixed 256-bit (32-byte) hash:

```python
import hashlib
hashlib.sha256(b"Hello World").hexdigest()
# → "a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e"
```

**Properties:**
- **Deterministic**: Same input always produces same hash
- **One-way**: Cannot reverse-engineer input from hash
- **Collision-resistant**: Practically impossible to find two different inputs with the same hash
- **Avalanche effect**: Changing one bit of input completely changes the hash

### What is HMAC?

HMAC (Hash-based Message Authentication Code) adds a **secret key** to the hashing process:

```python
import hmac, hashlib
hmac.new(b"secret_key", b"message", hashlib.sha256).hexdigest()
# → Only someone with "secret_key" can produce this exact hash
```

HMAC proves two things:
1. **Authenticity**: The message was created by someone who knows the secret key
2. **Integrity**: The message hasn't been modified since the HMAC was computed

### How Cryptography Is Used in Aquanex

**1. HMAC-SHA256 Action Approval Tokens** ([`approval_tokens.py`](backend/app/policy/approval_tokens.py)):

When the AI prepares a consequential action (like sending an email), it generates an approval token:

```python
# Token generation (simplified)
claims = {
    "action_type": "EMAIL_DISPATCH",
    "target": "turnaround-team@mrpl.co.in",
    "payload_hash": sha256(email_body + attachments),  # Hash of the EXACT content
    "user_id": "rajat_admin",
    "expires_at": "2026-09-18T18:00:00Z"
}
payload_b64 = base64url_encode(json.dumps(claims))
signature = hmac_sha256(secret_key, payload_b64)
token = f"{payload_b64}.{signature}"
```

**Verification ensures:**
- The signature matches → token wasn't forged
- The token hasn't expired → human intent is recent
- The payload_hash matches → email content wasn't modified after approval

If someone changes the email recipient after approval, the payload_hash changes, and verification fails. The approval is **cryptographically bound** to the exact content reviewed.

**2. SHA-256 Audit Hash Chain** (`mrpl_audit.db`):

```
Block 0 (Genesis):  prev_hash = "000...000"
                    data = "System initialized"
                    hash = SHA-256(prev_hash + data + timestamp)
                         = "abc123..."

Block 1:            prev_hash = "abc123..."  ← links to Block 0
                    data = "Model inference: DeepSeek-R1 70B"
                    hash = SHA-256("abc123..." + data + timestamp)
                         = "def456..."

Block 2:            prev_hash = "def456..."  ← links to Block 1
                    data = "Deliverable compiled: MRPL_Report.docx"
                    hash = SHA-256("def456..." + data + timestamp)
                         = "ghi789..."
```

If anyone tampers with Block 1 (e.g., changes the model name), its hash changes from "def456..." to something else, but Block 2 still expects "def456..." as `prev_hash`. The chain **breaks** - tamper detected.

---

## 10. Access Control - RBAC vs ABAC

### What is RBAC (Role-Based Access Control)?

RBAC assigns permissions based on a user's **role**:

```
Admin  → Can access ALL models, ALL endpoints, issue approval tokens
Senior → Can access ENTERPRISE/WORKSTATION/EDGE models, issue tokens
Junior → Can access EDGE model only, CANNOT issue tokens
```

### What is ABAC (Attribute-Based Access Control)?

ABAC is more granular - it evaluates **attributes** of the data, the user, and the environment:

```
Access Decision = f(user.role, user.clearance, document.classification, document.department)
```

Example:
- Document: `MRPL-BOARD-AUDIT.pdf`, classification=RESTRICTED, authorized_roles=[admin, senior]
- User: Naveen (junior, clearance=INTERNAL)
- Decision: **DENIED** (INTERNAL < RESTRICTED, and "junior" not in [admin, senior])

### How ABAC Is Used in Aquanex RAG

The [`_is_authorized()`](backend/app/rag/retriever.py#L94-L109) function implements pre-retrieval ABAC:

```python
CLEARANCE_RANK = {
    "UNCLASSIFIED": 1,
    "INTERNAL": 2,
    "CONFIDENTIAL": 3,
    "RESTRICTED": 4,
}

def _is_authorized(chunk_classification, chunk_roles, user_role, clearance):
    user_rank = CLEARANCE_RANK.get(clearance, 2)
    doc_rank = CLEARANCE_RANK.get(chunk_classification, 2)
    
    # Classification check: user must have equal or higher clearance
    if doc_rank > user_rank:
        return False
    
    # Role check: user's role must be in the authorized list
    if user_role not in chunk_roles and user_role != "admin":
        return False
    
    return True
```

**Why "pre-retrieval" matters:**
- **Post-retrieval filtering**: Retrieve all chunks, then remove unauthorized ones. Problem: unauthorized data was already loaded into memory and could leak through prompt injection or logging.
- **Pre-retrieval filtering**: Unauthorized chunks are **never returned from the database**. They never enter the model's context window, making prompt injection attacks ineffective.

**Concrete example:**
```python
# Junior technician queries for restricted board audit data
result = query_sovereign_rag(
    query="turnaround capital procurement budget",
    user_role="junior",
    clearance="INTERNAL"    # Junior's max clearance
)
# The RESTRICTED board audit document (CLEARANCE_RANK=4) is NEVER returned
# because INTERNAL (rank 2) < RESTRICTED (rank 4)
```

---

## 11. Server-Sent Events (SSE) & Async Architecture

### What are Server-Sent Events?

SSE is a protocol where the server pushes real-time updates to the client over a long-lived HTTP connection. Unlike WebSockets (bidirectional), SSE is **unidirectional** (server → client only).

```
Client: GET /api/telemetry/stream
Server: 200 OK, Content-Type: text/event-stream

data: {"node": "router", "status": "Classifying your request..."}

data: {"node": "vision", "status": "Analyzing P&ID drawing..."}

data: {"node": "rag", "status": "Retrieving API 570 clauses..."}

data: {"node": "sandbox", "status": "Running verified calculation..."}

data: {"node": "compile", "status": "Generating DOCX report..."}

data: {"complete": true, "deliverables": [...]}
```

### What is Async/Await?

Python's `async/await` allows concurrent I/O operations without blocking. When one request waits for a model response (120s), other requests can still be served:

```python
# WITHOUT async - blocks everything during model call
def handle_request():
    result = model.generate(prompt)  # Thread blocked for 120 seconds!
    return result

# WITH async - serves other requests while waiting
async def handle_request():
    result = await model.generate(prompt)  # Yields control while waiting
    return result
```

### How SSE & Async Are Used in Aquanex

**The "Thought Stream"**: As LangGraph progresses through nodes, each node appends progress messages to `state["thought_stream"]`. These are streamed to the frontend via SSE, showing the user exactly what the AI is doing in real-time:

```python
# nodes.py - Each node appends to the thought stream
async def rag_retrieval_node(state):
    thought = "Checking refinery safety standards and statutory guidelines..."
    current_thoughts = state.get("thought_stream", [])
    # ... perform retrieval ...
    return {"thought_stream": current_thoughts + [thought]}
```

**Async threading for sandbox**: The Bubblewrap sandbox is a blocking `subprocess` call. Using `asyncio.to_thread()` dispatches it to an OS thread, keeping the FastAPI event loop responsive:

```python
result = await asyncio.to_thread(execute_in_sandbox, code)
# Other HTTP requests continue being served while sandbox runs
```

---

## 12. FastAPI & Pydantic - The Backend Framework

### What is FastAPI?

FastAPI is a modern Python web framework built on **ASGI** (Asynchronous Server Gateway Interface). Key features:
- Native `async/await` support
- Automatic request/response validation via Pydantic
- Auto-generated OpenAPI documentation
- First-class SSE streaming support

### What is Pydantic?

Pydantic is a data validation library using Python type hints. You define a schema as a class, and Pydantic automatically validates data against it:

```python
from pydantic import BaseModel, Field

class PipeInspectionData(BaseModel):
    line_tag: str                          # Must be a string
    nominal_thickness_mm: float            # Must be a float
    actual_thickness_mm: float             # Must be a float
    remaining_life_years: float            # Must be a float
    mandatory_action: str                  # Must be a string

# This works:
data = PipeInspectionData(line_tag="CDU-2-04-150-A1A", nominal_thickness_mm=4.8, ...)

# This raises ValidationError:
data = PipeInspectionData(line_tag=123, nominal_thickness_mm="not a number", ...)
```

### How They're Used in Aquanex

[`schemas.py`](backend/app/schemas.py) is the **frozen contract** between all three developers. Every data structure flowing through the system is a validated Pydantic model:

```python
# schemas.py - The contract between developers
class SandboxResult(BaseModel):
    success: bool                   # Did the code execute successfully?
    exit_code: int                  # Process exit code (0 = success)
    stdout: str                     # Captured output
    stderr: str                     # Captured errors
    distilled_error: Optional[str]  # Clean error summary for self-healing
    parsed_output: Optional[Dict]   # Structured JSON from stdout

class ActionApprovalRequest(BaseModel):
    user_id: str
    user_role: str
    action_type: str      # "EMAIL_DISPATCH", "FILE_COMMIT"
    target: str           # Recipient or file path
    payload_hash: str     # SHA-256 of the action payload
```

**Configuration with Pydantic Settings:** [`config.py`](backend/app/config.py) uses `pydantic-settings` to load environment variables with type-safe defaults:

```python
class Settings(BaseSettings):
    SANDBOX_TIMEOUT_SECONDS: int = 5
    SANDBOX_MEMORY_LIMIT_MB: int = 256
    SANDBOX_MAX_RETRIES: int = 3
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"
    APPROVAL_TOKEN_TTL_SECONDS: int = 300
    ALLOW_UNSANDBOXED_FALLBACK: bool = False  # Fail-closed by default
```

---

## 13. Frontend Architecture - Vanilla JS, Vite, CSS Design Systems

### Why Vanilla JavaScript?

Aquanex uses zero frontend frameworks (no React, no Vue, no Angular). Reasons:
1. **Zero CDN dependency**: Frameworks typically require internet-hosted packages or CDNs. In an air-gap, every byte must be local.
2. **No supply chain risk**: No `node_modules` with thousands of transitive dependencies that could contain malware.
3. **Instant rendering**: On ruggedized field laptops with limited CPU, vanilla JS renders immediately without virtual DOM overhead.
4. **Full control**: CSS Grid + Flexbox + CSS Custom Properties give complete design system control.

### What is Vite?

Vite is a frontend build tool that serves ES modules natively during development (no bundling step) and uses `esbuild` for production builds. Result: **sub-300ms builds**.

### The RBAC View System

The frontend dynamically shows/hides UI components based on the persona query parameter:

```javascript
// main.js - Role-based UI switching
const params = new URLSearchParams(window.location.search);
const persona = params.get('persona') || 'senior';

if (persona === 'admin') {
    // Show: Cluster dashboard, audit stream, RBAC matrix
    // Hide: Chat input, model dropdown, deliverable preview
} else if (persona === 'senior') {
    // Show: Full engineering workbench with all controls
} else if (persona === 'junior') {
    // Show: Simplified field terminal
    // Hide: Model dropdown (locked to Edge-8B)
}
```

---

## 14. Multimodal Vision Models - Reading Engineering Drawings

### What is a Vision-Language Model (VLM)?

A VLM is a model that can process both images and text simultaneously. It combines a **vision encoder** (processes pixel data into features) with a **language model** (processes text and generates responses).

### How Vision Is Used in Aquanex

Node 2 (`vision_extraction_node`) uses **Qwen2-VL** to extract engineering parameters from uploaded P&ID drawings and NDT inspection reports:

```python
# nodes.py - Vision extraction
llm_prompt = "Extract piping inspection parameters from the attached technical drawings"
content, trace = await call_llm(
    prompt=llm_prompt,
    system_prompt=(
        "You are an expert industrial engineering vision assistant. "
        "Extract parameters as JSON: line_tag, material_spec, "
        "nominal_thickness_mm, actual_thickness_mm, design_pressure_psi"
    ),
    model_type="vision"  # Routes to Qwen2-VL
)
```

**Defensive parsing**: The extracted JSON is validated and supplemented with regex-based extraction from the user's prompt text:

```python
# Extract line tag from prompt: "CDU-2-04-150-A1A"
tag_match = re.search(r'\b([A-Z]{2,4}-\d{1,2}-\d{2,3}-[A-Z0-9\-]+)\b', prompt_text)

# Extract thickness: "nominal thickness 4.8mm"
nom_match = re.search(r'(?:nominal|t_nom)\s*[:=]\s*(\d+\.?\d*)', prompt_text)
```

This dual approach (VLM extraction + regex fallback) ensures robust parameter extraction even when the model's JSON output is malformed.

---

## 15. Speech-to-Text (STT) - Local Voice Processing

### What is Whisper?

Whisper is OpenAI's open-source speech recognition model. It converts audio waveforms into text with high accuracy across multiple languages.

### Faster-Whisper

Faster-Whisper is a CTranslate2-optimized implementation of Whisper that runs 4× faster on CPU and 2× faster on GPU compared to the original. It's used in Aquanex because it runs entirely locally - no cloud API calls.

### The Zero-Surveillance Protocol

```python
# voice.py - Privacy-first voice processing
async def transcribe_voice(audio_stream):
    # 1. Push-to-Talk only - no always-on listening
    raw_bytes = io.BytesIO()           # In-memory buffer, NOT a file
    raw_bytes.write(audio_stream)
    
    # 2. Transcribe locally
    text = whisper_model.transcribe(raw_bytes)
    
    # 3. IMMEDIATELY destroy the audio
    del raw_bytes                       # Remove reference
    # Python's garbage collector reclaims the memory
    # Zero audio files ever written to disk
    
    return text
```

**Why this matters**: In a refinery, voice conversations might contain sensitive operational data. The zero-surveillance invariant ensures no audio recordings exist after transcription - eliminating any surveillance risk.

---

## 16. Industrial File Compilers - From Data to Engineering Deliverables

### What Makes Aquanex Different from ChatGPT?

ChatGPT outputs text. Aquanex outputs **physical engineering files** that can be directly used in industrial workflows:

| Format | Python Library | What It Creates |
|--------|---------------|----------------|
| `.docx` | `python-docx` | Executive approval notes with MRPL letterhead, calculation steps, signature blocks |
| `.xlsx` | `openpyxl` | Cost & risk matrices with conditional formatting, contingency formulas |
| `.dxf` | `ezdxf` | AutoCAD-compatible piping spool drawings with ANSI layer standards |
| `.stl` | `numpy-stl` | 3D binary mesh files for replacement spool visualization and 3D printing |
| `.pdf` | `ReportLab` | Statutory inspection certificates with sign-off blocks and QR codes |
| `.png` | `matplotlib` | Ultrasonic thickness corrosion heatmaps |
| `.csv` | `csv` (stdlib) | NDT thickness survey data for spreadsheet analysis |

**Every file gets:**
1. A **statutory watermark**: "AI-GENERATED DRAFT - STATUTORY HUMAN REVIEW REQUIRED"
2. A **SHA-256 checksum** recorded in the audit manifest
3. Storage in `data/staging/` for download

### Why `ezdxf` for CAD?

`ezdxf` is a pure-Python library that generates AutoCAD-compatible DXF files programmatically. In an air-gapped environment where AutoCAD may not be installed, this allows headless generation of engineering drawings that can be opened in any DXF viewer (AutoCAD, BricsCAD, FreeCAD, LibreCAD).

---

## 17. Air-Gap Network Security - Kernel-Level Enforcement

### What is an Air Gap?

An air gap is a **physical separation** between a secure network and any external network. There is literally no cable, no WiFi, no cellular connection between the refinery's operational network and the internet.

### How Aquanex Enforces the Air Gap in Software

The Network Isolation Watchdog reads the Linux kernel's routing table directly:

```python
# Pseudocode - Air-gap watchdog
def check_airgap():
    with open("/proc/net/route") as f:
        for line in f:
            destination = line.split()[1]
            if destination == "00000000":   # 0.0.0.0 = default gateway
                # DEFAULT GATEWAY EXISTS → WAN route detected!
                trigger_lockdown()
                return False
    return True  # No default gateway → air-gap intact
```

**Why `/proc/net/route`?**
- It's a **kernel interface** - reflects the actual routing table, not firewall rules (which can be misconfigured)
- Requires **no root privileges** - unlike configuring iptables
- **Reactive detection** - doesn't try to prevent connections (which can be circumvented) but detects them and **halts all processing**

**Lockdown sequence:**
1. All API endpoints return HTTP 403
2. SSE alert streamed to all connected frontends
3. Red Emergency Lockdown Modal covers the UI
4. Security event logged to SHA-256 audit chain
5. If the offending route disappears (cable unplugged), operations auto-resume within ~1.5s

---

## 18. End-to-End Data Flow - Putting It All Together

Here's the complete journey from user prompt to engineering deliverable:

```
STEP 1: USER INPUT
├── Engineer types: "Audit line CDU-2-04-150-A1A per API 570"
├── Uploads: P&ID drawing (PNG) + NDT thickness log (CSV)
└── Persona: senior (via ?persona=senior)

STEP 2: FASTAPI GATEWAY (Port 8000)
├── Auth check: senior role validated
├── Air-gap check: /proc/net/route → no WAN routes → PASS
└── Request forwarded to LangGraph engine

STEP 3: LANGGRAPH NODE 1 - ROUTER
├── Keyword analysis: "audit", "CDU", "API 570" → VISION_AUDIT
├── File analysis: .png upload detected → vision model needed
├── Model selection: Qwen2-VL-72B (enterprise tier)
└── State update: task_type = "VISION_AUDIT"

STEP 4: LANGGRAPH NODE 2 - VISION EXTRACTION
├── Qwen2-VL processes P&ID drawing → extracts line_tag, thicknesses
├── Regex parsing extracts user-specified parameters from prompt
├── Pydantic validation → PipeInspectionData entity
└── SSE thought: "Extracted line tag CDU-2-04-150-A1A (4.8mm nominal)"

STEP 5: LANGGRAPH NODE 3 - RAG RETRIEVAL
├── ChromaDB query: "API 570 corrosion remaining life"
├── ABAC filter: senior/CONFIDENTIAL → retrieves API 570, ASME B31.3, OISD-118
│   (RESTRICTED board audit excluded? No - senior has CONFIDENTIAL clearance)
├── Top-5 chunks ranked by relevance
└── Context injected into state

STEP 6: LANGGRAPH NODE 4 - MATH GENERATION (PAL)
├── Qwen2.5-Coder generates standalone Python script
├── Script implements: CR = (t_nom - t_act) / years
│                      t_min = (P×D) / (2×(S×E + P×Y))
│                      RL = (t_act - t_min) / CR
└── Script prints JSON result to stdout

STEP 7: LANGGRAPH NODE 5 - SANDBOX EXECUTION
├── Code → Bubblewrap container (no network, 256MB RAM, 5s timeout)
├── Python executes → stdout: {"remaining_life_years": 3.14, ...}
├── Exit code 0 → SUCCESS
└── If exit ≠ 0 → Node 6 (distill error) → retry loop back to Node 4

STEP 8: LANGGRAPH NODE 7 - COMPILE DELIVERABLES
├── DOCX: Executive approval note with MRPL letterhead + watermark
├── XLSX: Cost matrix with pipe procurement + labor + contingency
├── DXF: AutoCAD piping spool replacement drawing
├── STL: 3D mesh for replacement spool visualization
├── PDF: Statutory inspection certificate with sign-off blocks
├── PNG: Corrosion heatmap visualization
├── CSV: NDT thickness survey export
├── SHA-256 checksums computed for all files
└── All files saved to data/staging/

STEP 9: LANGGRAPH NODE 8 - AUDIT LEDGER
├── Block #N appended to mrpl_audit.db
├── prev_hash = SHA-256 of Block #(N-1)
├── payload = prompt hash + output hash + model ID + timestamp + operator
├── current_hash = SHA-256(prev_hash + payload)
└── Chain integrity maintained

STEP 10: SSE RESPONSE → FRONTEND
├── Final markdown report streamed to UI
├── Deliverable download chips appear (DOCX, PDF, DXF, STL, etc.)
├── Thought stream shows complete reasoning trace
└── Engineer reviews, downloads files, optionally approves actions
```

---

## 19. Rapid-Fire Viva Q&A

**Q: "What is a Transformer?"**
A: A neural network architecture that processes all input tokens simultaneously using self-attention, rather than sequentially like RNNs. Enables parallel training and captures long-range dependencies.

**Q: "What is attention in AI?"**
A: A mechanism where each token computes relevance scores against all other tokens: `Attention(Q,K,V) = softmax(QK^T/√d)×V`. This lets the model focus on the most relevant parts of the input.

**Q: "What is RAG?"**
A: Retrieval-Augmented Generation - retrieve relevant documents from a vector database, inject them into the LLM's prompt as context, then generate a grounded answer. Reduces hallucination.

**Q: "What is an embedding?"**
A: A dense numerical vector representing text in high-dimensional space. Similar texts have similar vectors (close in cosine similarity). Used for semantic search in vector databases.

**Q: "What is LangGraph?"**
A: A framework for building stateful, multi-step AI agent workflows as directed graphs with support for cycles. Unlike LangChain chains (linear), LangGraph enables retry loops and conditional branching.

**Q: "What is PAL?"**
A: Program-Aided Language - the LLM writes code to solve math problems instead of computing answers in its attention layers. Ensures deterministic, verifiable results.

**Q: "What is HMAC-SHA256?"**
A: A keyed hash function that proves both message authenticity (created by secret key holder) and integrity (message wasn't modified). Used for approval tokens.

**Q: "What is Bubblewrap (bwrap)?"**
A: An unprivileged Linux sandboxing tool using kernel namespaces. Isolates network, filesystem, PID, IPC without root or Docker daemon.

**Q: "What is quantization?"**
A: Reducing model weight precision (32-bit → 4-bit) to fit large models on smaller hardware. Q4_K_M fits a 70B model in ~40GB instead of 280GB.

**Q: "What is ABAC?"**
A: Attribute-Based Access Control - access decisions based on attributes of the data (classification level, department) and the user (role, clearance). More granular than role-based RBAC.

**Q: "What is an air gap?"**
A: Physical network isolation - no cable, WiFi, or cellular connects the secure network to the internet. Aquanex enforces this in software by monitoring `/proc/net/route` for default gateways.

**Q: "Why not use Docker?"**
A: Docker needs root daemon (attack surface), registry pulls (impossible in air-gap), and ~200MB per image. Bwrap is a single binary with zero overhead.

**Q: "How does the self-healing loop work?"**
A: Sandbox error → `distill_error_node` extracts root cause → loops back to `math_generation_node` with error context → LLM generates corrected code → retry (max 3 times) → graceful degradation if all fail.

**Q: "Why not use OpenAI embeddings?"**
A: They require API calls to `api.openai.com`, violating the zero-egress air-gap. We use `bge-small-en-v1.5` locally on CPU.

**Q: "What is SSE?"**
A: Server-Sent Events - unidirectional server-to-client streaming over HTTP. Used to push real-time "thought stream" updates as LangGraph progresses through nodes.

**Q: "Why Pydantic?"**
A: Type-safe data validation. `PipeInspectionData`, `SandboxResult`, and `ActionApprovalRequest` are Pydantic models - invalid data raises `ValidationError` before reaching business logic.

**Q: "What is the statutory watermark?"**
A: "AI-GENERATED DRAFT - STATUTORY HUMAN REVIEW REQUIRED" - embedded in all DOCX/PDF files. Prevents AI outputs from being mistaken for certified engineering documents.

**Q: "Can it run without GPU?"**
A: Yes. 8B models run on CPU (AVX-512) via Ollama/llama.cpp at ~10-20 tokens/sec. Slower but functional for field inspections.

**Q: "How do you prevent prompt injection in RAG?"**
A: Pre-retrieval ABAC. Unauthorized chunks are filtered at the database level - they never enter the model's context. Even if a RESTRICTED document contains a prompt injection payload, a Junior user's query never retrieves it.

**Q: "Why is the audit chain not a real blockchain?"**
A: A blockchain requires network consensus between peers. In an air-gapped single-workstation deployment, there are no peers. SHA-256 hash chains in SQLite provide equivalent tamper-evidence for a single-authority system.

---

> **End of Learning Guide**  
> *Aquanex Sovereign AI Workbench - Understand the Tech, Apply the Tech, Ship the Tech.*
