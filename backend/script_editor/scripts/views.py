import openai
import faiss
import numpy as np
import json
from dotenv import load_dotenv
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

# 환경 변수 로드
# load_dotenv()
# openai.api_key = os.getenv("OPENAI_API_KEY")


# # /modules 디렉터리에서 FAISS 인덱스와 메타데이터 파일 로드
# modules_dir = os.path.join(os.path.dirname(__file__), "modules")
# faiss_index_path = os.path.join(modules_dir, "faiss_index.index")
# metadata_path = os.path.join(modules_dir, "metadata.json")

# # 저장된 FAISS 인덱스와 메타데이터 로드
# index = faiss.read_index(faiss_index_path)  # .index 파일에서 FAISS 인덱스 로드
# with open(metadata_path, "r", encoding="utf-8") as f:
#     metadata = json.load(f)


# # 1. 입력받은 글을 문장 단위로 파싱
# def parse_text_into_sentences(text):
#     """
#     1. 전체 텍스트를 문장 단위로 파싱합니다.
#     """
#     import re

#     # 문장 분할을 위한 정규 표현식 사용
#     sentences = re.split(r"(?<=[.!?]) +", text)
#     return sentences


# # 2. 문장 안에서 문법적으로 틀린 부분 찾기
# def identify_grammatical_errors(sentence):
#     """
#     2. 문장 내에서 문법적으로 틀린 부분을 식별합니다.
#     """
#     # OpenAI ChatCompletion API를 사용하여 문법 오류를 식별
#     response = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",
#         messages=[
#             {"role": "system", "content": "You are a helpful assistant."},
#             {
#                 "role": "user",
#                 "content": f"문장에서 문법적으로 틀린 부분을 찾아주세요:\n\n{sentence}",
#             },
#         ],
#         max_tokens=100,
#         temperature=0.5,
#     )
#     errors = response.choices[0].message["content"].strip().split("\n")
#     return errors


# # 3. 텍스트 임베딩 생성 함수
# def create_embedding(text):
#     """
#     3. 텍스트 임베딩을 생성하여 FAISS 검색에 사용합니다.
#     """
#     response = openai.Embedding.create(input=text, model="text-embedding-ada-002")
#     return np.array(response["data"][0]["embedding"], dtype=np.float32)


# # 3. FAISS 인덱스를 사용하여 유사한 오류와 수정본 검색
# def search_faiss_for_corrections(errors):
#     """
#     3. 발견된 오류에 대해 FAISS에서 유사한 오류와 수정할 내용을 검색합니다.
#     """
#     corrections = []
#     for error in errors:
#         # 오류를 임베딩하여 유사도 검색
#         error_embedding = create_embedding(error).reshape(1, -1)
#         distances, indices = index.search(error_embedding, k=5)

#         # 검색 결과에서 메타데이터 추출
#         matched_texts = [metadata[i]["corrected"] for i in indices[0]]
#         corrections.append(matched_texts)

#     return corrections


# # 4. LLM을 사용하여 문장 수정
# def correct_sentence_with_llm(sentence, errors, corrections):
#     """
#     4. LLM을 사용하여 문장과 검색된 수정 사항을 기반으로 문장을 수정합니다.
#     """
#     prompt = f'문장: "{sentence}"\n\n발견된 문법 오류와 수정 제안:\n'
#     for i, (error, correction) in enumerate(zip(errors, corrections), start=1):
#         prompt += f'{i}. 오류: "{error}" -> 수정: "{correction[0]}"\n'

#     prompt += (
#         "\n위 제안을 참고하여 문장을 수정해주세요. 수정된 문장만 간단하게 반환하세요."
#     )

#     response = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",
#         messages=[
#             {"role": "system", "content": "You are a helpful assistant."},
#             {"role": "user", "content": prompt},
#         ],
#         max_tokens=100,
#     )

#     corrected_sentence = response.choices[0].message["content"].strip()
#     return corrected_sentence


# # 5. 전체 텍스트의 모든 문장을 수정
# def correct_text(text):
#     """
#     5. 입력된 전체 텍스트를 문장 단위로 수정합니다.
#     """
#     sentences = parse_text_into_sentences(text)
#     corrected_sentences = []

#     for sentence in sentences:
#         errors = identify_grammatical_errors(sentence)
#         corrections = search_faiss_for_corrections(errors)
#         corrected_sentence = correct_sentence_with_llm(sentence, errors, corrections)
#         corrected_sentences.append(corrected_sentence)

#     return " ".join(corrected_sentences)


# # 6. 최종 수정된 텍스트를 반환
# def process_user_text(text):
#     """
#     6. 전체 텍스트를 받아 수정된 텍스트를 반환합니다.
#     """
#     corrected_text = correct_text(text)
#     # 모든 수정된 문장을 하나의 문자열로 결합
#     return corrected_text.replace('"', "")


# # APIView로 1~6 포장
# class ProcessUserTextAPIView(APIView):
#     def post(self, request):
#         user_text = request.data.get("text", "")
#         if not user_text:
#             return Response(
#                 {"error": "텍스트를 입력해 주세요."}, status=status.HTTP_400_BAD_REQUEST
#             )

#         # process_user_text 함수 호출
#         corrected_text = process_user_text(user_text)
#         return Response({"corrected_text": corrected_text}, status=status.HTTP_200_OK)



class ProcessUserTextAPIView(APIView):
    permission_classes = [AllowAny]  # 인증 요구사항 제거
    def post(self, request):
        # 요청 데이터 전체 로깅
        print("전체 요청 데이터:", request.data)
        
        # text 필드 추출
        user_text = request.data.get("text", "")
        print("받은 텍스트:", user_text)
        
        if not user_text:
            return Response(
                {"error": "텍스트를 입력해 주세요."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # 테스트용 에코 응답
        return Response({
            "generated_question": "생성된 질문",
            "message": "새로운 문제를 성공적으로 생성했습니다."
        }, status=status.HTTP_200_OK)

    
