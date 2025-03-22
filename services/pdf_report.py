from fpdf import FPDF
import os

def generate_pdf_report(student_id, conversation_id, evaluation_data):
    os.makedirs("data/evaluation_logs", exist_ok=True)

    pdf = FPDF()
    pdf.add_page()

    # ✅ 한글 폰트 등록 (Regular + Bold)
    pdf.add_font("Nanum", "", "services/NanumGothic-Regular.ttf", uni=True)
    pdf.add_font("Nanum", "B", "services/NanumGothic-Bold.ttf", uni=True)

    # ✅ 기본 폰트 설정
    pdf.set_font("Nanum", "B", size=14)
    pdf.cell(200, 10, txt="GPT 평가 리포트", ln=True, align='C')

    pdf.ln(10)
    pdf.set_font("Nanum", "", size=12)
    pdf.cell(200, 10, txt=f"학생: {student_id}", ln=True)
    pdf.cell(200, 10, txt=f"대화 ID: {conversation_id}", ln=True)
    pdf.ln(5)

    # ✅ 평가 항목별 점수 및 설명
    scores = evaluation_data.get("scores", {})
    explanations = evaluation_data.get("explanations", {})

    pdf.set_font("Nanum", "B", size=12)
    pdf.cell(200, 10, txt="📊 평가 항목별 점수 및 설명", ln=True)
    pdf.ln(5)

    pdf.set_font("Nanum", "", size=11)
    for criterion, score in scores.items():
        explanation = explanations.get(criterion, "")
        pdf.cell(200, 8, txt=f"- {criterion}: {score}점", ln=True)
        if explanation:
            pdf.multi_cell(0, 8, txt=f"  설명: {explanation}")

    pdf.ln(5)
    pdf.set_font("Nanum", "B", size=12)
    pdf.cell(200, 10, txt="📝 총평", ln=True)
    pdf.set_font("Nanum", "", size=11)
    pdf.multi_cell(0, 8, txt=evaluation_data.get("summary", ""))

    # ✅ 저장 경로
    output_path = f"data/evaluation_logs/{conversation_id}_report.pdf"
    pdf.output(output_path)
    return output_path