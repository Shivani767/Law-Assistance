import pandas as pd
import numpy as np
import json
import re

# Define key legal acts and their important sections
ipc_sections = {
    "302": "Punishment for murder",
    "304": "Punishment for culpable homicide not amounting to murder",
    "304A": "Causing death by negligence",
    "304B": "Dowry death",
    "307": "Attempt to murder",
    "323": "Punishment for voluntarily causing hurt",
    "324": "Voluntarily causing hurt by dangerous weapons or means",
    "326": "Voluntarily causing grievous hurt by dangerous weapons or means",
    "354": "Assault or criminal force to woman with intent to outrage her modesty",
    "376": "Punishment for rape",
    "377": "Unnatural offences",
    "379": "Punishment for theft",
    "380": "Theft in dwelling house, etc.",
    "383": "Extortion",
    "384": "Punishment for extortion",
    "392": "Punishment for robbery",
    "395": "Punishment for dacoity",
    "396": "Dacoity with murder",
    "406": "Punishment for criminal breach of trust",
    "420": "Cheating and dishonestly inducing delivery of property",
    "498A": "Husband or relative of husband of a woman subjecting her to cruelty",
    "499": "Defamation",
    "500": "Punishment for defamation",
    "504": "Intentional insult with intent to provoke breach of the peace",
    "506": "Punishment for criminal intimidation",
    "507": "Criminal intimidation by an anonymous communication",
    "509": "Word, gesture or act intended to insult the modesty of a woman"
}

# Criminal Procedure Code (CrPC)
crpc_sections = {
    "41": "When police may arrest without warrant",
    "50": "Person arrested to be informed of grounds of arrest and of right to bail",
    "57": "Person arrested not to be detained more than twenty-four hours",
    "154": "Information in cognizable cases",
    "161": "Examination of witnesses by police",
    "164": "Recording of confessions and statements",
    "167": "Procedure when investigation cannot be completed in twenty-four hours",
    "173": "Report of police officer on completion of investigation",
    "190": "Cognizance of offences by Magistrates",
    "200": "Examination of complainant",
    "204": "Issue of process",
    "207": "Supply to the accused of copy of police report and other documents",
    "225": "Trial to be conducted by Public Prosecutor",
    "228": "Framing of charge",
    "235": "Judgment of acquittal or conviction",
    "300": "Person once convicted or acquitted not to be tried for same offence",
    "302": "Permission to conduct prosecution",
    "313": "Power to examine the accused",
    "357": "Order to pay compensation",
    "374": "Appeals from convictions",
    "378": "Appeal in case of acquittal",
    "437": "When bail may be taken in case of non-bailable offence",
    "438": "Direction for grant of bail to person apprehending arrest",
    "439": "Special powers of High Court or Court of Session regarding bail"
}

# Civil Procedure Code (CPC)
cpc_sections = {
    "1": "Short title, commencement and extent",
    "2": "Definitions",
    "9": "Courts to try all civil suits unless barred",
    "10": "Stay of suit",
    "11": "Res judicata",
    "20": "Other suits to be instituted where defendants reside or cause of action arises",
    "26": "Institution of suits",
    "35": "Costs",
    "39": "Execution of decrees and orders of Supreme Court and certain orders of High Court",
    "51": "Powers of Court to enforce execution",
    "75": "Power of Court to issue commissions",
    "80": "Notice to government or public officer before instituting suit",
    "89": "Settlement of disputes outside the Court",
    "96": "Appeal from original decree",
    "100": "Second appeal",
    "115": "Revision",
    "148": "Enlargement of time",
    "151": "Saving of inherent powers of Court",
    "Order 1": "Parties to Suits",
    "Order 5": "Issue and Service of Summons",
    "Order 6": "Pleadings Generally",
    "Order 7": "Plaint",
    "Order 8": "Written Statement, Set-off and Counter-claim",
    "Order 18": "Hearing of the Suit and Examination of Witnesses",
    "Order 20": "Judgment and Decree",
    "Order 39": "Temporary Injunctions and Interlocutory Orders"
}

