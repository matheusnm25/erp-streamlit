import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns

# Interface Streamlit
def main():
    st.title("ERP Financeiro com Streamlit")
    
    menu = ["Clientes", "Contas a Pagar", "Contas a Receber", "Lançamentos", "Relatórios"]
    choice = st.sidebar.selectbox("Selecione uma opção", menu)
    conn = sqlite3.connect("erp_finance.db", detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()
    
    # Obter dados de lançamentos para os gráficos por dia
    df_dia = pd.read_sql_query("SELECT strftime('%Y-%m-%d', data) as periodo, tipo, SUM(valor) as total FROM lancamentos GROUP BY periodo, tipo", conn)
    df_pivot_dia = df_dia.pivot(index="periodo", columns="tipo", values="total").fillna(0) if not df_dia.empty else None
    
    if choice == "Clientes":
        st.subheader("Cadastro de Clientes")
        df_clientes = pd.read_sql_query("SELECT * FROM clientes", conn)
        st.dataframe(df_clientes)
        
    elif choice == "Contas a Pagar":
        st.subheader("Contas a Pagar")
        df_pagar = pd.read_sql_query("SELECT * FROM contas_pagar", conn)
        st.dataframe(df_pagar)
        
    elif choice == "Contas a Receber":
        st.subheader("Contas a Receber")
        df_receber = pd.read_sql_query("SELECT * FROM contas_receber", conn)
        st.dataframe(df_receber)
        
    elif choice == "Lançamentos":
        st.subheader("Lançamentos Financeiros")
        df_lancamentos = pd.read_sql_query("SELECT * FROM lancamentos", conn)
        st.dataframe(df_lancamentos)
    
    # Gráfico de Receita e Despesa por Dia
    st.subheader("Comparação Receita x Despesa (Diária)")
    if df_pivot_dia is not None:
        fig, ax = plt.subplots(figsize=(10, 5))
        df_pivot_dia.plot(kind='bar', ax=ax)
        ax.set_title("Receita e Despesa por Dia")
        ax.set_xlabel("Dia")
        ax.set_ylabel("Valor")
        ax.legend(title="Tipo")
        st.pyplot(fig)
    else:
        st.warning("Não há dados disponíveis para exibir o gráfico diário.")
    
    # Gráfico de Pizza para Principais Fornecedores
    st.subheader("Distribuição dos Valores Devidos por Fornecedor")
    df_fornecedores = pd.read_sql_query("SELECT fornecedor, SUM(valor) as total FROM contas_pagar GROUP BY fornecedor ORDER BY total DESC LIMIT 10", conn)
    
    if not df_fornecedores.empty:
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.pie(df_fornecedores["total"], labels=df_fornecedores["fornecedor"], autopct='%1.1f%%', startangle=140)
        ax.set_title("Principais Fornecedores e Valores Devidos")
        st.pyplot(fig)
    else:
        st.warning("Não há dados disponíveis para exibir o gráfico de fornecedores.")
    
    # Gráfico de Barras - Contas Pendentes vs Pagas/Recebidas
    st.subheader("Contas Pendentes vs Pagas/Recebidas")
    df_status = pd.read_sql_query("""
        SELECT status, SUM(valor) as total FROM (
            SELECT status, valor FROM contas_pagar 
            UNION ALL 
            SELECT status, valor FROM contas_receber
        ) GROUP BY status
    """, conn)
    
    if not df_status.empty:
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.barplot(x="status", y="total", data=df_status, ax=ax)
        ax.set_title("Total de Contas Pendentes vs Pagas/Recebidas")
        ax.set_xlabel("Status")
        ax.set_ylabel("Valor Total")
        st.pyplot(fig)
    else:
        st.warning("Não há dados disponíveis para exibir o gráfico de status das contas.")
    
    # Gráfico de Barras - Clientes que mais geram receita
    st.subheader("Clientes que Mais Geram Receita")
    df_clientes_receita = pd.read_sql_query("""
        SELECT c.nome, SUM(cr.valor) as total FROM contas_receber cr
        JOIN clientes c ON cr.cliente_id = c.id
        WHERE cr.status = 'Recebido'
        GROUP BY c.nome ORDER BY total DESC LIMIT 10
    """, conn)
    
    if not df_clientes_receita.empty:
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(x="total", y="nome", data=df_clientes_receita, ax=ax)
        ax.set_title("Top 10 Clientes por Receita")
        ax.set_xlabel("Valor Total Recebido")
        ax.set_ylabel("Cliente")
        st.pyplot(fig)
    else:
        st.warning("Não há dados disponíveis para exibir o gráfico de clientes.")
    
    # Comparação entre total de receitas e despesas do mês atual
    st.subheader("Receitas vs Despesas do Mês Atual")
    df_mes_atual = pd.read_sql_query("""
        SELECT tipo, SUM(valor) as total FROM lancamentos 
        WHERE strftime('%Y-%m', data) = strftime('%Y-%m', 'now') 
        GROUP BY tipo
    """, conn)
    
    if not df_mes_atual.empty:
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.barplot(x="tipo", y="total", data=df_mes_atual, ax=ax)
        ax.set_title("Receitas vs Despesas - Mês Atual")
        ax.set_xlabel("Tipo")
        ax.set_ylabel("Valor Total")
        st.pyplot(fig)
    else:
        st.warning("Não há dados disponíveis para exibir o gráfico do mês atual.")
    
    conn.close()
    
if __name__ == "__main__":
    main()
