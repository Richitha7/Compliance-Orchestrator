# Demo Script

## 1) Normal compliant decision (no HITL)
```bash
python client/client.py --session DEMO1 --question "Does our login meet MFA under Policy X?" --autoplay
# Client prints progress updates and final decision JSON
```

## 2) Two HITL interruptions (clarification + upload)
```bash
python client/client.py --session DEMO2 --question "Check MFA for mobile login" --hitl 2
# Client will receive:
#  - clarification: "Which MFA method is used in mobile login?"
#  - upload_request: "Upload the iOS config screenshot."
```

## 3) Insufficient evidence after timeout
```bash
python client/client.py --session DEMO3 --question "Is SSO configured per Policy Y?" --force-timeout
```
