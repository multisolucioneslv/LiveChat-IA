# 🚀 Ejecución Rápida - LiveChat-IA

## ⚡ **Ejecutar en 3 Pasos**

### **Paso 1: Instalar Dependencias**
```bash
pip install -r requirements.txt
```

### **Paso 2: Configurar Base de Datos**
```bash
# Crear base de datos
mysql -u root -p -e "CREATE DATABASE \`livechat-ia\`"

# Ejecutar migraciones (ejecutar uno por uno)
mysql -u root -p livechat-ia < database/migrations.sql
mysql -u root -p livechat-ia < database/agents_migration.sql
mysql -u root -p livechat-ia < database/seeds.sql
```

### **Paso 3: Configurar .env**
Editar el archivo `.env` con tu contraseña de MySQL:
```env
DB_PASSWORD=tu_password_mysql_aqui
```

### **Paso 4: Ejecutar**
```bash
python main.py
```

---

## 🎯 **¡Listo para Usar!**

### **Usuario Admin Preconfigurado:**
- **Usuario**: `jscothserver`
- **Contraseña**: `72900968`

### **Agentes Preconfigurados:**
- 🤖 **GPT-4o Mini** (OpenAI)
- 🧠 **Claude 3.5 Sonnet** (Anthropic)
- 🎯 **Gemini 1.5 Flash** (Google)
- 🏠 **Llama 3.1** (Ollama - Local)
- ⚡ **Llama 3.1 70B** (Groq)

### **Estado de los Agentes:**
- ⚠️ **Sin API Key**: Los agentes aparecerán pero necesitas configurar API keys para usarlos
- 🔵 **Configurado**: Agente listo para usar
- 🟢 **Por Defecto**: Agente seleccionado automáticamente

---

## ⚙️ **Configurar API Keys (Opcional)**

### **Para usar agentes externos, configura las API keys en `.env`:**

```env
# API Keys para agentes de IA
OPENAI_API_KEY=sk-tu_api_key_de_openai_aqui
ANTHROPIC_API_KEY=sk-ant-tu_api_key_de_claude_aqui
GOOGLE_API_KEY=tu_api_key_de_gemini_aqui
```

### **O usa Ollama para agentes locales gratuitos:**
```bash
# Instalar Ollama
# Descargar desde: https://ollama.com

# Ejecutar Ollama
ollama serve

# Descargar modelo (en otra terminal)
ollama pull llama3.1
```

---

## 📋 **Funcionalidades Disponibles Sin API Keys:**

- ✅ **Interfaz completa** con footer animado
- ✅ **Navegación** entre secciones
- ✅ **Lista de agentes** preconfigurados
- ✅ **Selector de agentes** en el chat
- ✅ **Panel de configuración** de agentes
- ✅ **Mensajes informativos** sobre configuración

### **Con API Keys Configuradas:**
- 🚀 **Chat funcional** con IA real
- 📊 **Historial** de conversaciones
- 💰 **Estimación de costos**
- 📝 **Reportes** automáticos
- 🔄 **Múltiples agentes** simultáneos

---

## 🔧 **Solución Rápida de Problemas**

### ❌ **Error MySQL Connection**
```bash
# Verificar que MySQL esté ejecutándose
mysql -u root -p -e "SHOW DATABASES;"
```

### ❌ **ModuleNotFoundError**
```bash
# Reinstalar dependencias
pip install --upgrade -r requirements.txt
```

### ❌ **No aparecen agentes**
```bash
# Re-ejecutar seeds
mysql -u root -p livechat-ia < database/agents_migration.sql
```

---

## 📱 **Uso de la Aplicación**

1. **🏠 Inicio**:
   - Selecciona un agente del dropdown
   - Escribe mensajes y presiona Enter
   - Sin API key: recibirás mensajes informativos
   - Con API key: chat real con IA

2. **⚙️ Configuraciones**:
   - ➕ Crear nuevos agentes
   - ✏️ Editar agentes existentes
   - 🔌 Probar conexiones
   - 🔑 Configurar API keys

3. **👨‍💼 Administración**:
   - Panel básico (en desarrollo)
   - Estadísticas futuras

---

## 🎉 **¡Todo Listo!**

La aplicación funciona completamente sin API keys configuradas. Simplemente:

1. **Ejecuta** con `python main.py`
2. **Explora** la interfaz
3. **Configura** API keys cuando las tengas
4. **Disfruta** del chat con IA

**Tiempo total de instalación: ~5 minutos** ⏱️