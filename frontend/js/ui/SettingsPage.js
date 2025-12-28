export class SettingsPage {
  constructor() {
    this.availableVoices = [];
    this.selectedVoice = "";
    this._list = document.getElementById("voiceList");
    this._msg = document.getElementById("settingsMsg");
  }
  
  displayVoiceOptions() {
    this.renderVoiceList();
    this.highlightCurrentVoice();
  }
  
  showPlayingIndicator() {
    this._msg.textContent = "Playing preview...";
  }
  
  showSuccessMessage() {
    this._msg.textContent = "Voice preference saved successfully.";
  }
  
  renderVoiceList() {
    this._list.innerHTML = "";
    for (const v of this.availableVoices) {
      const d = document.createElement("div");
      d.className = "voiceItem" + (v === this.selectedVoice ? " active" : "");
      d.textContent = v;
      d.onclick = () => this.updateCurrentSelection(v);
      this._list.appendChild(d);
    }
  }
  
  highlightCurrentVoice() {
    this.renderVoiceList();
  }
  
  updateCurrentSelection(voiceId) {
    this.selectedVoice = voiceId;
    this.highlightCurrentVoice();
  }
  
  showError(message) {
    this._msg.textContent = message;
  }
}