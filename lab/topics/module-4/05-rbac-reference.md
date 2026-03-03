# RBAC and Access Control (Do This First)

## Topics to Cover (in order)
1. SCM IAM model -- tenants, service accounts, custom roles
2. Creating a custom role -- minimum permissions for model scanning only
3. Service accounts -- creating a restricted SA for the scanning pipeline
4. Least-privilege principle -- why the scanning SA should not manage security groups
5. Testing the restricted SA -- verify it can scan but cannot administer

## How to Explore
- Use Context7 MCP to fetch SCM API docs for IAM and service accounts
- Look at the permissions model: what permissions exist for AI Model Security?
- This project's scanning credentials: MODEL_SECURITY_CLIENT_ID / CLIENT_SECRET + TSG_ID

## Student Activities
- Create a custom role called "model-scanning-only" with minimum scan permissions
- Create a service account with that role
- Use the restricted SA for all subsequent scanning exercises in Modules 4-7
- Verify: can this SA submit a scan? Can it create or modify security groups?

## Why RBAC First
Every subsequent exercise uses AIRS scanning. By setting up a restricted SA now, students practice least-privilege from the start and use it consistently throughout the lab.
