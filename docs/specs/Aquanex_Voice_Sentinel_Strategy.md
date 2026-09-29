# Aquanex Voice Sentinel: Sovereign Voice Assistant and Employee Support Strategy

## Purpose

This document describes how Aquanex (Aquanex) can add local audio input/output, voice-assistant interaction, reminders, alerts, and employee-support workflows while preserving air-gap, privacy, safety, and human-control principles.

The intended experience is a capable “Jarvis-like” workplace assistant. The intended operating model is not surveillance or autonomous management of employees; it is a consent-aware, policy-governed operational assistant for authorized users.

> Scope note: This is an engineering and product roadmap, not legal advice. Deployment must be reviewed by organizational IT, cybersecurity, HR, safety, legal, records-management, and data-governance teams.

## Product Vision

**Aquanex Voice Sentinel** provides privacy-preserving, local voice interaction for industrial teams. Wake-word detection, speech recognition, reasoning, document retrieval, tool use, and speech output run within the organization’s on-premise environment.

It can help engineers and employees with authorized work: inspection summaries, SOP questions, calculation explanations, task reminders, shift handovers, approvals, training/certification deadlines, and operational checklists. It keeps humans in control of consequential decisions.

## Core Architecture

```text
Microphone / Push-to-Talk Button
              |
              v
Local Wake Word + Voice Activity Detection
              |
              v
Local Speech-to-Text Service
              |
              v
Aquanex Policy Engine + Agent + RAG + Tool Router
              |
              +--> Local Model Gateway
              +--> OCR / Vision Pipeline
              +--> Deterministic Calculation Service
              +--> Permission-Aware RAG
              +--> Alert / Reminder Scheduler
              +--> Approved Local Connectors
              |
              v
Local Text-to-Speech Service
              |
              v
Speaker / Headset / Desktop Notification
```

No raw audio, transcript, prompt, retrieval context, or generated response should leave the approved local network boundary.

## Recommended Local Technology Stack

| Layer | Recommended options | Purpose |
|---|---|---|
| Wake-word detection | openWakeWord, LiveKit WakeWord, custom ONNX wake-word model | Detect activation phrase such as “Hey Aquanex” locally |
| Voice activity detection | Silero VAD, WebRTC VAD | Detect speech start/end and reduce unnecessary recording |
| Speech-to-text | faster-whisper, whisper.cpp | Transcribe speech locally |
| Noise control | WebRTC audio processing, local noise suppression | Improve usability in noisy office/industrial environments |
| Reasoning and agent | Existing Ollama/vLLM + LangGraph stack | Reasoning, RAG, routing, tool use |
| Text-to-speech | Piper, Kokoro, Coqui/XTTS where approved | Produce spoken response locally |
| Audio transport | Local WebSocket/WebRTC/native desktop audio | Stream audio between frontend and backend |
| Scheduler | SQLite/PostgreSQL + APScheduler/Celery | Manage reminders, deadlines, and notifications |
| Audit | Tamper-evident event ledger | Record voice actions, approvals, and alert decisions |

## Voice Interaction Modes

Voice must be opt-in and visibly active. Do not operate an always-recording system by default.

| Mode | Behavior | Recommended use |
|---|---|---|
| Push-to-talk | User holds a key/button while speaking | Default for confidential engineering work |
| Wake-word | “Hey Aquanex” activates a short recording window | Personal desktop/headset usage |
| Meeting mode | User explicitly starts and stops recording/transcription | Authorized meetings and briefings |
| Alert-only | No microphone recording; system issues visual/spoken notifications | Shift reminders and deadline alerts |
| Secure mode | Voice input/output disabled or restricted | Classified/sensitive areas and discussions |

## Example Commands

### Engineering support

- “Aquanex, summarize today’s inspection findings.”
- “Explain the remaining safe-life calculation and its assumptions.”
- “What does the relevant SOP say about this inspection interval?”
- “Create a draft approval note from this report.”
- “Compare this UT thickness reading with the prior survey.”
- “Read the critical exceptions only.”
- “Show the source clauses behind this recommendation.”

### Productivity support

- “Remind me at 4 PM to review the Unit-3 approval note.”
- “What approvals are waiting for my review?”
- “Prepare my shift handover summary.”
- “List inspections due this week for my assigned unit.”
- “Draft a message to the inspection manager; do not send it.”
- “Read my next authorized task reminder.”

### Required confirmation behavior

For ambiguous or consequential commands, Aquanex must request confirmation:

