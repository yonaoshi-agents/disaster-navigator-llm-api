# LLMチャットと入力提案

## API
/chat : チャットのAPI
/query_suggest : 入力提案のためのAPI

## LLMとインフラ
- LLM : [Qwen3-32B](https://huggingface.co/Qwen/Qwen3-32B)
- GPU : NVIDIA H100 VRAM 240GB

## 依存関係
- Poetry=2.2.1
- CUDA toolkit=12.8

##　起動方法
```
poetry install
poetry run uvicorn main:app --host 0.0.0.0 --port 8000
```

## ファイル構成
- ./main.py : APIサーバー(fastapi)
- ./generate.py : 生成用の関数
- ./junk_scripts/* : 動作確認用コード