# 📋 Guía de Instalación - LiveChat-IA

## 🚀 Cómo Ejecutar el Proyecto desde Cero

### 📋 **Requisitos Previos**

#### 1. Software Necesario
- **Python 3.8+** - [Descargar aquí](https://www.python.org/downloads/)
- **MySQL 8.0+** - [Descargar aquí](https://dev.mysql.com/downloads/)
- **Git** (opcional) - [Descargar aquí](https://git-scm.com/)

#### 2. Verificar Instalaciones
```bash
# Verificar Python
python --version
# Debe mostrar: Python 3.8.x o superior

# Verificar MySQL
mysql --version
# Debe mostrar: mysql Ver 8.0.x o superior

# Verificar pip
pip --version
```

---

## 🔧 **Paso 1: Preparar el Entorno**

### 1.1 Descargar el Proyecto
```bash
# Si tienes Git instalado
git clone [URL_DEL_REPOSITORIO] LiveChat-IA
cd LiveChat-IA

# O simplemente descomprime el archivo ZIP en la carpeta deseada
```

### 1.2 Crear Entorno Virtual (Recomendado)
```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate

# En macOS/Linux:
source venv/bin/activate
```

### 1.3 Instalar Dependencias
```bash
# Instalar dependencias de Python
pip install customtkinter
pip install mysql-connector-python
pip install bcrypt
pip install python-dotenv
pip install requests

# O si tienes requirements.txt:
pip install -r requirements.txt
```

---

## 🗄️ **Paso 2: Configurar Base de Datos**

### 2.1 Crear Base de Datos
```bash
# Conectar a MySQL como root
mysql -u root -p

# Crear la base de datos
CREATE DATABASE IF NOT EXISTS `livechat-ia`
DEFAULT CHARACTER SET utf8mb4
DEFAULT COLLATE utf8mb4_unicode_ci;

# Salir de MySQL
EXIT;
```

### 2.2 Ejecutar Migraciones
```bash
# Ejecutar migración principal
mysql -u root -p livechat-ia < database/migrations.sql

# Ejecutar migración de agentes
mysql -u root -p livechat-ia < database/agents_migration.sql

# Ejecutar seeds (datos iniciales)
mysql -u root -p livechat-ia < database/seeds.sql
```

### 2.3 Verificar Instalación de BD
```bash
# Verificar tablas creadas
mysql -u root -p livechat-ia -e "SHOW TABLES;"

# Verificar usuario admin creado
mysql -u root -p livechat-ia -e "SELECT username, is_admin FROM users;"
```

**Resultado esperado:**
```
+------------------+
| Tables_in_livechat-ia |
+------------------+
| agents           |
| agent_usage      |
| ai_providers     |
| history          |
| reports          |
| sessions         |
| system_config    |
| user_agent_preferences |
| users            |
+------------------+

+---------------+----------+
| username      | is_admin |
+---------------+----------+
| jscothserver  |        1 |
+---------------+----------+
```

---

## ⚙️ **Paso 3: Configurar Variables de Entorno**

### 3.1 Configurar Base de Datos
Edita el archivo `.env` con tus datos de MySQL:

```env
# Configuración de la base de datos MySQL
DB_HOST=localhost
DB_PORT=3306
DB_NAME=livechat-ia
DB_USER=root
DB_PASSWORD=tu_password_mysql_aqui

# Configuración de zona horaria
TIMEZONE=America/Los_Angeles

# Configuración general de la aplicación
APP_NAME=LiveChat-IA
APP_ENV=development
APP_DEBUG=true
APP_VERSION=1.0.0
LOG_LEVEL=INFO
```

### 3.2 Configurar API Keys de Agentes IA (Opcional)

Para usar agentes de IA externos, agrega las API keys correspondientes:

```env
# API Keys para agentes de IA
OPENAI_API_KEY=sk-tu_api_key_de_openai_aqui
ANTHROPIC_API_KEY=sk-ant-tu_api_key_de_claude_aqui
GOOGLE_API_KEY=tu_api_key_de_gemini_aqui
GROQ_API_KEY=tu_api_key_de_groq_aqui
TOGETHER_API_KEY=tu_api_key_de_together_aqui

# URLs de APIs (opcional - usar defaults si no se especifica)
OPENAI_API_URL=https://api.openai.com/v1
ANTHROPIC_API_URL=https://api.anthropic.com/v1
GOOGLE_API_URL=https://generativelanguage.googleapis.com/v1
GROQ_API_URL=https://api.groq.com/openai/v1
TOGETHER_API_URL=https://api.together.xyz/v1
OLLAMA_API_URL=http://localhost:11434
```

### 3.3 Obtener API Keys

#### **OpenAI (GPT-4, GPT-3.5)**
1. Ve a [platform.openai.com](https://platform.openai.com)
2. Crea una cuenta o inicia sesión
3. Ve a "API Keys" en el dashboard
4. Crea una nueva API key
5. Copia y pega en `OPENAI_API_KEY`

#### **Anthropic (Claude)**
1. Ve a [console.anthropic.com](https://console.anthropic.com)
2. Crea una cuenta o inicia sesión
3. Ve a "API Keys"
4. Genera una nueva API key
5. Copia y pega en `ANTHROPIC_API_KEY`

#### **Google (Gemini)**
1. Ve a [ai.google.dev](https://ai.google.dev)
2. Obtén una API key desde Google AI Studio
3. Copia y pega en `GOOGLE_API_KEY`

#### **Ollama (Local) - Opcional**
```bash
# Instalar Ollama (modelos locales gratuitos)
# Windows: Descargar desde https://ollama.com
# macOS: brew install ollama
# Linux: curl -fsSL https://ollama.com/install.sh | sh

# Ejecutar Ollama
ollama serve

# Descargar un modelo (en otra terminal)
ollama pull llama3.1
```

---

## 🏃‍♂️ **Paso 4: Ejecutar la Aplicación**

### 4.1 Verificar Estructura del Proyecto
```
LiveChat-IA/
├── main.py                 # Archivo principal
├── .env                    # Variables de entorno
├── config/                 # Configuraciones
├── components/             # Componentes UI
├── models/                 # Modelos de datos
├── agents/                 # Agentes de IA
├── database/               # Scripts de BD
├── utils/                  # Utilidades
├── logs/                   # Logs de la aplicación
└── reportes/               # Reportes generados
```

### 4.2 Ejecutar la Aplicación
```bash
# Asegúrate de estar en la carpeta del proyecto
cd LiveChat-IA

# Activar entorno virtual (si usas uno)
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Ejecutar la aplicación
python main.py
```

### 4.3 Resultado Esperado
- Se abrirá una ventana de 1200x800 píxeles
- Verás el footer animado en la parte inferior
- La aplicación iniciará en la sección "Inicio" con el chat
- En "Configuraciones" podrás gestionar agentes IA

---

## 🔐 **Paso 5: Primer Uso**

### 5.1 Configurar tu Primer Agente IA

1. **Ir a Configuraciones:**
   - Clic en "⚙️ Configuraciones" en la barra de navegación

2. **Crear Nuevo Agente:**
   - Clic en "➕ Nuevo"
   - Completa el formulario:
     - **Nombre:** Mi GPT-4o
     - **Proveedor:** openai
     - **Modelo:** gpt-4o-mini
     - **API Key:** tu_api_key_de_openai
     - **Descripción:** Mi agente personal para chat

3. **Probar Conexión:**
   - Clic en "🔌 Probar Conexión"
   - Debe mostrar "✅ Conexión exitosa"

4. **Guardar Agente:**
   - Clic en "💾 Guardar Agente"

### 5.2 Usar el Chat

1. **Ir a Inicio:**
   - Clic en "🏠 Inicio"

2. **Seleccionar Agente:**
   - En el dropdown "🤖 Agente:" selecciona tu agente creado
   - El estado debe cambiar a "🟢 gpt-4o-mini - Listo"

3. **Chatear:**
   - Escribe un mensaje y presiona Enter o clic en "Enviar 📤"
   - El agente responderá usando la API configurada

---

## 🔧 **Solución de Problemas**

### ❌ **Error de Conexión a MySQL**
```
mysql.connector.errors.DatabaseError: 2003 (HY000): Can't connect to MySQL server
```
**Solución:**
1. Verificar que MySQL esté ejecutándose
2. Verificar credenciales en `.env`
3. Verificar puerto (por defecto 3306)

### ❌ **Error de Módulos Python**
```
ModuleNotFoundError: No module named 'customtkinter'
```
**Solución:**
```bash
pip install customtkinter mysql-connector-python bcrypt python-dotenv requests
```

### ❌ **Error de API Key**
```
Error: 401 Unauthorized
```
**Solución:**
1. Verificar que la API key esté correcta en `.env`
2. Verificar que la API key tenga créditos/cuota disponible
3. Probar la conexión desde el panel de configuraciones

### ❌ **Base de Datos Vacía**
Si no aparecen agentes en el dropdown:
```bash
# Re-ejecutar seeds
mysql -u root -p livechat-ia < database/agents_migration.sql
```

---

## 📊 **Funcionalidades Disponibles**

### 🏠 **Sección Inicio**
- ✅ Chat interactivo con agentes IA
- ✅ Selector de agentes en tiempo real
- ✅ Historial de conversaciones
- ✅ Estado de conexión del agente

### ⚙️ **Sección Configuraciones**
- ✅ Gestión completa de agentes IA
- ✅ Soporte para múltiples proveedores
- ✅ Prueba de conexión en tiempo real
- ✅ Configuración de parámetros avanzados

### 👨‍💼 **Sección Administración**
- 🔄 Panel de monitoreo (en desarrollo)
- 🔄 Estadísticas de uso (en desarrollo)
- 🔄 Gestión de usuarios (en desarrollo)

---

## 📝 **Notas Adicionales**

### **Proveedores Soportados:**
- **OpenAI:** GPT-4o, GPT-4o-mini, GPT-3.5-turbo
- **Anthropic:** Claude 3.5 Sonnet, Claude 3 Opus, Claude 3 Haiku
- **Google:** Gemini 1.5 Pro, Gemini 1.5 Flash
- **Ollama:** Modelos locales (llama3.1, codestral, etc.)
- **Groq:** Llama 3.1 70B, Mixtral, Gemma
- **Together AI:** Meta-Llama, Qwen, DeepSeek

### **Costos Estimados:**
- **OpenAI GPT-4o-mini:** ~$0.15 por 1K tokens
- **Claude 3.5 Sonnet:** ~$3.00 por 1K tokens
- **Gemini 1.5 Flash:** ~$0.075 por 1K tokens
- **Ollama:** Gratuito (local)

### **Logs y Reportes:**
- Los logs se guardan en la carpeta `logs/`
- Los reportes se generan automáticamente en `reportes/`
- El sistema registra todas las interacciones para análisis

---

## 🆘 **Soporte**

Si tienes problemas:

1. **Revisar logs:** Carpeta `logs/` para errores detallados
2. **Verificar configuración:** Archivo `.env` con datos correctos
3. **Probar conexiones:** Usar panel de configuraciones para probar agentes
4. **Base de datos:** Verificar que todas las tablas estén creadas

**¡Listo! Ya tienes LiveChat-IA funcionando completamente.** 🎉