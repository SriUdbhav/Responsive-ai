"""
Voice Assistant HTML/JS components for Speech-to-Text and Text-to-Speech.
Seamlessly integrates with Streamlit and browser Web Speech API.
"""

import json
import html as html_lib
import streamlit.components.v1 as components
from translator import clean_text_for_speech, LANGUAGES


def render_voice_input_card(target_lang: str = "English", theme: str = "dark"):
    """
    Renders an in-browser Web Speech API voice input widget.
    Allows speaking in English, Hindi, Telugu, or Japanese.
    """
    lang_info = LANGUAGES.get(target_lang, LANGUAGES["English"])
    bcp47 = lang_info["bcp47"]
    lang_label = lang_info["label"]

    is_dark = theme == "dark"
    bg_card = "#141D2C" if is_dark else "#FFFFFF"
    border_color = "#212C3D" if is_dark else "#E2E8F0"
    text_color = "#E9EEF6" if is_dark else "#0F172A"
    text_muted = "#9BA8BE" if is_dark else "#64748B"
    accent = "#4FE8D3" if is_dark else "#0EA5E9"
    accent_dim = "rgba(79,232,211,0.15)" if is_dark else "rgba(14,165,233,0.12)"

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <style>
      body {{
        margin: 0;
        padding: 0;
        font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', sans-serif;
        background: transparent;
        color: {text_color};
      }}
      .mic-wrap {{
        display: flex;
        align-items: center;
        gap: 12px;
        background: {bg_card};
        border: 1px solid {border_color};
        border-radius: 12px;
        padding: 10px 16px;
      }}
      .mic-btn {{
        background: {accent_dim};
        border: 1.5px solid {accent};
        color: {accent};
        border-radius: 50%;
        width: 44px;
        height: 44px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        font-size: 20px;
        transition: all 0.25s ease;
        flex-shrink: 0;
      }}
      .mic-btn:hover {{
        transform: scale(1.05);
        box-shadow: 0 0 16px {accent_dim};
      }}
      .mic-btn.listening {{
        background: #F5677D;
        border-color: #F5677D;
        color: #FFFFFF;
        animation: pulse-mic 1.2s infinite;
      }}
      @keyframes pulse-mic {{
        0% {{ box-shadow: 0 0 0 0 rgba(245, 103, 125, 0.7); }}
        70% {{ box-shadow: 0 0 0 14px rgba(245, 103, 125, 0); }}
        100% {{ box-shadow: 0 0 0 0 rgba(245, 103, 125, 0); }}
      }}
      .mic-info {{
        flex: 1;
        min-width: 0;
      }}
      .mic-title {{
        font-size: 13px;
        font-weight: 600;
        color: {text_color};
        display: flex;
        align-items: center;
        gap: 6px;
      }}
      .lang-pill {{
        font-size: 10.5px;
        font-family: monospace;
        background: {accent_dim};
        color: {accent};
        padding: 2px 6px;
        border-radius: 4px;
      }}
      .mic-transcript {{
        font-size: 12px;
        color: {text_muted};
        margin-top: 3px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }}
      .copy-btn {{
        background: transparent;
        border: 1px solid {border_color};
        color: {accent};
        border-radius: 8px;
        padding: 6px 12px;
        font-size: 12px;
        cursor: pointer;
        font-weight: 500;
        display: none;
      }}
      .copy-btn:hover {{
        background: {accent_dim};
      }}
    </style>
    </head>
    <body>
      <div class="mic-wrap">
        <button id="micBtn" class="mic-btn" title="Click to speak">🎙️</button>
        <div class="mic-info">
          <div class="mic-title">
            Voice Query Assistant
            <span class="lang-pill">{lang_label} ({bcp47})</span>
          </div>
          <div id="transcriptBox" class="mic-transcript">Click the microphone to speak your research query...</div>
        </div>
        <button id="useBtn" class="copy-btn">📋 Copy to Query</button>
      </div>

      <script>
        const micBtn = document.getElementById("micBtn");
        const transcriptBox = document.getElementById("transcriptBox");
        const useBtn = document.getElementById("useBtn");
        let recognition = null;
        let isRecording = false;
        let finalQuery = "";

        const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;

        if (SpeechRec) {{
          recognition = new SpeechRec();
          recognition.lang = "{bcp47}";
          recognition.continuous = false;
          recognition.interimResults = true;

          recognition.onstart = () => {{
            isRecording = true;
            micBtn.classList.add("listening");
            transcriptBox.innerText = "Listening... Speak now ({lang_label})";
            transcriptBox.style.color = "{accent}";
          }};

          recognition.onresult = (event) => {{
            let interim = "";
            for (let i = event.resultIndex; i < event.results.length; ++i) {{
              if (event.results[i].isFinal) {{
                finalQuery += event.results[i][0].transcript;
              }} else {{
                interim += event.results[i][0].transcript;
              }}
            }}
            const current = finalQuery || interim;
            transcriptBox.innerText = current;
          }};

          recognition.onerror = (event) => {{
            isRecording = false;
            micBtn.classList.remove("listening");
            transcriptBox.innerText = "Error: " + event.error;
            transcriptBox.style.color = "#F5677D";
          }};

          recognition.onend = () => {{
            isRecording = false;
            micBtn.classList.remove("listening");
            if (finalQuery.trim()) {{
              transcriptBox.innerText = '"' + finalQuery.trim() + '"';
              transcriptBox.style.color = "{text_color}";
              useBtn.style.display = "inline-block";
              // Copy directly to clipboard so user can paste or we sync
              navigator.clipboard.writeText(finalQuery.trim());
            }} else {{
              transcriptBox.innerText = "Finished. Click mic to speak again.";
              transcriptBox.style.color = "{text_muted}";
            }}
          }};

          micBtn.addEventListener("click", () => {{
            if (isRecording) {{
              recognition.stop();
            }} else {{
              finalQuery = "";
              useBtn.style.display = "none";
              try {{
                recognition.start();
              }} catch (e) {{
                recognition.stop();
              }}
            }}
          }});

          useBtn.addEventListener("click", () => {{
            if (finalQuery) {{
              navigator.clipboard.writeText(finalQuery.trim());
              useBtn.innerText = "✓ Copied to Clipboard!";
              setTimeout(() => {{
                useBtn.innerText = "📋 Copy to Query";
              }}, 2000);
            }}
          }});

        }} else {{
          transcriptBox.innerText = "Web Speech Recognition not supported in this browser. Use Chromium / Edge for voice input.";
        }}
      </script>
    </body>
    </html>
    """
    components.html(html_code, height=72)


def render_voice_player_card(
    report_text: str,
    summary_text: str = "",
    target_lang: str = "English",
    theme: str = "dark",
    key: str = "voice_player"
):
    """
    Renders a Text-to-Speech audio reader using browser SpeechSynthesis.
    Supports English, Hindi, Telugu, and Japanese native voices with Play, Pause, Stop and Speed controls.
    """
    lang_info = LANGUAGES.get(target_lang, LANGUAGES["English"])
    bcp47 = lang_info["bcp47"]
    lang_label = lang_info["label"]

    clean_full = clean_text_for_speech(report_text, max_chars=3000)
    clean_summary = clean_text_for_speech(summary_text, max_chars=1200) if summary_text else clean_full[:1200]

    payload_full = json.dumps(clean_full)
    payload_summary = json.dumps(clean_summary)

    is_dark = theme == "dark"
    bg_card = "#141D2C" if is_dark else "#FFFFFF"
    border_color = "#212C3D" if is_dark else "#E2E8F0"
    text_color = "#E9EEF6" if is_dark else "#0F172A"
    text_muted = "#9BA8BE" if is_dark else "#64748B"
    accent = "#4FE8D3" if is_dark else "#0EA5E9"
    accent_dim = "rgba(79,232,211,0.15)" if is_dark else "rgba(14,165,233,0.12)"

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <style>
      body {{
        margin: 0;
        padding: 0;
        font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', sans-serif;
        background: transparent;
        color: {text_color};
      }}
      .voice-card {{
        background: {bg_card};
        border: 1px solid {border_color};
        border-radius: 14px;
        padding: 14px 18px;
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
      }}
      .voice-left {{
        display: flex;
        align-items: center;
        gap: 12px;
      }}
      .voice-icon {{
        width: 36px;
        height: 36px;
        border-radius: 10px;
        background: {accent_dim};
        border: 1px solid {accent};
        color: {accent};
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        flex-shrink: 0;
      }}
      .voice-info {{
        display: flex;
        flex-direction: column;
      }}
      .voice-title {{
        font-size: 13.5px;
        font-weight: 600;
        color: {text_color};
      }}
      .voice-status {{
        font-size: 11.5px;
        color: {text_muted};
        font-family: monospace;
      }}
      .voice-controls {{
        display: flex;
        align-items: center;
        gap: 8px;
        flex-wrap: wrap;
      }}
      .btn {{
        background: {accent_dim};
        border: 1px solid {accent};
        color: {accent};
        border-radius: 8px;
        padding: 7px 14px;
        font-size: 12.5px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s ease;
      }}
      .btn:hover {{
        background: {accent};
        color: #04110E;
      }}
      .btn-secondary {{
        background: transparent;
        border-color: {border_color};
        color: {text_muted};
      }}
      .btn-secondary:hover {{
        border-color: {accent};
        color: {accent};
      }}
      .rate-select {{
        background: {bg_card};
        border: 1px solid {border_color};
        color: {text_color};
        border-radius: 6px;
        padding: 6px 10px;
        font-size: 12px;
        outline: none;
      }}
    </style>
    </head>
    <body>
      <div class="voice-card">
        <div class="voice-left">
          <div class="voice-icon" id="pulseIcon">🔊</div>
          <div class="voice-info">
            <div class="voice-title">AI Voice Assistant &mdash; {lang_label} ({bcp47})</div>
            <div class="voice-status" id="statusLabel">Ready to read aloud</div>
          </div>
        </div>
        <div class="voice-controls">
          <button class="btn" id="playFullBtn">&#9658; Read Full Report</button>
          <button class="btn btn-secondary" id="playSummaryBtn">&#10024; Read Summary</button>
          <button class="btn btn-secondary" id="pauseBtn">&#10074;&#10074; Pause</button>
          <button class="btn btn-secondary" id="stopBtn">&#9632; Stop</button>
          <select id="rateSelect" class="rate-select" title="Speech rate">
            <option value="0.85">0.85x</option>
            <option value="1.0" selected>1.0x</option>
            <option value="1.2">1.2x</option>
            <option value="1.4">1.4x</option>
          </select>
        </div>
      </div>

      <script>
        const fullText = {payload_full};
        const summaryText = {payload_summary};
        const targetBcp47 = "{bcp47}";

        const statusLabel = document.getElementById("statusLabel");
        const pulseIcon = document.getElementById("pulseIcon");
        const playFullBtn = document.getElementById("playFullBtn");
        const playSummaryBtn = document.getElementById("playSummaryBtn");
        const pauseBtn = document.getElementById("pauseBtn");
        const stopBtn = document.getElementById("stopBtn");
        const rateSelect = document.getElementById("rateSelect");

        let synth = window.speechSynthesis;
        let currentUtterance = null;
        let isPaused = false;

        function getBestVoice(bcp) {{
          if (!synth) return null;
          const voices = synth.getVoices();
          // Exact match
          let match = voices.find(v => v.lang === bcp);
          if (!match) {{
            // Prefix match (e.g. 'hi' in 'hi-IN')
            const prefix = bcp.split("-")[0];
            match = voices.find(v => v.lang.startsWith(prefix));
          }}
          return match || null;
        }}

        function speak(text, modeName) {{
          if (!synth) {{
            statusLabel.innerText = "Speech synthesis not supported in this browser.";
            return;
          }}
          synth.cancel();

          currentUtterance = new SpeechSynthesisUtterance(text);
          currentUtterance.lang = targetBcp47;
          currentUtterance.rate = parseFloat(rateSelect.value) || 1.0;

          const matchedVoice = getBestVoice(targetBcp47);
          if (matchedVoice) {{
            currentUtterance.voice = matchedVoice;
          }}

          currentUtterance.onstart = () => {{
            statusLabel.innerText = "Speaking " + modeName + "...";
            pulseIcon.style.borderColor = "#F5677D";
            pulseIcon.style.color = "#F5677D";
          }};

          currentUtterance.onend = () => {{
            statusLabel.innerText = "Completed reading.";
            pulseIcon.style.borderColor = "{accent}";
            pulseIcon.style.color = "{accent}";
          }};

          currentUtterance.onerror = (e) => {{
            statusLabel.innerText = "Playback error: " + e.error;
          }};

          synth.speak(currentUtterance);
        }}

        playFullBtn.addEventListener("click", () => {{
          speak(fullText, "Full Report");
        }});

        playSummaryBtn.addEventListener("click", () => {{
          speak(summaryText, "Summary");
        }});

        pauseBtn.addEventListener("click", () => {{
          if (synth.speaking && !synth.paused) {{
            synth.pause();
            isPaused = true;
            statusLabel.innerText = "Paused";
            pauseBtn.innerText = "&#9658; Resume";
          }} else if (synth.paused) {{
            synth.resume();
            isPaused = false;
            statusLabel.innerText = "Speaking...";
            pauseBtn.innerText = "&#10074;&#10074; Pause";
          }}
        }});

        stopBtn.addEventListener("click", () => {{
          if (synth) {{
            synth.cancel();
            statusLabel.innerText = "Stopped";
            pauseBtn.innerText = "&#10074;&#10074; Pause";
            pulseIcon.style.borderColor = "{accent}";
            pulseIcon.style.color = "{accent}";
          }}
        }});

        rateSelect.addEventListener("change", () => {{
          if (synth.speaking && currentUtterance) {{
            // Restart with new rate
            const activeText = fullText;
            speak(activeText, "with updated speed");
          }}
        }});

        if (speechSynthesis.onvoiceschanged !== undefined) {{
          speechSynthesis.onvoiceschanged = () => {{}};
        }}
      </script>
    </body>
    </html>
    """
    components.html(html_code, height=78)

