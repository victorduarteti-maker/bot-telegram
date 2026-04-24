import telebot
import schedule
import time
import os
import threading

# 🔐 Configurações via Variáveis de Ambiente (Configurar no painel da Square Cloud/Railway)
TOKEN = os.getenv("TOKEN")
# Tenta pegar o ID fixo da variável 'MY_CHAT_ID', se não existir, vira None
ENV_CHAT_ID = os.getenv("MY_CHAT_ID")
CHAT_ID = int(ENV_CHAT_ID) if ENV_CHAT_ID else None

bot = telebot.TeleBot(TOKEN)

# 📁 Garante o caminho correto da pasta de imagens
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
pasta = os.path.join(BASE_DIR, "imagens")

indice = 0
agendador_iniciado = False

def enviar_imagem():
    global indice, CHAT_ID

    # Se o CHAT_ID ainda for None, o bot não tem para onde enviar
    if CHAT_ID is None:
        print("Aguardando definição do CHAT_ID (Envie /start para o bot ou configure a variável MY_CHAT_ID)")
        return

    try:
        if not os.path.exists(pasta):
            print(f"Erro: Pasta {pasta} não encontrada!")
            return

        # Filtra apenas arquivos de imagem
        imagens = sorted([f for f in os.listdir(pasta) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])

        if not imagens:
            print("Pasta de imagens está vazia!")
            return

        if indice >= len(imagens):
            indice = 0

        caminho = os.path.join(pasta, imagens[indice])
        print(f"Enviando: {caminho} para o chat {CHAT_ID}")

        with open(caminho, 'rb') as foto:
            bot.send_photo(
                CHAT_ID,
                foto,
                caption="⚠️ Dica de Segurança do Dia"
            )

        indice += 1
    except Exception as e:
        print(f"Erro ao enviar imagem: {e}")

def rodar_agendador():
    while True:
        schedule.run_pending()
        time.sleep(30) # Verifica a cada 30 segundos (mais eficiente)

def iniciar_agendamentos():
    global agendador_iniciado
    if not agendador_iniciado:
        # Agendamento segunda a sexta às 08:00
        for dia in ["monday", "tuesday", "wednesday", "thursday", "friday"]:
            getattr(schedule.every(), dia).at("08:00").do(enviar_imagem)
        
        t = threading.Thread(target=rodar_agendador, daemon=True)
        t.start()
        agendador_iniciado = True
        print("Agendador iniciado com sucesso!")

@bot.message_handler(commands=['start'])
def start(msg):
    global CHAT_ID
    CHAT_ID = msg.chat.id
    bot.reply_to(msg, f"👋 Bot ativado! ID registrado: {CHAT_ID}\nDicas agendadas para as 08:00 (Seg-Sex).")
    
    # Envia uma imagem na hora para testar
    enviar_imagem()

if __name__ == "__main__":
    # Inicia o agendador assim que o script liga
    iniciar_agendamentos()
    
    print("Bot online...")
    bot.infinity_polling()
