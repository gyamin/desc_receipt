# desc_receipt
レシートPDF解析プログラム

## 使い方


### ビルド
```
% docker build -t desc_receipt .
```

### コンテナ実行
```
% docker run --name desc_receipt \
-v ~/Library/CloudStorage/OneDrive-個人用/ドキュメント:/receipts \
-v ~/Desktop/レシート:/output \
desc_receipt:latest
```

