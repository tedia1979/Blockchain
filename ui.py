import streamlit as st
import requests
import json

# URL da API da Blockchain (ajuste conforme necessário)
API_URL = "http://192.168.1.6:5000"

st.title("Interface Visual da Blockchain")

st.sidebar.header("Ações")

# Exibir a cadeia de blocos
if st.sidebar.button("Exibir Blockchain"):
    response = requests.get(f"{API_URL}/chain")
    if response.status_code == 200:
        data = response.json()
        st.subheader("Blockchain")
        st.write(f"Comprimento: {data['length']}")
        st.json(data["chain"])
    else:
        st.error("Erro ao recuperar a cadeia de blocos.")

# Minerar um novo bloco
if st.sidebar.button("Minerar Bloco"):
    response = requests.get(f"{API_URL}/mine")
    if response.status_code == 200:
        data = response.json()
        st.success("Bloco minerado com sucesso!")
        st.json(data)
    else:
        st.error("Erro ao minerar o bloco.")

st.header("Nova Transação")

with st.form("transaction_form"):
    sender = st.text_input("Remetente")
    recipient = st.text_input("Destinatário")
    amount = st.number_input("Quantidade", min_value=0, step=1)
    submitted = st.form_submit_button("Enviar Transação")
    
    if submitted:
        # Valida os campos obrigatórios
        if not sender or not recipient:
            st.warning("Preencha os campos 'Remetente' e 'Destinatário'.")
        else:
            payload = {
                "sender": sender,
                "recipient": recipient,
                "amount": amount
            }
            st.write("Payload enviado:", payload)  # Depuração
            headers = {"Content-Type": "application/json"}
            response = requests.post(
                f"{API_URL}/transactions/new",
                data=json.dumps(payload),
                headers=headers
            )
            if response.status_code == 201:
                data = response.json()
                st.success(data["message"])
            else:
                st.error(f"Erro ao criar transação. Código {response.status_code}: {response.text}")
