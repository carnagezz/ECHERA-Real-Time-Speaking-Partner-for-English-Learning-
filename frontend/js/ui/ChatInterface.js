export class ChatInterface {
  constructor() {
    this.messageInput = "";
    this.isListening = false;
    this.isSpeakingMode = false;
    this._inputEl = document.getElementById("messageInput");
    this._log = document.getElementById("chatLog");
    this._indicator = document.getElementById("indicator");
    this._modeBtn = document.getElementById("btnMode");
  }
  
  toggleMode() {
    this.isSpeakingMode = !this.isSpeakingMode;
    
    if (this.isSpeakingMode) {
      this._modeBtn.textContent = "📢 Speaking Mode";
      this._modeBtn.classList.add("active-mode");
      this._inputEl.disabled = true;
      this._inputEl.placeholder = "Speaking mode active - use microphone";
      document.getElementById("btnSend").style.display = "none";
    } else {
      this._modeBtn.textContent = "💬 Text Mode";
      this._modeBtn.classList.remove("active-mode");
      this._inputEl.disabled = false;
      this._inputEl.placeholder = "Type your message...";
      document.getElementById("btnSend").style.display = "inline-block";
    }
  }
  
  displayMessage(text) {
    this.appendToChat(text);
  }
  
  enableInputs() {
    if (!this.isSpeakingMode) {
      this._inputEl.disabled = false;
      document.getElementById("btnSend").disabled = false;
    } else {
      this._inputEl.disabled = true;
      document.getElementById("btnSend").style.display = "none";
    }
    document.getElementById("btnMic").disabled = false;
  }
  
  disableInputs() {
    this._inputEl.disabled = true;
    document.getElementById("btnSend").disabled = true;
    document.getElementById("btnMic").disabled = true;
  }
  
  showIndicator(message) {
    this._indicator.textContent = message;
    this._indicator.classList.remove("hidden");
  }
  
  startVoiceInput() {
    this.isListening = true;
  }
  
  stopVoiceInput() {
    this.isListening = false;
  }
  
  clearInput() {
    this._inputEl.value = "";
  }
  
  appendToChat(text) {
    this.appendBubble("user", text);
  }
  
  enableSendButton() {
    document.getElementById("btnSend").disabled = false;
  }
  
  disableSendButton() {
    document.getElementById("btnSend").disabled = true;
  }
  
  preventSending() {
    if (!this.isSpeakingMode) {
      this.disableSendButton();
    }
  }
  
  removeIndicators() {
    this._indicator.classList.add("hidden");
    this._indicator.textContent = "";
  }
  
  ready() {
    this.enableInputs();
  }
  
  appendBubble(senderId, text) {
    const div = document.createElement("div");
    div.className = "bubble " + (senderId === "ai" ? "ai" : "user");
    div.textContent = text;
    this._log.appendChild(div);
    this._log.scrollTop = this._log.scrollHeight;
  }
}