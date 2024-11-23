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
            """문의 유형을 파악합니다."""
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

        @tool
        def analyze_difficulty(question: str) -> str:
            """문제의 난이도를 분석합니다."""
            prompt = PromptTemplate(
                input_variables=["question"],
                template="""다음 영어 문제의 난이도를 분석해주세요 (수능, 고1, 고2, 고3 등의 수준으로 판단):
                문제: {question}
                
                난이도를 판단한 근거와 함께 제시해주세요.""",
            )
            chain = LLMChain(llm=self.llm, prompt=prompt)
            return chain.run(question=question)

        self.tools = [
            analyze_grammar,
            identify_question_type,
            analyze_topic,
            analyze_difficulty,
        ]

        # ReAct 프롬프트 템플릿 수정
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You must use ALL of the following tools in sequence to analyze the given English question:

{tools}

Follow these steps:
1. First, analyze the grammar using analyze_grammar
2. Then, identify the question type using identify_question_type
3. Next, analyze the topic using analyze_topic
4. Finally, analyze the difficulty using analyze_difficulty

Use this format for each tool:

```
Thought: I will now use [tool name] to analyze the question
Action: [tool name] (one of [{tool_names}])
Action Input: [question]
Observation: [tool result]
```

After using all tools, summarize the findings:

```
Thought: I have completed all analyses
Final Answer: Here is the complete analysis:
Grammar: [grammar analysis]
Question Type: [question type]
Topic: [topic analysis]
Difficulty: [difficulty analysis]
```""",
                ),
                ("user", "{input}"),
                ("assistant", "{agent_scratchpad}"),
            ]
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
                "difficulty_level": str,
                "raw_analysis": dict
            }
        """
        # 기존 에이전트 실행
        raw_result = self.agent_executor.invoke({"input": question})

        # 개별 분석 실행
        grammar_analysis = self.tools[0].run(question)
        question_type = self.tools[1].run(question)
        topic_analysis = self.tools[2].run(question)
        difficulty_level = self.tools[3].run(question)

        # 구조화된 결과 반환
        return {
            "question_type": question_type.strip(),
            "grammar_analysis": grammar_analysis.strip(),
            "topic_analysis": topic_analysis.strip(),
            "difficulty_level": difficulty_level.strip(),
            "raw_analysis": raw_result,
        }


