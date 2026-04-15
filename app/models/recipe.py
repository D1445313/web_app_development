from .db import get_db

class RecipeModel:
    @staticmethod
    def get_all():
        """取得所有食譜清單"""
        conn = get_db()
        recipes = conn.execute("SELECT * FROM recipes ORDER BY created_at DESC").fetchall()
        conn.close()
        return [dict(r) for r in recipes]

    @staticmethod
    def get_by_id(recipe_id):
        """根據 ID 取得單筆食譜，包含其食材"""
        conn = get_db()
        recipe = conn.execute("SELECT * FROM recipes WHERE id = ?", (recipe_id,)).fetchone()
        if not recipe:
            conn.close()
            return None
        
        # 取得關聯的食材
        ingredients = conn.execute("SELECT * FROM ingredients WHERE recipe_id = ?", (recipe_id,)).fetchall()
        
        result = dict(recipe)
        result['ingredients'] = [dict(i) for i in ingredients]
        conn.close()
        return result

    @staticmethod
    def create(title, description, instructions, ingredients_list=None):
        """新增食譜與食材。ingredients_list 格式應為 [{'name': '雞蛋', 'amount': '2顆'}, ...]"""
        conn = get_db()
        cursor = conn.cursor()
        
        # 新增 recipes 表
        cursor.execute(
            "INSERT INTO recipes (title, description, instructions) VALUES (?, ?, ?)",
            (title, description, instructions)
        )
        recipe_id = cursor.lastrowid
        
        # 批次新增 ingredients 表
        if ingredients_list:
            for item in ingredients_list:
                cursor.execute(
                    "INSERT INTO ingredients (recipe_id, name, amount) VALUES (?, ?, ?)",
                    (recipe_id, item.get('name'), item.get('amount'))
                )
                
        conn.commit()
        conn.close()
        return recipe_id

    @staticmethod
    def update(recipe_id, title, description, instructions):
        """更新食譜內容"""
        conn = get_db()
        conn.execute(
            "UPDATE recipes SET title = ?, description = ?, instructions = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (title, description, instructions, recipe_id)
        )
        conn.commit()
        conn.close()
        return True

    @staticmethod
    def delete(recipe_id):
        """刪除食譜。有設定 FOREIGN KEY ON DELETE CASCADE，故相關聯的食材會一併被移除"""
        conn = get_db()
        # 需要確保 SQLite 有啟用 foreign keys
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
        conn.commit()
        conn.close()
        return True

    @staticmethod
    def search_by_keyword(keyword):
        """關鍵字搜尋食譜標題與內容"""
        conn = get_db()
        query = f"%{keyword}%"
        recipes = conn.execute(
            "SELECT * FROM recipes WHERE title LIKE ? OR description LIKE ? OR instructions LIKE ? ORDER BY created_at DESC", 
            (query, query, query)
        ).fetchall()
        conn.close()
        return [dict(r) for r in recipes]
        
    @staticmethod
    def recommend_by_ingredients(ingredient_names):
        """根據手邊的食材推薦食譜"""
        if not ingredient_names:
            return []
            
        placeholders = ', '.join(['?'] * len(ingredient_names))
        conn = get_db()
        
        # 給定食材在資料庫內的對應數量遞減排序
        sql = f"""
            SELECT r.*, COUNT(i.id) as match_count 
            FROM recipes r
            JOIN ingredients i ON r.id = i.recipe_id
            WHERE i.name IN ({placeholders})
            GROUP BY r.id
            ORDER BY match_count DESC, r.created_at DESC
        """
        recipes = conn.execute(sql, ingredient_names).fetchall()
        conn.close()
        return [dict(r) for r in recipes]
