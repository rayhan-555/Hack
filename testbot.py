import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    JobQueue,
)
import random
from datetime import datetime
import asyncio

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = "7894669364:AAEgEYVOVbNOVhISWHVI8LT2CvKuU7ah7B4"


current_prediction = None
prediction_history = []
active_chats = set()
last_period = 0

def get_current_period():
    """Calculate current period number based on UTC midnight"""
    now = datetime.utcnow()
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    return int((now - midnight).total_seconds() // 60)

async def generate_new_prediction():
    """Generate a new prediction for the upcoming period"""
    global current_prediction, last_period
    
    current_period = get_current_period()
    upcoming_period = current_period + 1
    
    if last_period != current_period:
        last_period = current_period
        
        
        result = "BIG" if random.random() < 0.5 else "SMALL"
        color = "🟢 GREEN" if random.random() < 0.5 else "🔴 RED"
        number = random.randint(0, 9)
        
        current_prediction = {
            "upcoming_period": upcoming_period,
            "result": result,
            "color": color,
            "number": number,
            "timestamp": datetime.now()
        }
        
        prediction_history.append(current_prediction)
        if len(prediction_history) > 100:
            prediction_history.pop(0)
    
    return current_prediction

def format_prediction():
    """Format the prediction with beautiful UI"""
    if not current_prediction:
        return "🔮 Preparing prediction..."
    
    next_update = (60 - datetime.utcnow().second) % 60 or 60
    last_five = prediction_history[-5:] if len(prediction_history) > 5 else prediction_history
    history = " • ".join(["🟢" if "GREEN" in p["color"] else "🔴" for p in last_five])
    
    return f"""
<b>✨ DK WIN VIP HACK ✨</b>
<code>┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓</code>
<b>🕒 TIME:</b> <code>{datetime.utcnow().strftime("%H:%M:%S UTC")}</code>
<b>🔢 PERIOD:</b> <code>#{current_prediction['upcoming_period']}</code>
<code>┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫</code>
<b>🎯 RESULT:</b> <code>{current_prediction['result']}</code>
<b>🎨 COLOR:</b> {current_prediction['color']}
<b>🔢 NUMBER:</b> <code>{current_prediction['number']}</code>
<code>┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫</code>
<b>📊 HISTORY:</b> <code>{history}</code>
<code>┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫</code>
<b>⏳ NEXT UPDATE:</b> <code>{next_update}s</code>
<code>┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛</code>
<pre>💎 Premium Prediction System 💎</pre>
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message with Get Prediction button"""
    user = update.effective_user
    chat_id = update.message.chat_id
    
    
    context.chat_data['chat_id'] = chat_id
   
    
    if 'prediction_msg_id' in context.chat_data:
        try:
            await context.bot.delete_message(chat_id, context.chat_data['prediction_msg_id'])
        except:
            pass
        del context.chat_data['prediction_msg_id']
    
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎯 GET PREDICTION 🎯", callback_data="get_prediction")]
    ])
    
    welcome_msg = f"""
<b>🌟 WELCOME {user.first_name.upper()}! 🌟</b>
<code>┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓</code>
<i>RS AI Prediction System</i>

<b>🔮 FEATURES:</b>
• Automatic Updates Every Minute
• BIG/SMALL Predictions
• RED/GREEN Colors
• Lucky Numbers

<b>⏱ NEXT PERIOD:</b> <code>#{get_current_period() + 1}</code>
<code>┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛</code>
"""
    
    
    msg = await update.message.reply_text(
        welcome_msg,
        parse_mode="HTML",
        reply_markup=keyboard
    )
    
    
    context.chat_data['welcome_msg_id'] = msg.message_id
    
    
    active_chats.add(chat_id)
    
  
    if 'prediction_job' not in context.chat_data:
        context.chat_data['prediction_job'] = context.job_queue.run_repeating(
            update_prediction,
            interval=15,
            first=0,
            chat_id=chat_id,
            name=str(chat_id)
        )

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Get Prediction button"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "get_prediction":
        chat_id = query.message.chat_id
        
        
        if 'welcome_msg_id' in context.chat_data:
            try:
                await context.bot.delete_message(chat_id, context.chat_data['welcome_msg_id'])
            except:
                pass
            del context.chat_data['welcome_msg_id']
        
        
        if 'prediction_msg_id' in context.chat_data:
            try:
                await context.bot.delete_message(chat_id, context.chat_data['prediction_msg_id'])
            except:
                pass
        
        
        loading_msg = await context.bot.send_message(
            chat_id,
            "<i>🔮 Analyzing patterns...</i>",
            parse_mode="HTML"
        )
        
        
        await generate_new_prediction()
        await asyncio.sleep(1.5)
        
        
        await context.bot.delete_message(chat_id, loading_msg.message_id)
       
        
        prediction_msg = await context.bot.send_message(
            chat_id,
            format_prediction(),
            parse_mode="HTML"
        )
        
        
        context.chat_data['prediction_msg_id'] = prediction_msg.message_id

async def update_prediction(context: ContextTypes.DEFAULT_TYPE):
    """Update prediction on period change - delete old, send new"""
    job = context.job
    chat_id = job.chat_id
    
    if chat_id in active_chats and 'prediction_msg_id' in context.chat_data:
        try:
            
            old_period = last_period
            await generate_new_prediction()
            
            if old_period != last_period:
                
                try:
                    await context.bot.delete_message(
                        chat_id=chat_id,
                        message_id=context.chat_data['prediction_msg_id']
                    )
                except Exception as e:
                    logger.warning(f"Couldn't delete old prediction: {e}")
                
                
                prediction_msg = await context.bot.send_message(
                    chat_id,
                    format_prediction(),
                    parse_mode="HTML"
                )
                
                
                context.chat_data['prediction_msg_id'] = prediction_msg.message_id
                
        except Exception as e:
            logger.error(f"Error updating prediction: {e}")

def main():
    """Start the bot"""
    application = Application.builder().token(BOT_TOKEN).build()
    
  
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_button))
    
    
    application.run_polling()

if __name__ == "__main__":
    main()
