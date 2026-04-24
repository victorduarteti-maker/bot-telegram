import telebot
import schedule
import time
import os
import threading

TOKEN = "8605448094:AAFqgXaqhh76TWE1b0ngkZLsFIB_uScl0LY"
bot = telebot.TeleBot(TOKEN)

# caminho da pasta das imagens
pasta = r"C:\Users\victor.duarte.CYNTHIACHARONE\Documents\DESCOMPLICA PYTHON\imagens"

indice = 0
CHAT_ID = None
agendador_iniciado = False

def enviar_imagem():
    global indice, CHAT_ID

    if CHAT_ID is None:
        print("CHAT_ID não definido")
        return

    try:
        imagens = sorted(os.listdir(pasta))

        if not imagens:
            print("Pasta vazia!")
            return

        if indice >= len(imagens):
            indice = 0

        caminho = os.path.join(pasta, imagens[indice])

        print(f"Enviando: {caminho}")

        with open(caminho, 'rb') as foto:
            bot.send_photo(
                CHAT_ID,
                foto,
                caption="⚠️ Dica de Segurança do Dia"
            )

        indice += 1

    except Exception as e:
        print("Erro ao enviar imagem:", e)


def rodar_agendador():
    while True:
        schedule.run_pending()
        time.sleep(1)


@bot.message_handler(commands=['start'])
def start(msg):
    global CHAT_ID, agendador_iniciado

    CHAT_ID = msg.chat.id

    bot.reply_to(msg, "Bot iniciado! Enviando primeira imagem...")

    # envia imediatamente
    enviar_imagem()

    # inicia agendador só uma vez
    if not agendador_iniciado:
        schedule.every().day.at("08:00").do(enviar_imagem)
        threading.Thread(target=rodar_agendador, daemon=True).start()
        agendador_iniciado = True


bot.infinity_polling()
