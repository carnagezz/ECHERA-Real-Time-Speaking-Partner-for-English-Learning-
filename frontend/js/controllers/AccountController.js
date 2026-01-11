import { api } from '../utils/api.js';

export class AccountController {
  async register(email, password, nickname) {
    return api("/api/account/register", "POST", { email, password, nickname });
  }
  
  async login(email, password) {
    return api("/api/account/login", "POST", { email, password });
  }
  
  async logout(sessionId) {
    return api("/api/account/logout", "POST", { sessionId });
  }
  
  async updateProfile(userId, data) {
    return api("/api/account/updateProfile", "POST", { userId, data });
  }
  
  validateInput(data) {
    return true;
  }
}