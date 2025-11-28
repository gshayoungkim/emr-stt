from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
from transcriber import Transcriber
from soap_generator import SOAPGenerator
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()  # .env 파일 로드
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB 제한
app.config['UPLOAD_FOLDER'] = 'temp'

# 업로드 폴더 생성
os.makedirs('temp', exist_ok=True)

# 전역 객체 초기화
transcriber = None
soap_gen = None

def init_models():
    """모델 초기화 (처음 한 번만)"""
    global transcriber, soap_gen
    if transcriber is None:
        print("🔄 Whisper 모델 로딩 중...")
        transcriber = Transcriber(model_name="base")
    if soap_gen is None:
        soap_gen = SOAPGenerator()

@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_audio():
    """오디오 파일 업로드"""
    if 'audio' not in request.files:
        return jsonify({'error': '파일이 없습니다'}), 400
    
    file = request.files['audio']
    if file.filename == '':
        return jsonify({'error': '파일이 선택되지 않았습니다'}), 400
    
    # 파일 저장
    filename = secure_filename(f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    return jsonify({
        'success': True,
        'filepath': filepath,
        'filename': filename
    })

@app.route('/api/transcribe', methods=['POST'])
def transcribe_audio():
    """STT 처리"""
    data = request.json
    filepath = data.get('filepath')
    
    if not filepath or not os.path.exists(filepath):
        return jsonify({'error': '파일을 찾을 수 없습니다'}), 400
    
    try:
        init_models()
        transcript = transcriber.transcribe(filepath, language="ko")
        
        # 임시 파일 삭제 (휘발성 처리)
        os.remove(filepath)
        
        return jsonify({
            'success': True,
            'transcript': transcript
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-soap', methods=['POST'])
def generate_soap():
    """SOAP 노트 생성"""
    data = request.json
    transcript = data.get('transcript')
    department = data.get('department', '내과')
    
    if not transcript:
        return jsonify({'error': '전사 텍스트가 없습니다'}), 400
    
    try:
        init_models()
        soap_note = soap_gen.generate_soap_note(transcript, department)
        
        return jsonify({
            'success': True,
            'soap_note': soap_note
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/medications', methods=['GET'])
def get_medications():
    """약물 템플릿 조회"""
    init_models()
    return jsonify(soap_gen.medications)

@app.route('/api/medications/search', methods=['POST'])
def search_medications():
    """약물 검색"""
    data = request.json
    keyword = data.get('keyword', '')
    
    init_models()
    results = soap_gen.search_medication(keyword)
    
    return jsonify({
        'success': True,
        'results': results
    })

@app.route('/api/medications/add', methods=['POST'])
def add_medication():
    """약물 추가"""
    data = request.json
    category = data.get('category')
    medication = data.get('medication')
    
    if not category or not medication:
        return jsonify({'error': '카테고리와 약물 정보가 필요합니다'}), 400
    
    try:
        init_models()
        soap_gen.add_medication_template(category, medication)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Render가 할당하는 포트 사용
    app.run(host='0.0.0.0', port=port)