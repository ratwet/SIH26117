# Aquanex CoWork: Sovereign Industrial AI Connector Strategy

## Purpose

This document outlines how SovereignWorkbench (Aquanex) can evolve into an air-gapped, policy-governed industrial coworker. The goal is to let authorized refinery, PSU, and defence users work with internal documents, email, collaboration messages, Office files, drawings, and approved enterprise systems without sending confidential content to external AI services.

> Scope note: This is an engineering and product roadmap, not legal advice. Any integration must be approved by the organization’s IT, OT, cybersecurity, legal, records-management, and data-governance teams.

## Product Vision

**Aquanex CoWork** is a sovereign, air-gapped industrial AI coworker that operates across authorized internal documents, mail, collaboration channels, Office files, engineering drawings, and local enterprise systems.

It uses approved on-premise models and controlled local connectors; applies access policy before retrieval or action; requires human approval for consequential writes; and produces tamper-evident evidence for every task.

## Example Workflow

A refinery engineer asks:

> “Review the latest Unit-3 inspection report, compare it with the previous thickness survey, check the relevant SOP, prepare an approval note and cost workbook, then draft an email to the inspection manager.”

Aquanex CoWork should:

1. Authenticate the engineer and resolve their department, clearance, project, and role.
2. Retrieve only files, mail, drawings, and knowledge-base records that the engineer is authorized to access.
3. Route the scanned inspection report through local OCR/document understanding.
4. Retrieve applicable SOP/API/OISD references through permission-aware local RAG.
5. Run deterministic calculations in an isolated no-egress sandbox.
6. Generate a DOCX approval-note draft and XLSX cost matrix with citations, calculation inputs, and classification labels.
7. Prepare—not automatically send—an email draft with selected recipients and attachments.
8. Show a preview, evidence trace, and exact write/send action to the user.
9. Send/save only after explicit approval.
10. Record identity, source references, model version, tool actions, approvals, artifact hashes, and policy decisions in the tamper-evident audit ledger.

## Reference Architecture

```text
Users / Desktop Workbench
          |
          v
Local SSO / LDAP / Active Directory
          |
          v
Policy Decision Point + Approval Gateway
          |
          v
Aquanex Agent Orchestrator + Task Router
          |
          +--> Local Model Gateway (approved open-weight models)
          +--> OCR / Vision Pipeline
          +--> Permission-Aware RAG
          +--> Deterministic Calculation Service
          +--> Isolated Code Sandbox (no egress)
          +--> Controlled Connector Gateway (MCP/API adapters)
          |       |
          |       +--> Internal Email / Exchange / IMAP-SMTP
          |       +--> Mattermost / Rocket.Chat / approved messaging
          |       +--> SMB/NAS / Document Management System
          |       +--> MS Office / LibreOffice / ONLYOFFICE
          |       +--> AutoCAD / Autodesk Vault / drawing repositories
          |       +--> SAP / ERP / CMMS / EAM (read-only initially)
          |
          v
Tamper-Evident Audit Ledger --> Offline Admin/SIEM Node --> Protected Backups
```

All services should be reachable only through explicit LAN allow-lists, with mTLS or equivalent internal authentication where feasible. The model should never receive unrestricted network, filesystem, or business-system privileges.

## Connector Principles

Every integration must be implemented as a **bounded capability**, not a general “computer control” permission.

### Required controls

- Local-only endpoint or explicitly approved internal endpoint.
- Separate connector service account or delegated identity.
- Least-privilege permissions.
- Explicit allowed data classifications, folders, mailboxes, channels, projects, or systems.
- Read/write/delete permissions separated by policy.
- Human confirmation for consequential actions.
- Request validation before action execution.
- Complete audit receipt for every operation.
- No cloud fallback when a connector fails.
- Network allow-list for the connector process.

### Read versus write

