import os
from transcriber import Transcriber
from soap_generator import SOAPGenerator

def medication_management_menu(soap_gen):
    """약물 템플릿 관리 메뉴"""
    while True:
        print("\n=== 약물 템플릿 관리 ===")
        print("1. 등록된 약물 보기")
        print("2. 새 약물 추가")
        print("3. 약물 검색")
        print("4. 돌아가기")
        
        choice = input("\n선택: ")
        
        if choice == "1":
            soap_gen.show_medication_templates()
        
        elif choice == "2":
            category = input("카테고리 입력 (예: 해열제, 항생제): ")
            med_info = input("약물 정보 입력 (예: 타이레놀 500mg 1T #3 5일분): ")
            soap_gen.add_medication_template(category, med_info)
        
        elif choice == "3":
            keyword = input("검색 키워드: ")
            results = soap_gen.search_medication(keyword)
            if results:
                print("\n검색 결과:")
                for r in results:
                    print(f"  - {r}")
            else:
                print("❌ 검색 결과가 없습니다.")
        
        elif choice == "4":
            break

def main():
    print("=== 의료 차트 작성 도우미 MVP ===\n")
    
    # SOAP Generator 초기화 (약물 템플릿 로드)
    soap_gen = SOAPGenerator()
    
    # 메인 메뉴
    print("1. 차트 작성 (음성 → SOAP)")
    print("2. 약물 템플릿 관리")
    print("3. 종료")
    
    menu_choice = input("\n선택: ")
    
    if menu_choice == "2":
        medication_management_menu(soap_gen)
        return
    elif menu_choice == "3":
        print("👋 종료합니다.")
        return
    elif menu_choice != "1":
        print("❌ 잘못된 선택입니다.")
        return
    
    # === 기존 차트 작성 플로우 ===
    
    # Step 1: 오디오 파일 선택
    print("\n1. 오디오 파일 업로드")
    print("2. 마이크로 녹음")
    choice = input("\n선택하세요 (1 또는 2): ")
    
    audio_file = None
    
    if choice == "1":
        audio_file = input("오디오 파일 경로: ")
        if not os.path.exists(audio_file):
            print(f"❌ 파일을 찾을 수 없습니다.")
            return
    elif choice == "2":
        try:
            from audio_recorder import AudioRecorder
            recorder = AudioRecorder()
            audio_file = recorder.record()
            recorder.cleanup()
        except Exception as e:
            print(f"❌ 녹음 실패: {e}")
            return
    else:
        print("❌ 잘못된 선택입니다.")
        return
    
    # Step 2: STT 처리
    transcriber = Transcriber(model_name="base")
    transcript = transcriber.transcribe(audio_file, language="ko")
    
    print("\n" + "="*60)
    print("📄 STT 결과:")
    print(transcript)
    print("="*60 + "\n")
    
    # Step 3: SOAP 노트 생성 (추출 방식)
    department = input("진료과를 입력하세요 (예: 내과, 정형외과): ") or "내과"
    soap_note = soap_gen.generate_soap_note(transcript, department=department)
    
    if soap_note:
        print("\n" + "="*60)
        print("📋 생성된 SOAP 노트:")
        print("="*60)
        print(soap_note)
        print("="*60 + "\n")
        
        # 약물 추가 제안
        print("💊 처방에 약물을 추가하시겠습니까?")
        if input("약물 검색 (y/n): ").lower() == 'y':
            keyword = input("검색 키워드 (예: 해열, 소화): ")
            results = soap_gen.search_medication(keyword)
            if results:
                print("\n검색 결과:")
                for i, r in enumerate(results, 1):
                    print(f"{i}. {r}")
        
        # 클립보드 복사
        copy_choice = input("\n클립보드에 복사하시겠습니까? (y/n): ")
        if copy_choice.lower() == 'y':
            try:
                import pyperclip
                pyperclip.copy(soap_note)
                print("✅ 클립보드에 복사 완료!")
            except ImportError:
                print("⚠️  pyperclip 설치 필요: pip install pyperclip")
    
    # Step 4: 휘발성 처리
    if audio_file.startswith("temp/"):
        os.remove(audio_file)
        print("\n🗑️  임시 파일 삭제 완료")
    
    print("\n✅ 처리 완료! 모든 데이터가 휘발되었습니다.")

if __name__ == "__main__":
    main()
