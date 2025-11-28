from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()

class SOAPGenerator:
    def __init__(self, template_file="medication_templates.json"):
        """OpenAI 클라이언트 및 약물 템플릿 초기화"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("❌ OPENAI_API_KEY가 .env 파일에 설정되지 않았습니다.")
        
        self.client = OpenAI(api_key=api_key)
        
        # 약물 템플릿 로드
        self.medications = {}
        if os.path.exists(template_file):
            with open(template_file, 'r', encoding='utf-8') as f:
                self.medications = json.load(f)
            print(f"✅ 약물 템플릿 {len(self.medications)}개 로드 완료")
        else:
            print("⚠️  약물 템플릿 파일이 없습니다. 기본 모드로 실행합니다.")
        
        print("✅ OpenAI API 연결 완료\n")
    
    def generate_soap_note(self, transcript, department="내과"):
        """
        진료 대화에서 의사가 말한 내용만 추출하여 SOAP 작성
        AI가 임의로 진단/처방을 생성하지 않음
        """
        
        system_prompt = f"""당신은 한국 {department} 의원의 의료 차트 작성 보조 AI입니다.

**핵심 규칙 - 절대 준수**:
1. 진단(Assessment)과 처방(Plan)을 절대 생성하거나 추론하지 마세요
2. 의사가 명시적으로 말한 내용만 추출하세요
3. 환자 발언은 S에, 의사 발언은 O/A/P에 배치하세요
4. 불확실하면 빈 칸으로 두세요

**출력 형식**:
S (Subjective - 주관적 증상):
- 환자가 호소한 증상만 나열

O (Objective - 객관적 소견):
- 의사가 관찰/측정한 객관적 사실만 기록
- 예: 체온, 혈압, 신체 검진 소견

A (Assessment - 평가/진단):
- 의사가 "~의심됩니다", "~로 보입니다", "~진단" 등으로 언급한 내용만 기록
- 의사 발언이 없으면 "(의사 진단 필요)" 표시

P (Plan - 치료 계획):
- 의사가 언급한 처방, 검사, 생활 지도만 기록
- 약물명이 언급되면 그대로 기록
- 의사 발언이 없으면 "(의사 처방 필요)" 표시
"""

        user_prompt = f"""다음 진료 대화에서 정보를 추출해주세요:

{transcript}

**중요**: 진단과 처방은 의사가 명확히 말한 내용만 적어주세요. 추측하지 마세요.
"""

        print("🤖 GPT가 진료 내용을 추출 중...")
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,  # 매우 낮게 설정 (창의성 최소화)
                max_tokens=800
            )
            
            soap_note = response.choices[0].message.content
            print("✅ SOAP 노트 추출 완료!\n")
            
            return soap_note
            
        except Exception as e:
            print(f"❌ GPT API 호출 실패: {e}")
            return None
    
    def add_medication_template(self, category, medication_info):
        """
        약물 템플릿 추가
        
        Args:
            category: 약물 카테고리 (예: "해열제", "항생제")
            medication_info: 약물 정보 (예: "타이레놀 500mg 1T #3")
        """
        if category not in self.medications:
            self.medications[category] = []
        
        self.medications[category].append(medication_info)
        
        # 파일에 저장
        with open("medication_templates.json", 'w', encoding='utf-8') as f:
            json.dump(self.medications, ensure_ascii=False, indent=2)
        
        print(f"✅ '{category}' 카테고리에 약물 추가: {medication_info}")
    
    def show_medication_templates(self):
        """등록된 약물 템플릿 출력"""
        if not self.medications:
            print("❌ 등록된 약물 템플릿이 없습니다.")
            return
        
        print("\n=== 등록된 약물 템플릿 ===")
        for category, meds in self.medications.items():
            print(f"\n[{category}]")
            for i, med in enumerate(meds, 1):
                print(f"  {i}. {med}")
        print()
    
    def search_medication(self, keyword):
        """
        키워드로 약물 검색
        
        Args:
            keyword: 검색할 키워드 (예: "열", "타이레놀")
        
        Returns:
            매칭되는 약물 리스트
        """
        results = []
        for category, meds in self.medications.items():
            for med in meds:
                if keyword in category or keyword in med:
                    results.append(f"[{category}] {med}")
        
        return results
