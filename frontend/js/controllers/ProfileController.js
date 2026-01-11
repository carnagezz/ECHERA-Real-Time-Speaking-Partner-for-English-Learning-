import { api } from '../utils/api.js';

export class ProfileController {
  async getStatistics(userId) {
    return api("/api/profile/statistics?userId=" + encodeURIComponent(userId));
  }
  
  calculateAverageFluency(scores) {
    return 0.0;
  }
  
  calculateAverageWordChoice(scores) {
    return 0.0;
  }
  
  calculateAverageGrammar(scores) {
    return 0.0;
  }
  

}