import { api } from '../utils/api.js';

export class SettingsController {
  constructor(speechSystem) {
    this.speechSystem = speechSystem;
  }
  
  async loadVoiceSettings(userId) {
    return api("/api/settings/load?userId=" + encodeURIComponent(userId));
  }
  
  async saveVoicePreference(userId, voiceId) {
    return api("/api/settings/save", "POST", { userId, voiceId });
  }
  
  async previewVoice(voiceId) {
    await api("/api/settings/preview", "POST", { voiceId });
    return this.speechSystem.playSample(voiceId);
  }
}