import os
import sys
import django
import pandas as pd
from scripts.models import QuestionMeta  # 정의한 모델 임포트

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(project_root)

# Django 설정 초기화 (맨 위에 추가)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'script_editor.config.settings')
django.setup()

def save_metadata_to_db(csv_file_path):
    """
    CSV 파일을 읽어서 Django ORM에 저장하는 함수.
    """
    # 1. CSV 파일 읽기
    metadata_df = pd.read_csv(csv_file_path)

    # 2. 데이터프레임의 각 행을 순회하며 저장
    for _, row in metadata_df.iterrows():
        QuestionMeta.objects.create(
            question_type=row['question_type'],         # 문제 유형
            question=row['question'],            # 문제 본문
            options=row['options'],                  # 보기 (콤마로 구분된 텍스트)
            vocabulary=row['vocabulary'],               # 어휘
            answer=row['answer'],                     # 정답
            explanation=row['explanation']               # 해설
        )
    print("Successfully saved all 'suneung_data' to the database.")

csv_file_path = '../../db/suneung_data.csv'
save_metadata_to_db(csv_file_path)
