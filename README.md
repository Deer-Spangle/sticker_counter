# Sticker counter
This is just a couple simple scripts to log which stickers I use on telegram.

- `sticker_logger.py` Is a script to leave running 24/7, and it will check every minute to see if a sticker has been used, and if so, send it to a sticker log chat.
- `sticker_counter.py` Is a scrit to read through the log chat, and count up how many times each sticker was used, and send some stats to the log chat, and a top 5 ranking of stickers to your saved messages.


## Setup
1. You should be able to copy the code with
`git clone https://github.com/Deer-Spangle/sticker_counter.git`
That'll download it into `sticker_counter` directory.

2. Then you need to create a config.json file like this:
    ```json
    {
        "api_id": 1,
        "api_hash": "--",
        "chat_id": -1001
    }
    ```
3. You get `api_id` and `api_hash` from https://my.telegram.org
   - You login there, then click "API development tools".
   - Then the top two text boxes should be your API ID and API hash.
   - The first one is a number, and the second one is a string. Those need putting into the config.json file.
   - Those are secret, and should not be shared.

4. You will also need to create a telegram groupchat to store the copied stickers.
   - (Worth making it a supergroup too, go into settings and set chat history to "visible")
   - Then get the chat ID, post something there, right click (or long press), and copy the message link, which should look something like this: https://t.me/c/1287900913/19376
   - The first number, the bigger one, is the one you want. That's the chat ID.
   - That needs prefixing with -100, and putting into `config.json` as the value for `chat_id`. 
   - So, in this example: -1001287900913

5. And then you need to install dependencies, so `pip install -r requirements.txt` in that sticker counter directory.

6. Then you run it! `python sticker_logger.py` And it'll ask your phone number, then send you a verification code, and then start monitoring your stickers!

Every minute it checks, and if new stickers have been used, it sends them to the log chat