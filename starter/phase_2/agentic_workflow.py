from workflow_agents.base_agents import (
    ActionPlanningAgent,
    EvaluationAgent,
    KnowledgeAugmentedPromptAgent,
    RoutingAgent,
)
import os
from dotenv import load_dotenv

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# load the product spec
with open("Product-Spec-Email-Router.txt", "r") as file:
    product_spec = file.read()

# Instantiate all the agents

# Action Planning Agent
knowledge_action_planning = (
    "Stories are defined from a product spec by identifying a "
    "persona, an action, and a desired outcome for each story. "
    "Each story represents a specific functionality of the product "
    "described in the specification. \n"
    "Features are defined by grouping related user stories. \n"
    "Tasks are defined for each story and represent the engineering "
    "work required to develop the product. \n"
    "A development Plan for a product contains all these components.\n"
    "For a full product development plan, the steps are:\n"
     # I added the 3 explicit steps below, so the planner does not made his own
    "1. Define user stories from the product specification.\n"
    "2. Group the user stories into product features.\n"
    "3. Define detailed engineering tasks for the user stories and features."
)
action_planning_agent = ActionPlanningAgent(openai_api_key, knowledge_action_planning)

# Product Manager - Knowledge Augmented Prompt Agent
persona_product_manager = "You are a Product Manager, you are responsible for defining the user stories for a product."
knowledge_product_manager = (
    "Stories are defined by writing sentences with a persona, an action, and a desired outcome. "
    "The sentences always start with: As a "
    "Write several stories for the product spec below, where the personas are the different users of the product. "
    f"\n\nProduct specification:\n{product_spec}"
)

product_manager_knowledge_agent = KnowledgeAugmentedPromptAgent(openai_api_key,persona_product_manager,knowledge_product_manager)

# Product Manager - Evaluation Agent
persona_product_manager_eval = "You are an evaluation agent that checks the answers of other worker agents"
evaluation_criteria_product_manager = ( "The answer should be stories that follow the following structure: "
    "As a [type of user], I want [an action or feature] so that [benefit/value]."
)

product_manager_evaluation_agent = EvaluationAgent(
    openai_api_key,
    persona_product_manager_eval,
    evaluation_criteria_product_manager,
    product_manager_knowledge_agent,
    max_interactions=10,
)


# Program Manager - Knowledge Augmented Prompt Agent
persona_program_manager = "You are a Program Manager, you are responsible for defining the features for a product."
knowledge_program_manager = (
    "Features of a product are defined by organizing similar user stories into cohesive groups. "
    "Each feature must follow this exact structure:\n"
    "Feature Name: A clear, concise title that identifies the capability\n"
    "Description: A brief explanation of what the feature does and its purpose\n"
    "Key Functionality: The specific capabilities or actions the feature provides\n"
    "User Benefit: How this feature creates value for the user\n\n"
    "Only create product features. Do not create user stories or engineering tasks.\n\n"
    f"Product specification:\n{product_spec}"
)

program_manager_knowledge_agent = KnowledgeAugmentedPromptAgent(
    openai_api_key,
    persona_program_manager,
    knowledge_program_manager,
)

# Program Manager - Evaluation Agent
persona_program_manager_eval = "You are an evaluation agent that checks the answers of other worker agents."

evaluation_criteria_program_manager = (
    "The answer should be product features that follow the following structure: "
    "Feature Name: A clear, concise title that identifies the capability\n"
    "Description: A brief explanation of what the feature does and its purpose\n"
    "Key Functionality: The specific capabilities or actions the feature provides\n"
    "User Benefit: How this feature creates value for the user"
)
program_manager_evaluation_agent = EvaluationAgent(
    openai_api_key,
    persona_program_manager_eval,
    evaluation_criteria_program_manager,
    program_manager_knowledge_agent,
    max_interactions=10,
)


# Development Engineer - Knowledge Augmented Prompt Agent
persona_dev_engineer = "You are a Development Engineer, you are responsible for defining the development tasks for a product."
knowledge_dev_engineer = (
    "Development tasks are defined by identifying what needs to be built to implement each user story. "
    "Each task must follow this exact structure:\n"
    "Task ID: A unique identifier for tracking purposes\n"
    "Task Title: Brief description of the specific development work\n"
    "Related User Story: Reference to the parent user story\n"
    "Description: Detailed explanation of the technical work required\n"
    "Acceptance Criteria: Specific requirements that must be met for completion\n"
    "Estimated Effort: Time or complexity estimation\n"
    "Dependencies: Any tasks that must be completed first\n\n"
    "Only create engineering tasks. Do not create user stories or features.\n\n"
    f"Product specification:\n{product_spec}"
)

development_engineer_knowledge_agent = KnowledgeAugmentedPromptAgent(
    openai_api_key,
    persona_dev_engineer,
    knowledge_dev_engineer,
)

# Development Engineer - Evaluation Agent
persona_dev_engineer_eval = "You are an evaluation agent that checks the answers of other worker agents."

