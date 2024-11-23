import dotenv
import os
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent, create_react_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.memory import ConversationBufferMemory



dotenv.load_dotenv()
upstage_api_key = os.getenv("UPSTAGE_API_KEY")
if not upstage_api_key:
    raise ValueError("UPSTAGE_API_KEY not found in .env file.")
os.environ["UPSTAGE_API_KEY"] = upstage_api_key

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in .env file.")
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# 메모리 초기화
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

def invoke_llm(llm, query):
    """Utility function to invoke LLM and return its output."""
    return llm.invoke(query)

@tool
def analyze_question(llm, original_question):
    """
    1. Analyzes the type of the original question.
    2. Identifies and explains the grammar points used in the original question.
    """
    query = f"Analyze following question as the way the prompt tell me so: {original_question}"
    result = invoke_llm(llm, query)
    return result

@tool
def generate_question(llm, query):
    """
    1. Creates a new question based on the given information about the original question.
    """
    result = invoke_llm(llm, query)
    return result

@tool
def validate_question(llm, query):
    """
    1. Checks whether the generated question follows next criteria:
        - Question type of the original question.
        - Grammar Points of the original question.
    2. Checks whether the context of the question passage is logical.
    """
    result = invoke_llm(llm, query)
    return result

class SpecialistAgent:
    ROLE_DESCRIPTIONS = {
        "analyzer": """
        1. Analyzing the type of question.
        2. Identifying and explaining the grammar points used in the question.
    """,
        "generator": """
        1. Creating a new question based on the given information about the original question.
    """,
        "validator": """
        1. Check whether the generated question follows next criteria:
            - Question type of the original question.
            - Grammar Points of the original question.
        2. Check whether the context of the question passage is logical.
    """
    }
    
    RESPONSE_SCHEMAS = {
    "analyzer": [
        ResponseSchema(name='question_type', description='Either "underlined" OR "box"', type='string'),
        ResponseSchema(name='question_type', description='Either "underlined" OR "box"', type='string'),
        ResponseSchema(name='grammar_points', description='List of DISTINCT grammar points used.', type='list'),
        ResponseSchema(name='grammar_points_count', description='Number of DISTINCT grammar concepts used ("underlined": 5, "box": 3).', type='integer')
    ],
    "generator": [
        ResponseSchema(name='question type', description='Either "underlined" OR "box"', type='string'),
        ResponseSchema(name='grammar_points', description='List of DISTINCT grammar points used.', type='list'),
        ResponseSchema(name='grammar_points_count', description='Number of DISTINCT grammar concepts used ("underlined": 5, "box": 3).', type='integer'),
        ResponseSchema(name='generated_question', description='Newly generated question which is based on the given type and grammar concepts.', type='string')
    ],
    "validator":[
        ResponseSchema(name='validity', description='Validity check for newly generated question. This should result in "valid", or "invalid"', type='string'),
        ResponseSchema(name='errors', description='List of errors if the question is invalid.', type='list'),
        ResponseSchema(name='recommendations', description='Suggestions to improve the invalid question.', type='string')
    ]
}
    
    INPUT_FORMAT = {
        "analyzer":"""
### Input Format:
You will receive the input as a string with the following structure:

Example Input:
"The most useful thing I brought out of my childhood was confidence in reading. Not long ago, I went on a weekend self-exploratory workshop, in the hope of getting a clue about how to live. One of the exercises we were given (A) [was/were] to make a list of the ten most important events of our lives. Number one was: "I was born," and you could put (B) [however/whatever] you liked after that. Without even thinking about it, my hand wrote at number two: "I learned to read." "I was born and learned to read" wouldn't be a sequence that occurs to many people, I imagine. But I knew what I meant to say. Being born was something (C) [done/doing] to me, but my own life began when I first made out the meaning of a sentence."

Use the provided string data to analyze or generate the required output based on your role.
""",
        "generator":"""
### Input Format:
You will receive the input as a JSON format with the following structure:

Example Input:
{
    "original_question": "The most useful thing I brought out of my childhood was confidence in reading. Not long ago, I went on a weekend self-exploratory workshop, in the hope of getting a clue about how to live. One of the exercises we were given (A) [was/were] to make a list of the ten most important events of our lives. Number one was: "I was born," and you could put (B) [however/whatever] you liked after that. Without even thinking about it, my hand wrote at number two: "I learned to read." "I was born and learned to read" wouldn't be a sequence that occurs to many people, I imagine. But I knew what I meant to say. Being born was something (C) [done/doing] to me, but my own life began when I first made out the meaning of a sentence."
    "question_type": "box",
    "grammar_points": '''
    - (A) Subject-verb agreement: In the structure "One of [plural noun]," the singular subject "One" requires a singular verb, so the answer is "was."
    - (B) Understanding compound relative pronouns: "you liked after that" requires "whatever" as the object of the verb "liked."
    - (C) Understanding active and passive voice: "Being born" implies a passive meaning, so the answer should also reflect a passive form, which is "done."
    '''
}
Use the provided JSON data to analyze or generate the required output based on your role.
""",
        "validator": """
You will receive the input as a JSON format with the following structure:

Example Input:
{
    "original_question": "The most useful thing I brought out of my childhood was confidence in reading. Not long ago, I went on a weekend self-exploratory workshop, in the hope of getting a clue about how to live. One of the exercises we were given (A) [was/were] to make a list of the ten most important events of our lives. Number one was: "I was born," and you could put (B) [however/whatever] you liked after that. Without even thinking about it, my hand wrote at number two: "I learned to read." "I was born and learned to read" wouldn't be a sequence that occurs to many people, I imagine. But I knew what I meant to say. Being born was something (C) [done/doing] to me, but my own life began when I first made out the meaning of a sentence."
    "question_type": "box",
    "grammar_points": '''
    - (A) Subject-verb agreement: In the structure "One of [plural noun]," the singular subject "One" requires a singular verb, so the answer is "was."
    - (B) Understanding compound relative pronouns: "you liked after that" requires "whatever" as the object of the verb "liked."
    - (C) Understanding active and passive voice: "Being born" implies a passive meaning, so the answer should also reflect a passive form, which is "done."
    ''',
    "generated_question": A new question text goes here.
}
"""
}
    
    def __init__(self, name, tools, temperature, memory):
        self.name = name
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=temperature
        )
        
        global_template = """
You are an expert in creating English grammar questions for the College Scholastic Ability Test (CSAT) in South Korea.
Your primary role is {role}.
{role} specializes in the following task(s):

{role_description}

Answer the following questions as best you can. You have access to the following tools:

{tools}

## Information
### Grammar Question Types:
- **'box'**: Questions that include multiple-choice items within boxes.
- **'underlined'**: Questions where you correct the underlined parts of the text.

### Example Questions:
```Example Question 1
The most useful thing I brought out of my childhood was confidence in reading. Not long ago, I went on a weekend self-exploratory workshop, in the hope of getting a clue about how to live. One of the exercises we were given (A) [was/were] to make a list of the ten most important events of our lives. Number one was: "I was born," and you could put (B) [however/whatever] you liked after that. Without even thinking about it, my hand wrote at number two: "I learned to read." "I was born and learned to read" wouldn't be a sequence that occurs to many people, I imagine. But I knew what I meant to say. Being born was something (C) [done/doing] to me, but my own life began when I first made out the meaning of a sentence.

Question Type: 'box'
Answer:
(A) was - (B) whatever - (C) done

Grammar Points:
- (A) Subject-verb agreement: In the structure "One of [plural noun]," the singular subject "One" requires a singular verb, so the answer is "was."
- (B) Understanding compound relative pronouns: "you liked after that" requires "whatever" as the object of the verb "liked."
- (C) Understanding active and passive voice: "Being born" implies a passive meaning, so the answer should also reflect a passive form, which is "done."
```

```Example Question 2
Like most parents, you might have spent money on a toy that your child didn’t play with very much. You might have found your child playing ① much with the box than the toy that came in it. There is one toy that is a guaranteed winner for children ― Blocks. ② Buying a set of table blocks, cube blocks, or cardboard blocks is a very good investment in your child’s play. Blocks help children ③ learn many subjects. Children learn ④ a lot about shapes and sizes. Young children develop math skills by counting, matching, sorting, grouping, and ⑤ adding blocks while they play.

Question Type: 'underlined'
Answer: ① more

Grammar Points:
- (① much → more): In comparative structures, "more" is used to indicate a higher degree of action or quality compared to something else. Here, the correct expression is "playing more with the box than the toy," as "more" is required to complete the comparative structure with "than."
- (② Buying): The gerund "Buying" is correctly used as the subject of the sentence. Gerunds function as nouns and can serve as the subject of a verb, as seen in "Buying a set of blocks is a very good investment."
- (③ learn): The base form "learn" is correctly used after the verb "help." In English, "help" is followed by the bare infinitive (base form) or a to-infinitive. Both are acceptable.
- (④ a lot): The phrase "a lot" is correctly used to describe the extent of learning ("learn a lot about shapes and sizes"). This is grammatically correct and contextually appropriate.
- (⑤ adding): The gerund "adding" is correctly used after the preposition "by" to indicate the means or method ("by counting, matching, sorting, grouping, and adding blocks").
```

Use the following format:
 
{input_format}

IMPORTANT: THE OUTPUT STRUCTURE MUST FOLLOW THE {instruction}. You must always return valid JSON fenced by a markdown code block. Do not return any additional text.

STRICTLY use the following format:
Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question
 
Begin!
 
Question: {input}
Thought:{agent_scratchpad}

IMPORTANT: THE OUTPUT STRUCTURE MUST FOLLOW THE INSTRUCTION: {instruction}
"""
        template_values = {
            "role": name, 
            "role_description": self.get_task(), 
            "instruction": self.get_instruction(),
            "input_format": self.get_input_format()
        }
        prompt = ChatPromptTemplate.from_template(template=global_template).partial(**template_values)
        self.agent = create_react_agent(llm=self.llm, tools=tools, prompt=prompt)
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            name=name,
            tools=tools,
            memory=memory,
            verbose=True,
            max_iterations=5,
            handle_parsing_errors="Check your output and make sure it conforms! Only output the Final Answer."
        )

    def get_task(self):
        return self.ROLE_DESCRIPTIONS.get(self.name)
    
    def get_instruction(self):
        output_parser = StructuredOutputParser(response_schemas=self.RESPONSE_SCHEMAS[self.name])
        return output_parser.get_format_instructions()
    
    def get_input_format(self):
        return self.INPUT_FORMAT.get(self.name)

    def run(self, input):
        result = self.agent_executor.invoke({"input": query})["output"]
        return result


