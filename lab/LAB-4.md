# Module 4: AIRS Model Security Deep Dive

## Overview

Welcome to Act 2 — **Understand the Security.**

You have a working ML pipeline with no security checks. Before you can secure it, you need to understand AIRS Model Security inside and out — the way you'd need to demo it to a customer. You'll install the SDK, run your first scans, discover that the base model you've been training on is blocked by default policy, investigate why using the API, and fix the policy.

## Objectives

- Install the AIRS Model Security SDK from authenticated PyPI and run CLI scans
- Scan safe, malicious, and HuggingFace models — interpret the results
- Understand the difference between threat detection rules and governance rules
- Use Claude Code to discover and call the data API for per-rule violation details
- Navigate SCM to explore security groups, rules, and enforcement modes
- Make a policy decision: fix the governance rules blocking your base model

## Prerequisites

- Modules 0-3 completed (working pipeline, deployed model)
- Prisma AIRS tenant with Model Security deployment profile (from Module 0)
- AIRS credentials in `.env`: `MODEL_SECURITY_CLIENT_ID`, `MODEL_SECURITY_CLIENT_SECRET`, `TSG_ID`

## Challenges

### 4.1: Verify Model Security Is Active
Confirm your deployment profile is active in SCM and your credentials authenticate. Understand the RBAC model and service account permissions.

### 4.2: Install the SDK
Follow the official docs to install `model-security-client` from the authenticated PyPI. Set up environment variables for both the lab scripts and the SDK.

### 4.3: Your First Scans
Scan three models: a safe local file, a malicious pickle bomb, and the Qwen base model from HuggingFace. The last one will surprise you.

### 4.4: Explore Security Groups & Rules
Navigate SCM to understand security groups, source types, and the rules that control scanning policy. Categorize rules as threat detection vs governance.

### 4.5: Investigate Scan Violations (Discovery Mode)
The instructor wants you to figure out how to retrieve detailed scan violation data using Claude Code. No prepared steps — you drive.

### 4.6: Fix the Policy
Make a governance decision about the Qwen model. Modify the security group policy and verify the change.

## Customer Context

- "AI Model Security is a deployment profile on your existing AIRS tenant. Your SCM, IAM, and service accounts carry over. Adding scanning capability is a configuration change, not a new infrastructure deployment."
- "Security admins configure policy in SCM — security groups, rules, enforcement. Engineering consumes it through the scan API. They're decoupled by design."
- "The question isn't whether AIRS detects threats — it does. The question is whether your governance rules match your organization's risk tolerance. Same detection engine, configurable enforcement."
- "When a customer says 'HuggingFace already scans models,' the answer is: HF gives visibility, AIRS gives control. Custom policies, pipeline enforcement, private model scanning, security operations integration."

## What's Next

You now understand AIRS scanning. Module 5 integrates everything into your pipeline — the manual scans you ran here become automated CI/CD gates. The pipeline currently has no security checks. You're about to change that.