```text
User: “Send the approval note to the inspection manager.”

Aquanex: “I prepared a draft addressed to inspection.manager@internal,
with Approval_Note.docx and Cost_Matrix.xlsx attached. Please review the
preview and select Approve and Send. I will not send it by voice alone.”
```

## Employee Support and Alerting

The alert engine must be deterministic and policy-driven. The LLM may explain a notification but must not independently create, suppress, or escalate safety/compliance actions without authoritative inputs and policy controls.

```text
Authoritative Sources
(Calendar / CMMS / training system / inspection register / approved SOP)
                 |
                 v
Deterministic Rules Engine
                 |
                 +--> Reminder
                 +--> Warning
                 +--> Escalation candidate
                 |
                 v
Policy, role, schedule, and classification checks
                 |
                 v
Desktop notification / Voice alert / Draft message
                 |
                 v
Approval gate where escalation or external communication is required
```

### Appropriate reminders and alerts

| Category | Example | Default behavior |
|---|---|---|
| Informational | “Shift handover begins in 15 minutes” | Local desktop/voice reminder |
| Task reminder | “Approval note review is due before 5 PM” | Notify task owner |
| Inspection reminder | “Two UT readings require qualified review” | Notify assigned inspector/reviewer |
| Compliance reminder | “Training or certificate expires in 30 days” | Notify employee; escalate only under approved policy |
| Engineering validation | “Mandatory calculation input is missing” | Block release; explain required information |
| Safety review | “Inspection finding awaits authorized sign-off” | Notify relevant role; do not infer safety conclusion |
| Escalation candidate | “Review overdue by approved threshold” | Prepare escalation notification; require policy-based action |

### Useful employee-support features

- Shift-start checklists and reminders.
- Toolbox-talk and PPE reminders where policy allows.
- Inspection and calibration due-date reminders.
- Training and certification expiry reminders.
- Pending task and approval reminders.
- End-of-shift handover summaries from authorized records.
- Meeting preparation summaries from authorized calendar/documents.
- Follow-up reminders based on explicitly approved action items.
- Personal focus reminders or task lists chosen by the employee.

## Employee Privacy Boundaries

Do not position or build Voice Sentinel as a surveillance system.

### Explicitly avoid

- Continuous audio recording.
- Covert microphone activation.
- Emotion, stress, fatigue, health, or personality inference from voice.
- Productivity scoring based on speech, desktop activity, or presence.
- Automatic disciplinary warnings or HR decisions.
- Attendance decisions based solely on voice recognition.
- Recording meetings without clear participant notice and consent.
- Using private/personal data for reminders without clear purpose and access controls.

### Preferred positioning

| Avoid | Prefer |
|---|---|
| “Monitors employee behavior” | “Provides opt-in task, shift, and compliance assistance” |
| “Detects fatigue from voice” | “Lets employees self-report fatigue and request supervisor support” |
| “Automatically warns poor performers” | “Flags policy-defined overdue tasks to authorized owners” |
| “Records all conversations” | “Transcribes only explicitly started and consented sessions” |
| “Tracks employees continuously” | “Provides employee-controlled workplace reminders” |

## Audio Privacy and Data Retention

### Default data policy

- Keep microphone audio in volatile memory during normal voice-command use.
- Delete raw audio after local transcription unless the user explicitly elects to save it for an authorized purpose.
- Store only the transcript when retention is necessary.
- Label stored audio/transcripts with owner, classification, purpose, retention period, and access policy.
- Encrypt retained audio and transcripts at rest.
- Include voice transcripts in the same permission and audit model as other sensitive documents.
- Provide clear microphone/listening indicators in the UI.
- Provide a visible microphone-off switch and secure-mode control.

### Recording consent

Meeting transcription should require:

1. Explicit start action by the authorized host.
2. Visible and audible recording indicator.
3. Notice to participants according to organization policy.
4. Defined meeting purpose and retention classification.
5. Explicit stop action.
6. Controlled access to transcript, summary, and recordings.

## Authentication and Voice Identity

Voice is not sufficient authentication for high-risk industrial or enterprise actions. Voice recordings can be replayed or cloned, and users may be in shared/noisy spaces.

### Required approach

- Require normal local login/SSO session before voice commands can access confidential data.
- Use desktop lock, password/PIN, MFA, or approved local authentication for sensitive workflows.
- Use explicit on-screen confirmation for email, message posting, file writes, ERP requests, drawing release, or final approval actions.
- Treat voice as an input mechanism, not an authorization credential.
- Do not rely on speaker recognition for safety-critical or privileged actions.

