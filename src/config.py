class Config:
    SECRET_KEY = 'C!sadADASD'  # 🔑 Para CSRF y sesiones

class DevelopmentConfig(Config):
    DEBUG = True
    
    # 🔗 Conexión a la base de datos PostgreSQL
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@localhost:5432/colegio_db'
    
    # ❌ Desactiva el seguimiento de modificaciones (consume recursos)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

# 📦 Diccionario de configuraciones disponibles
config = {
    'development': DevelopmentConfig
}
