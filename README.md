# Zoid

How to start

# inside devcontainer (Ubuntu 24.04)
python -m pip install --upgrade pip
pip install -r gpt2-hypercube-phase1/requirements.txt || true
pip install flask transformers torch

# run all tests (may take some time)
pytest -q
# or run specific tests
pytest -q gpt2-hypercube-phase1/tests/test_inference.py -q

python scripts/local_server.py --host 0.0.0.0 --port 5000

curl -s -X POST "http://127.0.0.1:5000/generate" -H "Content-Type: application/json" \
  -d '{"user_id":"me","prompt":"Write a short joke about onions.","mode":"balanced","max_new_tokens":50}' | jq# GPT2-model-intgration-in-website
# zoid-gpt2-chat-app