evaluation_criteria_dev_engineer = (
    "The answer should be tasks following this exact structure: "
    "Task ID: A unique identifier for tracking purposes\n"
    "Task Title: Brief description of the specific development work\n"
    "Related User Story: Reference to the parent user story\n"
    "Description: Detailed explanation of the technical work required\n"
    "Acceptance Criteria: Specific requirements that must be met for completion\n"
    "Estimated Effort: Time or complexity estimation\n"
    "Dependencies: Any tasks that must be completed first"
)
development_engineer_evaluation_agent = EvaluationAgent(
    openai_api_key,
    persona_dev_engineer_eval,
    evaluation_criteria_dev_engineer,
    development_engineer_knowledge_agent,
    max_interactions=10,
)

# Module-level list so the support functions below can read previous step
# results without the workflow loop pre-enriching the routing input.
completed_steps = []


def _context_from_completed_steps():
    if not completed_steps:
        return ""
    blocks = []
    for step in completed_steps:
        blocks.append(f"Step: {step['step']}\nResult:\n{step['result']}")
    return "\n\n".join(blocks)


def product_manager_support_function(query):
    response = product_manager_knowledge_agent.respond(query)
    evaluation = product_manager_evaluation_agent.evaluate(query, initial_response=response)
    return evaluation["final_response"]

def program_manager_support_function(query):
    # Append previous step outputs (the user stories from Step 1) so the
    # Program Manager groups real stories instead of inventing new ones.
    context = _context_from_completed_steps()
    enriched_query = (
        f"{query}\n\n"
        "Use the following prior workflow outputs as input:\n"
        f"{context}"
    ) if context else query
    response = program_manager_knowledge_agent.respond(enriched_query)
    evaluation = program_manager_evaluation_agent.evaluate(enriched_query, initial_response=response)
    return evaluation["final_response"]

def development_engineer_support_function(query):
    # Append previous step outputs (stories + features) so the engineering
    # tasks reference the real user stories and features from Step 1 and Step 2.
    context = _context_from_completed_steps()
    enriched_query = (
        f"{query}\n\n"
        "Use the following prior workflow outputs as input:\n"
        f"{context}"
    ) if context else query
    response = development_engineer_knowledge_agent.respond(enriched_query)
    evaluation = development_engineer_evaluation_agent.evaluate(enriched_query, initial_response=response)
    return evaluation["final_response"]


# Routing Agent
routing_agent = RoutingAgent(openai_api_key)

# Without 'Never ...' clauses the router sent the user-story step to the Program Manager
# because both descriptions mentioned 'user stories'. Negative clauses fix that.
routing_agent.agents = [
    {
        "name": "Product Manager",
        "description": (
            "Defines user stories and product personas. "
            "Writes 'As a [user], I want [feature] so that [benefit]' sentences. "
            "Only creates user stories. "
            "Never groups stories. Never creates product features. Never creates engineering tasks."
        ),
        "func": product_manager_support_function,
    },
    {
        "name": "Program Manager",
        "description": (
            "Defines product features by grouping already-existing user stories into cohesive feature sets. "
            "Outputs Feature Name, Description, Key Functionality, User Benefit for each feature. "
            "Only creates product features. "
            "Never writes user stories. Never writes engineering tasks."
        ),
        "func": program_manager_support_function,
    },
    {
        "name": "Development Engineer",
        "description": (
            "Defines detailed engineering tasks for implementing features and user stories. "
            "Outputs Task ID, Task Title, Related User Story, Description, Acceptance Criteria, "
            "Estimated Effort, and Dependencies for each task. "
            "Only creates engineering tasks. "
            "Never writes user stories. Never writes product features."
        ),
        "func": development_engineer_support_function,
    },
]


# Run the workflow

print("\n*** Workflow execution started ***\n")
# Workflow Prompt

workflow_prompt = (
    "Create a full product development plan for the Email Router product. "
    "Include user stories, group them into product features, and create detailed engineering tasks."
)

print(f"Task to complete in this workflow, workflow prompt = {workflow_prompt}")

print("\nDefining workflow steps from the workflow prompt")

workflow_steps = action_planning_agent.extract_steps_from_prompt(workflow_prompt)

print("\nWorkflow steps extracted:")
for index, step in enumerate(workflow_steps, start=1):
    print(f"  {index}. {step}")

# Route each step on its raw text (no pre-enrichment) so the previous step's
# content doesn't bias the embedding. The support functions read the prior
# results from completed_steps themselves.
for index, step in enumerate(workflow_steps, start=1):
    print(f"\n--- Processing workflow step {index}: {step} ---")
    result = routing_agent.route(step)
    completed_steps.append({"step": step, "result": result})
    print(f"\nResult for step {index}:\n{result}")

print("\nFinal workflow output\n")
if completed_steps:
    print(completed_steps[-1]["result"])
else:
    print("No steps were executed.")

# Final consolidated report: all step results in one structured block.
print("\n" + "=" * 50)
print("EMAIL ROUTER PROJECT DEVELOPMENT PLAN")
print("=" * 50)

for index, step in enumerate(completed_steps, start=1):
    print(f"\n--- Step {index}: {step['step']} ---")
    print(step["result"])

print("\n" + "=" * 50)
print("END OF PROJECT PLAN")
print("=" * 50)