---
source: pdf_url
url: https://docs.paloaltonetworks.com/content/dam/techdocs/en_US/pdf/ai-runtime-security/ai-model-security.pdf
title: AI Model Security
fetched: 2026-02-01T21:49:15.476Z
pages: 62
credentials: Use MODEL_SECURITY_CLIENT_ID and MODEL_SECURITY_CLIENT_SECRET for SDK authentication
---
![](images/fetchpdf-1769982541307.pdf-0-full.png)
# AI Model Security



docs.paloaltonetworks.com


**Contact Information**

Corporate Headquarters:
Palo Alto Networks
3000 Tannery Way
Santa Clara, CA 95054
[www.paloaltonetworks.com/company/contact-support](http://www.paloaltonetworks.com/company/contact-support)


**About the Documentation**

- For the most recent version of this guide or for access to related documentation, visit the Technical
[Documentation portal docs.paloaltonetworks.com.](https://docs.paloaltonetworks.com)

[• To search for a specific topic, go to our search page docs.paloaltonetworks.com/search.html.](https://docs.paloaltonetworks.com/search.html)

- Have feedback or questions for us? Leave a comment on any page in the portal, or write to us at

[documentation@paloaltonetworks.com.](mailto:documentation@paloaltonetworks.com)


**Copyright**

Palo Alto Networks, Inc.
[www.paloaltonetworks.com](https://www.paloaltonetworks.com)


© 2025-2026 Palo Alto Networks, Inc. Palo Alto Networks is a registered trademark of Palo
Alto Networks. A list of our trademarks can be found at [www.paloaltonetworks.com/company/](https://www.paloaltonetworks.com/company/trademarks.html)
[trademarks.html. All other marks mentioned herein may be trademarks of their respective companies.](https://www.paloaltonetworks.com/company/trademarks.html)


**Last Revised**

January 22, 2026


AI Model Security **2** © 2026 Palo Alto Networks, Inc.


### Table of Contents
###### **Secure Your AI Models with AI Model Security.........................................5**

What is AI Model Security?......................................................................................................6
What is a Model?........................................................................................................................ 7
Impact of Model Vulnerabilities...............................................................................................8
AI Model Security Core Components.....................................................................................9
Get Started with AI Model Security.....................................................................................11
Create a Deployment Profile for Prisma AIRS AI Model Security......................12
Configure Identity and Access Management..........................................................17
Install AI Model Security..............................................................................................21
Default Security Groups and Rules...........................................................................25
Customizing Security Groups......................................................................................26
Scanning Models............................................................................................................28
Organize Security Scans with Custom Labels.........................................................34
Viewing Scan Results....................................................................................................40
Understanding Model Security Scan Results..........................................................44
Understanding Model Security Rules...................................................................................47
How Scans, Security Groups, and Rules Work Together.....................................48
Connecting Scans to Rules..........................................................................................50
Security Rule Checks.................................................................................................... 51
Hugging Face Model Rules......................................................................................... 54
Reporting New Threats........................................................................................................... 57
Supported Model Formats......................................................................................................59


AI Model Security **3** © 2026 Palo Alto Networks, Inc.


Table of Contents


AI Model Security **4** © 2026 Palo Alto Networks, Inc.


![](images/fetchpdf-1769982541307.pdf-4-0.png)
## Model Security

|Where Can I Use This?|What Do I Need?|
|---|---|
|• Prisma AIRS (AI Model Security)|Prisma AIRS AI Model Security License|



**5**


Secure Your AI Models with AI Model Security

#### What is AI Model Security?

AI Model Security is an enterprise application designed to enforce comprehensive security
standards for both internal and external machine learning models deployed in production
environments. The application addresses a critical gap in organizational security practices where
machine learning models, despite their significant impact on business operations, often lack the
rigorous security validation that is standard for other data inputs and systems.

In most enterprise environments, traditional data inputs such as PDF files undergo extensive
security scrutiny before processing, yet machine learning models that drive critical business
decisions frequently bypass equivalent security measures. This disparity creates substantial
operational risk, as compromised or inadequately validated models can impact business logic,
data integrity, and decision-making processes. AI Model Security solves this problem by providing
comprehensive model validation through automated security assessments, multi-source support
for both internally developed and third-party models, and proactive identification and remediation
of model-related security vulnerabilities.

By implementing AI Model Security, organizations can establish consistent security standards
across all ML model deployments, significantly reducing operational risk from unvalidated or
compromised models. It enables secure adoption of third-party ML solutions while maintaining
organizational security rules and industry compliance standards. Additionally, it provides
comprehensive audit trails and compliance reporting capabilities, ensuring that AI Model Security
assessments meet regulatory requirements and internal governance standards.


AI Model Security **6** © 2026 Palo Alto Networks, Inc.


Secure Your AI Models with AI Model Security

#### What is a Model?

A Model represents a complete set of files necessary to execute one fundamental inference
operation. The Model follows this organizational structure:

  - **Source** —Where the AI model lives.

  - **Model** —Logical entity (like "sentiment-analyzer").

  - **ModelVersion** —Specific AI model version (like "v1.2.3").

  - **Files** —Artifacts of that AI model version.

Models are the foundational asset of AI/ML workloads and already power many of your key
systems in use today. AI model security focuses on securing your models against threats like:

  - **Deserialization Threats** : Protecting your models from executing malicious and unknown code
at load time.

  - **Neural Backdoors** : Detecting Manchurian Candidate like models.

  - **Runtime Threats** : Protecting your models from executing malicious and unknown code at
inference time.

  - **Invalid Licenses** : Ensuring that your models are not using invalid licenses.

  - **Insecure Formats** : Ensuring that your models use formats that help prevent threats.


AI Model Security **7** © 2026 Palo Alto Networks, Inc.


Secure Your AI Models with AI Model Security

#### Impact of Model Vulnerabilities

Models can execute arbitrary code and existing tooling is not checking that for you. Models have
been found at the root of cloud take over attacks, and can be used to exfiltrate data, or even to
execute ransomware attacks. The sensitivity of the data that models are trained on and exposed
to at inference time makes them a prime target for attackers.


AI Model Security **8** © 2026 Palo Alto Networks, Inc.


Secure Your AI Models with AI Model Security

#### AI Model Security Core Components

AI Model Security enables you to have flexible controls to secure, validate, and manage AI models
across different sources through _Security Groups_, _Sources_, _Rules_, and _Scans_ .

AI Model Security delivers a comprehensive framework to establish and enforce security
standards for AI models across your organization. Unlike traditional security tools that simply
scan for malware, AI Model Security recognizes that AI models require more nuanced security
considerations that incorporate license validation, file format verification, and context-specific
security checks based on the teams and environments using the models.

The AI Model Security approach moves beyond the simplified first-party versus third-party model
distinction to provide granular security controls that scale with enterprise needs. This approach
centers around four key components: _Security Groups_, _Sources_, _Rules_, and _Scans_ .










|Entity|Description|Examples|
|---|---|---|
|Security<br>Groups|Serve as the foundation of your AI Model Security posture,<br>allowing you to combine specific rules and requirements for<br>models from a particular source.|• HuggingFace-<br>Research<br>• S3-Production<br>• Partner-S3-<br>Audit|
|Source|Each Security Group is assigned to a specific_Source_, which<br>represents where model artifacts reside, such as Hugging Face<br>for external models or Local Storage and Object Storage for<br>internal models. The source designation is crucial as it provides<br>metadata that powers specific security rules applicable to<br>models from that source.|• Hugging Face<br>• S3<br>• Local Disk|
|Rules|Within each Security Group, you configure_Rules_ that define<br>the specific evaluations performed on models. Rules can verify<br>proper licensing, check for approved file formats, scan for<br>malicious code, and detect architectural backdoors. Each Rule<br>can be enabled or disabled and configured as blocking or<br>non-blocking, giving you precise control over which security<br>issues prevent model usage versus those that simply generate<br>warnings.|• License<br>Existence<br>Check<br>• Serialization<br>Format Safety<br>• Author<br>Verification<br>• Malicious<br>Backdoor<br>Detection|
|Scan|When models are evaluated against these Rules, a_Scan_ is<br>performed, documenting the verdict across all rules. These<br>Scans create an audit trail of security evaluations and serve as<br>decision points to either promote secure models forward or<br>block potentially threatening ones early in your workflow.<br>Here's what a typical scan will look like:|Scan of fraud-<br>detector:v2.1.0<br>using S3-<br>Production group|



AI Model Security **9** © 2026 Palo Alto Networks, Inc.


Secure Your AI Models with AI Model Security

|Entity|Description|Examples|
|---|---|---|
||||



AI Model Security leverages rules to help organizations establish sophisticated, scalable
security frameworks tailored to their specific requirements. This flexible approach enables
teams to enforce strict blocking mechanisms for high-severity threats while maintaining nondisruptive alerting for compliance monitoring—allowing security teams to effectively manage
risk without hindering developer productivity. The result delivers dual benefits: end users gain
confident access to vetted models through a seamless experience, while security teams receive
comprehensive protection for their AI/ML infrastructure.

To implement AI Model Security effectively, you'll typically need at least two Security Groups: one
for external models using Hugging Face as a Source, and another for internal models using Local
or Object Storage Sources. This separation allows you to apply appropriate security standards
based on the origin and intended use of models across your organization.


AI Model Security **10** © 2026 Palo Alto Networks, Inc.



![](images/fetchpdf-1769982541307.pdf-9-0.png)

![](images/fetchpdf-1769982541307.pdf-9-1.png)
Secure Your AI Models with AI Model Security

#### Get Started with AI Model Security

|Where Can I Use This?|What Do I Need?|
|---|---|
|• Prisma AIRS (AI Model Security)|Prisma AIRS AI Model Security License|



**AI Model Security Workflow**

AI Model Security operates on a two-tier hierarchical structure where each security group
encompasses one or more security rules.


**1. Source Type Binding** : Model Security Groups are initially created and associated with a specific
source type (such as, S3 buckets).


AI Model Security **11** © 2026 Palo Alto Networks, Inc.



![](images/fetchpdf-1769982541307.pdf-10-0.png)
Secure Your AI Models with AI Model Security


**2. Rule Configuration** : Populate these groups with relevant rules. AI Model Security provides
intelligent suggestions and validation based on the selected source type, including default rule
collections tailored to each source.

For instance, a "Verify Author" rule wouldn't be available for S3-based groups since S3 doesn't
maintain author metadata.

Rules operate in either blocking or non-blocking modes, streamlining the previous severitybased threshold system from AI Model Security.

**3. Scanning Process** : During model evaluation, the scan request specifies the applicable model
security group to establish context. The system then processes two rule categories:

   - **Metadata Rules** : Validate model metadata from the source platform

   - **Artifact Rules** : Conduct comprehensive analysis of model files

**4. Result Processing** : Each rule produces a binary PASS or FAIL outcome. The final scan verdict
aggregates all rule results and determines whether to apply blocking enforcement (for critical
issues) or non-Blocking responses (for logging and alerts).

The AI Model Security delivers structured flexibility—the same model can undergo evaluation
against multiple Model Security Groups (such as separate development and production
configurations), each with distinct Source Types and rule sets, enabling context-appropriate
security rules.

##### Create a Deployment Profile for Prisma AIRS AI Model Security

|Where Can I Use This?|What Do I Need?|
|---|---|
|• Prisma AIRS|Prisma AIRS Model Security License|



AI Model Security **12** © 2026 Palo Alto Networks, Inc.



![](images/fetchpdf-1769982541307.pdf-11-0.png)
Secure Your AI Models with AI Model Security


Use this information to deploy a tenant for AI Model Security. Consider the following when
creating a deployment profile:

   - AI Model Security is licensed via NGFW credits.

   - The deployment profile is accessible to all SCM Pro users.

   - The deployment profile is accessible on the Customer Support Portal.

   - For this early access release, the deployment profile name is **AI Model Security (preview)** .


_You need an active deployment profile and have a proper Identity & Access to view the AI_
_Model Security and its features in Prisma AIRS._


Creating a deployment profile for AI Model Security includes the following steps:

**1.** Create the deployment profile.

**2.** Associate the deployment profile with a tenant.

**Create a Deployment Profile for Prisma AIRS AI Model Security in the Customer**
**Support Portal**

**STEP 1 |** [Log in to the Palo Alto Customer Support Portal (CSP).](https://support.paloaltonetworks.com/Support/Index)


**STEP 2 |** Navigate to **Products** - **Software/Cloud NGFW Credits** .


**STEP 3 |** Locate your credit pool and click **Create Deployment Profile** .


**STEP 4 |** Under **Select firewall type**, expand **Prisma AIRS** and select **Model Scanning (preview)** .


**STEP 5 |** Select **Next** .


**STEP 6 |** Enter a **Profile Name** .


_Click_ _**Calculate Estimated Cost**_ _to view the credits used for AI Model Security._


**STEP 7 |** Click **Create Deployment Profile** .

This takes you to the **Software NGFW Credits** page in the **Customer Support Portal** . The page
displays the list of deployment profiles within the credit pool for the selected account.

After creating the deployment profile, you'll associated it with a tenant.


AI Model Security **13** © 2026 Palo Alto Networks, Inc.



![](images/fetchpdf-1769982541307.pdf-12-0.png)
Secure Your AI Models with AI Model Security


**Associate the Deployment Profile with a Tenant**

Use the information in this section to associate a deployment profile with a tenant. Consider the
following:

[• Once the deployment profile is created, you're provided with a link to the Palo Alto Networks](https://apps.paloaltonetworks.com/apps)
[Hub to associate the profile with a TSG.](https://apps.paloaltonetworks.com/apps)

   - You can create a new tenant (TSG), or, you can associate the profile with an existing tenant.

   - If a new tenant is created, a Strata Cloud Manager (SCM) instance is created; this process can
take approximately 15-20 minutes to complete.

   - If you are using an existing tenant, a SCM instance is typically associated with it.

   - Because AI Model Security is accessible for all SCM Pro users, you'll see SCM and Strata
Logging Service (SLS) instances being created; these elements are part of the SCM Pro license.

To associate the deployment profile with a tenant:

**STEP 1 |** In the CSP dashboard, locate your deployment profile and click **Finish Setup** ; this redirects
you to the Palo Alto Networks hub.


**STEP 2 |** Select the name of the CSP account in which you created the deployment profile.


_If you select a new tenant, also select the region where the tenant should be created._
_This is referred to as the platform region. AI Model Security determines which regions_
_are supported._

_Only_ _**Region: United States - Americas**_ _is currently supported._


**STEP 3 |** Select the deployment profile that you want to associate with the tenant.


**STEP 4 |** Select **None** in **Additional Services** .


AI Model Security **14** © 2026 Palo Alto Networks, Inc.



![](images/fetchpdf-1769982541307.pdf-13-0.png)

![](images/fetchpdf-1769982541307.pdf-13-1.png)
Secure Your AI Models with AI Model Security


**STEP 5 |** Agree to the terms, then click **Activate** .


_Deployment Profile activation may take up to two hours. Once activated, the AI model_
_Security will be visible in the Strata Cloud Manager web interface (_ _**Insights**_ _>_ _**Prisma**_
_**AIRS**_ _>_ _**Model Security**_ _)._


You're redirected to the Tenant Management page which shows the instances for the tenant.


**STEP 6 |** [Verify the TSG association in the Hub. To do this:](https://apps.paloaltonetworks.com/apps)

1. Navigate to **Common Services**      - **Tenant Management** .

2. Select the tenant and switch to **Deployment Profiles** .

3. Confirm that the **Profile Association Status** is **Complete** .


**Edit or Update a Deployment Profile**

You can edit an existing deployment profile on the CSP as long as AI Model Security supports
your updates to the deployment profile. These changes may include changing the number of scans
allocated per month.

**STEP 1 |** [Log in to the Palo Alto Customer Support Portal (CSP).](https://support.paloaltonetworks.com/Support/Index)


**STEP 2 |** In the CSP dashboard, click on the three dots (ellipsis or overflow menu) next to your
deployment profile.


**STEP 3 |** Edit, delete or deactivate the deployment profile.


AI Model Security **15** © 2026 Palo Alto Networks, Inc.



![](images/fetchpdf-1769982541307.pdf-14-0.png)

![](images/fetchpdf-1769982541307.pdf-14-1.png)
Secure Your AI Models with AI Model Security


**Deactivate the Deployment Profile**

You can deactivate your deployment profile at any time:

**STEP 1 |** [Log in to the Palo Alto Customer Support Portal (CSP).](https://support.paloaltonetworks.com/Support/Index)


**STEP 2 |** In the CSP dashboard, click on the three dots (ellipsis or overflow menu) next to the
deployment profile.


**STEP 3 |** Select **Deactivate Firewall** .


**Delete the Deployment Profile**

You can delete the deployment profile at any time. Consider the following when deleting the
profile:

   - Ensure that there are no firewalls associated with the deployment profile; you cannot delete
the profile if it is attached to an existing firewall.

   - Deactivate the firewall from the deployment profile first, then delete it.

**STEP 1 |** [Log in to the Palo Alto Customer Support Portal (CSP).](https://support.paloaltonetworks.com/Support/Index)


**STEP 2 |** In the CSP dashboard, click on the three dots (ellipsis or overflow menu) next to the
deployment profile.


**STEP 3 |** If you have not yet deactivated the profile, select **Deactivate Firewall** .


AI Model Security **16** © 2026 Palo Alto Networks, Inc.



![](images/fetchpdf-1769982541307.pdf-15-0.png)
Secure Your AI Models with AI Model Security


**STEP 4 |** After you have successfully deactivated the profile, select **Delete** .

##### Configure Identity and Access Management

|Where Can I Use This?|What Do I Need?|
|---|---|
|• Prisma AIRS (AI Model Security)|Prisma AIRS AI Model Security License|



_If you have an active deployment profile but lack IAM permissions for AI Model Security,_
_it may result in user authentication error. Hence it is important to have an active_
_deployment profile and IAM permission to access AI Model Security._


**STEP 1 |** Navigate to Strata Cloud Manager Identity and Access Management (IAM) settings, **Common**
**Services**      - **Identity & Access** .


**STEP 2 |** Navigate to **Identity & Access** - **Access Management** and select the tenant from the tenants
list. Verify the **Identity Information** for the selected tenant to ensure that the **Role** assigned


AI Model Security **17** © 2026 Palo Alto Networks, Inc.



![](images/fetchpdf-1769982541307.pdf-16-0.png)
Secure Your AI Models with AI Model Security


is either **Superuser** for all apps and services, or a custom role with access to AI Model
Security.


AI Model Security **18** © 2026 Palo Alto Networks, Inc.



![](images/fetchpdf-1769982541307.pdf-17-0.png)
Secure Your AI Models with AI Model Security


**STEP 3 |** (Optional) (Administrator Only) Create a custom role.

1. To create a new custom role and assign it to their identity, select **Roles** and then **Custom**
**Roles** .


2. Enable **AI Model Security** .


3. If you need a service account with API access, select **API** and **Add permissions** and
assign the minimum permissions.


_To use SDK, you need at least the following permissions:_ _**ai_ms_pypi_auth**_ _,_
_**ai_ms.scans**_ _, and_ _**ai_ms.security_groups**_ _._


4. Enter the **Name** and **Description** for the custom role and **Save** the changes.


AI Model Security **19** © 2026 Palo Alto Networks, Inc.



![](images/fetchpdf-1769982541307.pdf-18-0.png)

![](images/fetchpdf-1769982541307.pdf-18-1.png)

![](images/fetchpdf-1769982541307.pdf-18-2.png)
Secure Your AI Models with AI Model Security


5. Create a service account.

A service account is used to provide the credentials needed for generating an access
[token. You also assign roles to service accounts to identify what API actions they can](https://pan.dev/scm/docs/roles-overview/)
take.

[Before you create a service account, you must have created at least one tenant service](https://pan.dev/scm/docs/tenant-service-groups/)
[group (TSG). The service account is added as a user to that TSG.](https://pan.dev/scm/docs/tenant-service-groups/)

You can create the service account using any of the following two methods:

[• By using the Strata Cloud Manager web interface.](https://docs.paloaltonetworks.com/common-services/identity-and-access-access-management/manage-identity-and-access/add-service-accounts)

       - By using the Identity and Access Management APIs.

To create a service account using the Identity and Access Management API, you must
have already created at least one service account using the User Interface, and then
obtained an access token for that account.

To create a service account using the Identity and Access Management API, use
[the create a Service Account API. The Client ID and Client Secret for this account is](https://pan.dev/scm/api/iam/post-iam-v-1-service-accounts/)
returned in the response payload:

```
        {
        "id": "xxxxxxxxxxxxxxxxxxxxx",
        "name": "xxxxxxxxxx",
        "tsg_id": "1111111111",
        "contact_email": "user@example.com",
        "identity_email":
        "xxxxxxxxxx@1111111111.iam.panServiceAccounts.com",
        "description": "Descriptive text",
        "client_id": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "client_secret": "xxxxxxxxxxxxxxxxxxxxx"

```

AI Model Security **20** © 2026 Palo Alto Networks, Inc.


Secure Your AI Models with AI Model Security

```
        }

```

_• The new service account is created within the TSG that is identified in_
_the access token used on the request to create the service account. If you_
_don't want to use your root TSG for this purpose, create a new TSG before_
_you create your service account._

_• No matter which approach you choose for creating a service account,_
_make sure to store the Client Secret immediately, as it cannot be retrieved_
_once the account creation process is complete._

6. Select **Assign Roles** and verify if the custom role that you created appears in the **Apps &**
**Services** list.

##### Install AI Model Security

|Where Can I Use This?|What Do I Need?|
|---|---|
|• Prisma AIRS (AI Model Security)|Prisma AIRS AI Model Security License<br>SCM IAM Service Account with<br>appropriate permissions|



To scan both internal and external models, you require either AI Model Security CLI or SDK. AI
Model Security is available as a Python package that offers both a command-line interface and a
Python SDK. Install the package using your preferred Python package manager.

**STEP 1 |** Generate the `pip` index link.

Copy the script below and save it to your local environment (alternatively, you can create your
own script using this as a reference).

```
    #!/bin/bash
    #
    # Model Security Private PyPI Authentication Script
    # Authenticates with SCM and retrieves PyPI repository URL
    #

```

AI Model Security **21** © 2026 Palo Alto Networks, Inc.



![](images/fetchpdf-1769982541307.pdf-20-0.png)
Secure Your AI Models with AI Model Security

```
    set -euo pipefail

    # Check required environment variables
    : "${MODEL_SECURITY_CLIENT_ID:?Error: MODEL_SECURITY_CLIENT_ID not
    set}"
    : "${MODEL_SECURITY_CLIENT_SECRET:?Error:
    MODEL_SECURITY_CLIENT_SECRET not set}"
    : "${TSG_ID:?Error: TSG_ID not set}"

    # Set default endpoints
    API_ENDPOINT="${MODEL_SECURITY_API_ENDPOINT:-https://
    api.sase.paloaltonetworks.com/aims}"
    TOKEN_ENDPOINT="${MODEL_SECURITY_TOKEN_ENDPOINT:-https://
    auth.apps.paloaltonetworks.com/oauth2/access_token}"

    # Get SCM access token
    TOKEN_RESPONSE=$(curl -sf -X POST "$TOKEN_ENDPOINT" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -u "$MODEL_SECURITY_CLIENT_ID:$MODEL_SECURITY_CLIENT_SECRET" \
    -d "grant_type=client_credentials&scope=tsg_id:$TSG_ID") || {
    echo "Error: Failed to obtain SCM access token" >&2
    exit 1
    }

    SCM_TOKEN=$(echo "$TOKEN_RESPONSE" | jq -r '.access_token')
    if [[ -z "$SCM_TOKEN" || "$SCM_TOKEN" == "null" ]]; then
    echo "Error: Failed to extract access token from response" >&2
    exit 1
    fi

    # Get PyPI URL
    PYPI_RESPONSE=$(curl -sf -X GET "$API_ENDPOINT/mgmt/v1/pypi/
    authenticate" \
    -H "Authorization: Bearer $SCM_TOKEN") || {
    echo "Error: Failed to retrieve PyPI URL" >&2
    exit 1
    }

    PYPI_URL=$(echo "$PYPI_RESPONSE" | jq -r '.url')
    if [[ -z "$PYPI_URL" || "$PYPI_URL" == "null" ]]; then
    echo "Error: Failed to extract PyPI URL from response" >&2
    exit 1
    fi

    echo "$PYPI_URL"

```

**STEP 2 |** Set up authentication using environment variables.
After placing the script in an executable location, you'll need to set several environment
variables before running it. Both the AI Model Security CLI and SDK require authentication
credentials set as environment variables. The client automatically manages OAuth2
authentication with the provided credentials.

```
    export MODEL_SECURITY_CLIENT_ID=<your-client-id>
    export MODEL_SECURITY_CLIENT_SECRET=<your-client-secret>

```

AI Model Security **22** © 2026 Palo Alto Networks, Inc.


Secure Your AI Models with AI Model Security

```
    export TSG_ID=<your-tsg-id>
    export MODEL_SECURITY_API_ENDPOINT="https://
    api.sase.paloaltonetworks.com/aims"

```

**Mandatory Environment Variables**

|Environmental Variable|Description|
|---|---|
|`MODEL_SECURITY_CLIENT_ID`|Client ID of the SCM service account.|
|`MODEL_SECURITY_CLIENT_SECRET`|Client secret of the SCM service account.|
|`TSG_ID`|TSG ID of your tenant service group.|
|`MODEL_SECURITY_API_ENDPOINT`|URL of the AI Model Security API service.|



**Optional Environment Variables**

|Environmental Variable|Description|
|---|---|
|**Set Commands**|**Set Commands**|
|`--base-url`|Base URL of the Model<br>Security API that overrides the<br>`MODEL_SECURITY_API_ENDPOINT`<br>environment variable.|
|`--log-level`|Log level settings:<br>• critical<br>• error<br>• (default) info<br>• debug<br>Setting_debug_ log level is helpful when you<br>want to troubleshoot any issue.|
|`--silent`|(CLI only) Disables all output and logging to<br>standard output.|
|**Show commands**|**Show commands**|
|`--version` or`-v`|(CLI only) Displays the CLI version<br>information.|
|`--help`|(CLI only) Displays the help information.|



AI Model Security **23** © 2026 Palo Alto Networks, Inc.


Secure Your AI Models with AI Model Security


**STEP 3 |** Install AI Model Security package (both SDK and CLI) with `uv` or `pip` .

The SDK enables model scanning across multiple cloud storage platforms. Install the SDK with
support for all model sources or select specific cloud providers to minimize package size.

Available model source types: `aws`, `gcp`, `azure`, `artifactory`, `gitlab`, and `all` .

1. Install AI Model Security package (both SDK and CLI) using `uv`, or.

```
       uv add "model-security-client[all]" --index $(/path/to/
       script.sh)
```

2. Install AI Model Security package (both SDK and CLI) using `pip` .

```
       pip install "model-security-client[all]" --extra-index-url
       <URL from Script>

```

For example, to install AWS cloud storage support.

```
       pip install "model-security-client[aws]" --extra-index-url
       <URL from Script>

```

_The SDK leverages_ _`boto3`_ _for S3,_ _`google-cloud-storage`_ _for GCS, and_ _`azure-`_
_`storage-blob`_ _for Azure. Authentication is handled by these underlying SDKs._
_Refer the respective SDK documentation for authentication setup and additional_
_configuration options._

_• AWS:_ [Credentials - Boto3 1.42.26 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html#environment-variables) _._

_• GCS:_ [How Application Default Credentials works | Authentication | Google](https://docs.cloud.google.com/docs/authentication/application-default-credentials)

[Cloud Documentation](https://docs.cloud.google.com/docs/authentication/application-default-credentials) _._

_• Azure:_ [Authorize access to blobs using Microsoft Entra ID - Azure Storage](https://learn.microsoft.com/en-us/azure/storage/blobs/authorize-access-azure-active-directory) _._

_• JFrog Artifactory:_

_• Use basic authentication. Identity tokens are not supported._

_•_ [Access Tokens](https://jfrog.com/help/r/jfrog-platform-administration-documentation/access-tokens)

_•_ [Comparing Identity Reference Tokens With API Keys](https://jfrog.com/help/r/jfrog-platform-administration-documentation/comparing-identity-reference-tokens-with-api-keys)

_• The model-security-client requires the_ _`ARTIFACTORY_TOKEN`_ _environment_
_variable for the token and_ _`ARTIFACTORY_USERNAME`_ _for the username._

_• Gitlab Model Registry:_

_• Generate token following the instructions in_ [REST API authentication | GitLab](https://docs.gitlab.com/api/rest/authentication/)

[Docs](https://docs.gitlab.com/api/rest/authentication/) _._

_• The_ _`model-security-client`_ _requires the token as the_ _`GITLAB_TOKEN`_
_environment variable._

_• OAuth not supported, refer_ [OAuth 2.0 identity provider API](https://docs.gitlab.com/api/oauth2/#oauth-20-tokens-and-gitlab-registries) _for details._


AI Model Security **24** © 2026 Palo Alto Networks, Inc.


Secure Your AI Models with AI Model Security


**STEP 4 |** Initialize the AI Model Security Python SDK.

To use the Python SDK in your code, import and initialize the AI Model Security client.

```
    from uuid import UUID
    from model_security_client.api import ModelSecurityAPIClient

    # Initialize the client
    client = ModelSecurityAPIClient (
    base_url="https://api.sase.paloaltonetworks.com/aims"
    )

```

The AI Model Security client uses the same environment variables for authentication as the
CLI.
##### Default Security Groups and Rules

|Where Can I Use This?|What Do I Need?|
|---|---|
|• Prisma AIRS (Model Security)|Prisma AIRS Model Security License|



AI Model Security leverages Security Groups to enable you to establish and configure your Model
Security controls. Security Groups have a one-to-one relationship with Model Sources and this
association is permanent once set.

Each Model Source provides specialized metadata that is used in rules and security validation
processes.

AI Model Security supports one default Security Group per source and these security groups are
already created for you. Currently, you cannot create a security group. Use the existing security
groups for your AI model scanning.

   - (Default) Local Storage

  - Hugging Face

  - Amazon S3

   - Google Cloud Storage

   - Azure Blob Storage

   - JFrog Artifactory

   - GitLab Model Registry

Your Strata Cloud Manager tenant includes the following pre-configured default security groups.

|Security Group Name|Model Source|
|---|---|
|Default LOCAL|Local Storage|
|Default HUGGING_FACE|Hugging Face|



AI Model Security **25** © 2026 Palo Alto Networks, Inc.


Secure Your AI Models with AI Model Security

|Security Group Name|Model Source|
|---|---|
|Default S3|Amazon S3|
|Default GCS|Google Cloud Storage|
|Default AZURE|Azure Blob Storage|
|Default ARTIFACTORY|JFrog Artifactory|
|Default GITLAB|GitLab Model Registry|


##### Customizing Security Groups

|Where Can I Use This?|What Do I Need?|
|---|---|
|• Prisma AIRS (AI Model Security)|Prisma AIRS AI Model Security License|



**Create a Model Security Group**

To create a new model security group, follow these steps:

**STEP 1 |** [Log in to Strata Cloud Manager.](https://stratacloudmanager.paloaltonetworks.com/)


**STEP 2 |** Navigate to the **AI Security** - **AI Model Security** - **Model Security Groups** and **Create a**
**Group** .


**STEP 3 |** Enter the **Group Name** and select the **Model Source** type from the drop-down list.
Optionally, configure the security rules that appear and add a description.


**STEP 4 |** (Optional) Configure the compatible security rules by enabling or blocking the rule.


AI Model Security **26** © 2026 Palo Alto Networks, Inc.



![](images/fetchpdf-1769982541307.pdf-25-0.png)
Secure Your AI Models with AI Model Security


**STEP 5 |** Add a Description for the **Model Security Group** .


**STEP 6 |** **Save Changes** .

**Modify a Model Security Group**

To modify a security group's name or description, select the pencil icon adjacent to the group
[name. To change the existing security group's rules, click directly on the group name.](https://docs.paloaltonetworks.com/ai-runtime-security/ai-model-security/model-security-to-secure-your-ai-models/understanding-ai-model-security-rules)

Each rule can be in one of the three states:

|Rule State|State Description|
|---|---|
|**Enabled and blocking**|This rule will always be evaluated and, if<br>violated, will cause the scan to fail and the<br>Model Security CLI to exit with an error code.|
|**Enabled and not blocking**|This rule will always be evaluated, but<br>violations will not affect the overall scan<br>result. The evaluation will still be recorded for<br>future reference.|
|**Disabled**|This rule will not be evaluated when in this<br>state.|



**Delete a Model Security Group**

To delete a model security group, select the trash icon next to its name, and then confirm the
deletion.


AI Model Security **27** © 2026 Palo Alto Networks, Inc.



![](images/fetchpdf-1769982541307.pdf-26-0.png)
Secure Your AI Models with AI Model Security

##### Scanning Models

|Where Can I Use This?|What Do I Need?|
|---|---|
|• Prisma AIRS (AI Model Security)|Prisma AIRS AI Model Security License|



Once your Security Group is configured, you can scan models through either the CLI or Python
SDK. The process varies slightly depending on whether you're scanning Hugging Face AI models
or local models.

While scanning a model using Python SDK:

   - you will need to use `ModelSecurityAPIClient` which is the base object to perform API
calls.

   - you can configure the _base_url_ using environment variables or in your code.

When you scan using SDK, it's your responsibility to enforce allow or block decisions according to
the scan evaluation outcomes.

When you scan using CLI, the CLI will exit with a non-zero exit code if the model is unsafe.


_• AI Model Security can handle up to 1,000 files per scan._

_• You cannot delete a scan._


  - **Scan a Hugging Face Model**

  - **Scan a Local Model**

  - **Scan a Model from Object Storage**

  - **Customize Model Scans**

**Scan a Hugging Face Model**


**Scan a Hugging Face Model**

To scan a model hosted on Hugging Face, provide the model URI and your security group UUID.
For Hugging Face AI models, only `model_uri` is required.


AI Model Security **28** © 2026 Palo Alto Networks, Inc.



![](images/fetchpdf-1769982541307.pdf-27-0.png)
Secure Your AI Models with AI Model Security


_Before you start the model scanning process:_

_• Ensure that the security group source type must match the source of the model that_
_you are scanning. For example, you cannot use a S3 security group on a Hugging Face._

_• Verify and ensure that HuggingFace.co domain (https://huggingface.co/) is allowed._

_• Ensure that the ignore_patterns and allow_patters do not overlap with each other._


We don’t support private Hugging Face repositories. You can only scan public Hugging Face
repositories. If you want to scan private Hugging Face repository, then you can download the
model and scan it using local model scan.


_When creating a scan, you can attach up to 50 custom labels to help_ organize your
scans _._


**Scan using CLI**

```
   model-security scan \
   --security-group-uuid "12345678-1234-1234-1234-123456789012" \
   --model-uri "https://huggingface.co/microsoft/DialoGPT-medium" \
   -l env=production

```

**Scan using Python SDK**

```
   from model_security_client.api import ModelSecurityAPIClient

   # Initialize the client
   client = ModelSecurityAPIClient (
   base_url="https://api.sase.paloaltonetworks.com/aims"
   )
   result = client.scan (
   security_group_uuid="12345678-1234-1234-1234-123456789012",
   model_uri="https://huggingface.co/microsoft/DialoGPT-medium",
   labels={ "env": "production" }
   )

   print(f"Scan completed: {result.eval_outcome}")

```

The AI Model Security automatically fetches the latest version from Hugging Face. To scan a
specific version, include the version parameter.

**Scan using CLI**

```
   model-security scan \
   --security-group-uuid "12345678-1234-1234-1234-123456789012" \
   --model-uri "https://huggingface.co/microsoft/DialoGPT-medium" \
   --model-version "7b40bb0f92c45fefa957d088000d8648e5c7fa33"

```

**Scan using Python SDK**


AI Model Security **29** © 2026 Palo Alto Networks, Inc.


Secure Your AI Models with AI Model Security

```
   from model_security_client.api import ModelSecurityAPIClient

   # Initialize the client
   client = ModelSecurityAPIClient (
   base_url="https://api.sase.paloaltonetworks.com/aims"
   )
   result = client.scan (
   security_group_uuid="12345678-1234-1234-1234-123456789012",
   model_uri="https://huggingface.co/microsoft/DialoGPT-medium",
   model_version="7b40bb0f92c45fefa957d088000d8648e5c7fa33"
   )

```

**Filter Files in Hugging Face Scans**

Large Hugging Face repositories may contain files you don't need to scan. Use global patterns to
include or exclude specific files.

**Scan using CLI**

```
   model-security scan \
   --security-group-uuid "12345678-1234-1234-1234-123456789012" \
   --model-uri "https://huggingface.co/microsoft/DialoGPT-medium" \
   --allow-patterns "*.bin" "*.json" \
   --ignore-patterns "*.md" "*.txt"

```

**Scan using Python SDK**

```
   from model_security_client.api import ModelSecurityAPIClient

   # Initialize the client
   client = ModelSecurityAPIClient (
   base_url="https://api.sase.paloaltonetworks.com/aims"
   )
   result = client.scan (
   security_group_uuid="12345678-1234-1234-1234-123456789012",
   model_uri="https://huggingface.co/microsoft/DialoGPT-medium",
   allow_patterns=["*.bin", "*.json"],
   ignore_patterns=["*.md", "*.txt"]
   )

```

**Scan a Local Model**


**Scan a Local Model**

For models stored locally, specify the path to the model directory. To scan a model from the local
disk, only `model_path` is required.


AI Model Security **30** © 2026 Palo Alto Networks, Inc.


Secure Your AI Models with AI Model Security


_Before you start the model scanning process:_

_• Ensure that the security group source type must match the source of the model that_
_you are scanning. For example, you cannot use a Hugging Face security group on a_
_local model. If you don’t provide any model URI, then by default local disk source type_
_is used._

_• Validate that the model path points to the correct storage location._

_• The ignore_patterns and allow_patters is not applicable for local model scans._

_• Running a model scan can consume up to 4GB memory depending on the size and_
_type of the model. Therefore, ensure that the environment used for the scanning has_
_sufficient resources. Verify if you've enough space to download and sàve the model_
_being scanned._

_• Use_ _`model_path`_ _to specify the local disk location for models._


_When creating a scan, you can attach up to 50 custom labels to help_ organize your
scans _._


**Scan using CLI**

```
   model-security scan \
   --security-group-uuid "12345678-1234-1234-1234-123456789012" \
   --model-path "path/to/local/model" \
   -l env=production

```

**Scan using Python SDK**

```
   from model_security_client.api import ModelSecurityAPIClient

   # Initialize the client
   client = ModelSecurityAPIClient (
   base_url="https://api.sase.paloaltonetworks.com/aims"
   )
   result = client.scan (
   security_group_uuid="12345678-1234-1234-1234-123456789012",
   model_path="path/to/local/model",
   labels={ "env": "production" }
   )

```

**Scan a Model from Object Storage**


**Scan a Model from Object Storage**

We support object storages Amazon S3, Google Cloud Storage, Azure Blob Storage, JFrog
Artifactory, and Gitlab Model Registry. To scan an AI model from these cloud storage models,
provide the URL of these models as `model_uri` parameter while calling the scan on the SDK.

The model security SDK will perform the download for you and queue the model for scan.


AI Model Security **31** © 2026 Palo Alto Networks, Inc.


Secure Your AI Models with AI Model Security


_When creating a scan, you can attach up to 50 custom labels to help_ organize your
scans _._


**Scan using CLI**

```
   model-security scan \
   --security-group-uuid "12345678-1234-1234-1234-123456789012" \

   --model-uri "<model_uri>" \
   --model-name "production-classifier" \
   --model-author "ml-team" \
   --model-version "v2.1" \
   -l env=production

```

**Scan using Python SDK**

```
   from model_security_client.api import ModelSecurityAPIClient

   # Initialize the client
   client = ModelSecurityAPIClient (
   base_url="https://api.sase.paloaltonetworks.com/aims"
   )
   result = client.scan (
   security_group_uuid="12345678-1234-1234-1234-123456789012",

   model_uri="<model_uri>",
   model_name="production-classifier",
   model_author="ml-team",
   model_version="v2.1",
   labels={ "env": "production" }
   )

```

The `model_uri` parameter must use the format of supported cloud storage platforms:

  - Amazon S3 ( `s3://` )

   - Google Cloud Storage ( `gs://` )

   - Azure Blob Storage ( `https://[account].blob.core.windows.net/` )

   - JFrog Artifactory ( `https://[instance].jfrog.io/` )

   - GitLab Model Registry ( `https://[gitlab-instance]/-/ml/models/` )

The CLI shows scan results in real-time as they finish. Each scan tests the model against all active
rules in your Security Group. The output shows whether the model passes or fails based on your
rule configuration.

A model fails if any blocking rule detects a violation. Non-blocking rules record findings without
preventing the model from being approved.


AI Model Security **32** © 2026 Palo Alto Networks, Inc.


Secure Your AI Models with AI Model Security


**Customize Model Scans**


**Customize Model Scans**

You can configure scan execution and adjust result timeout settings.

**Customize Scan using CLI**

```
   model-security scan \
   --security-group-uuid "12345678-1234-1234-1234-123456789012" \
   --model-uri "<model_uri>" \
   --poll-interval-secs 10 \
   --poll-timeout-secs 900 \
   --download-timeout-secs 1800 \       # Object storage
   download timeout
   --download-dir "/custom/download/path"\  # Object storage
   download location
   --cleanup-download-dir \  # Cleanup downloads after scan
   --block-on-errors

```

**Customize Scan using Python SDK**

```
   from model_security_client.api import ModelSecurityAPIClient

   # Initialize the client with download configuration
   client = ModelSecurityAPIClient (
   base_url="https://api.sase.paloaltonetworks.com/aims",
   download_timeout_secs=1800,      # Object storage download
   timeout
   download_dir="/custom/download/path", # Object storage download
   location
   cleanup_download_dir=True       # Cleanup downloads after
   scan
   )

   # Perform scan with polling configuration
   result = client.scan (
   security_group_uuid="12345678-1234-1234-1234-123456789012",
   model_uri="<model_uri>",
   poll_interval_secs=10,
   poll_timeout_secs=900,
   )

```

Following are the configuration options to customize the scan for AI models.






|Configuration Option|Description|Default Value|
|---|---|---|
|`download_timeout_secs`|(Object storage scans only) Specify<br>the timeout duration for model<br>downloads from cloud storage.|600 seconds|
|`download_dir`|(Object storage scans only) Specify<br>the destination directory for|~/.cache/airsms/|



AI Model Security **33** © 2026 Palo Alto Networks, Inc.


Secure Your AI Models with AI Model Security



|Configuration Option|Description|Default Value|
|---|---|---|
||downloading models from object<br>storage.||
|`cleanup_download_dir`|(Object storage scans only) Remove<br>downloaded models after scanning to<br>conserve disk space.|False|
|`poll_interval_secs`|Specify the frequency of scan status<br>checks.|5 seconds|
|`poll_timeout_secs`|Specify the maximum wait time for<br>scan completion.|600 seconds|
||||
|`block_on_errors`|(CLI only) CLI exits with an error code<br>when scan errors occurs.|NA|

##### Organize Security Scans with Custom Labels





|Where Can I Use This?|What Do I Need?|
|---|---|
|• Prisma AIRS (AI Model Security)|Prisma AIRS AI Model Security License|


Model Scan Labels provide a foundational organizational capability that empowers security teams
to categorize, manage, and efficiently navigate their scan results through a flexible custom labeling
system. This feature enables you to attach arbitrary key-value string labels to model scan results
through SDK/APIs and web interface, creating powerful filtering and organizational capabilities
that align with their specific operational needs.

Whether organizing by deployment environment, team ownership, compliance requirements, or
custom workflows, labels offer the metadata structure necessary to manage scan results at scale.
The system supports full CRUD (Create, Read, Update, Delete) operations for label management
and provides advanced filtering capabilities in the web interface, allowing security teams to
structure their scan data according to their organizational model. Our expanded API suite includes
new endpoints and enhanced existing functionality to support comprehensive label management
across all scan operations.

All label APIs follow these validation rules:

|Property|Specification/Validation Rule|
|---|---|
|Label Keys|1-128 characters, alphanumeric with _ and -<br>allowed|
|Label Values|1-256 characters, alphanumeric with _ and -<br>allowed|



AI Model Security **34** © 2026 Palo Alto Networks, Inc.


Secure Your AI Models with AI Model Security


A maximum of 50 labels can be applied for one scan.


_Labels should contain organizational metadata only (such as, environment, team, and_
_region). Do not include sensitive data such as PII, credentials, or confidential business_
_information._


   - Include Label while Scan Creation

  - Add Labels

   - Replace Labels

  - Remove Labels

   - Filter and View Labels

   - Scan Filtering using Labels

**Include Label while Scan Creation**


**`CreateScan`** **API with Labels**

Include labels during scan creation by providing the `labels` parameter:

**Using CLI**

```
   model-security scan \
   --security-group-uuid "your-security-group-uuid" \
   --model-uri "https://huggingface.co/microsoft/DialoGPT-medium" \
   -l env=production \
   -l team=ml-platform \
   -l region=us-west \
   -l compliance=soc2

```

**Using Python SDK**

```
   from uuid import UUID
   from model_security_client.api import ModelSecurityAPIClient

   client = ModelSecurityAPIClient(
   base_url="https://api.sase.paloaltonetworks.com/aims"
   )

   # Scan with labels attached
   result = client.scan(
   security_group_uuid=UUID("your-security-group-uuid"),
   model_uri="https://huggingface.co/microsoft/DialoGPT-medium",
   labels={
   "env": "production",
   "team": "ml-platform",
   "region": "us-west",
   "compliance": "soc2"
   }
   )

   print(f"Scan {result.uuid} created with labels")
   print(f"Labels: {result.labels}")

```

AI Model Security **35** © 2026 Palo Alto Networks, Inc.


Secure Your AI Models with AI Model Security


**Add Labels**


**`AddLabels`** **API**

Add new labels or modify existing ones on a scan. When a label key already exists, the previous
value will be replaced:

**Using CLI**

```
   model-security add-labels 550e8400-e29b-41d4-a716-446655440000 \
   -l owner=alice \
   -l priority=high \
   -l reviewed=true

```

**Using Python SDK**

```
   from uuid import UUID

   scan_uuid = UUID("550e8400-e29b-41d4-a716-446655440000")

   # Add new labels or update existing ones
   client.add_scan_labels(
   scan_uuid=scan_uuid,
   labels={
   "owner": "alice",
   "priority": "high",
   "reviewed": "true"
   }
   )

```

**Replace Labels**


**SetLabels API**

Replace the complete set of existing labels on the scan with the new provided labels.

**Using CLI**

```
   model-security set-labels 550e8400-e29b-41d4-a716-446655440000 \
   -l env=staging \
   -l version=v2-0 \
   -l deployed=false

```

**Using Python SDK**

```
   from uuid import UUID

   scan_uuid = UUID("550e8400-e29b-41d4-a716-446655440000")

   # Replace all existing labels
   client.set_scan_labels(
   scan_uuid=scan_uuid,
   labels={
   "env": "staging",
   "version": "v2-0",

```

AI Model Security **36** © 2026 Palo Alto Networks, Inc.


Secure Your AI Models with AI Model Security

```
   "deployed": "false"
   }
   )

   print(f"Labels set for scan {scan_uuid} (all previous labels
   removed)")

```

**Remove Labels**


**RemoveLabels API**

Remove specific labels from a scan using their keys. Keys that do not exist on the scan are
ignored.

**Using CLI**

```
   model-security delete-labels 550e8400-e29b-41d4-a716-446655440000 \
   -k temporary \
   -k draft \
   -k old-label

```

**Using Python SDK**

```
   from uuid import UUID

   scan_uuid = UUID("550e8400-e29b-41d4-a716-446655440000")

   # Remove specific labels by key
   client.delete_scan_labels(
   scan_uuid=scan_uuid,
   keys=["temporary", "draft", "old-label"]
   )

   print(f"Labels removed from scan {scan_uuid}")

```

**Filter and View Labels**

Using Strata Cloud Manager, view the complete set of labels for each scan in the console.


AI Model Security **37** © 2026 Palo Alto Networks, Inc.


Secure Your AI Models with AI Model Security


Labels enable advanced scan filtering based on custom attributes. Follow these steps to filter
using labels:

**1.** Login to Strata Cloud Manager.

**2.** Navigate to the **AI Security**    - **AI Model Security**    - **Scans** .

**3.** Select **Labels** filter option.


AI Model Security **38** © 2026 Palo Alto Networks, Inc.



![](images/fetchpdf-1769982541307.pdf-37-0.png)
Secure Your AI Models with AI Model Security


**4.** Create a list of label criteria to filter by, then select **Done** .


**Scan Filtering using Labels**


**Using** **`ListScans`** **API with** **`labels_query`**

The `ListScans` API includes a `labels_query` parameter that enables scan filtering based on
labels. This parameter supports AND/OR logic with grouping functionality.

The `labels_query` syntax combines label filters with logical operators.

**Label Filters**

A label filter follows the format `key:value_type` where:

  - `key:value` —Match exact key-value pair (for example, `env:prod` ).

  - `key:*` —Match any value for the specified key (for example, `env:*` )

**Operators**

Valid operators are:

  - `AND` —Logical AND operation (for example, `env:prod AND team:guardian` ).

  - `OR` —Logical OR operation (for example, `env:prod OR env:staging` ).


AI Model Security **39** © 2026 Palo Alto Networks, Inc.



![](images/fetchpdf-1769982541307.pdf-38-0.png)
Secure Your AI Models with AI Model Security


  - `( )` —Single-level grouping for precedence (for example, `(env:prod OR env:staging)`
`AND team:platform` ).


_Nested subqueries are not supported (for example,_ _`((env:prod OR env:dev)`_
_`AND team:ml) OR region:us-west`_ _)._

**Using CLI**

```
   model-security list-scans \
   --labels-query "(env:production OR env:staging) AND (team:ml   platform OR team:security)"

```

**Using Python SDK**

```
   from model_security_client.api import ModelSecurityAPIClient

   client = ModelSecurityAPIClient(base_url="https://
   api.sase.paloaltonetworks.com/aims")

   # List scans that have a label key 'env' with value 'production' or
   'staging' and have a label key 'team' with value 'ml-platform' or
   'security'
   scans = client.list_scans(
   labels_query="(env:production OR env:staging) AND (team:ml   platform OR team:security)"
   )

   for scan in scans.scans:
   print(f"Scan {scan.uuid}: {scan.model_uri}")
   print(f" Labels: {scan.labels}")
   print(f" Outcome: {scan.eval_outcome}")

##### Viewing Scan Results

|Where Can I Use This?|What Do I Need?|
|---|---|
|• Prisma AIRS (AI Model Security)|Prisma AIRS AI Model Security License|


```

The `scan` command displays results directly, showing the overall verdict and key findings. For
deeper analysis, you can retrieve detailed results using the scan ID.

After a model is scanned, it will either pass or fail the scan based on the security checks
performed by AI Model Security. If the model passes the scan, it will be downloaded as usual. If
the model fails the scan, it will fail to download and return a 403 error as well as a Universally
Unique Identifier (UUID) that can be used to view the scan results.

  - **Using CLI**

  - **Strata Cloud Manager**


AI Model Security **40** © 2026 Palo Alto Networks, Inc.


Secure Your AI Models with AI Model Security


**Using CLI**


**Retrieving a Specific Scan (CLI/SDK)**

After a scan completes, note the scan ID from the output. Retrieve the full results at any time.

**Retrieve Scan Results using CLI**

```
   model-security get-scan "87654321-4321-4321-4321-210987654321"

```

**Retrieve Scan Results using Python SDK**

```
   scan_id = "87654321-4321-4321-4321-210987654321"
   scan_result = client.get_scan(scan_id)

   print(f"Scan Status: {scan_result.eval_outcome}")
   print(f"Model URI: {scan_result.model_uri}")
   print(f"Created: {scan_result.created_at}")

```

**View Scan Summary (CLI/SDK)**

View a summary of recent scans to track your security assessments.

**View Scan Summary using CLI**

```
   model-security list-scans --limit 20

```

**View Scan Summary using Python SDK**

```
   scans = client.list_scans(limit=20)

   for scan in scans.scans:
   print(f"Scan {scan.uuid}: {scan.eval_outcome}    {scan.model_uri}")

```

You can also filter scans by source type, evaluation outcome, or time range.

**Filter Scans by source type, evaluation outcome, or time range using CLI**

```
   model-security list-scans \
   --source-types "HUGGING_FACE" "S3" \
   --eval-outcomes "ALLOWED" "BLOCKED" \
   --start-time "2025-01-01T00:00:00" \
   --limit 50

```

**Filter Scans by source type, evaluation outcome, or time range using Python SDK**

```
   from datetime import datetime, timezone
   from airs_schemas.constants import SourceType, EvalOutcome

```

AI Model Security **41** © 2026 Palo Alto Networks, Inc.


Secure Your AI Models with AI Model Security

```
   scans = client.list_scans(
   source_types=[SourceType.HUGGING_FACE, SourceType.S3],
   eval_outcomes=[EvalOutcome.ALLOWED, EvalOutcome.BLOCKED],
   start_time=datetime(2025, 1, 1, tzinfo=timezone.utc),
   limit=50
   )

```

**Strata Cloud Manager**

Although the CLI delivers complete results, the AI Model Security web interface provides
additional tools for analyzing scan findings.

**1.** [Log in to Strata Cloud Manager.](https://stratacloudmanager.paloaltonetworks.com/)

**2.** Navigate to the **AI Security**    - **AI Model Security**    - **Scans** .


AI Model Security **42** © 2026 Palo Alto Networks, Inc.



![](images/fetchpdf-1769982541307.pdf-41-0.png)
Secure Your AI Models with AI Model Security


**3.** Locate your scan by ID or filter the scan list. Review detailed findings for each rule evaluation.
Export results or share them with your team.

Following is an example scan result that is **Allowed** . After locating the specific scan, select
**Overview** to review the evaluation details.


Following is an example scan result that is **Blocked** . After locating the specific scan, select
**Overview** to review the evaluation details.


Select **Files** to review the complete file structure of the model that was scanned, including filelevel violation detail.


AI Model Security **43** © 2026 Palo Alto Networks, Inc.



![](images/fetchpdf-1769982541307.pdf-42-0.png)

![](images/fetchpdf-1769982541307.pdf-42-1.png)
Secure Your AI Models with AI Model Security


Select **JSON** of the specific Scan, to review the details of the scan, its violations (if any), and
rule evaluations and get instructions for retrieving that JSON locally.


The Strata Cloud Manager displays rule violations visually, identifies the specific files or model
components that caused findings, and offers remediation guidance.
##### Understanding Model Security Scan Results

|Where Can I Use This?|What Do I Need?|
|---|---|
|• Prisma AIRS (Model Security)|Prisma AIRS Model Security License|



AI Model Security **44** © 2026 Palo Alto Networks, Inc.



![](images/fetchpdf-1769982541307.pdf-43-0.png)

![](images/fetchpdf-1769982541307.pdf-43-1.png)
Secure Your AI Models with AI Model Security


Once a scan finishes, you can retrieve the results through either the SDK or the Strata Cloud
Manager web interface. The primary check involves determining whether your scanned model is
permitted or restricted.

Execute the following command to retrieve the scan result using the SDK:

```
   scan_result.eval_outcome

```

To view the scan results in the Strata Cloud Manager, navigate to **AI Security**   - **AI Model Security**

   - **Scans** and locate your recently scanned model.


A red shield indicates the model was blocked, while a green shield shows the model is
allowed.

Select the **Scan Request ID** to open a detailed flyover with comprehensive scan information:


AI Model Security **45** © 2026 Palo Alto Networks, Inc.



![](images/fetchpdf-1769982541307.pdf-44-0.png)

![](images/fetchpdf-1769982541307.pdf-44-1.png)
Secure Your AI Models with AI Model Security


This example shows a result of a scan that is blocked due to failure in compliance to the rules: the
use of non-approved file formats and detection of code execution in `unsafe_model.pkl` that
runs during model loading, indicating a potential deserialization attack.

To view the complete JSON response that your SDK would receive, select **JSON** :


AI Model Security **46** © 2026 Palo Alto Networks, Inc.



![](images/fetchpdf-1769982541307.pdf-45-0.png)
Secure Your AI Models with AI Model Security

#### Understanding Model Security Rules

|Where Can I Use This?|What Do I Need?|
|---|---|
|• Prisma AIRS (Model Security)|Prisma AIRS Model Security License|



Model security rules serves as the central mechanism for securing model access. Model security
scanning covers several key areas: thread and metadata. To learn more about threat categories
[and risk mitigation strategies for AI and machine learning systems, refer Model Threats.](https://protectai.com/insights/knowledge-base/deserialization-threats/PAIT-GGUF-101)

Following are the three major threat categories:

|Threat|Description|
|---|---|
|**Deserialization threats**|Issues that arise when you load a model into<br>memory.|
|**Backdoor Threats**|Issues that arise when a model was<br>specifically designed to support alternative or<br>hidden paths in its behavior.|
|**Runtime Threats**|Issues that arise when you use a model to<br>perform inference.|



Model security also examine specific metadata fields in models to address security considerations,
such as verifying a model's license to ensure it's appropriate for commercial use. Model security
rules enables you to validate the following concerns:

|Metadata in Models|Security Rule Validation|
|---|---|
|**Open Source License**|Ensures that the model you are using is<br>licensed for your use case.|
|**Model Format**|Ensures that the model you are using is in a<br>format that is supported by your environment.|
|**Model Location**|Ensures that the model you are using is<br>hosted in a location that is secure and trusted.|
|**Verified Organizations in Hugging Face**|Ensures that the model you are using is from a<br>trusted source.|
|**Model is Blocked**|Overrides all other checks to ensure that a<br>model is blocked no matter what.|



AI Model Security **47** © 2026 Palo Alto Networks, Inc.


Secure Your AI Models with AI Model Security


Our managed rules integrate all of these checks to provide comprehensive security for model
usage. To get started, you can explore your defaults in your Model Security at **AI Security**   - **AI**
**Model Security**   - **Model Security Groups** .

##### How Scans, Security Groups, and Rules Work Together

With Model Security, you initiate a model scan and associate it with a security group. Model
Security evaluates the model against all enabled rules within that security group to assess whether
it satisfies your security requirements. This assessment relies on the results from enabled rules in
the security group and the group's configured threshold.

When you scan a model as follows:

```
   # Import the Model Security SDK/Client
   from model_security_client.api import ModelSecurityAPIClient
   # Load your scanner URL

```

AI Model Security **48** © 2026 Palo Alto Networks, Inc.



![](images/fetchpdf-1769982541307.pdf-47-0.png)
Secure Your AI Models with AI Model Security

```
   scanner_url = os.environ["MODEL_SECURITY_TOKEN_ENDPOINT"]
   # Define your model's URI
   model_uri = "s3://demo-models/unsafe_model.pkl"
   # Set your security group's UUID
   security_group_uuid = "6e2ccc3a-db57-4901-a944-ce65e064a3f1"
   # Create a Model Security Client
   guardian = ModelSecurityAPIClient(base_url=scanner_url)
   # Scan your model
   response = client.scan(model_uri=model_uri,
   security_group_uuid=security_group_uuid)

```

The response will appear as follows (showing the security rules results):

```
   {
   "http_status_code": 200,
   "scan_status_json": {
   "aggregate_eval_outcome": "FAIL",
   "aggregate_eval_summary": {
   "critical_count": 1,
   "high_count": 0,
   "low_count": 0,
   "medium_count": 1
   },
   "violations": [
   {
   "issue": "Model file 'ykilcher_totally-harmless-model/
   retr0reg.gguf' is stored in an unapproved format: gguf",
   "threat": "UNAPPROVED_FORMATS",
   "operator": null,
   "module": null,
   "file": "ykilcher_totally-harmless-model/retr0reg.gguf",
   "hash": "f59ad9c65c5a74b0627eb6ca5c066b02f4a76fe6",
   "threat_description": "Model is stored in a format that your
   Security Group does not allow",
   "policy_name": "Stored In Approved File Format",
   "policy_instance_uuid": "34ef1ddc-0b7a-45b8-a84a   c96b1d8383d0",
   "remediation": {
   "steps": [
   "Store the model in a format approved by your
   organization"
   ]
   }
   },
   {
   "issue": "The model will execute remote code since it
   contains operator `__class__` in Jinja template.",
   "threat": "PAIT-GGUF-101",
   "operator": "__class__",
   "module": null,
   "file": "ykilcher_totally-harmless-model/retr0reg.gguf",
   "hash": "f59ad9c65c5a74b0627eb6ca5c066b02f4a76fe6",
   "threat_description": "GGUF Model Template Containing
   Arbitrary Code Execution Detected",
   "policy_name": "Load Time Code Execution Check",

```

AI Model Security **49** © 2026 Palo Alto Networks, Inc.


Secure Your AI Models with AI Model Security

```
   "policy_instance_uuid": "09780b9f-c4f7-4e0b   ad21-7ff779472283",
   "remediation": {
   "steps": [
   "Use model formats that disallow arbitrary code
   execution"
   ]
   }
   }
   ]
   }
   }

```

Note the `FAIL` status in the `aggregate_eval_outcome` field. This indicates the model did not
pass the scan because security rule failures surpassed your security group's threshold, with the
`violations` field providing details about which rules were breached.

Each model security rule contains the following fields.

|Rule Field|Description|
|---|---|
|**Rule Name**|Specifies the name of the security rule.|
|**Rule Description**|Specifies the description of the security rule.|
|**Compatible Sources**|Specifies the model source types that this rule is<br>compatible with.|
|**Status**|Specifies the status of the security rule, either`Enabled`<br>or`Disabled`. This can be set globally, or at the security<br>group level.|


##### Connecting Scans to Rules

When scanning a model, model security first identifies its format through introspection. After
determining the model type, model security maps it to the taxonomy of model vulnerability
threats and coordinate the specific deeper scans required for that model.

A series of specific threats like `Arbitrary Code Execution At Runtime` are grouped
together when they are reported and are shown in a specific rule. This allows you to block
specific types of threats without having to manage the complexity of all the various formats and
permutations.


_You can also configure common rules for all models regardless of their source type._


AI Model Security **50** © 2026 Palo Alto Networks, Inc.


Secure Your AI Models with AI Model Security

##### Security Rule Checks








|Rule Name|Status|Description|Example|
|---|---|---|---|
|**Runtime**<br>**Code**<br>**Execution**<br>**Check**|`Enabled`|This rule detects Arbitrary Code Execution<br>that can occur during model inference through<br>various methods.|• Keras<br>Model<br>Lambda<br>Layer<br>Arbitrary<br>Code<br>Execution<br>Detected<br>at Model<br>Run Time<br>• TensorFlow<br>SavedModel<br>Contains<br>Arbitrary<br>Code<br>Execution<br>at Model<br>Run Time<br>These attacks<br>mean the<br>model will<br>execute code<br>without your<br>knowledge<br>during use,<br>making this<br>a `Critical`<br>issue to block.<br>Learn more<br>about this<br>threat type<br>here:Runtime<br>Threats.|
|**Known**<br>**Framework**<br>**Operators**<br>**Check**|`Enabled`|Machine learning model formats often include<br>built-in operators to support common data<br>science tasks during model operation. Some<br>frameworks allow custom operator definitions,<br>which poses risks when executing unknown<br>third-party code.|When<br>`TensorFlow`<br>`SavedModel`<br>`Contains`<br>`Unknown`<br>`Operators`<br>is detected, it<br>indicates that<br>the model<br>creator is|



AI Model Security **51** © 2026 Palo Alto Networks, Inc.


Secure Your AI Models with AI Model Security








|Rule Name|Status|Description|Example|
|---|---|---|---|
||||using non-<br>standard<br>tooling<br>approaches.<br>For more<br>information<br>refer,<br>SavedModel<br>Contains<br>Unknown<br>Operators.|
|**Model**<br>**Architecture**<br>**Backdoor**<br>**Check**|`Enabled`|A model's behavior can contain a backdoor<br>embedded in its architecture, specifically<br>through a parallel data flow path within the<br>model. For most inputs, the model operates as<br>expected, but for certain inputs containing a<br>trigger, the backdoor activates and effectively<br>alters the model's behavior.|When`ONNX`<br>`Model`<br>`Contains`<br>`Architectur`<br>`Backdoor`<br>is detected,<br>it warns you<br>that a model<br>has at least<br>one non-<br>standard path<br>requiring<br>further<br>investigation.<br>For more<br>information<br>refer,ONNX<br>Model<br>Contains<br>Architectural<br>Backdoor.|
|**Load Time**<br>**Code**<br>**Execution**<br>**Check**|`Enabled`|This rule is similar to the runtime attacks, but<br>these attacks execute immediately upon model<br>loading. For example, the below python snippet<br>is sufficient to trigger the exploit without your<br>knowledge:<br>`with`<br>` open('path_to_your_model.pkl',`<br>` 'rb') as file:`<br>`            model =`<br>` pickle.load(file)`|When<br>`Pickle,`<br>`Keras`<br>`Lambda`<br>`Layers,`<br>`PyTorch`<br>`models,`<br>`and more`<br>`are all`<br>`vulnerable`<br>`to this`<br>`threat` is<br>detected in a|



AI Model Security **52** © 2026 Palo Alto Networks, Inc.


Secure Your AI Models with AI Model Security








|Rule Name|Status|Description|Example|
|---|---|---|---|
||||model, there's<br>no reliable<br>method to<br>eliminate the<br>threat.<br>However,<br>you can<br>investigate<br>the model's<br>history or,<br>if it's your<br>own model,<br>examine the<br>build process<br>to identify<br>the source of<br>the malicious<br>code.<br>For more<br>information<br>refer,PyTorch<br>Model<br>Arbitrary<br>Code<br>Execution|
|**Suspicious**<br>**Model**<br>**Components**<br>**Check**|`Enabled`|Not all rules target specific threats; some, like<br>this one, assess a model's potential for future<br>exploitation. This check identifies components<br>within the model that could enable malicious<br>code execution later.<br>Example:<br>• Remote code execution being called by<br>fetching external data from Protobuf files or<br>others over the internet.<br>A violation here should prompt you to be<br>cautious and to evaluate all relevant components<br>around the model before making a decision on<br>whether or not the model is safe for use.<br>More information can be found here:Keras<br>Lambda Layers Can Execute Code|`Remote`<br>`code`<br>`execution`<br>`being`<br>`called by`<br>`fetching`<br>`external`<br>`data from`<br>`Protobuf`<br>`files or`<br>`others`<br>`over the`<br>`internet.`<br>This violation<br>prompts<br>caution and<br>thorough<br>evaluation of<br>all relevant<br>model|



AI Model Security **53** © 2026 Palo Alto Networks, Inc.


Secure Your AI Models with AI Model Security








|Rule Name|Status|Description|Example|
|---|---|---|---|
||||components<br>before<br>determining<br>whether the<br>model is safe<br>for use.<br>For more<br>information<br>refer,Keras<br>Lambda<br>Layers Can<br>Execute Code|
|**Stored In**<br>**Approved**<br>**File Format**|`Enabled`|This rule verifies whether the model is stored in<br>a format that you've approved within the rule's<br>list.<br>We recommend enabling these formats by<br>default:<br>• Safetensors<br>• JSON<br>By default Model Security reports that`pickle`<br>and`keras_metadata` are not approved<br>formats.|—|


##### Hugging Face Model Rules

Lastly, there are rules specifically scoped to Hugging Face models. These rules target the
particular metadata you control or that is consistently provided by Hugging Face.












|Hugging Face Model<br>Rule|Status|Description|
|---|---|---|
|License Exists|`Enabled`|The simplest rule in the application. This<br>rule checks to see if the model has a<br>license associated with it.<br>If no license is present, then this rule will<br>fail.|
|License Is Valid For<br>Use|`Enabled`|This rule gives you more control for the<br>models that your organization will run or<br>test. As a commercial entity, you may not<br>want to run models with non-permissive<br>open-source licenses like GPLv3 or others.|



AI Model Security **54** © 2026 Palo Alto Networks, Inc.


Secure Your AI Models with AI Model Security












|Hugging Face Model<br>Rule|Status|Description|
|---|---|---|
|||Adding licenses to the rule will expand the<br>list of licenses that are allowed for use.<br>A reasonable set of defaults are:<br>• apache-2.0<br>• mit<br>• bsd-3.0<br>You can find a full list of license options<br>here:Hugging Face Licenses<br>Note we use the`License identifier`<br>field to map to the license in the model<br>metadata.|
|Model Is Blocked|`Enabled`|Sometimes you just cannot tolerate a<br>model for whatever reason. This rule<br>allows you to block a specific model from<br>being used.<br>The format for blocking a model from<br>Hugging Face relies on the Organization<br>and Model Name.<br>For example`opendiffusion/`<br>`sentiment-check` can be entered and<br>it would block the model`sentiment-`<br>`check` from`opendiffusion`.<br>_When a model is both blocked_<br>_and allowed simultaneously,_<br>_the block takes precedence._|
|Organization Verified<br>By Hugging Face|`Enabled`|Hugging Face is an excellent site for the<br>latest models from all over the world,<br>giving you access to cutting edge research.<br>You may want to restrict organizations<br>from providing unverified models from<br>Hugging Face. This prevents accidentally<br>running models from deceptively similar<br>sources like`facebook-llama` instead of<br>the`legitimate meta-llama` (where<br>`legitimate meta-llama` is the correct<br>model).<br>This rule simply checks that Hugging Face<br>has verified the organization, if that passes|



AI Model Security **55** © 2026 Palo Alto Networks, Inc.


Secure Your AI Models with AI Model Security






|Hugging Face Model<br>Rule|Status|Description|
|---|---|---|
|||the models from the organization will pass<br>this check.|
|Organization Is<br>Blocked|`Enabled`|If you find a particular organization that<br>just delivers problematic models or for any<br>other reason, you'd like to block them, this<br>is your rule.<br>Enter the organization name into the rule<br>and all models from that organization will<br>be blocked.<br>For example`facebook-llama` would<br>block ALL of the models provided by that<br>organization.|



AI Model Security **56** © 2026 Palo Alto Networks, Inc.


Secure Your AI Models with AI Model Security

#### Reporting New Threats

|Where Can I Use This?|What Do I Need?|
|---|---|
|• Prisma AIRS (Model Security)|Prisma AIRS Model Security License|



Our comprehensive vulnerability detection begins with the industry's most extensive dataset
of model security issues. This intelligence is driven by our Huntr community—a network of over
16,000 security researchers who continuously discover novel attack vectors through our bug
[bounty program and strategic partnership with Hugging Face.](https://huggingface.co/)


[You can explore our most recent discoveries in the Insights DB, where we publish vulnerability](https://protectai.com/insights)
assessments from scanning every public model in the Hugging Face repository. The platform
includes mechanisms for security researchers and ML practitioners to challenge or validate our
findings.

[InsightsDB classifies and lists the models as](https://protectai.com/insights/models) **Safe**, **Unsafe**, and **Suspicious** . You can dispute a
[finding in Insights DB by selecting the specific model from the list and](https://protectai.com/insights) **Report an issue** :

  - **Report your finding** if you've found a new threat.

  - **Report an incorrect threat** if you disagree with our findings

This continuous intelligence stream enables us to identify a broad spectrum of vulnerabilities in
your models, including many AI-specific security issues that fall outside the scope of traditional
software vulnerabilities—threats that typically won't appear in the National Vulnerability Database
(NVD) or conventional security feeds.

Model Security operates as a centralized repository of models from third-party sources like
Hugging Face.

Additionally, we provide an on-premises scanning solution that deploys directly within your
infrastructure, enabling you to assess your proprietary models locally without data transmission to
our systems—ensuring complete privacy and security of your assets.


AI Model Security **57** © 2026 Palo Alto Networks, Inc.



![](images/fetchpdf-1769982541307.pdf-56-0.png)
Secure Your AI Models with AI Model Security


AI Model Security **58** © 2026 Palo Alto Networks, Inc.



![](images/fetchpdf-1769982541307.pdf-57-0.png)
Secure Your AI Models with AI Model Security

#### Supported Model Formats

|Where Can I Use This?|What Do I Need?|
|---|---|
|• Prisma AIRS (Model Security)|Prisma AIRS Model Security License|



AI Model Security checks are supported on the following formats:







|Model File Type|File Extension|Model Description|
|---|---|---|
|Microsoft Cognitive<br>Toolkit|`cntk`|Models saved in Microsoft Cognitive<br>Toolkit format.|
|JAX/Flax Models|`flax`|Models created with Flax, a neural<br>network library for JAX.|
|GGUF Models|`gguf`|General-purpose model format using<br>GGUF.|
|Keras 3.x archive|`keras3`|Newer Keras models using the latest<br>Keras version.|
|Keras 1.x/2.x archive|`keras_legacy`|Older Keras models, often saved with<br>HDF5.|
|Keras pickled model|`keras_pickle`|Keras models saved with Python<br>pickle.|
|Keras 1.x/2.x HDF5|`keras_legacy_h5`|Legacy Models in HDF5 format.|
|Keras 3.x HDF5|`keras3_h5`|Models in HDF5 format, compatible<br>with legacy and newer versions.|
|Keras weights file|`keras_weights`|Separate files storing only model<br>weights.|
|Keras model JSON|`keras_model_json`|Models saved in JSON format for<br>architecture storage.|
|Keras metadata protobuf|`keras_metadata`|Auxiliary files that store metadata for<br>Keras models.|
|LightGBM Models|`lightgbm`|Gradient boosting models using<br>LightGBM.|
|Llamafile executable|`llamafile`|Distribute and Run LLMs with a single<br>file.|


AI Model Security **59** © 2026 Palo Alto Networks, Inc.


Secure Your AI Models with AI Model Security







|Model File Type|File Extension|Model Description|
|---|---|---|
|Apache MXNet model|`mxnet`|Models saved in Apache MXNet<br>format.|
|Numpy Array Files|`numpy`|Arrays saved in .npy format.|
|Numpy Zip Files|`numpy_zip`|Arrays compressed in .npz format.|
|Numpy Pickle Files|`numpy_pickle`|Arrays serialized with pickle.|
|ONNX Models|`onnx`|Models saved in Open Neural<br>Network Exchange format.|
|OpenVINO Binary<br>Weights|`openvino_bin`|Compiled binary files for OpenVINO.|
|OpenVINO XML Graph|`openvino_xml`|XML files storing OpenVINO model<br>metadata.|
|Pickle Files|`pickle`|Models serialized using Python's<br>pickle.|
|PyTorch v0.1.1 tar|`pytorch_v0_1_1`|Models saved with v0.1.1 PyTorch<br>version.|
|PyTorch v0.1.10 stacked|`pytorch_v0_1_10`|Models saved with v0.1.10 PyTorch<br>version.|
|PyTorch v1.3+ zip|`pytorch_v1_13`|Models saved with v1.3+ PyTorch<br>version.|
|PyTorch TorchScript|`pytorch_torch_script`|PyTorch's format for serializing<br>models.|
|PyTorch model archive|`pytorch_archive`|Archived files containing serialized<br>models.|
|Rockchip RKNN model|`rknn`|Models saved in Rockchip Neural<br>Network (RKNN) format.|
|Safetensors Weights|`safetensors`|Models saved using safetensors<br>format for secure tensor storage.|
|Safetensors Index|`safetensors_index`|Index files for safetensors.|
|SKLearn Models|`sklearn`|Scikit-learn models serialized for<br>deployment.|


AI Model Security **60** © 2026 Palo Alto Networks, Inc.


Secure Your AI Models with AI Model Security

|Model File Type|File Extension|Model Description|
|---|---|---|
|TensorRT Engine|`tensorrt`|NVIDIA's TensorRT models optimized<br>for inference.|
|TensorFlow SavedModel|`tensorflow`|TensorFlow's standard saved model<br>format.|
|TensorFlow Hub module|`tf_hub`|Models from TensorFlow Hub.|
|TensorFlow MetaGraph|`tf_meta_graph`|TensorFlow's MetaGraph format for<br>exporting graphs.|
|TensorFlow Lite/LiteRT|`litert`|TensorFlow Lightweight format.|
|TensorFlow Lite JSON|`litert_json`|Lightweight format for mobile and<br>embedded devices.|
|TensorFlow.js model|`tf_js`|TensorFlow.js format for models<br>running in the browser.|
|Torch7 Models|`torch`|General format for PyTorch models.|
|JSON Files|`json`|JSON-based configurations or model<br>descriptions.|
|Joblib serialized|`joblib`|Python library that facilitates efficient<br>serialization and deserialization of<br>Python objects.|
|Tar archive|`tar`|A single file that bundles multiple files<br>and directories together, preserving<br>their original structure, permissions,<br>and other file system metadata.|
|Zip archive|`zip`|A file format that combines multiple<br>files into a single compressed archive,<br>making it easier to store, send, and<br>share.|
|NVIDIA NeMo model|`nemo`|Scalable and cloud-native generative<br>AI framework.|
|Zlib compressed|`zlib`|Lossless data compression method.|
|Gzip compressed|`gzip`|Lossless data compression and<br>decompression.|
|Bzip2 compressed|`bzip2`|Files compressed using the bzip2<br>algorithm.|



AI Model Security **61** © 2026 Palo Alto Networks, Inc.


Secure Your AI Models with AI Model Security

|Model File Type|File Extension|Model Description|
|---|---|---|
|LZMA compressed|`lzma`|Lossless data compression algorithm<br>with high compression ratio.|
|XZ compressed|`xz`|Data compression tool in Linux.|
|LZ4 compressed|`lz4`|Extremely fast compression algorithm.|
|7-Zip archive|`7_zip`|Compressed archive file format<br>created by the open-source 7-Zip tool.|
|Hydra config|`hydra`|Open-source Python framework.|
|YAML file|`yaml`|Human-readable data serialization<br>language, often used for configuration<br>files, to structure data like lists and<br>key-value pairs.|



AI Model Security **62** © 2026 Palo Alto Networks, Inc.



