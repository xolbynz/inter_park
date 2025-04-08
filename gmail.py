import smtplib
from email.mime.text import MIMEText

# 기본 설정
sender_email = "rnjs5162@gmail.com"
receiver_email = "rnjs5162@gmail.com"  # 자기 자신에게 보내도 OK
subject = "긴급 알림!"
body = "출발하세요! 교통이 혼잡합니다."

# 메일 내용 구성
msg = MIMEText(body)
msg['Subject'] = subject
msg['From'] = sender_email
msg['To'] = receiver_email

# Gmail SMTP 서버로 전송
smtp_server = "smtp.gmail.com"
smtp_port = 587

with smtplib.SMTP(smtp_server, smtp_port) as server:
    server.starttls()
    server.login(sender_email, "dnruf1006")  # 2단계 인증 시 앱 비밀번호 필요
    server.send_message(msg)

print("메일 전송 완료!")