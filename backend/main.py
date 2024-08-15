from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from datetime import date
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
import os
from typing import List, Optional
from collections import defaultdict

app = FastAPI()

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

submissions = defaultdict(list)


class FormData(BaseModel):
    name: str
    telegram_nick: str
    referrer_nick: Optional[str] = None
    dob: date
    phone: str
    interview_time: str


@app.post("/submit")
async def submit_form(data: FormData):
    today = date.today()
    if len([d for d in submissions[data.phone] if d == today]) >= 2:
        raise HTTPException(status_code=429, detail="Вы можете отправлять форму не более 2 раз в день.")

    submissions[data.phone].append(today)

    message = MessageSchema(
        subject="Новая анкета",
        recipients=[os.getenv("RECIPIENT_EMAIL")],
        body=(
            f"Имя: {data.name}\n"
            f"Ник в Telegram: {data.telegram_nick}\n"
            f"Ник пригласившего: {data.referrer_nick or 'Не указан'}\n"
            f"Дата рождения: {data.dob}\n"
            f"Телефон: {data.phone}\n"
            f"время собеседования: {data.interview_time.replace('T', ' | ')}"
        ),
        subtype="plain"
    )

    fm = FastMail(conf)
    await fm.send_message(message)

    return {"message": "Форма успешно отправлена!"}
