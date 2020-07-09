## Account management

| Provider | User/role management| Entities                         |
|----------|:-------------------:|----------------------------------|
| AWS      | IAM                 | users, roles                     |
| GCP      | RBAC                | users, groups, service-principal |
| Azure    | IAM                 | users, groups, service-accounts  |
     


#### AWS IAM
AWS captures all user and role management within IAM, which stands for “Identity and Access Management”. Through IAM, you can manage your users and roles, along with all the permissions and visibility those users and service accounts have within your AWS account. There are a couple different IAM entities:

 * Users – used when an actual human will be logging in
 * Roles – used when service accounts or scripts will be interacting with resources
 
Both users and roles can have IAM policies attached, which give specific permissions to operate or view any of the other AWS services.

#### Azure RBAC
Azure utilizes the RBAC system within Resource Manager for user permissions, which stands for “Role Based Access Control”. Granting access to Azure resources starts with creating a Security Principal, which can be one of 3 types:

 * User – a person who exists in Azure Active Directory
 * Group – a collection of users in Azure Active Directory
 * Service Principal – an application or service that needs to access a resource
 
Each Security Principal can be assigned a Role Definition, which is a collection of permissions that they can utilize to view or access resources in Azure. There are a few built-in Role Definitions, such as Owner, Contributor, Reader, and User Access Administrator, but you can also create custom role definitions as well depending on your cloud user management needs.  Roles may be assigned on a subscription by subscription basis.

#### Google Cloud Platform IAM
Google Cloud Platform also uses the term IAM for their user permissions. The general workflow is to grant each “identity” a role that applies to each resource within a project. An identity can be any of the following:

 * Google account – any user with an email that is associated with a Google account
 * Service account – an application that logs in through the Google Cloud API
 * Google group – a collection of Google accounts and service accounts
 * G Suite domain – all Google accounts under a domain in G Suite
 * Cloud Identity domain – all Google accounts in a non-G-Suite organization
 
Roles in Google Cloud IAM are a collection of permissions. There are some primitive roles (Owner, Editor, and Viewer), some predefined roles, and the ability to create custom roles with specific permissions through an IAM policy.

