"""
해당 소스의 저작권은 hyxxn2011, msh@cfam.co.kr이 가지고 있습니다!
해당 소스를 판매하지 말아주세요!
"""



import discord
from discord.ext import commands
from discord import app_commands
import random
import json
import os
import datetime

DATA_FILE = "user_data.json"

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

user_data = load_data()

@bot.tree.command(name="돈지급", description="유저에게 돈을 지급합니다.")
@app_commands.describe(user="지급할 유저", amount="지급할 금액")
async def give_money(interaction: discord.Interaction, user: discord.Member, amount: int):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("관리자만 사용할 수 있는 명령어입니다.", ephemeral=True)
        return

    if amount <= 0:
        await interaction.response.send_message("금액은 1 이상의 값이어야 합니다.", ephemeral=True)
        return

    user_id = str(user.id)
    if user_id not in user_data:
        user_data[user_id] = {"money": 0, "history": []}

    user_data[user_id]["money"] += amount
    save_data(user_data)

    embed = discord.Embed(
        title="돈 지급 알림",
        description=f"서버 관리자가 {amount}원을 지급하였습니다.",
        color=discord.Color.green(),
    )
    await user.send(embed=embed)
    await interaction.response.send_message(f"{user.mention}에게 {amount}원을 지급하였습니다.", ephemeral=True)

@bot.tree.command(name="돈회수", description="유저의 돈을 회수합니다.")
@app_commands.describe(user="회수할 유저", amount="회수할 금액")
async def take_money(interaction: discord.Interaction, user: discord.Member, amount: int):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("관리자만 사용할 수 있는 명령어입니다.", ephemeral=True)
        return

    if amount <= 0:
        await interaction.response.send_message("금액은 1 이상의 값이어야 합니다.", ephemeral=True)
        return

    user_id = str(user.id)
    if user_id not in user_data or user_data[user_id]["money"] < amount:
        await interaction.response.send_message("유저의 잔액이 부족하거나 존재하지 않습니다.", ephemeral=True)
        return

    user_data[user_id]["money"] -= amount
    save_data(user_data)

    embed = discord.Embed(
        title="돈 회수 알림",
        description=f"서버 관리자가 {amount}원을 회수하였습니다.",
        color=discord.Color.red(),
    )
    await user.send(embed=embed)
    await interaction.response.send_message(f"{user.mention}의 {amount}원을 회수하였습니다.", ephemeral=True)

@bot.tree.command(name="정보", description="자신의 돈 정보를 확인합니다.")
async def info(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    balance = user_data.get(user_id, {}).get("money", 0)
    await interaction.response.send_message(f"{interaction.user.mention}, 현재 잔액: {balance}원", ephemeral=True)

@bot.tree.command(name="사용이력", description="지난 돈 사용 이력을 확인합니다.")
async def history(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    history = user_data.get(user_id, {}).get("history", [])

    if not history:
        await interaction.response.send_message("돈 사용 이력이 없습니다.", ephemeral=True)
        return

    embed = discord.Embed(title="돈 사용 이력", color=discord.Color.blue())
    for entry in history:
        embed.add_field(name=entry["time"], value=f"{entry['type']}: {entry['amount']}원", inline=False)

    await interaction.user.send(embed=embed)
    await interaction.response.send_message("돈 사용 이력을 DM으로 전송하였습니다.", ephemeral=True)

@bot.tree.command(name="도박", description="돈을 베팅하여 도박을 합니다.")
@app_commands.describe(amount="베팅할 금액")
async def gamble(interaction: discord.Interaction, amount: int):
    user_id = str(interaction.user.id)
    balance = user_data.get(user_id, {}).get("money", 0)

    if amount <= 0:
        await interaction.response.send_message("금액은 1 이상의 값이어야 합니다.", ephemeral=True)
        return

    if amount > balance:
        await interaction.response.send_message("잔액이 부족합니다.", ephemeral=True)
        return

    base_chance = 0.2

    if random.random() < base_chance:
        winnings = amount * 2
        user_data[user_id]["money"] += winnings
        result = f"도박에 성공하여 {winnings}원을 획득했습니다!"
    else:
        user_data[user_id]["money"] -= amount
        result = f"도박에 실패하여 {amount}원을 잃었습니다."

    user_data[user_id]["history"].append(
        {"type": "도박", "amount": winnings if '성공' in result else -amount, "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    )    save_data(user_data)

    await interaction.response.send_message(result)

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Slash commands synced: {len(synced)}")
    except Exception as e:
        print(f"Error syncing commands: {e}")

    print(f"봇 실행 완료!")

bot.run("")