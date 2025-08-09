# -*- coding: utf-8 -*-
##############################################################################
{
    "name": "Business Process Management",
    'author': 'Daric',
    'website': 'https://daric-saas.ir',
    "version": "17.3.0",
    "depends": ["web", "documents", "requirement"],
    "category": "Governance",
    "summary": "Streamline, automate, and optimize business processes with BPM.",
    "description": """
    Daric BPM (Business Process Management) is a comprehensive tool designed to model, execute, and monitor business workflows efficiently. With a focus on governance and process optimization, this module enables organizations to:
    
    - **Design and visualize workflows** using intuitive BPMN (Business Process Model and Notation) tools.
    - **Streamline approvals, tasks, and document management** for better operational efficiency.
    - **Collaborate effectively** across teams with integrated task management.
    - **Monitor progress in real-time** and ensure alignment with organizational goals.
    - Ensure compliance with industry standards through structured workflows and documentation.

    Features:
    - Workflow automation with BPMN
    - Task tracking and management
    - Integration with document workflows
    - Real-time monitoring and reporting
    - User-friendly wizard-driven workflow creation

    Daric BPM helps you transition from manual processes to an automated, optimized, and scalable operational model.

    Learn more about Daric BPM at [Daric SaaS](https://daric-saas.ir).
    """,
    "application": True,
    "data": [
        "secureity/ir.model.access.csv",
        "views/workflow.xml",
        "wizard/wizard_workflow.xml",
        "views/bpm_process_view.xml",
    ],
    "installable": True,
    "license": "OPL-1",
}
