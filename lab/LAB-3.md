# Module 3: Deploy & Serve

## Overview

Your Cloud Security Advisor — fine-tuned on NIST Cybersecurity Framework and incident response guidance — is sitting as training artifacts in cloud storage. Time to make it real. You will merge the LoRA adapter, publish the model, deploy it to a GPU endpoint, and deploy a thin application that talks to it. By the end, you will have a working cybersecurity chatbot running in production that you can interact with in a browser.

## Objectives

- Understand why organizations self-host fine-tuned models instead of using commercial APIs
- Understand the decoupled inference architecture and the basics of model serving (vLLM, endpoints, chat templates)
- Run Gate 2 (merge + publish) and Gate 3 (deploy endpoint + deploy app)
- Test the live application and observe fine-tuning effects
- Articulate the full pipeline architecture and identify the security gap

## Prerequisites

- Module 2 complete (training finished, adapter in GCS)
- GCP authentication working, GitHub CLI authenticated

## Challenges

### 3.1: Architecture First
Understand what you built and why it's self-hosted. Learn the components of model serving — vLLM, inference endpoints, chat templates — and why the model and app are separated.

### 3.2: Run the Pipeline
Trigger Gate 2 (merge + publish) and Gate 3 (deploy). Watch the pipeline execute and understand what each gate does.

### 3.3: Test Your App
Interact with your deployed chatbot. Observe fine-tuning effects and test the boundaries of your model's knowledge.

### 3.4: Explain the Architecture
Synthesize everything. Trace the full pipeline from training to production and identify what security is missing.

## Customer Context

- "Customers self-host fine-tuned models for data sovereignty, compliance, and domain specialization. The security question they never ask: what scans happened between training and deployment? In most organizations, the answer is none."
- "This is a common enterprise architecture — the model runs on GPU infrastructure, the application is a thin client. Decoupled serving means you can scan and gate the model independently from the app."
- "Gate-based pipelines give you audit points. At each gate, you can scan, verify provenance, and make go/no-go decisions. This is where AIRS fits."

## What's Next

**Presentation Break** — Instructor-led session on AIRS, real incident case studies, and customer scenarios. Then Module 4: AIRS Deep Dive, where you will learn the scanning product before integrating it into your pipeline.

*Transition question: "If someone published a malicious model on HuggingFace and your pipeline downloaded it, what would stop it from executing arbitrary code?" Right now, the answer is nothing.*