# Indian Evidence Act
evidence_act_sections = {
    "3": "Interpretation clause",
    "5": "Evidence may be given of facts in issue and relevant facts",
    "6": "Relevancy of facts forming part of same transaction",
    "17": "Admission defined",
    "24": "Confession caused by inducement, threat or promise",
    "25": "Confession to police officer not to be proved",
    "27": "How much of information received from accused may be proved",
    "32": "Cases in which statement of relevant fact by person who is dead or cannot be found, etc., is relevant",
    "45": "Opinions of experts",
    "59": "Proof of facts by oral evidence",
    "60": "Oral evidence must be direct",
    "65": "Cases in which secondary evidence relating to documents may be given",
    "65B": "Admissibility of electronic records",
    "74": "Public documents",
    "101": "Burden of proof",
    "112": "Birth during marriage, conclusive proof of legitimacy",
    "113A": "Presumption as to abetment of suicide by a married woman",
    "113B": "Presumption as to dowry death",
    "114": "Court may presume existence of certain facts",
    "118": "Who may testify",
    "132": "Witness not excused from answering on ground that answer will criminate",
    "133": "Accomplice",
    "145": "Cross-examination as to previous statements in writing",
    "165": "Judge's power to put questions or order production"
}

it_act_sections = {
    "43": "Penalty and compensation for damage to computer, computer system, etc.",
    "65": "Tampering with computer source documents",
    "66": "Computer related offences",
    "66A": "Punishment for sending offensive messages through communication service, etc.",
    "66B": "Punishment for dishonestly receiving stolen computer resource or communication device",
    "66C": "Punishment for identity theft",
    "66D": "Punishment for cheating by personation by using computer resource",
    "66E": "Punishment for violation of privacy",
    "66F": "Punishment for cyber terrorism",
    "67": "Punishment for publishing or transmitting obscene material in electronic form",
    "67A": "Punishment for publishing or transmitting of material containing sexually explicit act, etc., in electronic form",
    "67B": "Punishment for publishing or transmitting of material depicting children in sexually explicit act, etc., in electronic form",
    "70": "Protected system",
    "72": "Penalty for breach of confidentiality and privacy",
    "79": "Exemption from liability of intermediary in certain cases"
}

mv_act_sections = {
    "184": "Driving dangerously",
    "185": "Driving by a drunken person or by a person under the influence of drugs",
    "186": "Driving when mentally or physically unfit to drive",
    "187": "Punishment for offences relating to accident",
    "188": "Punishment for abetment of certain offences",
    "189": "Racing and trials of speed",
    "190": "Using vehicle in unsafe condition",
    "194": "Driving vehicle exceeding permissible weight",
    "196": "Driving uninsured vehicle",
    "197": "Taking vehicle without authority"
}

# Defendant rights based on offense type
defendant_rights = {
    "general": [
        "Right to legal representation",
        "Right to a fair trial",
        "Right to be presumed innocent until proven guilty",
        "Right to remain silent",
        "Right to present evidence in defense",
        "Right to cross-examine witnesses",
        "Right to appeal to higher courts"
    ],
    "bail": [
        "Right to apply for regular bail under Section 439 of CrPC",
        "Right to apply for anticipatory bail under Section 438 of CrPC",
        "Right to seek bail on the ground of prolonged trial",
        "Right to seek bail on medical grounds",
        "Right to appeal against rejection of bail"
    ],
    "trial": [
        "Right to speedy trial",
        "Right to be informed of charges",
        "Right to be tried in presence",
        "Right to present witnesses",
        "Right to an interpreter if required",
        "Right to appeal against conviction"
    ]
}

