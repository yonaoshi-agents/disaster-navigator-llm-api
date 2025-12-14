import json
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from generate import generate
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.middleware.cors import CORSMiddleware
import secrets
from jinja2 import Template

app = FastAPI()

security = HTTPBasic()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     # すべてのオリジンを許可
    allow_credentials=True,  # Cookie / 認証情報を許可
    allow_methods=["*"],     # GET, POST などすべてのメソッドを許可
    allow_headers=["*"],     # 任意のヘッダーを許可
)


# 認証情報（ベーシック認証）
def verify_password(credentials: HTTPBasicCredentials = Depends(security)):
    # 固定ユーザー名とパスワード
    correct_username = secrets.compare_digest(credentials.username, "admin")
    correct_password = secrets.compare_digest(credentials.password, "tech_worlds_1213")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

class ChatRequest(BaseModel):
    messages: list[dict[str, str]]

class ChatResponse(BaseModel):
    reply: str

def format_messages(messages: list[dict[str, str]]) -> str:
    formatted = ""
    for message in messages:
        role = message.get("role", "user")
        content = message.get("content", "")
        formatted += f"{role}: {content}\n"
    return formatted

@app.get("/")
async def root():
    return {"message": "Chat API is running."}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, username: str = Depends(verify_password)):
    # ここに実際のチャットモデル処理を追加できます
    user_messages = request.messages
    formatted_messages = format_messages(user_messages)
    prompt = """あなたは地震の専門家のAIです。
現在ユーザーは地震に関して不安を抱えているので、適切なアドバイスや情報を提供してください。

以下のメッセージは地震災害に関するユーザーとそのアシスタントの会話です。

## 制約条件
- 回答は地震災害に関連するものであること。
- 回答は具体的であること。
- 回答は150文字程度で行うこと
- 出力は英語で行うこと

## 入力メッセージ
{{formatted_messages}}

# 出力

"""
    full_prompt = Template(prompt).render(formatted_messages=formatted_messages)
    reply_text = generate(full_prompt)
    return ChatResponse(reply=reply_text)

@app.post("/query_suggest")
async def query_suggest(request: ChatRequest, username: str = Depends(verify_password)):
    prompt = """あなたは地震の専門家のAIです。
現在ユーザーは地震に関して不安を抱えているので、適切なアドバイスや情報を提供してください。

以下のメッセージは地震災害に関するユーザーとそのアシスタントの会話です。ユーザーが次に尋ねそうな質問を3つ提案してください。

## 制約条件
- 質問は地震災害に関連するものであること。
- 質問は具体的であること。
- json形式で出力すること。
- 改行や箇条書きは使用しないこと。
- 英語で回答するようにしてください

## 出力形式
出力は以下のjson形式で行ってください。
{"suggest": ["質問1","質問2","質問3"]}

# 入力メッセージ
{{formatted_messages}}

# 出力

"""

    # 最後のrole == user の　contentを取得
    request_messages = request.messages
    for message in reversed(request_messages):
        if message.get("role") == "user":
            user_last_message_content = message.get("content", "")
            break

    full_prompt = Template(prompt).render(formatted_messages=user_last_message_content)
    # ここに実際のチャットモデル処理を追加できます
    try:
        suggestions_text = generate(full_prompt)
        suggest = json.loads(suggestions_text)
        suggestions = [s.strip() for s in suggest["suggest"]]
    except exception as e:
        # デフォルトの提案を返す
        suggestions = [
            "地震が発生した際の初動対応は？",
            "避難所での生活で注意すべきことは？",
            "地震に備えるための日常的な準備は？"
        ]
    return {"suggest": suggestions}