## Industrial Usability Requirements

Refinery and inspection environments may contain high background noise, PPE, accents, mixed languages, and equipment identifiers that cannot be misheard.

### Recommended safeguards

- Use push-to-talk as the default in noisy locations.
- Support approved headsets and directional microphones.
- Use local noise suppression and echo cancellation.
- Display live transcript before sensitive tool execution.
- Show an STT confidence score or low-confidence marker.
- Ask for confirmation of equipment tags, dates, units, numerical readings, recipients, and locations.
- Present critical results visually even when reading them aloud.
- Fall back to keyboard/touch input without loss of functionality.
- Support domain-specific vocabulary, tag dictionaries, abbreviations, and language variants through approved offline customization.

### Example confirmation

```text
“I heard ‘12-inch P-301 line, thickness 5.8 millimetres.’
Please confirm the equipment tag and thickness before I calculate remaining safe life.”
```

## Safety-Critical Engineering Rules

Voice interaction must not convert an LLM into an autonomous safety decision-maker.

- Use deterministic, tested code for engineering calculations.
- Display formulas, variables, units, input sources, and intermediate results.
- Require qualified engineer review for inspection conclusions, replacement recommendations, and statutory artifacts.
- Mark generated documents as `DRAFT - HUMAN REVIEW REQUIRED` until approved.
- Do not let spoken instructions directly modify DCS, SCADA, PLC, SIS, or other OT/ICS systems.
- Keep Aquanex separated from plant-control networks in the initial architecture.
- Use voice to retrieve information, generate drafts, and remind people-not to actuate equipment.

## Suggested Modules

```text
backend/
├── app/
│   ├── voice/
│   │   ├── audio_gateway.py
│   │   ├── wake_word.py
│   │   ├── vad.py
│   │   ├── noise_suppression.py
│   │   ├── stt_service.py
│   │   ├── tts_service.py
│   │   ├── voice_session.py
│   │   ├── transcript_policy.py
│   │   └── command_confirmation.py
│   ├── alerts/
│   │   ├── scheduler.py
│   │   ├── rules_engine.py
│   │   ├── notification_router.py
│   │   ├── escalation_policy.py
│   │   ├── calendar_connector.py
│   │   ├── cmms_connector.py
│   │   └── training_compliance_connector.py
│   ├── policy/
│   │   ├── voice_privacy_policy.py
│   │   ├── alert_policy.py
│   │   ├── classification_policy.py
│   │   └── approval_engine.py
│   └── audit/
│       ├── voice_alert_receipts.py
│       └── event_ledger.py
frontend/
├── src/
│   ├── voice_input.js
│   ├── audio_player.js
│   ├── live_transcript.js
│   ├── alert_center.js
│   ├── reminder_settings.js
│   └── privacy_controls.js
```

## Voice Session State Machine

```text
IDLE
  -> WAKE_DETECTED / PUSH_TO_TALK
  -> LISTENING
  -> TRANSCRIBING
  -> POLICY_CHECK
  -> ROUTING
  -> TOOL_OR_RAG_EXECUTION
  -> RESPONSE_GENERATION
  -> SPEAKING + DISPLAYING
  -> IDLE

For any consequential tool action:
  -> PREVIEW_REQUIRED
  -> USER_APPROVAL_REQUIRED
  -> EXECUTE_EXACT_APPROVED_ACTION
  -> AUDIT_RECEIPT
  -> IDLE
```

## Alert Engine State Model

```text
AUTHORITATIVE_EVENT
  -> RULE_MATCHED
  -> USER/ROLE/POLICY_CHECK
  -> NOTIFY
  -> ACKNOWLEDGED | SNOOZED | ESCALATION_CANDIDATE
  -> APPROVAL_IF_REQUIRED
  -> AUDIT_EVENT
```

The rules engine should be able to explain why an alert occurred by naming the authoritative source, rule version, deadline, recipient policy, and escalation threshold.

## Tamper-Evident Voice and Alert Audit Events

Record these events in the append-only hash-chained ledger:

- Voice session started/stopped.
- Wake-word detection event, without storing raw audio by default.
- Transcript created, with transcript hash and retention status.
- Model/router decision.
- Sources retrieved and policy result.
- Tool call requested, previewed, approved, denied, or executed.
- Reminder created, edited, snoozed, acknowledged, or escalated.
- Notification delivered/failed.
- Audio file retained/deleted under policy.

Example event:

