import streamlit as st
import tempfile
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from loaders import *

st.set_page_config(
        layout =  'wide', 
        page_title = 'CamppoAI Vision')

ARQUIVOS = ['Site', 'Vídeo Youtube', 'PDF', 'CSV', 'EXCEL', 'Texto']

ASSISTENTES = ['Oraculo']

MEMORIA = ConversationBufferMemory()

MODELO = 'gpt-3.5-turbo-0125'

def carrega_arquivo(tipo_arquivo, arquivo):
    if tipo_arquivo == 'Site':
        documento = carrega_site(arquivo)
    if tipo_arquivo == 'Vídeo Youtube':
        documento = carrega_youtube(arquivo)
    if tipo_arquivo == 'PDF':
        with tempfile.NamedTemporaryFile(suffix= '.pdf', delete=False) as temp:
            temp.write(arquivo.read())
            nome_temp = temp.name
        documento = carrega_pdf(nome_temp)
    if tipo_arquivo == 'CSV':
        with tempfile.NamedTemporaryFile(suffix= '.csv', delete=False) as temp:
            temp.write(arquivo.read())
            nome_temp = temp.name
        documento = carrega_csv(nome_temp)
    if tipo_arquivo == 'EXCEL':
        with tempfile.NamedTemporaryFile(suffix= '.xlsx', delete=False) as temp:
            temp.write(arquivo.read())
            nome_temp = temp.name
        documento = carrega_xlsx(nome_temp)
    if tipo_arquivo == 'Texto':
        with tempfile.NamedTemporaryFile(suffix= '.txt', delete=False) as temp:
            temp.write(arquivo.read())
            nome_temp = temp.name
        documento = carrega_txt(nome_temp)
    return documento

def carrega_modelo(tipo_arquivo, arquivo):

    documento = carrega_arquivo(tipo_arquivo, arquivo)
    
    system_message = '''Você é um assistente amigável chamado Oráculo.
                    Você possui acesso às seguintes informações vindas 
                    de um documento {}: 

                    ####
                    {}
                    ####

                    Utilize as informações fornecidas para basear as suas respostas.

                    Sempre que houver $ na sua saída, substita por S.

                    Se a informação do documento for algo como "Just a moment...Enable JavaScript and cookies to continue" 
                    sugira ao usuário carregar novamente o Oráculo!'''.format(tipo_arquivo, documento)
    
    template = ChatPromptTemplate([
        ('system', system_message),
        ('placeholder', '{chat_history}'),
        ('user', '{input}')
    ])

    chat = ChatOpenAI(model=MODELO)

    chain = template | chat

    st.session_state['chat'] = chain    

def pagina_chat():
    st.header('CamppoAI Vision')
    st.markdown('O seu assistente "Sabe Tudo"')
    st.divider()

    chat_llm = st.session_state.get('chat')
    memoria = st.session_state.get('memoria', MEMORIA)
    for mensagem in memoria.buffer_as_messages:
        chat = st.chat_message(mensagem.type)
        chat.markdown(mensagem.content)

    input_user = st.chat_input('Fale com o Vision!')
    if input_user:
        chat = st.chat_message('human')
        chat.markdown(input_user)

        chat = st.chat_message('ai')
        resposta = chat.write_stream(chat_llm.stream({'input' : input_user,
                                                      'chat_history' : memoria.buffer_as_messages}))

        memoria.chat_memory.add_user_message(input_user)
        memoria.chat_memory.add_ai_message(resposta)
        st.session_state['memoria'] = memoria
        
def barra_lateral():
    tabs = st.tabs(['Carregamento de arquivos', 'Seleção de assistentes'])
    with tabs[0]:
        tipo = st.selectbox('Selecione o tipo de arquivo', ARQUIVOS)
        if tipo == 'Site':
            arquivo = st.text_input('Passe o link do site')
        if tipo == 'Vídeo Youtube':
            arquivo = st.text_input('Passe o link do vídeo')
        if tipo == 'PDF':
            arquivo = st.file_uploader('Faça o upload do PDF', type= ['.pdf'])#, accept_multiple_files= True)
        if tipo == 'CSV':
            arquivo = st.file_uploader('Faça o upload do CSV', type= ['.csv'])#, accept_multiple_files= True)
        if tipo == 'EXCEL':
            arquivo = st.file_uploader('Faça o upload do Excel', type= ['.xlsx'])#, accept_multiple_files= True)
        if tipo == 'Texto':
            arquivo = st.file_uploader('Faça o upload de texto', type= ['.txt'])#, accept_multiple_files= True)

    with tabs[1]:
        assistente = st.selectbox('Selecione qual assistente precisa', ASSISTENTES)

    mdl = st.button('Iniciar IA', use_container_width= True)
    if mdl:
        carrega_modelo(tipo_arquivo=tipo, arquivo=arquivo)
        
    limpa = st.button('Limpar Conversa', use_container_width= True)
    if limpa:
        st.session_state['memoria'] = MEMORIA
        st.rerun()

def main():
    pagina_chat()
    with st.sidebar:
        barra_lateral()

if __name__ == '__main__':
    main()