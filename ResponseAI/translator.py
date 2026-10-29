"""
Translation, localization, and speech-text utilities for AI Research Command Center.
Supports English, Hindi, Telugu, and Japanese.
"""

from typing import Dict, Any, Tuple
import os
import re
from pathlib import Path
from dotenv import load_dotenv

# Ensure environment is loaded
load_dotenv(Path(__file__).resolve().parent / ".env")

LANGUAGES = {
    "English": {
        "code": "en",
        "bcp47": "en-US",
        "label": "English",
        "native": "English",
        "flag": "🇬🇧",
        "voice_name": "en-US",
    },
    "Hindi": {
        "code": "hi",
        "bcp47": "hi-IN",
        "label": "Hindi",
        "native": "हिंदी",
        "flag": "🇮🇳",
        "voice_name": "hi-IN",
    },
    "Telugu": {
        "code": "te",
        "bcp47": "te-IN",
        "label": "Telugu",
        "native": "తెలుగు",
        "flag": "🇮🇳",
        "voice_name": "te-IN",
    },
    "Japanese": {
        "code": "ja",
        "bcp47": "ja-JP",
        "label": "Japanese",
        "native": "日本語",
        "flag": "🇯🇵",
        "voice_name": "ja-JP",
    },
}

LANGUAGE_LIST = list(LANGUAGES.keys())