class QuestionGeneratorAgent:
    def __init__(self, llm):
        self.llm = llm

        # 도구 정의
        @tool
        def generate_grammar_question(analysis: dict) -> str:
            """문법 분석을 바탕으로 새로운 문제를 생성합니다.
            Args:
                analysis (dict): 문법 분석 결과가 담긴 딕셔너리
                    - grammar_analysis: 문법 분석 내용
                    - question_type: 문제 유형
            """
            if isinstance(analysis, str):
                try:
                    import ast

                    analysis = ast.literal_eval(analysis)
                except:
                    analysis = {
                        "grammar_analysis": analysis,
                        "question_type": "grammar",
                    }

            prompt = PromptTemplate(
                input_variables=["grammar_analysis", "question_type"],
                template="""Based on the following grammar analysis and question type, generate a new English question:
                Grammar Analysis: {grammar_analysis}
                Question Type: {question_type}
                
                Please create a new English question that:
                1. Follows the same grammatical structure and difficulty level
                2. Matches the specified question type exactly
                3. Uses natural, academic English appropriate for high school students
                4. Includes clear instructions in English
                
                Generate the complete question in English, including any necessary context and answer choices.""",
            )
            chain = prompt | self.llm

            result = chain.invoke(
                {
                    "grammar_analysis": analysis.get("grammar_analysis", ""),
                    "question_type": analysis.get("question_type", ""),
                }
            )

            return result.content if hasattr(result, "content") else str(result)

        @tool
        def generate_topic_question(analysis: dict) -> str:
            """주제 분석을 바탕으로 새로운 지문과 문제를 생성합니다.
            Args:
                analysis (dict): 주제 분석 결과가 담긴 딕셔너리
                    - topic_analysis: 주제 분석 내용
                    - question_type: 문제 유형
            """
            if isinstance(analysis, str):
                try:
                    import ast

                    analysis = ast.literal_eval(analysis)
                except:
                    analysis = {"topic_analysis": analysis}

            prompt = PromptTemplate(
                input_variables=["topic_analysis", "question_type"],
                template="""Based on the following topic analysis and question type, generate a new English passage and question:
                Topic Analysis: {topic_analysis}
                Question Type: {question_type}
                
                Please create:
                1. A new English passage that:
                   - Covers a similar topic and main ideas
                   - Uses appropriate academic language
                   - Has similar length and complexity
                
                2. A question that:
                   - Matches the specified question type exactly
                   - Tests understanding of similar concepts
                   - Includes clear instructions and answer choices in English
                
                Generate both the passage and question in English.""",
            )
            chain = prompt | self.llm

            result = chain.invoke(
                {
                    "topic_analysis": analysis.get("topic_analysis", ""),
                    "question_type": analysis.get("question_type", ""),
                }
            )

            return result.content if hasattr(result, "content") else str(result)

        @tool
        def adapt_difficulty(question: str, target_level: str) -> str:
            """생성된 문제의 난이도를 조정합니다."""
            prompt = PromptTemplate(
                input_variables=["question", "target_level"],
                template="""다음 문제의 난이도를 {target_level} 수준으로 조정해주세요:
                문제: {question}
                
                난이도를 조정한 새로운 버전의 문제를 제시해주세요.""",
            )
            chain = LLMChain(llm=self.llm, prompt=prompt)
            return chain.run(question=question, target_level=target_level)

        self.tools = [
            generate_grammar_question,
            generate_topic_question,
            adapt_difficulty,
        ]

        # ReAct 프롬프트 템플릿도 수정
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are an AI assistant that helps generate English questions.
            You have access to the following tools:
            
            {tools}
            
            When analyzing questions, first use analyze_grammar, then identify_question_type, and finally analyze_topic.
            When generating questions, use the appropriate tool based on the question type.
            
            Available tools: {tool_names}""",
                ),
                ("user", "{input}"),
                ("assistant", "{agent_scratchpad}"),
            ]
        )

        # ReAct 에이전트 생성
        self.agent = create_react_agent(llm=self.llm, tools=self.tools, prompt=prompt)

        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            max_iterations=3,
            handle_parsing_errors=True,
        )

    def generate(self, analysis: dict, target_level: str = "수능") -> dict:
        """분석된 결과를 바탕으로 새로운 문제를 생성합니다."""
        # 기본 문제 생성
        if "grammar" in analysis.get("question_type", "").lower():
            base_question = self.tools[0].run(analysis)
        else:
            # topic_analysis가 있는지 확인하고 필요한 형식으로 변환
            topic_data = {
                "analysis": {
                    "topic_analysis": analysis.get(
                        "topic_analysis", analysis.get("analysis", "")
                    ),
                    "question_type": analysis.get("question_type", ""),
                }
            }
            base_question = self.tools[1].run(topic_data)

        # 난이도 조정 (입력 형식 수정)
        difficulty_input = {"question": base_question, "target_level": target_level}
        final_question = self.tools[2].run(difficulty_input)

        return {
            "generated_question": final_question.strip(),
            "question_type": analysis.get("question_type", ""),
            "difficulty_level": target_level,
        }


# ... (기존 클래스들은 그대로 유지) ...


def process_question(question_text: str) -> dict:
    """
    입력받은 문제를 분석하고 새로운 문제를 생성하는 전체 프로세스를 실행합니다.

    Args:
        question_text: 분석할 영어 문제 텍스트

    Returns:
        dict: {
            "original_analysis": dict,
            "generated_question": dict
        }
    """
    # LLM 초기화
    llm = ChatOpenAI(model="gpt-4", temperature=0.7)

    # 분석 에이전트 생성 및 분석 수행
    analysis_agent = QuestionAnalysisAgent(llm)
    analysis_result = analysis_agent.analyze(question_text)

    # 생성 에이전트 생성 및 새로운 문제 생성
    generator_agent = QuestionGeneratorAgent(llm)
    generated_question = generator_agent.generate(
        analysis_result, target_level=analysis_result["difficulty_level"]
    )

    return {
        "original_analysis": analysis_result,
        "generated_question": generated_question,
    }


if __name__ == "__main__":
    # 사용자로터 문제 입력 받기
    print("\n=== 영어 문제 입력 ===")
    print(
        "분석할 영어 문제를 입력해주세요 (입력 완료 후 빈 줄에서 Ctrl+D 또는 Ctrl+Z):"
    )

    # 여러 줄 입력 받기
    lines = []
    try:
        while True:
            line = input()
            lines.append(line)
    except (EOFError, KeyboardInterrupt):
        question_text = "\n".join(lines)

    # 입력받은 문제 처
    print("\n=== 처리 시작 ===")
    result = process_question(question_text)

    # 결과 출력
    print("\n=== 분석 결과 ===")
    print("문제 유형:", result["original_analysis"]["question_type"])
    print("문법 분석:", result["original_analysis"]["grammar_analysis"])
    print("주제 분석:", result["original_analysis"]["topic_analysis"])
    print("난이도:", result["original_analysis"]["difficulty_level"])

    print("\n=== 생성된 새로운 문제 ===")
    print(result["generated_question"]["generated_question"])
    print("\n난이도:", result["generated_question"]["difficulty_level"])
    print("문제 유형:", result["generated_question"]["question_type"])


# # 사용 예시는 그대로 유지
# llm = ChatOpenAI(model="gpt-4", temperature=0.7)
# question_analysis_agent = QuestionAnalysisAgent(llm)
# example_question = """
#         Pay attention to the cues you’re using to judge
#         what  you  have  learned.  (A)[What  /  Whether]
#         something feels familiar or fluent is not always a
#         reliable indicator of learning. Neither is your level
#         of ease in retrieving a fact or a phrase on a quiz
#         shortly  after  encountering  it  in  a  lecture  or  text.
#         Far  better  is  to  create  a  mental  model  of  the
#         material that integrates the various ideas across a
#         text,  connects  them  to  what  you  already  know,
#         and (B)[enable  /  enables] you to draw inferences.
#         How ably you can explain a text is an excellent cue
#         for judging comprehension, (C)[because / because of]
#         you  must  recall  the  salient  points  from  memory,
#         put  them  into  your  own  words,  and  explain  why
#         they  are  significant  how  they  relate  to  the —
#         larger subject.
#         """
# result = question_analysis_agent.analyze(example_question)
# print(result)
