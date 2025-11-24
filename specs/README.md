# 需求規格管理資料夾（Specs）

這個資料夾用來存放您的需求規格文件，供 AI 解析與實現。

> **注意**：此資料夾命名為 `specs/` 以避免與 `requirements.txt`（Python 套件依賴）混淆。

## 📁 資料夾結構

```
specs/
├── README.md           # 本檔案
├── template.md         # 需求範本
├── active/             # 進行中的需求
├── completed/          # 已完成的需求
└── archived/           # 封存的需求
```

## ✍️ 如何撰寫需求

### 方式 1: 使用範本

複製 `template.md` 並填寫您的需求：

```bash
cp specs/template.md specs/active/my_feature.md
# 編輯 my_feature.md
```

### 方式 2: 自由格式

在 `active/` 資料夾中建立 `.md` 檔案，使用任何您習慣的格式撰寫需求。

## 📝 需求文件格式建議

### 基本格式

```markdown
# 功能名稱

## 目標
簡短描述這個功能要達成什麼目標

## 需求描述
詳細描述功能需求

## 驗收條件
- [ ] 條件 1
- [ ] 條件 2
- [ ] 條件 3

## 技術考量
- 使用的技術/套件
- 效能要求
- 安全性考量

## 參考資料
- 相關連結
- 範例程式碼
```

### 範例：新增 OCR 功能

```markdown
# PDF OCR 掃描檔支援

## 目標
讓系統能處理掃描版 PDF（圖片型 PDF），提取其中的文字。

## 需求描述
當前系統只能處理有文字層的 PDF，遇到掃描檔會無法提取內容。
需要整合 OCR 引擎來辨識圖片中的文字。

## 驗收條件
- [ ] 能偵測 PDF 是否為掃描檔
- [ ] 使用 OCR 提取掃描檔文字
- [ ] OCR 準確率 > 90%
- [ ] 處理時間 < 30 秒/頁
- [ ] 支援中英文混合辨識

## 技術考量
- 使用 Tesseract OCR 或 Google Vision API
- 需要前置影像處理（去噪、對比增強）
- 大檔案要考慮記憶體使用

## 參考資料
- [pytesseract](https://github.com/madmaze/pytesseract)
- [pdf2image](https://github.com/Belval/pdf2image)
```

## 🔄 需求生命週期

1. **撰寫需求** → 放在 `active/` 資料夾
2. **AI 解析** → AI 讀取並實現功能
3. **測試驗證** → 確認功能正常
4. **完成** → 移至 `completed/` 資料夾
5. **封存** → 舊需求移至 `archived/` 資料夾

## 🤖 給 AI 的指示

當您要求 AI 處理需求時，可以這樣說：

- "請讀取 specs/active/ 中的需求並實現"
- "檢查 specs 資料夾，看有什麼要做的"
- "實現 specs/active/feature_x.md 中的功能"
- "檢視所有未完成的需求並排優先順序"

## 💡 撰寫需求的最佳實踐

### 1. 明確且具體
❌ 「改善效能」  
✅ 「PDF 解析時間從 10 秒降至 3 秒以內」

### 2. 可測試/可驗證
❌ 「介面要好看」  
✅ 「所有按鈕使用圓角、主色調為藍色 #007bff、符合 Material Design 規範」

### 3. 包含背景與動機
說明「為什麼需要這個功能」，幫助 AI 理解脈絡做出更好的實現。

### 4. 提供範例
如果可以，提供範例輸入/輸出、截圖、或參考網站。

### 5. 列出相依性
說明這個功能依賴哪些現有功能，或會影響哪些模組。

## 📚 需求分類標籤

在需求檔案開頭可以加上標籤：

```markdown
---
type: feature | bugfix | enhancement | refactor
priority: high | medium | low
status: draft | ready | in-progress | completed
estimated_time: 2h | 1d | 1w
tags: [pdf, ai, security]
---
```

範例：

```markdown
---
type: feature
priority: high
status: ready
estimated_time: 1d
tags: [ocr, pdf, enhancement]
---

# PDF OCR 掃描檔支援
...
```

## 🎯 快速開始

1. **複製範本**
   ```bash
   cp specs/template.md specs/active/my_new_feature.md
   ```

2. **編輯需求**
   用任何文字編輯器打開並填寫

3. **請 AI 實現**
   ```
   "請實現 specs/active/my_new_feature.md 中的功能"
   ```

4. **完成後移動**
   ```bash
   mv specs/active/my_new_feature.md specs/completed/
   ```

## 📞 需要協助？

- 參考 `template.md` 範本
- 查看 `completed/` 資料夾中已完成的需求作為範例
- 直接詢問 AI：「如何撰寫好的需求文件？」

---

**提示**：這個資料夾是您與 AI 協作的橋樑。清楚的需求 = 精確的實現！

