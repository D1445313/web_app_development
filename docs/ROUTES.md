# 路由與頁面設計文件 (Routes Design) - 食譜收藏系統

根據系統功能與流程規劃，本專案將 Flask 路由劃分為對應的模組，並遵循基本的 RESTful 原則（部分刪除更新操作因 HTML 表單限制改採 POST）。

## 1. 路由總覽表格

| 功能 | HTTP 方法 | URL 路徑 | 對應模板 | 說明 |
| --- | --- | --- | --- | --- |
| 首頁 / 食譜總覽 | GET | `/` | `templates/recipes/index.html` | 顯示所有食譜，作為系統首頁 (亦可導向 `/recipes`) |
| 新增食譜頁面 | GET | `/recipes/new` | `templates/recipes/new.html` | 顯示新增食譜與食材輸入的表單 |
| 建立食譜邏輯 | POST | `/recipes` | — | 接收表單並儲存至 DB 後，重導向至首頁 |
| 查看食譜詳情 | GET | `/recipes/<int:recipe_id>` | `templates/recipes/detail.html` | 顯示特定食譜的詳細內容與所需食材 |
| 編輯食譜頁面 | GET | `/recipes/<int:recipe_id>/edit`| `templates/recipes/edit.html` | 顯示帶有既有資料的表單供修改 |
| 更新食譜邏輯 | POST | `/recipes/<int:recipe_id>/update` | — | 接收並更新 DB 後，重導向至食譜首頁或詳情頁 |
| 刪除食譜邏輯 | POST | `/recipes/<int:recipe_id>/delete` | — | 刪除指定食譜，完成後重導向至首頁 |
| 食譜搜尋頁面 | GET | `/recipes/search` | `templates/recipes/search.html` | 輸入關鍵字搜尋並顯示相符的食譜清單 |
| 食材推薦頁面 | GET | `/recipes/recommend` | `templates/recipes/recommend.html` | 輸入現有食材並回傳可實作的推薦食譜 |

## 2. 每個路由的詳細說明

### `GET /`
- **輸入**: 無
- **處理邏輯**: 呼叫 `RecipeModel.get_all()` 取得所有食譜備妥於資料清單中。
- **輸出**: 渲染 `recipes/index.html`。
- **錯誤處理**: 若目前沒有任何食譜，列表仍建立並正常渲染，畫面中可顯示「無任何食譜紀錄」之提示。

### `GET /recipes/new`
- **輸入**: 無
- **處理邏輯**: 直接提供前端撰寫所需的空白表單網頁。
- **輸出**: 渲染 `recipes/new.html`。

### `POST /recipes`
- **輸入**: 由使用者透過表單提交的 `title`、`description`、`instructions` 與食材清單。
- **處理邏輯**: 
  1. 後端進行參數完整性檢查。
  2. 確認正常後呼叫 `RecipeModel.create(...)` 存入。
- **輸出**: 若成功建立，重新導向轉址至 `GET /`。
- **錯誤處理**: 標題若遺漏，則回傳含錯誤提示之新增頁面。

### `GET /recipes/<int:recipe_id>`
- **輸入**: URL 中的路徑參數 `recipe_id`
- **處理邏輯**: 呼叫 `RecipeModel.get_by_id(recipe_id)` 取得指定食譜。
- **輸出**: 渲染 `recipes/detail.html` 並傳遞取出之字典。
- **錯誤處理**: 如果 ID 不在資料庫內回傳 Null，則啟動 404 中斷回傳 Not Found。

### `GET /recipes/<int:recipe_id>/edit`
- **輸入**: 路徑參數 `recipe_id`
- **處理邏輯**: 藉由 ID 呼叫 `RecipeModel` 找出現值的快照，以便供前端載入成為初始值。
- **輸出**: 渲染 `recipes/edit.html` 並傳遞原資料。
- **錯誤處理**: 查無資料依舊回傳 404 中斷。

### `POST /recipes/<int:recipe_id>/update`
- **輸入**: ID 與被覆寫後的表單欄位。
- **處理邏輯**: 使用 `RecipeModel.update(...)`。
- **輸出**: 更新完成立刻轉為 `redirect(url_for('recipes.detail', recipe_id=recipe_id))` 檢視成品。

### `POST /recipes/<int:recipe_id>/delete`
- **輸入**: 藉由路徑對應目標 ID。
- **處理邏輯**: 觸發刪除邏輯 `RecipeModel.delete(recipe_id)`。
- **輸出**: 清空後轉至對應總覽頁。

### `GET /recipes/search`
- **輸入**: 透過 URL 參數取得 `?keyword=XXX`
- **處理邏輯**: 若參數不為空，呼叫 `search_by_keyword(keyword)`，從標題敘述中去尋找清單。
- **輸出**: 返回 `recipes/search.html` 將結果清單做呈現。

### `GET /recipes/recommend`
- **輸入**: 包含 Query String，如 `?ingredients=Apple,Egg`
- **處理邏輯**: 將收到的字串做切割，後送入 `RecipeModel.recommend_by_ingredients(...)` 作簡單加權。
- **輸出**: 攜帶匹配資料列交予 `recipes/recommend.html` 做結果渲染。

## 3. Jinja2 模板清單

將採用基本繼承版型維持網站外觀統一。

*   `templates/base.html`：基底佈局 (含有公用 Navbar, Footer 還有靜態資源路徑)。
*   `templates/recipes/index.html`：以 Card layout 或清單列出資訊的總表 (繼承自 `base`)。
*   `templates/recipes/new.html`：負責輸入新資料含前端增減項按鈕控制的表格。
*   `templates/recipes/detail.html`：專注於閱讀內文的使用者介面。
*   `templates/recipes/edit.html`：功能類似 `new.html`，但載有 Value 以做修補變更。
*   `templates/recipes/search.html`：提供顯目 SearchBar，與回傳條目串列區。
*   `templates/recipes/recommend.html`：提供能讓使用者輸入食材 Tag 的介面區域。

## 4. 路由骨架程式碼
為確保專案程式擴充性更佳，使用了 Flask Blueprint 將路徑打包，建立於 `app/routes/` 檔案內。請參閱專案 `app/routes/` 中的 `.py`。