| Operation type | Examples | Default policy |
|---|---|---|
| Read | Search email, retrieve drawing, read workbook, query work order | Allowed only after user authorization and policy check |
| Generate | Create approval-note draft, calculation sheet, slide deck | Generate in task workspace and mark as draft |
| Write | Save file, post message, send email, create work-order draft | Preview plus explicit user/reviewer approval |
| Delete/overwrite | Delete document, overwrite controlled drawing, modify ERP record | Disabled by default; separate controlled workflow if ever enabled |
| Critical action | Plant control, purchase approval, safety sign-off | Outside the scope of autonomous AI; human decision only |

## Model Context Protocol Strategy

MCP can be used as the internal tool-integration protocol. The Aquanex agent acts as the MCP client, while each internal connector runs as a tightly controlled MCP server or API adapter.

### Recommended internal MCP gateway features

- Tool allow-list by user role and task type.
- Per-tool JSON schema validation.
- Connector-specific authentication and authorization.
- Per-tool rate limits and output-size limits.
- No arbitrary shell command tool.
- No unrestricted filesystem roots.
- No unrestricted URL fetching.
- Approval token required for email/message/file-write actions.
- Unified audit-event schema.
- Connector health status and policy version included in every receipt.

Do not connect a strict air-gapped Aquanex deployment directly to public MCP services. A cloud-hosted connector would defeat the core sovereign-data proposition.

## Email Integration

### Supported capabilities

- Search approved internal mailboxes.
- Retrieve authorized messages and attachments.
- Summarize threads and extract action items.
- Draft replies, meeting notes, escalation notes, and inspection summaries.
- Attach Aquanex-generated artifacts from the task workspace.
- Send email only after explicit approval.

### Safe architecture

```text
Aquanex Agent
      |
      v
Internal Email Connector
      |
      +--> IMAP / Exchange read scope
      +--> SMTP / Exchange send scope
      +--> Internal mail server only
```

### Mandatory email controls

- Connector cannot send until a one-time approval token is issued.
- Recipient list, subject, body, attachments, and classification label are frozen before approval.
- Attachments are re-scanned and hash-verified before sending.
- No automatic forwarding to external domains.
- Optional policy: restrict all mail to approved internal domains.
- Show the user a final “Approve and Send” preview.
- Write a signed audit receipt containing sender, recipients, message hash, attachment hashes, and approval event.

### Suggested UI flow

```text
Draft email created
      |
      v
User sees recipients, subject, body, attachments, and classification
      |
      v
User approves exact message
      |
      v
Email connector sends exactly that message
      |
      v
Audit ledger records immutable receipt
```

## Collaboration and Messaging

### Suitable targets

- Mattermost or Rocket.Chat hosted within the organization.
- Internal chat archive or approved collaboration platform.
- Microsoft Teams only if an approved internal/on-prem integration path exists.
- Slack only where it is organizationally approved and compatible with the deployment’s data-boundary policy.

### Supported capabilities

- Search authorized channels/threads.
- Summarize technical discussions.
- Extract decisions and action owners.
- Draft status updates.
- Post a message only after approval.

### Security constraints

- Respect channel and message-level membership permissions.
- Avoid indexing all chat globally into RAG; ingest only approved channels with retention rules.
- Treat retrieved chat text as untrusted content, not tool instructions.
- Prevent the agent from adding members, changing channel permissions, deleting messages, or exporting channel histories by default.

## File, NAS, and Document-Management Integration

### Recommended file model

Aquanex should use three scoped file areas:

| Area | Purpose | Default rights |
|---|---|---|
| Input vault | Authorized source documents and drawings | Read-only |
| Task workspace | Temporary copies, OCR outputs, calculations, intermediate files | Isolated per task |
| Output staging | Generated drafts awaiting human review and controlled promotion | Write only through approval workflow |

### Required safeguards

- Allow-list folders rather than mounting an entire home drive or shared filesystem.
- Preserve upstream document ID, revision, owner, source hash, and classification.
- Create copy-on-write task copies; never overwrite source documents directly.
- Enforce file type, file size, malware-scan, and macro-content policies.
- Prevent path traversal and symlink escapes.
- Log each accessed file ID/path and purpose.

## Office Productivity Integration

### Preferred implementation model

Use backend document-generation and validation tools first. This is more reliable, reproducible, auditable, and secure than unrestricted GUI control of desktop Office applications.

