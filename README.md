# AWS
Miscellaneous automation utilities for managing AWS resources

---
### IAM (Identity and Access Management)
#### Accounts, groups, users, permissions, policies.

* **Accounts**: A formal contract with AWS that is associated with all of the following entities:
  - An "owner" email-address and password.
  - The control of all resources created. 
  - Payment for the AWS activity related to those resources.   
The AWS account has permission to do anything and everything with all account resources. This is **NOT** the same as a *User*.
---

  * **Users**: Each account can have multiple **users** associated with it. Each user is associates with a single *account*. Users have a set of permissions and policies that determine what AWS resources they can access. Each user has an access key id and secret access key for user identification. When an AWS account is first created, a **root** users is automatically created with complete access to all AWS services and resources in the account. This user is accessed by signing in with the email address and password used to create the account. It best practice to to create *IAM users* for handling the everyday administrative/automation tasks, rather than using the *root* user. The root user should only be used to create the initial *IAM user* and a few other non-standard tasks such as changing account seetings or closing the account. . IAM . Typical *IAM Users* include:
    - "Administrator" Users: typically for creation of additional IAM users, groups, permissions and policies.
    - Other Service/Role Users: users specific to certain roles or resources, for example "NetworkAdmin", "StorageAdmin"

#### List Users
```
aws iam list-users
```
---
 
  * **Groups**: Each account can have multiple groups; each group containing one or more users. A group has a particular set of permissions and policies that get inherited by the users in that group. Groups do not have access key id's or secret access keys.  It is generally more scalable to assign users to *groups* and assign permissions and policies to *groups* rather than *users*. Users inherit permissions and policies from a group.
  
#### List Groups
```
aws iam list-groups
```
---

  * **Permissions**: A permission defines the scope of work a user or group is allowed to do on AWS. For instance, one permission could allow a user or group to upload to an S3 bucket. Another permission could allow a user or group to shut down an EC2 instance. Permissions are grouped into **policies**.
  
---
  * **Policy**: Policies are groups of permissions combined into a single tag. Since a user will probably want to both upload and download from S3, these two permissions could be combined into one policy. Users and groups can have many policies assigned to them.

---

  * **Managed Policy**: Managed policies are permissions created and managed by AWS.  Managed policies are easier to manage, provide version-control and have an auto-update functionality: policies are auto-updated whenever a new AWS service or API is introduced. For example, the AWS *ReadOnlyAccess* policy provides read access to all AWS services and resources. When a new services is launched by AWS. AWS will make sure that *ReadOnlyAccess* policy is updated with this new service, and the change will be applied to all the entities associated with the *ReadOnlyAccess* policy.
   
While managed policies are a good starting point, using managed policies can also have disadvantages such as lack of fine-graned control - "too much accesss" or "not enough access".
  
  * **Inline Policy**: Inline policies are embedded directly into a single entity (user, group or role). This can be useful for enforcing a strict one-to-one relationship between a policy and the entity to which it applies. Therefore, deleting the entity or resource will result in the deletion of inline policy as well. On the other hand this makes them more difficult to manage and re-use - less suited for automation.

#### List all policies:
```
aws iam list-policies --no-only-attached
```
---

### Credentials 
AWS supports different types of Security credentials depending on how you are accessing AWS resources:
  * Email and password (root) - for **root** user logging into AWS Management Console.
  * Email and password (IAM user) - for IAM user logging into AWS Management Console, of Support Center.
  * Multi-factor authentication (MFA): typically used for *root* and other high-priveleged IAM users.
  * Access keys (access key ID and secret access key): Used for access with:
      - AWS-cli: read directly by the AWS SDK
      - AWS api's: Access key used to created a request *signature* which is passed in the the HTTP Authorization header or request query sting.
  * Temporary access keys: provide trusted users with temporary security credentials using AWS Security-Token-Service (STS). Similar to regular access-keys but temporary).
  * Key pairs (public/private): Used for ssh/scp and signed URL's for private content. Key pairs are created outside of any AWS framework and are uploaded to a user's profile.

#### Access-key storage
Access-keys are stored in ~/.aws/credentails file for the account using the SDK **aws** executable or making an API call.  Credentials consist of an pairs of *access-key-id* and *access-secret* identified with an access-profile name which serves as an alias for the set of credentials. You can name the alias anything you like. For example you might have an IAM user named "bfanse" in both your dev and prod AWS accounts and create two profiles: "bfanse-dev" and "bfanse-prod". There are Access Keys that are not associated with any IAM Users, such as the "default" profile. An IAM User can have multiple Access Keys active at the same time. An IAM User can also generate any number of new, temporary Access Keys as well.