# Sample legal precedents from Indian Supreme Court
legal_precedents = [
    {
        "case_name": "Bachan Singh v. State of Punjab",
        "citation": "(1980) 2 SCC 684",
        "section": "302",
        "act": "IPC",
        "summary": "Death penalty should be imposed only in the 'rarest of rare cases'. The court established that life imprisonment is the rule and death penalty is the exception.",
        "key_points": [
            "Death penalty to be awarded in the rarest of rare cases",
            "Aggravating and mitigating circumstances to be considered",
            "Balance sheet of aggravating and mitigating circumstances"
        ]
    },
    {
        "case_name": "K.S. Puttaswamy v. Union of India",
        "citation": "(2017) 10 SCC 1",
        "section": "66, 43",
        "act": "IT Act",
        "summary": "Right to privacy is a fundamental right protected under Article 21 of the Constitution. This impacts how digital evidence and surveillance can be used in cybercrime cases.",
        "key_points": [
            "Right to privacy is a fundamental right under Article 21",
            "Any state intrusion must satisfy tests of legality, necessity, and proportionality",
            "Impacts digital evidence collection in cybercrime cases"
        ]
    },
    {
        "case_name": "Shreya Singhal v. Union of India",
        "citation": "(2015) 5 SCC 1",
        "section": "66A",
        "act": "IT Act",
        "summary": "Section 66A of IT Act was struck down as unconstitutional for being vague and creating a chilling effect on free speech.",
        "key_points": [
            "Section 66A declared unconstitutional and void",
            "Vague terms like 'grossly offensive' and 'menacing character' cannot be basis for criminality",
            "Protected freedom of speech and expression in digital space"
        ]
    },
    {
        "case_name": "State of Tamil Nadu v. K. Balu",
        "citation": "(2017) 2 SCC 281",
        "section": "185",
        "act": "MV Act",
        "summary": "Prohibition of liquor shops along national and state highways to prevent drunken driving and related accidents.",
        "key_points": [
            "Banned liquor vends within 500 meters of national and state highways",
            "Aimed at reducing drunk driving incidents",
            "Emphasized road safety as a public health concern"
        ]
    },
    {
        "case_name": "Arnesh Kumar v. State of Bihar",
        "citation": "(2014) 8 SCC 273",
        "section": "498A",
        "act": "IPC",
        "summary": "Police officers shall not automatically arrest the accused in cases under Section 498A IPC. Proper procedure under Section 41 CrPC must be followed.",
        "key_points": [
            "Automatic arrest in 498A cases prohibited",
            "Police must use checklist under Section 41 CrPC before arrest",
            "Magistrates must examine necessity of arrest when authorizing detention"
        ]
    },
    {
        "case_name": "Navtej Singh Johar v. Union of India",
        "citation": "(2018) 10 SCC 1",
        "section": "377",
        "act": "IPC",
        "summary": "Section 377 of IPC was decriminalized to the extent it criminalized consensual sexual conduct between adults of the same sex.",
        "key_points": [
            "Decriminalized consensual homosexual acts between adults",
            "Recognized sexual orientation as integral to identity and dignity",
            "Applied constitutional morality over social morality"
        ]
    }
]

# Sample bail guidelines based on offense type
bail_guidelines = {
    "bailable": {
        "description": "Offenses where bail is a matter of right and can be granted by the police or court.",
        "procedure": [
            "Application can be made to the officer in charge of police station",
            "If arrested, bail to be granted on furnishing bail bond",
            "No need to go to court if police grants bail",
            "If police refuses, application can be made to Magistrate"
        ],
        "examples": [
            "IPC Section 323: Voluntarily causing hurt",
            "IPC Section 504: Intentional insult",
            "MV Act Section 184: Dangerous driving (first offense)"
        ]
    },
    "non_bailable": {
        "description": "Offenses where bail is not a matter of right but discretion of the court.",
        "procedure": [
            "Application to be made to Magistrate/Sessions Court under Section 437/439 CrPC",
            "Court considers factors like gravity of offense, evidence, possibility of influencing witnesses",
            "Anticipatory bail can be sought under Section 438 CrPC",
            "Higher courts can be approached if lower court refuses bail"
        ],
        "examples": [
            "IPC Section 302: Murder",
            "IPC Section 376: Rape",
            "IT Act Section 66F: Cyber terrorism"
        ]
    },
    "special_provisions": {
        "description": "Special considerations for bail in certain cases.",
        "details": [
            "For sick and infirm persons: Medical grounds can be basis for bail",
            "For women and juveniles: Special provisions exist under law",
            "Undertrials who have served half of maximum punishment: Eligible under Section 436A CrPC",
            "Delay in trial: Can be ground for bail as per Supreme Court judgments"
        ]
    }
}

# Jurisdiction types in Indian legal system
jurisdiction_types = {
    "territorial": {
        "description": "Based on geographical boundaries where the court can exercise its powers.",
        "hierarchy": [
            "Taluka/Munsif Courts (lowest level)",
            "District Courts",
            "High Courts",
            "Supreme Court (highest level)"
        ]
    },
    "subject_matter": {
        "description": "Based on the nature of the case or subject matter involved.",
        "types": [
            "Civil Courts: Deal with property disputes, contracts, etc.",
            "Criminal Courts: Deal with offenses under IPC and other criminal laws",
            "Family Courts: Deal with matrimonial disputes, custody, etc.",
            "Special Courts: NDPS courts, CBI courts, etc."
        ]
    },
    "pecuniary": {
        "description": "Based on the monetary value involved in the case.",
        "limits": [
            "Different courts have different pecuniary limits",
            "Cases valued higher than a specified amount go to higher courts",
            "Varies from state to state"
        ]
    },
    "original": {
        "description": "Power to hear a case for the first time.",
        "courts": [
            "District Courts have original jurisdiction in most matters",
            "High Courts have original jurisdiction in certain matters",
            "Supreme Court has original jurisdiction in disputes between states or state and center"
        ]
    },
    "appellate": {
        "description": "Power to hear appeals from lower courts.",
        "courts": [
            "District Courts hear appeals from Taluka/Munsif Courts",
            "High Courts hear appeals from District Courts",
            "Supreme Court hears appeals from High Courts"
        ]
    }
}

