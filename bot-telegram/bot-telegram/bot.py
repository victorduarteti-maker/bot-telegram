import telebot
import schedule
import time
import os
import threading

# Use variáveis de ambiente para segurança ou cole seu token aqui
TOKEN = os.getenv("TELEGRAM_TOKEN") # O Railway vai preencher isso
bot = telebot.TeleBot(TOKEN)

# AJUSTE: No servidor, as imagens ficam na mesma pasta do script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
pasta = os.path.join(BASE_DIR, "imagens")

indice = 0
# DICA: Coloque seu ID fixo aqui para o bot não "esquecer" se o servidor reiniciar
CHAT_ID = None 
agendador_iniciado = False

def enviar_imagem():
    global indice, CHAT_ID
    if CHAT_ID is None:
        return

    try:
        if not os.path.exists(pasta):
            print(f"Erro: Pasta {pasta} não encontrada!")
            return

        imagens = sorted([f for f in os.listdir(pasta) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])

        if not imagens:
            return

        if indice >= len(imagens):
            indice = 0

        caminho = os.path.join(pasta, imagens[indice])
        with open(caminho, 'rb') as foto:
            bot.send_photo(CHAT_ID, foto, caption="⚠️ Dica de Segurança do Dia")
        
        indice += 1
    except Exception as e:
        print(f"Erro: {e}")

def rodar_agendador():
    while True:
        schedule.run_pending()
        time.sleep(60) # Verifica a cada minuto

@bot.message_handler(commands=['start'])
def start(msg):
    global CHAT_ID, agendador_iniciado
    CHAT_ID = msg.chat.id
    bot.reply_to(msg, "Bot configurado para dicas diárias (08:00)! 🔒")
    enviar_imagem()

    if not agendador_iniciado:
        # Agendamento segunda a sexta
        for dia in ["monday", "tuesday", "wednesday", "thursday", "friday"]:
            getattr(schedule.every(), dia).at("08:00").do(enviar_imagem)
        
        t = threading.Thread(target=rodar_agendador, daemon=True)
        t.start()
        agendador_iniciado = True

if __name__ == "__main__":
    bot.infinity_polling()
