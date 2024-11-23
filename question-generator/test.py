from langchain.agents import AgentExecutor, Tool, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain.memory import ConversationBufferMemory
from typing import List

from dotenv import load_dotenv
import os

# .env 파일에서 환경 변수 로드
load_dotenv()

# OpenAI API 키 가져오기
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class QuestionAnalysisAgent:
    def __init__(self, llm):
        self.llm = llm
        
        # 도구 정의
        @tool
        def analyze_grammar(question: str) -> str:
            """문제의 문법적 구조를 분석합니다."""
            prompt = PromptTemplate(
                input_variables=["question"],
                template="다음 영어 문제의 문법적 구조를 분석해주세요:\n{question}"
            )
            chain = LLMChain(llm=self.llm, prompt=prompt)
            return chain.run(question=question)

        @tool
        def identify_question_type(question: str) -> str:
            """문제의 유형을 파악합니다."""
            prompt = PromptTemplate(
                input_variables=["question"],
                template="다음 영어 문제가 어떤 유형인지 파악해주세요 (빈칸 채우기, 어법, 독해 등):\n{question}"
            )
            chain = LLMChain(llm=self.llm, prompt=prompt)
            return chain.run(question=question)

        self.tools = [analyze_grammar, identify_question_type]

        # ReAct 프롬프트 템플릿
        prompt = ChatPromptTemplate.from_template("""TOOLS:

------

You have access to the following tools:

{tools}

To use a tool, please use the following format:

```

Thought: Do I need to use a tool? [Yes/No]

Action: the action to take, should be one of [{tool_names}]

Action Input: the input to the action

Observation: the result of the action

```

When you have a response to say to the Human, or if you do not need to use a tool, you MUST use the format:

```

Thought: Do I need to use a tool? [Yes/No]

Final Answer: [your response here]

```

Begin!

New input: {input}

{agent_scratchpad}
        """)

        # ReAct 에이전트 생성
        self.agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            max_iterations=3,
            handle_parsing_errors="Check your output and make sure it conforms! Only output the Final Answer."
        )

    def analyze(self, question: str) -> str:
        return self.agent_executor.invoke({"input": question})

# 사용 예시는 그대로 유지
llm = ChatOpenAI(model="gpt-4", temperature=0.7)
question_analysis_agent = QuestionAnalysisAgent(llm)
example_question = """
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
result = question_analysis_agent.analyze(example_question)
print(result['output'])