def get_offense_details(section, act="IPC"):
    """
    Get details about a specific offense based on section number and act.
    """
    section_str = str(section)
    
    if act == "IPC":
        sections_dict = ipc_sections
    elif act == "IT Act":
        sections_dict = it_act_sections
    elif act == "MV Act":
        sections_dict = mv_act_sections
    elif act == "CrPC":
        sections_dict = crpc_sections
    elif act == "CPC":
        sections_dict = cpc_sections
    elif act == "Evidence Act":
        sections_dict = evidence_act_sections
    else:
        return None
    
    if section_str in sections_dict:
        return {
            "section": section_str,
            "act": act,
            "title": sections_dict[section_str],
            "rights": defendant_rights["general"],
            "bail_info": get_bail_information(section_str, act)
        }
    return None

def get_bail_information(section, act="IPC"):
    """
    Get bail information for a specific section.
    This is a simplified implementation.
    """
    # In a real system, this would be based on a comprehensive database
    # This is simplified for demonstration purposes
    
    # Sections typically considered non-bailable in IPC
    ipc_non_bailable = ["302", "304", "304B", "307", "326", "376", "377", "392", "395", "396", "498A"]
    it_non_bailable = ["66F", "67", "67A", "67B"]
    mv_non_bailable = ["185", "187", "189"]
    
    if act == "IPC" and section in ipc_non_bailable:
        return bail_guidelines["non_bailable"]
    elif act == "IT Act" and section in it_non_bailable:
        return bail_guidelines["non_bailable"]
    elif act == "MV Act" and section in mv_non_bailable:
        return bail_guidelines["non_bailable"]
    else:
        return bail_guidelines["bailable"]

def get_precedents_for_section(section, act="IPC"):
    """
    Get legal precedents for a specific section.
    """
    relevant_precedents = []
    
    for precedent in legal_precedents:
        # Check if the precedent is relevant to the given section and act
        if precedent["act"] == act and section in precedent["section"]:
            relevant_precedents.append(precedent)
    
    return relevant_precedents

def get_jurisdiction_info():
    """
    Get information about jurisdiction types in the Indian legal system.
    """
    return jurisdiction_types

def search_legal_data(query):
    """
    Search for relevant legal information based on the query.
    """
    results = {
        "IPC": [],
        "CrPC": [],
        "CPC": [],
        "Evidence Act": [],
        "IT Act": [],
        "MV Act": [],
        "Precedents": []
    }
    
    query = query.lower()
    
    # Search in IPC sections
    for section, title in ipc_sections.items():
        if query in title.lower() or query in section.lower():
            results["IPC"].append({
                "section": section,
                "title": title
            })
    
    # Search in CrPC sections
    for section, title in crpc_sections.items():
        if query in title.lower() or query in section.lower():
            results["CrPC"].append({
                "section": section,
                "title": title
            })
    
    # Search in CPC sections
    for section, title in cpc_sections.items():
        if query in title.lower() or query in section.lower():
            results["CPC"].append({
                "section": section,
                "title": title
            })
    
    # Search in Evidence Act sections
    for section, title in evidence_act_sections.items():
        if query in title.lower() or query in section.lower():
            results["Evidence Act"].append({
                "section": section,
                "title": title
            })
    
    # Search in IT Act sections
    for section, title in it_act_sections.items():
        if query in title.lower() or query in section.lower():
            results["IT Act"].append({
                "section": section,
                "title": title
            })
    
    # Search in MV Act sections
    for section, title in mv_act_sections.items():
        if query in title.lower() or query in section.lower():
            results["MV Act"].append({
                "section": section,
                "title": title
            })
    
    # Search in precedents
    for precedent in legal_precedents:
        if (query in precedent["case_name"].lower() or 
            query in precedent["summary"].lower() or 
            any(query in point.lower() for point in precedent["key_points"])):
            results["Precedents"].append(precedent)
    
    return results