# UI String localization dictionary
UI_STRINGS: Dict[str, Dict[str, str]] = {
    "English": {
        "brand_title": "Research Command Center",
        "brand_sub": "Multi-Agent System",
        "hero_eyebrow": "Live Multi-Agent Research System",
        "hero_title": "Ask anything. Watch four agents<br><span>research it in real time.</span>",
        "hero_sub": "A search agent, a reader agent, a writer and a critic work in sequence — gathering sources, extracting content, drafting a structured report, and grading it.",
        "quick_start": "Quick-start queries",
        "topic_label": "Research Topic",
        "topic_placeholder": "e.g. Breakthroughs in solid-state EV batteries in 2026",
        "launch_button": "Launch Research →",
        "voice_input_title": "Voice Assistant — Speak Query",
        "voice_search_btn": "🎙️ Click to Speak",
        "voice_listening": "Listening... Speak your topic now",
        "voice_use_btn": "Use Spoken Query",
        "pipeline_title": "Multi-Agent Execution Pipeline",
        "tab_report": "Report",
        "tab_findings": "Key Findings",
        "tab_sources": "Sources",
        "tab_critic": "Critic Review",
        "tab_raw": "Raw Agent Output",
        "stat_runtime": "Total Runtime",
        "stat_sources": "Sources Found",
        "stat_score": "Critic Score",
        "stat_findings": "Key Findings",
        "copy_report": "Copy Report",
        "copied": "Copied",
        "download_report": "⬇ Download Full Report (.md)",
        "listen_report": "🔊 Listen to Report",
        "voice_assistant": "Voice Assistant",
        "speaking": "Reading report aloud...",
        "pause": "⏸️ Pause",
        "resume": "▶️ Resume",
        "stop": "⏹️ Stop",
        "system_status": "System Status",
        "pipeline_ready": "Pipeline ready",
        "agents_online": "4 online",
        "session_stats": "Session Stats",
        "reports_count": "Reports",
        "avg_score": "Avg Score",
        "history_title": "Research History",
        "no_history": "No research runs yet this session.",
        "view_btn": "View",
        "standing_by": "Standing by",
        "standing_by_sub": "Enter a topic or speak your query above, then launch research.",
        "translating": "Translating response to",
        "theme_dark": "🌙 Dark Theme",
        "theme_light": "☀️ Light Theme",
        "translated_badge": "Translated to",
        "original_badge": "Original (English)",
        "voice_controls": "Voice Assistant Controls",
        "speech_rate": "Speed",
    },
    "Hindi": {
        "brand_title": "रिसर्च कमांड सेंटर",
        "brand_sub": "मल्टी-एजेंट प्रणाली",
        "hero_eyebrow": "लाइव मल्टी-एजेंट अनुसंधान प्रणाली",
        "hero_title": "कुछ भी पूछें। चार एजेंटों को<br><span>वास्तविक समय में शोध करते देखें।</span>",
        "hero_sub": "एक खोज एजेंट, एक पाठक एजेंट, एक लेखक और एक समीक्षक क्रम में काम करते हैं — स्रोत एकत्र करना, सामग्री निकालना, संरचित रिपोर्ट तैयार करना और उसका मूल्यांकन करना।",
        "quick_start": "त्वरित-प्रारंभ प्रश्न",
        "topic_label": "शोध विषय",
        "topic_placeholder": "उदा. 2026 में सॉलिड-स्टेट ईवी बैटरी में सफलताएं",
        "launch_button": "शोध शुरू करें →",
        "voice_input_title": "वॉयस असिस्टेंट — बोलकर प्रश्न पूछें",
        "voice_search_btn": "🎙️ बोलने के लिए क्लिक करें",
        "voice_listening": "सुन रहा है... अब अपना विषय बोलें",
        "voice_use_btn": "इस बोले गए विषय का उपयोग करें",
        "pipeline_title": "मल्टी-एजेंट निष्पादन पाइपलाइन",
        "tab_report": "रिपोर्ट",
        "tab_findings": "मुख्य निष्कर्ष",
        "tab_sources": "स्रोत",
        "tab_critic": "समीक्षक समीक्षा",
        "tab_raw": "कच्चा आउटपुट",
        "stat_runtime": "कुल समय",
        "stat_sources": "मिले स्रोत",
        "stat_score": "समीक्षक स्कोर",
        "stat_findings": "मुख्य निष्कर्ष",
        "copy_report": "रिपोर्ट कॉपी करें",
        "copied": "कॉपी हो गया",
        "download_report": "⬇ पूरी रिपोर्ट डाउनलोड करें (.md)",
        "listen_report": "🔊 रिपोर्ट सुनें",
        "voice_assistant": "वॉयस असिस्टेंट",
        "speaking": "रिपोर्ट पढ़कर सुनाई जा रही है...",
        "pause": "⏸️ रोकें",
        "resume": "▶️ जारी रखें",
        "stop": "⏹️ बंद करें",
        "system_status": "सिस्टम स्थिति",
        "pipeline_ready": "पाइपलाइन तैयार",
        "agents_online": "4 ऑनलाइन",
        "session_stats": "सत्र आँकड़े",
        "reports_count": "रिपोर्ट्स",
        "avg_score": "औसत स्कोर",
        "history_title": "अनुसंधान इतिहास",
        "no_history": "इस सत्र में अभी तक कोई शोध नहीं हुआ है।",
        "view_btn": "देखें",
        "standing_by": "प्रतीक्षारत",
        "standing_by_sub": "विषय दर्ज करें या बोलने के लिए माइक पर क्लिक करें, फिर शोध शुरू करें।",
        "translating": "प्रतिक्रिया का अनुवाद किया जा रहा है:",
        "theme_dark": "🌙 डार्क थीम",
        "theme_light": "☀️ लाइट थीम",
        "translated_badge": "अनुवादित भाषा:",
        "original_badge": "मूल (अंग्रेज़ी)",
        "voice_controls": "वॉयस असिस्टेंट नियंत्रण",
        "speech_rate": "गति",
    },
    "Telugu": {
        "brand_title": "రీసెర్చ్ కమాండ్ సెంటర్",
        "brand_sub": "మల్టీ-ఏజెంట్ సిస్టమ్",
        "hero_eyebrow": "లైవ్ మల్టీ-ఏజెంట్ పరిశోధనా వ్యవస్థ",
        "hero_title": "ఏదైనా అడగండి. నాలుగు ఏజెంట్లు<br><span>నిజ సమయంలో పరిశోధన చేయడం చూడండి.</span>",
        "hero_sub": "శోధన ఏజెంట్, రీడర్ ఏజెంట్, రచయిత మరియు విమర్శకుడు వరుసగా పని చేస్తారు — మూలాలను సేకరించడం, కంటెంట్‌ను సంగ్రహించడం, నిర్మాణాత్మక నివేదికను రూపొందించడం మరియు మూల్యాంకనం చేయడం.",
        "quick_start": "త్వరిత ప్రశ్నలు",
        "topic_label": "పరిశోధనా అంశం",
        "topic_placeholder": "ఉదా. 2026లో సాలిడ్-స్టేట్ EV బ్యాటరీ పురోగతులు",
        "launch_button": "పరిశోధన ప్రారంభించండి →",
        "voice_input_title": "వాయిస్ అసిస్టెంట్ — ప్రశ్నను మాట్లాడండి",
        "voice_search_btn": "🎙️ మాట్లాడటానికి క్లిక్ చేయండి",
        "voice_listening": "వింటోంది... ఇప్పుడు మీ అంశాన్ని మాట్లాడండి",
        "voice_use_btn": "ఈ అంశాన్ని ఎంచుకోండి",
        "pipeline_title": "మల్టీ-ఏజెంట్ ఎగ్జిక్యూషన్ పైప్‌లైన్",
        "tab_report": "నివేదిక",
        "tab_findings": "ముఖ్య ఫలితాలు",
        "tab_sources": "వనరులు",
        "tab_critic": "విమర్శకుల సమీక్ష",
        "tab_raw": "రా అవుట్‌పుట్",
        "stat_runtime": "మొత్తం సమయం",
        "stat_sources": "కనుగొన్న వనరులు",
        "stat_score": "విమర్శకుల స్కోరు",
        "stat_findings": "ముఖ్య ఫలితాలు",
        "copy_report": "నివేదికను కాపీ చేయండి",
        "copied": "కాపీ చేయబడింది",
        "download_report": "⬇ పూర్తి నివేదిక డౌన్‌లోడ్ చేయండి (.md)",
        "listen_report": "🔊 నివేదిక వినండి",
        "voice_assistant": "వాయిస్ అసిస్టెంట్",
        "speaking": "నివేదికను చదువుతోంది...",
        "pause": "⏸️ పాజ్",
        "resume": "▶️ ప్లే",
        "stop": "⏹️ ఆపు",
        "system_status": "సిస్టమ్ స్థితి",
        "pipeline_ready": "పైప్‌లైన్ సిద్ధం",
        "agents_online": "4 ఆన్‌లైన్",
        "session_stats": "సెషన్ గణాంకాలు",
        "reports_count": "నివేదికలు",
        "avg_score": "సగటు స్కోర్",
        "history_title": "పరిశోధన చరిత్ర",
        "no_history": "ఈ సెషన్‌లో ఇంకా ఎలాంటి పరిశోధనలు జరగలేదు.",
        "view_btn": "చూడండి",
        "standing_by": "సిద్ధంగా ఉంది",
        "standing_by_sub": "అంశాన్ని నమోదు చేయండి లేదా మాట్లాడటానికి మైక్ క్లిక్ చేయండి, ఆపై పరిశోధనను ప్రారంభించండి.",
        "translating": "ప్రతిస్పందన అనువదించబడుతోంది:",
        "theme_dark": "🌙 డార్క్ థీమ్",
        "theme_light": "☀️ లైట్ థీమ్",
        "translated_badge": "అనువదించబడిన భాష:",
        "original_badge": "అసలు (ఇంగ్లీష్)",
        "voice_controls": "వాయిస్ అసిస్టెంట్ నియంత్రణలు",
        "speech_rate": "వేగం",
    },
    "Japanese": {
        "brand_title": "リサーチ・コマンドセンター",
        "brand_sub": "マルチエージェント・システム",
        "hero_eyebrow": "リアルタイム・マルチエージェント研究システム",
        "hero_title": "どんなテーマでも入力してください。<br><span>4つの自律エージェントがリアルタイムで調査します。</span>",
        "hero_sub": "検索、閲覧、執筆、批評の4エージェントが連携し、Webソース収集、深層解析、構成化レポート作成、厳格な品質評価を自動実行します。",
        "quick_start": "クイックスタートの検索例",
        "topic_label": "リサーチテーマ",
        "topic_placeholder": "例: 2026年全固体電池のブレークスルー",
        "launch_button": "リサーチを開始 →",
        "voice_input_title": "音声アシスタント — 音声入力",
        "voice_search_btn": "🎙️ クリックして話す",
        "voice_listening": "音声を聞き取り中... テーマを話してください",
        "voice_use_btn": "この音声テキストを使用",
        "pipeline_title": "マルチエージェント実行パイプライン",
        "tab_report": "レポート",
        "tab_findings": "主な知見",
        "tab_sources": "情報源",
        "tab_critic": "批評家レビュー",
        "tab_raw": "生出力データ",
        "stat_runtime": "総処理時間",
        "stat_sources": "発見した情報源",
        "stat_score": "批評スコア",
        "stat_findings": "重要ポイント",
        "copy_report": "レポートをコピー",
        "copied": "コピー完了",
        "download_report": "⬇ レポートをダウンロード (.md)",
        "listen_report": "🔊 レポートを音声で聴く",
        "voice_assistant": "音声アシスタント",
        "speaking": "レポートを読み上げています...",
        "pause": "⏸️ 一時停止",
        "resume": "▶️ 再生",
        "stop": "⏹️ 停止",
        "system_status": "システム状態",
        "pipeline_ready": "パイプライン準備完了",
        "agents_online": "4エージェント稼働中",
        "session_stats": "セッション統計",
        "reports_count": "レポート数",
        "avg_score": "平均スコア",
        "history_title": "リサーチ履歴",
        "no_history": "このセッションでのリサーチ履歴はありません。",
        "view_btn": "表示",
        "standing_by": "待機中",
        "standing_by_sub": "テーマを入力するかマイクボタンで話しかけ、リサーチを開始してください。",
        "translating": "回答を次の言語に翻訳中:",
        "theme_dark": "🌙 ダークテーマ",
        "theme_light": "☀️ ライトテーマ",
        "translated_badge": "翻訳言語:",
        "original_badge": "原文 (英語)",
        "voice_controls": "音声アシスタント操作",
        "speech_rate": "読み上げ速度",
    },
}


