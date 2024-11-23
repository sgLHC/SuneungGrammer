from langchain.agents import AgentExecutor, Tool, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from langchain.tools import tool
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
                template="다음 영어 문제의 문법적 구조를 분석해주세요:\n{question}",
            )
            chain = LLMChain(llm=self.llm, prompt=prompt)
            return chain.run(question=question)

        @tool
        def identify_question_type(question: str) -> str:
            """문제의 유형을 파악합니다."""
            prompt = PromptTemplate(
                input_variables=["question"],
                template="다음 영어 문제가 어떤 유형인지 파악해주세요 (빈칸 채우기, 어법, 독해 등):\n{question}",
            )
            chain = LLMChain(llm=self.llm, prompt=prompt)
            return chain.run(question=question)

        @tool
        def analyze_topic(question: str) -> str:
            """지문의 주제와 핵심 내용을 분석합니다."""
            prompt = PromptTemplate(
                input_variables=["question"],
                template="다음 영어 지문의 주제와 핵심 내용을 간단히 분석해주세요:\n{question}",
            )
            chain = LLMChain(llm=self.llm, prompt=prompt)
            return chain.run(question=question)

        self.tools = [analyze_grammar, identify_question_type, analyze_topic]

        # ReAct 프롬프트 템플릿
        prompt = ChatPromptTemplate.from_template(
            """TOOLS:

------

You have access to the following tools:

{tools}

To use a tool, please use the following format:

```

Thought: Do I need to use a tool? Yes

Action: the action to take, should be one of [{tool_names}]

Action Input: the input to the action

Observation: the result of the action

```

When you have a response to say to the Human, or if you do not need to use a tool, you MUST use the format:

```

Thought: Do I need to use a tool? No

Final Answer: [your response here]

```

Begin!

New input: {input}

{agent_scratchpad}
        """
        )

        # ReAct 에이전트 생성
        self.agent = create_react_agent(llm=self.llm, tools=self.tools, prompt=prompt)

        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            max_iterations=3,
            handle_parsing_errors="Check your output and make sure it conforms! Only output the Final Answer.",
        )

    def analyze(self, question: str) -> dict:
        """
        문제를 분석하고 결과를 JSON 형태로 반환합니다.

        Returns:
            dict: {
                "question_type": str,
                "grammar_analysis": str,
                "topic_analysis": str,
                "raw_analysis": dict
            }
        """
        # 기존 에이전트 실행
        raw_result = self.agent_executor.invoke({"input": question})

        # 개별 분석 실행
        grammar_analysis = self.tools[0].run(question)
        question_type = self.tools[1].run(question)
        topic_analysis = self.tools[2].run(question)

        # 구조화된 결과 반환
        return {
            "question_type": question_type.strip(),
            "grammar_analysis": grammar_analysis.strip(),
            "topic_analysis": topic_analysis.strip(),
            "raw_analysis": raw_result,
        }


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
print(result)
