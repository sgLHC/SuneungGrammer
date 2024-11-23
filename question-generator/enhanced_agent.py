from langchain.agents import create_react_agent, AgentExecutor, Tool
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

class QuestionGeneratorTools:
    """문제 생성 및 분석을 위한 도구 모음"""
    
    @staticmethod
    def analyze_grammar(text):
        """문법 구조 분석"""
        return f"문법 분석 결과: {text}의 주요 문법 구조 식별"
    
    @staticmethod
    def analyze_question_type(text):
        """문제 유형 분석"""
        return f"유형 분석 결과: {text}의 문제 유형 분류"
    
    @staticmethod
    def generate_similar_question(analysis):
        """유사 문제 생성"""
        return f"생성된 문제: {analysis}를 바탕으로 한 새로운 문제"
    
    @staticmethod
    def validate_question(question):
        """문제 검증"""
        return f"검증 결과: {question}의 적절성 평가"

class QuestionGeneratorPipeline:
    def __init__(self, llm):
        self.llm = llm
        self.tools = self._create_tools()
        self.agent = self._create_agent()
        self.executor = AgentExecutor(agent=self.agent, tools=self.tools, verbose=True)
    
    def _create_tools(self):
        """ReAct 에이전트용 도구 생성"""
        return [
            Tool(
                name="analyze_grammar",
                func=QuestionGeneratorTools.analyze_grammar,
                description="문제의 문법 구조를 분석합니다"
            ),
            Tool(
                name="analyze_question_type",
                func=QuestionGeneratorTools.analyze_question_type,
                description="문제의 유형을 분석합니다"
            ),
            Tool(
                name="generate_similar_question",
                func=QuestionGeneratorTools.generate_similar_question,
                description="분석을 바탕으로 유사한 새로운 문제를 생성합니다"
            ),
            Tool(
                name="validate_question",
                func=QuestionGeneratorTools.validate_question,
                description="생성된 문제의 적절성을 검증합니다"
            )
        ]
    
    def _create_agent(self):
        """ReAct 에이전트 생성"""
        template = """수능 영어 문제 생성 프로세스를 수행합니다.

주어진 문제: {input}

당신의 목표:
1. 주어진 문제의 문법적 특징과 유형을 분석
2. 분석을 바탕으로 유사한 새로운 문제 생성
3. 생성된 문제의 적절성 검증

사용 가능한 도구:
{tools}

도구 이름: {tool_names}

{agent_scratchpad}
"""
        prompt = PromptTemplate(
            input_variables=["input", "agent_scratchpad", "tools", "tool_names"],
            template=template
        )
        
        return create_react_agent(self.llm, self.tools, prompt)
    
    def generate_question(self, input_question):
        """문제 생성 프로세스 실행"""
        return self.executor.invoke({"input": input_question})

def main():
    # GPT-4를 LLM으로 초기화
    llm = ChatOpenAI(model="gpt-4", temperature=0.7, openai_api_key=OPENAI_API_KEY)
    
    # 파이프라인 생성
    pipeline = QuestionGeneratorPipeline(llm)
    
    # 예시 문제
    example_question = """
    다음 글의 밑줄 친 부분 중, 어법상 틀린 것은?
    
    The environmental impact of plastic waste ① has become a global concern. 
    Millions of tons of plastic ② are dumped into our oceans every year, 
    ③ threatening marine life and ecosystem. Scientists ④ have been working 
    on solutions, but the problem ⑤ continues to grow.
    """
    
    # 문제 생성 실행
    result = pipeline.generate_question(example_question)
    print(result)

if __name__ == "__main__":
    main()