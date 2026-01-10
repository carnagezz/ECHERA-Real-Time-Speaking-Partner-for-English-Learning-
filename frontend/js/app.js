import { api } from './utils/api.js';
import { AccountController } from './controllers/AccountController.js';
import { SettingsController } from './controllers/SettingsController.js';
import { ProfileController } from './controllers/ProfileController.js';
import { LoginPage } from './ui/LoginPage.js';
import { ChatInterface } from './ui/ChatInterface.js';
import { HistoryPanel } from './ui/HistoryPanel.js';
import { FeedbackPanel } from './ui/FeedbackPanel.js';
import { SettingsPage } from './ui/SettingsPage.js';
import { ProfilePage } from './ui/ProfilePage.js';
import { SpeechSystem } from './services/SpeechSystem.js';
import { createModalContainer, showModal, showConfirm } from './utils/modal.js';

const App = {
  loginPage: null,
  accountController: null,
  settingsPage: null,
  settingsController: null,
  profilePage: null,
  profileController: null,
  historyPanel: null,
  chatInterface: null,
  feedbackPanel: null,
  speechSystem: null,

  userId: "",
  sessionId: "",
  conversationId: "",

  api,

  saveSession(userId, sessionId) {
    this.userId = userId;
    this.sessionId = sessionId;
    localStorage.setItem("userId", userId);
    localStorage.setItem("sessionId", sessionId);
  },

  loadSession() {
    this.userId = localStorage.getItem("userId") || "";
    this.sessionId = localStorage.getItem("sessionId") || "";
    return !!(this.userId && this.sessionId);
  },

  clearSession() {
    this.userId = "";
    this.sessionId = "";
    localStorage.removeItem("userId");
    localStorage.removeItem("sessionId");
  },

  showPage(id) {
    for (const el of document.querySelectorAll(".page")) {
      el.classList.add("hidden");
    }
    
    const page = document.getElementById(id);
    if (page) {
      page.classList.remove("hidden");
    }
    
    const loggedIn = !!(this.userId && this.sessionId);
    const topbar = document.getElementById("topbar");
    
    if (topbar) {
      topbar.style.display = (id === "pageLogin" || id === "pageRegister") ? "none" : "flex";
    }
    
    const btnLogout = document.getElementById("btnLogout");
    const navChat = document.getElementById("navChat");
    const navProfile = document.getElementById("navProfile");
    const navSettings = document.getElementById("navSettings");
    
    if (btnLogout) btnLogout.style.display = loggedIn ? "inline-flex" : "none";
    if (navChat) navChat.style.display = loggedIn ? "inline" : "none";
    if (navProfile) navProfile.style.display = loggedIn ? "inline" : "none";
    if (navSettings) navSettings.style.display = loggedIn ? "inline" : "none";
  },

  async boot() {
    console.log("App booting...");

    this.speechSystem = new SpeechSystem();
    this.loginPage = new LoginPage();
    this.accountController = new AccountController();
    this.settingsPage = new SettingsPage();
    this.settingsController = new SettingsController(this.speechSystem);
    this.profilePage = new ProfilePage();
    this.profileController = new ProfileController();
    this.historyPanel = new HistoryPanel((id) => this.onSelectConversation(id));
    this.chatInterface = new ChatInterface();
    this.feedbackPanel = new FeedbackPanel();
    
    console.log("Components initialized");
    
    const btnLogin = document.getElementById("btnLogin");
    const btnRegister = document.getElementById("btnRegister");
    const btnLogout = document.getElementById("btnLogout");
    const linkToRegister = document.getElementById("linkToRegister");
    const linkToLogin = document.getElementById("linkToLogin");
    const btnNew = document.getElementById("btnNew");
    const btnDelete = document.getElementById("btnDelete");
    const btnSend = document.getElementById("btnSend");
    const btnMic = document.getElementById("btnMic");
    const btnMode = document.getElementById("btnMode");
    const messageInput = document.getElementById("messageInput");
    const btnPreview = document.getElementById("btnPreview");
    const btnSaveVoice = document.getElementById("btnSaveVoice");
    const btnUpdateProfile = document.getElementById("btnUpdateProfile");
    
    if (btnLogin) btnLogin.onclick = () => this.onLogin();
    if (btnRegister) btnRegister.onclick = () => this.onRegister();
    if (btnLogout) btnLogout.onclick = () => this.onLogout();
    
    if (linkToRegister) {
      linkToRegister.onclick = (e) => {
        e.preventDefault();
        this.showPage("pageRegister");
      };
    }
    
    if (linkToLogin) {
      linkToLogin.onclick = (e) => {
        e.preventDefault();
        this.showPage("pageLogin");
      };
    }
    
    if (btnNew) btnNew.onclick = () => this.onNewConversation();
    if (btnDelete) btnDelete.onclick = () => this.onDeleteConversation();
    if (btnSend) btnSend.onclick = () => this.onSend();

    if (btnMic) {
      btnMic.onclick = (e) => {
      e.preventDefault();
      e.stopPropagation();
      console.log("Mic button PHYSICALLY clicked");
      this.onMic();
    };
  
    btnMic.disabled = false;
    } 

    if (btnMode) btnMode.onclick = () => this.onToggleMode();
    
    if (messageInput) {
      messageInput.addEventListener("keydown", e => {
        if (e.key === "Enter" && !this.chatInterface.isSpeakingMode) this.onSend();
      });
      
      messageInput.addEventListener("input", e => {
        const hasText = e.target.value.trim().length > 0;
        if (btnSend && !this.chatInterface.isSpeakingMode) {
          btnSend.disabled = !hasText;
        }
      });
    }
    
    if (btnPreview) btnPreview.onclick = () => this.onPreviewVoice();
    if (btnSaveVoice) btnSaveVoice.onclick = () => this.onSaveVoice();
    if (btnUpdateProfile) btnUpdateProfile.onclick = () => this.onUpdateProfile();
    
    window.addEventListener("hashchange", () => this.route());
    
    this.loadSession();
    console.log("Session loaded, routing...");
    this.route();
    console.log("Route complete");

  },

  route() {
    const h = location.hash || "#/login";
    
    if (!this.userId || !this.sessionId) {
      if (h === "#/register") {
        this.showPage("pageRegister");
      } else {
        this.showPage("pageLogin");
      }
      return;
    }
    
    if (h.startsWith("#/profile")) {
      this.showProfile();
      return;
    }
    
    if (h.startsWith("#/settings")) {
      this.showSettings();
      return;
    }
    
    this.showChat();
  },

  async onRegister() {
    const email = document.getElementById("regEmail").value;
    const password = document.getElementById("regPassword").value;
    const nickname = document.getElementById("regNick").value;
    const msg = document.getElementById("regMsg");
    
    msg.textContent = "";
    
    try {
      await this.accountController.register(email, password, nickname);
      msg.textContent = "Registration successful! You can now log in.";
    } catch (e) {
      msg.textContent = e.message;
    }
  },

  async onLogin() {
    const email = document.getElementById("loginEmail").value;
    const password = document.getElementById("loginPassword").value;
    
    try {
      const out = await this.accountController.login(email, password);
      this.saveSession(out.userId, out.sessionId);
      this.loginPage.redirectToChat();
      await this.showChat();
    } catch (e) {
      this.loginPage.showError(e.message);
    }
  },

  async onLogout() {
    try {
      await this.accountController.logout(this.sessionId);
    } catch {}
  
    this.speechSystem.stopListening();
    this.speechSystem.setOnFinalResultCallback(null);
  
    this.chatInterface.isListening = false;
    this.chatInterface.removeIndicators();
  
    this.clearSession();
    this.conversationId = "";
  
    document.getElementById("loginEmail").value = "";
    document.getElementById("loginPassword").value = "";
  
    document.getElementById("loginMsg").textContent = "";
  
    location.hash = "#/login";
    this.showPage("pageLogin");
  },

  async refreshHistory() {
    const out = await api("/api/conversations?userId=" + encodeURIComponent(this.userId));
    this.historyPanel.conversationList = out.conversations || [];
    this.historyPanel.displayConversations();
  },

  async showChat() {
    this.showPage("pageChat");
    await this.refreshHistory();
    {
    const firstConv = this.historyPanel.conversationList[0];
    await this.onSelectConversation(firstConv.conversationId);
    }
  },

  async showProfile() {
    this.showPage("pageProfile");
    const msg = document.getElementById("profileMsg");
    const updateMsg = document.getElementById("updateMsg");
    msg.textContent = "Loading...";
    updateMsg.textContent = "";
    
    document.getElementById("updateNickname").value = "";
    document.getElementById("updatePassword").value = "";
    
    try {
      const out = await this.profileController.getStatistics(this.userId);
      
      document.getElementById("pEmail").textContent = out.accountInfo.email || "-";
      document.getElementById("pNick").textContent = out.accountInfo.nickname || "-";
      document.getElementById("pConvs").textContent = String(out.conversationCount ?? "-");
      document.getElementById("pMsgs").textContent = String(out.messageCount ?? "-");
      document.getElementById("pFlu").textContent = (out.avgFluency ?? 0).toFixed(1);
      document.getElementById("pWc").textContent = (out.avgWordChoice ?? 0).toFixed(1);
      document.getElementById("pGr").textContent = (out.avgGrammar ?? 0).toFixed(1);
      
      msg.textContent = "";
    } catch (e) {
      msg.textContent = e.message;
    }
  },
  
  async onUpdateProfile() {
    const nickname = document.getElementById("updateNickname").value.trim();
    const password = document.getElementById("updatePassword").value;
    const updateMsg = document.getElementById("updateMsg");
    
    updateMsg.textContent = "";
    
    if (!nickname && !password) {
      updateMsg.textContent = "Please enter a new nickname or password to update.";
      return;
    }
    
    try {
      const data = {};
      if (nickname) data.nickname = nickname;
      if (password) data.password = password;
      
      await this.accountController.updateProfile(this.userId, data);
      
      updateMsg.textContent = "Profile updated successfully!";
      updateMsg.style.color = "var(--success)";
      
      document.getElementById("updateNickname").value = "";
      document.getElementById("updatePassword").value = "";
      
      setTimeout(() => {
        this.showProfile();
      }, 1000);
      
    } catch (e) {
      updateMsg.textContent = e.message;
      updateMsg.style.color = "var(--danger)";
    }
  },

  async showSettings() {
    this.showPage("pageSettings");
    this.settingsPage.showError("");
    
    try {
      const out = await this.settingsController.loadVoiceSettings(this.userId);
      this.settingsPage.selectedVoice = out.selectedVoice || "";
      this.settingsPage.availableVoices = this.speechSystem.getAvailableVoices();
      this.settingsPage.displayVoiceOptions();
    } catch (e) {
      this.settingsPage.showError(e.message);
    }
  },

  async onPreviewVoice() {
    try {
      this.settingsPage.showPlayingIndicator();
      await this.settingsController.previewVoice(this.settingsPage.selectedVoice);
      this.settingsPage.showError("");
    } catch (e) {
      this.settingsPage.showError(e.message);
    }
  },

  async onSaveVoice() {
    try {
      await this.settingsController.saveVoicePreference(
        this.userId,
        this.settingsPage.selectedVoice
      );
      this.settingsPage.showSuccessMessage();
    } catch (e) {
      this.settingsPage.showError(e.message);
    }
  },

  async onNewConversation() {
    try {
      const out = await api("/api/conversations", "POST", {
        userId: this.userId
      });
      
      this.conversationId = out.conversationId;
      this.historyPanel._activeId = this.conversationId;
      document.getElementById("chatTitle").textContent = "New conversation";
      document.getElementById("chatLog").innerHTML = "";
      
      await this.refreshHistory();
      this.historyPanel._activeId = this.conversationId;
      this.historyPanel.displayConversations();
    } catch (e) {
      showModal(e.message);
    }
  },

  async onSelectConversation(conversationId) {
    this.conversationId = conversationId;  
    this.historyPanel._activeId = conversationId;
    this.historyPanel.displayConversations();
  
    const data = await api("/api/conversations/" + conversationId);
    this.historyPanel.displayTitle(data.title || "Conversation");
  
    document.getElementById("chatLog").innerHTML = "";
    for (const m of data.messages || []) {
      this.chatInterface.appendBubble(m.senderId, m.content);
    }
  },

  async onDeleteConversation() {
    if (!this.conversationId) return;
  
    showConfirm(
      "Are you sure you want to delete this conversation? This action is permanent.",
      "Delete Conversation",
      async () => {
        await api("/api/conversations/" + this.conversationId, "DELETE");
        this.historyPanel.removeFromList(this.conversationId);
        this.conversationId = "";
      
        document.getElementById("chatLog").innerHTML = "";
        document.getElementById("chatTitle").textContent = "New conversation";
      
        await this.refreshHistory();
      },
      () => {
        console.log("Delete cancelled");
      }
    );
  },
  
  async onToggleMode() {
    this.chatInterface.toggleMode();
  
    if (this.chatInterface.isSpeakingMode) {
      this.chatInterface.isListening = false;
    
      this.speechSystem.setOnFinalResultCallback(async (text) => {
        this.chatInterface.isListening = false;
        this.chatInterface.removeIndicators();
      
        if (text) {
          await this.sendMessageInMode(text, true);
        }
      });
    } 
    else {
      this.speechSystem.setOnFinalResultCallback(null);
      this.speechSystem.stopListening();
      this.chatInterface.isListening = false;
      this.chatInterface.removeIndicators();
    }
  },

  async onMic() {
    console.log("=== MIC BUTTON CLICKED ===");
    console.log("isSpeakingMode:", this.chatInterface.isSpeakingMode);
    console.log("isListening:", this.chatInterface.isListening);
    console.log("speechSystem._listening:", this.speechSystem._listening);
  
    if (!this.chatInterface.isSpeakingMode) {
      showModal("Please switch to Speaking Mode first!");
      return;
    }
  
    if (this.speechSystem.isSpeaking()) {
      showModal("Please wait for AI to finish speaking!");
      return;
    }
  
    if (!this.speechSystem.requestMicrophone()) {
      this.chatInterface.showIndicator(
        "Speech recognition not supported in this browser."
      );
      setTimeout(() => this.chatInterface.removeIndicators(), 2000);
      return;
    }
  
    if (this.chatInterface.isListening) {
      console.log(">>> STOPPING listening");
      this.chatInterface.isListening = false;
      this.speechSystem.stopListening();
      this.chatInterface.removeIndicators();
      return;
    }
  
    console.log(">>> STARTING listening");
    this.chatInterface.isListening = true;
    this.chatInterface.showIndicator("၊၊||၊ Listening... (will auto-send when you stop)");
  
    const started = this.speechSystem.startListening();
    console.log(">>> startListening returned:", started);
    console.log(">>> speechSystem._listening is now:", this.speechSystem._listening);
  
    if (!started) {
      console.log(">>> FAILED to start");
      this.chatInterface.isListening = false;
      this.chatInterface.showIndicator("❌ Microphone failed to start. Please try again.");
      setTimeout(() => {
        this.chatInterface.removeIndicators();
      }, 2000);
    } else {
      console.log(">>> SUCCESS - microphone started");
    }
  },

  async onSend() {
    if (this.chatInterface.isSpeakingMode) {
      showModal("You are in Speaking Mode. Please use the microphone or switch to Text Mode.");
      return;
    }
    
    const inputEl = document.getElementById("messageInput");
    const text = inputEl.value;
    
    if (!text || !text.trim()) {
      return this.chatInterface.preventSending();
    }
    
    await this.sendMessageInMode(text, false);
  },

async sendMessageInMode(text, isSpeakingMode) {
    console.log("sendMessageInMode called");
    console.log("Current conversationId:", this.conversationId);
    console.log("Text:", text);
    console.log("isSpeakingMode:", isSpeakingMode);
  
    if (!this.conversationId) {
      console.log("No conversationId, creating new conversation");
      await this.onNewConversation();
    }
    else {
      console.log("Using existing conversationId:", this.conversationId);
    }
    
    try {
      this.chatInterface.disableInputs();
      this.chatInterface.showIndicator("AI thinking...");
      this.feedbackPanel.showLoading();
      
      this.chatInterface.appendBubble("user", text);
      
      if (!isSpeakingMode) {
        this.chatInterface.clearInput();
      }
      
      if (document.getElementById("chatTitle").textContent === "New conversation") {
        try {
          const t = await api(
            "/api/conversations/" + this.conversationId + "/first-title",
            "POST",
            { text }
          );
          document.getElementById("chatTitle").textContent = t.title;
          await this.refreshHistory();
          this.historyPanel._activeId = this.conversationId;
          this.historyPanel.displayConversations();
        } catch {}
      }
      
      const out = await api("/api/messages/send", "POST", {
        conversationId: this.conversationId,
        userId: this.userId,
        text
      });
      
      this.chatInterface.appendBubble("ai", out.aiText);
      
      if (isSpeakingMode) {
        try {
          const voiceSettings = await api(
            "/api/settings/load?userId=" + encodeURIComponent(this.userId)
          );
          
          const savedVoice = voiceSettings.selectedVoice;
          
          if (savedVoice && savedVoice !== 'default') {
            this.chatInterface.showIndicator("🗣 AI speaking... (please wait)");
            
            const utterance = this.speechSystem.textToSpeech(out.aiText, savedVoice);
            
            if (utterance) {
              utterance.onend = () => {
                this.chatInterface.removeIndicators();
                this.chatInterface.ready();
              };
              
              utterance.onerror = () => {
                this.chatInterface.removeIndicators();
                this.chatInterface.ready();
              };
            } else {
              this.chatInterface.removeIndicators();
              this.chatInterface.ready();
            }
          } else {
            this.chatInterface.showIndicator("🔊 AI speaking... (please wait)");
            
            const utterance = this.speechSystem.textToSpeech(out.aiText, this.speechSystem.getAvailableVoices()[0]);
            
            if (utterance) {
              utterance.onend = () => {
                this.chatInterface.removeIndicators();
                this.chatInterface.ready();
              };
              
              utterance.onerror = () => {
                this.chatInterface.removeIndicators();
                this.chatInterface.ready();
              };
            } else {
              this.chatInterface.removeIndicators();
              this.chatInterface.ready();
            }
          }
        } catch (e) {
          console.error("Voice error:", e);
          this.chatInterface.removeIndicators();
          this.chatInterface.ready();
        }
      } else {
        this.chatInterface.removeIndicators();
        this.chatInterface.ready();
      }
      
      this.feedbackPanel.removeLoading();
      this.feedbackPanel.displayFluency(out.scores.fluency);
      this.feedbackPanel.displayWordChoice(out.scores.wordChoice);
      this.feedbackPanel.displayGrammar(out.scores.grammar);
      this.feedbackPanel.displayTips(out.tips);
      
    } catch (e) {
      if (e.message && e.message.toLowerCase().includes("100 message")) {
        const chatLog = document.getElementById("chatLog");
        const lastBubble = chatLog.lastElementChild;
        if (lastBubble && lastBubble.classList.contains("bubble")) {
          lastBubble.remove();
        }
        
        showModal(
          "This conversation has reached the maximum of 100 message exchanges. Please start a new conversation to continue.",
          "Message Limit Reached"
        );
        
        this.chatInterface.disableInputs();
        
      } else {
        showModal(e.message || "An error occurred", "Error");
        
        this.chatInterface.enableInputs();
      }
      
      this.feedbackPanel.removeLoading();
      this.chatInterface.removeIndicators();
    }
  }
};

window.App = App;
window.addEventListener("load", () => App.boot());