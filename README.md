# desc_receipt
レシートPDF解析プログラム

## 使い方


### ビルド
```
% docker build -t desc_receipt .
```

### 処理実行方法

#### pdfファイル解析
```
% docker run --rm --name desc_receipt --mode desc \
-v ~/Library/CloudStorage/OneDrive-個人用/ドキュメント:/receipts \
-v ~/Desktop/レシート:/output \
desc_receipt:latest
```

#### pdfファイル名変更
```
% docker run --rm --name desc_receipt --mode rename \
-v ~/Library/CloudStorage/OneDrive-個人用/ドキュメント:/receipts \
-v ~/Desktop/レシート:/output \
desc_receipt:latest
```