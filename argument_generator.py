import nltk
from nltk.tokenize import word_tokenize
import re
import random
from legal_data import (
    ipc_sections, it_act_sections, mv_act_sections, 
    legal_precedents, get_offense_details, get_precedents_for_section
)

# Ensure NLTK data is downloaded
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt')
    nltk.download('punkt_tab')

class ArgumentGenerator:
    """
    A class that generates legal arguments for and against cases 
    based on specific legal sections and case descriptions.
    """
    
    def __init__(self):
        """Initialize the ArgumentGenerator with legal codes data."""
        self.ipc_sections = ipc_sections
        self.it_act_sections = it_act_sections
        self.mv_act_sections = mv_act_sections
        self.legal_precedents = legal_precedents
        
        # Common argument templates
        self.argument_templates = self._load_argument_templates()
    
    def _load_argument_templates(self):
        """Load argument templates for different types of cases."""
        return {
            # Templates for arguments in favor of defense
            "defense_favor": [
                "The prosecution has failed to establish {element} beyond reasonable doubt.",
                "The evidence regarding {element} is circumstantial and insufficient.",
                "The witness testimony on {element} is inconsistent and unreliable.",
                "The investigation process was flawed, particularly regarding {element}.",
                "The alleged {element} does not satisfy the legal threshold required.",
                "According to the precedent set in {precedent}, {argument}.",
                "The prosecution's case lacks {element} which is essential to establish guilt.",
                "The constitutional right to {right} has been violated in this case.",
                "The evidence was collected in violation of the procedure established by law.",
                "The prosecution has not proven the mens rea (guilty mind) required for this offense."
            ],
            
            # Templates for arguments against defense (prosecution)
            "prosecution_favor": [
                "The evidence clearly establishes {element} beyond reasonable doubt.",
                "The witness testimony consistently confirms {element}.",
                "The documentary evidence proves {element} conclusively.",
                "The investigation was conducted following all procedural requirements.",
                "The accused's conduct satisfies all elements of the offense under section {section}.",
                "The precedent in {precedent} supports the prosecution's case that {argument}.",
                "The forensic evidence confirms {element} linking the accused to the crime.",
                "The accused had both motive and opportunity to commit the offense.",
                "The defense's alternative explanation fails to account for {element}.",
                "The accused's actions demonstrate clear intent (mens rea) required for this offense."
            ],
            
            # Templates for bail arguments
            "bail_favor": [
                "The accused has deep roots in the community and is not a flight risk.",
                "The offense is bailable and there is no reason to deny bail.",
                "The accused has no prior criminal record indicating good character.",
                "The case against the accused is prima facie weak.",
                "The accused requires special medical attention that cannot be provided in custody.",
                "The accused is the primary caregiver for dependents.",
                "The accused has consistently appeared for all prior court proceedings.",
                "As established in {precedent}, bail should be granted in such circumstances.",
                "The investigation is complete and there is no risk of evidence tampering.",
                "Extended pre-trial detention would amount to punishment before conviction."
            ],
            
            "bail_against": [
                "The offense is serious and non-bailable under section {section}.",
                "The accused poses a flight risk due to the severity of punishment.",
                "There is reasonable apprehension of witness tampering or evidence interference.",
                "The accused has a history of non-appearance in court proceedings.",
                "The investigation is ongoing and custody is necessary for proper investigation.",
                "The accused may influence or threaten witnesses if released.",
                "Public sentiment is strong against the offense and may lead to law and order issues.",
                "As established in {precedent}, bail should be denied in such circumstances.",
                "There is prima facie strong evidence against the accused.",
                "The accused has previously violated bail conditions in other cases."
            ]
        }
    
    def _get_case_elements(self, section, act, case_description):
        """Extract key elements relevant to the case based on section and description."""
        elements = []
        
        # Common legal elements
        common_elements = [
            "intent", "motive", "opportunity", "evidence", "witness testimony",
            "documentary proof", "alibi", "criminal history", "chain of events"
        ]
        
        # Extract specific elements from case description
        tokens = word_tokenize(case_description.lower())
        
        # Look for certain patterns in the description
        if "threat" in tokens or "intimidate" in tokens or "fear" in tokens:
            elements.append("threat or intimidation")
        
        if "weapon" in tokens or "gun" in tokens or "knife" in tokens:
            elements.append("use of dangerous weapon")
        
        if "plan" in tokens or "premeditate" in tokens or "conspire" in tokens:
            elements.append("premeditation")
        
        if "confess" in tokens or "admit" in tokens:
            elements.append("confession or admission")
        
        if "injury" in tokens or "harm" in tokens or "damage" in tokens:
            elements.append("extent of injury or damage")
        
        # Add section-specific elements
        if act == "IPC":
            if section == "302":  # Murder
                elements.extend(["intention to cause death", "premeditation", "motive for murder"])
            elif section == "376":  # Rape
                elements.extend(["consent", "force or coercion", "identification of accused"])
            elif section == "420":  # Cheating
                elements.extend(["fraudulent intent", "deception", "wrongful gain"])
        
        elif act == "IT Act":
            if section == "66":  # Computer-related offense
                elements.extend(["unauthorized access", "damage to computer system", "data theft"])
            elif section == "67":  # Obscene content
                elements.extend(["obscene nature of content", "publication intent", "public access"])
        
        elif act == "MV Act":
            if section == "184":  # Dangerous driving
                elements.extend(["dangerous speed", "reckless behavior", "traffic conditions"])
            elif section == "185":  # Drunk driving
                elements.extend(["blood alcohol level", "sobriety test", "driving impairment"])
        
        # If no specific elements found, use common ones
        if not elements:
            elements = common_elements
        
        return elements
    
    def _get_constitutional_rights(self):
        """Get list of relevant constitutional rights that might apply."""
        return [
            "fair trial", "legal representation", "silence", "protection against self-incrimination",
            "equality before law", "presumption of innocence", "speedy trial", "personal liberty",
            "bail", "due process"
        ]
    
    def _format_argument(self, template, replacements):
        """Format an argument template with given replacements."""
        try:
            return template.format(**replacements)
        except KeyError:
            # Fallback if formatting fails
            return template
    
    def generate_arguments(self, section, act, case_description, favor_defense=True, num_arguments=5):
        """
        Generate legal arguments based on section, act, and case description.
        
        Args:
            section (str): Legal section number (e.g., "302")
            act (str): Act name (e.g., "IPC", "IT Act", "MV Act")
            case_description (str): Description of the case
            favor_defense (bool): If True, generate arguments favoring defense, otherwise prosecution
            num_arguments (int): Number of arguments to generate
            
        Returns:
            dict: Dictionary containing generated arguments and supporting information
        """
        # Validate inputs
        if not section or not act or not case_description:
            return {"error": "Missing required input parameters"}
        
        # Get offense details
        offense_details = get_offense_details(section, act)
        if not offense_details:
            return {"error": f"Section {section} not found in {act}"}
        
        # Get relevant precedents
        precedents = get_precedents_for_section(section, act)
        
        # Get case elements
        elements = self._get_case_elements(section, act, case_description)
        
        # Get constitutional rights
        rights = self._get_constitutional_rights()
        
        # Select appropriate templates
        if favor_defense:
            primary_templates = self.argument_templates["defense_favor"]
            secondary_templates = self.argument_templates["bail_favor"]
        else:
            primary_templates = self.argument_templates["prosecution_favor"]
            secondary_templates = self.argument_templates["bail_against"]
        
        # Combine and shuffle templates
        all_templates = primary_templates + secondary_templates
        random.shuffle(all_templates)
        
        # Generate arguments
        arguments = []
        for i in range(min(num_arguments, len(all_templates))):
            template = all_templates[i]
            
            # Prepare replacements
            replacements = {
                "element": random.choice(elements),
                "right": random.choice(rights),
                "section": section
            }
            
            # Add precedent if available
            if precedents and "precedent" in template:
                precedent = random.choice(precedents)
                replacements["precedent"] = precedent["case_name"]
                replacements["argument"] = random.choice(precedent["key_points"])
            
            # Format the argument
            argument = self._format_argument(template, replacements)
            arguments.append(argument)
        
        return {
            "arguments": arguments,
            "offense_details": offense_details,
            "supporting_precedents": precedents if precedents else [],
            "position": "defense" if favor_defense else "prosecution"
        }
    
    def generate_bail_arguments(self, section, act, case_description, favor_bail=True, num_arguments=5):
        """
        Generate bail-specific arguments based on section, act, and case description.
        
        Args:
            section (str): Legal section number
            act (str): Act name
            case_description (str): Description of the case
            favor_bail (bool): If True, generate arguments favoring bail, otherwise against
            num_arguments (int): Number of arguments to generate
            
        Returns:
            dict: Dictionary containing generated bail arguments and supporting information
        """
        # Validate inputs
        if not section or not act or not case_description:
            return {"error": "Missing required input parameters"}
        
        # Get offense details
        offense_details = get_offense_details(section, act)
        if not offense_details:
            return {"error": f"Section {section} not found in {act}"}
        
        # Get bail information
        bail_info = offense_details.get("bail_info", {})
        
        # Get relevant precedents
        precedents = get_precedents_for_section(section, act)
        
        # Select appropriate templates
        templates = self.argument_templates["bail_favor"] if favor_bail else self.argument_templates["bail_against"]
        
        # Generate arguments
        arguments = []
        for i in range(min(num_arguments, len(templates))):
            template = templates[i]
            
            # Prepare replacements
            replacements = {
                "section": section
            }
            
            # Add precedent if available
            if precedents and "precedent" in template:
                precedent = random.choice(precedents)
                replacements["precedent"] = precedent["case_name"]
            
            # Format the argument
            argument = self._format_argument(template, replacements)
            arguments.append(argument)
        
        return {
            "bail_arguments": arguments,
            "offense_details": offense_details,
            "is_bailable": "bailable" in str(bail_info).lower(),
            "supporting_precedents": precedents if precedents else [],
            "position": "favor" if favor_bail else "against"
        }

# Initialize the argument generator
argument_generator = ArgumentGenerator()