```json
{
  "event_type": "voice_reminder_created",
  "task_id": "task-2026-00042",
  "actor": "EMP12345",
  "voice_mode": "push_to_talk",
  "transcript_hash": "sha256:...",
  "reminder": {
    "title": "Review Unit-3 approval note",
    "scheduled_time": "2026-09-09T16:00:00+05:30",
    "delivery": ["desktop", "local_tts"],
    "classification": "INTERNAL"
  },
  "policy_decision": "allowed",
  "previous_hash": "...",
  "event_hash": "..."
}
```

## Security Testing Checklist

### Voice privacy

- [ ] Verify no audio is sent outside approved local services.
- [ ] Verify raw audio is deleted after transcription when retention is disabled.
- [ ] Verify visible listening indicator appears before capture.
- [ ] Verify secure mode blocks microphone capture.
- [ ] Verify unauthorized user cannot retrieve another user’s transcript.

### Command safety

- [ ] Verify ambiguous equipment tag/number/unit causes confirmation request.
- [ ] Verify voice-only command cannot send email or modify files.
- [ ] Verify approval is bound to exact recipients, content, and attachments.
- [ ] Verify voice command cannot bypass role or classification policy.
- [ ] Verify injected instructions in a transcript or document cannot alter tool policy.

### Alerting

- [ ] Verify reminders originate from authoritative source/rule and not model invention.
- [ ] Verify alerts respect user, role, shift, and classification policy.
- [ ] Verify escalation requires approved thresholds and required human authorization.
- [ ] Verify audit ledger contains full alert lifecycle.

### Network and sandbox

- [ ] Verify STT/TTS/model services have no WAN egress.
- [ ] Verify no cloud speech API fallback occurs if local STT/TTS fails.
- [ ] Verify failure is explicit and safe.
- [ ] Verify sandboxes cannot use microphone, local audio files, or WAN routes unless explicitly authorized.

## Implementation Roadmap

### Phase 1: SIH-ready voice experience

Build one high-value, secure demonstration:

- Push-to-talk audio capture in the existing desktop/web UI.
- Local STT using faster-whisper or whisper.cpp.
- Existing Aquanex model/router/RAG/tool workflow.
- Local TTS response using Piper or another approved local engine.
- Local SQLite reminder scheduler.
- Desktop notification and spoken reminder.
- Visible live transcript and privacy state.
- No raw audio retention by default.
- Confirmation required for every send/save/write action.

### Phase 2: Personal voice assistant

- Optional wake-word activation.
- VAD and noise suppression.
- Audio streaming for lower response latency.
- User-controlled reminder preferences.
- Shift handover summaries and task dashboard integration.
- Domain vocabulary customization for refinery tags and terminology.

### Phase 3: Governed enterprise support

- Local calendar/CMMS/training connectors.
- Role-aware compliance reminders.
- Policy-governed manager escalation workflow.
- Meeting transcription with consent/retention controls.
- Audit/SIEM integration and admin dashboard.
- Multilingual support as approved by the organization.

## Recommended SIH Demonstration

1. User activates **push-to-talk** or says “Hey Aquanex.”
2. User asks: “Review this inspection report, check the SOP, calculate remaining safe life, prepare an approval note, and remind me to review it at 4 PM.”
3. Aquanex performs local transcription and displays the transcript.
4. It routes the scanned report to local OCR, retrieves authorized SOPs, and uses deterministic sandboxed calculations.
5. It generates a DOCX draft and reads a concise summary aloud.
6. It creates a local reminder and shows it in the alert center.
7. At the scheduled time, Aquanex displays and speaks: “Your Unit-3 approval-note draft is awaiting review.”
8. The user reviews the document and explicitly approves any mail/message action.
9. The UI shows local-only execution and the task/audit evidence trace.

## README Positioning Text

> **Aquanex Voice Sentinel** provides privacy-preserving, local voice interaction for industrial teams. Speech recognition, wake-word detection, reasoning, retrieval, and speech output run within the organization’s on-premise environment. The system supports opt-in reminders for shifts, training, inspections, approvals, and compliance deadlines, while keeping humans in control of consequential decisions. It does not conduct covert surveillance, infer employee emotions or health conditions, or autonomously issue disciplinary actions.

## Final Recommendation

Build a voice-first experience, but keep it **user-controlled, local, reviewable, and bounded**. The strongest version of a “Jarvis-like” feature is not a bot that listens all day or controls employees-it is a trusted assistant that understands authorized work, explains engineering evidence, creates drafts, helps people remember commitments, and requires accountable human approval before consequential action.
