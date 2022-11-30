import discord
from discord.ext import commands
import random
import os
import asyncio #なんか必要らしい

prefix = '!'

class Greet(commands.Cog, name = "おあそび"):
    """挨拶とかお遊び"""
    
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot: commands.Bot = bot

    #おはよう
    @commands.hybrid_command(name = 'おはよう', aliases=['おは'])
    async def ohayou(self, ctx: commands.Context):
        """おはよう"""
        await ctx.send('はい、おはようございます')

    #おみくじ
    @commands.hybrid_command(name = 'おみくじ', aliases=['占い', '運勢'])
    async def omikuji(self, ctx: commands.Context):
        """おみくじで占います"""
        unsei = ["大吉です！", "中吉です。", "吉ですね。", "小吉です～。", "凶でした。", "大凶です。あらあら。"]
        choice = random.choice(unsei) 
        await ctx.send(f'今日の運勢は……{choice}')

    # ウェルカムメッセージ
    @commands.Cog.listener()
    async def on_member_join(self, member):
        WelcomeChannel = self.bot.get_channel(int(os.getenv('WELCOME_CH')))
        await WelcomeChannel.send(f"{member.name}さん、ようこそいらっしゃいませ。必読１・２にはしっかり目を通してくださいね。\n<@{int(os.getenv('MASTER'))}>～！　お客様がお見えですよ！")


class Vch_kankei(commands.Cog, name = "ボイチャ"):
    """ボイチャに関わる機能群"""
    
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot: commands.Bot = bot
        self.guild = bot.get_guild(int(os.getenv('GUILD_ID')))
        # 人数取得の準備
        self.stagevch = bot.get_channel(int(os.getenv('STAGEVCH_ID')))

    #鯖内で使われたかを判定
    async def cog_check(self, ctx: commands.Context):
        if ctx.guild == self.guild:
            return True
        else:
            return False

    # 入退室ログ
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        guestnotech = bot.get_channel(int(os.getenv('GUESTNOTE_CH')))
        if before.channel is None:
            await guestnotech.send(f'{member.name} が {after.channel.name} に参加しました。')
        if after.channel is None:
            await guestnotech.send(f'{member.name} が {before.channel.name} から抜けました。')

    #きゅーふり
    @commands.hybrid_command(name = 'きゅーふり', aliases=['キューふり', 'キュー', 'きゅー'])
    async def Q_furi(self, ctx: commands.Context):
        """キュー返すよ"""
        await ctx.send(ctx.bot.voice_client.is_connected, self.voice_client.is_connected, voice_client.is_connected, ctx.message.guild.voice_client.is_connected, ctx.message.guild.voice_client.user.is_connected)
        # ぼいちゃにいないのに呼ばれたら注意する
        if ctx.author.voice is None:
            await ctx.send("ぼいちゃに入ってから呼んでください。")
            return
        # 音声を流す準備および音を小さく
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("https://kagamiya.work/gallery/voicefile/Q-furi-rugi2.mp3"), volume=0.2)
        if ctx.bot.voice_client.is_connected:
            voice = ctx.guild.voice_client
        else:
            # ぼいちゃに接続する
            voice = await ctx.author.voice.channel.connect()
        # 再生中の場合は再生しない
        if ctx.message.guild.voice_client.is_playing():
            await ctx.send("再生中です。")
            return
        voice.play(source)
        await ctx.send("はじまりはじまりー！") 
        

    # ボイチャから切断する
    @commands.hybrid_command(name = 'おちていいよ', aliases=['切断', 'ばいばい'])
    async def bye_bye(self, ctx: commands.Context):
        """切断するよ"""
        # botがぼいちゃにいないのに切断しようとしたら注意する
        if not ctx.bot.voice_client.is_connected:
            await ctx.send("私ぼいちゃにいませんよ。")
            return

        # 切断する
        await ctx.message.guild.voice_client.disconnect()
        VoiceProtocol.cleanup()
        await ctx.send("失礼しました～。")

    # かぞえる
    @commands.hybrid_command(name = '人数カウント', aliases=['数えて', 'カウントよろ'])
    async def NoP_count(self, ctx: commands.Context):
        """ボイチャに居る人数を数えます"""

        # ミュートでない人カウント
        active_items_list = list(self.stagevch.voice_states.items()) #ボイチャに接続しているメンバーのIDを取得
        if len(active_items_list) == 0:
            await ctx.send('参加者は0人です')
            return
        
        #self_mute == False の時、ボイチャ接続中のIDを取得
        active_set = {key for key, value in active_items_list if value.self_mute == False} #三項演算子・集合内包表記による一行での実装

        #男性カウント
        male = self.guild.get_role(int(os.getenv('MALE_ROLE'))) #鯖全体の男性に関して取得
        male_id_set = {male_mem.id for male_mem in male.members} #集合内包表記による一行での実装
        
        #女性カウント
        female = self.guild.get_role(int(os.getenv('FEMALE_ROLE'))) #鯖全体の女性に関して取得
        female_id_set = {female_mem.id for female_mem in female.members} #集合内包表記による一行での実装
        
        #積集合
        male_in_vch = male_id_set & active_set #積集合で男性の非ミュートのIDを取得
        female_in_vch = female_id_set & active_set #積集合で女性の非ミュートのIDを取得
        other_in_vch = active_set ^ (male_id_set | female_id_set) #和集合と対称差集合によって性別不問を取得
        
        #いよいよsend
        #await massage.channel.send(f'参加人数は　{len(active_set)}人　で、比率は　男性{len(male_in_vch) / functools.reduce(math.gcd, [len(male_in_vch), len(female_in_vch), len(other_in_vch)])}：女性{len(female_in_vch) / functools.reduce(math.gcd, [len(male_in_vch), len(female_in_vch), len(other_in_vch)])}：性別不問{len(other_in_vch) / functools.reduce(math.gcd, [len(male_in_vch), len(female_in_vch), len(other_in_vch)])}　となっています。') #比率でsendする場合
        await message.channel.send(f'参加者は{len(active_set)}人です。内訳は男性{len(male_in_vch)}人：女性{len(female_in_vch)}人：性別不問{len(active_set) - len(male_in_vch) - len(female_in_vch)}人です。')  

class JapaneseHelpCommand(commands.DefaultHelpCommand):
    def __init__(self):
        super().__init__()
        self.commands_heading = "コマンド:"
        self.no_category = "その他"
        self.command_attrs["help"] = "コマンド一覧と簡単な説明を表示"

    def get_ending_note(self):
        return (f"各コマンドの説明: {prefix}help コマンド名\n"
                f"各カテゴリの説明: {prefix}help カテゴリ名\n")

# 接続に必要なオブジェクトを生成
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True
intents.presences = True
intents.voice_states = True
bot = commands.Bot(
    command_prefix=prefix,
    case_insensitive=True, #コマンドの大文字小文字を無視する(True)
    intents=intents, 
    status=discord.Status.online, 
    activity=discord.Activity(
        type=discord.ActivityType.competing,
        name="!help　してみてね"
    ),
    help_command=JapaneseHelpCommand()
)

#起動時処理
@bot.event
async def on_ready():
    await bot.add_cog(Greet(bot))
    await bot.add_cog(Vch_kankei(bot))
    print('テストボット、起動しました！'.format(bot))

#エラー処理
@bot.event
async def on_command_error(ctx: commands.Context, error):
  if ctx.message.author.bot:
      return
  if isinstance(error, commands.errors.CheckFailure):
    await ctx.send(f'ここ私の動く鯖じゃないです', ephemeral=True)


bot.run(os.getenv('TOKEN'))
