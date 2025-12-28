export class SpeechSystem {
  constructor() {
    this.availableVoices = [];
    this._voices = [];
    this._currentVoice = null;
    
    this._rec = null;
    this._supported =
      "webkitSpeechRecognition" in window || "SpeechRecognition" in window;
    this._listening = false;
    this._finalText = "";
    this._partialText = "";
    this._error = "";
    this._onFinalResult = null;
    this._silenceTimer = null;
    this._silenceDuration = 4000;
    this._lastSpeechTime = null;
    
    if ("speechSynthesis" in window) {
      this.loadVoices();
      window.speechSynthesis.onvoiceschanged = () => this.loadVoices();
    }
    
    const Ctor = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (this._supported && Ctor) {
      this._rec = new Ctor();
      this._rec.lang = "en-US";
      this._rec.continuous = true;
      this._rec.interimResults = true;
      
      this._rec.onresult = e => {
        let finalText = "";
        let partialText = "";
        
        for (let i = e.resultIndex; i < e.results.length; i++) {
          const txt = e.results[i][0].transcript;
          if (e.results[i].isFinal) {
            finalText += txt;
          } else {
            partialText += txt;
          }
        }
        
        if (finalText.trim()) {
          this._finalText += (this._finalText ? " " : "") + finalText.trim();
        }
        this._partialText = partialText.trim();
        
        this._lastSpeechTime = Date.now();
        this._resetSilenceTimer();
      };
      
      this._rec.onerror = e => {
        console.error("Speech recognition error:", e.error);
        this._error = e.error || "speech_error";
        
        if (e.error === "no-speech") {
          console.log("No speech detected, resetting");
          this._finalText = "";
          this._partialText = "";
        }
      };
      
      this._rec.onend = () => {
        console.log("Speech recognition ended");
        this._listening = false;
        this._clearSilenceTimer();
  
        if (this._onFinalResult && this._finalText.trim()) {
          this._onFinalResult(this._finalText.trim());
        }
  
        this._finalText = "";
        this._partialText = "";
      };
      
      this._rec.onstart = () => {
        console.log("Speech recognition onstart event");
        this._listening = true;
        this._lastSpeechTime = Date.now();
      };
    }
  }
  
  setSilenceDuration(milliseconds) {
    this._silenceDuration = milliseconds;
    console.log(`Silence duration set to ${milliseconds}ms`);
  }
  
  _resetSilenceTimer() {
    this._clearSilenceTimer();
    
    this._silenceTimer = setTimeout(() => {
      console.log(`${this._silenceDuration}ms of silence detected, stopping...`);
      if (this._listening) {
        this.stopListening();
      }
    }, this._silenceDuration);
  }
  
  _clearSilenceTimer() {
    if (this._silenceTimer) {
      clearTimeout(this._silenceTimer);
      this._silenceTimer = null;
    }
  }

  loadVoices() {
    const load = () => {
      const voices = window.speechSynthesis.getVoices() || [];

      const nativeEnglishVoices = voices.filter(v =>
        (v.lang === "en-US") &&
        !v.localService
      );

      this._voices = nativeEnglishVoices;
      this.availableVoices = nativeEnglishVoices.map(
        v => `${v.lang} | ${v.name}`
      );

    console.log("Filtered voices:", nativeEnglishVoices);
    };

    load();
    window.speechSynthesis.onvoiceschanged = load;
  }

  getAvailableVoices() {
    return this.availableVoices;
  }
  
  listAllVoices() {
    return this.getAvailableVoices();
  }

  loadVoice(voiceId) {
    const v = this._voices.find(x => `${x.lang} | ${x.name}` === voiceId);
    this._currentVoice = v || null;
    return this._currentVoice;
  }

  textToSpeech(text, voiceId) {
    if (!("speechSynthesis" in window)) return false;
    
    const u = new SpeechSynthesisUtterance(text);
    const v = this._voices.find(x => `${x.lang} | ${x.name}` === voiceId);
    if (v) u.voice = v;
    
    speechSynthesis.speak(u);
    return u;
  }
  
  playSample(voiceId) {
    return this.textToSpeech("This is a voice preview.", voiceId);
  }
  
  isSpeaking() {
    return window.speechSynthesis && window.speechSynthesis.speaking;
  }
  
  cancelSpeech() {
    if (window.speechSynthesis) {
      window.speechSynthesis.cancel();
    }
  }

  requestMicrophone() {
    return this._supported;
  }

  activateMicrophone() {
    return this.requestMicrophone();
  }

  startListening() {
    if (!this._rec) return false;
    
    if (this._listening) {
      console.log("Already listening, ignoring start request");
      return true;
    }
    
    this._error = "";
    this._finalText = "";
    this._partialText = "";
    this._clearSilenceTimer();
    this._listening = true;
    this._lastSpeechTime = Date.now();
    
    try {
      this._rec.start();
      console.log("Speech recognition started");
      this._resetSilenceTimer();
      return true;
    } catch (e) {
      console.error("Start error:", e);
      
      if (e.message && e.message.toLowerCase().includes("already")) {
        console.log("Recognition already started, continuing");
        this._resetSilenceTimer();
        return true;
      }
      
      this._listening = false;
      this._clearSilenceTimer();
      return false;
    }
  }
  
  stopListening() {
    if (!this._rec) return false;
    
    this._clearSilenceTimer();
    
    try {
      this._rec.stop();
      return true;
    } catch {
      return false;
    }
  }
  
  setOnFinalResultCallback(callback) {
    this._onFinalResult = callback;
  }

  captureAudio() {
    return null;
  }
  
  detectSilence() {
    return null;
  }

  transcribeAudio() {
    if (this._error) return "";
    return (this._finalText || this._partialText || "").trim();
  }
}