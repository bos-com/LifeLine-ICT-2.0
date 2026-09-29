# Support Policy



## LifeLine-ICT-2.0



LifeLine-ICT-2.0 is an open-source AI, IoT and GIS platform for environmental disaster intelligence, including flood and other environmental hazard prediction, early warning, and resilient decision support in data-scarce environments.



This document explains how contributors, researchers, students, developers, system administrators, and other users can obtain support when working with the project.



---



## 1. Purpose



The purpose of this support policy is to provide a clear and structured approach for obtaining assistance with LifeLine-ICT-2.0.



Support may be required for:



* Installing and configuring the platform.

* Understanding the project architecture.

* Running the backend services.

* Working with AI and machine-learning components.

* Working with IoT devices and sensor integrations.

* Working with GIS components.

* Working with environmental datasets.

* Running experiments and validation procedures.

* Developing new hazard modules.

* Understanding APIs and services.

* Contributing code or documentation.

* Running tests.

* Deploying the platform.

* Understanding project documentation.

* Resolving ordinary development problems.



The project encourages contributors to use public and searchable support channels whenever possible so that solutions can benefit the wider community.



---



## 2. Before Requesting Support



Before requesting assistance, contributors should first check the available project resources.



Please review:



1. The project README.

2. The project documentation.

3. The architecture documentation.

4. The contribution guidelines.

5. Existing GitHub Issues.

6. Existing discussions where available.

7. Relevant source-code documentation.

8. Installation and deployment instructions.

9. Existing troubleshooting information.



A contributor should first determine whether the problem has already been reported or resolved.



This helps avoid duplicate requests and allows the project community to focus on unresolved issues.



---



## 3. GitHub Issues



GitHub Issues should be used for structured and reproducible project problems.



Appropriate issues include:



* Confirmed software bugs.

* Reproducible technical problems.

* Installation problems affecting multiple users.

* Documentation errors.

* Feature requests.

* Improvements to existing functionality.

* Requests for new hazard modules.

* Test failures.

* Integration problems.

* Data-processing problems.

* AI model implementation problems.

* IoT integration problems.

* GIS functionality problems.

* Performance issues.

* Deployment problems.

* Research and experimental issues that require project tracking.



Before opening an issue, search existing issues to determine whether the problem has already been reported.



When reporting an issue, provide sufficient technical information to allow another contributor to understand and reproduce the problem.



---



## 4. What to Include in a Support Request



A useful support request should normally include:



* A clear description of the problem.

* The component affected.

* The operating system.

* Relevant software versions.

* Python or other runtime versions where applicable.

* The LifeLine-ICT-2.0 branch or commit being used.

* Installation or configuration steps already attempted.

* The command that produced the problem.

* The complete error message where appropriate.

* Relevant logs.

* Expected behaviour.

* Actual behaviour.

* Steps required to reproduce the problem.

* Relevant configuration information that is safe to disclose.



Avoid including passwords, API keys, authentication tokens, private keys, or other secrets.



---



## 5. Reproducible Problems



Where possible, support requests should contain a minimal reproducible example.



A minimal reproducible example should:



1. Clearly identify the affected component.

2. Use the smallest practical dataset or configuration.

3. Provide the required commands.

4. Describe the expected result.

5. Describe the observed result.

6. Include relevant error messages.

7. Exclude confidential information and credentials.



Reproducible problems are easier for maintainers and contributors to investigate.



---



## 6. Installation and Environment Problems



For installation-related problems, provide information about:



* Operating system.

* Hardware architecture.

* Python version.

* Node.js version where applicable.

* Database version where applicable.

* Docker version where applicable.

* Git version.

* Relevant package versions.

* Installation method.

* Commands executed.

* Error messages.



Do not post private credentials or system secrets when requesting installation support.



---



## 7. AI and Machine-Learning Support



For AI-related problems, provide information such as:



* Hazard module involved.

* Model or algorithm being used.

* Dataset or dataset type.

* Feature-processing method.

* Training or inference mode.

* Model version or commit.

* Evaluation method.

* Relevant metrics.

* Error messages.

* Reproduction steps.



Where datasets cannot be publicly shared, provide a safe description of the dataset structure and, where possible, a synthetic or anonymised example.



AI-related support should distinguish between:



* Software implementation problems.

* Data-quality problems.

* Model-performance problems.

* Experimental findings.

* Scientific interpretation.



Unexpected model results should not automatically be treated as software bugs.



---



## 8. IoT and Sensor Support



For IoT-related problems, provide relevant information about:



* Device type.

* Sensor type.

* Firmware version.

* Communication protocol.

* Gateway configuration.

* Network configuration where safe.

* Sampling interval.

* Sensor readings.

* Connectivity status.

* Error messages.

* Relevant logs.

* Steps used to reproduce the problem.



