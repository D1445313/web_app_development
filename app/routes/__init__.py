def init_app(app):
    """負責把所有切分的 Blueprint 統一註冊進主 app 內"""
    from .recipes import recipes_bp
    
    app.register_blueprint(recipes_bp)
