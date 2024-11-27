import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import json, csv

def write_faiss_index():
    data = []
    with open ('../../db/suneung_data.csv', 'r') as f:
        reader = csv.reader(f)
        next(reader)
        data = [{"id": row[0], "question": row[2]} for row in reader]

    # 문제 본문 추출 및 임베딩 생성
    model = SentenceTransformer('all-MiniLM-L6-v2')
    texts = [item["question"] for item in data]
    ids = [item["id"] for item in data]
    embeddings = model.encode(texts)

    # FAISS 인덱스 생성 및 벡터 추가
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings).astype('float32'))

    # FAISS 인덱스 저장
    faiss.write_index(index, '../../db/faiss_index.index')

    return ids

def load_faiss_index():
    """FAISS 인덱스 및 ID 매핑 로드"""
    index = faiss.read_index('../../db/faiss_index.index')
    return index

def search_faiss_index(query):
    """사용자가 입력한 질문에 대해 FAISS 인덱스를 검색하여 가장 유사한 질문의 id를 반환"""
    index = load_faiss_index()

    # 사용자 입력 쿼리 처리
    query_vector = model.encode([query]).astype('float32')

    # FAISS 검색 수행
    distances, indices = index.search(query_vector, k=1)  # 가장 유사한 질문 1개 검색

    # 검색된 id 가져오기 (FAISS 결과 → id 매핑) 4
    matched_id = ids[indices[0][0]]
    return matched_id

if __name__ == "__main__":
    query = "The ability to understand emotions"
    print(search_faiss_index(query))