Do not publish device credentials, private network credentials, API tokens, or other sensitive information.



When working with physical devices, contributors should follow appropriate electrical, environmental, and operational safety procedures.



---



## 9. GIS Support



For GIS-related problems, provide information about:



* GIS component affected.

* Dataset type.

* Coordinate reference system.

* Geographic extent where appropriate.

* Processing operation.

* Map or spatial service involved.

* Error messages.

* Expected result.

* Observed result.



Where spatial data contains sensitive information, contributors should use anonymised, aggregated, or synthetic data when requesting public support.



---



## 10. Data and Dataset Support



LifeLine-ICT-2.0 may use environmental datasets from multiple sources.



When reporting data-related problems, identify:



* Dataset name or type.

* Source where permitted.

* Time period.

* Geographic coverage.

* File format.

* Relevant variables.

* Missing-data patterns.

* Data-quality concerns.

* Processing steps.

* Expected behaviour.

* Observed behaviour.



Do not upload confidential, restricted, personal, or otherwise sensitive datasets to public project channels.



Dataset licensing and usage restrictions must be respected.



---



## 11. Research and Experimental Support



LifeLine-ICT-2.0 supports research and experimentation.



Research-related support may include:



* Experimental configuration.

* Baseline comparison.

* Missing-data experiments.

* Sensor-failure simulation.

* Resilience experiments.

* Model evaluation.

* Data preprocessing.

* Reproducibility.

* Validation procedures.

* Performance analysis.



Researchers should clearly distinguish between:



* Established project functionality.

* Experimental functionality.

* Preliminary results.

* Simulated results.

* Validated results.

* Research hypotheses.



Research findings should be documented sufficiently to support reproducibility.



---



## 12. Deployment Support



Deployment-related requests should identify:



* Deployment environment.

* Operating system.

* Container or virtual-machine configuration where applicable.

* Database configuration.

* Network architecture where relevant.

* Service versions.

* Deployment method.

* Logs.

* Error messages.

* Configuration changes already attempted.



Production systems should not expose private infrastructure information in public support requests.



---



## 13. Documentation Problems



Documentation problems should be reported when information is:



* Incorrect.

* Outdated.

* Incomplete.

* Ambiguous.

* Difficult to follow.

* Missing important prerequisites.

* Inconsistent with the actual implementation.



Documentation improvements are valuable contributions to the project.



Where possible, contributors are encouraged to submit a pull request that corrects the documentation.



---



## 14. Feature Requests



Feature requests should explain:



1. The problem being addressed.

2. The proposed functionality.

3. The expected users or beneficiaries.

4. The affected project component.

5. Why the functionality is relevant to LifeLine-ICT-2.0.

6. Potential technical considerations.

7. Potential risks or limitations.



Feature requests should focus on the problem and expected outcome rather than prescribing an implementation without discussion.



New hazard modules should consider the project's hazard-module architecture and common platform services.



---



## 15. New Hazard Module Requests



LifeLine-ICT-2.0 is designed to support multiple environmental hazards.



Requests for new hazard modules may concern areas such as:



* Flood.

* Drought.

* Landslide.

* Wildfire.

* Extreme heat.

* Severe storms.

* Water-level hazards.

* Environmental degradation.

* Other environmental hazards.



A proposed hazard module should explain:



* The hazard being addressed.

* Required data sources.

* Required sensors where applicable.

* Relevant spatial information.

* AI or analytical requirements.

* Expected outputs.

* Alerting requirements.

* Resilience requirements.

* Validation approach.



New modules should reuse common platform services wherever practical.



---



## 16. Security Problems



Security vulnerabilities must not be reported through ordinary public support channels.



If you believe you have discovered a security vulnerability, follow the procedures described in:



`SECURITY.md`



Security reports should be handled responsibly to reduce the risk of harm to project users, contributors, infrastructure, environmental monitoring systems, and other stakeholders.



Do not publicly disclose sensitive vulnerability details before appropriate remediation or disclosure coordination.



---



## 17. Sensitive Information



Never include the following information in public support requests:



* Passwords.

* API keys.

* Authentication tokens.

* Private keys.

* Database passwords.

* Cloud credentials.

* IoT credentials.

* Personal information.

* Confidential research data.

* Restricted environmental datasets.

* Private infrastructure credentials.

* Sensitive security information.



If sensitive information has been accidentally exposed, treat it as potentially compromised and follow the procedures in `SECURITY.md`.



---



## 18. Student Contributors



LifeLine-ICT-2.0 welcomes student participation through the Bugema Open Source Community and other appropriate academic and open-source activities.



Students are encouraged to:



* Read the documentation first.

* Search existing issues.

* Ask clear technical questions.

* Provide reproducible examples.

* Work through assigned GitHub issues.

* Submit small and understandable changes.

* Participate in code reviews.

* Document their work.

