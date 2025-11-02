import os
import telebot
import sqlite3
import datetime
from threading import Thread
import time

BOT_TOKEN = "8372531838:AAEj4u8J9-9bQirOb26XJ6HClGP3sgunqHQ"  # Votre token direct
ADMIN_ID = 5853721950
NUMERO_MTN = "+229 53575203"
TAUX_QUOTIDIEN = 0.05  # 5% par jour

bot = telebot.TeleBot(BOT_TOKEN)

# Base de données
def init_db():
    conn = sqlite3.connect('investisseurs.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS utilisateurs (
            user_id INTEGER PRIMARY KEY,
            solde REAL DEFAULT 0,
            capital_investi REAL DEFAULT 0,
            profit_total REAL DEFAULT 0,
            date_inscription TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Calcul automatique des profits
def calculer_profits():
    while True:
        try:
            conn = sqlite3.connect('investisseurs.db')
            cursor = conn.cursor()
            cursor.execute('SELECT user_id, capital_investi FROM utilisateurs WHERE capital_investi > 0')
            utilisateurs = cursor.fetchall()
            
            for user_id, capital in utilisateurs:
                profit = capital * TAUX_QUOTIDIEN  # 5% quotidien
                cursor.execute('''
                    UPDATE utilisateurs 
                    SET solde = solde + ?, profit_total = profit_total + ?
                    WHERE user_id = ?
                ''', (profit, profit, user_id))
                
                # Notification du profit
                try:
                    bot.send_message(user_id, f"🎉 PROFIT QUOTIDIEN 5% : +{profit:.2f} F CFA")
                except:
                    pass
            
            conn.commit()
            conn.close()
        except:
            pass
        
        # Attendre 24 heures
        time.sleep(24 * 60 * 60)

# Démarrer le calcul des profits
Thread(target=calculer_profits, daemon=True).start()

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    init_db()
    
    conn = sqlite3.connect('investisseurs.db')
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO utilisateurs (user_id) VALUES (?)', (user_id,))
    conn.commit()
    conn.close()
    
    reponse = f"""
🏦 <b>Bienvenue {message.from_user.first_name} !</b>

<b>🚀 InvestSmaet Platform - 5% QUOTIDIEN</b>

📊 <b>Programme d'investissement EXCLUSIF :</b>
• Taux quotidien : <b>5% PAR JOUR</b>
• Dépôt minimum : 5,000 F CFA
• Retrait minimum : 1,000 F CFA
• Profits calculés automatiquement chaque jour

💳 <b>Compte de dépôt :</b>
📱 MTN Bénin : <code>{NUMERO_MTN}</code>

💰 <b>Votre argent multiplié par 5% chaque jour !</b>
    """
    bot.send_message(message.chat.id, reponse, parse_mode='HTML')

@bot.message_handler(commands=['depot'])
def depot(message):
    reponse = f"""
💰 <b>Déposer des Fonds - 5% QUOTIDIEN</b>

📋 <b>Informations de Paiement :</b>
🏦 <b>MTN Mobile Money Bénin</b>
📱 <b>Numéro :</b> <code>{NUMERO_MTN}</code>

💳 <b>Procédure :</b>
1. Transférez vers le numéro ci-dessus
2. Envoyez la preuve de paiement
3. Votre capital sera crédité immédiatement
4. Recevez 5% de profit chaque jour

📊 <b>Conditions :</b>
• Dépôt minimum : 5,000 F CFA
• Aucune commission
• Validation rapide
• <b>5% DE GAIN QUOTIDIEN GARANTI</b>
    """
    bot.send_message(message.chat.id, reponse, parse_mode='HTML')

@bot.message_handler(commands=['portefeuille'])
def portefeuille(message):
    user_id = message.from_user.id
    conn = sqlite3.connect('investisseurs.db')
    cursor = conn.cursor()
    cursor.execute('SELECT solde, capital_investi, profit_total FROM utilisateurs WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        solde, capital, profit = result
        reponse = f"""
💼 <b>Votre Portefeuille - 5% QUOTIDIEN</b>

💰 Solde disponible : <b>{solde:.2f} F CFA</b>
📈 Capital investi : <b>{capital:.2f} F CFA</b>
🎯 Profit total : <b>{profit:.2f} F CFA</b>

💡 <b>Votre capital génère 5% chaque jour !</b>
📊 <b>Prochain gain : {capital * 0.05:.2f} F CFA</b>
        """
    else:
        reponse = "❌ Aucune information trouvée. Utilisez /depot pour investir et gagner 5% quotidien !"
    
    bot.send_message(message.chat.id, reponse, parse_mode='HTML')

@bot.message_handler(commands=['admin'])
def admin(message):
    if message.from_user.id == ADMIN_ID:
        conn = sqlite3.connect('investisseurs.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*), SUM(solde), SUM(capital_investi) FROM utilisateurs')
        stats = cursor.fetchone()
        conn.close()
        
        reponse = f"""
👑 <b>Panel Administrateur - 5% QUOTIDIEN</b>

👥 Utilisateurs : {stats[0] or 0}
💰 Solde total : {stats[1] or 0:.2f} F CFA
📈 Capital total : {stats[2] or 0:.2f} F CFA
💸 Profit quotidien : {stats[2] * 0.05 if stats[2] else 0:.2f} F CFA

💳 {NUMERO_MTN}
🤖 Bot 5% quotidien opérationnel
        """
        bot.send_message(message.chat.id, reponse, parse_mode='HTML')

print("🚀 Bot InvestSmaet 5% Quotidien déployé sur Railway!")
init_db()
bot.infinity_polling()