| Format | Preferred technology | Typical Aquanex use |
|---|---|---|
| DOCX | `python-docx` | Approval notes, inspection summaries, formal letters |
| XLSX | `openpyxl` | Cost matrices, UT surveys, calculation workbooks |
| PPTX | `python-pptx` | Executive/board presentation drafts |
| PDF | ReportLab or headless conversion | Controlled reports and previews |
| ODT/ODS/ODP | LibreOffice UNO API | Open-document workflows |
| Collaborative documents | Locally hosted ONLYOFFICE | Multi-user review and document editing |

### LibreOffice integration

Run LibreOffice as a controlled headless service or through its UNO API.

Recommended uses:

- Convert DOCX/XLSX/PPTX to PDF for validation and review.
- Recalculate generated spreadsheets.
- Render documents to PDF/image previews.
- Validate that generated Office files open correctly.
- Create or edit ODT/ODS/ODP in a controlled environment.

### Microsoft Office integration

For Office desktop users, consider a future Aquanex add-in/sidebar that connects solely to an internal Aquanex endpoint such as `https://aquanex.local`.

Potential commands:

- Explain selected calculation
- Check selected text against SOP
- Generate an approval-note draft
- Review spreadsheet anomalies
- Create a slide deck from the current workbook
- Send selected content to Aquanex for local processing

The add-in should send only the user-selected content, display the destination/classification, and require the user to confirm transfer to the local server.

### ONLYOFFICE integration

A locally hosted ONLYOFFICE server can provide browser-based document collaboration while Aquanex provides controlled drafting, review, summarization, and content-generation workflows.

Recommended pattern:

1. Aquanex creates a draft in output staging.
2. Authorized reviewers edit collaboratively in ONLYOFFICE.
3. Reviewer approves the final version.
4. Aquanex records final artifact hash, version, classification, and sign-off in the ledger.

### GUI automation: restricted use

Local GUI automation through screenshot/vision/mouse/keyboard tooling is possible, but should be a last resort.

Appropriate cases:

- Legacy desktop application with no API or export capability.
- Human-supervised data entry into a non-critical local tool.
- Demonstrating an integration where no supported API is available.

Inappropriate cases:

- Unattended email sending.
- Safety-critical spreadsheet edits.
- Privileged administrative tools.
- Silent modification of engineering or controlled documents.

## CAD, AutoCAD, Autodesk, and Engineering Drawings

### Integration hierarchy

| Level | Method | Recommended use |
|---|---|---|
| File-level | DXF/DWG exports, CSV/PDF metadata, task-folder workflows | Best initial SIH implementation |
| Plugin-level | AutoCAD .NET, AutoLISP, ObjectARX extension | Strong production option |
| Repository-level | Autodesk Vault or internal DMS integration | Controlled revisions and permissions |
| GUI automation | Local VLM + keyboard/mouse automation | Legacy-only, supervised fallback |

### Recommended initial CAD capabilities

- Import a **copy** of a permitted drawing into a task workspace.
- Extract title-block values, revision, layers, dimensions, tags, and drawing metadata.
- Run local OCR/vision analysis on rasterized drawings or P&ID pages.
- Identify suspected tags/components/annotations with confidence scores.
- Compare approved drawing revisions and list changed layers/tags/metadata.
- Produce a DXF markup/overlay or a review report; do not overwrite the original.
- Generate preliminary spool, STL, DXF, or heatmap artifacts marked as draft.
- Store page/coordinate references for every finding.

### Non-negotiable boundaries

- Do not autonomously approve or release controlled drawings.
- Do not replace documents in Autodesk Vault or another controlled repository without human sign-off.
- Do not make plant-control recommendations executable by DCS/SCADA/PLC systems.
- Keep Aquanex logically and physically segregated from OT/ICS networks in the initial product.

## ERP, CMMS, and Enterprise Systems

Start with read-only data access.