* Learn Git and GitHub workflows.

* Respect project governance.

* Ask for clarification when requirements are unclear.



Student contributions should follow the same technical and security standards expected of other contributors.



---



## 19. Research Students



Students using LifeLine-ICT-2.0 for academic research should clearly identify research work as experimental where appropriate.



Research projects should document:



* Research objectives.

* Dataset sources.

* Experimental configuration.

* Methodology.

* Evaluation criteria.

* Limitations.

* Reproducibility information.

* Ethical considerations where applicable.



Academic research should not present simulated or preliminary results as operationally validated results.



---



## 20. Community Support



The project encourages peer-to-peer support among contributors.



Community members are encouraged to:



* Share solutions.

* Provide reproducible examples.

* Improve documentation.

* Link to relevant project documentation.

* Help identify existing issues.

* Suggest safe workarounds.

* Review proposed solutions.



Community support should remain respectful and consistent with the project's `CODE_OF_CONDUCT.md`.



---



## 21. Maintainer Support



Maintainers are responsible for helping the project community navigate significant technical and governance issues.



Maintainer responsibilities may include:



* Triaging issues.

* Identifying duplicate issues.

* Assigning appropriate labels.

* Directing contributors to relevant documentation.

* Coordinating technical investigations.

* Reviewing security-sensitive problems.

* Supporting project architecture decisions.

* Coordinating major feature discussions.

* Maintaining project documentation.



Maintainers are not required to provide unrestricted one-to-one technical support for every implementation problem.



Contributors should make reasonable efforts to investigate problems independently before requesting maintainer assistance.



---



## 22. Response Expectations



LifeLine-ICT-2.0 is an open-source community project.



Support responses may depend on:



* Maintainer availability.

* Issue complexity.

* Number of active contributors.

* Severity of the problem.

* Availability of reproducible information.

* Impact on project functionality.

* Availability of subject-matter expertise.



A support request should not assume an immediate response.



Urgent operational or safety-critical situations should not rely exclusively on the LifeLine-ICT-2.0 open-source support process.



---



## 23. Environmental Early-Warning Systems



LifeLine-ICT-2.0 may eventually support environmental monitoring and early-warning applications.



Project users must not assume that a research prototype, simulated model, or development deployment is an operational emergency-warning system.



Before operational deployment, appropriate validation, monitoring, reliability testing, risk assessment, governance, and responsible operational procedures should be established.



Where decisions may affect people, property, or public safety, LifeLine-ICT-2.0 outputs should be treated as decision-support information unless the relevant system has been appropriately validated and authorised for operational use.



---



## 24. Troubleshooting Principles



When troubleshooting LifeLine-ICT-2.0, contributors should generally follow this sequence:



1. Identify the affected component.

2. Reproduce the problem.

3. Check the documentation.

4. Check existing issues.

5. Check recent changes.

6. Inspect relevant logs.

7. Isolate the failing component.

8. Test the smallest practical case.

9. Document the findings.

10. Create or update an issue where appropriate.



This approach helps prevent unnecessary changes and improves the quality of technical investigations.



---



## 25. Contribution Through Support



Support activities can become valuable project contributions.



A contributor who identifies a recurring problem may help by:



* Improving documentation.

* Adding troubleshooting instructions.

* Creating tests.

* Fixing the underlying bug.

* Adding validation.

* Improving error messages.

* Adding monitoring.

* Creating examples.

* Improving installation instructions.

* Creating a reproducible experiment.



The goal is not only to solve an individual problem but also to improve the project for future users.



---



## 26. Support and Project Governance



Support activities must follow the project's governance documents, including:



* `CONTRIBUTING.md`

* `CODE_OF_CONDUCT.md`

* `SECURITY.md`

* Architecture documentation

* Relevant project documentation

* Applicable GitHub repository policies



Where documents conflict, maintainers should clarify the applicable project policy and update documentation where necessary.



---



## 27. Scope



This support policy applies to the official LifeLine-ICT-2.0 project and its associated open-source development activities.



It covers:



* Source code.

* Documentation.

* AI components.

* IoT components.

* GIS components.

* Data-processing components.

* APIs.

* Backend services.

* Testing.

* Research experiments.

* Development environments.

* Deployment guidance.

* Project infrastructure.



It does not replace professional technical support, emergency response procedures, institutional policies, regulatory requirements, or operational safety procedures.



---



## 28. Final Principle



LifeLine-ICT-2.0 is intended to grow through collaboration, documentation, experimentation, responsible engineering, and shared learning.



A good support request does more than ask for an answer. It helps the community understand a problem and makes it easier for future contributors to solve similar problems.



Contributors are therefore encouraged to:



> **Search first, reproduce carefully, document clearly, ask constructively, and improve the project when possible.**



---



**Maintained by the Bugema Open Source Community (BOSC).**



