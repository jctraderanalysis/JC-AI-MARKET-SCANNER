import time
import datetime
import threading
import config
from scanner import analyze_symbol
from notifier import notify_startup, send_telegram_msg, send_email_report

sent_signals = set()

def scan_loop():
    """Función para ejecutar el escaneo en segundo plano."""
    print("Iniciando JC AI MARKET SCANNER PRO...")
    notify_startup()

    while True:
        try:
            print(f"\n--- Escaneando Mercado: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
            
            bullish_signals = []
            bearish_signals = []

            all_symbols = []
            for category in config.SYMBOLS.values():
                all_symbols.extend(category)

            for symbol in set(all_symbols):
                signal = analyze_symbol(symbol)
                if signal:
                    sig_key = f"{symbol}_{signal['type']}_{signal['price']}"
                    if sig_key not in sent_signals:
                        sent_signals.add(sig_key)
                        if signal['type'] == "COMPRA":
                            bullish_signals.append(signal)
                        else:
                            bearish_signals.append(signal)

            # Enviar reportes agrupados
            if bullish_signals:
                msg_tg = "<b>🟢 MERCADO ALCISTA - OPORTUNIDADES</b>\n\n"
                email_body = "MERCADO WALLSTREET ALCISTA\n\n"
                for s in bullish_signals:
                    msg_tg += f"<b>{s['symbol']}</b> | COMPRA | Entrada: {s['price']}\nConfianza: {s['confidence']}% | RSI: {s['rsi']}\nMotivo: {s['reason']}\n\n"
                    email_body += f"{s['symbol']} - COMPRA - Entrada: {s['price']} - RSI: {s['rsi']}\n"
                
                send_telegram_msg(msg_tg)
                send_email_report("MERCADO WALLSTREET ALCISTA", email_body)

            if bearish_signals:
                msg_tg = "<b>🔴 MERCADO BAJISTA - OPORTUNIDADES</b>\n\n"
                email_body = "MERCADO WALLSTREET BAJISTA\n\n"
                for s in bearish_signals:
                    msg_tg += f"<b>{s['symbol']}</b> | VENTA | Entrada: {s['price']}\nConfianza: {s['confidence']}% | RSI: {s['rsi']}\nMotivo: {s['reason']}\n\n"
                    email_body += f"{s['symbol']} - VENTA - Entrada: {s['price']} - RSI: {s['rsi']}\n"
                
                send_telegram_msg(msg_tg)
                send_email_report("MERCADO WALLSTREET BAJISTA", email_body)

        except Exception as e:
            print(f"[!] Error en bucle de escaneo: {e}")

        time.sleep(config.SCAN_INTERVAL_SECONDS)

def start_background_scanner():
    """Inicia el hilo secundario para el escáner si no está corriendo."""
    # Verificar si el hilo ya fue iniciado para no duplicarlo
    for thread in threading.enumerate():
        if thread.name == "JC_Scanner_Thread":
            return
    
    t = threading.Thread(target=scan_loop, name="JC_Scanner_Thread", daemon=True)
    t.start()

if __name__ == "__main__":
    scan_loop()
