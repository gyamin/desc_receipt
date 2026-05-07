# ローカル開発環境構築手順

## dockerコンテナ利用の場合

### Execute main.py
```
% docker compose up
 ✔ Container desc_receipt-app-1 Recreated                                                       0.1s
Attaching to app-1
app-1  | Hello, World!
app-1 exited with code 0
```

### PyCharm での実行設定

#### configure python interpreter.
![10001.png](img/10001.png)

#### debug and execute main.py.
![10002.png](img/10002.png)


## virtualenv利用の場合

### python実行環境とvenv構築
python
```
% pyenv local 3.12.12
% pyenv versions
  system
  3.12.9
* 3.12.12 (set by /xx/desc_receipt/.python-version)
```

venv
```
% python -m venv .venv
% source .venv/bin/activate
(venv) % pip install -r requirements.txt
```