from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory

from agent.message_history import get_message_history
from agent.tools import create_pandas_ai_tool
from database.database_functions import add_message_to_existing_session, load_session_messages
from agent.llm import agent_llm


def define_and_return_the_agent_executor(dataframe) -> AgentExecutor:
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", """You are a data analyst and a helpful assistant. Use the tool that you have to retrieve relevant context.
            If you are not able to retrieve relevant information to answer the question then say that you don't know the answer.
            
            If the tool returns a file path or URL (e.g. to an image), your response must be exactly that string—no Markdown, no additional text, no commentary, no formatting. Do not wrap the result in `![...]()` or backticks or anything else. Just output the raw string returned by the tool.
            """),
            ("placeholder", "{history}"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}")
        ]
    )

    tools = [create_pandas_ai_tool(dataframe)]
    agent = create_tool_calling_agent(agent_llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    return agent_executor


def create_agent(dataframe) -> RunnableWithMessageHistory:
    agent_executor = define_and_return_the_agent_executor(dataframe)
    agent = RunnableWithMessageHistory(
        agent_executor,
        get_message_history,
        input_messages_key="input",
        history_messages_key="history"
    )
    return agent


def query(question: str, dataset, session_id: int) -> list:
    agent = create_agent(dataset)

    try:
        agent.invoke({"input" : question}, 
            config={"configurable" : {"session_id" : session_id}},
        )
    except Exception as e:
        print(e)
        add_message_to_existing_session(sender="User", session_id=session_id, text=question)
        add_message_to_existing_session(sender="AI", session_id=session_id, text="Sorry, I am having trouble answering this question, could you please try again?")
    
    list_of_messages = load_session_messages(session_id)
    return list_of_messages[-1][1]