| System | Initial capability | Avoid initially |
|---|---|---|
| SAP/ERP | Read material/cost/work-order data; create draft reports | Purchase orders, vendor changes, financial postings |
| CMMS/EAM | Retrieve equipment history; draft maintenance recommendations | Autonomous work-order closure or safety status changes |
| LIMS | Read approved lab results | Changing source records |
| Documentum/SharePoint/Vault | Search authorized revisions and metadata | Unattended deletion or publishing |
| OT/ICS | No connector in initial scope | Any live control or set-point action |

For later write actions, introduce separate approval workflows, two-person controls, and transaction-specific validations.

## Security and Compliance Requirements

### Identity and access

- Integrate with LDAP, Active Directory, SAML, or OIDC where available internally.
- Propagate the original user identity to every connector operation.
- Map groups to roles, department, project membership, and clearance.
- Enforce separation of duties: model operator, security auditor, document approver, and business user should not automatically share privileges.

### Permission-aware retrieval

Before every retrieval:

1. Authenticate the user.
2. Determine clearance, department, project entitlement, and purpose.
3. Filter at the source/connector and vector-store level.
4. Only then include approved material in the model context.
5. Record the allow/deny decision in the audit ledger.

### Classification and DLP

- Maintain classification labels: for example `UNCLASSIFIED`, `INTERNAL`, `CONFIDENTIAL`, `RESTRICTED`, and organization-defined higher classes.
- Preserve labels from source material into prompts, outputs, generated artifacts, and email drafts.
- Use headers/footers/watermarks in DOCX/PDF/PPTX where policy requires.
- Block external email domains and uncontrolled exports in protected modes.
- Redact personally identifiable information or vendor-sensitive fields where full disclosure is unnecessary.

### Prompt injection and untrusted content

- Treat email, chat, PDFs, OCR text, images, and RAG results as untrusted data.
- Never allow retrieved text to redefine system policy or tool permissions.
- Keep authorization and approval decisions outside the model prompt.
- Use structured tool calls with strict schemas and server-side validation.
- Test indirect prompt injection in mail attachments, scanned PDFs, chat messages, and drawings.

### Network isolation

- Use no default WAN route for protected interfaces where appropriate.
- Enforce default-deny outbound firewall rules.
- Block DNS egress as well as HTTP/HTTPS.
- Give sandboxes no network interface or route.
- Allow only required local services and ports.
- Keep wireless/cellular/Bluetooth/USB networking disabled in classified operating modes.
- Retain the existing reactive WAN detection and lockout as an additional visible defence layer.

### Auditability

Every connector operation should generate an event such as:

```json
{
  "event_type": "email_draft_created",
  "task_id": "task-2026-00042",
  "actor": "EMP12345",
  "connector": "internal_imap_smtp",
  "operation": "draft_email",
  "source_documents": ["INSPECTION-2026-014"],
  "output_artifacts": ["Approval_Note.docx", "Cost_Matrix.xlsx"],
  "policy_decision": "allowed",
  "approval_required": true,
  "classification": "CONFIDENTIAL",
  "model": {"name": "approved-local-model", "weight_hash": "sha256:..."},
  "previous_hash": "...",
  "event_hash": "..."
}
```

Use a hash-chained, append-only ledger with signed checkpoints. A simple artifact manifest is useful, but it is not sufficient for full action accountability.

## Suggested Repository Modules

```text
backend/
├── app/
│   ├── connectors/
│   │   ├── base.py
│   │   ├── mcp_gateway.py
│   │   ├── policy_gateway.py
│   │   ├── email_connector.py
│   │   ├── messaging_connector.py
│   │   ├── filesystem_connector.py
│   │   ├── office_connector.py
│   │   ├── libreoffice_connector.py
│   │   ├── onlyoffice_connector.py
│   │   ├── cad_connector.py
│   │   ├── vault_connector.py
│   │   ├── erp_readonly_connector.py
│   │   └── cmms_readonly_connector.py
│   ├── policy/
│   │   ├── approval_engine.py
│   │   ├── classification_policy.py
│   │   ├── tool_permissions.py
│   │   ├── retrieval_policy.py
│   │   └── dlp_policy.py
│   ├── audit/
│   │   ├── event_ledger.py
│   │   ├── connector_receipts.py
│   │   └── integrity_verifier.py
│   └── integrations/
│       ├── ldap_ad.py
│       ├── local_siem.py
│       └── offline_update_registry.py
```

