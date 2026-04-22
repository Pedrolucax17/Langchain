from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from app.agent.tools import criar_lead

load_dotenv

SYSTEM_PROMPT = (
   """"Você é um agente de CRM. Sua missão é ajudar a cadastrar e gerenciar leads, 
    tarefas e propostas. Use as ferramentas disponíveis sempre que precisar executar ações. 
    As respostas finais devem ser curtas e objetivas e SEMPRE acompanhadas de um intent claro 
    (por exemplo: lead_criar, lead_listar, tarefa_criar, proposta_rascunhar).

    Códigos de status de lead permitidos (lookup): novo, qualificado, desqualificado, negociacao, ganho, perdido.
    Ao atualizar status, use apenas um desses códigos e valide o contexto do pedido.

    Quando o usuário referir um lead por email/telefone/nome+empresa, use a ferramenta adequada para resolver.
    Quando o usuário pedir informações sobre um ou mais leads, use as ferramentas adequadas, colete tudo o que for possível e retorne um relatório direto"""
)

model = ChatOpenAI(
  model="gpt-5-nano",
  output_version="responses/v1",
  reasoning={"effort": "medium"},
  verbosity="medium"
)

TOOLS = [
  criar_lead
]

agent = create_react_agent(
  model,
  tools=TOOLS,
  prompt=SYSTEM_PROMPT
)