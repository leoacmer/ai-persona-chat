import datetime
import re
import traceback
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db import _conversations, _messages, _next, Conversation, Message
from services.ai_service import chat_completion
from services.persona_service import get_persona, list_personas
from services.memory_service import build_context, extract_and_save_memory

router = APIRouter(prefix="/api/chat", tags=["chat"])


def strip_actions(text: str) -> str:
    """去掉括号动作描写：（xxx）和 (xxx)，以及 *xxx*"""
    text = re.sub(r"[（(][^）)]*[）)]", "", text)
    text = re.sub(r"\*[^*]+\*", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


EMOJI_MAP = {
    # 表情
    "[笑]": "😊", "[大笑]": "😆", "[呲牙]": "😁", "[偷笑]": "🤭",
    "[笑哭]": "😂", "[笑cry]": "😂", "[破涕为笑]": "😂",
    "[微笑]": "🙂", "[嘻嘻]": "😁", "[哈哈]": "😆",
    "[害羞]": "😳", "[脸红]": "😊", "[不好意思]": "😅",
    "[开心]": "😄", "[高兴]": "😃", "[耶]": "✌️",
    "[得意]": "😎", "[酷]": "😎", "[帅]": "😎",
    "[星星眼]": "🤩", "[色]": "😍", "[花痴]": "😍",
    "[亲亲]": "😘", "[飞吻]": "😘", "[亲]": "😚",
    "[爱心]": "❤️", "[心]": "❤️", "[比心]": "🫰",
    "[喜欢]": "🥰", "[爱]": "😻", "[爱你]": "😘",
    "[飞吻]": "😘", "[吻]": "😘",
    # 负面情绪
    "[哭]": "😢", "[流泪]": "😢", "[大哭]": "😭", "[悲伤]": "😞",
    "[难过]": "😢", "[伤心]": "💔", "[心碎]": "💔",
    "[委屈]": "😣", "[可怜]": "🥺", "[求]": "🥺",
    "[生气]": "😡", "[发怒]": "😠", "[怒]": "😠",
    "[骂]": "🤬", "[打人]": "👊", "[揍]": "👊",
    "[敲头]": "😤", "[敲打]": "😤", "[拍打]": "😤",
    "[白眼]": "🙄", "[鄙视]": "🙄", "[翻白眼]": "🙄",
    "[叹气]": "😮‍💨", "[唉]": "😮‍💨", "[无奈]": "😮‍💨",
    "[石化]": "😰", "[汗]": "😅", "[尴尬]": "😅", "[冷汗]": "😰",
    "[无语]": "😑", "[冷漠]": "😐", "[冷漠脸]": "😐",
    "[困]": "😴", "[睡]": "😴", "[累]": "😩",
    "[吐]": "🤮", "[恶心]": "🤢",
    # 正面情绪
    "[赞]": "👍", "[强]": "💪", "[牛]": "🐂",
    "[鼓掌]": "👏", "[拍手]": "👏", "[好]": "👏",
    "[冲鸭]": "💪", "[加油]": "💪", "[努力]": "💪",
    "[干杯]": "🥂", "[庆祝]": "🎉", "[撒花]": "🎉",
    "[转圈圈]": "💫", "[旋转]": "💫", "[跳]": "🕺",
    "[抱抱]": "🫂", "[拥抱]": "🤗", "[hug]": "🤗",
    "[坏笑]": "😏", "[阴险]": "😏", "[奸笑]": "😏",
    "[傲娇]": "😤", "[哼]": "😤",
    "[惊讶]": "😲", "[吃惊]": "😮", "[吓]": "😱",
    "[捂脸]": "🤦", "[汗颜]": "🤦",
    "[思考]": "🤔", "[想]": "🤔", "[疑问]": "🤨",
    "[OK]": "👌", "[ok]": "👌", "[搞定]": "👌",
    "[胜利]": "✌️", "[V]": "✌️",
    # 自然天气
    "[太阳]": "☀️", "[晴天]": "☀️", "[阳光]": "☀️",
    "[月亮]": "🌙", "[晚安]": "🌙", "[夜晚]": "🌙",
    "[星星]": "⭐", "[星光]": "✨", "[闪]": "✨",
    "[火]": "🔥", "[热]": "🔥", "[火爆]": "🔥",
    "[彩虹]": "🌈", "[虹]": "🌈",
    "[雨]": "🌧️", "[下雨]": "🌧️", "[暴雨]": "⛈️",
    "[雪]": "❄️", "[下雪]": "❄️", "[雪花]": "❄️",
    "[风]": "🌬️", "[刮风]": "💨", "[风车]": "🎐",
    "[云]": "☁️", "[云朵]": "☁️",
    "[闪电]": "⚡", "[雷]": "⚡",
    # 动植物
    "[花]": "🌸", "[樱花]": "🌸", "[玫瑰]": "🌹", "[花束]": "💐",
    "[草]": "🌿", "[叶]": "🍃", "[四叶草]": "🍀",
    "[猫]": "🐱", "[猫咪]": "🐱", "[小猫]": "🐱",
    "[狗]": "🐶", "[狗狗]": "🐶", "[小狗]": "🐶",
    "[兔子]": "🐰", "[兔]": "🐰",
    "[熊]": "🐻", "[熊猫]": "🐼", "[猪]": "🐷",
    "[猴子]": "🐒", "[鸡]": "🐔", "[鱼]": "🐟",
    # 食物
    "[蛋糕]": "🎂", "[生日]": "🎂", "[甜点]": "🍰",
    "[吃]": "🍽️", "[饭]": "🍚", "[美食]": "🍜",
    "[面]": "🍜", "[面条]": "🍜", "[火锅]": "🍲",
    "[饭团]": "🍙", "[寿司]": "🍣", "[便当]": "🍱",
    "[咖啡]": "☕", "[茶]": "🍵", "[奶茶]": "🧋",
    "[啤酒]": "🍺", "[酒]": "🍷", "[红酒]": "🍷",
    "[鸡腿]": "🍗", "[炸鸡]": "🍗", "[肉]": "🥩",
    "[西瓜]": "🍉", "[水果]": "🍎", "[苹果]": "🍎",
    "[冰棍]": "🍦", "[冰淇淋]": "🍦", "[棒冰]": "🍧",
    "[糖]": "🍬", "[糖果]": "🍬",
    # 活动
    "[礼物]": "🎁", "[红包]": "🧧",
    "[烟花]": "🎆", "[鞭炮]": "🧨",
    "[音乐]": "🎵", "[听歌]": "🎧", "[歌]": "🎤",
    "[电影]": "🎬", "[相机]": "📷", "[拍照]": "📸",
    "[旅行]": "✈️", "[飞机]": "✈️", "[旅游]": "🧳",
    "[运动]": "🏃", "[跑步]": "🏃", "[健身]": "💪",
    "[篮球]": "🏀", "[足球]": "⚽", "[游戏]": "🎮",
    "[看书]": "📖", "[书]": "📖", "[学习]": "📚",
    "[购物]": "🛍️", "[买]": "🛒", "[逛街]": "🛍️",
    "[睡觉]": "😴", "[晚安]": "🌙", "[起床]": "🌅",
    # 符号
    "[ok]": "👌", "[OK]": "👌", "[yes]": "✅",
    "[no]": "❌", "[x]": "❌", "[X]": "❌",
    "[对]": "✅", "[错]": "❌", "[叉]": "❌",
    "[感叹号]": "❗", "[问号]": "❓", "[注意]": "⚠️",
    "[禁止]": "🚫", "[停]": "⛔",
    "[100]": "💯", "[满分]": "💯",
    "[钱]": "💰", "[金币]": "🪙", "[有钱]": "🤑",
    "[目标]": "🎯", "[击中]": "🎯",
    "[灯泡]": "💡", "[灵感]": "💡", "[想法]": "💡",
    "[钥匙]": "🔑", "[锁]": "🔒", "[解锁]": "🔓",
    "[电话]": "📞", "[手机]": "📱",
    "[闹钟]": "⏰", "[时间]": "⌚", "[钟]": "🕐",
    "[日历]": "📅", "[日期]": "📆",
    "[笔]": "✏️", "[铅笔]": "✏️", "[笔记]": "📝",
    "[邮件]": "📧", "[信封]": "✉️",
    "[家]": "🏠", "[房子]": "🏠", "[学校]": "🏫",
    "[车]": "🚗", "[汽车]": "🚗",
    "[伞]": "☂️", "[雨伞]": "☔",
}


def render_emoji(text: str) -> str:
    for tag, emoji in EMOJI_MAP.items():
        text = text.replace(tag, emoji)
    return text


class ChatRequest(BaseModel):
    conversation_id: int | None = None
    persona_id: int
    message: str


class ChatResponse(BaseModel):
    conversation_id: int
    reply: str


@router.get("/personas")
async def get_personas():
    personas = await list_personas()
    return [{"id": p.id, "name": p.name, "description": p.description} for p in personas]


@router.post("", response_model=ChatResponse)
async def chat(req: ChatRequest):
    try:
        persona = await get_persona(req.persona_id)
        if persona is None:
            raise HTTPException(status_code=404, detail="Persona not found")

        if req.conversation_id is None:
            conv = Conversation(
                id=_next(),
                persona_id=req.persona_id,
                title=req.message[:30],
                created_at=datetime.datetime.utcnow().isoformat(),
            )
            _conversations.append(conv)
            req.conversation_id = conv.id

        _messages.append(Message(
            id=_next(),
            conversation_id=req.conversation_id,
            role="user",
            content=req.message,
            created_at=datetime.datetime.utcnow().isoformat(),
        ))

        context = await build_context(req.conversation_id)
        reply = await chat_completion(context, persona.system_prompt)
        reply = strip_actions(reply)
        reply = render_emoji(reply)

        _messages.append(Message(
            id=_next(),
            conversation_id=req.conversation_id,
            role="assistant",
            content=reply,
            created_at=datetime.datetime.utcnow().isoformat(),
        ))

        await extract_and_save_memory(req.conversation_id, req.message, reply)

        return ChatResponse(conversation_id=req.conversation_id, reply=reply)
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations")
async def get_conversations(persona_id: int):
    convs = [c for c in _conversations if c.persona_id == persona_id]
    convs.sort(key=lambda x: x.created_at, reverse=True)
    return [{"id": c.id, "title": c.title, "created_at": c.created_at} for c in convs]


@router.get("/messages/{conversation_id}")
async def get_messages(conversation_id: int):
    msgs = [m for m in _messages if m.conversation_id == conversation_id]
    msgs.sort(key=lambda x: x.created_at)
    return [{"role": m.role, "content": m.content, "created_at": m.created_at} for m in msgs]