analyzer_agent = SpecialistAgent(name="analyzer", tools=[analyze_question], temperature=0.1, memory=memory)
# generator_agent = create_tool_calling_agent(model, tools=[generate_question], prompt=generator_prompt)
# validator_agent = create_tool_calling_agent(model, tools=[validate_question], prompt=validator_prompt)

# Instruction Schema Formatting
# generator_agent_executor = AgentExecutor(agent=generator_agent, tools=generate_question)
# validator_agent_executor = AgentExecutor(agent=validator_agent, tools=analyze_question)

def initialize_question_generation(query: str, original_question: str):
    analyzer_result = analyzer_agent.run(f"{query}: {original_question}")
    print(analyzer_result)
    return

if __name__ == "__main__":
    query = "다음 대학수학능력시험 영어 영역 어법 문제의 출제 유형과 출제 포인트를 설명해줘. "
    test_question = """
        Pay attention to the cues you’re using to judge 
        what  you  have  learned.  (A)[What  /  Whether] 
        something feels familiar or fluent is not always a 
        reliable indicator of learning. Neither is your level 
        of ease in retrieving a fact or a phrase on a quiz 
        shortly  after  encountering  it  in  a  lecture  or  text. 
        Far  better  is  to  create  a  mental  model  of  the 
        material that integrates the various ideas across a 
        text,  connects  them  to  what  you  already  know, 
        and (B)[enable  /  enables] you to draw inferences. 
        How ably you can explain a text is an excellent cue 
        for judging comprehension, (C)[because / because of] 
        you  must  recall  the  salient  points  from  memory, 
        put  them  into  your  own  words,  and  explain  why 
        they  are  significant  how  they  relate  to  the — 
        larger subject.
        """
    initialize_question_generation(query, test_question)
    # analyzer_agent.run(f"{query}: {test_question}")
