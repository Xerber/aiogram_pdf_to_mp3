import configparser
import pdfplumber
from gtts import gTTS
from aiogram import Bot, Dispatcher, executor, types
import os
from pathlib import Path


work_dir = os.path.abspath(os.path.dirname(__file__))

config = configparser.ConfigParser()
config.read(f'{work_dir}//config.ini')
bot_token = config['Telegram']['bot_token']


bot = Bot(token=bot_token)

dp = Dispatcher(bot)

@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def cmd_test1(message: types.Message):
    await message.reply('Hey! I am an elementary bot that converts pdf to mp3. You were handed the documents, and you have no time to sit and read it? Send it to me and listen to it!')


@dp.message_handler(content_types=types.ContentTypes.DOCUMENT)
async def download_doc(message: types.Message):
    if message.document.file_name.split('.')[-1] == 'pdf':
        if message.document.file_size<=1500000:
            await message.answer('Converting..')
            #Saving the file
            await message.document.download(
            destination_file=f'{work_dir}//file.pdf',
            )
            #We go through the text and write everything in one line
            with pdfplumber.PDF(open(file=f'{work_dir}//file.pdf', mode='rb')) as pdf:
                pages = [page.extract_text() for page in pdf.pages[0:3]]
            text = ''.join(pages)
            #Remove line breaks so that there are no pauses in reading
            text = text.replace('\n','')
            audio = gTTS(text=text, lang='ru', slow=False)
            await message.answer('Sound recording...')
            audio.save(f'{work_dir}//file.mp3')
            await bot.send_audio(message.from_user.id, open(f'{work_dir}//file.mp3','rb'), title = 'Have a nice day!')
            #Loop to delete the files we created
            for root, dirs, files in os.walk(work_dir):
                for file in files:
                    if Path(file).suffix in ('.pdf','.mp3'):
                        os.remove(file)
        else:
            await message.answer('Sorry, but I can only work with files no larger than 1.5mb') 
    else:
        await message.answer('Sorry, but I only work with .pdf')

if __name__=='__main__':
    executor.start_polling(dp, skip_updates=True)