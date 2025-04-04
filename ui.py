import streamlit as st
import requests

# Ajuste a URL conforme necessário (se estiver em outra máquina ou porta diferente)
BASE_URL = "http://localhost:5000"

st.title("Exemplo de Blockchain")

tab1, tab2, tab3 = st.tabs(["Registrar Transação", "Ver Blockchain", "Minerar Bloco"])

with tab1:
    st.header("Registrar Transação")

    sender = st.text_input("Remetente (sender)", "")
    recipient = st.text_input("Destinatário (recipient)", "")
    complete_recipient = st.text_input("Destinatário Completo (complete_recipient)", "")
    amount = st.text_input("Valor (amount) em texto", "")

    if st.button("Registrar Transação"):
        if sender and recipient and complete_recipient and amount:
            data = {
                "sender": sender,
                "recipient": recipient,
                "complete_recipient": complete_recipient,
                "amount": amount
            }
            try:
                response = requests.post(f"{BASE_URL}/transactions/new", json=data)
                if response.status_code == 201:
                    st.success(response.json()["message"])
                else:
                    st.error(f"Erro: {response.text}")
            except Exception as e:
                st.error(f"Falha ao se conectar ao servidor: {e}")
        else:
            st.warning("Preencha todos os campos antes de registrar a transação.")

with tab2:
    st.header("Ver Blockchain")
    if st.button("Carregar Blockchain"):
        try:
            response = requests.get(f"{BASE_URL}/chain")
            if response.status_code == 200:
                chain_data = response.json()
                st.write("Tamanho da Blockchain:", chain_data["length"])
                st.json(chain_data["chain"])
            else:
                st.error(f"Erro: {response.text}")
        except Exception as e:
            st.error(f"Falha ao se conectar ao servidor: {e}")

with tab3:
    st.header("Minerar Bloco")
    if st.button("Minerar"):
        try:
            response = requests.get(f"{BASE_URL}/mine")
            if response.status_code == 200:
                data = response.json()
                st.success("Bloco minerado com sucesso!")
                st.write("Índice:", data["index"])
                st.write("Prova (proof):", data["proof"])
                st.write("Hash anterior:", data["previous_hash"])
                st.write("Transações:", data["transactions"])
            else:
                st.error(f"Erro: {response.text}")
        except Exception as e:
            st.error(f"Falha ao se conectar ao servidor: {e}")
