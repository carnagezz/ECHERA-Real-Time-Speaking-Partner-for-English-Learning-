export class FeedbackPanel {
  constructor() {
    this.fluencyScore = 0;
    this.wordChoiceScore = 0;
    this.grammarScore = 0;
    this._flu = document.getElementById("fluency");
    this._wc = document.getElementById("wordChoice");
    this._gr = document.getElementById("grammar");
    this._tips = document.getElementById("tipsList");
    this._msg = document.getElementById("fbMsg");
  }
  
  displayFluency(score) {
    this.fluencyScore = score;
    this._flu.textContent = String(score);
  }
  
  displayWordChoice(score) {
    this.wordChoiceScore = score;
    this._wc.textContent = String(score);
  }
  
  displayGrammar(score) {
    this.grammarScore = score;
    this._gr.textContent = String(score);
  }
  
  displayTips(tips) {
    this._tips.innerHTML = "";
    for (const t of tips || []) {
      const li = document.createElement("li");
      li.textContent = t;
      this._tips.appendChild(li);
    }
  }
  
  showLoading() {
    this._msg.textContent = "Analyzing...";
  }
  
  removeLoading() {
    this._msg.textContent = "";
  }
  
  showError(message) {
    this._msg.textContent = message;
  }
  
}