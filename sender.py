from tools import split, list_splitter
from loguru import logger as log


class PostSender:
    def __init__(self, bot, post, chat_id):
        self.bot = bot
        self.post = post
        self.chat_id = chat_id
        self.text = split(self.post.text)

    def send_post(self):
        self.send_text_and_photos()
        if len(self.post.videos) != 0:
            self.send_videos()
        if len(self.post.docs) != 0:
            self.send_documents()
        if len(self.post.tracks) != 0:
            self.send_music()

    @log.catch()
    def send_text_and_photos(self):
        if self.post.photos:
            if len(self.post.photos) == 1:
                log.info('Отправка текста и фото')
                if len(self.post.text) > 1024:
                    send_splitted_message(self.bot, self.text, self.chat_id)
                    self.bot.send_message(self.chat_id, self.text[-1], parse_mode='HTML',
                                          reply_markup=self.post.reply_markup, disable_web_page_preview=True)
                    self.bot.send_photo(self.chat_id, self.post.photos[0]['media'], parse_mode='HTML')
                else:
                    self.bot.send_photo(self.chat_id, self.post.photos[0]['media'], caption=self.text[-1],
                                        reply_markup=self.post.reply_markup, parse_mode='HTML')
            else:
                log.info('Отправка текста')
                if len(self.post.text) > 1024:
                    send_splitted_message(self.bot, self.text, self.chat_id)
                    self.bot.send_message(self.chat_id, self.text[-1], parse_mode='HTML',
                                          reply_markup=self.post.reply_markup,
                                          disable_web_page_preview=True)
                    for i in list_splitter(self.post.photos, 10):
                        self.bot.send_media_group(self.chat_id, i)
                else:
                    for i in list_splitter(self.post.photos, 10):
                        self.bot.send_media_group(self.chat_id, i, reply_markup=self.post.reply_markup)
        elif self.post.text and not self.post.photos and not self.post.videos and not self.post.docs:
            send_splitted_message(self.bot, self.text, self.chat_id)
            self.bot.send_message(self.chat_id, self.text[-1], parse_mode='HTML', reply_markup=self.post.reply_markup,
                                  disable_web_page_preview=True)

    def send_videos(self):
        log.info('Отправка видео')
        for i in range(len(self.post.videos)):
            try:
                if i == 0:
                    if not self.post.photos:
                        if len(self.post.text) < 1024:
                            self.bot.send_video(self.chat_id, video=open(self.post.videos[i], 'rb'),
                                                timeout=60,
                                                parse_mode='HTML',
                                                caption=self.text[-1],
                                                reply_markup=self.post.reply_markup)
                        else:
                            send_splitted_message(self.bot, self.text, self.chat_id)
                            self.bot.send_message(self.chat_id, self.text[-1],
                                                  parse_mode='HTML',
                                                  reply_markup=self.post.reply_markup,
                                                  disable_web_page_preview=True)
                            self.bot.send_video(self.chat_id, video=open(self.post.videos[i], 'rb'), timeout=60)
                    else:
                        self.bot.send_video(self.chat_id, video=open(self.post.videos[i], 'rb'), timeout=60)
                else:
                    self.bot.send_video(self.chat_id, video=open(self.post.videos[i], 'rb'), timeout=60)
            except Exception:
                log.exception('Не удалось отправить видео. Пропускаем его...')

    def send_documents(self):
        log.info('Отправка прочих вложений')
        for i in range(len(self.post.docs)):
            doc, filename = self.post.docs[i]
            try:
                if i == 0:
                    if not self.post.photos and not self.post.videos:
                        if len(self.post.text) < 1024:
                            self.bot.send_document(self.chat_id, document=open(doc, 'rb'),
                                                   caption=self.text[-1], parse_mode='HTML', timeout=60,
                                                   filename=filename, reply_markup=self.post.reply_markup)
                        else:
                            send_splitted_message(self.bot, self.text, self.chat_id)
                            self.bot.send_message(self.chat_id, self.text[-1], parse_mode='HTML',
                                                  reply_markup=self.post.reply_markup, disable_web_page_preview=True)
                            self.bot.send_document(self.chat_id, document=open(doc, 'rb'), timeout=60)
                    else:
                        self.bot.send_document(self.chat_id, document=open(doc, 'rb'), timeout=60)
                else:
                    self.bot.send_document(self.chat_id, document=open(doc, 'rb'), timeout=60)
            except Exception:
                log.exception('Не удалось отправить документ. Пропускаем его...')

    def send_music(self):
        log.info('Отправка аудио')
        for audio, duration in self.post.tracks:
            try:
                self.bot.send_audio(self.chat_id, open(audio, 'rb'), duration, timeout=60)
            except Exception:
                log.exception('Не удалось отправить аудио файл. Пропускаем его...')


def send_splitted_message(bot, text, chat_id):
    for i in range(len(text) - 1):
        bot.send_message(chat_id, text[i], parse_mode='HTML')

