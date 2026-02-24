# -----------------------
# Formatta messaggio trade con distanza in pips
# -----------------------
def format_message(data):
    if isinstance(data, dict):
        event = data.get("event", "")
        symbol = data.get("symbol", "")
        timeframe = data.get("timeframe", "")
        side = data.get("side", "")
        entry = data.get("entry", "N/A")
        exit_price = data.get("exit", "N/A")
        tp = data.get("tp", "N/A")
        sl = data.get("sl", "N/A")
        profit_percent = data.get("profit_percent", "-")  # lo manteniamo per debug

        # Arrotondamenti numerici
        try: entry_f = float(entry)
        except: entry_f = None
        try: exit_f = float(exit_price)
        except: exit_f = None
        try: tp = f"{float(tp):.3f}"
        except: pass
        try: sl = f"{float(sl):.3f}"
        except: pass

        # 🔹 Calcolo distanza in pips sul singolo trade
        profit_pips = "-"
        try:
            if entry_f is not None and exit_f is not None:
                if side.upper() == "LONG":
                    profit_pips = exit_f - entry_f
                elif side.upper() == "SHORT":
                    profit_pips = entry_f - exit_f
                profit_pips = f"{profit_pips:.2f} pips"
        except:
            pass

        # Emoji per messaggi
        emoji_open = {"start":"🚀", "end":"📈"} if side.upper() == "LONG" else {"start":"🔻", "end":"📉"}
        emoji_reversal = "🔄"
        emoji_tp = {"start":"🟢", "end":"🎯"}
        emoji_sl = {"start":"🔴", "end":"🛑"}
        emoji_close = {"start":"⚡️", "end":""}

        # Apertura trade
        if event in ["OPEN", "REVERSAL_OPEN"]:
            if event == "REVERSAL_OPEN":
                emoji_text = f"{emoji_reversal} {side.upper()}"
            else:
                emoji_text = f"{emoji_open['start']} {side.upper()} {emoji_open['end']}"
            message = (
                f"{emoji_text}\n"
                f"Pair: {symbol}\n"
                f"Timeframe: {timeframe}\n"
                f"Price: {entry}\n"
                f"TP: {tp}\n"
                f"SL: {sl}"
            )
            return message

        # Chiusura trade
        elif event in ["TP_HIT", "SL_HIT", "CLOSE"]:
            if event == "TP_HIT":
                emoji_start = emoji_tp["start"]
                emoji_end = emoji_tp["end"]
                event_text = "TP HIT"
            elif event == "SL_HIT":
                emoji_start = emoji_sl["start"]
                emoji_end = emoji_sl["end"]
                event_text = "SL HIT"
            else:
                emoji_start = emoji_close["start"]
                emoji_end = emoji_close["end"]
                event_text = "CLOSE"

            message = (
                f"{emoji_start} {event_text} {emoji_end}\n"
                f"{side.upper()}\n"
                f"Pair: {symbol}\n"
                f"Timeframe: {timeframe}\n"
                f"Entry: {entry}\n"
                f"Exit: {exit_price}\n"
                f"Profit: {profit_pips}"
            )
            return message

        else:
            return f"{symbol}: {event}"
    else:
        return str(data)
