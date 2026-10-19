CollectOSS Project Compliance Information
=========================================

`CollectOSS <https://collectoss.org>`__ focuses on collecting data from public git-based code hosting platforms ("Forges") such as GitHub and GitLab. As such, it is almost impossible to entirely avoid collecting Personal Information (sometimes referred to as PII) from users of the platforms that we collect data from.

This page contains basic information and opinions from the maintainers of the CollectOSS project regarding how various key aspects of compliance relate to the design and intended purpose of our software. This is not legal advice and is not written by a lawyer. This document is also not a privacy policy. For legal advice or creation of a privacy policy, we suggest using this page to start a conversation with your lawyer about your specific situation/location.


Responsibilities of the CollectOSS Project
------------------------------------------
CollectOSS is made available under an MIT license. This `license <https://github.com/chaoss/CollectOSS/blob/main/LICENSE>`_ stipulates that this software is provided "as is" without liability or warranty. This is standard practice for open source software projects that make their software broadly available to the public and essentially means that responsibility for use of the software (such as complying with laws and Terms of Service) is the responsibility of the of the software.

While not being legally responsible for your use of this software (including its compliance with any specific privacy laws or platform terms), we do want to do our best to make software that is useful and helps make it easy for users to comply with applicable laws and terms of service.

Why and how do we collect information
-------------------------------------

As part of the `Scope of the CollectOSS project <./scope.rst>`__, we collect data from git-based code hosting platforms ("Forges"), such as GitHub and GitLab. This is part of the core function of the CollectOSS project - enabling open source projects to understand and use public data about both their own and other communities to better understand how to develop better open source software.

CollectOSS, and other metrics tools like it, rely on this data being available to function effectively for its intended purpose. While not public in the strictest sense, this data is used under the existing terms of the forge platforms. As an example, `Github's ToS/privacy policy <https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement>`_ says that “personal data” on github is effectively public if so configured by the user:

   Other Users and the Public: Depending on your account settings, we
   may share Personal Data with other users of the Services and the
   public. You control what information is made public. To adjust your
   settings, visit User Settings in your profile. Please be aware that
   any information you share in a collaborative context may become
   publicly accessible.

Operators of CollectOSS should be aware that, depending on the rest of the content in platform-specific terms, use of CollectOSS data  outside of its intended purpose of evaluating the health of open source communities may be prohibited or could carry legal liability.

It is the responsibility of the operator of a CollectOSS instance to ensure that they (and anyone they choose to grant access to) are compliant with the terms of service of the platforms they are collecting data from and the laws and regulations in their area.

PII we collect
--------------

The data we collect includes:

- Commit metadata, such as email addresses, names, usernames, etc.
- Repository metadata, such as names, descriptions, tags, etc.
- Repository contents, such as code, documentation, etc.
- Repository activity, such as commits, pull requests, issues, comments, etc.
- Contributor metadata, such as usernames, etc.

If you are directly using a CollectOSS instance, we may also Collect some additional data, such as:
- User metadata, such as email address and username when you create your credentials to access your instance.



Where PII is located
--------------------

CollectOSS stores all of its information locally within the application. This means that, once it enters the application, PII is likely to only be found:
- In the CollectOSS database
- In message/task queues and in temporary memory or other caches that we use during active processing of data
- As files disk, such as when cloning a repository to disk

CollectOSS also may make this information available via its API's (REST, database schema, etc) so that other applications can perform analysis on the data. This is the core function of CollectOSS as an application.


Tools for managing your PII
----------------------------

The CollectOSS maintainers plan to make available tools to help instance operators manage the PII in their instances so they can comply with relevant laws and regulations in their area, such as GDPR. These tools will help automate the process of querying, exporting, and removing PII from a CollectOSS database for organizations that are under such compliance obligations.

See `Issue #517 <https://github.com/chaoss/CollectOSS/issues/517>`_ for more information on the progress of these tools.


Opting out
----------

If you are worried about having your PII ingested into CollectOSS as a user of a code forge platform we collect from here are some things you can do to protect your information:

- Review and enable any privacy settings that are available in the forge you are using (i.e. GitHub), such as keeping your email address private from  your profile, blocking pushes that dont match your configured email address, etc.
- Utilize a Pseudonym and anonymous or proxy email address (such as a github noreply address, or another email service that is more anonymous) when making commits (this is very difficult to change retroactively).
- Select a username for use on GitHub (or any other forge) that is unique and not utilized by you on any other social platforms.
- Talk to the owners of the code forge platform you are using and ask them to adjust their terms of service and privacy policies.
- If you know about a CollectOSS instance that is gathering data on repositories you contribute to, you can try to file requests to see copies of, or remove, your data from their instance. 

