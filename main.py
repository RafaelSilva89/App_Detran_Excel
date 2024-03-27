# https://api.python.langchain.com/en/latest/agents/langchain.agents.agent_types.AgentType.html
# https://python.langchain.com/docs/modules/agents/agent_types/openai_functions_agent
import os
import streamlit as st
import pandas    as pd
#from langchain.llms                              import OpenAI
#from langchain_experimental.agents               import create_pandas_dataframe_agent
#from langchain_openai                            import OpenAI
from langchain.agents.agent_types                 import AgentType
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_openai                             import ChatOpenAI
from translate                                    import Translator
from htmlTemplates                                import css, bot_template, user_template
from dotenv                                       import load_dotenv

def get_query():
    input_text = st.chat_input("Ask a question about your documents...")
    return input_text

if 'historico' not in st.session_state:
    st.session_state['historico'] = []

if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

def chat_rh(question, api_key, dataframe):
    #llm = OpenAI(api_key=api_key)
    #agent = create_pandas_dataframe_agent(llm, dataframe, verbose=True)
    #agent = create_pandas_dataframe_agent(OpenAI(temperature=0), dataframe, verbose=True) gpt-3.5-turbo-0125 - gpt-3.5-turbo-0613
    agent = create_pandas_dataframe_agent(ChatOpenAI(api_key=api_key, temperature=0, model="gpt-3.5-turbo-0125"), dataframe, verbose=True, agent_type=AgentType.OPENAI_FUNCTIONS,)
    answer = agent.run(question.upper())
    return answer

def add_to_history(question, answer):
    st.session_state['chat_history'].append({'pergunta': question, 'resposta': answer})

st.set_page_config(
    page_title="Chat Excel",
    page_icon="📊",
)

def main():
    load_dotenv()
    st.title("Chat Excel 📊")
    st.write(css, unsafe_allow_html=True)
    with st.sidebar:
        #st.sidebar.header("Configurações")

        file = st.sidebar.file_uploader("Selecionar arquivo Excel", type=['xlsx', 'xls'])
        if file:
            df = pd.read_excel(file)
        api_key = os.getenv("OPENAI_API_KEY")
        #api_key = st.sidebar.text_input("Chave da API:", "insira_sua_chave_aqui", type="password")

        st.markdown('''
                        - [Streamlit](https://streamlit.io/)
                        - [LangChain](https://python.langchain.com/)
                        - [OpenAI](https://platform.openai.com/docs/models) LLM Model
                        - [Pandas Dataframe](https://python.langchain.com/docs/integrations/toolkits/pandas)
                        ''')
        #st.write('Also check out my portfolio for amazing content [Rafael Silva](https://rafaelsilva89.github.io/portfolioProjetos/#)')

    question = get_query()

    if file is not None and api_key != "insira_sua_chave_aqui":
        if isinstance(question, str):  # Verifica se question é uma string
            try:
                answer = chat_rh(question, api_key, df)
                translator = Translator(to_lang='pt')
                translated_response = translator.translate(answer)
                add_to_history(question, translated_response)
            except Exception as e:
                st.error(f"Erro ao executar a consulta: {str(e)}")
    else:
        st.warning("Por favor, preencha todos os campos e selecione um arquivo.")

    # Exibir histórico de conversas
    for item in st.session_state['chat_history']:
        st.write(user_template.replace("{{MSG}}", item['pergunta']), unsafe_allow_html=True)
        st.write(bot_template.replace("{{MSG}}", item['resposta']), unsafe_allow_html=True)

if __name__ == "__main__":
    main()