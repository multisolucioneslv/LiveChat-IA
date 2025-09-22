# 🤖 LiveChat-IA

**Sistema de Chat Inteligente con Múltiples Agentes de IA**

Una aplicación de escritorio moderna desarrollada en Python con CustomTkinter que permite chatear con diferentes proveedores de IA como OpenAI, Claude, Gemini, Groq y Ollama.

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![License](https://img.shields.io/badge/license-MIT-yellow.svg)

## ✨ **Características Principales**

### 🎯 **Interfaz Moderna**
- **Ventana 1200x800** con diseño ejecutivo
- **Footer animado** con efecto marquesina
- **Navegación intuitiva** con 3 secciones principales
- **Selector de agentes** dinámico en tiempo real

### 🤖 **Múltiples Agentes de IA**
- **OpenAI**: GPT-4o, GPT-4o-mini, GPT-3.5-turbo
- **Anthropic**: Claude 3.5 Sonnet, Claude 3 Opus, Claude 3 Haiku
- **Google**: Gemini 1.5 Pro, Gemini 1.5 Flash
- **Groq**: Llama 3.1 70B, Mixtral 8x7B (Ultra rápido)
- **Ollama**: Modelos locales gratuitos (Llama, CodeStral, etc.)

### 🗄️ **Base de Datos Completa**
- **MySQL** con 9 tablas optimizadas
- **Historial** completo de conversaciones
- **Estadísticas** de uso y costos
- **Gestión de usuarios** y sesiones

### 📊 **Funcionalidades Avanzadas**
- **Configuración visual** de agentes
- **Prueba de conexión** en tiempo real
- **Estimación de costos** por interacción
- **Reportes automáticos** en Markdown
- **Logs detallados** para debugging

## 🚀 **Instalación Rápida**

### **Paso 1: Requisitos**
```bash
# Python 3.8+ y MySQL 8.0+
pip install -r requirements.txt
```

### **Paso 2: Base de Datos**
```bash
# Crear base de datos
mysql -u root -p -e "CREATE DATABASE \`livechat-ia\`"

# Ejecutar migraciones
mysql -u root -p livechat-ia < database/migrations.sql
mysql -u root -p livechat-ia < database/agents_migration.sql
mysql -u root -p livechat-ia < database/seeds.sql
```

### **Paso 3: Configuración**
Editar `.env`:
```env
DB_PASSWORD=tu_password_mysql

# API Keys (opcional)
OPENAI_API_KEY=sk-tu_key_aqui
ANTHROPIC_API_KEY=sk-ant-tu_key_aqui
GOOGLE_API_KEY=tu_key_aqui
GROQ_API_KEY=tu_key_aqui
```

### **Paso 4: Ejecutar**
```bash
python main.py
```

## 📱 **Uso de la Aplicación**

### **🏠 Sección Inicio**
- **Chat interactivo** con agentes de IA
- **Selector de agentes** con iconos por proveedor
- **Estados visuales**: 🟢 Listo, ⚠️ Sin API Key, 🏠 Local
- **Historial automático** de conversaciones

### **⚙️ Sección Configuraciones**
- **Gestión completa** de agentes IA
- **Formularios intuitivos** para crear/editar agentes
- **Prueba de conexión** con validación en tiempo real
- **Configuración avanzada** (temperatura, tokens, etc.)

### **👨‍💼 Sección Administración**
- **Panel de monitoreo** (en desarrollo)
- **Estadísticas de uso** y costos
- **Gestión de usuarios** del sistema

## 🔑 **Proveedores Soportados**

| Proveedor | Icono | Modelos | Costo Aprox. | Velocidad |
|-----------|-------|---------|--------------|-----------|
| **OpenAI** | 🤖 | GPT-4o, GPT-4o-mini | $0.15/1K tokens | Media |
| **Anthropic** | 🧠 | Claude 3.5 Sonnet | $3.00/1K tokens | Media |
| **Google** | 🎯 | Gemini 1.5 Pro/Flash | $0.075/1K tokens | Rápida |
| **Groq** | ⚡ | Llama 3.1 70B | $0.59/1K tokens | Ultra rápida |
| **Ollama** | 🏠 | Llama, CodeStral | Gratuito | Variable |

## 🛠️ **Arquitectura Técnica**

### **Patrón MVC**
```
LiveChat-IA/
├── main.py              # Punto de entrada
├── config/              # Configuraciones
├── models/              # Modelos de datos
├── views/               # Vistas (no usado en desktop)
├── controllers/         # Controladores
├── components/          # Componentes UI reutilizables
├── agents/              # Implementaciones de agentes IA
├── utils/               # Utilidades y helpers
└── database/            # Scripts de BD y migraciones
```

### **Componentes Clave**
- **AgentFactory**: Patrón Factory para crear agentes
- **ChatInterface**: Interfaz principal de chat
- **AgentModel**: Gestión de agentes en BD
- **BaseAgent**: Clase abstracta para agentes

## 📊 **Base de Datos**

### **Tablas Principales**
- `users` - Gestión de usuarios
- `sessions` - Sesiones de chat
- `history` - Historial de interacciones
- `agents` - Configuración de agentes IA
- `agent_usage` - Estadísticas y costos
- `reports` - Metadatos de reportes

### **Usuario Admin Predeterminado**
- **Usuario**: `jscothserver`
- **Contraseña**: `72900968`

## 🔧 **Configuración Avanzada**

### **Variables de Entorno**
```env
# Base de datos
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=tu_password
DB_NAME=livechat-ia

# APIs de IA
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
GROQ_API_KEY=gsk_...

# URLs personalizadas (opcional)
OPENAI_API_URL=https://api.openai.com/v1
GROQ_API_URL=https://api.groq.com/openai/v1
```

### **Ollama (Modelos Locales)**
```bash
# Instalar Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Ejecutar servicio
ollama serve

# Descargar modelo
ollama pull llama3.1
```

## 🐛 **Solución de Problemas**

### **Error de Conexión MySQL**
```bash
# Verificar servicio
sudo systemctl status mysql

# Verificar conexión
mysql -u root -p -e "SHOW DATABASES;"
```

### **Error de Módulos Python**
```bash
# Reinstalar dependencias
pip install --upgrade -r requirements.txt
```

### **Error de API Keys**
- Verificar API keys en `.env`
- Comprobar cuotas en los dashboards de los proveedores
- Usar función "Probar Conexión" en Configuraciones

## 📝 **Desarrollo**

### **Agregar Nuevo Agente**
1. Crear `nuevo_agent.py` heredando de `BaseAgent`
2. Implementar métodos abstractos requeridos
3. Registrar en `AgentFactory.AGENT_CLASSES`
4. Agregar icono en `get_provider_icon()`

### **Estructura de Agente**
```python
class NuevoAgent(BaseAgent):
    def get_response(self, message: str) -> str:
        # Implementar llamada a API
        pass

    def test_connection(self) -> Dict[str, Any]:
        # Implementar prueba de conexión
        pass

    def get_available_models(self) -> List[str]:
        # Retornar modelos disponibles
        pass
```

## 📈 **Roadmap**

### **Versión 1.1**
- [ ] Soporte para Together AI
- [ ] Chat con archivos (RAG)
- [ ] Exportar conversaciones
- [ ] Temas visuales personalizables

### **Versión 1.2**
- [ ] API REST para integración
- [ ] Plugin system para agentes
- [ ] Modo multi-usuario
- [ ] Dashboard web opcional

## 🤝 **Contribuir**

1. **Fork** el repositorio
2. **Crear** rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. **Commit** cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. **Push** a la rama (`git push origin feature/nueva-funcionalidad`)
5. **Crear** Pull Request

## 📄 **Licencia**

Este proyecto está bajo la licencia MIT. Ver `LICENSE` para más detalles.

## 🎯 **Autor**

**Multisoluciones IA**
- GitHub: [@multisolucioneslv](https://github.com/multisolucioneslv)
- Proyecto: [LiveChat-IA](https://github.com/multisolucioneslv/LiveChat-IA)

---

### 🌟 **¡Dale una estrella si te gusta el proyecto!**

**LiveChat-IA** - La mejor solución para tus necesidades empresariales con IA