def get_ui_text(lang: str, key: str, default: str = "") -> str:
    """Retrieve localized UI text for a key, falling back to English."""
    lang_dict = UI_STRINGS.get(lang, UI_STRINGS["English"])
    return lang_dict.get(key, UI_STRINGS["English"].get(key, default))


def translate_query_to_english(query: str) -> str:
    """
    If query contains non-ASCII or non-English characters, translate it to English for optimal web search results.
    """
    if not query or not query.strip():
        return ""
    # Check if string is simple ASCII
    is_pure_ascii = all(ord(c) < 128 for c in query)
    if is_pure_ascii and len(query.split()) < 20:
        return query.strip()

    try:
        from agents import llm

        prompt = (
            "Translate the following user search query to concise, keyword-rich English for web research. "
            "If it is already in English, output it exactly. "
            "Output ONLY the English query, nothing else:\n\n"
            f"{query.strip()}"
        )
        response = llm.invoke(prompt)
        content = getattr(response, "content", response)
        if isinstance(content, list):
            content = "".join(b if isinstance(b, str) else b.get("text", "") for b in content)
        clean = str(content).strip().strip('"\'')
        return clean if clean else query
    except Exception:
        return query


def translate_text(text: str, target_lang: str, context: str = "research text") -> str:
    """
    Translates text into target_lang using LLM.
    If target_lang is English, returns text as-is.
    """
    if not text or target_lang == "English":
        return text

    try:
        from agents import llm

        prompt = (
            f"You are a professional multilingual translator. "
            f"Translate the following {context} accurately and fluently into {target_lang}. "
            f"Keep all markdown formatting (headings, lists, bullet points, bold text, citations, and URLs) intact. "
            f"Do not add conversational preamble or concluding remarks. Output ONLY the translated content:\n\n"
            f"{text}"
        )
        response = llm.invoke(prompt)
        content = getattr(response, "content", response)
        if isinstance(content, list):
            content = "".join(b if isinstance(b, str) else b.get("text", "") for b in content)
        return str(content).strip()
    except Exception as e:
        return f"{text}\n\n*(Translation note: Could not complete translation due to: {e})*"


def clean_text_for_speech(markdown_text: str, max_chars: int = 1500) -> str:
    """
    Cleans markdown formatting, links, URLs, and asterisks for smooth text-to-speech audio rendering.
    """
    if not markdown_text:
        return ""
    # Remove code blocks
    text = re.sub(r"```[\s\S]*?```", "", markdown_text)
    # Remove inline code
    text = re.sub(r"`[^`]*`", "", text)
    # Convert markdown links [text](url) to text
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    # Remove bare URLs
    text = re.sub(r"https?://\S+", "", text)
    # Remove markdown headings #, ##, etc.
    text = re.sub(r"#+\s*", "", text)
    # Remove bold/italic asterisks and underscores
    text = re.sub(r"[*_~]+", "", text)
    # Remove bullet symbols
    text = re.sub(r"^\s*[-+*•]\s*", "", text, flags=re.MULTILINE)
    # Remove excess whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_chars]
