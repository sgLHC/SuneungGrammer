from langchain.agents import AgentExecutor, Tool
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

# .env 파일에서 환경 변수 로드
load_dotenv()

# OpenAI API 키 가져오기
api_key = os.getenv("OPENAI_API_KEY")


# 문제 분석 에이전트
class QuestionAnalysisAgent:
    def __init__(self, llm):
        self.llm = llm
        self.prompt = PromptTemplate(
            input_variables=["example_question"],
            template=(
                "아래는 대한민국 수능 영어 문제의 예입니다:\n"
                "{example_question}\n"
                "이 문제의 핵심 문법 구조와 유형을 분석해주세요."
            ),
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)

    def analyze(self, example_question):
        return self.chain.run(example_question=example_question)


# 문제 생성 에이전트
class QuestionGenerationAgent:
    def __init__(self, llm):
        self.llm = llm
        self.prompt = PromptTemplate(
            input_variables=["analysis"],
            template=(
                "아래는 수능 영어 문제 분석 결과입니다:\n"
                "{analysis}\n"
                "이 분석 결과를 기반으로 새로운 문제를 생성해주세요. "
                "문제는 동일한 유형과 난이도를 유지하면서도 새롭게 작성되어야 합니다."
            ),
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)

    def generate(self, analysis):
        return self.chain.run(analysis=analysis)


# 문제 검증 에이전트
class QuestionValidationAgent:
    def __init__(self, llm):
        self.llm = llm
        self.prompt = PromptTemplate(
            input_variables=["generated_question"],
            template=(
                "아래는 생성된 영어 문제입니다:\n"
                "{generated_question}\n"
                "이 문제의 문법과 수능 문제로서의 적합성을 검증하고 개선점을 제안해주세요."
            ),
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)

    def validate(self, generated_question):
        return self.chain.run(generated_question=generated_question)


# 실행기 생성
class QuestionGeneratorPipeline:
    def __init__(self, llm):
        self.analysis_agent = QuestionAnalysisAgent(llm)
        self.generation_agent = QuestionGenerationAgent(llm)
        self.validation_agent = QuestionValidationAgent(llm)

    def run_pipeline(self, example_question):
        # Step 1: 문제 분석
        analysis = self.analysis_agent.analyze(example_question)
        print("문제 분석 결과:", analysis)

        # Step 2: 문제 생성
        generated_question = self.generation_agent.generate(analysis)
        print("생성된 문제:", generated_question)

        # Step 3: 문제 검증
        validation = self.validation_agent.validate(generated_question)
        print("문제 검증 결과:", validation)

        return {
            "analysis": analysis,
            "generated_question": generated_question,
            "validation": validation,
        }


if __name__ == "__main__":
    # GPT-4를 LLM으로 초기화 (ChatOpenAI 사용)
    llm = ChatOpenAI(model="gpt-4", temperature=0.7, openai_api_key=api_key)
    pipeline = QuestionGeneratorPipeline(llm)

    # 예시 문항 입력
    example_question = (
        "Choose the correct word to fill in the blank: \n"
        "He has been ______ the project for several months. \n"
        "1) work\n"
        "2) working\n"
        "3) works\n"
        "4) worked"
    )
    result = pipeline.run_pipeline(example_question)
