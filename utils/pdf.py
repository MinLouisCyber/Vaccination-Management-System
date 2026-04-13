from io import BytesIO
from datetime import datetime

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import qrcode


def generate_certificate_pdf(profile, appointment):
    """Generate a vaccination certificate PDF and return a BytesIO buffer."""

    # ── Font setup ──────────────────────────────────────────────────────────
    try:
        pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
        try:
            pdfmetrics.registerFont(TTFont('Arial-Bold', 'arialbd.ttf'))
            MAIN_FONT = 'Arial'
            BOLD_FONT = 'Arial-Bold'
        except Exception:
            MAIN_FONT = 'Arial'
            BOLD_FONT = 'Arial'
    except Exception as e:
        print(f"CẢNH BÁO FONT: {e}")
        MAIN_FONT = 'Helvetica'
        BOLD_FONT = 'Helvetica-Bold'

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    margin_left  = 50
    margin_right = 50
    current_y    = height - 50

    styles      = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=24,
        alignment=1,
        textColor=colors.HexColor("#003366"),
        spaceAfter=20,
        fontName=BOLD_FONT
    )
    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['BodyText'],
        fontSize=12,
        leading=16,
        fontName=MAIN_FONT
    )

    # ── Watermark ───────────────────────────────────────────────────────────
    p.saveState()
    p.setFillColor(colors.HexColor('#f0f0f0'))
    p.setFont(BOLD_FONT, 60)
    p.translate(width / 2, height / 2)
    p.rotate(45)
    p.drawCentredString(0, 0, "Vinavacci OFFICIAL")
    p.restoreState()

    # ── Header ──────────────────────────────────────────────────────────────
    header_height = 60
    p.setFillColor(colors.HexColor("#003366"))
    p.rect(0, height - header_height, width, header_height, stroke=0, fill=1)

    header_text_left = Paragraph(
        f"<font name='{BOLD_FONT}'>Bộ Y tế Việt Nam</font><br/>"
        f"<font name='{MAIN_FONT}'>Hệ thống tiêm chủng quốc gia</font>",
        ParagraphStyle('LeftHeader', parent=normal_style, fontSize=12, textColor=colors.white, alignment=0)
    )
    header_text_right = Paragraph(
        f"<font name='{BOLD_FONT}'>Hồ sơ tiêm chủng</font><br/>"
        f"<font name='{BOLD_FONT}'>Chứng nhận điện tử</font>",
        ParagraphStyle('RightHeader', parent=normal_style, fontSize=12, textColor=colors.white, alignment=2)
    )
    header_table = Table(
        [[header_text_left, header_text_right]],
        colWidths=[width * 0.7, width * 0.3],
        hAlign='LEFT'
    )
    header_table.setStyle(TableStyle([
        ('VALIGN',       (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING',  (0, 0), (-1, -1), 15),
        ('RIGHTPADDING', (0, 0), (-1, -1), 15),
    ]))
    header_table.wrapOn(p, width, height)
    header_table.drawOn(p, 0, height - header_height + 5)
    current_y = height - header_height - 30

    # ── Title ───────────────────────────────────────────────────────────────
    title = Paragraph("CHỨNG NHẬN TIÊM CHỦNG ĐIỆN TỬ", title_style)
    w, h  = title.wrap(width - margin_left - margin_right, 50)
    title.drawOn(p, margin_left, current_y - h)
    current_y -= h + 20

    # ── Personal Information ─────────────────────────────────────────────────
    p.setFillColor(colors.HexColor('#e8f4fc'))
    p.rect(margin_left, current_y - 25, width - margin_left - margin_right, 25, fill=1, stroke=0)
    section_title = Paragraph(
        f"<font name='{BOLD_FONT}'>Thông tin cá nhân</font>",
        ParagraphStyle('SectionTitle', parent=normal_style, fontSize=14, textColor=colors.HexColor("#003366"))
    )
    w, h = section_title.wrap(width - margin_left - margin_right, 25)
    section_title.drawOn(p, margin_left + 10, current_y - h - 5)
    current_y -= 35

    personal_info = [
        ["Mã chứng nhận:", f"VN/COV/{appointment.appointment_id:08d}"],
        ["Họ và tên:", f"{profile.fname} {(profile.mname + ' ') if profile.mname else ''}{profile.lname}"],
        ["Năm sinh:", f"{datetime.now().year - profile.age}"],
        ["Giới tính:", profile.gender.upper()],
        ["Mã y tế:", f"VN{profile.profile_id:011d}"],
    ]
    info_table = Table(personal_info, colWidths=[150, width - margin_left - margin_right - 150])
    info_table.setStyle(TableStyle([
        ('FONTNAME',      (0, 0), (-1, -1), MAIN_FONT),
        ('FONTSIZE',      (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING',    (0, 0), (-1, -1), 6),
        ('BACKGROUND',    (0, 0), (-1, 0),  colors.HexColor('#e8f4fc')),
        ('BOX',           (0, 0), (-1, -1), 0.5, colors.gray),
        ('INNERGRID',     (0, 0), (-1, -1), 0.5, colors.gray),
    ]))
    tw, th = info_table.wrap(width - margin_left - margin_right, current_y)
    info_table.drawOn(p, margin_left, current_y - th)
    current_y -= th + 30

    # ── Vaccination Details ──────────────────────────────────────────────────
    p.setFillColor(colors.HexColor('#e8f4fc'))
    p.rect(margin_left, current_y - 25, width - margin_left - margin_right, 25, fill=1, stroke=0)
    vacc_section_title = Paragraph(
        f"<font name='{BOLD_FONT}'>Chi tiết mũi tiêm</font>",
        ParagraphStyle('SectionTitle', parent=normal_style, fontSize=14, textColor=colors.HexColor("#003366"))
    )
    w, h = vacc_section_title.wrap(width - margin_left - margin_right, 25)
    vacc_section_title.drawOn(p, margin_left + 10, current_y - h - 5)
    current_y -= 35

    description_para    = Paragraph(appointment.vaccine.description, normal_style)
    center_address_text = (
        f"{appointment.schedule.centre.address}<br/>"
        f"{appointment.schedule.centre.district} - {appointment.schedule.centre.pincode}"
    )
    center_address_para = Paragraph(center_address_text, normal_style)

    vaccine_data = [
        ["Tên vắc-xin:", appointment.vaccine.name],
        ["Mô tả:",       description_para],
        ["Số lô:",       "BATCH-{:04d}".format(appointment.vaccine.vaccine_id)],
        ["Mũi tiêm số:", f"Mũi {appointment.schedule.dose_number}"],
        ["Ngày tiêm:",   appointment.appointment_date.strftime("%d/%m/%Y")],
        ["Nơi tiêm:",    appointment.schedule.centre.name],
        ["Địa chỉ:",     center_address_para],
    ]
    vaccine_table = Table(vaccine_data, colWidths=[150, width - margin_left - margin_right - 150])
    vaccine_table.setStyle(TableStyle([
        ('FONTNAME',      (0, 0), (-1, -1), MAIN_FONT),
        ('FONTSIZE',      (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING',    (0, 0), (-1, -1), 6),
        ('BACKGROUND',    (0, 0), (-1, 0),  colors.HexColor('#e8f4fc')),
        ('BOX',           (0, 0), (-1, -1), 0.5, colors.gray),
        ('INNERGRID',     (0, 0), (-1, -1), 0.5, colors.gray),
    ]))
    tw, th = vaccine_table.wrap(width - margin_left - margin_right, current_y)
    vaccine_table.drawOn(p, margin_left, current_y - th)
    current_y -= th + 40

    # ── QR Code ─────────────────────────────────────────────────────────────
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=3,
        border=2,
    )
    qr_data = (
        f"VACCINE CERTIFICATE\n"
        f"ID: IND/COV/{appointment.appointment_id:08d}\n"
        f"Name: {profile.fname} {(profile.mname + ' ') if profile.mname else ''}{profile.lname}\n"
        f"DOB: 01/01/{datetime.now().year - profile.age}\n"
        f"Vaccine: {appointment.vaccine.name}\n"
        f"Dose: {appointment.schedule.dose_number}\n"
        f"Date: {appointment.appointment_date.strftime('%d/%m/%Y')}\n"
        f"Center ID: {appointment.schedule.centre.centre_id}"
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")

    img_buffer = BytesIO()
    qr_img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    qr_image = ImageReader(img_buffer)

    qr_box_width  = 150
    qr_box_height = 150
    qr_box_x      = width - margin_right - qr_box_width
    qr_box_y      = 150

    p.setFillColor(colors.white)
    p.rect(qr_box_x, qr_box_y, qr_box_width, qr_box_height, fill=1, stroke=1)

    qr_img_margin  = 10
    qr_img_width   = qr_box_width  - 2 * qr_img_margin
    qr_img_height  = qr_box_height - 2 * qr_img_margin
    p.drawImage(qr_image, qr_box_x + qr_img_margin, qr_box_y + qr_img_margin, qr_img_width, qr_img_height)

    p.setFont("Helvetica-Bold", 10)
    p.setFillColor(colors.HexColor("#003366"))
    p.drawCentredString(qr_box_x + qr_box_width / 2, qr_box_y - 12, "Scan to Verify Authenticity")

    # ── Security Band ────────────────────────────────────────────────────────
    security_band_y      = 80
    security_band_height = 30
    p.setFillColor(colors.HexColor('#d3d3d3'))
    p.rect(margin_left, security_band_y, width - margin_left - margin_right, security_band_height, fill=1, stroke=0)
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 12)
    p.drawCentredString(width / 2, security_band_y + 10, "UNOFFICIAL DOCUMENT")

    # ── Footer ───────────────────────────────────────────────────────────────
    p.setFont("Helvetica", 8)
    footer_lines = [
        "* This is a mock certificate generated for educational purposes as part of a DBMS project demonstration.",
        "Not valid for official use. For demonstration purposes only.",
        f"Certificate Generated on: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
    ]
    footer_y = security_band_y - 12
    for line in footer_lines:
        p.drawCentredString(width / 2, footer_y, line)
        footer_y -= 12

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer
