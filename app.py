import streamlit as st
import speech_recognition as sr
# AudioSegment e pydub ainda são importados, mas não são usados para conversão de MP3 para WAV
# Isso evita a necessidade do FFmpeg.
from pydub import AudioSegment # Necessário para o AudioSegment
import os
from dotenv import load_dotenv
import google.generativeai as genai # Importa a biblioteca Google Gemini AI

# --- Configurações Iniciais ---
load_dotenv()

# st.set_page_config() DEVE SER A PRIMEIRA FUNÇÃO STREAMLIT A SER CHAMADA.
st.set_page_config(page_title="Transcrição e Tradução de Áudio", layout="wide")

# --- CSS para o GIF de Fundo e Estilização Mágica Lilás ---
gif_url_magic = "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExOHcwNmgxZzkxamdsOTc5MGRrMzhrejl3ZmlmNG5icGZxOW5xajVhOSZlcD1MVjEwOV82NDQ5MjY0NzAmY3Q9Zw/cgW5iwX0e37qg/giphy.gif"

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Baloo+2:wght@400;600;800&family=Poppins:wght@300;500;700&display=swap');

    /* Fundo mágico com overlay - OPACIDADE REDUZIDA */
    .stApp {{
        background: linear-gradient(rgba(240, 240, 255, 0.6), rgba(240, 240, 255, 0.6)), /* Opacidade de 0.6 (60%) */
                     url('{gif_url_magic}') no-repeat center center fixed;
        background-size: cover;
        font-family: 'Poppins', sans-serif;
        min-height: 100vh;
        color: #333333; /* Cor padrão do texto para contraste */
    }}

    /* Efeito de brilho global (adaptação do .magic-container::before) */
    .stApp::before {{
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.2) 0%, transparent 70%);
        animation: rotate 15s linear infinite;
        z-index: -1;
    }}

    @keyframes rotate {{
        0% {{ transform: rotate(0deg); }}
        100% {{ transform: rotate(360deg); }}
    }}

    /* Títulos principais (h1, h2, h3) */
    h1, h2, h3 {{
        font-family: 'Baloo 2', cursive !important;
        color: #8A2BE2 !important; /* Azul-violeta/Lilas vibrante */
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 800; /* Mais negrito */
        position: relative;
        display: block; /* Para o after funcionar corretamente */
        width: 100%;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1); /* Sombra para destaque */
    }}

    h1::after {{ /* Sublinhado animado para h1 */
        content: '';
        position: absolute;
        bottom: -10px;
        left: 25%;
        width: 50%;
        height: 4px;
        background: linear-gradient(90deg, transparent, #9370DB, transparent); /* Lilás médio */
        animation: titleUnderline 3s ease-in-out infinite;
    }}

    @keyframes titleUnderline {{
        0%, 100% {{ transform: scaleX(0.8); opacity: 0.7; }}
        50% {{ transform: scaleX(1.2); opacity: 1; }}
    }}

    /* Subtítulos (st.markdown que você usa) */
    .stApp > div > div > .stMarkdown > p {{
        font-size: 1.2rem; /* Tamanho ajustado para o subtítulo */
        color: #9370DB !important; /* Lilás médio */
        text-align: center;
        margin-bottom: 2rem;
        font-family: 'Poppins', sans-serif;
        animation: pulse 2s ease-in-out infinite;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.05); /* Sombra mais sutil */
    }}

    @keyframes pulse {{
        0%, 100% {{ transform: scale(1); }}
        50% {{ transform: scale(1.02); }} /* Pulsar mais sutil */
    }}

    /* Estilo para input de arquivo e selectbox (labels) */
    .stFileUploader label span, .stSelectbox > div > label, .stTextInput label {{
        color: #4B0082 !important; /* Indigo para labels */
        font-weight: 600 !important;
        font-size: 1.1em;
        font-family: 'Poppins', sans-serif;
        text-shadow: 0.5px 0.5px 1px rgba(0, 0, 0, 0.03); /* Sombra bem leve */
    }}

    /* Área de texto e outros inputs */
    .stFileUploader, .stSelectbox, .stTextInput {{
        background-color: rgba(255, 255, 255, 0.9) !important; /* Fundo quase branco para inputs */
        border: 2px solid #D8BFD8 !important; /* Thistle (lilás bem claro) */
        border-radius: 15px !important; /* Mais arredondado */
        padding: 10px !important;
        box-shadow: 0 5px 20px rgba(138, 43, 226, 0.15) !important; /* Sombra lilás */
        transition: all 0.3s !important;
        font-family: 'Poppins', sans-serif;
        color: #444444 !important; /* Cor do texto dentro do input */
    }}

    .stFileUploader:hover, .stSelectbox:hover, .stTextInput:hover {{
        border-color: #8A2BE2 !important; /* Azul-violeta no hover */
        box-shadow: 0 5px 25px rgba(138, 43, 226, 0.3) !important;
    }}
    /* Cor do texto dentro do selectbox */
    .stSelectbox div[data-baseweb="select"] div[role="button"] span {{
        color: #444444 !important;
    }}

    /* Botão de envio */
    .stButton > button {{
        background: linear-gradient(45deg, #8A2BE2, #9370DB) !important; /* Gradiente lilás */
        color: white !important;
        border: none !important;
        padding: 14px 30px !important;
        border-radius: 30px !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        transition: all 0.3s ease-in-out !important;
        width: auto !important; /* Ajusta a largura automaticamente */
        margin: 20px auto; /* Centraliza o botão */
        display: block; /* Para margin: auto funcionar */
        box-shadow: 0 5px 25px rgba(138, 43, 226, 0.3) !important;
        position: relative;
        overflow: hidden;
    }}

    .stButton > button:hover {{
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 35px rgba(138, 43, 226, 0.6) !important;
    }}

    .stButton > button::after {{ /* Efeito de brilho no botão */
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: rgba(255, 255, 255, 0.15); /* Mais visível */
        transform: rotate(45deg);
        animation: buttonShine 3s ease-in-out infinite;
    }}

    @keyframes buttonShine {{
        0% {{ left: -100%; }}
        20%, 100% {{ left: 100%; }}
    }}

    /* Estilo para expanders (transcrição/tradução) */
    .streamlit-expanderHeader {{
        background-color: rgba(255, 255, 255, 0.95) !important; /* Fundo branco semi-transparente */
        color: #8A2BE2 !important; /* Azul-violeta para o texto do cabeçalho */
        border-radius: 15px !important; /* Mais arredondado */
        padding: 10px 20px !important;
        margin-top: 20px;
        border: 2px solid #D8BFD8 !important; /* Lilás claro para borda */
        box-shadow: 0 5px 20px rgba(138, 43, 226, 0.15);
        font-family: 'Poppins', sans-serif;
        font-weight: 700;
        font-size: 1.1em;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.05); /* Sombra para o cabeçalho do expander */
    }}

    .streamlit-expanderContent {{
        background-color: rgba(255, 255, 255, 0.98) !important; /* Fundo branco mais opaco */
        padding: 25px !important;
        border-radius: 0 0 15px 15px !important;
        border-top: none !important; /* Remove linha divisória */
        box-shadow: 0 8px 25px rgba(138, 43, 226, 0.2);
        color: #555555 !important; /* Cinza escuro para o texto */
        font-family: 'Poppins', sans-serif;
        line-height: 1.7;
        font-size: 1.05em;
        animation: fadeInText 0.8s ease-out; /* Animação para o texto do conteúdo */
    }}

    @keyframes fadeInText {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    /* Mensagens de feedback (info, success, warning, error) */
    .stAlert {{
        background-color: rgba(255, 255, 255, 0.95) !important; /* Fundo branco para alertas */
        color: #444444 !important; /* Cor padrão para texto do alerta */
        border-radius: 10px !important;
        padding: 15px 20px !important;
        margin-bottom: 20px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        font-family: 'Poppins', sans-serif;
        font-weight: 500;
        text-shadow: 0.5px 0.5px 1px rgba(0, 0, 0, 0.02); /* Sombra bem leve para alertas */
    }}
    .stAlert.info {{ border-left: 7px solid #8A2BE2; }} /* Azul-violeta para info */
    .stAlert.success {{ border-left: 7px solid #BA55D3; }} /* Medium Orchid para success */
    .stAlert.warning {{ border-left: 7px solid #FFD700; }} /* Dourado para warning */
    .stAlert.error {{ border-left: 7px solid #DC143C; }} /* Carmesim para error */

    /* Fundo da barra lateral */
    .css-1d391kg {{ /* Esta é uma classe gerada pelo Streamlit, pode mudar em versões futuras */
        background-color: rgba(255, 255, 255, 0.98) !important; /* Fundo branco quase opaco para sidebar */
        border-right: 1px solid #DDA0DD !important; /* Plum (lilás suave) */
        box-shadow: 0 5px 25px rgba(138, 43, 226, 0.2);
    }}
    .css-1d391kg h2, .css-1d391kg h3, .css-1d391kg label {{ /* Ajusta cores na sidebar */
        color: #4B0082 !important; /* Indigo para títulos e labels na sidebar */
        text-shadow: 0.5px 0.5px 1px rgba(0, 0, 0, 0.03); /* Sombra para sidebar */
    }}
    .css-1d391kg .stMarkdown p {{
        color: #555555 !important; /* Cinza para o texto do rodapé na sidebar */
    }}

    /* Estilo para o player de áudio */
    .stAudio {{
        filter: none;
        background-color: rgba(255, 255, 255, 0.9);
        border-radius: 10px;
        padding: 8px;
        box-shadow: 0 3px 10px rgba(0,0,0,0.1);
    }}

    /* Estilo para a roda de spinner */
    .stSpinner > div > div {{
        border-top-color: #8A2BE2 !important; /* Azul-violeta para o spinner */
    }}

    /* Efeito de brilho para o texto do spinner */
    .stSpinner > div > span {{
        color: #4B0082 !important; /* Indigo para o texto do spinner */
        text-shadow: 0 0 5px rgba(138, 43, 226, 0.5);
        font-family: 'Poppins', sans-serif;
        font-weight: 600;
    }}

    /* Ajustes para o texto do st.markdown de rodapé geral */
    .stMarkdown p:last-child {{
        color: #000000 !important;
        font-family: 'Poppins', sans-serif;
        font-weight: 400;
        font-size: 0.85em;
        text-align: center;
        margin-top: 30px;
    }}

    </style>
    """,
    unsafe_allow_html=True
)

# --- Cabeçalho da Aplicação ---
st.title("🗣️💻🤖 Transcrição e Tradução de Áudio com IA")
st.markdown("Transforme áudios em texto e traduza para diversos idiomas usando o poder da inteligência artificial.")

# --- Configuração da API Gemini ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)

        # Tentar encontrar um modelo de texto adequado e atualizado
        available_models = []
        for m in genai.list_models():
            # Verifica se o modelo tem a capacidade de gerar conteúdo (texto)
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)

        MODEL_NAME = None # Inicializa com None

        # Ordem de preferência para modelos de texto, priorizando os mais recentes e estáveis
        # Desencorajando modelos vision 'latest' se houver um de texto puro
        preferred_models = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']

        # Encontra o primeiro modelo preferido disponível
        for p_model_suffix in preferred_models:
            # Verifica se o modelo preferido está na lista de modelos disponíveis
            # Lida com o prefixo 'models/' e o sufixo '-latest' se necessário para a busca
            if f'models/{p_model_suffix}' in available_models:
                MODEL_NAME = p_model_suffix
                break
            # Caso o modelo esteja disponível sem o prefixo 'models/'
            elif p_model_suffix in available_models:
                MODEL_NAME = p_model_suffix
                break
            # Verifica por versões '-latest' dos modelos preferidos, mas com menor prioridade
            elif f'models/{p_model_suffix}-latest' in available_models:
                MODEL_NAME = f'{p_model_suffix}-latest'
                break


        if MODEL_NAME:
            # Se o modelo encontrado for um "vision-latest" e não um dos modelos de texto preferidos, avisar
            if "vision-latest" in MODEL_NAME and not any(p in MODEL_NAME for p in ['gemini-1.5-flash', 'gemini-1.5-pro']):
                 st.warning(f"⚠️ O modelo `{MODEL_NAME}` foi selecionado, mas ele é uma versão 'vision' ou está sendo depreciado. "
                            "Para melhor performance e longevidade, procure por `gemini-1.5-flash` ou `gemini-1.5-pro` em sua região.")

            # Se o modelo selecionado for gemini-pro (antigo), também avisa
            elif MODEL_NAME == 'gemini-pro':
                st.warning("⚠️ O modelo 'gemini-pro' está sendo usado, mas ele será depreciado em breve. "
                           "Considere mudar para `gemini-1.5-flash` ou `gemini-1.5-pro` para maior longevidade e recursos.")

            model = genai.GenerativeModel(MODEL_NAME)
            st.success(f"API Gemini configurada com sucesso. Usando o modelo: `{MODEL_NAME}`.")
        else:
            st.error("❌ Nenhum modelo da API Gemini com capacidade de 'generateContent' foi encontrado. "
                     "Verifique as permissões da sua API Key ou a disponibilidade dos modelos na sua região. "
                     "Modelos de texto preferidos não disponíveis: " + ", ".join(preferred_models))
            st.stop()

    except Exception as e:
        st.error(f"❌ Erro ao configurar a API Gemini. Verifique sua chave ou conexão: {e}")
        st.stop()
else:
    st.error("🔑 A chave da API Gemini não foi encontrada. Certifique-se de configurar a variável de ambiente `GEMINI_API_KEY` "
             "no seu arquivo `.env` (localmente) ou nas 'Secrets' (na nuvem).")
    st.stop()

# --- Barra Lateral para Configurações ---
st.sidebar.header("⚙️ Configurações")

# Seleção de Idioma para Tradução movida para a barra lateral
st.sidebar.markdown("---")
st.sidebar.subheader("🌍 Idioma de Destino")
languages = {
    "Português": "pt",
    "Inglês": "en",
    "Espanhol": "es",
    "Francês": "fr",
    "Alemão": "de",
    "Italiano": "it",
    "Japonês": "ja",
    "Chinês (Simplificado)": "zh-CN",
    "Hindi": "hi",
    "Russo": "ru",
    "Árabe": "ar"
}
target_language_name = st.sidebar.selectbox(
    "Selecione o idioma para a tradução:",
    list(languages.keys()),
    index=0 # Define 'Português' como padrão
)
target_language_code = languages[target_language_name]
st.sidebar.markdown("---")


# --- Área Principal de Upload ---
st.subheader("⬆️ Faça o Upload do seu Áudio")
# Agora aceita SOMENTE arquivos WAV, eliminando a necessidade do FFmpeg.
uploaded_file = st.file_uploader("Selecione um arquivo de áudio WAV (Max: 25MB para SpeechRecognition)", type=["wav"])

if uploaded_file is not None:
    st.audio(uploaded_file, format="audio/wav")

    # Salva o arquivo temporariamente. Já é WAV, então não precisa de conversão.
    temp_wav_path = "temp_audio.wav"

    with open(temp_wav_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    if st.button("🚀 Processar Áudio"):
        with st.spinner("⏳ Processando áudio... A precisão da transcrição pode variar."):
            transcribed_text = ""
            translated_text = ""
            try:
                # 1. REMOVEMOS A CONVERSÃO DE MP3 PARA WAV (não é mais necessária)
                # O arquivo já é esperado como WAV.

                # 2. Transcrição com SpeechRecognition
                r = sr.Recognizer()
                with sr.AudioFile(temp_wav_path) as source:
                    r.adjust_for_ambient_noise(source) # Ajusta para o ruído do ambiente
                    audio_listened = r.record(source)

                try:
                    # Tenta reconhecer o áudio em português do Brasil
                    transcribed_text = r.recognize_google(audio_listened, language="pt-BR")
                    st.subheader("📝 Transcrição Original:")
                    # Exibe a transcrição em um expander para organização
                    with st.expander("Ver Transcrição"):
                        st.success(transcribed_text)
                except sr.UnknownValueError:
                    st.warning("⚠️ Não foi possível entender o áudio. A transcrição pode estar vazia ou incorreta.")
                    transcribed_text = "NÃO FOI POSSÍVEL TRANSCREVER O ÁUDIO" # Define um placeholder
                    with st.expander("Ver Transcrição"):
                         st.info(transcribed_text)
                except sr.RequestError as e:
                    st.error(f"❌ Erro no serviço de reconhecimento de fala; verifique sua conexão com a internet ou as configurações: {e}")
                    transcribed_text = "ERRO NA TRANSCRIÇÃO" # Define um placeholder
                    with st.expander("Ver Transcrição"):
                         st.info(transcribed_text)


                # 3. Tradução com Gemini API
                if transcribed_text and GEMINI_API_KEY and \
                   transcribed_text not in ["NÃO FOI POSSÍVEL TRANSCREVER O ÁUDIO", "ERRO NA TRANSCRIÇÃO"]:
                    st.subheader(f"🌐 Tradução para {target_language_name}:")
                    try:
                        prompt = f"Traduza o seguinte texto para o idioma {target_language_name}:\n\n{transcribed_text}"
                        response = model.generate_content(prompt)
                        translated_text = response.text
                        # Exibe a tradução em um expander
                        with st.expander("Ver Tradução"):
                            st.success(translated_text)
                    except Exception as e:
                        st.error(f"❌ Erro ao traduzir o texto com a API Gemini: {e}")
                        translated_text = "ERRO NA TRADUÇÃO"
                        with st.expander("Ver Tradução"):
                            st.warning(translated_text)
                elif not transcribed_text or transcribed_text in ["NÃO FOI POSSÍVEL TRANSCREVER O ÁUDIO", "ERRO NA TRANSCRIÇÃO"]:
                    st.info("ℹ️ Não há texto válido para traduzir, pois a transcrição falhou.")
                else:
                    st.info("ℹ️ Tradução não realizada devido a problemas na transcrição ou falta da chave da API Gemini.")


            except Exception as e:
                st.error(f"🔥 Ocorreu um erro inesperado durante o processamento do áudio: {e}")
            finally:
                # Limpa arquivo temporário (apenas o WAV)
                if os.path.exists(temp_wav_path):
                    os.remove(temp_wav_path)
else:
    st.info("👆 Por favor, faça upload de um arquivo WAV para começar a transcrever e traduzir.")

st.markdown("---")
st.markdown("Projeto desenvolvido para aprimorar habilidades em desenvolvimento web, processamento de áudio e IA.")
st.markdown("Criado com ❤️")