## Approval Engine Design

An approval engine should bind consent to the exact intended action.

```text
Agent proposes action
      |
      v
Server validates tool arguments and user authorization
      |
      v
User sees exact target, recipients, content, files, and classification
      |
      v
User/reviewer approves
      |
      v
Short-lived approval token binds to exact action hash
      |
      v
Connector executes that exact action
      |
      v
Tamper-evident receipt is appended to the audit ledger
```

If recipients, attachment hashes, file path, prompt-derived content, or target system change after approval, invalidate the token and request fresh approval.

## Delivery Roadmap

### Phase 1: Hackathon-ready industrial cowork

Implement one impressive end-to-end workflow:

- Local NAS/filesystem connector with allow-listed folders.
- Internal IMAP/SMTP connector or a controlled internal mail demonstration service.
- Permission-aware local RAG.
- OCR of scanned inspection report.
- Deterministic API 570/ASME calculation in no-egress sandbox.
- DOCX approval note + XLSX cost matrix generation.
- Email draft with attachments.
- Exact “Approve and Send” confirmation.
- Visible router selection, network isolation status, and audit receipt.

### Phase 2: Office and collaboration

- LibreOffice headless conversion/validation.
- Document previews and revision/diff views.
- Draft/final/rejected artifact lifecycle.
- Classification watermarking.
- Locally hosted ONLYOFFICE collaboration.
- Mattermost/Rocket.Chat connector with draft/post approval flow.

### Phase 3: Drawing-control workflow

- DXF/PDF drawing import and metadata extraction.
- Revision comparison.
- OCR/vision-assisted P&ID review.
- Markup overlay export to a staged draft location.
- Optional AutoCAD plugin to submit a user-selected drawing copy to Aquanex.

### Phase 4: Enterprise systems

- Read-only SAP/ERP and CMMS/EAM connectors.
- Internal document management/Vault connectors.
- Enhanced policy engine with clearance, department, project, purpose, and retention attributes.
- Formal SIEM, key-management, backup, and incident-response integration.

## Recommended Demonstration Script

1. User logs into Aquanex using a local enterprise identity.
2. User selects an authorized scanned inspection report from an allow-listed folder.
3. Aquanex displays classification and selects the OCR/document model locally.
4. The system retrieves only authorized SOP/standard clauses.
5. Deterministic calculations run in a no-egress sandbox.
6. Aquanex generates a classified, watermarked DOCX approval-note draft and XLSX cost matrix.
7. It prepares an email draft to an internal inspection-manager address with exact attachments.
8. User reviews recipient, body, attachments, artifact preview, evidence sources, and action details.
9. User selects “Approve and Send.”
10. Aquanex sends the exact approved mail through the local internal connector and displays an audit receipt.
11. An unauthorized user attempts the same retrieval and receives a policy denial without restricted content entering the model context.
12. A simulated outbound request is blocked by host/sandbox policy and triggers the existing air-gap alert.

## Claims to Use Carefully

| Avoid | Prefer |
|---|---|
| “Fully compliant” | “Designed to support organization-specific security and compliance controls” |
| “Autonomously sends emails” | “Drafts communications and sends only after explicit authorized approval” |
| “Automatically modifies AutoCAD drawings” | “Creates review overlays/draft outputs in a controlled staging area” |
| “Controls refinery systems” | “Provides evidence-grounded decision support; does not control OT/ICS systems” |
| “Zero data leakage guaranteed” | “Demonstrated local-only processing under documented network and access-control configuration” |
| “Statutory approval by AI” | “AI-generated draft requiring authorized human review and sign-off” |

## Final Recommendation

Build Aquanex CoWork as a **controlled-workflow platform**, not a universal autonomous desktop bot. Start with local file/RAG/OCR/calculation/document/email-draft workflow because it directly matches refinery work and can be demonstrated safely.

The winning distinction is: Aquanex can work across enterprise tools like a cowork agent, but it remains sovereign because every connector is local, permission-bounded, audit-recorded, and approval-gated.
