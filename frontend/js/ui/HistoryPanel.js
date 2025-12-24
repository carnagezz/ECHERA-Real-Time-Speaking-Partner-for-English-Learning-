export class HistoryPanel {
  constructor(onSelectCallback) {
    this.conversationList = [];
    this._root = document.getElementById("historyList");
    this._activeId = "";
    this._onSelectCallback = onSelectCallback;
  }
  
  displayConversations() {
    this.sortByDate();
    this._root.innerHTML = "";
    
    if (!this.conversationList.length) {
      return this.displayEmptyChat();
    }
    
    for (const c of this.conversationList) {
      const div = document.createElement("div");
      div.className = "item" + (c.conversationId === this._activeId ? " active" : "");
      div.textContent = c.title || "New conversation";
      div.onclick = () => this._onSelectCallback(c.conversationId);
      this._root.appendChild(div);
    }
  }
  
  displayEmptyChat() {
    const d = document.createElement("div");
    d.className = "msg";
    d.textContent = "No conversations yet. Click New to start.";
    this._root.appendChild(d);
  }
  
  displayTitle(title) {
    document.getElementById("chatTitle").textContent = title;
  }
  
  sortByDate() {
    this.conversationList.sort((a, b) =>
      (b.createdAt || "").localeCompare(a.createdAt || "")
    );
  }
  
  showConfirmation(message) {
    return confirm(message);
  }
  
  removeFromList(id) {
    this.conversationList = this.conversationList.filter(
      x => x.conversationId !== id
    );
  }
  
  showError(message) {
    alert(message);
  }
  
  showSuccess(message) {
    console.log(message);
  }
  
}